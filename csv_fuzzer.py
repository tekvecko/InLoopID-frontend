import os
import random
import string
from pathlib import Path

OUT_DIR = "csv_fuzz_tests"
os.makedirs(OUT_DIR, exist_ok=True)

FIRST_NAMES = ["Jan", "Petra", "Petr", "Lucie", "Martin", "Anna", "Tomáš", "Eva", "Karel", "Jana"]
LAST_NAMES = ["Novák", "Malá", "Král", "Bílá", "Svoboda", "Procházka", "Dvořák", "Němcová"]

DOMAINS = [
    "firma.cz",
    "company.com",
    "vendor.io",
    "gmail.com",
    "seznam.cz",
    "external.net"
]

EXTRA_HEADERS = [
    ["EmployeeID", "FirstName", "LastName", "Email", "Role"],
    ["ID", "Name", "Surname", "Mail", "Position"],
    ["emp_id", "fname", "lname", "email_address", "dept"],
    ["A", "B", "C", "D"],
]

SEPARATORS = [",", ";", "\t", "|"]

def rand_email(valid=True):
    if valid:
        return f"{random.choice(FIRST_NAMES).lower()}.{random.choice(LAST_NAMES).lower()}@{random.choice(DOMAINS)}"
    else:
        variants = [
            "invalid-email",
            "missing-at.com",
            "no.domain@",
            "broken@domain",
            "user@firma",
            "@missinguser.cz"
        ]
        return random.choice(variants)

def rand_row():
    return [
        str(random.randint(1000, 9999)),
        random.choice(FIRST_NAMES),
        random.choice(LAST_NAMES),
        rand_email(valid=random.random() > 0.2),
        random.choice(["Engineer", "HR", "Manager", "Vendor", "Intern"])
    ]

def corrupt_row(row):
    chaos = random.random()

    if chaos < 0.2:
        row.append("EXTRA_COLUMN_" + ''.join(random.choices(string.ascii_letters, k=5)))
    if chaos < 0.1:
        row[random.randint(0, len(row)-1)] = ""
    if chaos < 0.05:
        row = row[:2]  # truncated row
    return row

def generate_csv(i):
    sep = random.choice(SEPARATORS)
    headers = random.choice(EXTRA_HEADERS)

    lines = [sep.join(headers)]

    row_count = random.randint(3, 25)

    for _ in range(row_count):
        row = rand_row()
        row = corrupt_row(row)

        # occasional duplicate row injection
        if random.random() < 0.1:
            lines.append(sep.join(row))

        lines.append(sep.join(row))

    # shuffle corruption: mixed separators
    if random.random() < 0.1:
        lines = [line.replace(sep, random.choice(SEPARATORS)) for line in lines]

    filename = f"{OUT_DIR}/fuzz_{i:03d}.csv"
    Path(filename).write_text("\n".join(lines), encoding="utf-8")

def main():
    total = 120  # >100 variantů
    for i in range(total):
        generate_csv(i)

    print(f"Generated {total} fuzz CSV files in {OUT_DIR}/")

if __name__ == "__main__":
    main()
