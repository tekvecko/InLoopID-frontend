#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

LLAMA_SERVER_URL = "http://127.0.0.1:8080/v1/chat/completions"
MAX_FILE_SIZE_KB = 50

def run_command(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def print_project_structure():
    print("[Agent] Hlavní soubory projektu:")
    cmd = r'find . -maxdepth 3 -not -path "*/.*" -not -path "*/node_modules/*" -not -path "*/venv/*" \( -name "*.py" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.rs" \)'
    code, out, err = run_command(cmd)
    if code == 0 and out:
        lines = out.splitlines()[:15]
        print("\n".join(lines))
        if len(out.splitlines()) > 15:
            print("... (a další)")
    else:
        print(f"[!] Nelze načíst strukturu: {err}")
    print("-" * 50)

class GitGuard:
    def __init__(self):
        code, _, _ = run_command("git rev-parse --is-inside-work-tree")
        if code != 0:
            print("[!] Chyba: Aktuální adresář není Git repozitář.")
            sys.exit(1)

    def create_checkpoint(self, task_name):
        print("[GitGuard] Vytvářím před-změnový checkpoint...")
        run_command("git add -A")
        code, _, err = run_command(f'git commit -m "agent: checkpoint [{task_name}]" --allow-empty')
        if code != 0:
            print(f"[!] Chyba při vytváření checkpointu: {err}")
            return False
        return True

    def rollback(self):
        print("[GitGuard] Test selhal nebo změna byla odmítnuta. Provádím rollback (git reset --hard HEAD)...")
        code, _, err = run_command("git reset --hard HEAD")
        if code == 0:
            print("[GitGuard] Rollback úspěšně dokončen. Soubory jsou v původním stavu.")
        else:
            print(f"[!] Kritická chyba při rollbacku: {err}")

    def finalize(self, task_name):
        print(f"[GitGuard] Změny byly úspěšně potvrdzeny pro úkol: {task_name}")

def call_llama_api(prompt, system_prompt):
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "stream": False
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        LLAMA_SERVER_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.URLError as e:
        print(f"[!] Chyba při připojování k llama-serveru na portu 8080: {e}")
        sys.exit(1)

def extract_code(llm_response):
    if "```" in llm_response:
        lines = llm_response.splitlines()
        code_lines = []
        inside_block = False
        for line in lines:
            if line.startswith("```"):
                inside_block = not inside_block
                continue
            if inside_block:
                code_lines.append(line)
        return "\n".join(code_lines)
    return llm_response

def main():
    parser = argparse.ArgumentParser(description="Termux Multi-Agent Orchestrator CLI")
    parser.add_argument("--file", required=True, help="Cílový soubor k úpravě nebo analýze")
    parser.add_argument("--analyze", action="store_true", help="Režim analýzy kódu (čtení bez úprav)")
    parser.add_argument("--prompt", help="Zadání úpravy nebo specifického zaměření analýzy")
    parser.add_argument("--test-cmd", help="Příkaz pro verifikaci změn (vyžadováno bez --analyze)")
    args = parser.parse_args()

    if not args.analyze and (not args.prompt or not args.test_cmd):
        parser.error("--prompt a --test-cmd jsou vyžadovány, pokud není použit příznak --analyze.")

    target_file = args.file

    if not os.path.exists(target_file):
        print(f"[!] Soubor '{target_file}' neexistuje.")
        sys.exit(1)

    file_size_kb = os.path.getsize(target_file) / 1024
    if file_size_kb > MAX_FILE_SIZE_KB:
        print(f"[!] Bezpečnostní stop: Soubor '{target_file}' je příliš velký ({file_size_kb:.1f} KB).")
        sys.exit(1)

    with open(target_file, "r", encoding="utf-8") as f:
        original_code = f.read()

    if args.analyze:
        print(f"[Agent] Spouštím BEZPEČNOSTNÍ A ARCHITEKTONICKOU ANALÝZU pro: {target_file}")
        system_prompt = (
            "Jsi seniorní IT architekt a bezpečnostní auditor v prostředí Termux.\n"
            "Analyze the target code for potential vulnerabilities, architectural weaknesses, syntax/type issues, error handling, and optimization opportunities.\n"
            "Provide a concise, clear, and structured audit report in Czech with prioritized actionable recommendations."
        )
        custom_focus = f"\nSpecifické zaměření: {args.prompt}" if args.prompt else ""
        full_llm_prompt = (
            f"Kód souboru {target_file}:\n\n```\n{original_code}\n```{custom_focus}\n\n"
            "Proveď kompletní audit tohoto kódu."
        )
        print("[Agent] Odesílám kód k analýze lokálnímu modelu...\n" + "=" * 50)
        analysis_res = call_llama_api(full_llm_prompt, system_prompt)
        print(analysis_res)
        print("=" * 50)
        sys.exit(0)

    print_project_structure()

    user_prompt = args.prompt
    test_cmd = args.test_cmd

    guard = GitGuard()
    if not guard.create_checkpoint(user_prompt[:30]):
        sys.exit(1)

    system_prompt = (
        "Jsi seniorní Coder Agent v prostředí Termux.\n"
        "Uprav poskytnutý kód přesně podle požadavků.\n"
        "Vrať VÝHRADNĚ kompletní nový zdrojový kód bez jakéhokoliv úvodního nebo závěrečného textu."
    )
    full_llm_prompt = (
        f"Původní kód souboru {target_file}:\n\n```\n{original_code}\n```\n\n"
        f"Požadovaná změna: {user_prompt}\n\nVrať kompletní nový obsah souboru."
    )

    print("[Agent] Posílám zadání lokálnímu modelu...")
    response = call_llama_api(full_llm_prompt, system_prompt)
    new_code = extract_code(response)

    print(f"[Agent] Zapisuji navržené změny do {target_file}...")
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_code)

    print(f"[Tester] Spouštím testovací příkaz: '{test_cmd}'...")
    code, out, err = run_command(test_cmd)

    if code == 0:
        print("\n[Tester] VERIFIKACE ÚSPĚŠNÁ! (Return code 0)")
        if out: print(f"STDOUT:\n{out}\n")
        confirm = input("[Approval] Chceš změny ponechat? (y/n): ").strip().lower()
        if confirm == 'y': guard.finalize(user_prompt[:30])
        else: guard.rollback()
    else:
        print("\n[Tester] VERIFIKACE SELHALA! (Return code != 0)")
        if err: print(f"STDERR:\n{err}\n")
        elif out: print(f"STDOUT:\n{out}\n")
        guard.rollback()

if __name__ == "__main__":
    main()
