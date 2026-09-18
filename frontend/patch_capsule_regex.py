import os

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, 'r') as f:
    content = f.read()

# Ochrana proti neviditelným znakům z clipboardu
old_line = "const words = document.getElementById('seed').value.trim().toLowerCase();"
new_line = "const words = document.getElementById('seed').value.trim().toLowerCase().replace(/\\s+/g, ' ');"

if old_line in content:
    content = content.replace(old_line, new_line)
    with open(file_path, 'w') as f:
        f.write(content)
    print("[+] Kapsle zabezpečena proti chybám schránky (Regex normalizace mezer).")
else:
    print("[-] Kód pro nahrazení nenalezen. Je možné, že patch byl již aplikován.")

