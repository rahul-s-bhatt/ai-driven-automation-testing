/**
 * Analysis Overlay System for visualizing website structure analysis.
 * Provides real-time visualization of elements being analyzed.
 */

class AnalysisOverlay {
    constructor() {
        this.overlay = null;
        this.tooltipContainer = null;
        this.progressBar = null;
        this.currentElement = null;
        this.highlightedElements = new Set();
        this.colors = {
            form: '#3498db',      // Blue
            button: '#2ecc71',    // Green
            link: '#9b59b6',      // Purple
            dynamic: '#e67e22',   // Orange
            navigation: '#f1c40f', // Yellow
            analyzing: '#f39c12',  // Dark Yellow
            found: '#27ae60',     // Dark Green
            error: '#c0392b'      // Dark Red
        };
    }

    initialize() {
        // Create overlay container
        this.overlay = document.createElement('div');
        this.overlay.id = 'analysis-overlay';
        this.overlay.style.position = 'fixed';
        this.overlay.style.top = '0';
        this.overlay.style.left = '0';
        this.overlay.style.width = '100%';
        this.overlay.style.height = '100%';
        this.overlay.style.pointerEvents = 'none';
        this.overlay.style.zIndex = '10000';

        // Create tooltip container
        this.tooltipContainer = document.createElement('div');
        this.tooltipContainer.id = 'analysis-tooltip';
        this.tooltipContainer.style.position = 'fixed';
        this.tooltipContainer.style.padding = '8px';
        this.tooltipContainer.style.background = 'rgba(0, 0, 0, 0.8)';
        this.tooltipContainer.style.color = 'white';
        this.tooltipContainer.style.borderRadius = '4px';
        this.tooltipContainer.style.fontSize = '12px';
        this.tooltipContainer.style.zIndex = '10001';
        this.tooltipContainer.style.display = 'none';

        // Create progress bar
        this.progressBar = this.createProgressBar();

        // Add to document
        document.body.appendChild(this.overlay);
        document.body.appendChild(this.tooltipContainer);
        document.body.appendChild(this.progressBar);

        // Add styles
        this.injectStyles();
    }

    createProgressBar() {
        const container = document.createElement('div');
        container.id = 'analysis-progress';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.left = '50%';
        container.style.transform = 'translateX(-50%)';
        container.style.width = '300px';
        container.style.background = 'rgba(0, 0, 0, 0.8)';
        container.style.padding = '10px';
        container.style.borderRadius = '4px';
        container.style.zIndex = '10001';

        const text = document.createElement('div');
        text.style.color = 'white';
        text.style.marginBottom = '5px';
        text.style.textAlign = 'center';
        text.textContent = 'Analyzing...';

        const progress = document.createElement('div');
        progress.style.height = '4px';
        progress.style.background = '#2ecc71';
        progress.style.width = '0%';
        progress.style.transition = 'width 0.3s ease';
        progress.style.borderRadius = '2px';

        container.appendChild(text);
        container.appendChild(progress);

        return container;
    }

    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .element-highlight {
                position: absolute;
                pointer-events: none;
                transition: all 0.3s ease;
                border: 2px solid transparent;
                border-radius: 2px;
                box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.5);
            }
            
            .element-highlight.analyzing {
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 0.4; }
                50% { opacity: 0.8; }
                100% { opacity: 0.4; }
            }

            .element-label {
                position: absolute;
                top: -20px;
                left: 0;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 2px 4px;
                font-size: 10px;
                border-radius: 2px;
            }
        `;
        document.head.appendChild(style);
    }

    highlightElement(element, type, info = '') {
        const rect = element.getBoundingClientRect();
        const highlight = document.createElement('div');
        highlight.className = 'element-highlight analyzing';
        highlight.style.left = `${rect.left + window.scrollX}px`;
        highlight.style.top = `${rect.top + window.scrollY}px`;
        highlight.style.width = `${rect.width}px`;
        highlight.style.height = `${rect.height}px`;
        highlight.style.borderColor = this.colors[type];

        // Add label
        const label = document.createElement('div');
        label.className = 'element-label';
        label.textContent = type.toUpperCase();
        highlight.appendChild(label);

        // Add to overlay
        this.overlay.appendChild(highlight);
        this.highlightedElements.add(highlight);

        // Show tooltip on hover
        highlight.addEventListener('mouseenter', () => {
            this.showTooltip(rect, type, info);
        });
        highlight.addEventListener('mouseleave', () => {
            this.hideTooltip();
        });

        return highlight;
    }

    showTooltip(rect, type, info) {
        this.tooltipContainer.textContent = `${type}: ${info}`;
        this.tooltipContainer.style.display = 'block';
        
        // Position tooltip
        const tooltipRect = this.tooltipContainer.getBoundingClientRect();
        let left = rect.left + (rect.width - tooltipRect.width) / 2;
        let top = rect.top - tooltipRect.height - 5;

        // Keep tooltip in viewport
        left = Math.max(10, Math.min(left, window.innerWidth - tooltipRect.width - 10));
        top = Math.max(10, Math.min(top, window.innerHeight - tooltipRect.height - 10));

        this.tooltipContainer.style.left = `${left}px`;
        this.tooltipContainer.style.top = `${top}px`;
    }

    hideTooltip() {
        this.tooltipContainer.style.display = 'none';
    }

    updateProgress(percent, text) {
        const progressBar = this.progressBar.querySelector('div:last-child');
        const progressText = this.progressBar.querySelector('div:first-child');
        
        progressBar.style.width = `${percent}%`;
        progressText.textContent = text;
    }

    markElementFound(highlight) {
        highlight.classList.remove('analyzing');
        highlight.style.borderColor = this.colors.found;
    }

    markElementError(highlight) {
        highlight.classList.remove('analyzing');
        highlight.style.borderColor = this.colors.error;
    }

    clear() {
        this.highlightedElements.forEach(highlight => {
            highlight.remove();
        });
        this.highlightedElements.clear();
        this.hideTooltip();
        this.updateProgress(0, 'Analysis Complete');
    }
}

// Create global instance
window.analysisOverlay = new AnalysisOverlay();