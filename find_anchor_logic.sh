#!/bin/bash
echo "=========================================================="
echo " INLOOPID - LOKALIZACE ŠIFROVACÍ LOGIKY (READ-ONLY)"
echo "=========================================================="
echo "[*] Hledám volání API endpointu pro ukotvení:"
grep -rnw ~/InloopID/frontend/src/ -e "anchor-credential" -A 5 -B 5
echo ""
echo "[*] Hledám generování payloadu:"
grep -rnw ~/InloopID/frontend/src/ -e "encrypted_payload" -A 5 -B 5
echo "=========================================================="
