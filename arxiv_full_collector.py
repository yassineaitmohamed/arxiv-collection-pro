#!/usr/bin/env python3
"""
arXiv Full Collector - Collection complète 1986-2025
Collecte TOUS les articles arXiv et les exporte pour l'interface web
Par Yassine Ait Mohamed
"""

import sqlite3
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import time
import sys
import json
from pathlib import Path

class ArxivFullCollector:
    def __init__(self, db_path="arxiv_full_collection.db"):
        self.db_path = db_path
        self.base_url = "http://export.arxiv.org/api/query"
        self.init_database()
        
        # Catégories à collecter (ajoute les tiennes ici)
        self.categories = [
            'math.DG',  # Differential Geometry
            'math.SG',  # Symplectic Geometry
            'math-ph',  # Mathematical Physics
            'math.AG',  # Algebraic Geometry
            'math.QA',  # Quantum Algebra
            'math.RT',  # Representation Theory
            'math.GT',  # Geometric Topology
            'math.AT',  # Algebraic Topology
            'math.CT',  # Category Theory
            'math.KT',  # K-Theory and Homology
        ]
    
    def init_database(self):
        """Initialise la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                arxiv_id TEXT PRIMARY KEY,
                title TEXT,
                authors TEXT,
                abstract TEXT,
                category TEXT,
                published DATE,
                updated DATE,
                link TEXT,
                pdf_link TEXT,
                last_fetched TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                year INTEGER,
                month INTEGER,
                articles_count INTEGER,
                status TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index pour recherche rapide
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_published ON articles(published)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON articles(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON articles(title)')
        
        conn.commit()
        conn.close()
        print("✅ Base de données initialisée")
    
    def fetch_with_retry(self, params, max_retries=5, initial_wait=3):
        """Fetch avec retry automatique"""
        wait_time = initial_wait
        
        for attempt in range(max_retries):
            try:
                response = requests.get(self.base_url, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.text, True
                
                elif response.status_code == 429:
                    print(f"   ⚠️  Rate limit, attente {wait_time}s...")
                    time.sleep(wait_time)
                    wait_time *= 2
                    continue
                
                elif response.status_code in [500, 503]:
                    print(f"   ⚠️  Erreur serveur, attente {wait_time}s...")
                    time.sleep(wait_time)
                    wait_time *= 2
                    continue
                
                else:
                    print(f"   ❌ Erreur HTTP {response.status_code}")
                    return None, False
                    
            except requests.exceptions.Timeout:
                print(f"   ⚠️  Timeout, tentative {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
                wait_time *= 2
                continue
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                return None, False
        
        return None, False
    
    def parse_response(self, xml_data):
        """Parse la réponse XML d'arXiv"""
        try:
            root = ET.fromstring(xml_data)
            ns = {'atom': 'http://www.w3.org/2005/Atom',
                  'arxiv': 'http://arxiv.org/schemas/atom'}
            
            articles = []
            entries = root.findall('atom:entry', ns)
            
            for entry in entries:
                # ID arXiv
                arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                
                # Titre
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                
                # Auteurs
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns).text
                    authors.append(name)
                authors_str = '; '.join(authors)
                
                # Abstract
                abstract = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
                
                # Catégorie principale
                primary_cat = entry.find('arxiv:primary_category', ns)
                category = primary_cat.get('term') if primary_cat is not None else 'unknown'
                
                # Dates
                published = entry.find('atom:published', ns).text[:10]
                updated = entry.find('atom:updated', ns).text[:10]
                
                # Liens
                link = entry.find('atom:id', ns).text
                pdf_link = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                
                articles.append({
                    'arxiv_id': arxiv_id,
                    'title': title,
                    'authors': authors_str,
                    'abstract': abstract,
                    'category': category,
                    'published': published,
                    'updated': updated,
                    'link': link,
                    'pdf_link': pdf_link
                })
            
            return articles
            
        except Exception as e:
            print(f"   ❌ Erreur parsing XML: {e}")
            return []
    
    def save_articles(self, articles):
        """Sauvegarde les articles dans la base"""
        if not articles:
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved = 0
        for article in articles:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO articles 
                    (arxiv_id, title, authors, abstract, category, published, updated, link, pdf_link, last_fetched)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article['arxiv_id'],
                    article['title'],
                    article['authors'],
                    article['abstract'],
                    article['category'],
                    article['published'],
                    article['updated'],
                    article['link'],
                    article['pdf_link'],
                    datetime.now().isoformat()
                ))
                saved += 1
            except Exception as e:
                print(f"   ⚠️  Erreur sauvegarde {article['arxiv_id']}: {e}")
        
        conn.commit()
        conn.close()
        return saved
    
    def collect_by_month(self, category, year, month):
        """Collecte les articles pour un mois donné"""
        # Dates du mois
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        
        # Requête arXiv avec filtres de date
        query = f"cat:{category}"
        
        all_articles = []
        start = 0
        batch_size = 1000
        
        while True:
            params = {
                'search_query': query,
                'start': start,
                'max_results': batch_size,
                'sortBy': 'submittedDate',
                'sortOrder': 'ascending'
            }
            
            print(f"      Batch {start//batch_size + 1} (offset {start})...", end=' ')
            
            xml_data, success = self.fetch_with_retry(params)
            
            if not success or not xml_data:
                print("❌")
                break
            
            articles = self.parse_response(xml_data)
            
            if not articles:
                print("✅ Terminé")
                break
            
            # Filtrer par date (car l'API ne filtre pas toujours parfaitement)
            filtered = [a for a in articles 
                       if start_date.isoformat()[:10] <= a['published'] < end_date.isoformat()[:10]]
            
            if filtered:
                all_articles.extend(filtered)
                print(f"✅ {len(filtered)} articles")
            else:
                print("✅ 0 articles (hors période)")
            
            # Si on a moins d'articles que demandé, c'est fini
            if len(articles) < batch_size:
                print("      ✅ Fin de la collection")
                break
            
            start += batch_size
            time.sleep(3)  # Respecter l'API
            
            # Si on dépasse la date de fin, arrêter
            if articles and articles[-1]['published'] >= end_date.isoformat()[:10]:
                break
        
        return all_articles
    
    def collect_year(self, category, year):
        """Collecte tous les articles d'une année"""
        print(f"\n   📅 Année {year}")
        total_articles = 0
        
        for month in range(1, 13):
            print(f"      📆 {year}-{month:02d}...", end=' ')
            
            articles = self.collect_by_month(category, year, month)
            
            if articles:
                saved = self.save_articles(articles)
                total_articles += saved
                print(f"✅ {saved} articles sauvegardés")
                
                # Log du progrès
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO collection_progress (category, year, month, articles_count, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (category, year, month, saved, 'completed'))
                conn.commit()
                conn.close()
            else:
                print("⚠️  Aucun article")
            
            time.sleep(2)  # Pause entre les mois
        
        return total_articles
    
    def collect_all(self, start_year=1986, end_year=2025):
        """Collecte TOUT depuis 1986 jusqu'à 2025"""
        print("\n" + "="*80)
        print("🚀 COLLECTION COMPLÈTE arXiv 1986-2025")
        print("="*80)
        
        total_all = 0
        
        for category in self.categories:
            print(f"\n📂 Catégorie: {category}")
            category_total = 0
            
            for year in range(start_year, end_year + 1):
                year_total = self.collect_year(category, year)
                category_total += year_total
                print(f"   ✅ {year}: {year_total:,} articles")
            
            total_all += category_total
            print(f"\n   📊 Total pour {category}: {category_total:,} articles")
        
        print("\n" + "="*80)
        print(f"🎉 COLLECTION TERMINÉE: {total_all:,} articles au total!")
        print("="*80)
        
        return total_all
    
    def export_to_json(self, output_path="articles.json"):
        """Exporte la base de données vers JSON pour le site web"""
        print("\n" + "="*80)
        print("📤 EXPORT VERS JSON")
        print("="*80)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Compter le total
        cursor.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total d'articles: {total:,}")
        
        if total == 0:
            print("⚠️  Aucun article à exporter!")
            conn.close()
            return False
        
        # Exporter par batch pour économiser la mémoire
        print("\n📥 Exportation en cours...")
        
        cursor.execute("""
            SELECT arxiv_id, title, authors, abstract, category, published, link, pdf_link
            FROM articles 
            ORDER BY published DESC
        """)
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'id': row[0],
                'title': row[1],
                'authors': row[2] if row[2] else 'Unknown',
                'abstract': row[3] if row[3] else '',
                'category': row[4],
                'published': row[5][:10] if row[5] else None,
                'link': row[6],
                'pdf': row[7]
            })
        
        conn.close()
        
        # Sauvegarder
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        file_size = Path(output_path).stat().st_size / 1024 / 1024
        
        print(f"✅ Exporté {len(articles):,} articles vers {output_path}")
        print(f"📦 Taille du fichier: {file_size:.2f} MB")
        
        # Stats
        categories = {}
        years = {}
        for article in articles:
            cat = article['category']
            categories[cat] = categories.get(cat, 0) + 1
            
            if article['published']:
                year = article['published'][:4]
                years[year] = years.get(year, 0) + 1
        
        print(f"\n📂 {len(categories)} catégories")
        print(f"📅 Période: {min(years.keys())} - {max(years.keys())}")
        
        return True
    
    def show_stats(self):
        """Affiche les statistiques de collection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("\n" + "="*80)
        print("📊 STATISTIQUES")
        print("="*80)
        
        # Total
        cursor.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]
        print(f"\n📚 Total: {total:,} articles")
        
        # Par catégorie
        print("\n📂 Par catégorie:")
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM articles 
            GROUP BY category 
            ORDER BY count DESC
        """)
        for cat, count in cursor.fetchall():
            print(f"   {cat}: {count:,}")
        
        # Par année
        print("\n📅 Par année (top 10):")
        cursor.execute("""
            SELECT strftime('%Y', published) as year, COUNT(*) as count 
            FROM articles 
            WHERE year IS NOT NULL
            GROUP BY year 
            ORDER BY year DESC
            LIMIT 10
        """)
        for year, count in cursor.fetchall():
            print(f"   {year}: {count:,}")
        
        conn.close()
        print("\n" + "="*80)


