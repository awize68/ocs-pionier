import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="PIONIER - Advanced Operations Cockpit",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS POUR LE STYLE PROFESSIONNEL ET LES ANIMATIONS ---
st.markdown("""
<style>
/* Import des icônes Font Awesome */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

/* Style général de la page */
body { background-color: #0E1117; color: #FAFAFA; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

/* Titre principal */
.main-title { font-size: 2.5rem; font-weight: 700; color: #FFFFFF; text-align: center; margin-bottom: 1rem; text-shadow: 0 0 10px rgba(255, 69, 0, 0.5); }

/* Style pour chaque carte d'équipement */
.asset-card { background-color: #262730; border: 1px solid #434654; border-radius: 12px; padding: 20px; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); }
.asset-card:hover { transform: scale(1.03); box-shadow: 0 8px 24px rgba(0, 150, 255, 0.3); border-color: #00BFFF; }
.asset-card.grow { transform: scale(1.05); z-index: 10; box-shadow: 0 10px 30px rgba(0, 255, 150, 0.4); border-color: #00FF7F; }

/* En-tête et contenu de la carte */
.card-header { display: flex; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #434654; padding-bottom: 10px; }
.card-header i { font-size: 1.5rem; margin-right: 15px; color: #00BFFF; }
.card-header h3 { margin: 0; font-size: 1.2rem; font-weight: 600; color: #FFFFFF; }
.card-content { display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; }
.metric { text-align: center; padding: 10px; }
.metric-label { font-size: 0.8rem; color: #B0B3B8; text-transform: uppercase; letter-spacing: 1px; }
.metric-value { font-size: 1.8rem; font-weight: 700; margin-top: 5px; }

/* Code couleur pour la santé et les tendances */
.health-good { color: #00FF7F; }
.health-warning { color: #FFD700; }
.health-critical { color: #FF4500; }
.trend-up { color: #FF4500; }
.trend-down { color: #00FF7F; }

/* Style pour la barre latérale et le journal des événements */
.sidebar .sidebar-content { background-color: #262730; }
.event-log-container { height: 250px; overflow-y: auto; background-color: #1e1f26; border-radius: 8px; padding: 10px; }
.event-log-entry { padding: 8px; border-left: 3px solid #434654; margin-bottom: 5px; }
.event-log-entry.warning { border-left-color: #FFD700; }
.event-log-entry.error { border-left-color: #FF4500; }
.event-log-entry.success { border-left-color: #00FF7F; }
</style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT POUR L'INTERACTIVITÉ (CLIC) ---
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


# --- CLASSE POUR SIMULER LES DONNÉES D'UN ÉQUIPEMENT ---
class AssetData:
    """Représente un équipement industriel avec son état et sa logique de simulation."""
    def __init__(self, name, icon, initial_health=95):
        self.name = name
        self.icon = icon
        self.health = initial_health
        self.previous_health = initial_health
        self.temp = random.uniform(75, 85)
        self.vibration = random.uniform(2.0, 4.0)
        self.status = "Operational"
        self.last_status = "Operational"  # Mémorise le statut précédent pour un logging intelligent
        self.degradation_rate = random.uniform(0.05, 0.15)
        self.anomaly_chance = 0.02
        self.active_alerts = []
        
    def update(self):
        """Met à jour l'état de l'équipement à chaque cycle de simulation."""
        self.previous_health = self.health
        self.health -= self.degradation_rate
        self.health = max(0, self.health)

        # Simule des anomalies aléatoires (pics de vibration)
        if random.random() < self.anomaly_chance:
            self.vibration += random.uniform(5, 8)
            self.add_event("warning", f"Vibration spike detected on {self.name}.")
        else:
            # Corrèle la température et la vibration à la santé
            self.vibration = 2.0 + (100 - self.health) * 0.1 + random.uniform(-0.5, 0.5)
            self.temp = 75 + (100 - self.health) * 0.5 + random.uniform(-2, 2)

        self._check_and_generate_alerts()
        self.last_status = self.status # Met à jour le statut pour le prochain cycle

    def _check_and_generate_alerts(self):
        """Vérifie l'état de santé et génère des alertes et des événements."""
        self.active_alerts = []
        new_status = "Operational"

        if self.health > 80:
            new_status = "Operational"
        elif self.health > 50:
            new_status = "Anomaly Detected"
            self.active_alerts.append({"level": "warning", "title": "Performance Degradation", "recommendation": "Schedule visual inspection."})
        elif self.health > 20:
            new_status = "Maintenance Required"
            self.active_alerts.append({"level": "error", "title": "Critical Wear", "recommendation": "Plan parts replacement within 48h."})
        else:
            new_status = "Imminent Failure"
            self.degradation_rate = 0
            self.active_alerts.append({"level": "error", "title": "IMMINENT FAILURE", "recommendation": "SHUTDOWN IMMEDIATELY."})
        
        # --- LOGGING INTELLIGENT : Ne loggue que si le statut change ---
        if new_status != self.last_status:
            if new_status == "Imminent Failure": self.add_event("error", f"Imminent failure predicted for {self.name}!")
            elif new_status == "Maintenance Required": self.add_event("error", f"Critical state reached on {self.name}.")
            elif new_status == "Anomaly Detected": self.add_event("warning", f"Performance anomaly detected on {self.name}.")
            elif new_status == "Operational" and self.last_status != "Operational": self.add_event("success", f"{self.name} is back to operational status.")

        self.status = new_status

    def trigger_catastrophic_failure(self):
        """Action pour simuler une panne catastrophique."""
        self.health = 5
        self.vibration = 15.0
        self.temp = 150.0
        self.status = "Imminent Failure"
        self.add_event("error", f"Catastrophic failure SIMULATED on {self.name}!")
        st.toast(f"🚨 CATASTROPHIC FAILURE on {self.name}!", icon="🚨")

    def perform_maintenance(self):
        """Action pour simuler une maintenance réussie."""
        self.health = random.randint(92, 99)
        self.temp = random.uniform(75, 80)
        self.vibration = random.uniform(2.0, 3.5)
        self.status = "Operational (Post-Maintenance)"
        self.degradation_rate = random.uniform(0.05, 0.15)
        self.active_alerts = []
        self.add_event("success", f"Maintenance successfully performed on {self.name}.")

    def add_event(self, level, message):
        """Ajoute un événement au journal global."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        event = {"time": timestamp, "level": level, "message": message}
        st.session_state.event_log.insert(0, event) # Ajoute au début de la liste

# --- INITIALISATION DE L'ÉTAT DE L'APPLICATION ---
# Ce bloc ne s'exécute qu'une seule fois par session utilisateur
if 'assets' not in st.session_state:
    st.session_state.assets = {
        "P-101": AssetData("Centrifugal Pump P-101", "fa-oil-can", initial_health=90),
        "C-205": AssetData("Compressor C-205", "fa-wind", initial_health=75),
        "T-310": AssetData("Gas Turbine T-310", "fa-fan", initial_health=60),
        "R-420": AssetData("Chemical Reactor R-420", "fa-flask", initial_health=98),
    }
if 'event_log' not in st.session_state:
    st.session_state.event_log = []

# --- LOGIQUE PRINCIPALE DE L'APPLICATION ---

st.markdown('<h1 class="main-title">PIONIER Advanced Operations Cockpit</h1>', unsafe_allow_html=True)

# --- BARRE LATÉRALE : PANNEAU DE CONTRÔLE, ALERTES ET JOURNAL ---
with st.sidebar:
    st.title("🎛️ Control & Alerts")

    # Panneau des alertes actives
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

    # Contrôles de simulation
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
    
    # Journal des événements
    st.markdown("### 📜 Event Log")
    with st.container():
        log_html = '<div class="event-log-container">'
        if not st.session_state.event_log:
            log_html += '<p style="color: #888;">No events yet.</p>'
        else:
            # --- CORRECTION APPLIQUÉE ICI ---
            for event in st.session_state.event_log[:20]:
                log_html += f"<div class=\"event-log-entry {event['level']}\"><b>{event['time']}</b> - {event['message']}</div>"
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)


# --- ZONE PRINCIPALE : CARTES DES ÉQUIPEMENTS ---

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
    
    trend_icon = '<i class="fas fa-arrow-trend-up trend-up"></i>' if asset.health < asset.previous_health else ('<i class="fas fa-arrow-trend-down trend-down"></i>' if asset.health > asset.previous_health else '')

    # Générer le HTML pour une carte
    card_html = f"""
    <div class="asset-card">
        <div class="card-header"><i class="fas {asset.icon}"></i><h3>{asset.name}</h3></div>
        <div class="card-content">
            <div class="metric"><div class="metric-label">AI Health {trend_icon}</div><div class="metric-value {health_color_class}">{asset.health:.1f}%</div></div>
            <div class="metric"><div class="metric-label">Temp (°C)</div><div class="metric-value">{asset.temp:.1f}</div></div>
            <div class="metric"><div class="metric-label">Vibration (mm/s)</div><div class="metric-value">{asset.vibration:.2f}</div></div>
        </div>
    </div>
    """
    with col:
        st.markdown(card_html, unsafe_allow_html=True)

# --- BOUCLE DE SIMULATION EN TEMPS RÉEL ---
st.caption(f"Last update: {time.strftime('%H:%M:%S')}")
time.sleep(simulation_speed)
st.rerun()
