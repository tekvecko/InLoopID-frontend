import os

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Záloha pro bezpečnost
with open(file_path + ".bak_crypto", 'w') as f:
    f.write(content)

# 2. Vložení skutečné WebCrypto SHA-256 funkce
crypto_func = """
  // Skutečný kryptografický engine
  const generateRealHash = async (dataStr, prefix="SHA256_") => {
      const msgUint8 = new TextEncoder().encode(dataStr);
      const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      return prefix + hashHex.toUpperCase();
  };

  const handleKeyFileUpload"""

content = content.replace("  const handleKeyFileUpload", crypto_func)

# 3. Nahrazení simulátoru u hromadné migrace
old_mock_1 = 'const mockHash = "SHA256_MIGRATED_" + Math.random().toString(36).substring(2, 10).toUpperCase();'
new_mock_1 = 'const mockHash = await generateRealHash(payloadString, "SHA256_MIGRATED_");'
content = content.replace(old_mock_1, new_mock_1)

# 4. Nahrazení simulátoru u nových smluv
old_mock_2 = 'const mockHash = "SHA256_" + Math.random().toString(36).substring(2, 10).toUpperCase();'
new_mock_2 = 'const mockHash = await generateRealHash(payloadString, "SHA256_");'
content = content.replace(old_mock_2, new_mock_2)

with open(file_path, 'w') as f:
    f.write(content)

print("[+] Simulátor vypnut. Skutečné WebCrypto SHA-256 na frontendu aktivováno.")