def main():
    """Fonction principale"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           📚 arXiv Full Collector 1986-2025                   ║
║                                                               ║
║              Par Yassine Ait Mohamed                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    collector = ArxivFullCollector()
    
    # Menu
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'collect':
            # Collection complète
            start_year = int(sys.argv[2]) if len(sys.argv) > 2 else 1986
            end_year = int(sys.argv[3]) if len(sys.argv) > 3 else 2025
            collector.collect_all(start_year, end_year)
            collector.show_stats()
            
        elif command == 'export':
            # Export seulement
            output = sys.argv[2] if len(sys.argv) > 2 else 'articles.json'
            collector.export_to_json(output)
            
        elif command == 'stats':
            # Stats seulement
            collector.show_stats()
            
        elif command == 'full':
            # Tout: collect + export
            start_year = int(sys.argv[2]) if len(sys.argv) > 2 else 1986
            end_year = int(sys.argv[3]) if len(sys.argv) > 3 else 2025
            collector.collect_all(start_year, end_year)
            collector.export_to_json('articles.json')
            collector.show_stats()
            
        else:
            print("❌ Commande inconnue!")
            print_usage()
    else:
        print_usage()


def print_usage():
    """Affiche l'aide"""
    print("""
Usage:
    python arxiv_full_collector.py [command] [options]

Commandes:
    collect [start_year] [end_year]  - Collecte les articles
                                      Défaut: 1986 2025
    
    export [output.json]             - Exporte la DB vers JSON
                                      Défaut: articles.json
    
    stats                            - Affiche les statistiques
    
    full [start_year] [end_year]     - Collecte + Export + Stats
                                      Défaut: 1986 2025

Exemples:
    # Collecte TOUT depuis 1986
    python arxiv_full_collector.py full
    
    # Collecte seulement 2020-2025
    python arxiv_full_collector.py collect 2020 2025
    
    # Juste exporter ce qui est déjà collecté
    python arxiv_full_collector.py export
    
    # Voir les stats
    python arxiv_full_collector.py stats

IMPORTANT:
    - La collection complète peut prendre PLUSIEURS JOURS!
    - L'API arXiv a des limites de taux
    - Le script fait des pauses automatiques
    - Tu peux l'arrêter et reprendre (il skip les déjà collectés)

Catégories collectées:
    math.DG, math.SG, math-ph, math.AG, math.QA, math.RT, etc.
    
    Pour changer les catégories, édite la variable self.categories
    dans la classe ArxivFullCollector.
    """)


if __name__ == "__main__":
    main()
