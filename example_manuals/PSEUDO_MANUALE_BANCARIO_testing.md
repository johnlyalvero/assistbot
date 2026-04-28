# MANUALE OPERATIVO INTERNO — BANCA ESEMPIO S.P.A.
## Procedure Operative per le Filiali
### Versione 3.2 — Gennaio 2025 (DOCUMENTO DI TEST)

> ⚠️ DOCUMENTO FITTIZIO creato esclusivamente per il testing del chatbot. Non ha valore operativo reale.

---

# PARTE I — INCASSI E PAGAMENTI

## 1.1 Bonifici Italia e SEPA

### Procedura di inserimento bonifico ordinario

Per inserire un bonifico ordinario da conto corrente cliente, accedere al gestionale SIB dal percorso:
**Operatività → Pagamenti → Bonifico SEPA**

Campi obbligatori:
- IBAN beneficiario (24 caratteri, formato IT + 2 check + 23 alfanumerici)
- Importo (massimo €100.000 per operazione singola senza autorizzazione aggiuntiva)
- Causale (minimo 5 caratteri)
- Data valuta (non può essere precedente alla data odierna)

**Limiti operativi filiale (senza doppia firma):**
- Fino a €10.000: operatore abilitato B1 o superiore
- Da €10.001 a €50.000: richiede firma responsabile di filiale
- Oltre €50.000: richiede autorizzazione Operations centrale tramite ticket

**Errore frequente — Codice SIB-4421:** Indica IBAN non censito in archivio. Verificare il codice BIC corrispondente e, se estero, aprire ticket su coda "Bonifici: Italia/Estero/Finimport".

---

## 1.2 Bonifici Esteri (Swift/Settlement)

### Paesi con restrizioni operative (aggiornamento Circolare 07/2024)

Non è consentita la disposizione di bonifici verso i seguenti Paesi senza preventiva autorizzazione AML:
- Iran, Corea del Nord, Myanmar, Siria, Cuba (lista completa in allegato alla Circolare 07/2024)

Per i Paesi a rischio medio (lista B), è obbligatoria la compilazione del modulo AML-EXT/02 prima dell'inserimento nel sistema.

### Procedura bonifico estero in valuta

1. Accedere a **SIB → Estero → Bonifico Swift**
2. Selezionare la valuta (USD, GBP, CHF, JPY disponibili con cambio automatico; per altre valute contattare la Tesoreria)
3. Inserire il codice BIC/SWIFT del beneficiario (8 o 11 caratteri)
4. Compilare il campo "Informazioni per il beneficiario" in inglese
5. Selezionare la commissione: SHA (condivisa) o OUR (a carico ordinante)

**Errore codice 504 su SIB:** Indica timeout del servizio di validazione Swift. Attendere 15 minuti e riprovare. Se persiste, aprire ticket su coda "Estero (Swift/Settlement)" con screenshot dell'errore.

**Errore codice 512 su SIB:** Valuta non disponibile per il Paese selezionato. Contattare Tesoreria interno 4421.

---

## 1.3 F24 e Tributi

### Presentazione F24 per conto cliente

Accedere a **SIB → Tributi → F24 Telematico**

Scadenze tassative:
- F24 con saldo > €0: presentazione entro le ore 17:00 del giorno di scadenza
- F24 a saldo zero: accettati fino alle ore 20:00
- F24 con compensazione IVA > €5.000: richiede visto di conformità del cliente

**Attenzione (Circolare 03/2025):** A partire dal 1° marzo 2025, i modelli F24 con codice tributo 1040 (ritenute su redditi da lavoro autonomo) superiori a €250.000 devono essere inoltrati esclusivamente tramite Entratel dal cliente o dal suo intermediario fiscale. La filiale non può procedere in autonomia.

---

## 1.4 Monetica — ATM, Carte e POS

### Aumento temporaneo massimali carta

Per richiedere un aumento temporaneo del massimale giornaliero di una carta cliente:
1. Verificare l'identità del cliente (documento + firma o accesso autenticato)
2. Accedere a **SIB → Carte → Gestione Massimali**
3. Il massimale può essere aumentato fino al 150% del limite contrattuale per un massimo di 7 giorni
4. Modifiche superiori al 150% richiedono ticket su coda "Monetica (ATM, Carte, POS)" con motivazione

