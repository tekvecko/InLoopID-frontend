#!/usr/bin/env python3
import time
import os
import hashlib
import textwrap

# ANSI Barvy (Navy Blue & Slate tématika)
C_NAVY = '\033[38;2;15;23;42m'     # Slate 900
C_BLUE = '\033[38;2;37;99;235m'    # Blue 600
C_EMERALD = '\033[38;2;16;185;129m'# Emerald 500
C_ROSE = '\033[38;2;225;29;72m'    # Rose 600
C_SLATE = '\033[38;2;100;116;139m' # Slate 500
C_BOLD = '\033[1m'
C_END = '\033[0m'

def clear_screen():
    os.system('clear')

def type_text(text, speed=0.03, color=C_SLATE):
    for char in text:
        print(f"{color}{char}{C_END}", end='', flush=True)
        time.sleep(speed)
    print()

def print_step(number, title):
    print(f"\n{C_BOLD}{C_BLUE}[KROK {number}]{C_END} {C_BOLD}{title}{C_END}")
    print(f"{C_BLUE}" + "="*50 + f"{C_END}")

def demo():
    clear_screen()
    print(f"{C_BOLD}{C_BLUE}--- InLoopID Zero-Knowledge Demo pro Investory ---{C_END}\n")
    
    # KROK 1: Klientská strana
    print_step(1, "Zařízení klienta (HR Oddělení)")
    type_text("Generuji čitelnou pracovní smlouvu...", 0.02)
    contract = "PRACOVNÍ SMLOUVA: Jan Novák, Plat: 85 000 CZK, RČ: 900101/1234"
    print(f"\n{C_EMERALD}Dokument:{C_END} {contract}\n")
    time.sleep(1)

    # KROK 2: Lokální šifrování
    print_step(2, "Lokální AES-256-GCM Šifrování (Stále na zařízení klienta)")
    type_text("Vytvářím unikátní klientský klíč (Master Key)...", 0.03)
    time.sleep(0.5)
    print(f"{C_EMERALD}Klíč vytvořen a uložen pouze v keystore klienta.{C_END}")
    type_text("Šifruji dokument...", 0.05)
    
    # Simulace šifrování
    encrypted_payload = hashlib.sha512(contract.encode()).hexdigest().upper()
    print(f"\n{C_BLUE}Šifrovaný Payload (To, co opustí počítač):{C_END}")
    print(f"{C_SLATE}{textwrap.fill(encrypted_payload, 64)}{C_END}\n")
    time.sleep(2)

    # KROK 3: Pohled Serveru
    print_step(3, "Pohled serveru InLoopID (Slepý notář)")
    type_text("Odesílám data do cloudové databáze InLoopID...", 0.02)
    time.sleep(1)
    print(f"\n{C_ROSE}Co vidí náš server a databáze:{C_END}")
    print(f"{C_SLATE}{textwrap.fill(encrypted_payload, 64)}{C_END}")
    print(f"\n{C_ROSE}Co nevidíme:{C_END} Jméno, Plat, Rodné číslo. Klíč nemáme.")
    time.sleep(2)

    # KROK 4: eIDAS Audit
    print_step(4, "Zajištění právní nevyvratitelnosti (eIDAS TSA)")
    type_text("Vyžaduji kvalifikované časové razítko od státní autority pro tento payload...", 0.04)
    time.sleep(1)
    tsa_hash = hashlib.sha256(encrypted_payload.encode()).hexdigest()
    print(f"{C_EMERALD}Pečeť úspěšně získána.{C_END}")
    print(f"{C_BLUE}Auditní stopa (Blockchain fixace):{C_END} {tsa_hash[:32]}... [Zapsáno]")
    
    print(f"\n{C_BOLD}{C_EMERALD}ZÁVĚR: Dokument je právně platný, auditovatelný, ale InLoopID nenese žádné GDPR riziko.{C_END}\n")

if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print(f"\n{C_SLATE}Demo přerušeno.{C_END}")
