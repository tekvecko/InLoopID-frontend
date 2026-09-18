# InLoopID - Enterprise HR Architektura (Slepý Notář)

## Koncept a Bezpečnost (Zero-Knowledge)
InLoopID je decentralizovaná B2B SaaS platforma pro správu pracovněprávních dokumentů. Systém je navržen na principu **Slepého notáře**.
- **Backend nikdy nevidí obsah smluv:** HR Velín šifruje data lokálně v prohlížeči před odesláním na server. Server uchovává pouze zašifrovaný payload a kryptografický otisk (SHA-256 hash).
- **MojeID Integrace:** Zaměstnanci se do trezoru přihlašují výhradně ověřenou národní identitou.
- **Real-time synchronizace (Smart Polling):** Místo blokujících WebSockets (které by zahltily jednovláknový mobilní Flask server v Termuxu) využíváme optimalizované asynchronní dotazování každé 3 vteřiny.

## Moduly systému

### 1. HR Velín (HRDashboard.jsx)
- **Hromadná Migrace (CSV/TXT Dropzone):** Lokální čtení souborů pomocí `FileReader`. Parser inteligentně ignoruje balast (např. systémová ID) a přesně mapuje Jméno, Příjmení, E-mail, Pozici a Datum nástupu. Podporuje nahrání více souborů naráz.
- **Interaktivní validace:** Záznamy lze před zašifrováním ručně upravovat (včetně e-mailu). Rozbité záznamy (např. chybějící e-mail či smlouva) jsou vizuálně zvýrazněny červeně. Lze filtrovat a řadit podle 10 kritérií.
- **Historické smlouvy:** HR může ke každému zaměstnanci přiložit URL odkaz na cloud, nebo nahrát fyzický soubor, který se zašifruje (Data URI) a vloží do databáze.
- **Právní Radar & PDF Audit:** Generování kryptografického důkazu o shodě (F-PDF s plnou podporou českého UTF-8 fontu Roboto a wrapováním dlouhých DID/Hash řetězců na nové řádky).

### 2. Zaměstnanecký Trezor (EmployeePortal.jsx)
- **Přístup přes DID:** Data se odemykají pouze úspěšným JWT tokenem z MojeID.
- **Otevírání smluv:** Lokální dešifrování dat o odměně a pozici.
- **Zpětná kompatibilita:** Vizuální odlišení historických smluv od nových. Možnost stažení přiložených souborů přímo ze šifrovaného payloadu nebo přesměrování na firemní cloud.

## Vývojové prostředí
- **OS:** Android (Termux)
- **Frontend:** React, Vite, Tailwind CSS, Lucide-React
- **Backend:** Flask, FPDF, SQLite, WebCrypto API (frontend delegace)
- **Design Jazyk:** Striktní "Navy Blue" enterprise paleta, responzivní UI, ohraničené Dropzone sekce pro drag&drop.

*Poslední aktualizace dokumentace provedena automatizovaným skriptem.*
