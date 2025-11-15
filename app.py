import streamlit as st
import time
import random
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="PIONIER - Real-Time Control Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS for Professional Styling and Animations ---
st.markdown("""
<style>
/* Import Font Awesome for professional icons */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

/* General body styling */
body {
    background-color: #0E1117;
    color: #FAFAFA;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Main dashboard title */
.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #FFFFFF;
    text-align: center;
    margin-bottom: 1rem;
    text-shadow: 0 0 10px rgba(0, 150, 255, 0.5);
}

/* Styling for each asset card/zone */
.asset-card {
    background-color: #262730;
    border: 1px solid #434654;
    border-radius: 12px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    position: relative;
    overflow: hidden;
}

/* Hover effect: card grows slightly */
.asset-card:hover {
    transform: scale(1.03);
    box-shadow: 0 8px 24px rgba(0, 150, 255, 0.3);
    border-color: #00BFFF;
}

/* Class added by JS for a persistent grow effect on click */
.asset-card.grow {
    transform: scale(1.05);
    z-index: 10;
    box-shadow: 0 10px 30px rgba(0, 255, 150, 0.4);
    border-color: #00FF7F;
}

/* Asset card header (icon and name) */
.card-header {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    border-bottom: 1px solid #434654;
    padding-bottom: 10px;
}

.card-header i {
    font-size: 1.5rem;
    margin-right: 15px;
    color: #00BFFF;
}

.card-header h3 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: #FFFFFF;
}

/* Content of the card (metrics) */
.card-content {
    display: flex;
    justify-content: space-around;
    align-items: center;
    flex-wrap: wrap;
}

.metric {
    text-align: center;
    padding: 10px;
}

.metric-label {
    font-size: 0.8rem;
    color: #B0B3B8;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    margin-top: 5px;
}

/* Health score color coding */
.health-good { color: #00FF7F; }
.health-warning { color: #FFD700; }
.health-critical { color: #FF4500; }

/* Trend arrow color coding */
.trend-up { color: #FF4500; }
.trend-down { color: #00FF7F; }

/* Sidebar styling */
.sidebar .sidebar-content {
    background-color: #262730;
}
</style>
""", unsafe_allow_html=True)

# --- JavaScript for Click Interactivity ---
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.asset-card');
    cards.forEach(card => {
        card.addEventListener('click', function() {
            // If clicking an already grown card, shrink it.
            if (this.classList.contains('grow')) {
                this.classList.remove('grow');
            } else {
                // Otherwise, shrink all others and grow this one.
                cards.forEach(c => c.classList.remove('grow'));
                this.classList.add('grow');
            }
        });
    });
});
</script>
""", unsafe_allow_html=True)


# --- Class to Simulate Realistic Asset Data ---
class AssetData:
    def __init__(self, name, icon, initial_health=95):
        self.name = name
        self.icon = icon
        self.health = initial_health
        self.previous_health = initial_health
        self.temp = random.uniform(75, 85)
        self.vibration = random.uniform(2.0, 4.0)
        self.status = "Operational"
        self.degradation_rate = random.uniform(0.05, 0.15)  # Health loss per cycle
        self.anomaly_chance = 0.02  # 2% chance of an anomaly per cycle

    def update(self):
        self.previous_health = self.health
        
        # Simulate normal degradation
        self.health -= self.degradation_rate
        self.health = max(0, self.health) # Health cannot be negative

        # Simulate random anomalies (vibration spikes)
        if random.random() < self.anomaly_chance:
            self.vibration += random.uniform(5, 8)
            st.toast(f"⚠️ Anomaly detected on {self.name}!", icon="⚠️")
        else:
            # Vibration and temperature increase as health decreases
            self.vibration = 2.0 + (100 - self.health) * 0.1 + random.uniform(-0.5, 0.5)
            self.temp = 75 + (100 - self.health) * 0.5 + random.uniform(-2, 2)

        # Update status based on health
        if self.health > 80:
            self.status = "Operational"
        elif self.health > 50:
            self.status = "Anomaly Detected"
        elif self.health > 20:
            self.status = "Maintenance Required"
        else:
            self.status = "Imminent Failure"
            self.degradation_rate = 0 # Stop degradation to avoid negative values

    def perform_maintenance(self):
        self.health = random.randint(92, 99)
        self.temp = random.uniform(75, 80)
        self.vibration = random.uniform(2.0, 3.5)
        self.status = "Operational (Post-Maintenance)"
        self.degradation_rate = random.uniform(0.05, 0.15)
        st.toast(f"✅ Maintenance performed on {self.name}", icon="✅")

# --- Initialize assets in session_state for persistence ---
if 'assets' not in st.session_state:
    st.session_state.assets = {
        "P-101": AssetData("Centrifugal Pump P-101", "fa-oil-can", initial_health=90),
        "C-205": AssetData("Compressor C-205", "fa-wind", initial_health=75),
        "T-310": AssetData("Gas Turbine T-310", "fa-fan", initial_health=60),
        "R-420": AssetData("Chemical Reactor R-420", "fa-flask", initial_health=98),
    }

# --- Main Application Logic ---

# Main title
st.markdown('<h1 class="main-title">PIONIER Real-Time Dashboard Simulation</h1>', unsafe_allow_html=True)

# --- Control Panel (Sidebar) ---
with st.sidebar:
    st.title("🎛️ Simulation Control")
    
    # Asset selector
    asset_keys = list(st.session_state.assets.keys())
    selected_asset_key = st.selectbox("Select an Asset:", asset_keys)
    
    # Maintenance button
    if st.button("Trigger Maintenance", type="primary", use_container_width=True):
        st.session_state.assets[selected_asset_key].perform_maintenance()
        st.rerun() # Rerun to see the effect immediately

    st.markdown("---")
    
    # Simulation speed slider
    simulation_speed = st.slider("Refresh Speed (seconds):", 1, 10, 3)

    # Display details of the selected asset
    st.markdown("### Selected Asset Details:")
    selected_asset = st.session_state.assets[selected_asset_key]
    st.metric("AI Health", f"{selected_asset.health:.1f}%")
    st.metric("Temperature", f"{selected_asset.temp:.1f} °C")
    st.metric("Vibration", f"{selected_asset.vibration:.2f} mm/s")
    st.write(f"**Status:** {selected_asset.status}")


# --- Main Dashboard Area with Asset Cards ---

# Update the state of all assets
for asset in st.session_state.assets.values():
    asset.update()

# Create columns for a clean, responsive layout
cols = st.columns(len(st.session_state.assets))

# Iterate over columns and assets to render each card
for i, (col, (key, asset)) in enumerate(zip(cols, st.session_state.assets.items())):
    
    # Determine health score color and trend
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

    # Generate the HTML for a single, well-formed asset card
    card_html = f"""
    <div class="asset-card">
        <div class="card-header">
            <i class="fas {asset.icon}"></i>
            <h3>{asset.name}</h3>
        </div>
        <div class="card-content">
            <div class="metric">
                <div class="metric-label">AI Health {trend_icon}</div>
                <div class="metric-value {health_color_class}">{asset.health:.1f}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Temp (°C)</div>
                <div class="metric-value">{asset.temp:.1f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Vibration (mm/s)</div>
                <div class="metric-value">{asset.vibration:.2f}</div>
            </div>
        </div>
    </div>
    """
    
    # Render the card inside its respective column
    with col:
        st.markdown(card_html, unsafe_allow_html=True)

# --- Real-time Simulation Loop ---
st.caption(f"Last update: {time.strftime('%H:%M:%S')}")
time.sleep(simulation_speed)
st.rerun()