**Rapporti dormienti:** Un conto si considera dormiente dopo 24 mesi di inattività (Circolare 11/2023). Per riattivarlo è necessario che il cliente si presenti in filiale con documento valido. Non è possibile operare su conti dormienti da remoto.

---

# PARTE II — CREDITO E FINANZIAMENTI

## 2.1 Mutui Ipotecari Ordinari

### Requisiti per l'erogazione

**Soggetti ammissibili:**
- Persone fisiche residenti in Italia con reddito dimostrabile (busta paga, CUD, 730)
- Persone giuridiche con sede legale in Italia

**Soggetti NON ammissibili (Circolare 12/2024, pag. 45):**
- Soggetti non residenti in Italia (cittadinanza estera non è elemento ostativo, ma la residenza anagrafica in Italia è condizione necessaria)
- Soggetti con segnalazioni attive in CRIF categoria "Sofferenza"
- Persone fisiche di età superiore a 75 anni alla data di scadenza del mutuo

**Loan-to-Value massimo:**
- Prima casa: 80% del valore di perizia
- Seconda casa / investimento: 70%
- Con garanzia SACE/MCC: fino al 90% (procedura dedicata)

### Procedura di stipula

La stipula avviene esclusivamente in filiale alla presenza del cliente e del notaio. Almeno 5 giorni lavorativi prima della data di stipula, aprire ticket su coda "Mutui ipotecari ordinari" con:
- Data di stipula prevista
- CAG del cliente
- Numero pratica credito
- Nome del notaio

---

## 2.2 Prestiti Personali

### Erogazione a soggetti non residenti

**Circolare 12/2024, pag. 45 — DIVIETO:** Non è prevista l'erogazione di prestiti personali a soggetti non residenti nel territorio italiano, indipendentemente dalla nazionalità. La residenza anagrafica deve essere verificata tramite documento ufficiale non scaduto.

In caso di cliente straniero con residenza italiana documentata, la pratica segue il percorso ordinario.

### Limiti importo (senza garanzie aggiuntive)
- Fino a €30.000: decisione filiale (responsabile + operatore)
- Da €30.001 a €75.000: delibera Centro Crediti
- Oltre €75.000: delibera Direzione Crediti Centrale

---

## 2.3 Pegni

### Costituzione pegno su titoli/fondi

Per costituire un pegno su strumenti finanziari detenuti in dossier cliente:
1. Il cliente deve essere presente in filiale o aver sottoscritto mandato notarile
2. Verificare che il dossier non abbia vincoli preesistenti (SIB → Dossier → Verifica Vincoli)
3. Compilare modulo PEG-01 (disponibile in Intranet → Moduli → Credito)
4. Aprire ticket su coda "Pegni" allegando il modulo firmato in PDF

**Attenzione:** I pegni su fondi di investimento con NAV in valuta estera richiedono conversione al tasso BCE del giorno. Il sistema SIB applica il tasso automaticamente solo per EUR, USD e GBP.

---

## 2.4 Affidamenti Imprese

### Richiesta aumento temporaneo fido

