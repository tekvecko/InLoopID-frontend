#!/usr/bin/env python3
import os
import secrets
import time

# ANSI barvy pro profesionální výstup
C_NAVY = '\033[38;2;15;23;42m'
C_BLUE = '\033[38;2;37;99;235m'
C_GREEN = '\033[38;2;16;185;129m'
C_RED = '\033[38;2;225;29;72m'
C_SLATE = '\033[38;2;100;116;139m'
C_BOLD = '\033[1m'
C_END = '\033[0m'

# 256-bitové prvočíslo pro kryptografické operace (Secp256k1 prime)
PRIME = 2**256 - 2**32 - 977

def make_random_shares(secret, minimum, shares):
    # Generování náhodného polynomu stupně (minimum - 1)
    poly = [secret] + [secrets.randbelow(PRIME) for _ in range(minimum - 1)]
    
    def evaluate_polynomial(x):
        result = 0
        for i, coeff in enumerate(poly):
            result = (result + coeff * pow(x, i, PRIME)) % PRIME
        return result

    # Vygenerování bodů (podílů) na křivce
    points = []
    for i in range(1, shares + 1):
        points.append((i, evaluate_polynomial(i)))
    return points

def recover_secret(shares):
    # Lagrangeova interpolace pro nalezení průsečíku s osou Y (kde x = 0)
    secret = 0
    for i in range(len(shares)):
        x_i, y_i = shares[i]
        numerator = 1
        denominator = 1
        for j in range(len(shares)):
            if i == j: continue
            x_j, _ = shares[j]
            numerator = (numerator * (-x_j)) % PRIME
            denominator = (denominator * (x_i - x_j)) % PRIME
        
        lagrange_val = (y_i * numerator * pow(denominator, PRIME - 2, PRIME)) % PRIME
        secret = (secret + lagrange_val) % PRIME
    return secret

def demo():
    os.system('clear')
    print(f"{C_BOLD}{C_BLUE}--- InLoopID: Shamir's Secret Sharing (2 ze 3) ---{C_END}\n")
    
    # 1. Generování Master klíče
    original_secret = secrets.randbits(256)
    secret_hex = hex(original_secret)[2:].zfill(64)
    print(f"{C_BOLD}Vytvářím 256-bitový Master Klíč pro AES-GCM šifrování databáze:{C_END}")
    print(f"{C_GREEN}{secret_hex}{C_END}\n")
    time.sleep(1.5)
    
    # 2. Rozdělení na 3 střípky
    shares = make_random_shares(original_secret, minimum=2, shares=3)
    owners = ["CEO", "HR Ředitel", "Právní oddělení"]
    
    print(f"{C_BOLD}Rozděluji Master Klíč na 3 samostatné střípky:{C_END}")
    for i, share in enumerate(shares):
        share_hex = hex(share[1])[2:].zfill(64)
        print(f"{C_BLUE}[Klíč {i+1} - {owners[i]}]{C_END} {C_SLATE}{share_hex[:32]}...{C_END}")
        time.sleep(0.5)
    
    print(f"\n{C_RED}Poznámka: Původní Master Klíč je nyní ze serveru nenávratně smazán.{C_END}\n")
    time.sleep(2)
    
    # 3. Pokus o obnovu s 1 klíčem
    print(f"{C_BOLD}Krizový scénář A: Nespokojený HR Ředitel se snaží sám dešifrovat data.{C_END}")
    fake_recovery = recover_secret([shares[1]]) # Pouze 1 klíč
    print(f"Výsledek: {C_RED}SELVHÁNÍ - Nedostatek entropie. Klíč nelze zrekonstruovat.{C_END}\n")
    time.sleep(2)
    
    # 4. Úspěšná obnova se 2 klíči
    print(f"{C_BOLD}Krizový scénář B: HR Ředitel ztratil přístup. CEO a Právník obnovují systém.{C_END}")
    recovered_secret = recover_secret([shares[0], shares[2]]) # CEO (0) + Právník (2)
    recovered_hex = hex(recovered_secret)[2:].zfill(64)
    
    print(f"Skládám Klíč 1 (CEO) + Klíč 3 (Právník)...")
    time.sleep(1)
    
    if recovered_secret == original_secret:
        print(f"Obnovený Master Klíč: {C_GREEN}{recovered_hex}{C_END}")
        print(f"\n{C_BOLD}{C_GREEN}[ÚSPĚCH] Databáze odemčena dvěma oprávněnými osobami.{C_END}")
    else:
        print(f"{C_RED}[CHYBA] Matematická obnova selhala.{C_END}")

if __name__ == "__main__":
    demo()
