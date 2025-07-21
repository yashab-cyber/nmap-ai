/**
 * NMAP-AI Main JavaScript Application
 * Handles client-side functionality for the web interface
 */

class NmapAI {
    constructor() {
        this.apiBaseUrl = '/api';
        this.wsUrl = `ws://${window.location.host}/ws`;
        this.websocket = null;
        this.activeScanId = null;
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.bindEvents();
        this.initializeWebSocket();
        this.loadDashboardData();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Scan form submission
        const scanForm = document.getElementById('scanForm');
        if (scanForm) {
            scanForm.addEventListener('submit', this.handleScanSubmit.bind(this));
        }

        // Result refresh buttons
        document.querySelectorAll('.refresh-results').forEach(btn => {
            btn.addEventListener('click', this.refreshResults.bind(this));
        });

        // Export buttons
        document.querySelectorAll('.export-btn').forEach(btn => {
            btn.addEventListener('click', this.handleExport.bind(this));
        });

        // Configuration save
        const configForm = document.getElementById('configForm');
        if (configForm) {
            configForm.addEventListener('submit', this.handleConfigSave.bind(this));
        }
    }

    /**
     * Initialize WebSocket connection for real-time updates
     */
    initializeWebSocket() {
        try {
            this.websocket = new WebSocket(this.wsUrl);
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.websocket.onclose = () => {
                console.log('WebSocket connection closed. Attempting to reconnect...');
                setTimeout(() => this.initializeWebSocket(), 5000);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }

    /**
     * Handle WebSocket messages
     */
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'scan_progress':
                this.updateScanProgress(data);
                break;
            case 'scan_completed':
                this.handleScanCompleted(data);
                break;
            case 'scan_error':
                this.handleScanError(data);
                break;
            case 'vulnerability_detected':
                this.handleVulnerabilityDetected(data);
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }

    /**
     * Handle scan form submission
     */
    async handleScanSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const scanData = {
            targets: formData.get('targets').split('\n').map(t => t.trim()).filter(t => t),
            scan_type: formData.get('scan_type'),
            ports: formData.get('ports'),
            ai_enabled: formData.has('ai_enabled'),
            vulnerability_scan: formData.has('vulnerability_scan')
        };

        try {
            this.showLoading('Initiating scan...');
            
            const response = await fetch(`${this.apiBaseUrl}/scan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(scanData)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.activeScanId = result.scan_id;
                this.showSuccess('Scan initiated successfully!');
                this.redirectToResults(result.scan_id);
            } else {
                throw new Error(result.detail || 'Failed to start scan');
            }
        } catch (error) {
            this.showError(`Failed to start scan: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Update scan progress display
     */
    updateScanProgress(data) {
        const progressBar = document.querySelector(`[data-scan-id="${data.scan_id}"] .progress-bar`);
        const statusBadge = document.querySelector(`[data-scan-id="${data.scan_id}"] .status-badge`);
        
        if (progressBar) {
            progressBar.style.width = `${data.progress}%`;
            progressBar.setAttribute('aria-valuenow', data.progress);
        }

        if (statusBadge) {
            statusBadge.textContent = data.status;
            statusBadge.className = `status-badge ${data.status.toLowerCase()}`;
        }

        // Update progress text
        const progressText = document.querySelector(`[data-scan-id="${data.scan_id}"] .progress-text`);
        if (progressText) {
            progressText.textContent = `${data.progress}% - ${data.current_task || 'Scanning...'}`;
        }
    }

    /**
     * Handle scan completion
     */
    handleScanCompleted(data) {
        this.showSuccess('Scan completed successfully!');
        this.updateScanStatus(data.scan_id, 'completed');
        this.refreshResults();
    }

    /**
     * Handle scan error
     */
    handleScanError(data) {
        this.showError(`Scan failed: ${data.error}`);
        this.updateScanStatus(data.scan_id, 'failed');
    }

    /**
     * Handle vulnerability detection
     */
    handleVulnerabilityDetected(data) {
        this.showWarning(`New vulnerability detected: ${data.vulnerability.cve}`);
        this.updateVulnerabilityCount();
    }

    /**
     * Load dashboard data
     */
    async loadDashboardData() {
        if (!document.querySelector('.dashboard')) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/dashboard`);
            const data = await response.json();
            
            if (response.ok) {
                this.updateDashboard(data);
            }
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    }

    /**
     * Update dashboard statistics
     */
    updateDashboard(data) {
        this.updateStatCard('total-scans', data.total_scans);
        this.updateStatCard('active-scans', data.active_scans);
        this.updateStatCard('vulnerabilities', data.vulnerabilities_found);
        this.updateStatCard('hosts-discovered', data.hosts_discovered);
    }

    /**
     * Update a statistics card
     */
    updateStatCard(cardId, value) {
        const card = document.getElementById(cardId);
        if (card) {
            const valueElement = card.querySelector('.stat-value');
            if (valueElement) {
                valueElement.textContent = value;
            }
        }
    }

    /**
     * Handle export functionality
     */
    async handleExport(event) {
        const button = event.target;
        const scanId = button.dataset.scanId;
        const format = button.dataset.format;

        try {
            this.showLoading('Exporting data...');
            
            const response = await fetch(`${this.apiBaseUrl}/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ scan_id: scanId, format: format })
            });

            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, `scan_${scanId}.${format}`);
                this.showSuccess('Export completed successfully!');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            this.showError(`Export failed: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Download a file
     */
    downloadFile(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Refresh results data
     */
    async refreshResults() {
        const resultsContainer = document.querySelector('.results-container');
        if (!resultsContainer) return;

        try {
            this.showLoading('Refreshing results...');
            
            const response = await fetch(`${this.apiBaseUrl}/results`);
            const data = await response.json();
            
            if (response.ok) {
                this.updateResultsTable(data);
                this.showSuccess('Results refreshed!');
            }
        } catch (error) {
            this.showError(`Failed to refresh results: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Update results table
     */
    updateResultsTable(data) {
        // Implementation would update the results table with new data
        console.log('Updating results table with:', data);
    }

    /**
     * Redirect to results page
     */
    redirectToResults(scanId) {
        window.location.href = `/results?scan_id=${scanId}`;
    }

    /**
     * Show loading indicator
     */
    showLoading(message = 'Loading...') {
        // Implementation would show a loading spinner/message
        console.log('Loading:', message);
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        // Implementation would hide loading spinner
        console.log('Loading hidden');
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    /**
     * Show error message
     */
    showError(message) {
        this.showAlert(message, 'error');
    }

    /**
     * Show warning message
     */
    showWarning(message) {
        this.showAlert(message, 'warning');
    }

    /**
     * Show alert message
     */
    showAlert(message, type = 'info') {
        // Create and show alert using Bootstrap alerts or custom implementation
        const alertHtml = `
            <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.alert-container') || document.body;
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = alertHtml;
        container.insertBefore(tempDiv.firstElementChild, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NmapAI();
});
