# Všeobecné obchodní podmínky a Podmínky užití služby InLoopID

Tyto podmínky upravují práva a povinnosti mezi poskytovatelem služby InLoopID (dále jen "Poskytovatel") a firemním klientem (dále jen "Tenant") využívajícím platformu pro správu pracovněprávních dokumentů.

## 1. Definice služby a Architektura
1.1. **InLoopID** je B2B (Business-to-Business) softwarová platforma poskytovaná formou SaaS (Software as a Service). Slouží jako kryptografický trezor pro uzavírání a archivaci pracovněprávních vztahů.
1.2. **Zero-Knowledge (Slepý notář):** Služba je vybudována na architektuře nulové znalosti (Zero-Knowledge). Poskytovatel poskytuje výhradně technologickou infrastrukturu a funguje jako "slepý notář". Veškeré dokumenty a osobní údaje jsou šifrovány symetrickou a asymetrickou kryptografií přímo na koncových zařízeních uživatelů (Tenantů a jejich zaměstnanců).
1.3. Poskytovatel nemá k dispozici dešifrovací klíče, nemá přístup k textu smluv, osobním údajům ani mzdovým podmínkám, a nedokáže tyto informace na svých serverech rekonstruovat.

## 2. Nařízení o digitálních službách (DSA) a Odpovědnost za obsah
2.1. **Kvalifikace služby:** InLoopID spadá pod definici poskytovatele hostingových služeb ve smyslu nařízení EU 2022/2065 (DSA). Služba není online platformou (nešíří informace veřejnosti).
2.2. **Vyloučení odpovědnosti:** V souladu s článkem 6 DSA nenese Poskytovatel žádnou odpovědnost za informace ukládané na žádost Tenanta. Za obsah veškerých generovaných a ukládaných dokumentů nese výhradní právní odpovědnost Tenant.
2.3. **Absence monitorování:** Poskytovatel výslovně prohlašuje, že v souladu s článkem 8 DSA a z důvodu koncové (end-to-end) kryptografie neprovádí žádné proaktivní monitorování uloženého obsahu ani nevyhledává skutečnosti naznačující protiprávní činnost. 
2.4. **Moderování obsahu:** Služba neuplatňuje žádné algoritmické moderování obsahu (článek 14 DSA).

## 3. Ochrana osobních údajů (GDPR) a Datová minimalizace
3.1. Zpracování osobních údajů probíhá v režimu "Záměrné a standardní ochrany" (Data Protection by Design).
3.2. **Klientská hydratace:** Systém standardně neukládá identifikační údaje zaměstnanců do databáze v otevřené formě. Osobní data získávaná prostřednictvím státní identity (MojeID) jsou přenášena výhradně do paměti prohlížeče uživatele, kde jsou bezprostředně vložena do dokumentu a zašifrována (princip datové minimalizace).
3.3. **Právo být zapomenut:** Poskytovatel zajišťuje výkon práva na výmaz cestou "Kryptografické skartace" (Cryptographic Shredding). Na žádost dojde k nevratnému zničení dešifrovacích klíčů a kryptografických hašů, čímž se uložený obsah stane trvale nepřístupným a plně anonymizovaným.

## 4. Elektronická identifikace a Podpis (eIDAS / ZP)
4.1. Přístup k zaměstnaneckým dokumentům a jejich následný podpis je podmíněn úspěšnou autentizací přes službu MojeID (nebo jiný podporovaný prostředek el. identity).
4.2. Tenant bere na vědomí, že InLoopID zajišťuje nezvratný kryptografický auditní záznam spojující identitu uživatele (odvozenou z MojeID) s časovým razítkem a hashem dokumentu, což slouží jako průkazný materiál pro potřeby plnění povinností dle Zákoníku práce ČR.

## 5. Zneužití služby a Kontaktní místa
5.1. Tenant se zavazuje, že nebude využívat platformu k činnostem, které jsou v rozporu s právním řádem České republiky nebo Evropské unie.
5.2. **Hlášení nezákonného obsahu:** V souladu s článkem 16 DSA mohou orgány veřejné moci i jednotlivci nahlásit zneužití infrastruktury na e-mailové adrese: `legal@inloopid.com`. 
5.3. Ačkoliv Poskytovatel nezná obsah dat, v případě legitimního příkazu orgánu veřejné moci je oprávněn omezit přístup Tenanta k infrastruktuře. V takovém případě poskytne Tenantovi odůvodnění v souladu s článkem 17 DSA.

## 6. Závěrečná ustanovení
6.1. Poskytovatel si vyhrazuje právo omezit nebo ukončit poskytování služby Tenantovi v případě porušení těchto podmínek.
6.2. Tyto podmínky nabývají účinnosti dnem jejich zveřejnění.
