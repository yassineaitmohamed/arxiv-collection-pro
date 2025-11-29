#!/bin/bash
# Script d'automatisation complète: Collecte + Export + Déploiement
# Par Yassine Ait Mohamed

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║        🚀 arXiv Collection - Automatisation Complète         ║"
echo "║                                                               ║"
echo "║              Par Yassine Ait Mohamed                          ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Configuration
DB_FILE="arxiv_full_collection.db"
JSON_FILE="articles.json"
COLLECTOR_SCRIPT="arxiv_full_collector.py"

# Fonction: afficher menu
show_menu() {
    echo -e "${YELLOW}Que veux-tu faire?${NC}\n"
    echo "1. 🚀 Collection COMPLÈTE (1986-2025) + Export + Stats"
    echo "2. 📅 Collection d'une période spécifique"
    echo "3. 🔄 Mise à jour (collecter seulement 2025)"
    echo "4. 📤 Exporter DB existante vers JSON"
    echo "5. 📊 Voir les statistiques"
    echo "6. 🌐 Déployer sur GitHub Pages"
    echo "7. ⚡ TOUT FAIRE (Collect + Export + Deploy)"
    echo "8. 🧪 Test rapide (1 mois seulement)"
    echo "9. ❌ Quitter"
    echo ""
    read -p "Choix (1-9): " choice
}

# Fonction: collection complète
full_collection() {
    echo -e "\n${GREEN}🚀 Lancement de la collection complète (1986-2025)${NC}"
    echo -e "${YELLOW}⚠️  ATTENTION: Ceci peut prendre PLUSIEURS JOURS!${NC}"
    read -p "Continuer? (o/n): " confirm
    
    if [ "$confirm" != "o" ]; then
        echo "❌ Annulé"
        return
    fi
    
    echo -e "\n${CYAN}📚 Début de la collection...${NC}\n"
    python3 "$COLLECTOR_SCRIPT" full 1986 2025
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ Collection terminée avec succès!${NC}"
    else
        echo -e "\n${RED}❌ Erreur pendant la collection${NC}"
    fi
}

# Fonction: période spécifique
period_collection() {
    echo -e "\n${CYAN}📅 Collection pour une période spécifique${NC}\n"
    read -p "Année de début (ex: 2020): " start_year
    read -p "Année de fin (ex: 2025): " end_year
    
    echo -e "\n${CYAN}📚 Collection de $start_year à $end_year...${NC}\n"
    python3 "$COLLECTOR_SCRIPT" full "$start_year" "$end_year"
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ Collection terminée!${NC}"
    else
        echo -e "\n${RED}❌ Erreur pendant la collection${NC}"
    fi
}

# Fonction: mise à jour
update_collection() {
    echo -e "\n${CYAN}🔄 Mise à jour avec les articles de 2025${NC}\n"
    python3 "$COLLECTOR_SCRIPT" collect 2025 2025
    
    if [ $? -eq 0 ]; then
        echo -e "\n${CYAN}📤 Export vers JSON...${NC}"
        python3 "$COLLECTOR_SCRIPT" export "$JSON_FILE"
        echo -e "${GREEN}✅ Mise à jour terminée!${NC}"
    else
        echo -e "\n${RED}❌ Erreur pendant la mise à jour${NC}"
    fi
}

# Fonction: export
export_to_json() {
    if [ ! -f "$DB_FILE" ]; then
        echo -e "${RED}❌ Base de données non trouvée: $DB_FILE${NC}"
        return
    fi
    
    echo -e "\n${CYAN}📤 Export de la base de données vers JSON...${NC}\n"
    python3 "$COLLECTOR_SCRIPT" export "$JSON_FILE"
    
    if [ $? -eq 0 ]; then
        size=$(du -h "$JSON_FILE" | cut -f1)
        echo -e "\n${GREEN}✅ Export réussi!${NC}"
        echo -e "📦 Taille: $size"
    else
        echo -e "\n${RED}❌ Erreur pendant l'export${NC}"
    fi
}

