# INLOOPID: B2B SALES BATTLE CARDS

## 1. OBRANA PROTI NÁMITCE: "Už máme SAP / Workday, proč další systém?"
* **Argument:** InLoopID tyto systémy nenahrazuje, ale izoluje jejich riziko. Tradiční ERP systémy nemají nativní eIDAS integraci a drží data v otevřeném formátu. InLoopID funguje jako kryptografický "trezor" pro nejcitlivější dokumenty (smlouvy, NDA), čímž zmenšuje plochu pro případný útok (Attack Surface).

## 2. OBRANA PROTI NÁMITCE: "Cloudové řešení je pro nás příliš riskantní."
* **Argument:** Naopak. Tradiční cloud vyžaduje důvěru v poskytovatele. Architektura Zero-Knowledge znamená, že my, jako poskytovatelé, *nemůžeme* vaše data číst. Matematika WebCrypto API a AES-256-GCM šifrování na straně klienta garantuje, že InLoopID hostuje pouze šifrovaný šum. Riziko zneužití dat poskytovatelem je matematicky rovno nule.

## 3. OBRANA PROTI NÁMITCE: "Co když ztratíme přístupové heslo?"
* **Argument:** Naše architektura využívá Shamir's Secret Sharing (prahové sdílení). Master klíč vaší korporace je rozdělen do více částí (např. 3 členové představenstva). K obnově stačí libovolná kombinace dvou z nich. Matematicky je zajištěno, že ani únos jednoho manažera, ani ztráta jednoho disku neznamená ztrátu agendy.

## 4. OBRANA PROTI NÁMITCE: "Jak prokážeme integritu při auditu?"
* **Argument:** Auditor nepotřebuje přístup k datům, čímž se radikálně snižuje administrativní zátěž. Poskytneme mu vygenerovaný 'Audit JSON', který obsahuje kvalifikovaná časová razítka a kryptografické kotvy. Auditor si je nezávisle matematicky ověří, aniž by viděl obsah jediné smlouvy. Proces je okamžitý a plně automatizovaný.
