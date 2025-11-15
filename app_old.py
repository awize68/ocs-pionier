import streamlit as st
import time
import random
import pandas as pd

# --- Configuration de la page ---
st.set_page_config(
    page_title="PIONIER - Dashboard de Contrôle Temps Réel",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS pour le style et les animations ---
# (Le CSS reste le même que la version précédente, il est déjà très bien)
st.markdown("""
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
body { background-color: #0E1117; color: #FAFAFA; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.main-title { font-size: 2.5rem; font-weight: 700; color: #FFFFFF; text-align: center; margin-bottom: 1rem; text-shadow: 0 0 10px rgba(0, 150, 255, 0.5); }
.zones-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; padding: 10px; }
.zone { background-color: #262730; border: 1px solid #434654; border-radius: 12px; padding: 20px; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); position: relative; overflow: hidden; }
.zone:hover { transform: scale(1.03); box-shadow: 0 8px 24px rgba(0, 150, 255, 0.3); border-color: #00BFFF; }
.zone.grow { transform: scale(1.05); z-index: 10; box-shadow: 0 10px 30px rgba(0, 255, 150, 0.4); border-color: #00FF7F; }
.zone-header { display: flex; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #434654; padding-bottom: 10px; }
.zone-header i { font-size: 1.5rem; margin-right: 15px; color: #00BFFF; }
.zone-header h3 { margin: 0; font-size: 1.2rem; font-weight: 600; color: #FFFFFF; }
.zone-content { display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; }
.metric { text-align: center; padding: 10px; }
.metric-label { font-size: 0.8rem; color: #B0B3B8; text-transform: uppercase; letter-spacing: 1px; }
.metric-value { font-size: 1.8rem; font-weight: 700; margin-top: 5px; }
.health-good { color: #00FF7F; }
.health-warning { color: #FFD700; }
.health-critical { color: #FF4500; }
.trend-up { color: #FF4500; }
.trend-down { color: #00FF7F; }
.st-emotion-cache-1y4p8pa { padding-top: 1rem; }
.sidebar .sidebar-content { background-color: #262730; }
</style>
""", unsafe_allow_html=True)

# --- JavaScript pour gérer le clic ---
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    const zones = document.querySelectorAll('.zone');
    zones.forEach(zone => {
        zone.addEventListener('click', function() {
            if (this.classList.contains('grow')) { this.classList.remove('grow'); }
            else { zones.forEach(z => z.classList.remove('grow')); this.classList.add('grow'); }
        });
    });
});
</script>
""", unsafe_allow_html=True)


# --- Classe pour simuler les données d'un équipement ---
class AssetData:
    def __init__(self, name, icon, initial_health=95):
        self.name = name
        self.icon = icon
        self.health = initial_health
        self.previous_health = initial_health
        self.temp = random.uniform(75, 85)
        self.vibration = random.uniform(2.0, 4.0)
        self.status = "Opérationnel"
        self.degradation_rate = random.uniform(0.05, 0.15) # Taux de dégradation par cycle
        self.anomaly_chance = 0.02 # 2% de chance d'anomalie par cycle

    def update(self):
        self.previous_health = self.health
        
        # Simulation de la dégradation
        self.health -= self.degradation_rate
        self.health = max(0, self.health) # La santé ne peut pas être négative

        # Simulation des anomalies (pics de vibration)
        if random.random() < self.anomaly_chance:
            self.vibration += random.uniform(5, 8)
            st.toast(f"⚠️ Anomalie détectée sur {self.name}!", icon="⚠️")
        else:
            # La vibration et la température augmentent quand la santé baisse
            self.vibration = 2.0 + (100 - self.health) * 0.1 + random.uniform(-0.5, 0.5)
            self.temp = 75 + (100 - self.health) * 0.5 + random.uniform(-2, 2)

        # Mise à jour du statut
        if self.health > 80:
            self.status = "Opérationnel"
        elif self.health > 50:
            self.status = "Anomalie Détectée"
        elif self.health > 20:
            self.status = "Maintenance Requise"
        else:
            self.status = "Panne Imminente"
            self.degradation_rate = 0 # Arrête la dégradation pour éviter de passer en négatif

    def perform_maintenance(self):
        self.health = random.randint(92, 99)
        self.temp = random.uniform(75, 80)
        self.vibration = random.uniform(2.0, 3.5)
        self.status = "Opérationnel (Post-Maintenance)"
        self.degradation_rate = random.uniform(0.05, 0.15)
        st.toast(f"✅ Maintenance effectuée sur {self.name}", icon="✅")

# --- Initialisation des données dans session_state ---
if 'assets' not in st.session_state:
    st.session_state.assets = {
        "P-101": AssetData("Pompe Centrifuge P-101", "fa-oil-can", initial_health=90),
        "C-205": AssetData("Compresseur C-205", "fa-wind", initial_health=75),
        "T-310": AssetData("Turbine à Gaz T-310", "fa-fan", initial_health=60),
        "R-420": AssetData("Réacteur Chimique R-420", "fa-flask", initial_health=98),
    }

# --- Logique de l'application Streamlit ---

# Titre principal
st.markdown('<h1 class="main-title">Tableau de Bord PIONIER - Simulation Temps Réel</h1>', unsafe_allow_html=True)

# --- Panneau de Contrôle (Sidebar) ---
with st.sidebar:
    st.title("🎛️ Contrôle de la Simulation")
    
    # Sélection de l'équipement
    asset_keys = list(st.session_state.assets.keys())
    selected_asset_key = st.selectbox("Sélectionner un équipement:", asset_keys)
    
    # Bouton de maintenance
    if st.button("Déclencher la Maintenance", type="primary"):
        st.session_state.assets[selected_asset_key].perform_maintenance()
        st.rerun() # Rerun pour voir l'effet immédiatement

    st.markdown("---")
    
    # Vitesse de simulation
    simulation_speed = st.slider("Vitesse de rafraîchissement (secondes):", 1, 10, 3)

    # Afficher l'état de l'actif sélectionné
    st.markdown("### Détails de l'actif sélectionné:")
    selected_asset = st.session_state.assets[selected_asset_key]
    st.metric("Santé", f"{selected_asset.health:.1f}%")
    st.metric("Température", f"{selected_asset.temp:.1f} °C")
    st.metric("Vibration", f"{selected_asset.vibration:.2f} mm/s")
    st.write(f"**Statut:** {selected_asset.status}")


# --- Boucle de mise à jour et de rendu des zones ---
# Mettre à jour l'état de tous les actifs
for asset in st.session_state.assets.values():
    asset.update()

# Créer le HTML pour les zones
zones_html = ""
for key, asset in st.session_state.assets.items():
    
    # Déterminer la couleur et la tendance du score de santé
    if asset.health > 80:
        health_color_class = "health-good"
    elif asset.health > 50:
        health_color_class = "health-warning"
    else:
        health_color_class = "health-critical"
    
    trend_icon = ""
    if asset.health < asset.previous_health:
        trend_icon = '<i class="fas fa-arrow-trend-up trend-up"></i>'
    elif asset.health > asset.previous_health:
        trend_icon = '<i class="fas fa-arrow-trend-down trend-down"></i>'

    # Générer le HTML pour une zone
    zone_html = f"""
    <div class="zone">
        <div class="zone-header">
            <i class="fas {asset.icon}"></i>
            <h3>{asset.name}</h3>
        </div>
        <div class="zone-content">
            <div class="metric">
                <div class="metric-label">Santé IA {trend_icon}</div>
                <div class="metric-value {health_color_class}">{asset.health:.1f}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Température (°C)</div>
                <div class="metric-value">{asset.temp:.1f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Vibration (mm/s)</div>
                <div class="metric-value">{asset.vibration:.2f}</div>
            </div>
        </div>
    </div>
    """
    zones_html += zone_html

# Afficher toutes les zones
st.markdown(f'<div class="zones-container">{zones_html}</div>', unsafe_allow_html=True)

# --- Boucle pour simuler le temps réel ---
st.caption(f"Dernière mise à jour: {time.strftime('%H:%M:%S')}")
time.sleep(simulation_speed)
st.rerun()