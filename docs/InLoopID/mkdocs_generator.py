#!/usr/bin/env python3

import csv
import os
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(ROOT, "chapters.csv")
MKDOCS_PATH = os.path.join(ROOT, "mkdocs.yml")

def load_structure():
    structure = defaultdict(list)

    with open(CSV_PATH, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            num, cat, title = row
            structure[cat].append((num, title))

    return structure

def generate_nav(structure):
    nav = []
    nav.append("nav:")
    nav.append("  - Home: docs/index.md")
    nav.append("  - Overview: docs/SUMMARY.md")

    for category in sorted(structure.keys()):
        nav.append(f"  - {category.capitalize()}:")
        for num, title in structure[category]:
            path = f"docs/{category}/{num}.md"
            nav.append(f"      - {num} {title}: {path}")

    return "\n".join(nav)

def generate_mkdocs_yaml(nav):
    config = f"""
site_name: InLoopID Enterprise Documentation

theme:
  name: material
  palette:
    - scheme: default
      toggle:
        icon: material/brightness-7
        name: Dark mode
    - scheme: slate
      toggle:
        icon: material/brightness-4
        name: Light mode

plugins:
  - search:
      lang: en
  - mermaid2

markdown_extensions:
  - admonition
  - tables
  - toc:
      permalink: true
  - pymdownx.superfences

extra:
  generator: false

{nav}
"""
    return config

def main():
    if not os.path.exists(CSV_PATH):
        print("CSV missing")
        return

    structure = load_structure()
    nav = generate_nav(structure)
    yaml = generate_mkdocs_yaml(nav)

    with open(MKDOCS_PATH, "w") as f:
        f.write(yaml)

    print("mkdocs.yml generated")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import csv
import os
from collections import defaultdict
from datetime import datetime
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_FILE = os.path.join(ROOT, "chapters.csv")
OUT_FILE = os.path.join(ROOT, "mkdocs.yml")


def load_chapters():
    data = defaultdict(list)

    with open(CSV_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            num, cat, title = row
            data[cat.strip()].append({
                "id": num.strip(),
                "title": title.strip()
            })

    return data


def build_nav(data):
    nav = [
        {"Home": "docs/index.md"},
        {"Summary": "docs/SUMMARY.md"}
    ]

    for cat in sorted(data.keys()):
        section = []
        for item in sorted(data[cat], key=lambda x: int(x["id"])):
            section.append({
                f'{item["id"]} {item["title"]}': f'docs/{cat}/{item["id"]}.md'
            })

        nav.append({cat.capitalize(): section})

    return nav


def build_config(nav):
    return {
        "site_name": "InLoopID Enterprise Documentation",
        "site_description": "Auto-generated enterprise documentation system",
        "site_author": "InLoopID Generator",
        "docs_dir": "docs",
        "site_dir": "site",

        "theme": {
            "name": "material",
            "features": [
                "navigation.tabs",
                "navigation.sections",
                "navigation.top",
                "search.highlight",
                "content.code.copy"
            ],
            "palette": [
                {
                    "scheme": "default",
                    "toggle": {
                        "icon": "material/brightness-7",
                        "name": "Dark mode"
                    }
                },
                {
                    "scheme": "slate",
                    "toggle": {
                        "icon": "material/brightness-4",
                        "name": "Light mode"
                    }
                }
            ]
        },

        "plugins": [
            "search",
            {
                "mermaid2": {
                    "arguments": {
                        "theme": "dark"
                    }
                }
            }
        ],

        "markdown_extensions": [
            "admonition",
            "tables",
            "toc",
            "fenced_code",
            "pymdownx.superfences",
            "pymdownx.details"
        ],

        "extra": {
            "generator": False,
            "current_year": datetime.now().year
        },

        "nav": nav
    }


def main():
    if not os.path.exists(CSV_FILE):
        raise SystemExit("chapters.csv not found")

    data = load_chapters()
    nav = build_nav(data)
    config = build_config(nav)

    with open(OUT_FILE, "w") as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)

    print("[OK] mkdocs.yml generated")


if __name__ == "__main__":
    main()
