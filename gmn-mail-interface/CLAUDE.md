# GMN Mail Interface — Runbook per Claude Code

Documento operativo per una futura sessione Claude Code: descrive il progetto,
quello che è già stato implementato, quello che resta da fare per andare in
produzione e come farlo. Tieni questo file come unica fonte di verità.

---

## 1. Cos'è

App self-hosted in due pezzi:

- **Backend FastAPI** (`backend/`): parsing email `.eml`, calcolo punteggio
  per parole chiave, stima acconto al 30%, autenticazione **magic link** via
  email, login alternativo con **Google OAuth**, ingester **IMAP** opzionale
  che scarica in background le mail dalla casella dell'utente.
- **Frontend React** (`frontend/`): schermata di login, dashboard con lista
  email processate, upload manuale `.eml`. In produzione è servito da nginx
  che fa da proxy verso il backend.

Pensata per essere deployata in un container singolo via `docker compose`.

---

## 2. Stato attuale del codice

Tutto già implementato:

```
gmn-mail-interface/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI app + lifespan che avvia l'ingester IMAP
│       ├── config.py           # pydantic-settings, legge .env
│       ├── models.py           # SQLAlchemy: User, EmailRecord
│       ├── auth.py             # JWT magic-link + session cookie
│       ├── mailer.py           # SMTP via aiosmtplib (fallback su log se non configurato)
│       ├── email_parser.py     # parsing RFC 5322
│       ├── score_calculator.py # keyword + estrazione importi
│       ├── imap_ingester.py    # loop async che polla IMAP ogni N secondi
│       └── routes.py           # /api/auth/* e /api/emails/*
├── frontend/
│   ├── Dockerfile              # build React → nginx
│   ├── nginx.conf              # serve build + proxy /api → backend:8000
│   ├── package.json
│   ├── public/index.html
│   └── src/
│       ├── index.js
│       ├── App.js              # gestisce sessione (fetch /api/auth/me)
│       └── components/
│           ├── Login.js        # form magic-link + link Google
│           ├── EmailList.js
│           └── UploadEmail.js
├── docker-compose.yml          # backend + frontend
├── .env.example                # template variabili d'ambiente
└── .gitignore
```

Endpoint backend:

| Metodo | Path                          | Descrizione                                     |
| ------ | ----------------------------- | ----------------------------------------------- |
| POST   | `/api/auth/request`           | Riceve `{email}` e invia il magic link          |
| GET    | `/api/auth/verify?token=...`  | Verifica il token, setta cookie, redirige al FE |
| POST   | `/api/auth/logout`            | Cancella il cookie sessione                     |
| GET    | `/api/auth/me`                | Profilo utente loggato                          |
| GET    | `/api/auth/google/login`      | Inizia OAuth Google (se configurato)            |
| GET    | `/api/auth/google/callback`   | Callback OAuth Google                           |
| GET    | `/api/emails`                 | Elenco email dell'utente                        |
| GET    | `/api/emails/{id}`            | Dettaglio                                       |
| POST   | `/api/emails/upload`          | Upload manuale `.eml`                           |

Sicurezza:
- Magic-link: JWT HS256 con audience dedicata, TTL 10 minuti.
- Session: JWT HS256 in cookie HttpOnly, SameSite=Lax, Secure se `APP_URL` è https.
- Allowlist email opzionale (`ALLOWED_EMAILS`).
- CORS limitato a `FRONTEND_URL`.

---

## 3. Cosa manca per deployare (azione utente richiesta)

Tutto quello che serve credenziali o piattaforme esterne. **Senza queste,
l'app gira ma non manda email e non scarica nulla dall'IMAP.**

### 3.1 Secret della sessione
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
Mettilo in `SESSION_SECRET`.

