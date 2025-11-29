# 🤖 AUTOMATISATION GITHUB ACTIONS - Guide Complet

## 🎯 CE QUE ÇA FAIT

GitHub Actions va **AUTOMATIQUEMENT**:
1. ✅ Collecter les nouveaux articles arXiv **tous les jours à 2h**
2. ✅ Mettre à jour le fichier `articles.json`
3. ✅ Déployer ton site sur GitHub Pages
4. ✅ **TOUT ÇA SANS QUE TU TOUCHES À RIEN!** 🚀

## 📁 Fichiers Créés

```
.github/
└── workflows/
    ├── auto-update.yml         # Mise à jour quotidienne automatique
    ├── initial-collection.yml  # Collection complète (manuel)
    └── deploy-pages.yml        # Déploiement GitHub Pages
```

## 🚀 SETUP ULTRA RAPIDE (5 ÉTAPES)

### 📋 ÉTAPE 1: Créer le Repository GitHub

1. Va sur **github.com**
2. Click **"New repository"**
3. Nom: `arxiv-collection-pro`
4. ✅ **Public** (requis pour GitHub Pages gratuit)
5. ❌ **NE PAS** cocher "Add README"
6. Click **"Create repository"**

### 📦 ÉTAPE 2: Pousser Tous les Fichiers

```bash
cd /chemin/vers/tes/fichiers

# Initialise git
git init
git branch -M main

# Ajoute tout
git add .

# Commit
git commit -m "🚀 Initial commit - arXiv Collection Pro with GitHub Actions"

# Ajoute le remote (REMPLACE TON_USERNAME!)
git remote add origin https://github.com/TON_USERNAME/arxiv-collection-pro.git

# Push
git push -u origin main
```

### ⚙️ ÉTAPE 3: Activer GitHub Pages

1. Va dans ton repo sur GitHub
2. Click **Settings** ⚙️
3. Dans le menu gauche, click **Pages**
4. Sous "Build and deployment":
   - Source: **GitHub Actions**
5. Save

**C'est tout!** GitHub Pages est activé.

### 🔧 ÉTAPE 4: Donner les Permissions

1. Toujours dans **Settings**
2. Menu gauche → **Actions** → **General**
3. Scroll vers "Workflow permissions"
4. Sélectionne **"Read and write permissions"** ✅
5. Coche **"Allow GitHub Actions to create and approve pull requests"** ✅
6. Save

### 🎬 ÉTAPE 5: Lancer la Première Collection

#### Option A: Collection Complète (1986-2025)

⚠️ **ATTENTION:** Prend plusieurs jours!

1. Va dans ton repo GitHub
2. Click onglet **"Actions"**
3. Click **"Initial Full Collection (Manual)"** dans la liste à gauche
4. Click **"Run workflow"** (bouton à droite)
5. Configure:
   - Start year: `1986`
   - End year: `2025`
6. Click **"Run workflow"**

GitHub va maintenant collecter pendant **plusieurs jours**. Tu peux fermer la page!

#### Option B: Collection Partielle (Recommandé pour commencer!)

**Commence par 2020-2025:**

1. Actions → "Initial Full Collection"
2. Run workflow
3. Start year: `2020`
4. End year: `2025`
5. Run workflow

**Temps:** ~6-12 heures

#### Option C: Juste 2024-2025 (Test Rapide!)

1. Actions → "Initial Full Collection"
2. Start year: `2024`
3. End year: `2025`
4. Run workflow

**Temps:** ~1-2 heures

## 🔄 APRÈS LA PREMIÈRE COLLECTION

### Automatisation Quotidienne

Une fois la collection initiale terminée, le workflow **auto-update.yml** prend le relais:

✅ **Tous les jours à 2h UTC**, GitHub va:
1. Collecter les nouveaux articles de l'année en cours
2. Mettre à jour `articles.json`
3. Commit et push automatiquement
4. Déployer le site

**TU N'AS RIEN À FAIRE!** 🎉

### Lancement Manuel

Tu peux aussi lancer manuellement:

1. Actions → **"Auto Update arXiv Collection"**
2. Run workflow
3. Done!

## 📊 Suivre la Progression

### Pendant la Collection

1. Va dans **Actions**
2. Click sur le workflow en cours
3. Click sur le job (ex: "update-collection")
4. Tu verras les logs en temps réel!

### Vérifier les Résultats

```
Actions → Workflow terminé → Artifacts
```

Tu peux télécharger:
- `articles.json`
- `arxiv_full_collection.db`

## 🎨 Ton Site Sera Live À

```
https://TON_USERNAME.github.io/arxiv-collection-pro/
```

**Délai:** 1-2 minutes après chaque push

## 📅 Planning des Workflows

| Workflow | Quand | Durée | Purpose |
|----------|-------|-------|---------|
| `initial-collection.yml` | Manuel | 1 heure - 3 jours | Première collection |
| `auto-update.yml` | Tous les jours 2h UTC | 10-30 min | Nouveaux articles |
| `deploy-pages.yml` | À chaque push | 1-2 min | Déploie le site |

## 🔧 Configuration Avancée

### Changer l'Heure de Mise à Jour

Édite `.github/workflows/auto-update.yml` ligne 9:

```yaml
- cron: '0 2 * * *'  # 2h UTC
```

Exemples:
- `'0 0 * * *'` = Minuit UTC
- `'0 12 * * *'` = Midi UTC
- `'0 */6 * * *'` = Toutes les 6 heures

**Convertisseur:** https://crontab.guru/

