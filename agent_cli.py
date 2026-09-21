#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import ast
import difflib
import subprocess

DEFAULT_LLAMA_SERVER_URL = "http://127.0.0.1:8100/v1/chat/completions"
MAX_SAFE_CHARS = 35000
STATE_FILE = ".agent_state.json"
METRICS_FILE = ".agent_metrics.jsonl"

class TeeLogger:
    """Duplikuje výstup do konzole i do textového souboru s podporou strukturovaných metrik."""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

def log_metric(event_type: str, data: dict):
    """Zapisuje strukturované metriky ve formátu JSON Lines do .agent_metrics.jsonl."""
    record = {
        "timestamp": time.time(),
        "event": event_type,
        **data
    }
    try:
        with open(METRICS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass

def save_state(state_data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=2, ensure_ascii=False)

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def clear_state():
    for f_path in [STATE_FILE, METRICS_FILE]:
        if os.path.exists(f_path):
            try:
                os.remove(f_path)
            except Exception:
                pass

def run_recovery_agent() -> dict | None:
    """Recovery Agent: Zanalyzuje stav po pádu Termuxu, zkontroluje integritu a rozhodne o dalším postupu."""
    print("\n" + "=" * 50)
    print("--- 🛡️ RECOVERY AGENT: ANALÝZA PÁDU A OBNOVENÍ ---")
    print("=" * 50)

    state = load_state()
    if not state:
        print("[!] Žádný uložený stav k obnovení (.agent_state.json) nebyl nalezen.")
        return None

    file_path = state.get("file_path")
    current_index = state.get("current_index", 0)
    steps = state.get("steps", [])

    print(f"[Recovery Agent] Cílový soubor: {file_path}")
    print(f"[Recovery Agent] Přerušené provádění na kroku: {current_index + 1}/{len(steps)}")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        is_valid, err = validate_syntax(code)
        if not is_valid:
            print(f"[!] VAROVÁNÍ: Soubor '{file_path}' obsahuje syntax error po předchozím pádu: {err}")
            backup_path = file_path + ".bak"
            if os.path.exists(backup_path):
                print(f"[Recovery Agent] Nalezena záloha ({backup_path}). Provádím automatický návrat do bezpečné verze...")
                with open(backup_path, "r", encoding="utf-8") as bf:
                    safe_code = bf.read()
                with open(file_path, "w", encoding="utf-8") as ff:
                    ff.write(safe_code)
                print("[Recovery Agent] Soubor úspěšně obnoven ze zálohy.")
            else:
                print("[!] Záloha nebyla nalezena. Před pokračováním je nutné kód ručně zkontrolovat.")
        else:
            print("[Recovery Agent] Integrita souboru (AST syntax) je v pořádku.")

    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    last_metrics = json.loads(lines[-1].strip())
                    print(f"[Recovery Agent] Poslední zaznamenaná událost v metrikách: {last_metrics.get('event')}")
        except Exception:
            pass

    print("=" * 50)
    confirm = input("[Recovery Agent] Chceš bezpečně pokračovat v plánu od přerušeného kroku? (y/n): ").strip().lower()
    if confirm == 'y':
        return state
    else:
        print("[Recovery Agent] Obnovení zrušeno uživatelem.")
        return None

def generate_lod_code(code: str, focus_pattern: str) -> str:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return _regex_fallback(code, focus_pattern)

    header_nodes = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            header_nodes.append(ast.unparse(node))
        elif isinstance(node, ast.Assign):
            is_constant = any(
                isinstance(target, ast.Name) and target.id.isupper()
                for target in node.targets
            )
            if is_constant:
                header_nodes.append(ast.unparse(node))

    header_context = "\n".join(header_nodes)

    if not focus_pattern:
        full_code = code
        if len(full_code) > MAX_SAFE_CHARS:
            return full_code[:MAX_SAFE_CHARS] + "\n... [LOD: Hard Limit Truncated] ..."
        return full_code

    regex = re.compile(focus_pattern, re.IGNORECASE)
    matched_nodes = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            node_str = ast.unparse(node)
            if regex.search(node_str):
                matched_nodes.append(node_str)

    if not matched_nodes:
        return f"# Žádné routy, funkce ani třídy neodpovídají vzoru '{focus_pattern}'"

    res_parts = []
    if header_context:
        res_parts.append("# --- Automaticky přibalené importy a konstanty ---\n" + header_context)
    
    res_parts.append("\n\n# " + "="*40 + "\n\n".join(matched_nodes))
    res_code = "\n\n".join(res_parts)

    if len(res_code) > MAX_SAFE_CHARS:
        res_code = res_code[:MAX_SAFE_CHARS] + "\n... [LOD: Hard Limit Truncated] ..."

    return res_code

def _regex_fallback(code: str, pattern: str) -> str:
    blocks = re.split(r'\n(?=@)', code)
    regex = re.compile(pattern, re.IGNORECASE)
    filtered = [b for b in blocks if regex.search(b)]
    if not filtered:
         return f"# [AST Fallback] Žádné shody pro vzor '{pattern}'"
    return "\n\n".join(filtered)

def call_llama_api(server_url: str, prompt: str, system_prompt: str, timeout: int = 600) -> str:
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "repeat_penalty": 1.18,
        "max_tokens": 2000,
        "stream": False
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        server_url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    start_time = time.time()
    try:
        print(f"[LOD Agent] Odesílám požadavek na LLM API ({len(data)} B payload)...")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - start_time
            content = result["choices"][0]["message"]["content"]
            log_metric("llm_call", {"payload_bytes": len(data), "elapsed_sec": round(elapsed, 2), "success": True})
            return content
    except Exception as e:
        elapsed = time.time() - start_time
        log_metric("llm_call", {"payload_bytes": len(data), "elapsed_sec": round(elapsed, 2), "success": False, "error": str(e)})
        print(f"[!] Chyba připojení/volání API ({server_url}): {e}")
        sys.exit(1)

def extract_python_code(llm_response: str) -> str:
    match = re.search(r"```python\n(.*?)\n```", llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    match_generic = re.search(r"```\n(.*?)\n```", llm_response, re.DOTALL)
    if match_generic:
        return match_generic.group(1).strip()
    return llm_response.strip()

def validate_syntax(code: str) -> tuple[bool, str | None]:
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError on line {e.lineno}: {e.msg}"

def integrate_code_into_original(original_code: str, candidate_code: str) -> tuple[bool, str, list[str]]:
    try:
        tree_orig = ast.parse(original_code)
        tree_cand = ast.parse(candidate_code)
    except Exception as e:
        return False, f"AST Parse Error during integration: {e}", []

    cand_nodes = {
        node.name: node
        for node in tree_cand.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }

    if not cand_nodes:
        return False, "Candidate code contains no top-level function or class definitions.", []

    orig_lines = original_code.splitlines(keepends=True)
    replaced_symbols = []

    nodes_to_replace = [
        node for node in tree_orig.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in cand_nodes
    ]
    nodes_to_replace.sort(key=lambda n: n.lineno, reverse=True)

    for node in nodes_to_replace:
        cand_node = cand_nodes[node.name]
        cand_source = ast.unparse(cand_node) + "\n"
        start_line = node.lineno - 1
        end_line = node.end_lineno
        orig_lines[start_line:end_line] = [cand_source]
        replaced_symbols.append(node.name)

    merged_code = "".join(orig_lines)
    try:
        ast.parse(merged_code)
        return True, merged_code, replaced_symbols
    except Exception as e:
        return False, f"Merged file failed AST verification: {e}", []

def run_test_command(test_cmd: str) -> tuple[bool, str]:
    if not test_cmd:
        return True, ""
    print(f"[Quality Gate] Spouštím testovací příkaz: {test_cmd}")
    start_time = time.time()
    try:
        res = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=90)
        elapsed = time.time() - start_time
        success = (res.returncode == 0)
        log_metric("gate3_test", {"command": test_cmd, "elapsed_sec": round(elapsed, 2), "success": success})
        if success:
            return True, res.stdout
        else:
            err_output = (res.stdout + "\n" + res.stderr).strip()
            return False, err_output[:1500]
    except Exception as e:
        log_metric("gate3_test", {"command": test_cmd, "success": False, "error": str(e)})
        return False, f"Test execution error: {e}"

def generate_patch(original_code: str, fixed_code: str, file_path: str) -> str:
    orig_lines = original_code.splitlines(keepends=True)
    fixed_lines = fixed_code.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines,
        fixed_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}"
    )
    return "".join(diff)

