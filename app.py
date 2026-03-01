import streamlit as st
import json
import re
import os
from datetime import datetime
from groq import Groq
import time

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Visibility Tracker",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme via query params
st.markdown("""
    <script>
        var observer = new MutationObserver(function() {
            document.documentElement.setAttribute('data-theme', 'light');
        });
        observer.observe(document.documentElement, {attributes: true});
        document.documentElement.setAttribute('data-theme', 'light');
    </script>
""", unsafe_allow_html=True)
# ─── STYLES ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0f0f13; }
    .stApp { background: #0f0f13; }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1a1a24;
        border: 1px solid #2d2d3d;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: #6366f1; }
    .metric-value {
        font-size: 2.4rem;
        font-weight: 700;
        color: #fff;
        line-height: 1;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.4rem;
    }
    .score-excellent { color: #10b981 !important; }
    .score-good      { color: #6366f1 !important; }
    .score-medium    { color: #f59e0b !important; }
    .score-poor      { color: #ef4444 !important; }

    .query-card {
        background: #1a1a24;
        border: 1px solid #2d2d3d;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .query-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
    }
    .query-text { color: #e5e7eb; font-weight: 500; font-size: 0.95rem; }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-found    { background: #064e3b; color: #10b981; }
    .badge-not-found{ background: #450a0a; color: #ef4444; }
    .badge-partial  { background: #451a03; color: #f59e0b; }

    .position-pill {
        background: #312e81;
        color: #a5b4fc;
        border-radius: 999px;
        padding: 0.15rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .competitor-tag {
        display: inline-block;
        background: #1e1b4b;
        color: #818cf8;
        border-radius: 6px;
        padding: 0.2rem 0.5rem;
        font-size: 0.78rem;
        margin: 0.15rem;
    }
    .reco-card {
        background: #1a1a24;
        border-left: 3px solid #6366f1;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .reco-priority-high   { border-left-color: #ef4444; }
    .reco-priority-medium { border-left-color: #f59e0b; }
    .reco-priority-low    { border-left-color: #10b981; }
    .reco-title { color: #e5e7eb; font-weight: 600; font-size: 0.95rem; }
    .reco-desc  { color: #9ca3af; font-size: 0.85rem; margin-top: 0.3rem; }

    .history-item {
        background: #1a1a24;
        border: 1px solid #2d2d3d;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
        cursor: pointer;
    }
    .history-domain { color: #a5b4fc; font-weight: 600; }
    .history-date   { color: #4b5563; font-size: 0.78rem; }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.8rem !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }

    .stTextInput > div > div > input {
        background: #1a1a24 !important;
        border: 1px solid #2d2d3d !important;
        color: #e5e7eb !important;
        border-radius: 10px !important;
    }
    .stSidebar { background: #0d0d17 !important; }
    div[data-testid="stSidebar"] { background: #0d0d17 !important; }

    .section-title {
        color: #e5e7eb;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2d2d3d;
    }
    .context-snippet {
        color: #9ca3af;
        font-size: 0.82rem;
        font-style: italic;
        margin-top: 0.4rem;
        line-height: 1.5;
    }
    .llm-label {
        font-size: 0.7rem;
        color: #4b5563;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .progress-bar-bg {
        background: #2d2d3d;
        border-radius: 999px;
        height: 8px;
        margin-top: 0.5rem;
    }
    .stExpander { border: 1px solid #2d2d3d !important; border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None


# ─── GROQ CLIENT ──────────────────────────────────────────────────────────────
def get_groq_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def llm_call(client: Groq, system: str, user: str, model="llama-3.3-70b-versatile", temperature=0.3) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=temperature,
        max_tokens=2048
    )
    return response.choices[0].message.content


# ─── STEP 1 : SECTOR DETECTION ────────────────────────────────────────────────
def detect_sector(client: Groq, domain: str) -> dict:
    prompt = f"""Analyse ce nom de domaine : {domain}

Déduis :
1. Le secteur d'activité principal
2. La cible probable (B2B, B2C, etc.)
3. Le pays/marché principal
4. 3 mots-clés principaux du secteur
5. Le type de service/produit

Réponds UNIQUEMENT en JSON valide, sans markdown, sans backticks :
{{"sector": "...", "target": "B2B|B2C|B2B2C", "market": "...", "keywords": ["...", "...", "..."], "service_type": "..."}}"""

    raw = llm_call(client, "Tu es un expert en analyse de marchés digitaux. Réponds uniquement en JSON valide sans backticks ni markdown.", prompt)
    # Clean potential markdown
    raw = re.sub(r"```json|```", "", raw).strip()
    # Extract JSON
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"sector": "Digital", "target": "B2B", "market": "France", "keywords": [domain], "service_type": "Services"}


# ─── STEP 2 : QUERY GENERATION ────────────────────────────────────────────────
def generate_queries(client: Groq, domain: str, sector_info: dict) -> list:
    prompt = f"""Domaine : {domain}
Secteur : {sector_info.get('sector')}
Service : {sector_info.get('service_type')}
Cible : {sector_info.get('target')}
Marché : {sector_info.get('market')}

Génère 6 requêtes de recherche réalistes qu'un utilisateur poserait à ChatGPT, Gemini ou Perplexity pour trouver ce type de service/produit.

Varie les types :
- Requêtes génériques du secteur
- Comparaisons / alternatives
- Recommandations ("meilleur X pour Y")
- Questions problème-solution

Réponds UNIQUEMENT en JSON valide :
{{"queries": ["requête 1", "requête 2", "requête 3", "requête 4", "requête 5", "requête 6"]}}"""

    raw = llm_call(client, "Expert SEO et GEO (Generative Engine Optimization). JSON uniquement.", prompt)
    raw = re.sub(r"```json|```", "", raw).strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        data = json.loads(match.group())
        return data.get("queries", [])
    return []


# ─── STEP 3 : SIMULATE LLM RESPONSE & ANALYZE VISIBILITY ─────────────────────
SIMULATED_LLMS = ["ChatGPT", "Gemini", "Perplexity"]

def analyze_query_visibility(client: Groq, domain: str, query: str, sector_info: dict) -> dict:
    brand = domain.replace("www.", "").split(".")[0].lower()

    prompt = f"""Tu dois simuler et analyser la visibilité d'une marque dans les réponses IA.

Domaine analysé : {domain}
Marque/brand : {brand}
Requête utilisateur : "{query}"
Secteur : {sector_info.get('sector')}

Fais comme si tu étais un LLM généraliste (ChatGPT/Gemini/Perplexity) qui répond à cette requête.

Puis analyse :
1. Est-ce que la marque "{brand}" serait naturellement citée ? (oui/non/partiel)
2. Si oui, à quelle position dans la réponse ? (1=première mention, 0=non citée)
3. Quels sont les 3-5 concurrents/alternatives qui seraient typiquement cités AVANT elle ?
4. Un extrait simulé de ce qu'un LLM répondrait (2-3 phrases)
5. Pourquoi ces concurrents apparaissent-ils avant ? (manque de contenu, autorité de domaine, etc.)

Réponds UNIQUEMENT en JSON valide :
{{
  "mentioned": "yes|no|partial",
  "position": 0,
  "competitors_before": ["concurrent1", "concurrent2", "concurrent3"],
  "simulated_snippet": "Réponse simulée du LLM...",
  "why_competitors_win": "Explication courte"
}}"""

    raw = llm_call(client, "Expert GEO et analyse de visibilité LLM. JSON uniquement.", prompt, temperature=0.5)
    raw = re.sub(r"```json|```", "", raw).strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"mentioned": "no", "position": 0, "competitors_before": [], "simulated_snippet": "", "why_competitors_win": ""}


# ─── STEP 4 : GENERATE RECOMMENDATIONS ───────────────────────────────────────
def generate_recommendations(client: Groq, domain: str, sector_info: dict, results: list) -> list:
    mentions_count = sum(1 for r in results if r.get("mentioned") == "yes")
    partial_count  = sum(1 for r in results if r.get("mentioned") == "partial")
    all_competitors = []
    for r in results:
        all_competitors.extend(r.get("competitors_before", []))
    top_competitors = list(dict.fromkeys(all_competitors))[:5]

    prompt = f"""Analyse de visibilité IA pour : {domain}
Secteur : {sector_info.get('sector')} | Marché : {sector_info.get('market')}
Résultats : {mentions_count}/{len(results)} requêtes avec mention directe, {partial_count} mentions partielles
Concurrents récurrents : {', '.join(top_competitors)}

Génère 5 recommandations concrètes et actionnables pour améliorer la visibilité de cette marque dans les LLMs (GEO - Generative Engine Optimization).

Pour chaque reco, inclus :
- Un titre court et percutant
- Une description actionnable (2-3 phrases)
- La priorité (high/medium/low)
- L'impact attendu (court terme / long terme)

Réponds UNIQUEMENT en JSON valide :
{{
  "recommendations": [
    {{
      "title": "...",
      "description": "...",
      "priority": "high|medium|low",
      "impact": "court terme|long terme",
      "category": "Contenu|Technique|Autorité|Structure|Notoriété"
    }}
  ]
}}"""

    raw = llm_call(client, "Expert GEO (Generative Engine Optimization) et stratégie de contenu IA. JSON uniquement.", prompt)
    raw = re.sub(r"```json|```", "", raw).strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        data = json.loads(match.group())
        return data.get("recommendations", [])
    return []


# ─── SCORE CALCULATION ────────────────────────────────────────────────────────
def compute_score(results: list) -> int:
    if not results:
        return 0
    total = 0
    for r in results:
        if r.get("mentioned") == "yes":
            pos = r.get("position", 5)
            total += max(0, 100 - (pos - 1) * 15)
        elif r.get("mentioned") == "partial":
            total += 30
    return min(100, int(total / len(results)))


def score_color(score: int) -> str:
    if score >= 75: return "score-excellent"
    if score >= 50: return "score-good"
    if score >= 25: return "score-medium"
    return "score-poor"


def score_label(score: int) -> str:
    if score >= 75: return "🟢 Excellente"
    if score >= 50: return "🔵 Bonne"
    if score >= 25: return "🟡 Faible"
    return "🔴 Invisible"


# ─── FULL ANALYSIS PIPELINE ───────────────────────────────────────────────────
def run_analysis(client: Groq, domain: str, progress_cb):
    domain = domain.strip().lower().replace("https://", "").replace("http://", "").rstrip("/")

    progress_cb(0.05, "🔍 Analyse du secteur...")
    sector_info = detect_sector(client, domain)
    time.sleep(0.3)

    progress_cb(0.15, "💡 Génération des requêtes types...")
    queries = generate_queries(client, domain, sector_info)
    time.sleep(0.3)

    query_results = []
    for i, query in enumerate(queries):
        pct = 0.2 + (i / len(queries)) * 0.55
        progress_cb(pct, f"🤖 Analyse requête {i+1}/{len(queries)} : « {query[:50]}... »")
        result = analyze_query_visibility(client, domain, query, sector_info)
        result["query"] = query
        query_results.append(result)
        time.sleep(0.2)

    progress_cb(0.80, "🧠 Génération des recommandations GEO...")
    recommendations = generate_recommendations(client, domain, sector_info, query_results)
    time.sleep(0.3)

    score = compute_score(query_results)

    progress_cb(1.0, "✅ Analyse terminée !")

    return {
        "domain": domain,
        "sector_info": sector_info,
        "queries": queries,
        "query_results": query_results,
        "recommendations": recommendations,
        "score": score,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "mentions_count": sum(1 for r in query_results if r.get("mentioned") == "yes"),
        "partial_count": sum(1 for r in query_results if r.get("mentioned") == "partial"),
        "all_competitors": list(dict.fromkeys([c for r in query_results for c in r.get("competitors_before", [])]))[:8]
    }


# ─── UI ───────────────────────────────────────────────────────────────────────

# SIDEBAR
with st.sidebar:
    st.markdown("### 🔭 AI Visibility Tracker")
    st.markdown("<hr style='border-color:#2d2d3d'>", unsafe_allow_html=True)

    api_key = st.text_input("Clé API Groq", type="password", placeholder="gsk_...")
    st.markdown("<small style='color:#4b5563'>→ <a href='https://console.groq.com/keys' style='color:#6366f1'>Obtenir une clé gratuite</a></small>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2d2d3d'>", unsafe_allow_html=True)
    st.markdown("### 📚 Historique")

    if st.session_state.history:
        for idx, h in enumerate(reversed(st.session_state.history[-5:])):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"<div class='history-domain'>{h['domain']}</div><div class='history-date'>{h['timestamp']}</div>", unsafe_allow_html=True)
            with col2:
                sc = h['score']
                color = "#10b981" if sc >= 75 else "#6366f1" if sc >= 50 else "#f59e0b" if sc >= 25 else "#ef4444"
                st.markdown(f"<div style='color:{color};font-weight:700;font-size:1.1rem;text-align:right'>{sc}</div>", unsafe_allow_html=True)
            if st.button("Recharger", key=f"reload_{idx}"):
                st.session_state.current_result = h
                st.rerun()
    else:
        st.markdown("<small style='color:#4b5563'>Aucune analyse encore</small>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2d2d3d'>", unsafe_allow_html=True)
    st.markdown("""
<small style='color:#4b5563'>
<b style='color:#6366f1'>GEO</b> = Generative Engine Optimization<br>
Mesure la présence d'une marque dans les réponses des IA génératives (ChatGPT, Gemini, Perplexity...)
</small>
""", unsafe_allow_html=True)


# MAIN CONTENT
st.markdown("<div class='hero-title'>🔭 AI Visibility Tracker</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-sub'>Analysez la visibilité de votre marque dans les moteurs de recherche IA</div>", unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    domain_input = st.text_input("", placeholder="ex: decupler.com ou votre-marque.fr", label_visibility="collapsed")
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("Analyser →", use_container_width=True)


# TRIGGER ANALYSIS
if analyze_btn:
    if not api_key:
        st.error("⚠️ Renseigne ta clé API Groq dans la barre latérale.")
    elif not domain_input.strip():
        st.error("⚠️ Entre un nom de domaine à analyser.")
    else:
        client = get_groq_client(api_key)
        progress_placeholder = st.empty()
        bar = st.progress(0)
        status_text = st.empty()

        def update_progress(pct, msg):
            bar.progress(pct)
            status_text.markdown(f"<div style='color:#9ca3af;font-size:0.88rem'>{msg}</div>", unsafe_allow_html=True)

        try:
            result = run_analysis(client, domain_input, update_progress)
            st.session_state.current_result = result
            # Save to history
            st.session_state.history.append(result)
            bar.empty()
            status_text.empty()
            st.rerun()
        except Exception as e:
            bar.empty()
            st.error(f"Erreur lors de l'analyse : {e}")


# DISPLAY RESULTS
if st.session_state.current_result:
    r = st.session_state.current_result
    score = r["score"]
    sector = r["sector_info"]

    st.markdown("---")

    # ── TOP METRICS ──
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (str(score), "Score GEO", score_color(score)),
        (score_label(score).split(" ", 1)[1], "Visibilité", score_color(score)),
        (f"{r['mentions_count']}/{len(r['query_results'])}", "Mentions directes", ""),
        (f"{r['partial_count']}", "Mentions partielles", ""),
        (str(len(r["all_competitors"])), "Concurrents détectés", ""),
    ]
    for col, (val, label, cls) in zip([c1, c2, c3, c4, c5], metrics):
        with col:
            st.markdown(f"""
<div class='metric-card'>
  <div class='metric-value {cls}'>{val}</div>
  <div class='metric-label'>{label}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SECTOR INFO BANNER ──
    st.markdown(f"""
<div style='background:#1a1a24;border:1px solid #2d2d3d;border-radius:12px;padding:1rem 1.5rem;margin-bottom:1.5rem;display:flex;gap:2rem;flex-wrap:wrap'>
  <span style='color:#6b7280;font-size:0.85rem'>🏢 <b style='color:#e5e7eb'>{sector.get("sector","—")}</b></span>
  <span style='color:#6b7280;font-size:0.85rem'>🎯 <b style='color:#e5e7eb'>{sector.get("target","—")}</b></span>
  <span style='color:#6b7280;font-size:0.85rem'>🌍 <b style='color:#e5e7eb'>{sector.get("market","—")}</b></span>
  <span style='color:#6b7280;font-size:0.85rem'>🔑 <b style='color:#e5e7eb'>{", ".join(sector.get("keywords",[]))}</b></span>
  <span style='color:#6b7280;font-size:0.85rem'>🕐 Analysé le {r.get("timestamp","—")}</span>
</div>""", unsafe_allow_html=True)

    # ── TABS ──
    tab1, tab2, tab3 = st.tabs(["🔍 Analyse par requête", "⚡ Recommandations GEO", "🏆 Concurrents"])

    with tab1:
        st.markdown("<div class='section-title'>Résultats par requête simulée</div>", unsafe_allow_html=True)
        for qr in r["query_results"]:
            mentioned = qr.get("mentioned", "no")
            badge_class = "badge-found" if mentioned == "yes" else "badge-partial" if mentioned == "partial" else "badge-not-found"
            badge_text  = "✓ Citée" if mentioned == "yes" else "~ Partielle" if mentioned == "partial" else "✗ Non citée"
            pos = qr.get("position", 0)
            pos_html = f"<span class='position-pill'>pos. #{pos}</span>" if pos > 0 else ""
            competitors = qr.get("competitors_before", [])
            comp_html = "".join([f"<span class='competitor-tag'>{c}</span>" for c in competitors]) if competitors else "<span style='color:#4b5563;font-size:0.8rem'>Aucun concurrent identifié</span>"

            with st.expander(f"{'🟢' if mentioned=='yes' else '🟡' if mentioned=='partial' else '🔴'}  {qr['query']}", expanded=False):
                st.markdown(f"""
<div style='margin-bottom:0.8rem'>
  <span class='badge {badge_class}'>{badge_text}</span> &nbsp; {pos_html}
</div>
<div style='margin-bottom:0.8rem'>
  <span style='color:#6b7280;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em'>Concurrents cités avant :</span><br>
  <div style='margin-top:0.3rem'>{comp_html}</div>
</div>
<div style='margin-bottom:0.8rem'>
  <span style='color:#6b7280;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em'>Pourquoi ils dominent :</span><br>
  <span style='color:#9ca3af;font-size:0.85rem'>{qr.get("why_competitors_win","—")}</span>
</div>
<div>
  <span style='color:#6b7280;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em'>Extrait simulé (LLM) :</span><br>
  <span class='context-snippet'>"{qr.get("simulated_snippet","—")}"</span>
</div>
""", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='section-title'>Recommandations pour améliorer ta visibilité GEO</div>", unsafe_allow_html=True)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recos = sorted(r.get("recommendations", []), key=lambda x: priority_order.get(x.get("priority", "low"), 2))

        for reco in recos:
            priority = reco.get("priority", "medium")
            priority_label = {"high": "🔴 Priorité haute", "medium": "🟡 Priorité moyenne", "low": "🟢 Priorité basse"}.get(priority, "")
            impact_label = reco.get("impact", "")
            category = reco.get("category", "")
            st.markdown(f"""
<div class='reco-card reco-priority-{priority}'>
  <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.3rem'>
    <div class='reco-title'>{reco.get("title","")}</div>
    <div style='display:flex;gap:0.4rem;flex-wrap:wrap'>
      <span style='font-size:0.7rem;color:#6b7280'>{priority_label}</span>
      <span style='font-size:0.7rem;background:#1e1b4b;color:#818cf8;padding:0.1rem 0.4rem;border-radius:4px'>{category}</span>
      <span style='font-size:0.7rem;background:#064e3b;color:#34d399;padding:0.1rem 0.4rem;border-radius:4px'>{impact_label}</span>
    </div>
  </div>
  <div class='reco-desc'>{reco.get("description","")}</div>
</div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='section-title'>Concurrents qui apparaissent dans les réponses IA</div>", unsafe_allow_html=True)

        all_comps_count = {}
        for qr in r["query_results"]:
            for c in qr.get("competitors_before", []):
                all_comps_count[c] = all_comps_count.get(c, 0) + 1

        if all_comps_count:
            sorted_comps = sorted(all_comps_count.items(), key=lambda x: -x[1])
            total_queries = len(r["query_results"])
            for comp, count in sorted_comps:
                pct = int((count / total_queries) * 100)
                st.markdown(f"""
<div style='background:#1a1a24;border:1px solid #2d2d3d;border-radius:10px;padding:0.9rem 1.2rem;margin-bottom:0.6rem'>
  <div style='display:flex;justify-content:space-between;align-items:center'>
    <span style='color:#e5e7eb;font-weight:600'>{comp}</span>
    <span style='color:#818cf8;font-size:0.85rem'>{count}/{total_queries} requêtes ({pct}%)</span>
  </div>
  <div class='progress-bar-bg'>
    <div style='background:linear-gradient(90deg,#6366f1,#8b5cf6);width:{pct}%;height:100%;border-radius:999px'></div>
  </div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#4b5563'>Aucun concurrent détecté dans cette analyse.</span>", unsafe_allow_html=True)

    # Export JSON
    st.markdown("---")
    col_exp1, col_exp2 = st.columns([3, 1])
    with col_exp2:
        export_data = json.dumps({k: v for k, v in r.items() if k != "sector_info"}, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ Exporter JSON",
            data=export_data,
            file_name=f"ai_visibility_{r['domain']}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

else:
    # EMPTY STATE
    st.markdown("""
<div style='text-align:center;padding:4rem 2rem;'>
  <div style='font-size:4rem;margin-bottom:1rem'>🔭</div>
  <div style='color:#e5e7eb;font-size:1.3rem;font-weight:600;margin-bottom:0.5rem'>Prêt à analyser ta visibilité IA</div>
  <div style='color:#6b7280;font-size:0.9rem;max-width:500px;margin:0 auto'>
    Entre un nom de domaine ci-dessus et lance l'analyse pour découvrir comment ta marque apparaît 
    (ou n'apparaît pas) dans les réponses de ChatGPT, Gemini et Perplexity.
  </div>
  <div style='margin-top:2rem;display:flex;justify-content:center;gap:2rem;flex-wrap:wrap'>
    <div style='background:#1a1a24;border:1px solid #2d2d3d;border-radius:12px;padding:1rem 1.5rem;text-align:center;min-width:130px'>
      <div style='font-size:1.5rem'>🤖</div>
      <div style='color:#a5b4fc;font-size:0.8rem;margin-top:0.3rem'>ChatGPT</div>
    </div>
    <div style='background:#1a1a24;border:1px solid #2d2d3d;border-radius:12px;padding:1rem 1.5rem;text-align:center;min-width:130px'>
      <div style='font-size:1.5rem'>✨</div>
      <div style='color:#a5b4fc;font-size:0.8rem;margin-top:0.3rem'>Gemini</div>
    </div>
    <div style='background:#1a1a24;border:1px solid #2d2d3d;border-radius:12px;padding:1rem 1.5rem;text-align:center;min-width:130px'>
      <div style='font-size:1.5rem'>🔍</div>
      <div style='color:#a5b4fc;font-size:0.8rem;margin-top:0.3rem'>Perplexity</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)