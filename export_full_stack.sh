#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - EXPORT KOMPLETNÍHO KÓDU (FRONTEND + BACKEND)"
echo "=========================================================="

python3 << 'PY_EOF'
import os

project_dir = os.path.expanduser("~/InloopID")
output_file = os.path.expanduser("~/InloopID_FullStack_Export.txt")

# Striktní filtrace adresářů pro zachování relevance a optimální velikosti
exclude_dirs = {".git", "node_modules", "venv", "__pycache__", "dist", "build", "mail_spool", ".vite"}

# Definice auditovaných přípon souborů
allowed_exts = {".js", ".jsx", ".py", ".json", ".yml", ".yaml", ".conf", ".env.example", ".sh", ".css", ".md"}

with open(output_file, "w", encoding="utf-8") as out_f:
    out_f.write("================================================================================\n")
    out_f.write(" INLOOPID ENTERPRISE - KOMPLETNÍ ZDROJOVÝ KÓD (FRONTEND & BACKEND)\n")
    out_f.write("================================================================================\n\n")

    for root, dirs, files in os.walk(project_dir):
        # Odstranění ignorovaných adresářů z aktuálního průchodu
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in sorted(files):
            ext = os.path.splitext(file)[1].lower()
            
            # Kontrola povolené přípony a ignorování bezpečnostních záloh
            if ext in allowed_exts and ".bak" not in file:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, project_dir)
                
                try:
                    with open(filepath, "r", encoding="utf-8") as in_f:
                        content = in_f.read()

                    out_f.write("=" * 80 + "\n")
                    out_f.write(f" SOUBOR: {file}\n")
                    out_f.write(f" CESTA:  /{rel_path}\n")
                    out_f.write("=" * 80 + "\n\n")
                    out_f.write(content)
                    out_f.write("\n\n\n")
                except UnicodeDecodeError:
                    pass # Ignorování případných binárních souborů bez přerušení chodu
                except Exception as e:
                    out_f.write(f"// [!] KRITICKÁ CHYBA PŘI ČTENÍ SOUBORU {file}: {str(e)}\n\n")

print(f"[+] Full-stack export byl úspěšně vygenerován.")
print(f"[+] Výstupní soubor uložen do: {output_file}")
PY_EOF

echo "=========================================================="
echo " HOTOVO. Soubor InloopID_FullStack_Export.txt je připraven."
echo "=========================================================="
