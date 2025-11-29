# 🚀 Guide Collecteur arXiv Complet (1986-2025)

## 📚 Ce Script Fait Quoi?

Le script `arxiv_full_collector.py` va:
1. ✅ Collecter TOUS les articles arXiv depuis 1986 jusqu'à 2025
2. ✅ Les stocker dans une base SQLite (`arxiv_full_collection.db`)
3. ✅ Exporter automatiquement vers JSON pour ton site web
4. ✅ Gérer les erreurs et retry automatiquement
5. ✅ Respecter les limites de l'API arXiv

## ⚡ Utilisation Rapide

### Option 1: TOUT EN UNE FOIS (Recommandé)

```bash
# Collecte TOUT depuis 1986 + Export JSON
python3 arxiv_full_collector.py full
```

**⏱️ Temps estimé:** Plusieurs jours (l'API est lente)

### Option 2: Période Spécifique

```bash
# Seulement les 5 dernières années
python3 arxiv_full_collector.py full 2020 2025

# Seulement une décennie
python3 arxiv_full_collector.py full 2010 2020
```

### Option 3: Juste la Collection (sans export)

```bash
# Collecter sans exporter
python3 arxiv_full_collector.py collect 1986 2025
```

### Option 4: Juste l'Export (si déjà collecté)

```bash
# Exporter la DB existante vers JSON
python3 arxiv_full_collector.py export articles.json
```

### Option 5: Voir les Statistiques

```bash
# Afficher les stats de la collection
python3 arxiv_full_collector.py stats
```

## 📋 Workflow Complet

### 1️⃣ Première Utilisation

```bash
# Lance la collection complète
python3 arxiv_full_collector.py full 1986 2025

# Résultat:
# - arxiv_full_collection.db (base SQLite)
# - articles.json (pour le site web)
```

### 2️⃣ Mettre à Jour le Site Web

```bash
# Copie le JSON dans ton dossier web
cp articles.json /chemin/vers/ton/site/

# Déploie sur GitHub
cd /chemin/vers/ton/site/
./deploy.sh
```

### 3️⃣ Mises à Jour Régulières

```bash
# Collecte seulement les nouveaux (2025)
python3 arxiv_full_collector.py collect 2025 2025

# Exporte
python3 arxiv_full_collector.py export

# Déploie
cd /chemin/vers/ton/site/
./deploy.sh
```

## ⚙️ Personnalisation

### Changer les Catégories

Édite le fichier `arxiv_full_collector.py` ligne 24:

```python
self.categories = [
    'math.DG',  # Differential Geometry
    'math.SG',  # Symplectic Geometry
    'math-ph',  # Mathematical Physics
    'math.AG',  # Algebraic Geometry
    'math.QA',  # Quantum Algebra
    'math.RT',  # Representation Theory
    # Ajoute les tiennes ici!
    'physics.quant-ph',  # Quantum Physics
    'cs.AI',  # Artificial Intelligence
]
```

**Liste complète des catégories arXiv:**
- https://arxiv.org/category_taxonomy

### Changer la Taille des Batches

Ligne 208:

```python
batch_size = 1000  # Change ce nombre (max 2000)
```

### Changer les Délais

```python
time.sleep(3)  # Pause entre requêtes (ligne 259)
time.sleep(2)  # Pause entre mois (ligne 280)
```

## 📊 Structure de la Base de Données

### Table `articles`

```sql
arxiv_id     TEXT PRIMARY KEY  - ID arXiv
title        TEXT              - Titre
authors      TEXT              - Auteurs (séparés par ;)
abstract     TEXT              - Résumé
category     TEXT              - Catégorie
published    DATE              - Date publication
updated      DATE              - Date mise à jour
link         TEXT              - Lien arXiv
pdf_link     TEXT              - Lien PDF
last_fetched TIMESTAMP         - Dernière collecte
```

### Table `collection_progress`

Garde trace de ce qui a été collecté pour éviter les doublons.

## ⚠️ Points Importants

### 1. Temps de Collection

**La collection COMPLÈTE prend DU TEMPS:**
- 1 catégorie, 1 année = ~30 minutes à 2 heures
- 10 catégories, 40 ans = **PLUSIEURS JOURS**

**Pourquoi?**
- L'API arXiv limite les requêtes (3 secondes entre chaque)
- Des milliers d'articles à traiter
- Sécurités anti-rate-limit

### 2. Reprendre Après Interruption

**Bonne nouvelle:** Tu peux arrêter (Ctrl+C) et reprendre!

Le script utilise `INSERT OR REPLACE`, donc:
- Les articles déjà collectés sont skippés
- Pas de doublons
- Tu peux relancer sans problème

### 3. Taille du Fichier JSON

**Attention:** Le JSON peut devenir ÉNORME!

Estimations:
- 1,000 articles ≈ 600 KB
- 10,000 articles ≈ 6 MB
- 100,000 articles ≈ 60 MB
- 1,000,000 articles ≈ 600 MB

**Si le fichier est trop gros (>100MB):**

**Option A: Filtrer par période**
```python
# Exporte seulement 2020-2025
# Modifie la requête SQL ligne 313
WHERE published >= '2020-01-01'
```

**Option B: Diviser en plusieurs fichiers**
```bash
# Crée un fichier par année
python3 arxiv_full_collector.py export articles_2024.json
```

**Option C: Utiliser Git LFS**
```bash
git lfs install
git lfs track "articles.json"
```

**Option D: Héberger le JSON ailleurs**
- Upload sur CDN (Cloudflare, AWS S3)
- Change l'URL dans `app.js`

### 4. Respecter l'API arXiv

**IMPORTANT:** L'API arXiv est gratuite mais limitée!

Règles:
- ✅ Max 1 requête toutes les 3 secondes
- ✅ Pas de requêtes parallèles
- ✅ Utiliser un User-Agent informatif
- ❌ Ne pas abuser

**Le script respecte déjà ces règles!**

## 🐛 Résolution de Problèmes

### Erreur: "Rate limit"

**Normal!** Le script attend automatiquement et réessaye.

### Erreur: "Timeout"

**Normal!** Réseaux lents. Le script réessaye 5 fois.

### Erreur: "No articles found"

Vérifie:
- La catégorie existe bien
- La période est valide (arXiv existe depuis 1991)
- Ta connexion internet

### Base de données corrompue

```bash
# Supprime et recommence
rm arxiv_full_collection.db
python3 arxiv_full_collector.py full
```

### JSON trop gros pour GitHub

Voir "Taille du Fichier JSON" ci-dessus.

## 📈 Monitoring

### Voir la Progression en Temps Réel

```bash
# Dans un autre terminal
watch -n 10 'sqlite3 arxiv_full_collection.db "SELECT COUNT(*) FROM articles"'
```

### Voir les Derniers Articles Collectés

```bash
sqlite3 arxiv_full_collection.db "SELECT arxiv_id, title, published FROM articles ORDER BY last_fetched DESC LIMIT 10"
```

### Voir le Progrès par Catégorie

```bash
python3 arxiv_full_collector.py stats
```

## 🎯 Exemples Réels

### Exemple 1: Test Rapide (1 mois)

```bash
# Teste avec juste janvier 2024
# Modifie temporairement collect_all() pour:
collector.collect_by_month('math.DG', 2024, 1)
```

### Exemple 2: Collection Progressive

```bash
# Jour 1: Collecte 2020-2025
python3 arxiv_full_collector.py collect 2020 2025

# Jour 2: Collecte 2010-2019
python3 arxiv_full_collector.py collect 2010 2019

# Jour 3: Collecte 2000-2009
python3 arxiv_full_collector.py collect 2000 2009

# Etc.

# À la fin: Export
python3 arxiv_full_collector.py export
```

### Exemple 3: Mise à Jour Quotidienne

Crée un cron job:

```bash
# Édite crontab
crontab -e

# Ajoute (lance tous les jours à 2h du matin)
0 2 * * * cd /chemin/vers/script && python3 arxiv_full_collector.py collect 2025 2025 && python3 arxiv_full_collector.py export
```

## 📊 Résultats Attendus

Pour les catégories math (1986-2025):

| Catégorie | Articles Estimés |
|-----------|-----------------|
| math.DG   | ~50,000         |
| math.AG   | ~60,000         |
| math.QA   | ~15,000         |
| math.SG   | ~10,000         |
| math-ph   | ~40,000         |
| **TOTAL** | **~200,000+**   |

**Taille DB:** ~500 MB  
**Taille JSON:** ~120 MB  
**Temps:** 3-5 jours

## 🚀 Optimisations

### Accélérer (avec prudence)

```python
# Réduis les pauses (ATTENTION: risque de ban!)
time.sleep(1)  # Au lieu de 3

# Augmente batch_size
batch_size = 2000  # Max autorisé
```

### Économiser de l'Espace

```python
# Ne garde que certains champs
# Modifie parse_response() pour exclure 'abstract'
```

## ✅ Checklist Finale

Avant de lancer:
- [ ] Python 3 installé
- [ ] Bibliothèques installées (`requests`)
- [ ] Connexion internet stable
- [ ] Espace disque suffisant (1+ GB)
- [ ] Temps disponible (plusieurs jours)
- [ ] Catégories configurées
- [ ] Période définie

Après collection:
- [ ] Vérifie les stats
- [ ] Exporte vers JSON
- [ ] Teste le JSON dans le site web
- [ ] Backup la base de données
- [ ] Déploie sur GitHub

## 🎉 Résultat Final

Tu auras:
1. ✅ Une base SQLite complète
2. ✅ Un fichier JSON pour ton site
3. ✅ Tous les articles arXiv 1986-2025
4. ✅ Mise à jour facile
5. ✅ Interface web fonctionnelle

---

**Questions? Check la doc complète ou le code (bien commenté)!**

**Créé avec ❤️ pour Yassine Ait Mohamed**

Bonne collection habibi! 🚀
