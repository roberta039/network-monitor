class NetworkMonitor {
    constructor() {
        this.isMonitoring = false;
        this.monitorInterval = null;
        this.speedData = {
            labels: [],
            local: [],
            download: [],
            upload: [],
            ping: []
        };
        
        this.discoveredDevices = [];
        this.currentSort = { field: 'hostname', direction: 'asc' };
        
        this.initializeCharts();
        this.setupEventListeners();
    }

    initializeCharts() {
        // Main speed chart
        this.speedChart = new Chart(document.getElementById('speedChart'), {
            type: 'line',
            data: {
                labels: this.speedData.labels,
                datasets: [
                    {
                        label: 'Local Speed (Mbps)',
                        data: this.speedData.local,
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Download (Mbps)',
                        data: this.speedData.download,
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Upload (Mbps)',
                        data: this.speedData.upload,
                        borderColor: '#FF9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Network Speed - Live Monitoring'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Mbps'
                        }
                    }
                }
            }
        });

        // Comparison chart
        this.comparisonChart = new Chart(document.getElementById('comparisonChart'), {
            type: 'bar',
            data: {
                labels: ['Local', 'Download', 'Upload'],
                datasets: [{
                    label: 'Current Speeds (Mbps)',
                    data: [0, 0, 0],
                    backgroundColor: [
                        '#4CAF50',
                        '#2196F3',
                        '#FF9800'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Speed Comparison'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    setupEventListeners() {
        document.getElementById('startMonitor').addEventListener('click', () => {
            this.toggleMonitoring();
        });

        document.getElementById('speedTest').addEventListener('click', () => {
            this.runSpeedTest();
        });

        document.getElementById('scanNetwork').addEventListener('click', () => {
            this.scanNetwork();
        });

        document.getElementById('detectConnection').addEventListener('click', () => {
            this.detectConnectionType();
        });

        document.getElementById('refreshDevices').addEventListener('click', () => {
            this.scanNetwork();
        });

        document.getElementById('exportDevices').addEventListener('click', () => {
            this.exportToCSV();
        });

        // Table sorting
        document.querySelectorAll('#devicesTable th[data-sort]').forEach(th => {
            th.addEventListener('click', () => {
                this.sortTable(th.dataset.sort);
            });
        });
    }

    toggleMonitoring() {
        if (this.isMonitoring) {
            this.stopMonitoring();
        } else {
            this.startMonitoring();
        }
    }

    startMonitoring() {
        this.isMonitoring = true;
        document.getElementById('startMonitor').textContent = 'Stop Monitoring';
        document.getElementById('startMonitor').classList.add('btn-danger');
        
        this.log('🚀 Live monitoring started...');
        
        this.monitorInterval = setInterval(() => {
            this.updateLocalSpeed();
            this.updateCharts();
        }, 3000);
    }

    stopMonitoring() {
        this.isMonitoring = false;
        document.getElementById('startMonitor').textContent = 'Start Monitoring';
        document.getElementById('startMonitor').classList.remove('btn-danger');
        
        this.log('⏹️ Monitoring stopped');
        
        if (this.monitorInterval) {
            clearInterval(this.monitorInterval);
        }
    }

    async updateLocalSpeed() {
        try {
            // Simulate local speed measurement
            const localSpeed = Math.random() * 1000;
            const timestamp = new Date().toLocaleTimeString();
            
            document.getElementById('localSpeed').textContent = `${localSpeed.toFixed(2)} Mbps`;
            
            // Update chart data
            this.speedData.labels.push(timestamp);
            this.speedData.local.push(localSpeed);
            
            // Keep only last 20 data points
            if (this.speedData.labels.length > 20) {
                this.speedData.labels.shift();
                this.speedData.local.shift();
                this.speedData.download.shift();
                this.speedData.upload.shift();
                this.speedData.ping.shift();
            }
            
        } catch (error) {
            this.log(`❌ Error measuring local speed: ${error.message}`);
        }
    }

    async scanNetwork() {
        try {
            this.log('🔍 Scanning network for devices...');
            
            // Show loading state
            document.getElementById('devicesTableBody').innerHTML = 
                '<tr><td colspan="9" class="no-devices">Scanning network... Please wait.</td></tr>';
            
            const devices = await this.performNetworkScan();
            this.discoveredDevices = devices;
            
            this.displayDevicesTable(devices);
            this.updateDeviceCount(devices.length);
            this.log(`✅ Found ${devices.length} devices on the network`);
            
        } catch (error) {
            this.log(`❌ Network scan failed: ${error.message}`);
            document.getElementById('devicesTableBody').innerHTML = 
                '<tr><td colspan="9" class="no-devices">Scan failed. Please try again.</td></tr>';
        }
    }

    async performNetworkScan() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const deviceTypes = ['computer', 'phone', 'router', 'tablet', 'iot', 'printer'];
                const manufacturers = ['Apple', 'Samsung', 'Dell', 'HP', 'TP-Link', 'Netgear', 'Cisco', 'Asus'];
                const osTypes = ['Windows 11', 'macOS', 'Linux', 'iOS', 'Android', 'RouterOS'];
                
                const devices = [];
                const deviceCount = Math.floor(Math.random() * 15) + 8; // 8-23 devices
                
                for (let i = 0; i < deviceCount; i++) {
                    const deviceType = deviceTypes[Math.floor(Math.random() * deviceTypes.length)];
                    const manufacturer = manufacturers[Math.floor(Math.random() * manufacturers.length)];
                    const os = osTypes[Math.floor(Math.random() * osTypes.length)];
                    const isOnline = Math.random() > 0.1; // 90% chance online
                    
                    devices.push({
                        ip: `192.168.1.${Math.floor(Math.random() * 254) + 1}`,
                        mac: this.generateRandomMAC(),
                        hostname: this.generateHostname(manufacturer, deviceType),
                        manufacturer: manufacturer,
                        type: deviceType,
                        os: os,
                        responseTime: Math.floor(Math.random() * 100) + 1,
                        lastSeen: new Date(),
                        status: isOnline ? 'online' : 'offline'
                    });
                }
                
                // Add router/gateway
                devices.push({
                    ip: '192.168.1.1',
                    mac: this.generateRandomMAC(),
                    hostname: 'router.local',
                    manufacturer: 'TP-Link',
                    type: 'router',
                    os: 'RouterOS',
                    responseTime: 1,
                    lastSeen: new Date(),
                    status: 'online'
                });
                
                resolve(devices);
            }, 2000);
        });
    }

    generateRandomMAC() {
        const hex = '0123456789ABCDEF';
        let mac = '';
        for (let i = 0; i < 6; i++) {
            mac += hex[Math.floor(Math.random() * 16)];
            mac += hex[Math.floor(Math.random() * 16)];
            if (i < 5) mac += ':';
        }
        return mac;
    }

    generateHostname(manufacturer, type) {
        const suffixes = {
            computer: ['PC', 'Laptop', 'Workstation', 'Desktop'],
            phone: ['Phone', 'Mobile', 'Smartphone'],
            router: ['Router', 'Gateway', 'Access-Point'],
            tablet: ['Tablet', 'Pad'],
            iot: ['Smart-TV', 'Camera', 'Speaker', 'Thermostat'],
            printer: ['Printer', 'Multifunction']
        };
        
        const suffix = suffixes[type][Math.floor(Math.random() * suffixes[type].length)];
        const randomNum = Math.floor(Math.random() * 100);
        return `${manufacturer}-${suffix}-${randomNum}`.toLowerCase();
    }

    displayDevicesTable(devices) {
        const tbody = document.getElementById('devicesTableBody');
        
        if (devices.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="no-devices">No devices found on the network.</td></tr>';
            return;
        }
        
        // Sort devices before displaying
        const sortedDevices = this.sortDevices(devices, this.currentSort.field, this.currentSort.direction);
        
        tbody.innerHTML = sortedDevices.map(device => `
            <tr class="type-${device.type}">
                <td><strong>${device.hostname}</strong></td>
                <td>${device.ip}</td>
                <td><span class="mac-address">${device.mac}</span></td>
                <td>${this.capitalizeFirstLetter(device.type)}</td>
                <td>${device.manufacturer}</td>
                <td>${device.os}</td>
                <td>${device.responseTime} ms</td>
                <td>${device.lastSeen.toLocaleTimeString()}</td>
                <td><span class="status-${device.status}">${device.status.toUpperCase()}</span></td>
            </tr>
        `).join('');
    }

    sortTable(field) {
        // Toggle sort direction if same field
        if (this.currentSort.field === field) {
            this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.field = field;
            this.currentSort.direction = 'asc';
        }
        
        // Update table headers
        document.querySelectorAll('#devicesTable th').forEach(th => {
            th.classList.remove('sorted-asc', 'sorted-desc');
        });
        
        const currentTh = document.querySelector(`#devicesTable th[data-sort="${field}"]`);
        currentTh.classList.add(`sorted-${this.currentSort.direction}`);
        
        // Re-display sorted devices
        this.displayDevicesTable(this.discoveredDevices);
    }

    sortDevices(devices, field, direction) {
        return [...devices].sort((a, b) => {
            let aValue = a[field];
            let bValue = b[field];
            
            // Handle special cases
            if (field === 'responseTime') {
                aValue = parseInt(aValue);
                bValue = parseInt(bValue);
            }
            
            if (field === 'lastSeen') {
                aValue = new Date(aValue);
                bValue = new Date(bValue);
            }
            
            if (aValue < bValue) return direction === 'asc' ? -1 : 1;
            if (aValue > bValue) return direction === 'asc' ? 1 : -1;
            return 0;
        });
    }

    updateDeviceCount(count) {
        document.getElementById('deviceCount').textContent = `${count} device${count !== 1 ? 's' : ''} found`;
    }

    exportToCSV() {
        if (this.discoveredDevices.length === 0) {
            this.log('❌ No devices to export');
            return;
        }

        const headers = ['Hostname', 'IP Address', 'MAC Address', 'Device Type', 'Manufacturer', 'OS/System', 'Response Time (ms)', 'Last Seen', 'Status'];
        const csvData = [
            headers.join(','),
            ...this.discoveredDevices.map(device => [
                device.hostname,
                device.ip,
                device.mac,
                device.type,
                device.manufacturer,
                device.os,
                device.responseTime,
                device.lastSeen.toLocaleString(),
                device.status
            ].join(','))
        ].join('\n');

        const blob = new Blob([csvData], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `network-devices-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        this.log('📊 Devices exported to CSV file');
    }

    // ... rest of the methods remain the same (runSpeedTest, detectConnectionType, etc.)
    async runSpeedTest() {
        try {
            this.log('🧪 Running internet speed test...');
            
            const speedTest = await this.performSpeedTest();
            
            document.getElementById('downloadSpeed').textContent = `${speedTest.download} Mbps`;
            document.getElementById('uploadSpeed').textContent = `${speedTest.upload} Mbps`;
            document.getElementById('pingValue').textContent = `${speedTest.ping} ms`;
            
            this.updateSpeedStatus('download', speedTest.download);
            this.updateSpeedStatus('upload', speedTest.upload);
            this.updatePingStatus(speedTest.ping);
            
            this.speedData.download.push(speedTest.download);
            this.speedData.upload.push(speedTest.upload);
            this.speedData.ping.push(speedTest.ping);
            
            this.log(`✅ Speed test complete: Download ${speedTest.download} Mbps, Upload ${speedTest.upload} Mbps, Ping ${speedTest.ping} ms`);
            
        } catch (error) {
            this.log(`❌ Speed test failed: ${error.message}`);
        }
    }

    async performSpeedTest() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const download = (Math.random() * 100 + 50).toFixed(2);
                const upload = (Math.random() * 50 + 10).toFixed(2);
                const ping = (Math.random() * 50 + 10).toFixed(2);
                
                resolve({ download, upload, ping });
            }, 3000);
        });
    }

    detectConnectionType() {
        const localSpeed = this.speedData.local[this.speedData.local.length - 1] || 0;
        
        let connectionType, speedClass;
        
        if (localSpeed > 500) {
            connectionType = "1000 Mbps (Gigabit Ethernet)";
            speedClass = "gigabit";
        } else if (localSpeed > 50) {
            connectionType = "100 Mbps (Fast Ethernet)";
            speedClass = "fast-ethernet";
        } else {
            connectionType = "10 Mbps (Ethernet)";
            speedClass = "ethernet";
        }
        
        document.getElementById('connectionType').textContent = connectionType;
        document.getElementById('connectionType').className = `connection-type ${speedClass}`;
        
        this.log(`🔍 Connection type detected: ${connectionType}`);
        this.log(`📊 Current local speed: ${localSpeed.toFixed(2)} Mbps`);
    }

    updateSpeedStatus(type, speed) {
        const element = document.getElementById(`${type}Status`);
        let status, color;
        
        if (type === 'download') {
            if (speed > 50) {
                status = '✓ Excellent';
                color = '#4CAF50';
            } else if (speed > 25) {
                status = '✓ Good';
                color = '#8BC34A';
            } else if (speed > 10) {
                status = '⚠ Acceptable';
                color = '#FFC107';
            } else {
                status = '✗ Poor';
                color = '#F44336';
            }
        } else {
            if (speed > 20) {
                status = '✓ Excellent';
                color = '#4CAF50';
            } else if (speed > 10) {
                status = '✓ Good';
                color = '#8BC34A';
            } else if (speed > 5) {
                status = '⚠ Acceptable';
                color = '#FFC107';
            } else {
                status = '✗ Poor';
                color = '#F44336';
            }
        }
        
        element.textContent = status;
        element.style.color = color;
    }

    updatePingStatus(ping) {
        const element = document.getElementById('pingStatus');
        let status, color;
        
        if (ping < 30) {
            status = '✓ Excellent';
            color = '#4CAF50';
        } else if (ping < 60) {
            status = '✓ Good';
            color = '#8BC34A';
        } else if (ping < 100) {
            status = '⚠ Acceptable';
            color = '#FFC107';
        } else {
            status = '✗ High';
            color = '#F44336';
        }
        
        element.textContent = status;
        element.style.color = color;
    }

    updateCharts() {
        this.speedChart.update();
        
        const latestLocal = this.speedData.local[this.speedData.local.length - 1] || 0;
        const latestDownload = this.speedData.download[this.speedData.download.length - 1] || 0;
        const latestUpload = this.speedData.upload[this.speedData.upload.length - 1] || 0;
        
        this.comparisonChart.data.datasets[0].data = [latestLocal, latestDownload, latestUpload];
        this.comparisonChart.update();
    }

    log(message) {
        const logElement = document.getElementById('log');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `<strong>[${timestamp}]</strong> ${message}`;
        
        logElement.appendChild(logEntry);
        logElement.scrollTop = logElement.scrollHeight;
    }

    capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
}

// Initialize application when page loads
document.addEventListener('DOMContentLoaded', () => {
    new NetworkMonitor();
});
