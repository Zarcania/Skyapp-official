#!/usr/bin/env python3
"""
Script de vérification complète du backend SkyApp
Teste tous les endpoints critiques et fonctionnalités
"""

import requests
import json
import time
import os
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

class BackendVerifier:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.technicien_token = None
        self.company_id = None
        self.test_user_id = None
        self.test_search_id = None
        
    def print_status(self, message, status="INFO"):
        """Affiche un message avec un statut"""
        colors = {
            "INFO": "\033[94m",     # Bleu
            "SUCCESS": "\033[92m",  # Vert
            "WARNING": "\033[93m",  # Jaune
            "ERROR": "\033[91m",    # Rouge
            "ENDC": "\033[0m"       # Reset
        }
        print(f"{colors.get(status, '')}{status}: {message}{colors['ENDC']}")

    def check_server_health(self):
        """Vérification de base du serveur"""
        self.print_status("Vérification de la santé du serveur...")
        
        try:
            # Test du endpoint de base
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                self.print_status("✓ Serveur backend accessible", "SUCCESS")
            else:
                self.print_status(f"✗ Erreur serveur: {response.status_code}", "ERROR")
                return False
                
            # Test du endpoint health
            response = self.session.get(f"{API_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.print_status(f"✓ Health check: {data.get('status', 'OK')}", "SUCCESS")
            else:
                self.print_status("✗ Health check échoué", "WARNING")
                
            return True
            
        except requests.exceptions.ConnectionError:
            self.print_status("✗ Impossible de se connecter au serveur", "ERROR")
            self.print_status("Assurez-vous que le serveur backend est démarré", "INFO")
            return False
        except Exception as e:
            self.print_status(f"✗ Erreur lors de la vérification: {str(e)}", "ERROR")
            return False

    def test_authentication(self):
        """Test du système d'authentification"""
        self.print_status("Test du système d'authentification...")
        
        try:
            # Test de création de compte admin
            admin_data = {
                "email": "admin@test.com",
                "password": "admin123",
                "nom": "Admin",
                "prenom": "Test",
                "role": "ADMIN",
                "company_name": "Test Company"
            }
            
            response = self.session.post(f"{API_URL}/auth/register", json=admin_data)
            if response.status_code in [200, 201]:
                self.print_status("✓ Création de compte admin réussie", "SUCCESS")
                data = response.json()
                self.company_id = data.get('user', {}).get('company_id')
            else:
                # Peut-être que l'admin existe déjà
                self.print_status("ℹ Admin pourrait déjà exister", "INFO")
                
            # Test de connexion admin
            login_data = {
                "email": "admin@test.com",
                "password": "admin123"
            }
            
            response = self.session.post(f"{API_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                if not self.company_id:
                    self.company_id = data.get('user', {}).get('company_id')
                self.print_status("✓ Connexion admin réussie", "SUCCESS")
            else:
                self.print_status(f"✗ Échec connexion admin: {response.status_code}", "ERROR")
                return False
                
            # Configuration des headers d'authentification
            self.session.headers.update({
                'Authorization': f'Bearer {self.admin_token}'
            })
            
            return True
            
        except Exception as e:
            self.print_status(f"✗ Erreur authentification: {str(e)}", "ERROR")
            return False

    def test_user_management(self):
        """Test de la gestion des utilisateurs"""
        self.print_status("Test de la gestion des utilisateurs...")
        
        try:
            # Création d'un technicien
            technicien_data = {
                "email": "technicien@test.com",
                "password": "tech123",
                "nom": "Technicien",
                "prenom": "Test",
                "role": "TECHNICIEN"
            }
            
            response = self.session.post(f"{API_URL}/users", json=technicien_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_user_id = data.get('id')
                self.print_status("✓ Création de technicien réussie", "SUCCESS")
            else:
                self.print_status(f"✗ Échec création technicien: {response.status_code}", "WARNING")
                
            # Liste des utilisateurs
            response = self.session.get(f"{API_URL}/users")
            if response.status_code == 200:
                data = response.json()
                users_count = len(data)
                self.print_status(f"✓ Liste des utilisateurs récupérée ({users_count} utilisateurs)", "SUCCESS")
            else:
                self.print_status(f"✗ Échec récupération utilisateurs: {response.status_code}", "ERROR")
                
            return True
            
        except Exception as e:
            self.print_status(f"✗ Erreur gestion utilisateurs: {str(e)}", "ERROR")
            return False

    def test_search_management(self):
        """Test de la gestion des recherches terrain"""
        self.print_status("Test de la gestion des recherches terrain...")
        
        try:
            # Création d'une recherche
            search_data = {
                "location": "Paris, France",
                "description": "Test de recherche terrain",
                "observations": "Observations de test",
                "latitude": 48.8566,
                "longitude": 2.3522
            }
            
            response = self.session.post(f"{API_URL}/searches", json=search_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_search_id = data.get('id')
                self.print_status("✓ Création de recherche réussie", "SUCCESS")
            else:
                self.print_status(f"✗ Échec création recherche: {response.status_code}", "ERROR")
                return False
                
            # Récupération des recherches
            response = self.session.get(f"{API_URL}/searches")
            if response.status_code == 200:
                data = response.json()
                searches_count = len(data)
                self.print_status(f"✓ Liste des recherches récupérée ({searches_count} recherches)", "SUCCESS")
            else:
                self.print_status(f"✗ Échec récupération recherches: {response.status_code}", "ERROR")
                
            # Modification du statut
            if self.test_search_id:
                status_data = {"status": "SHARED"}
                response = self.session.put(f"{API_URL}/searches/{self.test_search_id}/status", json=status_data)
                if response.status_code == 200:
                    self.print_status("✓ Modification du statut réussie", "SUCCESS")
                else:
                    self.print_status(f"✗ Échec modification statut: {response.status_code}", "WARNING")
                    
            return True
            
        except Exception as e:
            self.print_status(f"✗ Erreur gestion recherches: {str(e)}", "ERROR")
            return False

    def test_file_upload(self):
        """Test de l'upload de fichiers"""
        self.print_status("Test de l'upload de fichiers...")
        
        try:
            if not self.test_search_id:
                self.print_status("✗ Pas de recherche disponible pour test upload", "WARNING")
                return False
                
            # Création d'un fichier test
            test_content = b"Test image content"
            files = {
                'files': ('test_image.jpg', test_content, 'image/jpeg')
            }
            
            response = self.session.post(
                f"{API_URL}/searches/{self.test_search_id}/photos",
                files=files
            )
            
            if response.status_code in [200, 201]:
                self.print_status("✓ Upload de photo réussi", "SUCCESS")
            else:
                self.print_status(f"✗ Échec upload photo: {response.status_code}", "WARNING")
                
            return True
            
        except Exception as e:
            self.print_status(f"✗ Erreur upload fichiers: {str(e)}", "ERROR")
            return False

    def test_reports_and_pdf(self):
        """Test de la génération de rapports et PDF"""
        self.print_status("Test de la génération de rapports et PDF...")
        
        try:
            if not self.test_search_id:
                self.print_status("✗ Pas de recherche disponible pour test rapport", "WARNING")
                return False
                
            # Génération d'un rapport PDF
            response = self.session.get(f"{API_URL}/searches/{self.test_search_id}/pdf")
            
            if response.status_code == 200:
                if 'application/pdf' in response.headers.get('content-type', ''):
                    self.print_status("✓ Génération PDF réussie", "SUCCESS")
                else:
                    self.print_status("✓ Réponse reçue mais type de contenu inattendu", "WARNING")
            else:
                self.print_status(f"✗ Échec génération PDF: {response.status_code}", "WARNING")
                
            return True
            
        except Exception as e:
            self.print_status(f"✗ Erreur génération rapports: {str(e)}", "ERROR")
            return False

    def test_database_collections(self):
        """Test des collections de base de données"""
        self.print_status("Test des collections de base de données...")
        
        collections_to_test = [
            ("companies", "/companies"),
            ("users", "/users"), 
            ("searches", "/searches"),
            ("clients", "/clients"),
            ("quotes", "/quotes"),
            ("worksites", "/worksites")
        ]
        
        success_count = 0
        for collection_name, endpoint in collections_to_test:
            try:
                response = self.session.get(f"{API_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "N/A"
                    self.print_status(f"✓ Collection {collection_name}: {count} éléments", "SUCCESS")
                    success_count += 1
                else:
                    self.print_status(f"✗ Collection {collection_name}: erreur {response.status_code}", "WARNING")
                    
            except Exception as e:
                self.print_status(f"✗ Collection {collection_name}: {str(e)}", "ERROR")
                
        return success_count >= len(collections_to_test) // 2

    def run_verification(self):
        """Exécute toutes les vérifications"""
        self.print_status("=" * 60, "INFO")
        self.print_status("DÉMARRAGE DE LA VÉRIFICATION COMPLÈTE DU BACKEND", "INFO")
        self.print_status("=" * 60, "INFO")
        
        tests = [
            ("Santé du serveur", self.check_server_health),
            ("Authentification", self.test_authentication),
            ("Gestion des utilisateurs", self.test_user_management),
            ("Gestion des recherches", self.test_search_management),
            ("Upload de fichiers", self.test_file_upload),
            ("Rapports et PDF", self.test_reports_and_pdf),
            ("Collections de données", self.test_database_collections)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_function in tests:
            self.print_status(f"\n--- Test: {test_name} ---", "INFO")
            try:
                if test_function():
                    passed_tests += 1
                time.sleep(1)  # Pause entre les tests
            except Exception as e:
                self.print_status(f"✗ Erreur inattendue dans {test_name}: {str(e)}", "ERROR")
                
        # Résumé final
        self.print_status("\n" + "=" * 60, "INFO")
        self.print_status("RÉSUMÉ DE LA VÉRIFICATION", "INFO")
        self.print_status("=" * 60, "INFO")
        
        success_rate = (passed_tests / total_tests) * 100
        self.print_status(f"Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)", "INFO")
        
        if passed_tests == total_tests:
            self.print_status("✓ TOUS LES TESTS SONT PASSÉS - BACKEND OPÉRATIONNEL", "SUCCESS")
        elif passed_tests >= total_tests * 0.8:
            self.print_status("⚠ MAJORITÉ DES TESTS PASSÉS - BACKEND FONCTIONNEL AVEC AVERTISSEMENTS", "WARNING")
        else:
            self.print_status("✗ PLUSIEURS TESTS ÉCHOUÉS - PROBLÈMES DÉTECTÉS", "ERROR")
            
        return success_rate >= 80

def main():
    """Fonction principale"""
    print("SkyApp Backend Verification Tool")
    print("-" * 40)
    
    # Vérification que le serveur est démarré
    verifier = BackendVerifier()
    
    try:
        success = verifier.run_verification()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nVérification interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\nErreur critique: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()