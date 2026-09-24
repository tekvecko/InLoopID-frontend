#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - PŘÍPRAVA DISTRIBUCE PRO AWS EC2"
echo "=========================================================="

PROJECT_DIR="$HOME/InloopID"
RELEASE_DIR="$HOME/InloopID_EC2_Release"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE_NAME="InLoopID_Release_${TIMESTAMP}.tar.gz.enc"

# 1. Kompilace produkčního frontendu
echo "[*] Zahajuji kompilaci produkčního buildu frontendu..."
cd "$PROJECT_DIR/frontend"
npm run build

# 2. Příprava release struktury
echo "[*] Sestavuji strukturu pro distribuci..."
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR/frontend"
mkdir -p "$RELEASE_DIR/backend"

cp -r "$PROJECT_DIR/frontend/dist" "$RELEASE_DIR/frontend/"
cp -r "$PROJECT_DIR/backend" "$RELEASE_DIR/"
cp "$PROJECT_DIR/docker-compose.yml" "$RELEASE_DIR/" 2>/dev/null || true
cp "$PROJECT_DIR/docker-compose.preprod.yml" "$RELEASE_DIR/" 2>/dev/null || true
cp "$PROJECT_DIR/nginx.conf" "$RELEASE_DIR/" 2>/dev/null || true

# Bezpečné odstranění vývojových artefaktů z backendové složky
find "$RELEASE_DIR/backend" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$RELEASE_DIR/backend" -type d -name "venv" -exec rm -rf {} + 2>/dev/null || true
find "$RELEASE_DIR/backend" -type d -name "instance" -exec rm -rf {} + 2>/dev/null || true

# 3. Generování orchestračního manifestu pro cílový server
cat << 'EC2_EOF' > "$RELEASE_DIR/install_ec2.sh"
#!/bin/bash
set -e
echo "=========================================================="
echo " INLOOPID - INICIALIZACE AWS EC2 INFRASTRUKTURY"
echo "=========================================================="
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

# Nastavení striktních oprávnění pro Docker volumes
mkdir -p ./backend/instance
chmod 700 ./backend/instance

echo "[*] Startuji produkční kontejnery..."
docker-compose up -d --build
echo "[+] Nasazení na EC2 instanci úspěšně dokončeno."
EC2_EOF
chmod +x "$RELEASE_DIR/install_ec2.sh"

# 4. Symetrické šifrování archivu pro bezpečný SCP/SFTP transport
echo "[*] Šifruji release archiv (AES-256-CBC)..."
echo "[!] Zadejte jednorázové transportní heslo pro zašifrování balíčku:"
cd "$HOME"
tar -czf - -C "$HOME" InloopID_EC2_Release | openssl enc -aes-256-cbc -salt -pbkdf2 -out "$ARCHIVE_NAME"

# Dekontaminace dočasného sestavení
rm -rf "$RELEASE_DIR"

echo "=========================================================="
echo " [+] Distribuční balíček úspěšně vygenerován."
echo " [+] Cesta k transportnímu souboru: $HOME/$ARCHIVE_NAME"
echo " "
echo " Pro extrakci na AWS EC2 serveru použijte příkaz:"
echo " openssl enc -d -aes-256-cbc -pbkdf2 -in $ARCHIVE_NAME | tar -xz"
echo "=========================================================="