### 3.2 SMTP (per magic link)
Opzioni rapide:
- **Resend** (https://resend.com) — free tier 100 email/giorno.
  `SMTP_HOST=smtp.resend.com`, `SMTP_PORT=587`, `SMTP_USER=resend`,
  `SMTP_PASSWORD=<api-key>`.
- **SendGrid**, **Mailgun**, **Postmark** — equivalenti.
- **Gmail SMTP**: `smtp.gmail.com:587` con **App Password** (richiede 2FA).

Senza SMTP il backend logga il link su stdout invece di inviarlo: utile in dev.

### 3.3 Google OAuth (opzionale ma comodo)
1. https://console.cloud.google.com → APIs & Services → Credentials.
2. Crea "OAuth client ID" tipo "Web application".
3. Authorized redirect URI: `${APP_URL}/api/auth/google/callback`.
4. Copia Client ID e Secret in `.env`.

### 3.4 IMAP (opzionale, per ingestione automatica)
- **Gmail**: abilita 2FA e crea una App Password
  (https://myaccount.google.com/apppasswords).
  `IMAP_HOST=imap.gmail.com`, `IMAP_PORT=993`.
- Altri provider: stessa logica, vedi i loro doc.

### 3.5 Hosting
Piattaforma a piacere (in ordine di semplicità):

| Piattaforma | Note |
| ----------- | ---- |
| **Fly.io** | `fly launch` legge il `Dockerfile`. Volume persistente per SQLite. |
| **Railway** | Importa repo, espone porte 8000 e 8080 separatamente. |
| **Render** | Web service per backend, Static Site per frontend (oppure single docker). |
| **VPS** (Hetzner/DO) | `git clone`, `docker compose up -d`, reverse proxy con Caddy. |

Per qualunque opzione serve poi un **dominio** e **HTTPS**:
- Su Fly/Railway/Render i certificati sono automatici.
- Su VPS usa Caddy con `tls user@email`.

---

## 4. Procedura di deploy (locale → cloud)

### 4.1 Test in locale
```bash
cd gmn-mail-interface
cp .env.example .env
# popola almeno SESSION_SECRET e ALLOWED_EMAILS
docker compose up --build
```
Apri `http://localhost:8080`, inserisci l'email autorizzata, prendi il
magic link dal log del container backend, clicca → entri.

### 4.2 Deploy su Fly.io (esempio)
```bash
fly launch --no-deploy            # genera fly.toml
fly volumes create backend_data --size 1
fly secrets set SESSION_SECRET=... ALLOWED_EMAILS='["tu@example.com"]' \
                SMTP_HOST=... SMTP_USER=... SMTP_PASSWORD=...
fly deploy
```
Aggiorna `APP_URL` e `FRONTEND_URL` al dominio fly. Per Google OAuth
aggiungi il redirect URI nella console Google.

### 4.3 Deploy su VPS con Caddy
```bash
# sulla VPS
git clone <repo> && cd gmn-mail-interface
cp .env.example .env  # popola
docker compose up -d --build
```
Caddyfile:
```
mail.tuodominio.it {
    reverse_proxy localhost:8080
}
```

---

## 5. Cose da non dimenticare (pre-flight)

- [ ] `SESSION_SECRET` generato (≥48 byte random).
- [ ] `ALLOWED_EMAILS` contiene il tuo indirizzo (altrimenti aperto a tutti).
- [ ] `APP_URL` e `FRONTEND_URL` puntano al dominio reale (https).
- [ ] DNS A/AAAA verso il server.
- [ ] HTTPS attivo (certificato valido).
- [ ] SMTP testato (manda una mail di prova: `curl -X POST $APP_URL/api/auth/request -H 'content-type: application/json' -d '{"email":"tu@example.com"}'`).
- [ ] Backup del DB (`backend_data` volume) schedulato se ti serve persistenza.

---

## 6. Estensioni future probabili

Roba che non ho fatto perché non richiesta — annota qui se la vuoi:

- IMAP IDLE vero (push-based) invece del polling. `imap_tools` lo supporta
  via `mailbox.idle.poll(timeout=...)`. Cambia `imap_ingester.py`.
- Multi-utente: ogni utente registra le proprie credenziali IMAP cifrate
  nel DB. Oggi è single-tenant (un solo set IMAP in `.env`).
- Rate limit su `/api/auth/request` (per evitare spam magic-link).
- Migrations con Alembic invece di `create_all`.
- Tests con pytest + httpx.

---

## 7. Come usarmi (per Claude Code)

Quando l'utente apre una nuova sessione su questa cartella:

1. Leggi questo `CLAUDE.md` per primo.
2. Se l'utente chiede di "deployare", chiedi quale piattaforma vuole usare
   e quali credenziali ha pronte (SMTP? OAuth? IMAP?). Non assumere niente.
3. Se chiede modifiche al codice di auth o all'ingester, ricorda che la
   sicurezza è il punto chiave: niente token in URL log, niente secret in
   chiaro, cookie sempre HttpOnly+SameSite=Lax.
4. Non aggiungere dipendenze a caso: il `requirements.txt` è già minimale.
