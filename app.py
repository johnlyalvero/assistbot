import streamlit as st
from openai import OpenAI
import sqlite3
import re
import PyPDF2
import io
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURAZIONE
# ─────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_NAME        = os.getenv("DB_NAME", "chat_logs.db")

# ─────────────────────────────────────────────
# MODELLO
# ─────────────────────────────────────────────
SELECTED_MODEL = {
    "id":           "gpt-4o",
    "description":  "Modello OpenAI principale. Ottimo equilibrio qualità/velocità.",
    "context":      "128k token",
    "max_tokens":   2500,
    "kb_max_chars": 60_000,
    "prompt_file":  "system_prompt.txt",
}

TICKET_PATTERN = re.compile(r"<ticket>(.*?)</ticket>", re.DOTALL)

# ─────────────────────────────────────────────
# PAGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AssistBot — Supporto Filiale",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS TEMA BANCARIO
# ─────────────────────────────────────────────
_css_path = Path(__file__).parent / "style_claude.css"
if _css_path.exists():
    with open(_css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
.bank-header {
    display: flex; align-items: center; gap: 16px;
    padding: 20px 0 12px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
}
.logo-mark { font-size: 2.4rem; }
.title-block h1 { margin: 0; font-size: 1.4rem; font-weight: 700; }
.title-block p  { margin: 0; font-size: 0.85rem; color: #b4b4b4; }
.model-badge {
    display: inline-block; background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.3); border-radius: 20px;
    padding: 3px 12px; font-size: 0.78rem; color: #3b82f6; margin-bottom: 16px;
}
.model-info-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 10px 14px; font-size: 0.82rem; color: #b4b4b4;
    margin-top: 8px;
}
.ticket-container {
    background: rgba(59,130,246,0.07); border: 1px solid rgba(59,130,246,0.25);
    border-radius: 12px; padding: 16px 20px; margin-top: 16px;
}
.ticket-header {
    font-weight: 700; font-size: 1rem; margin-bottom: 14px;
    color: #3b82f6; border-bottom: 1px solid rgba(59,130,246,0.2); padding-bottom: 8px;
}
.ticket-row   { display: flex; gap: 12px; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.tk-label     { min-width: 160px; font-size: 0.8rem; color: #b4b4b4; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }
.tk-value     { font-size: 0.9rem; color: #ececec; }
.state-badge  {
    display: inline-block; background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.3); border-radius: 12px;
    padding: 2px 10px; font-size: 0.75rem; color: #22c55e; margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
def init_db() -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversation_logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role      TEXT,
            content   TEXT,
            model     TEXT
        )
    """)
    c.execute("PRAGMA table_info(conversation_logs)")
    if "model" not in [col[1] for col in c.fetchall()]:
        c.execute("ALTER TABLE conversation_logs ADD COLUMN model TEXT")
    conn.commit()
    conn.close()


def log_message(role: str, content: str, model: str = "") -> None:
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        "INSERT INTO conversation_logs (role, content, model) VALUES (?, ?, ?)",
        (role, content, model),
    )
    conn.commit()
    conn.close()


init_db()


# ─────────────────────────────────────────────
# UTILS RAG
# ─────────────────────────────────────────────
def extract_text(uploaded_file) -> str:
    """Estrae testo da PDF, TXT o MD per il context injection."""
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    elif uploaded_file.name.lower().endswith((".txt", ".md")):
        text = uploaded_file.read().decode("utf-8")
    return text


# ─────────────────────────────────────────────
# CARICAMENTO SYSTEM PROMPT DA FILE
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_system_prompt_template(filename: str = "system_prompt.txt") -> str:
    """Carica il template del system prompt dal file (con cache).
    Cerca nella stessa directory di app.py."""
    path = Path(__file__).parent / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Fallback minimale se il file non esiste
    return (
        "Sei AssistBot, assistente operativo interno di filiale bancaria.\n"
        "Rispondi solo in base alla KB. Zero allucinazioni.\n\n"
        "KB:\n{docs_text}\n{kb_status}"
    )


def build_system_prompt(docs_text: str = "", model_cfg: dict | None = None) -> str:
    """Costruisce il system prompt iniettando la KB nel template."""
    if model_cfg is None:
        model_cfg = {}

    prompt_file  = model_cfg.get("prompt_file", "system_prompt.txt")
    kb_max_chars = model_cfg.get("kb_max_chars", 60_000)
    template     = load_system_prompt_template(prompt_file)

    # Tronca KB se supera il budget del modello
    if docs_text and len(docs_text) > kb_max_chars:
        docs_text = (
            docs_text[:kb_max_chars]
            + f"\n\n[⚠️ DOCUMENTO TRONCATO: superato il limite di {kb_max_chars:,} caratteri "
            "per questo modello.]"
        )

    if docs_text.strip():
        kb_status = (
            f"✅ KB ATTIVA — {len(docs_text):,} caratteri. "
            "Usa ESCLUSIVAMENTE questo contenuto per le risposte operative."
        )
    else:
        kb_status = (
            "⚠️ KB VUOTA. Non rispondere a domande operative. "
            "Invita l'utente a caricare i manuali."
        )

    return (
        template
        .replace("{docs_text}", docs_text or "Nessun documento caricato.")
        .replace("{kb_status}", kb_status)
    )


# ─────────────────────────────────────────────
# RENDER TICKET
# ─────────────────────────────────────────────
def _parse_ticket_text(raw_ticket: str) -> list[tuple[str, str]]:
    """Parsa il contenuto testuale del ticket (formato 'Campo: Valore') in una lista di tuple."""
    fields = []
    for line in raw_ticket.strip().splitlines():
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            fields.append((key.strip(), value.strip()))
    return fields


def _render_ticket(fields: list[tuple[str, str]]) -> None:
    """Renderizza il ticket come card strutturata a partire dalla lista di campi."""
    rows_html = "".join(
        f'<div class="ticket-row">'
        f'<span class="tk-label">{key}</span>'
        f'<span class="tk-value">{value if value else "—"}</span>'
        f"</div>"
        for key, value in fields
    )
    st.markdown(
        f'<div class="ticket-container">'
        f'<div class="ticket-header">🎟️ Riepilogo Richiesta di Assistenza</div>'
        f"{rows_html}</div>",
        unsafe_allow_html=True,
    )
    st.success("✅ Copia i dati nel portale di assistenza interno.")


def _try_parse_and_render_ticket(raw_response: str) -> tuple[str, bool]:
    """
    Se la risposta contiene un tag <ticket>…</ticket>, estrae il testo,
    lo parsa come lista campi e renderizza la card.
    Restituisce (testo_pulito, ticket_trovato).
    """
    match = TICKET_PATTERN.search(raw_response)
    if not match:
        return raw_response, False

    display_text = TICKET_PATTERN.sub("", raw_response).strip()
    fields = _parse_ticket_text(match.group(1))
    if fields:
        _render_ticket(fields)
        return display_text, True
    return raw_response, False


# ─────────────────────────────────────────────
# AUTO-LOAD MANUALI DI DEFAULT (example_manuals/)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_default_manuals() -> str:
    """Carica automaticamente tutti i file .md/.txt/.pdf dalla cartella example_manuals/.
    Eseguito una sola volta grazie alla cache di Streamlit."""
    manuals_dir = Path(__file__).parent / "example_manuals"
    if not manuals_dir.exists():
        return ""
    combined = ""
    for filepath in sorted(manuals_dir.iterdir()):
        if filepath.suffix.lower() in (".md", ".txt"):
            text = filepath.read_text(encoding="utf-8")
            combined += f"\n\n--- DOCUMENTO: {filepath.name} ---\n{text}"
        elif filepath.suffix.lower() == ".pdf":
            try:
                import PyPDF2, io as _io
                reader = PyPDF2.PdfReader(str(filepath))
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                combined += f"\n\n--- DOCUMENTO: {filepath.name} ---\n{text}"
            except Exception:
                pass
    return combined


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "messages":   [],
    "docs_text":  load_default_manuals(),   # KB pre-caricata dai manuali di default
    "conv_state": "INTAKE",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configurazione")

    # — Info modello —
    st.markdown(f"""
    <div class="model-info-card">
        <b>Modello:</b> <code>{SELECTED_MODEL['id']}</code><br>
        <b>Contesto:</b> {SELECTED_MODEL['context']}<br>
        <b>Note:</b> {SELECTED_MODEL['description']}
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # — System Prompt Info —
    import datetime
    st.markdown("### 📝 System Prompt")
    prompt_file = SELECTED_MODEL.get("prompt_file", "system_prompt.txt")
    sp_path     = Path(__file__).parent / prompt_file
    if sp_path.exists():
        chars  = len(sp_path.read_text(encoding="utf-8"))
        mod_dt = datetime.datetime.fromtimestamp(sp_path.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
        st.markdown(
            f"<small>✅ <code>{prompt_file}</code><br>"
            f"{chars:,} caratteri · modificato {mod_dt}</small>",
            unsafe_allow_html=True,
        )
        if st.button("🔄 Ricarica prompt", use_container_width=True,
                     help="Svuota la cache e ricarica il file prompt"):
            load_system_prompt_template.clear()
            st.success("Cache prompt svuotata.")
    else:
        st.warning(f"⚠️ `{prompt_file}` non trovato nella cartella dell'app.")

    st.divider()

    # — Caricamento documenti KB —
    st.markdown("### 📂 Knowledge Base (RAG)")
    st.caption("Carica manuali, circolari e procedure interne.")

    uploaded_files = st.file_uploader(
        "Carica documenti (PDF/TXT/MD)",
        type=["txt", "pdf", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if st.button("⚡ Sincronizza Knowledge Base", use_container_width=True):
        if uploaded_files:
            combined = ""
            for f in uploaded_files:
                combined += f"\n\n--- DOCUMENTO: {f.name} ---\n" + extract_text(f)
            st.session_state.docs_text = combined
            st.success(f"✅ {len(uploaded_files)} documento/i caricato/i.")
        else:
            st.session_state.docs_text = ""
            st.info("Nessun documento. KB resettata.")

    # Indicatore stato KB
    if st.session_state.docs_text:
        chars     = len(st.session_state.docs_text)
        kb_limit  = SELECTED_MODEL.get("kb_max_chars", 60_000)
        truncated = chars > kb_limit
        label     = f"{'⚠️ KB troncata' if truncated else '📄 KB attiva'} — {chars:,} caratteri"
        if truncated:
            label += f" (limite: {kb_limit:,})"
        st.markdown(f"<small>{label}</small>", unsafe_allow_html=True)
        if truncated:
            st.warning(
                f"⚠️ La KB ({chars:,} caratteri) supera il limite del modello "
                f"({kb_limit:,} caratteri). Verrà usata solo la prima parte."
            )
    else:
        st.markdown(
            "<small>⚠️ KB vuota — carica documenti per il self-service</small>",
            unsafe_allow_html=True,
        )

    st.divider()

    # — Reset sessione —
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Reset chat", use_container_width=True):
            st.session_state.messages   = []
            st.session_state.conv_state = "INTAKE"
            st.rerun()
    with col2:
        if st.button("🗑️ + KB", use_container_width=True, help="Reset chat e KB"):
            st.session_state.messages   = []
            st.session_state.docs_text  = ""
            st.session_state.conv_state = "INTAKE"
            st.rerun()

    st.divider()

    # — Debug stato macchina —
    with st.expander("🔍 Debug stato conversazione"):
        st.write(f"**Stato attuale:** `{st.session_state.conv_state}`")
        st.write(f"**Messaggi in sessione:** {len(st.session_state.messages)}")
        st.write(f"**Token KB (stima):** {len(st.session_state.docs_text) // 4:,}")

    st.caption(f"Log su SQLite locale · Powered by OpenAI {SELECTED_MODEL['id']}")


# ─────────────────────────────────────────────
# MAIN — HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="bank-header">
    <div class="logo-mark">🏛️</div>
    <div class="title-block">
        <h1>AssistBot — Supporto Filiale</h1>
        <p>Sistema di assistenza operativa interna · Solo per uso interno</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="model-badge">● Modello attivo: {SELECTED_MODEL['id']}</div>
""", unsafe_allow_html=True)

if not st.session_state.docs_text:
    st.warning(
        "⚠️ Knowledge Base vuota. Carica i manuali nella sidebar per abilitare il supporto operativo."
    )


# ─────────────────────────────────────────────
# RENDERING CRONOLOGIA MESSAGGI
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        raw = msg.get("raw_content", msg["content"])

        if msg["role"] == "assistant" and "<ticket>" in raw:
            clean_text = TICKET_PATTERN.sub("", raw).strip()
            st.markdown(clean_text)
            match = TICKET_PATTERN.search(raw)
            if match:
                fields = _parse_ticket_text(match.group(1))
                if fields:
                    _render_ticket(fields)
        else:
            st.markdown(msg["content"])


# ─────────────────────────────────────────────
# CHAT INPUT & CORE LOGIC
# ─────────────────────────────────────────────
if prompt := st.chat_input("Descrivi il problema o la necessità operativa..."):

    # Salva e mostra messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    log_message("user", prompt, SELECTED_MODEL["id"])
    with st.chat_message("user"):
        st.markdown(prompt)

    # Costruisci history con system prompt
    system_prompt = build_system_prompt(
        st.session_state.docs_text,
        model_cfg=SELECTED_MODEL,
    )
    history = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        history.append({"role": m["role"], "content": m["content"]})

    # Chiamata API OpenAI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        try:
            client = OpenAI(api_key=OPENAI_API_KEY)

            with st.spinner(f"Analisi in corso con {SELECTED_MODEL['id']}..."):
                response = client.chat.completions.create(
                    model=SELECTED_MODEL["id"],
                    messages=history,
                    max_tokens=SELECTED_MODEL["max_tokens"],
                    temperature=0.15,
                )

            full_response = response.choices[0].message.content

            # Post-processing: gestione ticket
            display_text, has_ticket = _try_parse_and_render_ticket(full_response)
            message_placeholder.markdown(display_text)

            # Aggiornamento stato macchina a stati (euristico lato client)
            if has_ticket:
                st.session_state.conv_state = "TICKET"
            elif any(kw in full_response.lower() for kw in ["ha risolto", "apro la richiesta", "confermo che"]):
                st.session_state.conv_state = "CONFERMA"
            elif any(kw in full_response.lower() for kw in ["passo", "procedura", "verifica", "manuale", "circolare"]):
                st.session_state.conv_state = "SELFSERVICE"
            else:
                st.session_state.conv_state = "TRIAGE"

            # Salva in session state
            st.session_state.messages.append({
                "role":        "assistant",
                "content":     display_text,
                "raw_content": full_response,
            })
            log_message("assistant", full_response, SELECTED_MODEL["id"])

        except Exception as e:
            err = str(e)
            if "api_key" in err.lower() or "authentication" in err.lower() or "invalid_api_key" in err.lower():
                st.error("❌ Chiave API OpenAI non valida. Verifica OPENAI_API_KEY nel file .env")
            elif "model_not_found" in err.lower() or ("model" in err.lower() and "not" in err.lower()):
                st.error(f"❌ Modello `{SELECTED_MODEL['id']}` non disponibile. Verifica il tuo piano OpenAI.")
            elif "rate_limit" in err.lower():
                st.error("❌ Rate limit OpenAI raggiunto. Attendi qualche secondo e riprova.")
            elif "context_length" in err.lower() or "tokens" in err.lower():
                st.error(
                    "❌ La Knowledge Base è troppo grande per questo modello. "
                    "Carica meno documenti o riduci la dimensione dei PDF."
                )
            else:
                st.error(f"❌ Errore inatteso: {err}")
            with st.expander("🔍 Dettaglio errore tecnico"):
                st.code(err)
