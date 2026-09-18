#!/data/data/com.termux/files/usr/bin/bash

set -e

PROJECT="InLoopID"
CSV="$PROJECT/chapters.csv"

mkdir -p "$PROJECT"

cat >> "$CSV" <<'EOF'
51,architecture,Security architektura
52,architecture,Scalability návrh
53,architecture,Load balancing
54,architecture,Caching vrstva
55,architecture,Message queue
56,architecture,Event-driven design
57,architecture,State management
58,architecture,Failover strategie
59,architecture,High availability
60,architecture,Cloud deployment
61,security,Bezpečnostní model
62,security,Autentizace
63,security,Autorizace
64,security,Role-based access control
65,security,OAuth2
66,security,JWT
67,security,Šifrování dat
68,security,Transport Layer Security
69,security,Audit logy
70,security,Penetrační testy
71,security,Threat modeling
72,security,OWASP
73,security,GDPR compliance
74,security,Data retention
75,security,Backup strategie
76,gdpr,GDPR přehled
77,gdpr,Zpracování osobních údajů
78,gdpr,Práva subjektů údajů
79,gdpr,Consent management
80,gdpr,Data anonymizace
81,gdpr,Data pseudonymizace
82,gdpr,Right to be forgotten
83,gdpr,Data export
84,gdpr,Incident reporting
85,integrations,API integrace
86,integrations,Webhooky
87,integrations,ERP integrace
88,integrations,CRM integrace
89,integrations,Email integrace
90,integrations,SMS gateway
91,integrations,OAuth integrace
92,integrations,Third-party services
93,integrations,Rate limiting
94,integrations,API versioning
95,api,REST API
96,api,GraphQL
97,api,OpenAPI spec
98,api,Endpoint design
99,api,Error handling
100,api,Pagination
EOF

echo
echo "=================================="
echo "chapters.csv doplněn"
echo "Kapitoly: 51–100"
echo "=================================="

