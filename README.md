# AssistBot — Assistente Operativo Interno di Filiale

AssistBot è un chatbot di supporto operativo interno progettato per i dipendenti di filiale bancaria. Riduce il carico sul Service Desk fornendo risposte immediate basate sulla documentazione ufficiale e, solo quando necessario, guidando l'utente alla compilazione strutturata di una richiesta di assistenza.

---

## Funzionalità principali

**Self-service guidato (RAG)** — Il bot interroga i manuali operativi e le circolari caricate nella Knowledge Base e restituisce risposte numerate passo-passo, con riferimento al documento sorgente. Se il problema viene risolto, il ticket non viene aperto.

**Routing intelligente** — Se la documentazione non copre il caso, il bot classifica automaticamente la richiesta per ambito e coda (Incassi, Crediti, IT, Compliance, ecc.) e guida l'utente alla raccolta dei campi necessari per il ticket.

**Compilazione strutturata del ticket** — A fine flusso, il bot genera un riepilogo pronto per il copia-incolla nel portale di assistenza interno, con tutti i campi standardizzati: Oggetto, Categoria, Ambito, Coda, Priorità, UO Richiedente, Descrizione.

**Controllo privacy integrato** — In fase di consulenza, i dati personali citati dall'utente (CF, IBAN, nomi clienti) vengono ignorati. Solo in fase di ticket viene raccolto il codice azienda (CAG/NDG) come campo strutturato.

**Log delle conversazioni** — Ogni sessione viene registrata in un database SQLite locale per analisi post-test e affinamento dei prompt.

---

## Struttura del progetto

```
assistbot/
├── app.py                    # Applicazione principale Streamlit
├── system_prompt.txt         # System prompt con macchina a stati e tassonomia
├── style_claude.css          # Tema grafico dark mode
├── requirements.txt          # Dipendenze Python
├── .env                      # Variabili d'ambiente locali (non versionare)
├── .gitignore
└── example_manuals/          # Manuali di default caricati all'avvio
    └── *.md / *.txt / *.pdf
```

---

## Requisiti

- Python 3.10+
- Chiave API OpenAI (modello `gpt-4o`)

---

## Installazione locale

```bash
# 1. Clona il repository
git clone https://github.com/tuo-username/assistbot.git
cd assistbot

# 2. Installa le dipendenze
pip install -r requirements.txt

# 3. Configura la chiave API
# Crea un file .env nella root del progetto:
echo 'OPENAI_API_KEY="sk-..."' > .env

# 4. Avvia l'applicazione
streamlit run app.py
```

L'app sarà disponibile su `http://localhost:8501`.

---

## Configurazione

### Variabili d'ambiente

| Variabile | Descrizione | Default |
|---|---|---|
| `OPENAI_API_KEY` | Chiave API OpenAI | — (obbligatoria) |
| `DB_NAME` | Nome del file SQLite per i log | `chat_logs.db` |

In locale, le variabili vengono lette dal file `.env`. Su Streamlit Cloud, vanno inserite in **Settings → Secrets** nel formato:

```toml
OPENAI_API_KEY = "sk-..."
DB_NAME = "chat_logs.db"
```

### Knowledge Base

I manuali caricati nella cartella `example_manuals/` vengono letti automaticamente all'avvio come KB di default. Sono supportati i formati `.md`, `.txt` e `.pdf`.

È possibile caricare documenti aggiuntivi dinamicamente dalla sidebar durante la sessione, tramite il pulsante **Sincronizza Knowledge Base**. I file caricati manualmente si aggiungono alla KB di default.

Il limite della KB per il modello `gpt-4o` è **60.000 caratteri**. Documenti più lunghi vengono troncati automaticamente con avviso.

### System prompt

Il comportamento del bot è definito nel file `system_prompt.txt`, che include la macchina a stati conversazionale (INTAKE → TRIAGE → SELFSERVICE → CONFERMA → TICKET), le regole fondamentali e la tassonomia delle code di riferimento.

Per aggiornare il prompt a runtime senza riavviare l'app, usa il pulsante **Ricarica prompt** nella sidebar.

---

## Flusso conversazionale

```
INTAKE      → Chiarimento della richiesta (max 1 domanda)
    ↓
TRIAGE      → Classificazione interna: ambito, tipo, presenza in KB
    ↓
SELFSERVICE → Guida passo-passo dai manuali + domanda di conferma
    ↓ (se non risolto)
CONFERMA    → Raccolta campi ticket uno alla volta
    ↓
TICKET      → Riepilogo strutturato pronto per il copia-incolla
```

---

## Deploy su Streamlit Cloud

1. Fai il push del progetto su un repository GitHub (pubblico o privato)
2. Vai su [share.streamlit.io](https://share.streamlit.io) e collega il repository
3. Imposta `app.py` come file principale
4. Aggiungi le variabili in **Settings → Secrets**
5. Clicca **Deploy**

I file in `example_manuals/` vengono inclusi automaticamente nel deploy e caricati come KB di default all'avvio.

---

## Dipendenze

```
streamlit
openai
PyPDF2
python-dotenv
```

---

## Note tecniche

- Il modello attivo è `gpt-4o` con temperatura `0.15` per massimizzare la coerenza delle risposte operative.
- Il context window è 128k token. La KB viene iniettata direttamente nel system prompt (approccio RAG leggero, senza Vector DB).
- Il log SQLite si resetta ad ogni redeploy su Streamlit Cloud. Per persistenza dei log in produzione, è necessario un database esterno (es. Supabase, PostgreSQL).
- Il file `.env` non deve mai essere versionato. Verificare che sia presente nel `.gitignore`.
