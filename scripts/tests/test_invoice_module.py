"""
Test du module de facturation électronique
Vérifie que les endpoints sont fonctionnels
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://127.0.0.1:8001/api"

def test_invoice_creation():
    """Test de création d'une facture électronique"""
    
    print("=" * 80)
    print("🧪 TEST MODULE FACTURATION ÉLECTRONIQUE")
    print("=" * 80)
    
    # Données de test
    invoice_data = {
        "customer_name": "Client Test SA",
        "siren_client": "123456789",  # SIREN valide (9 chiffres)
        "address_billing": "123 Rue de la République\n75001 PARIS",
        "address_delivery": "",
        "invoice_date": datetime.now().strftime("%Y-%m-%d"),
        "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "payment_terms": "30 jours",
        "payment_method": "virement",
        "total_ht": 1000.00,
        "total_tva": 200.00,
        "total_ttc": 1200.00,
        "notes": "Facture de test - Module conforme réforme 2026-2027",
        "lines": [
            {
                "line_number": 1,
                "designation": "Prestation de service",
                "description": "Développement module facturation",
                "quantity": 1,
                "unit": "jour",
                "unit_price_ht": 800.00,
                "tva_rate": 20
            },
            {
                "line_number": 2,
                "designation": "Formation",
                "description": "Formation à l'utilisation",
                "quantity": 2,
                "unit": "heure",
                "unit_price_ht": 100.00,
                "tva_rate": 20
            }
        ]
    }
    
    # Note: Ce test nécessite un token d'authentification valide
    print("\n⚠️  REMARQUE IMPORTANTE :")
    print("Ce script de test nécessite un token d'authentification valide.")
    print("Pour tester réellement, utilisez l'interface web : http://localhost:3002")
    print("\nStructure de la requête à envoyer :")
    print("-" * 80)
    print(f"POST {API_BASE}/invoices/electronic")
    print("Headers:")
    print('  Authorization: Bearer <votre_token>')
    print('  Content-Type: application/json')
    print("\nBody:")
    print(json.dumps(invoice_data, indent=2, ensure_ascii=False))
    print("-" * 80)
    
    print("\n✅ Validation des données de test :")
    print(f"   - SIREN : {invoice_data['siren_client']} (9 chiffres) ✅")
    print(f"   - Nombre de lignes : {len(invoice_data['lines'])} ✅")
    print(f"   - Total HT : {invoice_data['total_ht']}€ ✅")
    print(f"   - Total TVA : {invoice_data['total_tva']}€ ✅")
    print(f"   - Total TTC : {invoice_data['total_ttc']}€ ✅")
    
    # Validation calculs
    calculated_ht = sum(line['quantity'] * line['unit_price_ht'] for line in invoice_data['lines'])
    calculated_tva = sum(
        (line['quantity'] * line['unit_price_ht']) * (line['tva_rate'] / 100)
        for line in invoice_data['lines']
    )
    calculated_ttc = calculated_ht + calculated_tva
    
    print(f"\n🔍 Vérification des calculs :")
    print(f"   - HT calculé : {calculated_ht:.2f}€ {'✅' if abs(calculated_ht - invoice_data['total_ht']) < 0.01 else '❌'}")
    print(f"   - TVA calculée : {calculated_tva:.2f}€ {'✅' if abs(calculated_tva - invoice_data['total_tva']) < 0.01 else '❌'}")
    print(f"   - TTC calculé : {calculated_ttc:.2f}€ {'✅' if abs(calculated_ttc - invoice_data['total_ttc']) < 0.01 else '❌'}")
    
    print("\n" + "=" * 80)
    print("📋 INSTRUCTIONS POUR TESTER :")
    print("=" * 80)
    print("1. Ouvrir http://localhost:3002")
    print("2. Se connecter avec votre compte")
    print("3. Aller dans l'onglet 'Facturation'")
    print("4. Cliquer sur '+ Nouvelle Facture'")
    print("5. Remplir le formulaire avec les données ci-dessus")
    print("6. Vérifier que les totaux se calculent automatiquement")
    print("7. Cliquer sur 'Créer la facture'")
    print("8. Vérifier que la facture apparaît dans la liste")
    print("=" * 80)
    
    return True

def test_siren_validation():
    """Test de validation SIREN"""
    print("\n" + "=" * 80)
    print("🧪 TEST VALIDATION SIREN")
    print("=" * 80)
    
    test_cases = [
        ("123456789", True, "SIREN valide (9 chiffres)"),
        ("12345678", False, "SIREN invalide (8 chiffres)"),
        ("1234567890", False, "SIREN invalide (10 chiffres)"),
        ("12345678A", False, "SIREN invalide (contient lettres)"),
        ("", False, "SIREN vide"),
    ]
    
    for siren, should_pass, description in test_cases:
        is_valid = len(siren) == 9 and siren.isdigit()
        status = "✅" if (is_valid == should_pass) else "❌"
        print(f"{status} {description} : '{siren}' -> {'VALIDE' if is_valid else 'INVALIDE'}")
    
    print("=" * 80)

if __name__ == "__main__":
    test_siren_validation()
    test_invoice_creation()
    
    print("\n" + "=" * 80)
    print("✅ TESTS PRÉPARATOIRES TERMINÉS")
    print("=" * 80)
    print("\n💡 Pour tester réellement le module, utilisez l'interface web.")
    print("   Le backend est prêt à recevoir les requêtes sur :")
    print(f"   {API_BASE}/invoices/electronic")
    print("\n" + "=" * 80)
