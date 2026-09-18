#!/bin/bash
echo "=========================================================="
echo " VÝPIS CHYBNÉHO BLOKU LANDINGPAGE.JSX (Řádky 490-530)"
echo "=========================================================="
awk 'NR>=490 && NR<=530 {printf "%4d: %s\n", NR, $0}' ~/InloopID/frontend/src/components/LandingPage.jsx
echo "=========================================================="