# Fonction: statistiques
show_stats() {
    if [ ! -f "$DB_FILE" ]; then
        echo -e "${RED}❌ Base de données non trouvée: $DB_FILE${NC}"
        return
    fi
    
    echo -e "\n${CYAN}📊 Statistiques de la collection${NC}\n"
    python3 "$COLLECTOR_SCRIPT" stats
}

# Fonction: déploiement
deploy_to_github() {
    if [ ! -f "$JSON_FILE" ]; then
        echo -e "${RED}❌ Fichier JSON non trouvé: $JSON_FILE${NC}"
        echo -e "${YELLOW}💡 Lance d'abord l'export!${NC}"
        return
    fi
    
    echo -e "\n${CYAN}🌐 Déploiement sur GitHub Pages${NC}\n"
    
    # Copie le JSON dans le dossier du site (si différent)
    if [ -f "index.html" ]; then
        cp "$JSON_FILE" .
        echo -e "${GREEN}✅ JSON copié${NC}"
    fi
    
    # Lance le script de déploiement
    if [ -f "deploy.sh" ]; then
        ./deploy.sh
    else
        echo -e "${YELLOW}⚠️  deploy.sh non trouvé${NC}"
        echo -e "${YELLOW}Déploiement manuel:${NC}"
        echo "  git add ."
        echo "  git commit -m 'Update articles'"
        echo "  git push origin main"
    fi
}

# Fonction: tout faire
do_everything() {
    echo -e "\n${GREEN}⚡ AUTOMATISATION COMPLÈTE${NC}"
    echo -e "${YELLOW}⚠️  Ceci va:${NC}"
    echo "   1. Collecter tous les articles (plusieurs jours!)"
    echo "   2. Exporter vers JSON"
    echo "   3. Déployer sur GitHub"
    echo ""
    read -p "Continuer? (o/n): " confirm
    
    if [ "$confirm" != "o" ]; then
        echo "❌ Annulé"
        return
    fi
    
    # Collection
    echo -e "\n${CYAN}═══ ÉTAPE 1/3: Collection ═══${NC}"
    python3 "$COLLECTOR_SCRIPT" full 1986 2025
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erreur pendant la collection${NC}"
        return
    fi
    
    # Export
    echo -e "\n${CYAN}═══ ÉTAPE 2/3: Export ═══${NC}"
    python3 "$COLLECTOR_SCRIPT" export "$JSON_FILE"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erreur pendant l'export${NC}"
        return
    fi
    
    # Déploiement
    echo -e "\n${CYAN}═══ ÉTAPE 3/3: Déploiement ═══${NC}"
    deploy_to_github
    
    echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ TOUT EST TERMINÉ AVEC SUCCÈS! 🎉  ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
}

# Fonction: test rapide
quick_test() {
    echo -e "\n${CYAN}🧪 Test rapide (math.DG janvier 2024)${NC}\n"
    
    # Crée un script Python temporaire pour test
    cat > test_quick.py << 'EOF'
from arxiv_full_collector import ArxivFullCollector
import sys

collector = ArxivFullCollector("arxiv_test.db")
print("\n🧪 Test: Collection de math.DG pour janvier 2024\n")
articles = collector.collect_by_month('math.DG', 2024, 1)
saved = collector.save_articles(articles)
print(f"\n✅ Test terminé: {saved} articles collectés")
collector.export_to_json("articles_test.json")
EOF
    
    python3 test_quick.py
    rm test_quick.py
    
    echo -e "\n${GREEN}✅ Test terminé!${NC}"
    echo -e "Fichiers créés: arxiv_test.db, articles_test.json"
}

# Programme principal
while true; do
    show_menu
    
    case $choice in
        1)
            full_collection
            ;;
        2)
            period_collection
            ;;
        3)
            update_collection
            ;;
        4)
            export_to_json
            ;;
        5)
            show_stats
            ;;
        6)
            deploy_to_github
            ;;
        7)
            do_everything
            ;;
        8)
            quick_test
            ;;
        9)
            echo -e "\n${CYAN}👋 À bientôt!${NC}\n"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Choix invalide${NC}"
            ;;
    esac
    
    echo -e "\n${YELLOW}────────────────────────────────────────${NC}\n"
    read -p "Appuie sur Enter pour continuer..."
done