Per aumenti temporanei del fido (massimo 30 giorni, massimo 30% dell'affidamento vigente):
- Accedere a SIB → Credito → Fidi → Modifica Temporanea
- Selezionare durata (1-30 giorni)
- Inserire motivazione (campo obbligatorio, minimo 20 caratteri)
- Importi > 20% dell'affidamento richiedono conferma via ticket a coda "Affidamenti Imprese"

---

# PARTE III — SISTEMI INFORMATIVI

## 3.1 Problemi alla Postazione di Lavoro

### Hardware — PC non si avvia

1. Verificare che l'alimentatore sia collegato correttamente
2. Tentare spegnimento forzato (tasto power per 10 secondi) e riaccensione
3. Se il PC non si avvia dopo 2 tentativi → aprire ticket su coda "Postazione di Lavoro (Hardware)" con numero seriale del PC (etichetta sul retro/sotto)
4. **Non spostare l'apparecchio autonomamente.** Attendere l'intervento del tecnico ICT

### Monitor — schermo nero o distorto

1. Verificare i cavi di collegamento (HDMI/VGA)
2. Premere WIN+P e selezionare "Solo schermo PC"
3. Se il problema persiste → ticket su "Postazione di Lavoro (Hardware)"

---

## 3.2 Software di Filiale — SIB

### Errori comuni SIB e risoluzione

| Codice Errore | Descrizione | Soluzione |
|---|---|---|
| SIB-1001 | Sessione scaduta | Effettuare nuovamente il login |
| SIB-2210 | Permessi insufficienti | Verificare il profilo autorizzativo in SIB → Profilo Utente |
| SIB-4421 | IBAN non validato | Controllare il formato e riprovare dopo 5 minuti |
| SIB-504 | Timeout servizio esterno | Attendere 15 minuti e riprovare; se persiste aprire ticket |
| SIB-9999 | Errore generico applicativo | Chiudere e riaprire SIB; se persiste aprire ticket ICT |

### Procedura di segnalazione anomalia SIB

1. Effettuare uno screenshot dell'errore (WIN+SHIFT+S)
2. Annotare ora esatta, operazione che si stava eseguendo, CAG cliente interessato (se applicabile)
3. Aprire ticket su coda "Software di Filiale" con screenshot allegato

---

## 3.3 Firma Elettronica (FEA/FEP)

### FEA non funzionante — tablet non risponde

1. Spegnere e riaccendere il tablet (tasto laterale per 5 secondi)
2. Verificare che la rete Wi-Fi di filiale sia attiva (controllare router)
3. Se il cliente deve firmare urgentemente: utilizzare la firma autografa su carta e acquisire in PDF tramite scanner
4. Aprire ticket su coda "Firma Elettronica (FEA/FEP)" indicando il numero seriale del dispositivo

### Firma non accettata dal sistema

**Causa frequente:** Il cliente ha una firma precedente salvata che non corrisponde. Procedura:
1. SIB → Anagrafe → Cliente → Gestione Firma → Cancella firma acquisita
2. Richiedere una nuova acquisizione firma al cliente
3. Se l'errore persiste dopo la cancellazione → ticket ICT

---

## 3.4 Posta Elettronica

### Casella di posta non accessibile

1. Verificare le credenziali (la password scade ogni 90 giorni — controllare data ultima modifica in Intranet → Profilo)
2. Accedere alla webmail via browser: **https://webmail.bancaesempio.internal**
3. Se la webmail funziona ma il client Outlook no: chiudere Outlook e riaprire
4. Se né webmail né Outlook funzionano: aprire ticket su coda "Posta elettronica" specificando il messaggio di errore esatto

### Fuori sede — accesso da postazione esterna

Per accedere alla posta da postazione non aziendale è necessario:
1. Connettersi alla VPN aziendale (client Cisco AnyConnect, credenziali = stesse della rete interna)
2. Aprire la webmail su **https://webmail.bancaesempio.internal**
L'accesso diretto al client Outlook da remoto non è supportato.

---

## 3.5 Abilitazioni e Accessi

### Richiesta nuova abilitazione applicativo

Le abilitazioni agli applicativi aziendali vengono gestite dalla coda "Abilitazione rapporti Dipendente". Per ogni richiesta indicare:
- Matricola del dipendente da abilitare
- Applicativo richiesto (es. SIB, CRM, portale crediti)
- Livello di accesso richiesto (consultazione / operativo / supervisore)
- Motivazione operativa

**Tempi di gestione:** Le richieste di abilitazione ordinarie vengono evase entro 2 giorni lavorativi. Per urgenze operative dichiarate, entro 4 ore lavorative.

### Reset password SIB

Il reset della password SIB può essere effettuato autonomamente:
1. Nella schermata di login SIB → "Password dimenticata"
2. Inserire la matricola dipendente
3. Ricevere il codice OTP sul cellulare aziendale registrato
4. Impostare la nuova password (minimo 10 caratteri, almeno 1 maiuscola, 1 numero, 1 carattere speciale)

Se il reset automatico non funziona → ticket su coda "Sblocco Utenza" con matricola.

---

# PARTE IV — COMPLIANCE E ANAGRAFE

## 4.1 Antiriciclaggio (AML) e Adeguata Verifica

### Adeguata verifica ordinaria (clienti retail)

Ai sensi del D.Lgs. 231/2007 e successive modifiche, è obbligatorio procedere all'adeguata verifica per:
- Apertura di nuovi rapporti
- Operazioni occasionali superiori a €10.000
- Operazioni frazionate che complessivamente superano €10.000 in 30 giorni
- Ogni volta che si sospetta riciclaggio o finanziamento al terrorismo

Documenti richiesti per persone fisiche:
- Documento di identità valido (carta identità, passaporto)
- Codice fiscale
- Autocertificazione residenza (se non presente in anagrafe)

### Segnalazione Operazione Sospetta (SOS)

In caso di dubbi su un'operazione, NON eseguire l'operazione e contattare immediatamente il Responsabile Compliance al numero interno **4500**. La segnalazione SOS va effettuata tramite il sistema **GIANOS** (SIB → Compliance → SOS).

**Attenzione:** La segnalazione SOS è coperta da segreto professionale. Non comunicare al cliente che è in corso una verifica.

---

## 4.2 Variazioni Anagrafiche

### Variazione indirizzo di residenza

Il cliente deve presentarsi in filiale con:
- Documento di identità valido
- Certificato di residenza (o autocertificazione ai sensi del DPR 445/2000)

Procedura SIB: **Anagrafe → Cliente → Variazione Dati → Residenza**

Le variazioni anagrafiche vengono validate entro 24 ore dal sistema centrale. In caso di urgenza (es. invio corrispondenza imminente), aprire ticket su coda "Variazioni Anagrafiche" specificando la data di urgenza.

### Trasferimento CAG da filiale a filiale

Il trasferimento del codice cliente (CAG) da una filiale a un'altra non è eseguibile autonomamente dalla filiale. Aprire ticket su coda "Anagrafe → Transazioni SIB" con:
- CAG del cliente
- Filiale di provenienza
- Filiale di destinazione
- Motivazione

---

# PARTE V — DIGITAL BANKING

## 5.1 Internet Banking (In Bank)

### Cliente non riesce ad accedere all'app In Bank

1. Verificare che il cliente abbia l'app aggiornata all'ultima versione (vers. 4.2.1 o superiore)
2. Verificare che le credenziali siano corrette (il sistema blocca dopo 3 tentativi errati)
3. In caso di blocco: la filiale può eseguire lo sblocco da **SIB → In Bank → Gestione Utente → Sblocco**
4. Se il cliente non riceve l'OTP per il login: verificare il numero di cellulare censito in anagrafe

**Censimento codice SIA per nuovo accesso:**
Se il cliente non è mai stato censito su In Bank, aprire ticket su coda "Richieste di censimento di codici SIA" allegando copia del documento di identità del cliente.

---

## 5.2 Installazione e Gestione POS

### POS non funzionante

1. Verificare la connessione di rete del POS (spia verde = connesso)
2. Spegnere e riaccendere il POS (tasto verde per 5 secondi)
3. Se persiste → ticket su coda "Installazione POS" con:
   - Numero terminale POS (etichetta sul retro)
   - Tipo di errore visualizzato
   - CAG esercente

### Storno commissioni POS

Per richiedere lo storno di commissioni POS erroneamente addebitate:
- Accedere a SIB → POS → Gestione Commissioni → Richiesta Storno
- Se il conto di addebito è già estinto: aprire ticket su coda "Storni commissioni e spese a Clienti" indicando il numero di disposizione originale

---

# APPENDICE A — NUMERI INTERNI UTILI

| Servizio | Numero Interno |
|---|---|
| Help Desk ICT (hardware/software) | 4400 |
| Tesoreria (valute/cambi) | 4421 |
| Compliance / AML | 4500 |
| Operations Centrale | 4600 |
| Back Office Crediti | 4700 |
| Gestione Immobili (REFM) | 4800 |

---

# APPENDICE B — INDICE CIRCOLARI PRINCIPALI

| Circolare | Data | Argomento principale |
|---|---|---|
| Circolare 03/2025 | Gen 2025 | F24 — nuove soglie per compensazioni IVA |
| Circolare 12/2024 | Dic 2024 | Credito — soggetti non residenti, LTV, limiti |
| Circolare 11/2023 | Nov 2023 | Monetica — conti dormienti e procedure riattivazione |
| Circolare 07/2024 | Lug 2024 | AML — paesi a rischio e procedure bonifici esteri |

---

*Fine documento — BANCA ESEMPIO S.P.A. — Solo per testing interno del chatbot*
