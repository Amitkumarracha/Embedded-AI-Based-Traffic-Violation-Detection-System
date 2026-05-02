// Traffic Violation Detection System - Frontend JavaScript

class TrafficMonitor {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.stats = {
            totalViolations: 0,
            todayViolations: 0,
            activeDetections: 0,
            systemUptime: 0
        };
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.startStatsUpdate();
        this.loadRecentViolations();
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.addLog('info', 'Connected to detection system');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.addLog('error', 'WebSocket connection error');
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.addLog('warning', 'Disconnected from detection system');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(), 3000);
        };
    }

    handleWebSocketMessage(data) {
        switch(data.type) {
            case 'violation':
                this.handleNewViolation(data.data);
                break;
            case 'stats':
                this.updateStats(data.data);
                break;
            case 'frame':
                this.updateVideoFrame(data.data);
                break;
            case 'log':
                this.addLog(data.level, data.message);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    handleNewViolation(violation) {
        this.addViolationToList(violation);
        this.stats.totalViolations++;
        this.stats.todayViolations++;
        this.updateStatsDisplay();
        this.showNotification('New Violation Detected!', violation.type);
    }

    addViolationToList(violation) {
        const violationsList = document.getElementById('violationsList');
        const violationItem = document.createElement('div');
        violationItem.className = 'violation-item';
        
        const time = new Date(violation.timestamp).toLocaleTimeString();
        
        violationItem.innerHTML = `
            <div class="violation-header">
                <span class="violation-type">🚨 ${violation.type}</span>
                <span class="violation-time">${time}</span>
            </div>
            <div class="violation-details">
                ${violation.details || 'No additional details'}
            </div>
            ${violation.plate ? `<span class="violation-plate">📋 ${violation.plate}</span>` : ''}
        `;
        
        violationsList.insertBefore(violationItem, violationsList.firstChild);
        
        // Keep only last 20 violations
        while (violationsList.children.length > 20) {
            violationsList.removeChild(violationsList.lastChild);
        }
    }

    updateStats(stats) {
        this.stats = { ...this.stats, ...stats };
        this.updateStatsDisplay();
    }

    updateStatsDisplay() {
        document.getElementById('totalViolations').textContent = this.stats.totalViolations;
        document.getElementById('todayViolations').textContent = this.stats.todayViolations;
        document.getElementById('activeDetections').textContent = this.stats.activeDetections;
        document.getElementById('systemUptime').textContent = this.formatUptime(this.stats.systemUptime);
    }

    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }

    updateVideoFrame(frameData) {
        const videoFeed = document.getElementById('videoFeed');
        videoFeed.src = `data:image/jpeg;base64,${frameData}`;
    }

    addLog(level, message) {
        const logsContainer = document.getElementById('logsContainer');
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${level}`;
        
        const time = new Date().toLocaleTimeString();
        logEntry.innerHTML = `
            <span class="log-time">[${time}]</span>
            <span class="log-message">${message}</span>
        `;
        
        logsContainer.insertBefore(logEntry, logsContainer.firstChild);
        
        // Keep only last 50 logs
        while (logsContainer.children.length > 50) {
            logsContainer.removeChild(logsContainer.lastChild);
        }
    }

    updateConnectionStatus(connected) {
        const statusBadge = document.querySelector('.status-badge');
        const statusText = statusBadge.querySelector('span');
        const statusDot = statusBadge.querySelector('.status-dot');
        
        if (connected) {
            statusText.textContent = 'System Active';
            statusDot.style.background = 'var(--success-color)';
        } else {
            statusText.textContent = 'Disconnected';
            statusDot.style.background = 'var(--danger-color)';
        }
    }

    setupEventListeners() {
        // Start/Stop Detection
        document.getElementById('startBtn')?.addEventListener('click', () => {
            this.sendCommand('start');
            this.addLog('info', 'Starting detection system...');
        });
        
        document.getElementById('stopBtn')?.addEventListener('click', () => {
            this.sendCommand('stop');
            this.addLog('info', 'Stopping detection system...');
        });
        
        // Capture Screenshot
        document.getElementById('captureBtn')?.addEventListener('click', () => {
            this.captureScreenshot();
        });
        
        // Settings
        document.getElementById('saveSettingsBtn')?.addEventListener('click', () => {
            this.saveSettings();
        });
        
        // Export Data
        document.getElementById('exportBtn')?.addEventListener('click', () => {
            this.exportViolations();
        });
    }

    sendCommand(command, data = {}) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'command',
                command: command,
                data: data
            }));
        } else {
            this.addLog('error', 'Cannot send command: Not connected');
        }
    }

    captureScreenshot() {
        const videoFeed = document.getElementById('videoFeed');
        const canvas = document.createElement('canvas');
        canvas.width = videoFeed.naturalWidth;
        canvas.height = videoFeed.naturalHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoFeed, 0, 0);
        
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `capture_${Date.now()}.jpg`;
            a.click();
            URL.revokeObjectURL(url);
            this.addLog('success', 'Screenshot captured');
        }, 'image/jpeg');
    }

    saveSettings() {
        const settings = {
            confidence: document.getElementById('confidenceThreshold')?.value,
            speedLimit: document.getElementById('speedLimit')?.value,
            processFrames: document.getElementById('processFrames')?.value
        };
        
        this.sendCommand('update_settings', settings);
        this.addLog('info', 'Settings updated');
        this.showNotification('Settings Saved', 'Configuration updated successfully');
    }

    async loadRecentViolations() {
        try {
            const response = await fetch('/api/violations/recent');
            const violations = await response.json();
            
            violations.forEach(violation => {
                this.addViolationToList(violation);
            });
        } catch (error) {
            console.error('Error loading violations:', error);
            this.addLog('error', 'Failed to load recent violations');
        }
    }

    async exportViolations() {
        try {
            const response = await fetch('/api/violations/export');
            const blob = await response.blob();
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `violations_${Date.now()}.csv`;
            a.click();
            URL.revokeObjectURL(url);
            
            this.addLog('success', 'Violations exported successfully');
        } catch (error) {
            console.error('Error exporting violations:', error);
            this.addLog('error', 'Failed to export violations');
        }
    }

    startStatsUpdate() {
        setInterval(() => {
            if (this.isConnected) {
                this.stats.systemUptime += 1;
                this.updateStatsDisplay();
            }
        }, 1000);
        
        // Request stats update every 5 seconds
        setInterval(() => {
            if (this.isConnected) {
                this.sendCommand('get_stats');
            }
        }, 5000);
    }

    showNotification(title, message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.png'
            });
        }
    }

    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const monitor = new TrafficMonitor();
    monitor.requestNotificationPermission();
    
    // Make monitor globally accessible for debugging
    window.trafficMonitor = monitor;
    
    console.log('Traffic Violation Detection System initialized');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Page hidden');
    } else {
        console.log('Page visible');
        // Reload recent violations when page becomes visible
        if (window.trafficMonitor) {
            window.trafficMonitor.loadRecentViolations();
        }
    }
});
