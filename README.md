# InLoopID Enterprise Platform

Autonomní HR platforma garantující digitální suverenitu a soulad s eIDAS pomocí Zero-Knowledge kryptografie.

## Architektura
Systém je rozdělen na dvě hlavní části:
1. **Frontend (React / Vite):** Zajišťuje veškerou kryptografickou logiku. Provádí lokální šifrování dat (AES-256-GCM), asymetrické podepisování (ECDSA P-256) a renderování PDF (pdfMake).
2. **Backend (Flask / SQLite):** Funguje výhradně jako "Slepý notář". Přijímá, ukládá a distribuuje kryptografický šum. Nezná klíče, nemá přístup k osobním údajům. Řeší SMTP komunikaci a integraci s MojeID.

## Integrace MojeID
Systém využívá standard OpenID Connect pro ztotožnění uchazeče s úrovní záruky "Značná" (nebo Vysoká). Osobní údaje (jméno, adresa, datum narození) jsou načteny až na straně klienta do lokální paměti prohlížeče a vloženy do smlouvy před jejím podepsáním.

## Zabezpečení (Shamir's Secret Sharing)
Modul Kapsle (Cold Vault) umožňuje vyexportovat off-grid zálohu celé agendy ve formátu HTML. Hlavní heslo je kryptograficky fragmentováno, pro jeho obnovu je nutná účast minimálně 2 ze 3 oprávněných osob.

## Spuštění (Termux prostředí)
Platforma je optimalizována pro běh na mobilním zařízení (ARM64). Ke startu obou serverů použijte:
\`./InLoopID_launcher.sh\`
