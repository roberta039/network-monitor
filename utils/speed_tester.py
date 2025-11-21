import streamlit as st
import time
from collections import deque
import threading
import random

class InternetSpeedTester:
    def __init__(self, max_history=10):
        self.speed_data = deque(maxlen=max_history)
        self.is_testing = False
        self.test_thread = None
        self.st = None
        
        # Încearcă să inițializeze speedtest, dar gestionează erorile
        try:
            import speedtest
            self.st = speedtest.Speedtest()
            self.speedtest_available = True
        except Exception as e:
            st.warning(f"⚠ Speedtest nu este disponibil: {e}")
            self.speedtest_available = False
    
    def run_speed_test(self):
        """Execută test de viteză internet cu fallback la date simulate"""
        if not self.speedtest_available:
            return self._run_simulated_test()
        
        try:
            self.is_testing = True
            
            # Obține serverele
            st.info("🔍 Se caută servere optimale...")
            self.st.get_best_server()
            
            # Test download
            st.info("📥 Se măsoară viteza de download...")
            download_speed = self.st.download() / 1_000_000  # Convert to Mbps
            
            # Test upload
            st.info("📤 Se măsoară viteza de upload...")
            upload_speed = self.st.upload() / 1_000_000  # Convert to Mbps
            
            # Obține ping
            ping = self.st.results.ping
            
            result = {
                'timestamp': time.time(),
                'download': round(download_speed, 2),
                'upload': round(upload_speed, 2),
                'ping': round(ping, 2),
                'server': self.st.results.server.get('name', 'N/A'),
                'real_test': True
            }
            
            self.speed_data.append(result)
            self.is_testing = False
            return result
            
        except Exception as e:
            st.error(f"❌ Eroare test viteză: {e}")
            st.info("🔄 Se folosesc date simulate...")
            self.is_testing = False
            return self._run_simulated_test()
    
    def _run_simulated_test(self):
        """Rulează un test simulat pentru medii restrictive"""
        self.is_testing = True
        
        # Simulează progresul testului
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(5):
            progress = (i + 1) * 20
            progress_bar.progress(progress)
            if i == 0:
                status_text.text("🔍 Se caută servere...")
            elif i == 1:
                status_text.text("📥 Se testează download...")
            elif i == 2:
                status_text.text("📤 Se testează upload...")
            elif i == 3:
                status_text.text("📊 Se procesează rezultate...")
            time.sleep(1)
        
        progress_bar.progress(100)
        status_text.text("✅ Test complet!")
        
        # Generează date simulate realiste
        result = {
            'timestamp': time.time(),
            'download': round(random.uniform(50, 200), 2),  # Mbps
            'upload': round(random.uniform(10, 50), 2),     # Mbps
            'ping': round(random.uniform(10, 50), 2),       # ms
            'server': 'Server Simulat',
            'real_test': False
        }
        
        self.speed_data.append(result)
        self.is_testing = False
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return result
    
    def run_test_in_thread(self):
        """Rulează testul într-un thread separat"""
        if self.is_testing:
            return
        
        self.test_thread = threading.Thread(target=self.run_speed_test)
        self.test_thread.daemon = True
        self.test_thread.start()
    
    def get_speed_data(self):
        """Returnează datele de viteză"""
        return list(self.speed_data)
    
    def get_latest_speed(self):
        """Returnează cel mai recent test"""
        if self.speed_data:
            return self.speed_data[-1]
        return None
    
    def clear_history(self):
        """Șterge istoricul"""
        self.speed_data.clear()
    
    def is_available(self):
        """Verifică dacă speedtest este disponibil"""
        return self.speedtest_available