def generate_plan(file_path: str, prompt_task: str, server_url: str) -> list[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    system_prompt = (
        "You are an expert Software Architect and Planner.\n"
        "Your job is to break down a complex refactoring/feature request into a sequence of small, precise, actionable steps.\n"
        "Output ONLY a valid JSON array of strings, with NO markdown code blocks, NO preamble, and NO explanation.\n"
        "Example format: [\"Step 1: Fix validation in function_a\", \"Step 2: Add error handling in function_b\"]"
    )

    user_prompt = (
        f"Target Code Architecture (Summary):\n```python\n{generate_lod_code(code, '')[:10000]}\n```\n\n"
        f"High-Level Task: {prompt_task}\n"
        f"Create an ordered execution plan as a JSON array of strings."
    )

    for attempt in range(1, 3):
        print(f"[Planner Agent] Generuji dekompoziční plán (pokus {attempt}/2)...")
        res = call_llama_api(server_url, user_prompt, system_prompt)
        
        clean_res = res
        md_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", res, re.DOTALL)
        if md_match:
            clean_res = md_match.group(1).strip()

        try:
            start_idx = clean_res.find('[')
            end_idx = clean_res.rfind(']')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = clean_res[start_idx:end_idx+1]
                json_str = re.sub(r',\s*]', ']', json_str)
                plan_steps = json.loads(json_str)
                if isinstance(plan_steps, list) and all(isinstance(s, str) for s in plan_steps):
                    log_metric("planner_success", {"attempts": attempt})
                    return plan_steps
        except Exception as e:
            print(f"[Planner Agent] Varování: JSON parsování selhalo ({e}).")

        system_prompt = (
            "CRITICAL: Your previous response failed JSON parsing.\n"
            "You MUST output ONLY a valid JSON array of strings (e.g. [\"Step 1\", \"Step 2\"]). "
            "No markdown, no explanation, just the JSON array."
        )

    log_metric("planner_fallback", {})
    lines = [line.strip('- *') for line in res.split('\n') if line.strip().startswith(('-', '*', '1', '2', '3', '4', '5'))]
    return lines if lines else [prompt_task]

def run_auto_loop(file_path: str, focus_pattern: str, prompt_task: str, server_url: str, max_retries: int, test_cmd: str, in_place: bool) -> bool:
    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    lod_code = generate_lod_code(original_code, focus_pattern)

    print("[Gate 0: Pre-flight AST Check] Ověřuji syntaxi výchozího výřezu kódu...")
    g0_valid, g0_err = validate_syntax(lod_code)
    
    feedback_context = ""
    if not g0_valid:
        print(f"[Gate 0] Upozornění: Výchozí výřez obsahuje syntaktickou chybu: {g0_err}")
        feedback_context = f"\n\n[Gate 0 Warning - Baseline SyntaxError]: {g0_err}\nPlease address this issue."
    else:
        print("[Gate 0 PASSED] Výchozí výřez kódu je syntakticky v pořádku.")

    system_prompt = (
        "You are an expert Python Refactoring Engine.\n"
        "Your task is to fix security and logic vulnerabilities in the provided Python code snippet.\n"
        "Return ONLY the complete, corrected Python code for the target functions/classes inside ```python ``` block.\n"
        "Do NOT omit necessary imports or internal function logic. Do NOT include markdown commentary outside the code block."
    )

    feedback_prompt = (
        f"Target Python Snippet:\n```python\n{lod_code}\n```\n"
        f"{feedback_context}\n\n"
        f"Task: {prompt_task}\n"
        f"Provide the complete, corrected Python code for the analyzed snippet."
    )

    for attempt in range(1, max_retries + 1):
        print(f"\n[Auto-Loop] Iterace {attempt}/{max_retries}...")
        response = call_llama_api(server_url, feedback_prompt, system_prompt)
        candidate_code = extract_python_code(response)

        is_valid, err_msg = validate_syntax(candidate_code)
        if not is_valid:
            print(f"[Gate 1: AST Syntax] Selhala syntaktická kontrola: {err_msg}")
            log_metric("gate1_fail", {"attempt": attempt, "error": err_msg})
            feedback_prompt += (
                f"\n\n[Iteration {attempt} Failed - Gate 1 SyntaxError]: {err_msg}\n"
                f"Please fix the syntax error and return valid Python code."
            )
            continue

        log_metric("gate1_pass", {"attempt": attempt})

        is_integrated, merged_or_err, replaced_symbols = integrate_code_into_original(original_code, candidate_code)
        if not is_integrated:
            print(f"[Gate 2: AST Integration] Selhalo sloučení kódu: {merged_or_err}")
            log_metric("gate2_fail", {"attempt": attempt, "error": merged_or_err})
            feedback_prompt += (
                f"\n\n[Iteration {attempt} Failed - Gate 2 Integration Error]: {merged_or_err}\n"
                f"Ensure top-level function names match target functions."
            )
            continue

        log_metric("gate2_pass", {"attempt": attempt, "symbols": replaced_symbols})
        print(f"[Gate 1 & 2 PASSED] AST kontrola i sloučení souboru byly úspěšné!")
        print(f"   Nahrazené funkce/symboly: {', '.join(replaced_symbols)}")

        if test_cmd:
            temp_test_file = file_path + ".tmp_test"
            with open(temp_test_file, "w", encoding="utf-8") as f:
                f.write(merged_or_err)
            
            os.rename(temp_test_file, file_path + ".fixed_tmp")
            os.rename(file_path, file_path + ".orig_tmp")
            os.rename(file_path + ".fixed_tmp", file_path)

            test_passed, test_output = run_test_command(test_cmd)

            os.rename(file_path, file_path + ".fixed_tmp")
            os.rename(file_path + ".orig_tmp", file_path)

            if not test_passed:
                print(f"[Gate 3: Pytest] Testy selhaly.")
                log_metric("gate3_fail", {"attempt": attempt})
                feedback_prompt += (
                    f"\n\n[Iteration {attempt} Failed - Gate 3 Test Failures]:\n{test_output}\n"
                    f"Fix the logic so that unit tests pass."
                )
                continue
            else:
                log_metric("gate3_pass", {"attempt": attempt})
                print(f"[Gate 3 PASSED] Všechny projektové testy prošly!")

        backup_path = file_path + ".bak"
        patch_path = file_path + ".patch"
        fixed_path = file_path + ".fixed"

        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_code)

        patch_content = generate_patch(original_code, merged_or_err, file_path)
        with open(patch_path, "w", encoding="utf-8") as f:
            f.write(patch_content)

        if in_place:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(merged_or_err)
            print(f"\n[Auto-Loop] Soubor byl aktualizován přímo: {file_path}")
        else:
            with open(fixed_path, "w", encoding="utf-8") as f:
                f.write(merged_or_err)
            print(f"\n[Auto-Loop] Celý opravený soubor uložen do: {fixed_path}")

        print(f"[Auto-Loop] Unified Diff patch uložen do: {patch_path}")
        print(f"[Auto-Loop] Původní verze zálohována do: {backup_path}")
        log_metric("loop_success", {"attempt": attempt})
        return True

    print(f"[!] Auto-Loop nedosáhl platného výsledku po {max_retries} iteracích.")
    log_metric("loop_failed_max_retries", {"max_retries": max_retries})
    return False

