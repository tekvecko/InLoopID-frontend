#!/data/data/com.termux/files/usr/bin/bash

set -e

PROJECT="InLoopID"
CSV="$PROJECT/chapters.csv"

mkdir -p "$PROJECT"

cat >> "$CSV" <<'EOF'
151,finance,Finanční model
152,finance,Cost struktura
153,finance,Revenue streams
154,finance,Profit analýza
155,finance,Break-even point
156,finance,Budget plánování
157,finance,Cashflow
158,finance,Investiční návratnost
159,finance,Riziková analýza
160,finance,Finanční reporting
161,marketing,Marketing strategie
162,marketing,Branding
163,marketing,SEO strategie
164,marketing,Content marketing
165,marketing,Social media
166,marketing,Email kampaně
167,marketing,PPC reklama
168,marketing,Lead generation
169,marketing,Conversion funnel
170,marketing,Marketing analytika
171,support,Helpdesk
172,support,Ticketing systém
173,support,Knowledge base
174,support,SLAs
175,support,Customer success
176,support,Chatbot support
177,support,Incident management
178,support,Feedback loop
179,support,Escalation proces
180,support,Support analytika
181,investors,Pitch deck
182,investors,Valuace
183,investors,Equity struktura
184,investors,Due diligence
185,investors,Investor reporting
186,appendix,Glosář
187,appendix,Reference a zdroje
EOF

echo
echo "=================================="
echo "chapters.csv DOKONČEN"
echo "Celkem kapitol: 187"
echo "=================================="

