class AnkiTTSApp {
    constructor() {
        this.apiBase = window.location.origin;
        this.currentDeck = null;
        this.allCards = [];
        this.cardsWithoutAudio = [];
        this.isProcessing = false;
        this.processedCount = 0;
        this.currentFilter = 'all';
        
        this.initializeEventListeners();
        this.loadDecks();
    }

    initializeEventListeners() {
        // Deck selection
        document.getElementById('deckSelect').addEventListener('change', () => {
            const selectedDeck = document.getElementById('deckSelect').value;
            document.getElementById('loadCardsBtn').disabled = !selectedDeck;
        });

        document.getElementById('loadCardsBtn').addEventListener('click', () => {
            this.loadCardsFromDeck();
        });

        // Processing controls
        document.getElementById('startProcessingBtn').addEventListener('click', () => {
            this.startBatchProcessing();
        });

        document.getElementById('stopProcessingBtn').addEventListener('click', () => {
            this.stopProcessing();
        });

        // Filter buttons
        document.getElementById('showAllBtn').addEventListener('click', () => {
            this.setFilter('all');
        });

        document.getElementById('showNoAudioBtn').addEventListener('click', () => {
            this.setFilter('no-audio');
        });

        document.getElementById('showProcessedBtn').addEventListener('click', () => {
            this.setFilter('processed');
        });

        // Log controls
        document.getElementById('clearLogBtn').addEventListener('click', () => {
            this.clearLog();
        });
    }

    async loadDecks() {
        this.log('Loading Anki decks...', 'info');
        
        try {
            const response = await fetch(`${this.apiBase}/api/decks`);
            const decks = await response.json();
            
            if (!response.ok) {
                throw new Error(decks.detail || 'Failed to load decks');
            }
            
            const deckSelect = document.getElementById('deckSelect');
            deckSelect.innerHTML = '<option value="">Select a deck...</option>';
            
            decks.forEach(deck => {
                const option = document.createElement('option');
                option.value = deck.name;
                option.textContent = `${deck.name} (${deck.card_count} cards)`;
                deckSelect.appendChild(option);
            });
            
            this.log(`Loaded ${decks.length} decks successfully`, 'success');
            
        } catch (error) {
            this.log(`Error loading decks: ${error.message}`, 'error');
            document.getElementById('deckSelect').innerHTML = '<option value="">Error loading decks</option>';
        }
    }

    async loadCardsFromDeck() {
        const selectedDeck = document.getElementById('deckSelect').value;
        if (!selectedDeck) return;

        this.log(`Loading cards from deck: ${selectedDeck}`, 'info');
        this.setLoadingState(true);
        
        try {
            const response = await fetch(`${this.apiBase}/api/deck/${encodeURIComponent(selectedDeck)}/cards`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to load cards');
            }
            
            this.allCards = data.cards;
            this.cardsWithoutAudio = data.cards.filter(card => !card.has_audio);
            this.currentDeck = selectedDeck;
            
            this.updateStats();
            this.displayCards();
            this.enableProcessing();
            
            this.log(`Loaded ${this.allCards.length} cards, ${this.cardsWithoutAudio.length} without audio`, 'success');
            
        } catch (error) {
            this.log(`Error loading cards: ${error.message}`, 'error');
        } finally {
            this.setLoadingState(false);
        }
    }

    async startBatchProcessing() {
        if (this.cardsWithoutAudio.length === 0) {
            this.log('No cards without audio to process', 'info');
            return;
        }

        this.isProcessing = true;
        this.processedCount = 0;
        const language = document.getElementById('batchLanguageSelect').value;
        
        this.showProcessingUI();
        this.log(`Starting batch processing of ${this.cardsWithoutAudio.length} cards in ${language}`, 'info');

        for (let i = 0; i < this.cardsWithoutAudio.length && this.isProcessing; i++) {
            const card = this.cardsWithoutAudio[i];
            await this.processCard(card, language);
            this.processedCount++;
            this.updateProgress();
        }

        if (this.isProcessing) {
            this.completeProcessing();
        }
    }

