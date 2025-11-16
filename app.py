import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="PIONIER - Predictive Operations Cockpit",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS POUR LE STYLE PROFESSIONNEL ---
st.markdown("""
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
body { background-color: #0E1117; color: #FAFAFA; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.main-title { font-size: 2.5rem; font-weight: 700; color: #FFFFFF; text-align: center; margin-bottom: 1rem; text-shadow: 0 0 10px rgba(0, 255, 150, 0.5); }
.asset-card { background-color: #262730; border: 1px solid #434654; border-radius: 12px; padding: 20px; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); }
.asset-card:hover { transform: scale(1.03); box-shadow: 0 8px 24px rgba(0, 150, 255, 0.3); border-color: #00BFFF; }
.asset-card.grow { transform: scale(1.05); z-index: 10; box-shadow: 0 10px 30px rgba(0, 255, 150, 0.4); border-color: #00FF7F; }
.card-header { display: flex; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #434654; padding-bottom: 10px; }
.card-header i { font-size: 1.5rem; margin-right: 15px; color: #00BFFF; }
.card-header h3 { margin: 0; font-size: 1.2rem; font-weight: 600; color: #FFFFFF; }
.card-content { display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; }
.metric { text-align: center; padding: 10px; }
.metric-label { font-size: 0.8rem; color: #B0B3B8; text-transform: uppercase; letter-spacing: 1px; }
.metric-value { font-size: 1.8rem; font-weight: 700; margin-top: 5px; }
.prediction-date { font-size: 1.1rem; font-weight: 600; color: #FFD700; text-align: center; margin-top: 10px; padding: 8px; background-color: rgba(255, 215, 0, 0.1); border-radius: 8px; }
.health-good { color: #00FF7F; }
.health-warning { color: #FFD700; }
.health-critical { color: #FF4500; }
.sidebar .sidebar-content { background-color: #262730; }
.event-log-container { height: 250px; overflow-y: auto; background-color: #1e1f26; border-radius: 8px; padding: 10px; }
.event-log-entry { padding: 8px; border-left: 3px solid #434654; margin-bottom: 5px; }
.event-log-entry.warning { border-left-color: #FFD700; }
.event-log-entry.error { border-left-color: #FF4500; }
.event-log-entry.success { border-left-color: #00FF7F; }
</style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT POUR L'INTERACTIVITÉ ---
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.asset-card');
    cards.forEach(card => {
        card.addEventListener('click', function() {
            if (this.classList.contains('grow')) { this.classList.remove('grow'); }
            else { cards.forEach(c => c.classList.remove('grow')); this.classList.add('grow'); }
        });
    });
});
</script>
""", unsafe_allow_html=True)


