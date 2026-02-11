#!/bin/bash
# Script de pré-déploiement - Vérifications de sécurité
# À exécuter AVANT de déployer en production

echo "=================================="
echo "🔍 VÉRIFICATIONS PRÉ-DÉPLOIEMENT"
echo "=================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# 1. Vérifier que .env n'est pas commité
echo "1️⃣  Vérification des fichiers .env..."
if git ls-files | grep -q "\.env$\|\.env\.local$"; then
    echo -e "${RED}❌ ERREUR: Des fichiers .env sont trackés par git!${NC}"
    echo "   Fichiers trouvés:"
    git ls-files | grep "\.env"
    echo "   → Exécutez: git rm --cached .env .env.local"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ OK: Aucun fichier .env n'est tracké${NC}"
fi
echo ""

# 2. Vérifier .gitignore
echo "2️⃣  Vérification du .gitignore..."
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore; then
        echo -e "${GREEN}✅ OK: .env est dans .gitignore${NC}"
    else
        echo -e "${RED}❌ ERREUR: .env n'est pas dans .gitignore!${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}❌ ERREUR: .gitignore manquant!${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 3. Vérifier les print() dans server_supabase.py
echo "3️⃣  Vérification des print() dans le code..."
PRINT_COUNT=$(grep -n "print(" backend/server_supabase.py 2>/dev/null | wc -l)
if [ "$PRINT_COUNT" -gt 5 ]; then
    echo -e "${YELLOW}⚠️  WARNING: $PRINT_COUNT print() trouvés dans server_supabase.py${NC}"
    echo "   → Recommandation: Remplacer par logging.info() ou logging.error()"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ OK: Peu de print() trouvés${NC}"
fi
echo ""

# 4. Vérifier les secrets hardcodés
echo "4️⃣  Recherche de secrets potentiellement hardcodés..."
SECRETS=$(grep -rn "sk-[a-zA-Z0-9]\{20,\}" backend/*.py 2>/dev/null | wc -l)
if [ "$SECRETS" -gt 0 ]; then
    echo -e "${RED}❌ ERREUR: Clés API potentiellement hardcodées trouvées!${NC}"
    grep -rn "sk-[a-zA-Z0-9]\{20,\}" backend/*.py
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ OK: Aucune clé API hardcodée détectée${NC}"
fi
echo ""

# 5. Vérifier render.yaml
echo "5️⃣  Vérification du render.yaml..."
if [ -f "render.yaml" ]; then
    if grep -q "ALLOWED_ORIGINS" render.yaml; then
        if grep -q 'value: "\*"' render.yaml; then
            echo -e "${YELLOW}⚠️  WARNING: ALLOWED_ORIGINS=* dans render.yaml${NC}"
            echo "   → Remplacer par vos domaines exacts en production"
            WARNINGS=$((WARNINGS + 1))
        else
            echo -e "${GREEN}✅ OK: ALLOWED_ORIGINS configuré${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  WARNING: ALLOWED_ORIGINS non trouvé dans render.yaml${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  WARNING: render.yaml non trouvé${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 6. Vérifier que les tests passent
echo "6️⃣  Exécution des tests..."
if [ -d "backend/tests" ]; then
    cd backend
    if command -v pytest &> /dev/null; then
        echo "   Lancement de pytest..."
        if pytest -q --maxfail=1 --disable-warnings 2>&1 | tee /tmp/pytest_output.txt; then
            echo -e "${GREEN}✅ OK: Tests passés${NC}"
        else
            echo -e "${RED}❌ ERREUR: Tests en échec!${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "${YELLOW}⚠️  WARNING: pytest non installé, tests ignorés${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    cd ..
else
    echo -e "${YELLOW}⚠️  WARNING: Dossier backend/tests non trouvé${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 7. Vérifier le frontend build
echo "7️⃣  Vérification du build frontend..."
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        echo "   Test du build production..."
        if npm run build > /tmp/frontend_build.log 2>&1; then
            echo -e "${GREEN}✅ OK: Build frontend réussi${NC}"
        else
            echo -e "${RED}❌ ERREUR: Build frontend échoué!${NC}"
            echo "   Voir /tmp/frontend_build.log pour les détails"
            ERRORS=$((ERRORS + 1))
        fi
    fi
    cd ..
fi
echo ""

# 8. Vérifier les migrations SQL
echo "8️⃣  Vérification des migrations SQL..."
if [ -d "migrations" ]; then
    SQL_COUNT=$(ls migrations/*.sql 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ $SQL_COUNT fichiers de migration trouvés${NC}"
    echo "   → N'oubliez pas de les appliquer sur la base de production!"
else
    echo -e "${YELLOW}⚠️  WARNING: Dossier migrations non trouvé${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Résumé
echo "=================================="
echo "📊 RÉSUMÉ DES VÉRIFICATIONS"
echo "=================================="
echo -e "Erreurs: ${RED}$ERRORS${NC}"
echo -e "Avertissements: ${YELLOW}$WARNINGS${NC}"
echo ""

if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}❌ DÉPLOIEMENT NON RECOMMANDÉ${NC}"
    echo "   → Corrigez les erreurs avant de déployer"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  DÉPLOIEMENT POSSIBLE AVEC PRÉCAUTIONS${NC}"
    echo "   → Vérifiez les avertissements"
    exit 0
else
    echo -e "${GREEN}✅ PRÊT POUR LE DÉPLOIEMENT${NC}"
    exit 0
fi
