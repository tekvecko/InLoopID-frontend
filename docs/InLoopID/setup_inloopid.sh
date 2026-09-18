#!/data/data/com.termux/files/usr/bin/bash

set -e

PROJECT="InLoopID"

echo "====================================="
echo " InLoopID Enterprise Documentation"
echo "====================================="

mkdir -p "$PROJECT"

cd "$PROJECT"

mkdir -p \
docs \
docs/assets \
docs/images \
docs/styles \
docs/scripts \
docs/templates \
docs/diagrams \
docs/openapi \
docs/uml \
docs/bpmn \
docs/c4 \
docs/adr \
docs/reference \
docs/generated \
docs/api \
docs/business \
docs/security \
docs/gdpr \
docs/devops \
docs/testing \
docs/ux \
docs/admin \
docs/finance \
docs/marketing \
docs/support \
docs/investors \
docs/appendix

mkdir -p \
scripts \
python \
config \
build \
output \
logs \
cache \
exports \
tmp \
.github/workflows

touch \
chapters.csv \
mkdocs.yml \
README.md \
requirements.txt \
.gitignore

cat > .gitignore <<EOF
.cache
build
output
exports
tmp
*.pyc
__pycache__
EOF

cat > requirements.txt <<EOF
mkdocs
mkdocs-material
mkdocs-mermaid2-plugin
pymdown-extensions
jinja2
pyyaml
rich
click
markdown
EOF

echo "# InLoopID Enterprise Documentation" > README.md

echo
echo "Projekt vytvořen."
echo
echo "Adresář:"
pwd

