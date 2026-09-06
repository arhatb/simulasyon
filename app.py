import streamlit as st
import time
import random
import pandas as pd
import plotly.express as px
from simulation_data import mock_weather_data
from decision_engine import evaluate_irrigation
from simulation import FarmSimulation

st.set_page_config(page_title="TerraCore Karar Sistemi", layout="wide")

# CSS Stilleri
st.markdown("""
<style>
    div[data-testid="metric-container"] { background-color: #1e1e2e; padding: 15px; border-radius: 8px; border-left: 4px solid #00f0ff; }
    .stage-badge { background-color: #b026ff; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 18px; }
    .savings-badge { background-color: #00f0ff; color: #000; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

if 'sim' not in st.session_state:
    st.session_state.sim = FarmSimulation()
    st.session_state.current_day = 0
    st.session_state.history = []
    st.session_state.auto_play = False

total_days = len(mock_weather_data)

# Uydu Haritası Üretici (NDVI değerine göre yeşillenir)
def generate_satellite_map(ndvi):
    # NDVI'a göre sahte bir 5x5 piksel tarlası oluştur
    grid = [[ndvi + random.uniform(-0.1, 0.1) for _ in range(5)] for _ in range(5)]
    fig = px.imshow(grid, color_continuous_scale='RdYlGn', zmin=0, zmax=1)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), coloraxis_showscale=False, xaxis_visible=False, yaxis_visible=False, width=200, height=200)
    return fig

# Toprak Görseli Üretici
def draw_soil_visual(moisture):
    color = "#00f0ff" if moisture >= 40 else "#ff3366"
    html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 300px;">
        <div style="font-size: 70px; margin-bottom: -15px; z-index: 2;">🌱</div>
        <div style="position: relative; width: 110px; height: 180px; background-color: #1a1614; border: 2px solid #333; border-radius: 8px 8px 30px 30px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.6);">
            <div style="position: absolute; bottom: 0; left: 0; width: 100%; height: {moisture}%; background: linear-gradient(180deg, {color} 0%, rgba(0,0,0,0) 100%); transition: height 1s ease-in-out; border-top: 2px solid {color}; opacity: 0.8;"></div>
            <div style="position: absolute; bottom: 15px; width: 100%; text-align: center; color: white; font-weight: bold; font-size: 16px;">%{moisture:.0f}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# YAN MENÜ
with st.sidebar:
    st.title("⚙️ TerraCore Kontrol")
    st.progress(st.session_state.current_day / total_days if total_days else 0)
    
    if st.session_state.current_day < total_days:
        if st.button("▶️ Otomatik İlerlet", use_container_width=True):
            st.session_state.auto_play = True
            st.rerun()
            
        if st.button("⏭️ Tek Gün İlerlet", use_container_width=True):
            st.session_state.auto_play = False
            day_data = mock_weather_data[st.session_state.current_day]
            st.session_state.sim.next_day(day_data)
            
            record = day_data.copy()
            record['soil_moisture'] = st.session_state.sim.soil_moisture
            st.session_state.history.append(record)
            st.session_state.current_day += 1
            st.rerun()
    
    st.divider()
    if st.button("🔄 Simülasyonu Sıfırla", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ANA EKRAN
st.title("🛰️ Parsel İzleme Paneli")

if st.session_state.history:
    current = st.session_state.history[-1]
    
    # TASARRUF VE EVRE BİLGİSİ (En Üstte)
    savings = st.session_state.sim.traditional_water_used - st.session_state.sim.terracore_water_used
    
    col_a, col_b = st.columns(2)
    col_a.markdown(f"🗓️ **Gün {current['day']} / {total_days}** | <span class='stage-badge'>{current['stage']}</span>", unsafe_allow_html=True)
    col_b.markdown(f"<div style='text-align: right;'><span class='savings-badge'>💧 Su Tasarrufu: {max(0, savings)} Ton/Dönüm</span></div>", unsafe_allow_html=True)
    st.write("") # Boşluk
    
    # METRİKLER
    cols = st.columns(4)
    cols[0].metric("Sıcaklık", f"{current['temp']}°C")
    cols[1].metric("Yağış", f"{current['rain']} mm")
    cols[2].metric("NDVI (Bitki Canlılığı)", f"{current['ndvi']}")
    cols[3].metric("Toprak Nemi", f"%{current['soil_moisture']:.1f}")

    st.divider()

    # ALT PANELLER: Görsel | Grafik | Karar & Uydu Haritası
    col_visual, col_chart, col_decision = st.columns([1, 2, 1.2])
    
    with col_visual:
        st.markdown("<div style='text-align:center; color:#888;'>Kök Bölgesi</div>", unsafe_allow_html=True)
        draw_soil_visual(current['soil_moisture'])

    with col_chart:
        df = pd.DataFrame(st.session_state.history)
        fig = px.line(df, x='day', y='soil_moisture', title="Toprak Nemi Trendi", markers=True)
        fig.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=40, b=0))
        fig.update_traces(line_color='#00f0ff', marker=dict(size=10, color='#b026ff'))
        fig.update_yaxes(range=[0, 100])
        fig.add_hline(y=45, line_dash="dot", line_color="#ff3366", annotation_text="Kritik Nem (Çiçeklenme)")
        st.plotly_chart(fig, use_container_width=True)

    with col_decision:
        st.subheader("🧠 Karar Motoru")
        status, amount, msg = evaluate_irrigation(current['soil_moisture'], current['et0'], current['rain'], current['stage'])
        
        if status == "SU STRESİ RİSKİ":
            st.session_state.auto_play = False 
            st.error(msg)
            if st.button("💧 Sulama Komutu Gönder", use_container_width=True, type="primary"):
                st.session_state.sim.apply_irrigation(amount)
                st.session_state.history[-1]['soil_moisture'] = st.session_state.sim.soil_moisture
                st.rerun()
        elif status == "İZLE":
            st.warning(msg)
        else:
            st.success(msg)
            
        st.write("---")
        st.markdown("<div style='text-align:center; color:#888;'>🛰️ Sentinel-2 NDVI Isı Haritası</div>", unsafe_allow_html=True)
        st.plotly_chart(generate_satellite_map(current['ndvi']), use_container_width=True, config={'displayModeBar': False})

if st.session_state.auto_play and st.session_state.current_day < total_days:
    time.sleep(3)
    day_data = mock_weather_data[st.session_state.current_day]
    st.session_state.sim.next_day(day_data)
    
    record = day_data.copy()
    record['soil_moisture'] = st.session_state.sim.soil_moisture
    st.session_state.history.append(record)
    st.session_state.current_day += 1
    st.rerun()