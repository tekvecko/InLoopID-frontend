#!/usr/bin/env python3
import os
from mnemonic import Mnemonic

# ANSI formátování
C_TITLE = '\033[1;38;2;37;99;235m'
C_SHARD = '\033[1;38;2;16;185;129m'
C_WORD = '\033[0;38;2;100;116;139m'
C_END = '\033[0m'

def generate_ceremony():
    os.system('clear')
    print(f"{C_TITLE}===================================================={C_END}")
    print(f"{C_TITLE}   InLoopID: Enterprise Key Generation Ceremony     {C_END}")
    print(f"{C_TITLE}===================================================={C_END}\n")
    
    print("Iniciuji Shamir's Secret Sharing (2-ze-3)...")
    print("Generuji entropii (256-bit) pro master klíč...\n")
    
    mnemo = Mnemonic("english")
    
    roles = ["CEO (Trezor A)", "HR Ředitel (Trezor B)", "Právní oddělení (Trezor C)"]
    
    for i, role in enumerate(roles, 1):
        # Generování 256bitové entropie (24 slov) pro každou část klíče
        words = mnemo.generate(strength=256)
        words_list = words.split()
        
        print(f"{C_SHARD}Klíč {i}/3: {role}{C_END}")
        print("-" * 50)
        
        # Formátovaný výpis 24 slov do dvou sloupců pro snadné opsání
        for j in range(0, 24, 2):
            left_word = f"{j+1:02d}. {words_list[j]}"
            right_word = f"{j+2:02d}. {words_list[j+1]}"
            print(f"{C_WORD}{left_word:<20} {right_word}{C_END}")
        print("\n")

    print(f"{C_TITLE}UPOZORNĚNÍ:{C_END} Pro obnovu firemní databáze musí být v budoucnu")
    print("zadány minimálně DVĚ z těchto tří 24slovných sekvencí.")
    print("Nyní uložte fyzické kopie do oddělených bezpečnostních schránek.\n")

if __name__ == "__main__":
    generate_ceremony()
