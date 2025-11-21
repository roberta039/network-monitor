import subprocess
import re
import time
from typing import Dict, List
import threading
from collections import deque
import platform

class PingMonitor:
    def __init__(self, max_history=100):
        self.ping_data = {}
        self.max_history = max_history
        self.is_monitoring = False
        self.threads = []
        
    def ping_host(self, host: str, hostname: str):
        """Monitorizează un host cu ping continuu"""
        history = deque(maxlen=self.max_history)
        self.ping_data[host] = {
            'history': history,
            'hostname': hostname,
            'status': 'unknown'
        }
        
        while self.is_monitoring:
            try:
                # Parametrii ping în funcție de OS
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                count_param = '1'
                
                # Execută ping
                process = subprocess.Popen(
                    ['ping', param, count_param, host],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    # Extrage timpul de răspuns
                    time_match = re.search(r'time=([\d.]+)\s*ms', stdout)
                    if time_match:
                        response_time = float(time_match.group(1))
                        status = self.determine_speed_status(response_time)
                    else:
                        response_time = 1.0
                        status = 'slow'
                    
                    self.ping_data[host]['status'] = status
                    history.append({
                        'timestamp': time.time(),
                        'response_time': response_time,
                        'status': status,
                        'packet_loss': False
                    })
                else:
                    # Ping failed - packet loss
                    self.ping_data[host]['status'] = 'down'
                    history.append({
                        'timestamp': time.time(),
                        'response_time': None,
                        'status': 'down',
                        'packet_loss': True
                    })
                    
            except Exception as e:
                print(f"Ping error for {host}: {e}")
                history.append({
                    'timestamp': time.time(),
                    'response_time': None,
                    'status': 'down',
                    'packet_loss': True
                })
            
            time.sleep(2)  # Ping la fiecare 2 secunde
    
    def determine_speed_status(self, response_time: float) -> str:
        """Determină statusul vitezei bazat pe timpul de răspuns"""
        if response_time < 10:
            return 'excellent'  # 1000 Mbps
        elif response_time < 50:
            return 'good'       # 100 Mbps
        elif response_time < 100:
            return 'fair'       # 10 Mbps
        else:
            return 'slow'       # Probleme
    
    def start_monitoring(self, devices: List[Dict]):
        """Pornește monitorizarea pentru toate dispozitivele"""
        self.stop_monitoring()
        self.is_monitoring = True
        
        for device in devices:
            if device['ip']:
                thread = threading.Thread(
                    target=self.ping_host,
                    args=(device['ip'], device['hostname'])
                )
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
    
    def stop_monitoring(self):
        """Oprește monitorizarea"""
        self.is_monitoring = False
        for thread in self.threads:
            thread.join(timeout=1)
        self.threads = []
