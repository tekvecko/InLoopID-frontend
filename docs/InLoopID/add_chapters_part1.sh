#!/data/data/com.termux/files/usr/bin/bash

set -e

PROJECT="InLoopID"
CSV="$PROJECT/chapters.csv"

mkdir -p "$PROJECT"

cat > "$CSV" <<'EOF'
1,executive,Executive Summary
2,executive,Vize
3,executive,Mise
4,executive,Hodnoty
5,executive,Strategické cíle
6,executive,Historie projektu
7,executive,Roadmap
8,executive,Milníky
9,executive,KPI
10,executive,Přehled produktu
11,business,Business model
12,business,Lean Canvas
13,business,Business Model Canvas
14,business,Value Proposition
15,business,SWOT
16,business,PESTLE
17,business,Tržní analýza
18,business,TAM
19,business,SAM
20,business,SOM
21,business,Segmentace zákazníků
22,business,Persony
23,business,Konkurenční analýza
24,business,Cenová strategie
25,business,ROI
26,business,Go-To-Market
27,business,Sales strategie
28,business,Partnerský program
29,business,Investorská strategie
30,product,Přehled funkcí
31,product,Workflow
32,product,Uživatelské role
33,product,Životní cyklus zaměstnance
34,product,Životní cyklus dokumentu
35,product,Schvalovací procesy
36,product,Automatizace
37,product,AI funkce
38,product,Notifikace
39,product,Dashboardy
40,product,Reporty
41,product,Audit
42,product,Exporty
43,product,Importy
44,architecture,Přehled architektury
45,architecture,Backend
46,architecture,Frontend
47,architecture,API Gateway
48,architecture,Databáze
49,architecture,Datový model
50,architecture,Mikroslužby
EOF

echo
echo "=================================="
echo "chapters.csv vytvořen"
echo "Kapitoly: 1–50"
echo "=================================="

