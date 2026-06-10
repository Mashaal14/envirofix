const API_BASE = 'http://localhost:7070';

class EnviroFixAPI {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      throw error;
    }
  }

  async getHealth() {
    return this.request('/health');
  }

  async getAlerts() {
    try {
      return await this.request('/alerts');
    } catch {
      return [];
    }
  }

  async getSystemInfo() {
    try {
      return await this.request('/system');
    } catch {
      return { kernel: {}, network: {} };
    }
  }

  async triggerScan() {
    return this.request('/scan');
  }

  async analyseIssue(issue, tool) {
    return this.request('/analyse', {
      method: 'POST',
      body: JSON.stringify({ issue, tool }),
    });
  }
}

export default new EnviroFixAPI();
