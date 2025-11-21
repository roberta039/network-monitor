import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
from datetime import datetime
import threading

from utils.network_scanner import NetworkScanner
from utils.ping_monitor import PingMonitor
from utils.speed_tester import InternetSpeedTester

# Configurare pagină
st.set_page_config(
    page_title="Network Monitor",
    page_icon="🌐",
    layout="wide"
)

# Inițializare clase
@st.cache_resource
def get_scanner():
    return NetworkScanner()

@st.cache_resource
def get_ping_monitor():
    return PingMonitor()

@st.cache_resource
def get_speed_tester():
    return InternetSpeedTester()

def main():
    st.title("🌐 Network Monitor - Monitorizare Rețea Locală și Internet")
    
    # Inițializare
    scanner = get_scanner()
    ping_monitor = get_ping_monitor()
    speed_tester = get_speed_tester()
    
    # Sidebar
    st.sidebar.header("Configurare")
    auto_refresh = st.sidebar.checkbox("Auto-refresh dispozitive", value=True)
    refresh_interval = st.sidebar.slider("Interval refresh (secunde)", 30, 300, 60)
    
    # Butoane control
    col1, col2, col3 = st.sidebar.columns(3)
    
    with col1:
        if st.button("Scan Now"):
            st.rerun()
    
    with col2:
        if st.button("Start Monitor"):
            devices = scanner.devices
            ping_monitor.start_monitoring(devices)
            speed_tester.start_continuous_test(interval=60)
    
    with col3:
        if st.button("Stop Monitor"):
            ping_monitor.stop_monitoring()
            speed_tester.stop_continuous_test()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Dispozitive Rețea", "📊 Monitor Rețea", "🌐 Viteza Internet"])
    
    with tab1:
        st.header("Dispozitive din Rețea")
        
        # Scanare dispozitive
        with st.spinner("Scanare rețea..."):
            # Obține rețeaua locală automat
            network_range = scanner.get_local_network()
    
            # Afișează rețeaua care va fi scanată
            st.info(f"🔍 Scanare rețea: {network_range}")
    
            # Execută scanarea
            devices = scanner.scan_network(network_range)
        
        if devices:
            # Creează DataFrame pentru afișare
            df_data = []
            for device in devices:
                df_data.append({
                    'IP Address': device['ip'],
                    'Hostname': device['hostname'],
                    'MAC Address': device['mac'],
                    'Vendor': device['vendor'],
                    'Status': device['status']
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Statistici
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Dispozitive", len(devices))
            with col2:
                up_devices = len([d for d in devices if d['status'] == 'up'])
                st.metric("Dispozitive Active", up_devices)
        else:
            st.warning("Nu s-au găsit dispozitive în rețea")
    
    with tab2:
        st.header("Monitorizare Rețea în Timp Real")
        
        if not ping_monitor.ping_data:
            st.info("Porniți monitorizarea din sidebar pentru a vedea datele")
        else:
            # Creează graficul pentru dispozitive
            fig = go.Figure()
            
            # Culori pentru status
            status_colors = {
                'excellent': '#00ff00',  # Verde - 1000 Mbps
                'good': '#ffff00',       # Galben - 100 Mbps  
                'fair': '#ffa500',       # Portocaliu - 10 Mbps
                'slow': '#ff0000',       # Roșu - Probleme
                'down': '#8b0000',       # Roșu închis - Down
                'unknown': '#808080'     # Gri - Unknown
            }
            
            # Adaugă dispozitivele pe grafic
            y_positions = {}
            current_y = 0
            
            for ip, data in ping_monitor.ping_data.items():
                hostname = data['hostname']
                y_positions[ip] = current_y
                
                # Adaugă hostname în stânga
                fig.add_trace(go.Scatter(
                    x=[-10],
                    y=[current_y],
                    mode='text',
                    text=[f"<b>{hostname}</b><br>{ip}"],
                    textposition="middle right",
                    showlegend=False,
                    hoverinfo='none'
                ))
                
                # Adaugă linia punctată spre dreapta
                if data['history']:
                    latest = list(data['history'])[-1]
                    color = status_colors.get(data['status'], '#808080')
                    
                    # Linie principală
                    fig.add_trace(go.Scatter(
                        x=[0, 100],
                        y=[current_y, current_y],
                        mode='lines',
                        line=dict(dash='dot', color=color, width=3),
                        showlegend=False,
                        hoverinfo='none'
                    ))
                    
                    # Marker cu viteza
                    speed_text = self.get_speed_text(data['status'])
                    fig.add_trace(go.Scatter(
                        x=[100],
                        y=[current_y],
                        mode='markers+text',
                        marker=dict(size=15, color=color),
                        text=[speed_text],
                        textposition="middle right",
                        showlegend=False,
                        name=f"{hostname} - {speed_text}"
                    ))
                
                current_y += 1
            
            # Configurează layout
            fig.update_layout(
                title="Monitorizare Dispozitive Rețea",
                xaxis=dict(
                    range=[-50, 150],
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    title=""
                ),
                yaxis=dict(
                    range=[-1, current_y],
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    title=""
                ),
                plot_bgcolor='white',
                height=400 + (len(ping_monitor.ping_data) * 30),
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabel cu status curent
            st.subheader("Status Curent Dispozitive")
            status_data = []
            for ip, data in ping_monitor.ping_data.items():
                if data['history']:
                    latest = list(data['history'])[-1]
                    status_data.append({
                        'Hostname': data['hostname'],
                        'IP': ip,
                        'Status': data['status'].upper(),
                        'Response Time': f"{latest['response_time']} ms" if latest['response_time'] else 'N/A',
                        'Packet Loss': 'DA' if latest['packet_loss'] else 'NU',
                        'Viteza Estimata': self.get_speed_text(data['status'])
                    })
            
            if status_data:
                status_df = pd.DataFrame(status_data)
                st.dataframe(status_df, use_container_width=True)
    
    with tab3:
        st.header("Viteza Internet în Timp Real")
        
        if not speed_tester.speed_data:
            st.info("Porniți monitorizarea pentru a vedea viteza internetului")
        else:
            # Creează grafice pentru viteza internet
            speed_list = list(speed_tester.speed_data)
            
            if speed_list:
                # DataFrame pentru date
                df_speed = pd.DataFrame(speed_list)
                df_speed['timestamp'] = pd.to_datetime(df_speed['timestamp'], unit='s')
                df_speed = df_speed.sort_values('timestamp')
                
                # Grafic viteze
                fig_speed = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Viteza Download/Upload (Mbps)', 'Ping (ms)'),
                    vertical_spacing=0.1
                )
                
                # Download/Upload
                fig_speed.add_trace(
                    go.Scatter(x=df_speed['timestamp'], y=df_speed['download'], 
                              name='Download', line=dict(color='blue')),
                    row=1, col=1
                )
                fig_speed.add_trace(
                    go.Scatter(x=df_speed['timestamp'], y=df_speed['upload'], 
                              name='Upload', line=dict(color='green')),
                    row=1, col=1
                )
                
                # Ping
                fig_speed.add_trace(
                    go.Scatter(x=df_speed['timestamp'], y=df_speed['ping'], 
                              name='Ping', line=dict(color='red')),
                    row=2, col=1
                )
                
                fig_speed.update_layout(height=600, showlegend=True)
                st.plotly_chart(fig_speed, use_container_width=True)
                
                # Ultimele valori
                latest = speed_list[-1]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Download", f"{latest['download']:.2f} Mbps")
                with col2:
                    st.metric("Upload", f"{latest['upload']:.2f} Mbps")
                with col3:
                    st.metric("Ping", f"{latest['ping']:.2f} ms")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

def get_speed_text(status):
    """Returnează textul pentru viteza estimată"""
    speed_map = {
        'excellent': '1000 Mbps',
        'good': '100 Mbps', 
        'fair': '10 Mbps',
        'slow': '<10 Mbps',
        'down': 'DOWN',
        'unknown': 'UNKNOWN'
    }
    return speed_map.get(status, 'UNKNOWN')

if __name__ == "__main__":
    main()
