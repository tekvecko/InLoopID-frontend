import os

files = [
    os.path.expanduser('~/InloopID/frontend/src/components/HRDashboard.jsx'),
    os.path.expanduser('~/InloopID/frontend/src/components/EmployeePortal.jsx')
]

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if 'const BACKEND_URL =' in line:
                    # Striktní vložení bez escapovacích znaků
                    f.write("const BACKEND_URL = `http://${window.location.hostname}:5000/api/v1`;\n")
                else:
                    f.write(line)
        print(f"[OK] Syntaktická chyba odstraněna v souboru: {os.path.basename(file_path)}")
    else:
        print(f"[CHYBA] Soubor nebyl nalezen: {file_path}")
