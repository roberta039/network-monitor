import streamlit as st
import subprocess
import platform
import ipaddress

class NetworkScanner:
    def __init__(self):
        self.nm = None
        self.devices = []
        
        # Verifică dacă nmap este disponibil
        if self._check_nmap_installed():
            try:
                import nmap
                self.nm = nmap.PortScanner()
            except ImportError:
                st.warning("python-nmap nu este instalat. Folosește pip install python-nmap")
            except Exception as e:
                st.warning(f"Eroare la inițializarea nmap: {e}")
        else:
            st.warning("nmap nu este instalat pe sistem. Funcționalitățile de scanare vor fi limitate.")
    
    def _check_nmap_installed(self):
        """Verifică dacă nmap este instalat în sistem"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["where", "nmap"], capture_output=True, text=True)
            else:
                result = subprocess.run(["which", "nmap"], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_local_network(self) -> str:
        """Detectează rețeaua locală"""
        try:
            # Încearcă să detecteze automat rețeaua
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Creează o adresă de rețea bazată pe IP-ul local
            ip_obj = ipaddress.IPv4Address(local_ip)
            network = ipaddress.IPv4Network(f"{ip_obj}/24", strict=False)
            return str(network)
        except:
            # Rețea implicită dacă detectarea eșuează
            return "192.168.1.0/24"
    
    def scan_network(self, network_range: str):
        """Scanează rețeaua - versiunea simplificată fără nmap"""
        if self.nm:
            # Folosește nmap dacă este disponibil
            try:
                self.nm.scan(hosts=network_range, arguments='-sn')
                self.devices = []
                for host in self.nm.all_hosts():
                    device_info = {
                        'ip': host,
                        'mac': self.nm[host]['addresses'].get('mac', 'N/A'),
                        'hostname': self.nm[host].hostname(),
                        'status': 'up'
                    }
                    self.devices.append(device_info)
                return self.devices
            except Exception as e:
                st.error(f"Eroare scanare nmap: {e}")
        
        # Fallback: returnează dispozitive mock pentru demo
        st.info("Mod demo: afișez dispozitive simulate (nmap nu este disponibil)")
        self.devices = [
            {'ip': '192.168.1.1', 'mac': '00:11:22:33:44:55', 'hostname': 'router', 'status': 'up'},
            {'ip': '192.168.1.100', 'mac': 'AA:BB:CC:DD:EE:FF', 'hostname': 'laptop', 'status': 'up'},
            {'ip': '192.168.1.101', 'mac': '11:22:33:44:55:66', 'hostname': 'phone', 'status': 'up'},
        ]
        return self.devices
