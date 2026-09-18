#!/data/data/com.termux/files/usr/bin/bash

set -e

PROJECT="InloopID"

echo "[INFO] Creating test environment..."

mkdir -p "$PROJECT/docs/executive"
mkdir -p "$PROJECT/docs/business"
mkdir -p "$PROJECT/docs/product"
mkdir -p "$PROJECT/docs/architecture"

cat > "$PROJECT/chapters.csv" <<'EOF'
1,executive,Executive Summary
2,executive,Vize projektu
3,business,Business model
4,business,Tržní analýza
5,product,Přehled funkcí
6,product,Workflow systému
7,architecture,System architecture overview
8,architecture,Datový model
EOF

cat > "$PROJECT/docs/index.md" <<'EOF'
# InloopID Test Documentation

Testovací prostředí generátoru dokumentace.
EOF

echo "[OK] Test environment ready"
echo "Next: python3 python/mkdocs_generator.py"