def main():
    parser = argparse.ArgumentParser(description="AST Multi-Gate Hybrid Orchestrator for Termux")
    parser.add_argument("--file", required=True, help="Cílový soubor")
    parser.add_argument("--analyze", action="store_true", help="Jednorázový režim analýzy")
    parser.add_argument("--plan", action="store_true", help="Spustit Planner Agenta pro dekompozici úkolu")
    parser.add_argument("--resume", action="store_true", help="Obnovit přerušený běh z .agent_state.json s Recovery Agentem")
    parser.add_argument("--auto-fix", action="store_true", help="Spustit autonomní opravnou smyčku (Auto-Loop)")
    parser.add_argument("--prompt", help="Zadání / popis požadavku na opravu")
    parser.add_argument("--focus-pattern", help="Regex vzor pro fokus")
    parser.add_argument("--url", default=DEFAULT_LLAMA_SERVER_URL, help="URL llama-serveru")
    parser.add_argument("--max-retries", type=int, default=3, help="Max počet iterací pro auto-fix")
    parser.add_argument("--test-cmd", help="Volitelný testovací příkaz")
    parser.add_argument("--in-place", action="store_true", help="Přepsat původní soubor přímo")
    parser.add_argument("--log", help="Uložit kompletní výstup konzole do zadaného textového souboru")
    args = parser.parse_args()

    if args.log:
        sys.stdout = TeeLogger(args.log)
        sys.stderr = sys.stdout

    if not os.path.exists(args.file):
        print(f"[!] Soubor '{args.file}' neexistuje.")
        sys.exit(1)

    if args.resume:
        state = run_recovery_agent()
        if not state:
            sys.exit(1)
        
        print(f"[State Machine] Pokračuji v obsluze plánu pro soubor: {state['file_path']}")
        plan_steps = state["steps"]
        start_index = state["current_index"]
        file_path = state["file_path"]
        test_cmd = state["test_cmd"]
        in_place = state["in_place"]
        focus_pattern = state["focus_pattern"]
        max_retries = state["max_retries"]
        server_url = state["url"]

        print(f"[State Machine] Pokračuji od kroku {start_index + 1}/{len(plan_steps)}...")
        for i in range(start_index, len(plan_steps)):
            step = plan_steps[i]
            print(f"\n>>> [RESUME] REALIZACE KROKU {i+1}/{len(plan_steps)}: {step}")
            success = run_auto_loop(file_path, focus_pattern, step, server_url, max_retries, test_cmd, in_place)
            if not success:
                print(f"[!] Krok {i+1} selhal. Ukládám aktuální pozici pro možnost opakování.")
                state["current_index"] = i
                save_state(state)
                sys.exit(1)
            state["current_index"] = i + 1
            save_state(state)

        print("\n[State Machine] Všechny zbývající kroky byly úspěšně dokončeny!")
        clear_state()
        return

    if args.plan:
        if not args.prompt:
            print("[!] Mód --plan vyžaduje parametr --prompt.")
            sys.exit(1)
        plan_steps = generate_plan(args.file, args.prompt, args.url)
        print("\n" + "=" * 50)
        print("--- NÁVRH PLÁNU REALIZACE (PLANNER AGENT) ---")
        print("=" * 50)
        for i, step in enumerate(plan_steps, 1):
            print(f"{i}. {step}")
        print("=" * 50)

        if args.auto_fix:
            print("\n[Planner Orchestrator] Zahajuji sekvenční realizaci plánu krok za krokem...")
            state = {
                "file_path": args.file,
                "prompt": args.prompt,
                "steps": plan_steps,
                "current_index": 0,
                "test_cmd": args.test_cmd,
                "in_place": args.in_place,
                "focus_pattern": args.focus_pattern,
                "max_retries": args.max_retries,
                "url": args.url
            }
            save_state(state)

            for i, step in enumerate(plan_steps):
                print(f"\n>>> REALIZACE KROKU {i+1}/{len(plan_steps)}: {step}")
                success = run_auto_loop(args.file, args.focus_pattern, step, args.url, args.max_retries, args.test_cmd, args.in_place)
                if not success:
                    print(f"[!] Krok {i+1} selhal. Stav byl uložen. Po opravě můžeš pokračovat přepínačem --resume.")
                    state["current_index"] = i
                    save_state(state)
                    sys.exit(1)
                
                state["current_index"] = i + 1
                save_state(state)

            print("\n[Planner Orchestrator] Všechny kroky plánu byly úspěšně dokončeny!")
            clear_state()
        return

    if args.auto_fix:
        if not args.prompt:
            print("[!] Mód --auto-fix vyžaduje parametr --prompt.")
            sys.exit(1)
        run_auto_loop(args.file, args.focus_pattern, args.prompt, args.url, args.max_retries, args.test_cmd, args.in_place)
    elif args.analyze:
        with open(args.file, "r", encoding="utf-8") as f:
            original_code = f.read()

        lod_code = generate_lod_code(original_code, args.focus_pattern)
        system_prompt = (
            "You are a senior Application Security Auditor. Analyze the provided Python code.\n"
            "Identify input validation issues, OIDC flow flaws (state/nonce), JWT claim checks, and unhandled NULL/None exceptions.\n"
            "Provide concise, technical feedback in Czech language."
        )
        task_desc = args.prompt if args.prompt else "Proveď bezpečnostní review."
        custom_prompt = f"Kód k analýze:\n```python\n{lod_code}\n```\n\nÚkol: {task_desc}"
        res = call_llama_api(args.url, custom_prompt, system_prompt)
        print("\n" + "=" * 50)
        print(res)
        print("=" * 50)

if __name__ == "__main__":
    main()
