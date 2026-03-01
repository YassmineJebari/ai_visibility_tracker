# ai_visibility_tracker# 🔭 AI Visibility Tracker

Analysez la visibilité de votre marque dans les moteurs de recherche IA (ChatGPT, Gemini, Perplexity).

## 🚀 Lancement en 3 étapes

### 1. Prérequis
- Python 3.9+
- Une clé API Groq gratuite → https://console.groq.com/keys

### 2. Installation

```bash
# Cloner / télécharger le projet, puis :
cd ai_visibility_tracker

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate        # Mac/Linux
# ou : venv\Scripts\activate    # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Lancer l'app

```bash
streamlit run app.py
```

L'app s'ouvre automatiquement sur http://localhost:8501

---

## 🎯 Comment ça marche

1. **Entre ton domaine** (ex: `decupler.com`)
2. **Renseigne ta clé Groq** dans la barre latérale
3. **Clique "Analyser →"**

L'app va :
- Détecter automatiquement le secteur d'activité
- Générer 6 requêtes types que des utilisateurs poseraient à une IA
- Simuler les réponses de ChatGPT/Gemini/Perplexity pour chaque requête
- Calculer un score de visibilité GEO (0-100)
- Identifier les concurrents qui apparaissent avant toi
- Générer des recommandations concrètes pour améliorer ta présence IA

---

## 📊 Métriques

| Score | Signification |
|-------|--------------|
| 75-100 | 🟢 Excellente visibilité |
| 50-74  | 🔵 Bonne visibilité |
| 25-49  | 🟡 Visibilité faible |
| 0-24   | 🔴 Marque invisible dans les LLMs |

---

## 🛠️ Stack technique

- **Frontend** : Streamlit (Python)
- **LLM** : LLaMA 3 70B via Groq API
- **Stockage** : Session state (historique en mémoire)
- **Export** : JSON

---

## 💡 Ce que mesure le GEO Score

Le GEO Score (Generative Engine Optimization) mesure :
- **Fréquence de citation** : combien de requêtes sur 6 mentionnent la marque
- **Position** : à quelle place dans la réponse la marque est citée
- **Type de mention** : directe, partielle, ou absente

---

## 📁 Structure du projet

```
ai_visibility_tracker/
├── app.py              # Application principale
├── requirements.txt    # Dépendances Python
└── README.md           # Ce fichier
```