# --- CLASSE ASSETDATA AMÉLIORÉE POUR LA PRÉDICTION ---
class AssetData:
    """
    Représente un équipement avec une logique de simulation avancée
    incluant la prédiction de la date de panne et le calcul des coûts.
    """
    def __init__(self, name, icon, initial_health, degradation_rate, cost_of_failure):
        self.name = name
        self.icon = icon
        self.health = initial_health
        self.previous_health = initial_health
        self.status = "Operational"
        self.last_status = "Operational"
        self.degradation_rate = degradation_rate  # Taux de dégradation par cycle
        self.cost_of_failure = cost_of_failure  # Coût d'une panne catastrophique
        self.active_alerts = []
        
        # --- Fonctionnalités Prédictives ---
        self.predicted_failure_date = None
        self.time_to_failure_hours = None

    def update(self):
        """Met à jour l'état de l'équipement et calcule la prédiction."""
        self.previous_health = self.health
        self.health -= self.degradation_rate
        self.health = max(0, self.health)

        # --- Calcul de la prédiction de panne ---
        # Si la santé est parfaite, on ne prédit pas de panne
        if self.health >= 99:
            self.predicted_failure_date = None
            self.time_to_failure_hours = None
        else:
            # Calcul simple : il reste 'health' points à perdre, à un rythme de 'degradation_rate' par cycle.
            # Un cycle est de 3 secondes dans notre simulation, mais nous le traitons comme une heure pour le calcul.
            hours_to_failure = (self.health / self.degradation_rate)
            self.time_to_failure_hours = int(hours_to_failure)
            self.predicted_failure_date = datetime.now() + timedelta(hours=hours_to_failure)

        # --- Génération des alertes basées sur la prédiction ---
        self._check_and_generate_alerts()
        self.last_status = self.status

    def _check_and_generate_alerts(self):
        """Génère des alertes en fonction du temps avant la panne prédit."""
        self.active_alerts = []
        new_status = "Operational"

        if self.time_to_failure_hours is None:
            new_status = "Operational"
        elif self.time_to_failure_hours > 168: # Plus de 7 jours
            new_status = "Operational"
        elif self.time_to_failure_hours > 72: # Entre 3 et 7 jours
            new_status = "Anomaly Detected"
            self.active_alerts.append({"level": "warning", "title": "Performance Degradation", "recommendation": "Schedule inspection within the week."})
        elif self.time_to_failure_hours > 24: # Entre 1 et 3 jours
            new_status = "Maintenance Required"
            self.active_alerts.append({"level": "error", "title": "Critical Wear Detected", "recommendation": "Plan parts replacement within 48 hours."})
        else: # Moins de 24h
            new_status = "Imminent Failure"
            self.degradation_rate = 0 # Arrêter la dégradation
            self.active_alerts.append({"level": "error", "title": "IMMINENT FAILURE", "recommendation": "SHUTDOWN IMMEDIATELY. Emergency maintenance required."})
        
        # --- Logging intelligent des changements de statut ---
        if new_status != self.last_status:
            if new_status == "Imminent Failure": self.add_event("error", f"Imminent failure predicted for {self.name} within {self.time_to_failure_hours} hours!")
            elif new_status == "Maintenance Required": self.add_event("error", f"Critical state reached on {self.name}. Failure predicted in {self.time_to_failure_hours} hours.")
            elif new_status == "Anomaly Detected": self.add_event("warning", f"Performance anomaly detected on {self.name}.")
            elif new_status == "Operational" and self.last_status != "Operational": self.add_event("success", f"{self.name} is back to operational status.")

        self.status = new_status

    def trigger_catastrophic_failure(self):
        """Simule une panne catastrophique."""
        self.health = 5
        self.time_to_failure_hours = 0
        self.predicted_failure_date = datetime.now()
        self.status = "Imminent Failure"
        self.add_event("error", f"Catastrophic failure SIMULATED on {self.name}!")
        st.toast(f"🚨 CATASTROPHIC FAILURE on {self.name}!", icon="🚨")

    def perform_maintenance(self):
        """Simule une maintenance réussie."""
        self.health = random.randint(92, 99)
        self.status = "Operational (Post-Maintenance)"
        self.degradation_rate = random.uniform(0.05, 0.15) # Le taux de dégradation peut changer après une maintenance
        self.active_alerts = []
        self.predicted_failure_date = None
        self.time_to_failure_hours = None
        self.add_event("success", f"Maintenance successfully performed on {self.name}.")

    def add_event(self, level, message):
        """Ajoute un événement au journal global."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        event = {"time": timestamp, "level": level, "message": message}
        st.session_state.event_log.insert(0, event)

# --- INITIALISATION DE L'ÉTAT AVEC DES DONNÉES RICHES ---
# Chaque actif a un état de départ et un taux de dégradation différent pour créer un scénario riche.
if 'assets' not in st.session_state:
    st.session_state.assets = {
        "P-101": AssetData("Centrifugal Pump P-101", "fa-oil-can", initial_health=95, degradation_rate=0.08, cost_of_failure=85000),
        "C-205": AssetData("Compressor C-205", "fa-wind", initial_health=75, degradation_rate=0.12, cost_of_failure=120000),
        "T-310": AssetData("Gas Turbine T-310", "fa-fan", initial_health=40, degradation_rate=0.15, cost_of_failure=250000), # Actif critique
        "R-420": AssetData("Chemical Reactor R-420", "fa-flask", initial_health=98, degradation_rate=0.05, cost_of_failure=500000),
    }
if 'event_log' not in st.session_state:
    st.session_state.event_log = []

# --- LOGIQUE PRINCIPALE DE L'APPLICATION ---

st.markdown('<h1 class="main-title">PIONIER - Predictive Operations Cockpit</h1>', unsafe_allow_html=True)

# --- BARRE LATÉRALE : ALERTES, PERSPECTIVE ET CONTRÔLE ---
with st.sidebar:
    st.title("🎛️ Control & Perspective")

    # --- Panneau des alertes actives ---
    st.markdown("### 🔔 Active Alerts")
    all_alerts = []
    for asset in st.session_state.assets.values():
        for alert in asset.active_alerts:
            all_alerts.append({**alert, "asset": asset.name})

    if not all_alerts:
        st.success("✅ All systems nominal.")
    else:
        for alert in all_alerts:
            if alert["level"] == "error": st.error(f"**{alert['asset']}**: {alert['title']}\n*{alert['recommendation']}*")
            else: st.warning(f"**{alert['asset']}**: {alert['title']}\n*{alert['recommendation']}*")
    
    st.markdown("---")

    # --- NOUVEAU : PANNEAU DE PERSPECTIVE DE MAINTENANCE ---
    st.markdown("### 📈 Maintenance Perspective")
    
    # Créer un planning de maintenance prédictive
    maintenance_schedule = []
    total_potential_savings = 0
    
    for asset in st.session_state.assets.values():
        if asset.predicted_failure_date and asset.time_to_failure_hours < 168: # Moins de 7 jours
            maintenance_schedule.append({
                "Asset": asset.name,
                "Predicted Failure": asset.predicted_failure_date.strftime("%Y-%m-%d %H:%M"),
                "Hours to Failure": f"{asset.time_to_failure_hours} h",
                "Cost of Failure": f"${asset.cost_of_failure:,}"
            })
            # On estime qu'une maintenance planifiée coûte 10% de la panne
            total_potential_savings += asset.cost_of_failure * 0.9

    if maintenance_schedule:
        st.dataframe(pd.DataFrame(maintenance_schedule), use_container_width=True)
        
        # Afficher le KPI de coût évité
        st.metric(
            "Potential Savings (Next 7 Days)",
            f"${total_potential_savings:,}",
            delta="vs. reactive maintenance"
        )
    else:
        st.info("No critical maintenance predicted in the next 7 days.")

    st.markdown("---")

    # --- Contrôles de simulation ---
    st.markdown("### ⚙️ Simulation Controls")
    asset_keys = list(st.session_state.assets.keys())
    selected_asset_key = st.selectbox("Select an Asset:", asset_keys)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Trigger Maintenance", type="primary", use_container_width=True):
            st.session_state.assets[selected_asset_key].perform_maintenance()
            st.rerun()
    with col2:
        if st.button("Simulate Failure", type="secondary", use_container_width=True):
            st.session_state.assets[selected_asset_key].trigger_catastrophic_failure()
            st.rerun()

    simulation_speed = st.slider("Refresh Speed (seconds):", 1, 10, 3)

    st.markdown("---")
    
    # --- Journal des événements ---
    st.markdown("### 📜 Event Log")
    with st.container():
        log_html = '<div class="event-log-container">'
        if not st.session_state.event_log:
            log_html += '<p style="color: #888;">No events yet.</p>'
        else:
            for event in st.session_state.event_log[:20]:
                log_html += f"<div class=\"event-log-entry {event['level']}\"><b>{event['time']}</b> - {event['message']}</div>"
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)


# --- ZONE PRINCIPALE : CARTES DES ÉQUIPEMENTS AVEC PRÉDICTION ---

# 1. Mettre à jour l'état de tous les équipements
for asset in st.session_state.assets.values():
    asset.update()

# 2. Créer les colonnes pour la mise en page
cols = st.columns(len(st.session_state.assets))

# 3. Itérer sur les colonnes et les équipements pour afficher chaque carte
for i, (col, (key, asset)) in enumerate(zip(cols, st.session_state.assets.items())):
    
    # Déterminer la couleur et la tendance
    if asset.health > 80: health_color_class = "health-good"
    elif asset.health > 50: health_color_class = "health-warning"
    else: health_color_class = "health-critical"
    
    # Formater la date de panne prédite pour l'affichage
    prediction_text = "No failure predicted"
    if asset.predicted_failure_date:
        if asset.time_to_failure_hours > 24:
            prediction_text = f"Failure in {asset.time_to_failure_hours // 24} days"
        else:
            prediction_text = f"Failure in {asset.time_to_failure_hours} hours!"

    # Générer le HTML pour une carte avec la prédiction
    card_html = f"""
    <div class="asset-card">
        <div class="card-header"><i class="fas {asset.icon}"></i><h3>{asset.name}</h3></div>
        <div class="card-content">
            <div class="metric"><div class="metric-label">AI Health</div><div class="metric-value {health_color_class}">{asset.health:.1f}%</div></div>
            <div class="metric"><div class="metric-label">Temp (°C)</div><div class="metric-value">{85 + (100 - asset.health) * 0.5:.1f}</div></div>
            <div class="metric"><div class="metric-label">Vibration (mm/s)</div><div class="metric-value">{2.0 + (100 - asset.health) * 0.1:.2f}</div></div>
        </div>
        <div class="prediction-date">
            <i class="fas fa-clock"></i> {prediction_text}
        </div>
    </div>
    """
    with col:
        st.markdown(card_html, unsafe_allow_html=True)

# --- BOUCLE DE SIMULATION EN TEMPS RÉEL ---
st.caption(f"Last update: {time.strftime('%H:%M:%S')}")
time.sleep(simulation_speed)
st.rerun()
