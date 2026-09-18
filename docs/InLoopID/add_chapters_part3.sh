#!/data/data/com.termux/files/usr/bin/bash

set -e

PROJECT="InLoopID"
CSV="$PROJECT/chapters.csv"

mkdir -p "$PROJECT"

cat >> "$CSV" <<'EOF'
101,ux,UX principy
102,ux,UI design system
103,ux,Wireframy
104,ux,Prototypy
105,ux,Design tokens
106,ux,Accessibility
107,ux,User journeys
108,ux,UX research
109,ux,A/B testování
110,ux,Feedback systém
111,ux,Analytics
112,ux,Heatmapy
113,ux,Mobile UX
114,ux,Responsive design
115,ux,Dark mode design
116,ux,Design guidelines
117,ux,Komponenty UI
118,ux,Design system architektura
119,ux,UX metriky
120,ux,Konverze
121,devops,CI/CD
122,devops,Git workflow
123,devops,Docker
124,devops,Kubernetes
125,devops,Deployment strategie
126,devops,Monitoring
127,devops,Logging
128,devops,Alerting
129,devops,Infrastructure as Code
130,devops,Terraform
131,devops,Ansible
132,devops,Scaling
133,devops,Zero downtime deploy
134,devops,Rollback strategie
135,devops,Performance tuning
136,testing,Unit testy
137,testing,Integration testy
138,testing,E2E testy
139,testing,Load testing
140,testing,Security testing
141,testing,Test automation
142,testing,Test coverage
143,testing,Mockování
144,testing,Test strategie
145,testing,QA proces
146,admin,Admin panel
147,admin,User management
148,admin,Role management
149,admin,System konfigurace
150,admin,Audit admin
EOF

echo
echo "=================================="
echo "chapters.csv doplněn"
echo "Kapitoly: 101–150"
echo "=================================="