### Changer les Catégories

Édite `arxiv_full_collector.py` ligne 24:

```python
self.categories = [
    'math.DG',
    'math.SG',
    # Ajoute les tiennes!
]
```

Puis commit et push:
```bash
git add arxiv_full_collector.py
git commit -m "Update categories"
git push
```

### Activer Update à Chaque Push

Édite `.github/workflows/auto-update.yml` lignes 11-12:

```yaml
# Décommente ces lignes:
push:
  branches: [ main ]
```

## 🐛 Troubleshooting

### Workflow échoue avec "Rate limit"

**Normal!** L'API arXiv limite les requêtes.

**Solution:** Le workflow réessayera automatiquement demain.

### "Permission denied" lors du push

**Fix:**
1. Settings → Actions → General
2. Workflow permissions → **Read and write** ✅
3. Save

### JSON > 100 MB

GitHub Actions n'aime pas les gros fichiers.

**Solutions:**

**Option 1: Git LFS**

Créé `.gitattributes`:
```bash
echo "*.json filter=lfs diff=lfs merge=lfs -text" > .gitattributes
echo "*.db filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
git add .gitattributes
git commit -m "Add Git LFS"
```

**Option 2: Filtrer les données**

Dans `arxiv_full_collector.py`, ligne 313:
```python
# Ajoute un WHERE dans la requête:
WHERE published >= '2020-01-01'
```

**Option 3: Héberger JSON ailleurs**

Upload sur Cloudflare R2 (gratuit):
```yaml
# Ajoute dans auto-update.yml après export:
- name: Upload to R2
  run: |
    # Script pour upload vers CDN
```

### Workflow bloqué / timeout

**Cause:** Collection trop longue (>6 heures)

**Fix:** Collecte par périodes plus courtes:
- Au lieu de 1986-2025
- Fais: 2020-2025, puis 2010-2019, etc.

### Site ne se met pas à jour

Vérifie:
1. Le workflow s'est terminé avec succès ✅
2. Les fichiers ont été commit et push
3. GitHub Pages est activé
4. Attends 2-3 minutes

## 🎯 Workflow Optimal

### Première Semaine

**Jour 1:**
```
Actions → Initial Collection → 2024-2025
```

**Jour 2:** (après succès jour 1)
```
Actions → Initial Collection → 2020-2023
```

**Jour 3:** (après succès jour 2)
```
Actions → Initial Collection → 2015-2019
```

Continue comme ça jusqu'à 1986!

### Après Setup Initial

**Rien à faire!** 🎉

Le workflow `auto-update.yml` tourne tous les jours automatiquement.

## 📊 Monitoring

### Recevoir des Notifications

1. Settings → Notifications
2. Actions → ✅ "Email notifications for failed workflows"

Tu seras alerté si un workflow échoue!

### Vérifier les Stats

Check les artifacts dans Actions:
- Download `arxiv-collection-XXX`
- Ouvre `articles.json` pour voir le nombre

## 💡 Astuces Pro

### 1. Badge de Status

Ajoute dans ton README.md:

```markdown
![Update Status](https://github.com/TON_USERNAME/arxiv-collection-pro/actions/workflows/auto-update.yml/badge.svg)
```

### 2. Logs Détaillés

Pour debug, ajoute dans le workflow:

```yaml
- name: Debug
  run: |
    ls -lah
    cat articles.json | head -n 50
```

### 3. Backup Automatique

Les artifacts sont gardés 30 jours!

Pour garder plus longtemps, change dans le workflow:

```yaml
retention-days: 90  # 3 mois
```

### 4. Multi-branches

Crée une branche `dev` pour tester:

```bash
git checkout -b dev
git push -u origin dev
```

Teste les workflows sur `dev` avant de merger sur `main`!

## ✅ Checklist Finale

Avant de lancer:

- [ ] Repository GitHub créé
- [ ] Tous les fichiers poussés
- [ ] GitHub Pages activé (Source: GitHub Actions)
- [ ] Workflow permissions: Read and write ✅
- [ ] Workflows présents dans `.github/workflows/`
- [ ] Categories configurées dans le script
- [ ] Premier workflow lancé (manual)

Après premier workflow:

- [ ] Workflow terminé avec succès
- [ ] `articles.json` créé et commit
- [ ] Site accessible à l'URL GitHub Pages
- [ ] Auto-update activé (schedule)

## 🎊 RÉSULTAT FINAL

Tu auras:

✅ Site web live sur GitHub Pages  
✅ Mise à jour **AUTOMATIQUE** tous les jours  
✅ Backup automatique dans Artifacts  
✅ Historique complet dans Git  
✅ **ZERO maintenance!** 🚀  

## 📞 Aide Rapide

### Ça marche pas?

1. Check Actions → Workflow → Logs (détails de l'erreur)
2. Vérifie Settings → Actions → Permissions
3. Essaye avec une période plus courte
4. Lis les logs d'erreur dans Actions

### Ça marche!

1. Vérifie ton site: `https://TON_USERNAME.github.io/arxiv-collection-pro/`
2. Check les artifacts pour download
3. Relax! GitHub fait le reste 😎

---

## 🎉 FÉLICITATIONS!

Ton site arXiv est maintenant **100% AUTOMATIQUE** sur GitHub!

**Plus besoin de lancer de scripts manuellement!**

**GitHub Actions fait TOUT pour toi!** 🤖✨

---

**Créé avec ❤️ pour Yassine Ait Mohamed**

**Bonne automatisation habibi! 🚀**
