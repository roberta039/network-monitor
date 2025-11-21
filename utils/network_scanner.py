import streamlit as st
import subprocess
import platform
import ipaddress
import socket
from typing import List, Dict, Optional

class NetworkScanner:
    def __init__(self):
        self.nm = None
        self.devices = []
        
        # Verifică dacă nmap este disponibil
        if self._check_nmap_installed():
            try:
                import nmap
                self.nm = nmap.PortScanner()
                st.success("✓ Nmap este disponibil - scanare completă activată")
            except ImportError:
                st.warning("⚠ python-nmap nu este instalat. Folosește `pip install python-nmap` pentru funcționalități complete")
            except Exception as e:
                st.warning(f"⚠ Eroare la inițializarea nmap: {e}")
        else:
            st.warning("⚠ Nmap nu este instalat pe sistem. Funcționalitățile de scanare vor fi limitate (mod demo).")
    
    def _check_nmap_installed(self) -> bool:
        """Verifică dacă nmap este instalat în sistem"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["where", "nmap"], capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run(["which", "nmap"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            st.error("⏰ Timeout la verificarea nmap")
            return False
        except Exception:
            return False
    
    def get_local_network(self) -> str:
        """Detectează rețeaua locală"""
        try:
            # Obține IP-ul local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Creează o adresă de rețea bazată pe IP-ul local
            ip_obj = ipaddress.IPv4Address(local_ip)
            network = ipaddress.IPv4Network(f"{ip_obj}/24", strict=False)
            st.success(f"✓ Rețea detectată automat: {network}")
            return str(network)
        except Exception as e:
            st.warning(f"⚠ Nu s-a putut detecta rețeaua automat: {e}")
            # Rețea implicită dacă detectarea eșuează
            return "192.168.1.0/24"
    
    def scan_network(self, network_range: str) -> List[Dict]:
        """Scanează rețeaua - folosește nmap dacă disponibil, altwise fallback la metoda simplă"""
        self.devices = []
        
        if self.nm:
            # Folosește nmap dacă este disponibil
            return self._scan_with_nmap(network_range)
        else:
            # Fallback la metoda simplă
            return self._scan_simple_fallback(network_range)
    
    def _scan_with_nmap(self, network_range: str) -> List[Dict]:
        """Scanează rețeaua folosind nmap"""
        try:
            st.info(f"🔍 Scanare rețea {network_range} cu nmap...")
            
            # Scanare ping (host discovery)
            self.nm.scan(hosts=network_range, arguments='-sn')
            
            self.devices = []
            for host in self.nm.all_hosts():
                device_info = {
                    'ip': host,
                    'mac': self.nm[host]['addresses'].get('mac', 'N/A'),
                    'hostname': self.nm[host].hostname() or 'N/A',
                    'status': 'up',
                    'vendor': self.nm[host].get('vendor', {}).get(self.nm[host]['addresses'].get('mac', ''), 'N/A')
                }
                self.devices.append(device_info)
            
            st.success(f"✓ Scanare completă: {len(self.devices)} dispozitive găsite")
            return self.devices
            
        except Exception as e:
            st.error(f"❌ Eroare scanare nmap: {e}")
            return self._scan_simple_fallback(network_range)
    
    def _scan_simple_fallback(self, network_range: str) -> List[Dict]:
        """Metodă fallback simplă pentru când nmap nu este disponibil"""
        st.info("🎭 Mod demo: afișez dispozitive simulate (nmap nu este disponibil)")
        
        # Parsează rețeaua pentru a genera IP-uri relevante
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
            base_ip = str(network.network_address).rsplit('.', 1)[0]
            
            # Dispozitive simulate bazate pe rețeaua actuală
            self.devices = [
                {
                    'ip': f'{base_ip}.1', 
                    'mac': '00:11:22:33:44:55', 
                    'hostname': 'router', 
                    'status': 'up',
                    'vendor': 'Router Vendor'
                },
                {
                    'ip': f'{base_ip}.100', 
                    'mac': 'AA:BB:CC:DD:EE:FF', 
                    'hostname': 'laptop-local', 
                    'status': 'up',
                    'vendor': 'Laptop Manufacturer'
                },
                {
                    'ip': f'{base_ip}.101', 
                    'mac': '11:22:33:44:55:66', 
                    'hostname': 'phone-wifi', 
                    'status': 'up',
                    'vendor': 'Phone Brand'
                },
                {
                    'ip': f'{base_ip}.50', 
                    'mac': '22:33:44:55:66:77', 
                    'hostname': 'smart-tv', 
                    'status': 'up',
                    'vendor': 'TV Manufacturer'
                },
            ]
        except:
            # Dispozitive default dacă parsing-ul eșuează
            self.devices = [
                {'ip': '192.168.1.1', 'mac': '00:11:22:33:44:55', 'hostname': 'router', 'status': 'up', 'vendor': 'Router Vendor'},
                {'ip': '192.168.1.100', 'mac': 'AA:BB:CC:DD:EE:FF', 'hostname': 'laptop', 'status': 'up', 'vendor': 'Laptop Brand'},
                {'ip': '192.168.1.101', 'mac': '11:22:33:44:55:66', 'hostname': 'phone', 'status': 'up', 'vendor': 'Phone Maker'},
            ]
        
        st.success(f"✓ Mod demo: {len(self.devices)} dispozitive simulate")
        return self.devices
    
    def get_device_services(self, ip: str) -> Dict:
        """Obține serviciile disponibile pe un dispozitiv"""
        if not self.nm:
            return {'http': 'Simulated', 'ssh': 'Simulated'}
        
        try:
            # Scanare porturi comune
            self.nm.scan(ip, '21-443')
            services = {}
            
            for proto in self.nm[ip].all_protocols():
                ports = self.nm[ip][proto].keys()
                for port in ports:
                    service_name = self.nm[ip][proto][port]['name']
                    services[port] = service_name
            
            return services
        except:
            return {'http': 'N/A', 'ssh': 'N/A'}
    
    def is_nmap_available(self) -> bool:
        """Verifică dacă nmap este disponibil"""
        return self.nm is not None
    
    def get_scan_method(self) -> str:
        """Returnează metoda de scanare curentă"""
        return "NMAP" if self.nm else "DEMO"

# Testare locală
if __name__ == "__main__":
    scanner = NetworkScanner()
    print(f"Metoda scanare: {scanner.get_scan_method()}")
    
    network = scanner.get_local_network()
    print(f"Rețea detectată: {network}")
    
    devices = scanner.scan_network(network)
    print(f"Dispozitive găsite: {len(devices)}")
    
    for device in devices:
        print(f" - {device['ip']} ({device['hostname']}) - {device['mac']}")
