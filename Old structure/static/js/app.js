class ChampionshipTracker {
    constructor() {
        this.refreshInterval = null;
        this.refreshTimer = null;
        this.timeRemaining = 120; // 2 minutes in seconds
        this.currentFormData = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.showInputPage();
    }
    
    bindEvents() {
        // Form submission
        document.getElementById('championship-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmit();
        });
        
        // Back button
        document.getElementById('back-button').addEventListener('click', () => {
            this.showInputPage();
        });
        
        // Manual refresh button
        document.getElementById('manual-refresh').addEventListener('click', () => {
            this.fetchResults();
        });
    }
    
    showInputPage() {
        document.getElementById('input-page').classList.add('active');
        document.getElementById('results-page').classList.remove('active');
        
        // Clear any existing intervals
        this.clearIntervals();
        
        // Clear form
        this.clearForm();
        
        // Clear errors
        this.hideError('error-display');
    }
    
    showResultsPage() {
        document.getElementById('input-page').classList.remove('active');
        document.getElementById('results-page').classList.add('active');
        
        // Show loading state
        document.getElementById('loading-message').classList.remove('hidden');
        document.getElementById('results-container').classList.add('hidden');
        
        // Clear errors
        this.hideError('results-error-display');
    }
    
    clearForm() {
        document.getElementById('height').value = '';
        document.getElementById('jumping-url').value = '';
        document.getElementById('agility-url').value = '';
    }
    
    clearIntervals() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
    
    handleFormSubmit() {
        const height = document.getElementById('height').value;
        const jumpingUrl = document.getElementById('jumping-url').value;
        const agilityUrl = document.getElementById('agility-url').value;
        
        // Validate height selection
        if (!height) {
            this.showError('error-display', 'Height selection is required.');
            return;
        }
        
        // Store form data for refresh
        this.currentFormData = {
            height: height,
            jumping_url: jumpingUrl || null,
            agility_url: agilityUrl || null
        };
        
        // Switch to results page and start fetching
        this.showResultsPage();
        this.startContinuousRefresh();
    }
    
    startContinuousRefresh() {
        // Initial fetch
        this.fetchResults();
        
        // Set up continuous refresh every 2 minutes
        this.refreshInterval = setInterval(() => {
            this.fetchResults();
        }, 120000); // 120 seconds
        
        // Start countdown timer
        this.startCountdownTimer();
    }
    
    startCountdownTimer() {
        this.timeRemaining = 120;
        this.updateTimerDisplay();
        
        this.refreshTimer = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            
            if (this.timeRemaining <= 0) {
                this.timeRemaining = 120; // Reset for next cycle
            }
        }, 1000);
    }
    
    updateTimerDisplay() {
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        const timerDisplay = document.getElementById('timer-display');
        timerDisplay.textContent = `Next refresh in ${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    async fetchResults() {
        try {
            console.log('=== FETCHING RESULTS ===');
            console.log('Form data:', this.currentFormData);
            
            // Reset timer
            this.timeRemaining = 120;
            
            const response = await fetch('/api/results', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.currentFormData)
            });
            
            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);
            
            const data = await response.json();
            console.log('Response data:', data);
            
            if (data.success) {
                console.log('Success! Displaying results...');
                this.displayResults(data.data);
                this.hideError('results-error-display');
            } else {
                console.log('Error from server:', data.error);
                this.showError('results-error-display', data.error);
            }
            
        } catch (error) {
            console.error('Error fetching results:', error);
            this.showError('results-error-display', 'Failed to fetch results. Please check your connection and try again.');
        }
    }
    
    displayResults(results) {
        console.log('=== DISPLAYING RESULTS ===');
        console.log('Results array:', results);
        console.log('Results length:', results.length);
        
        // Hide loading message and show results
        document.getElementById('loading-message').classList.add('hidden');
        document.getElementById('results-container').classList.remove('hidden');
        
        const tbody = document.getElementById('results-tbody');
        tbody.innerHTML = '';
        
        if (!results || results.length === 0) {
            console.log('No results to display');
            tbody.innerHTML = '<tr><td colspan="6">No results found</td></tr>';
            return;
        }
        
        results.forEach((row, index) => {
            console.log(`Processing row ${index}:`, row);
            
            const tr = document.createElement('tr');
            
            // Add cutoff styling for 20th place
            if (row.place === 20) {
                tr.classList.add('cutoff');
            }
            
            // Extract handler and dog from pairing
            const [handler, dog] = row.Pairing;
            console.log(`Handler: ${handler}, Dog: ${dog}`);
            
            tr.innerHTML = `
                <td>${row.place}</td>
                <td>${handler}</td>
                <td>${dog}</td>
                <td>${row.Points}</td>
                <td>${row['Round 1']}</td>
                <td>${row['Round 2']}</td>
            `;
            
            tbody.appendChild(tr);
        });
        
        console.log('Results display complete');
    }
    
    showError(elementId, message) {
        const errorDiv = document.getElementById(elementId);
        const errorMessage = document.getElementById(elementId.replace('-display', '-message'));
        
        errorMessage.textContent = message;
        errorDiv.classList.remove('hidden');
        
        // Auto-hide error after 5 seconds
        setTimeout(() => {
            this.hideError(elementId);
        }, 5000);
    }
    
    hideError(elementId) {
        const errorDiv = document.getElementById(elementId);
        errorDiv.classList.add('hidden');
    }
    
    setButtonLoading(loading) {
        const button = document.getElementById('find-button');
        const buttonText = document.getElementById('button-text');
        const spinner = document.getElementById('loading-spinner');
        
        if (loading) {
            button.disabled = true;
            buttonText.textContent = 'Loading...';
            spinner.classList.remove('hidden');
        } else {
            button.disabled = false;
            buttonText.textContent = 'Find Champ Class';
            spinner.classList.add('hidden');
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChampionshipTracker();
});