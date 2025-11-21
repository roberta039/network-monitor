import nmap
import socket
import netifaces
from typing import List, Dict
import threading
import time

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.devices = []
        
    def get_local_network(self) -> str:
        """Detectează rețeaua locală"""
        try:
            gateways = netifaces.gateways()
            default_gateway = gateways['default'][netifaces.AF_INET][0]
            interface = gateways['default'][netifaces.AF_INET][1]
            
            # Obține adresa IP a interfeței
            addrs = netifaces.ifaddresses(interface)
            ip_info = addrs[netifaces.AF_INET][0]
            ip = ip_info['addr']
            netmask = ip_info['netmask']
            
            # Calculează rețeaua CIDR
            network = self.calculate_network(ip, netmask)
            return network
        except:
            return "192.168.1.0/24"  # Fallback
    
    def calculate_network(self, ip: str, netmask: str) -> str:
        """Calculează rețeaua în format CIDR"""
        ip_parts = list(map(int, ip.split('.')))
        mask_parts = list(map(int, netmask.split('.')))
        
        network_parts = []
        for i in range(4):
            network_parts.append(str(ip_parts[i] & mask_parts[i]))
        
        # Calculează prefixul CIDR
        cidr = sum(bin(int(x)).count('1') for x in netmask.split('.'))
        
        return f"{'.'.join(network_parts)}/{cidr}"
    
    def scan_network(self) -> List[Dict]:
        """Scanează toate dispozitivele din rețea"""
        network = self.get_local_network()
        print(f"Scanning network: {network}")
        
        try:
            # Scanare cu nmap
            self.nm.scan(hosts=network, arguments='-sn -T5')
            devices = []
            
            for host in self.nm.all_hosts():
                hostname = ""
                try:
                    hostname = socket.getfqdn(host)
                except:
                    pass
                
                device_info = {
                    'ip': host,
                    'hostname': hostname if hostname else 'Unknown',
                    'mac': self.nm[host]['addresses'].get('mac', 'Unknown'),
                    'vendor': self.nm[host].get('vendor', {}).get(self.nm[host]['addresses'].get('mac', ''), 'Unknown'),
                    'status': 'up'
                }
                devices.append(device_info)
            
            self.devices = devices
            return devices
            
        except Exception as e:
            print(f"Scan error: {e}")
            return []
