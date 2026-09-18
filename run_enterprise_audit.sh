#!/bin/bash
echo "--- ZAHÁJENÍ INTEGRITNÍHO A BEZPEČNOSTNÍHO AUDITU ---"
~/InloopID/security_audit.sh
echo -e "\n--- VERIFIKACE DOKUMENTŮ ---"
python3 ~/audit_tool.py ~/InloopID/audit_logs/latest_evidence.json
echo -e "\n--- AUDIT DOKONČEN. SYSTÉM JE KONTROLOVÁN. ---"
