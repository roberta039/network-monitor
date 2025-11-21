import speedtest
import time
from collections import deque
import threading

class InternetSpeedTester:
    def __init__(self, max_history=50):
        self.speed_data = deque(maxlen=max_history)
        self.is_testing = False
        self.test_thread = None
        self.st = speedtest.Speedtest()
        
    def run_speed_test(self):
        """Execută test de viteză internet"""
        try:
            # Obține serverul cel mai apropiat
            self.st.get_best_server()
            
            # Testează download speed
            download_speed = self.st.download() / 1_000_000  # Convert to Mbps
            
            # Testează upload speed
            upload_speed = self.st.upload() / 1_000_000  # Convert to Mbps
            
            # Obține ping
            ping = self.st.results.ping
            
            return {
                'timestamp': time.time(),
                'download': download_speed,
                'upload': upload_speed,
                'ping': ping
            }
        except Exception as e:
            print(f"Speed test error: {e}")
            return None
    
    def continuous_testing(self, interval=60):
        """Testează continuu viteza internetului"""
        while self.is_testing:
            result = self.run_speed_test()
            if result:
                self.speed_data.append(result)
            
            # Așteaptă intervalul specificat
            for _ in range(interval):
                if not self.is_testing:
                    break
                time.sleep(1)
    
    def start_continuous_test(self, interval=60):
        """Pornește testarea continuă"""
        self.stop_continuous_test()
        self.is_testing = True
        self.test_thread = threading.Thread(
            target=self.continuous_testing,
            args=(interval,)
        )
        self.test_thread.daemon = True
        self.test_thread.start()
    
    def stop_continuous_test(self):
        """Oprește testarea continuă"""
        self.is_testing = False
        if self.test_thread:
            self.test_thread.join(timeout=1)
