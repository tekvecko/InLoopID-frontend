#!/usr/bin/env python3
import unittest
from unittest.mock import patch
import os
import sys

# Import funkcí k otestování z agent_cli.py
from agent_cli import (
    generate_lod_code,
    extract_python_code,
    validate_syntax,
    integrate_code_into_original,
    generate_patch,
    generate_plan
)

class TestAgentCLIOrchestrator(unittest.TestCase):

    def test_extract_python_code(self):
        """Testuje extrakci čistého kódu z různých formátů Markdown odpovědí LLM."""
        raw_markdown = "Zde je opravená funkce:\n```python\ndef foo():\n    return True\n```\nSnad to pomůže!"
        self.assertEqual(extract_python_code(raw_markdown), "def foo():\n    return True")

        generic_markdown = "```\ndef bar():\n    pass\n```"
        self.assertEqual(extract_python_code(generic_markdown), "def bar():\n    pass")

        plain_text = "def baz():\n    return 42"
        self.assertEqual(extract_python_code(plain_text), "def baz():\n    return 42")

    def test_validate_syntax(self):
        """Testuje Gate 1: Ověření syntaktické správnosti Python kódu."""
        valid_code = "def add(a, b):\n    return a + b"
        is_valid, err = validate_syntax(valid_code)
        self.assertTrue(is_valid)
        self.assertIsNone(err)

        invalid_code = "def add(a, b\n    return a + b"
        is_valid, err = validate_syntax(invalid_code)
        self.assertFalse(is_valid)
        self.assertIsNotNone(err)
        self.assertIn("SyntaxError", err)

    def test_generate_lod_code(self):
        """Testuje AST LOD Engine: Ořezání kódu na vybrané funkce dle vzoru."""
        sample_code = (
            "import os\n\n"
            "def login_user():\n"
            "    return 'login'\n\n"
            "def logout_user():\n"
            "    return 'logout'\n"
        )
        lod = generate_lod_code(sample_code, "login_user")
        self.assertIn("def login_user()", lod)
        self.assertNotIn("def logout_user()", lod)

        lod_none = generate_lod_code(sample_code, "nonexistent_function")
        self.assertIn("Žádné routy", lod_none)

    def test_integrate_code_into_original(self):
        """Testuje Gate 2: Bezpečné nahrazení opravené funkce s zachováním komentářů a zbytku souboru."""
        original_code = (
            "#!/usr/bin/env python3\n"
            "# Původní komentář\n"
            "import math\n\n"
            "def compute(x):\n"
            "    return x * 2\n\n"
            "def keep_this():\n"
            "    return 'untouched'\n"
        )
        candidate_code = (
            "def compute(x):\n"
            "    # Opravený výpočet\n"
            "    return math.pow(x, 2)\n"
        )

        success, merged_code, replaced = integrate_code_into_original(original_code, candidate_code)
        self.assertTrue(success)
        self.assertIn("compute", replaced)
        self.assertIn("#!/usr/bin/env python3", merged_code)
        self.assertIn("# Původní komentář", merged_code)
        self.assertIn("def keep_this():", merged_code)
        self.assertIn("math.pow(x, 2)", merged_code)

    def test_generate_patch(self):
        """Testuje generování Unified Diff (.patch)."""
        orig = "a = 1\nb = 2\n"
        fixed = "a = 1\nb = 3\n"
        patch = generate_patch(orig, fixed, "app.py")
        self.assertIn("--- a/app.py", patch)
        self.assertIn("+++ b/app.py", patch)
        self.assertIn("-b = 2", patch)
        self.assertIn("+b = 3", patch)

    @patch('agent_cli.call_llama_api')
    def test_generate_plan_json(self, mock_api):
        """Testuje Planner Agent: Extrakce strukturovaného plánu z JSON odpovedi."""
        mock_api.return_value = '[\"Krok 1: Pridať validáciu\", \"Krok 2: Ošetriť výnimku\"]'
        
        # Vytvoření dočasného testovacího souboru
        test_file = "test_dummy.py"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("def dummy(): pass\n")

        try:
            plan = generate_plan(test_file, "Refaktoruj dummy", "http://fake-url")
            self.assertEqual(len(plan), 2)
            self.assertEqual(plan[0], "Krok 1: Pridať validáciu")
            self.assertEqual(plan[1], "Krok 2: Ošetriť výnimku")
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    @patch('agent_cli.call_llama_api')
    def test_generate_plan_text_fallback(self, mock_api):
        """Testuje Planner Agent: Fallback na odrážkový seznam, pokud LLM nevrátí čistý JSON."""
        mock_api.return_value = "- Krok A: Opravit SQL\n- Krok B: Pridat testy"
        
        test_file = "test_dummy.py"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("def dummy(): pass\n")

        try:
            plan = generate_plan(test_file, "Refaktoruj dummy", "http://fake-url")
            self.assertEqual(len(plan), 2)
            self.assertEqual(plan[0], "Krok A: Opravit SQL")
            self.assertEqual(plan[1], "Krok B: Pridat testy")
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