    async processCard(card, language) {
        try {
            this.updateCurrentProcessing(card, 'Generating audio...');
            card.processing_status = 'processing';
            this.displayCards(); // Update display to show processing state
            
            const response = await fetch(`${this.apiBase}/api/generate-audio-for-card`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    card_id: card.id,
                    language: language
                })
            });

            const result = await response.json();
            
            if (response.ok) {
                card.has_audio = true;
                card.audio_url = result.audio_url;
                card.processing_status = 'completed';
                this.log(`✓ Generated audio for card ${card.id}: "${card.text}"`, 'success');
            } else {
                throw new Error(result.detail || 'Failed to generate audio');
            }
            
        } catch (error) {
            card.processing_status = 'failed';
            this.log(`✗ Failed to process card ${card.id}: ${error.message}`, 'error');
        }
        
        this.displayCards(); // Update display after processing
        await this.delay(1000); // Delay between requests
    }

    stopProcessing() {
        this.isProcessing = false;
        this.hideProcessingUI();
        this.log('Processing stopped by user', 'info');
    }

    completeProcessing() {
        this.isProcessing = false;
        this.hideProcessingUI();
        
        const successful = this.allCards.filter(card => card.processing_status === 'completed').length;
        const failed = this.allCards.filter(card => card.processing_status === 'failed').length;
        
        this.log(`Processing completed! Successful: ${successful}, Failed: ${failed}`, 'success');
        this.updateStats();
    }

    showProcessingUI() {
        document.getElementById('progressContainer').style.display = 'block';
        document.getElementById('currentProcessing').style.display = 'block';
        document.getElementById('startProcessingBtn').style.display = 'none';
        document.getElementById('stopProcessingBtn').style.display = 'inline-block';
    }

    hideProcessingUI() {
        document.getElementById('progressContainer').style.display = 'none';
        document.getElementById('currentProcessing').style.display = 'none';
        document.getElementById('startProcessingBtn').style.display = 'inline-block';
        document.getElementById('stopProcessingBtn').style.display = 'none';
    }

    updateCurrentProcessing(card, status) {
        document.getElementById('currentCardId').textContent = card.id;
        document.getElementById('currentCardText').textContent = card.text || 'No text';
        document.getElementById('currentStatus').textContent = status;
    }

    updateProgress() {
        const total = this.cardsWithoutAudio.length;
        const processed = this.processedCount;
        const percentage = Math.round((processed / total) * 100);
        
        document.getElementById('progressFill').style.width = `${percentage}%`;
        document.getElementById('progressText').textContent = `${processed} / ${total} cards processed`;
        document.getElementById('progressPercent').textContent = `${percentage}%`;
    }

    updateStats() {
        const total = this.allCards.length;
        const withoutAudio = this.allCards.filter(card => !card.has_audio).length;
        const withAudio = total - withoutAudio;
        const processed = this.allCards.filter(card => card.processing_status === 'completed').length;
        
        document.getElementById('totalCards').textContent = total;
        document.getElementById('cardsWithoutAudio').textContent = withoutAudio;
        document.getElementById('cardsWithAudio').textContent = withAudio;
        document.getElementById('processedCards').textContent = processed;
    }

    setFilter(filter) {
        this.currentFilter = filter;
        
        // Update active button
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        
        if (filter === 'all') {
            document.getElementById('showAllBtn').classList.add('active');
        } else if (filter === 'no-audio') {
            document.getElementById('showNoAudioBtn').classList.add('active');
        } else if (filter === 'processed') {
            document.getElementById('showProcessedBtn').classList.add('active');
        }
        
        this.displayCards();
    }

    displayCards() {
        const container = document.getElementById('cardsContainer');
        
        let cardsToShow = [];
        switch (this.currentFilter) {
            case 'all':
                cardsToShow = this.allCards;
                break;
            case 'no-audio':
                cardsToShow = this.allCards.filter(card => !card.has_audio);
                break;
            case 'processed':
                cardsToShow = this.allCards.filter(card => card.processing_status === 'completed');
                break;
        }
        
        if (cardsToShow.length === 0) {
            container.innerHTML = '<p>No cards to display</p>';
            return;
        }
        
        container.innerHTML = cardsToShow.map(card => this.createCardHTML(card)).join('');
    }

    createCardHTML(card) {
        let statusClass = card.has_audio ? 'has-audio' : 'no-audio';
        let statusText = card.has_audio ? 'Has Audio' : 'No Audio';
        let statusBadgeClass = card.has_audio ? 'status-has-audio' : 'status-no-audio';
        
        if (card.processing_status === 'processing') {
            statusClass = 'processing';
            statusText = 'Processing...';
            statusBadgeClass = 'status-processing';
        }
        
        return `
            <div class="card-item ${statusClass}">
                <h4>${card.text || 'No text available'}</h4>
                <p><strong>ID:</strong> ${card.id}</p>
                <p><strong>Type:</strong> ${card.note_type}</p>
                <p><strong>Status:</strong> <span class="card-status ${statusBadgeClass}">${statusText}</span></p>
                ${card.audio_url ? `<p><strong>Audio:</strong> <a href="${card.audio_url}" target="_blank">Play</a></p>` : ''}
            </div>
        `;
    }

    enableProcessing() {
        document.getElementById('startProcessingBtn').disabled = false;
    }

    setLoadingState(loading) {
        const loadBtn = document.getElementById('loadCardsBtn');
        if (loading) {
            loadBtn.disabled = true;
            loadBtn.textContent = 'Loading...';
        } else {
            loadBtn.disabled = false;
            loadBtn.textContent = 'Load Cards';
        }
    }

    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logContainer = document.getElementById('logContainer');
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.textContent = `[${timestamp}] ${message}`;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    clearLog() {
        document.getElementById('logContainer').innerHTML = '<p>Log cleared...</p>';
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AnkiTTSApp();
});