import sys
from pdf_engine import generate_contract_pdf

def test_generation():
    # Model dat simulující výstup z vašeho Fáze 01 - HR Terminálu
    test_data = {
        "employer_name": "InLoop Corp, a.s.",
        "employer_address": "Technologický park 1, 602 00 Brno",
        "employer_ico": "25874136",
        "employee_email": "karel.novotny@enterprise.cz",
        "position": "Senior Cloud Architekt",
        "workplace": "Brno (HQ) / Hybrid",
        "duration": "neurčitou",
        "probation_months": 6,
        "weekly_hours": 40,
        "salary": "120 000"
    }
    
    try:
        pdf_bytes = generate_contract_pdf(test_data)
        test_output_path = "InLoopID_Smlouva_Náhled.pdf"
        
        with open(test_output_path, "wb") as f:
            f.write(pdf_bytes)
            
        print(f"[OK] Finální PDF smlouva vygenerována: {test_output_path}")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Selhání generátoru: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_generation()
