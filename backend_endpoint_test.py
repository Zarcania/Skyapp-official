#!/usr/bin/env python3
"""
Test complet des endpoints du backend SkyApp
"""

import sys
import os
import requests
import time
import subprocess
import threading
import signal
from contextlib import contextmanager

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

class BackendTester:
    def __init__(self):
        self.server_process = None
        self.session = requests.Session()
        
    def start_server(self):
        """Démarre le serveur backend"""
        print("Démarrage du serveur backend...")
        
        backend_dir = os.path.join(os.getcwd(), "backend")
        server_cmd = [
            sys.executable, "-c",
            "import sys; sys.path.insert(0, '.'); import uvicorn; uvicorn.run('server:app', host='127.0.0.1', port=8000)"
        ]
        
        try:
            self.server_process = subprocess.Popen(
                server_cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre que le serveur soit prêt
            max_wait = 30
            wait_time = 0
            while wait_time < max_wait:
                try:
                    response = requests.get(f"{BASE_URL}/", timeout=2)
                    if response.status_code == 200:
                        print("✓ Serveur backend démarré avec succès")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
                wait_time += 1
                
            print("✗ Timeout: le serveur n'a pas pu démarrer")
            return False
            
        except Exception as e:
            print(f"✗ Erreur lors du démarrage du serveur: {str(e)}")
            return False
    
    def stop_server(self):
        """Arrête le serveur backend"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("✓ Serveur arrêté proprement")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("⚠ Serveur arrêté de force")
            except Exception as e:
                print(f"✗ Erreur lors de l'arrêt: {str(e)}")
    
    def test_health_endpoints(self):
        """Test des endpoints de santé"""
        print("\n=== Test des endpoints de santé ===")
        
        tests = [
            ("GET /", "Page d'accueil"),
            ("GET /api/health", "Health check"),
        ]
        
        success_count = 0
        for method_path, description in tests:
            method, path = method_path.split(" ", 1)
            url = BASE_URL + path if path.startswith("/") else f"{API_URL}{path}"
            
            try:
                if method == "GET":
                    response = self.session.get(url, timeout=5)
                else:
                    continue
                    
                if response.status_code == 200:
                    print(f"✓ {description}: {response.status_code}")
                    success_count += 1
                else:
                    print(f"✗ {description}: {response.status_code}")
                    
            except Exception as e:
                print(f"✗ {description}: Erreur - {str(e)}")
                
        return success_count == len(tests)
    
    def test_auth_endpoints(self):
        """Test des endpoints d'authentification"""
        print("\n=== Test des endpoints d'authentification ===")
        
        try:
            # Test de création de compte (peut échouer si admin existe déjà)
            admin_data = {
                "email": "admin@test.com",
                "password": "admin123",
                "nom": "Admin",
                "prenom": "Test",
                "role": "ADMIN",
                "company_name": "Test Company"
            }
            
            response = self.session.post(f"{API_URL}/auth/register", json=admin_data, timeout=10)
            if response.status_code in [200, 201]:
                print("✓ Création de compte admin: Succès")
            else:
                print(f"ℹ Création de compte admin: {response.status_code} (peut-être existant)")
            
            # Test de connexion
            login_data = {
                "email": "admin@test.com",
                "password": "admin123"
            }
            
            response = self.session.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                print("✓ Connexion admin: Succès")
                data = response.json()
                token = data.get('access_token')
                if token:
                    print("✓ Token JWT reçu")
                    # Configure les headers pour les prochaines requêtes
                    self.session.headers.update({'Authorization': f'Bearer {token}'})
                    return True
                else:
                    print("✗ Token JWT manquant")
            else:
                print(f"✗ Connexion admin: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Erreur lors des tests d'auth: {str(e)}")
            
        return False
    
    def test_crud_endpoints(self):
        """Test des endpoints CRUD principaux"""
        print("\n=== Test des endpoints CRUD ===")
        
        endpoints_to_test = [
            ("GET", "/users", "Liste des utilisateurs"),
            ("GET", "/searches", "Liste des recherches"),
            ("GET", "/companies", "Liste des entreprises"),
            ("GET", "/clients", "Liste des clients"),
            ("GET", "/quotes", "Liste des devis"),
            ("GET", "/worksites", "Liste des chantiers"),
        ]
        
        success_count = 0
        for method, path, description in endpoints_to_test:
            try:
                url = f"{API_URL}{path}"
                
                if method == "GET":
                    response = self.session.get(url, timeout=10)
                else:
                    continue
                    
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "N/A"
                    print(f"✓ {description}: {response.status_code} ({count} éléments)")
                    success_count += 1
                else:
                    print(f"✗ {description}: {response.status_code}")
                    
            except Exception as e:
                print(f"✗ {description}: Erreur - {str(e)}")
        
        return success_count >= len(endpoints_to_test) // 2
    
    def test_search_creation(self):
        """Test de création d'une recherche"""
        print("\n=== Test de création d'une recherche ===")
        
        try:
            search_data = {
                "location": "Paris, France",
                "description": "Test de recherche terrain automatisé",
                "observations": "Test effectué par le script de vérification",
                "latitude": 48.8566,
                "longitude": 2.3522
            }
            
            response = self.session.post(f"{API_URL}/searches", json=search_data, timeout=10)
            
            if response.status_code in [200, 201]:
                print("✓ Création de recherche: Succès")
                data = response.json()
                search_id = data.get('id')
                if search_id:
                    print(f"✓ ID de recherche reçu: {search_id}")
                    return search_id
                else:
                    print("✗ ID de recherche manquant")
            else:
                print(f"✗ Création de recherche: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Détail: {error_data.get('detail', 'Erreur inconnue')}")
                except:
                    pass
                    
        except Exception as e:
            print(f"✗ Erreur lors de la création de recherche: {str(e)}")
            
        return None
    
    def run_full_test(self):
        """Exécute tous les tests"""
        print("SkyApp Backend - Vérification complète des endpoints")
        print("=" * 60)
        
        # Démarrage du serveur
        if not self.start_server():
            print("✗ Impossible de démarrer le serveur")
            return False
        
        try:
            tests = [
                ("Endpoints de santé", self.test_health_endpoints),
                ("Authentification", self.test_auth_endpoints), 
                ("Endpoints CRUD", self.test_crud_endpoints),
                ("Création de recherche", lambda: self.test_search_creation() is not None)
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                print(f"\n--- {test_name} ---")
                try:
                    if test_func():
                        passed_tests += 1
                    time.sleep(1)  # Petite pause entre les tests
                except Exception as e:
                    print(f"✗ Erreur inattendue dans {test_name}: {str(e)}")
            
            # Résumé final
            print(f"\n{'='*60}")
            print("RÉSUMÉ DE LA VÉRIFICATION COMPLÈTE")
            print("=" * 60)
            
            success_rate = (passed_tests / total_tests) * 100
            print(f"Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
            
            if passed_tests == total_tests:
                print("✓ TOUS LES TESTS SONT PASSÉS - BACKEND COMPLÈTEMENT OPÉRATIONNEL")
                status = "SUCCÈS"
            elif passed_tests >= total_tests * 0.75:
                print("⚠ MAJORITÉ DES TESTS PASSÉS - BACKEND FONCTIONNEL AVEC AVERTISSEMENTS")
                status = "PARTIEL"
            else:
                print("✗ PLUSIEURS TESTS ÉCHOUÉS - PROBLÈMES DÉTECTÉS")
                status = "ÉCHEC"
            
            print(f"\nStatut final: {status}")
            return success_rate >= 75
            
        finally:
            self.stop_server()

def main():
    """Fonction principale"""
    tester = BackendTester()
    
    try:
        success = tester.run_full_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrompu par l'utilisateur")
        tester.stop_server()
        sys.exit(1)
    except Exception as e:
        print(f"\nErreur critique: {str(e)}")
        tester.stop_server()
        sys.exit(1)

if __name__ == "__main__":
    main()