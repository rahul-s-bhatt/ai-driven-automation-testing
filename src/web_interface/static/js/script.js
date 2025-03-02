// Theme Management
function initTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-toggle i');
    icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
}

// Chart Configuration
let charts = {
    loadTime: null,
    elements: null,
    performance: null
};

function initCharts(data) {
    const ctx = {
        loadTime: document.getElementById('loadTimeChart')?.getContext('2d'),
        elements: document.getElementById('elementChart')?.getContext('2d'),
        performance: document.getElementById('performanceChart')?.getContext('2d')
    };

    if (ctx.loadTime) {
        charts.loadTime = new Chart(ctx.loadTime, {
            type: 'line',
            data: {
                labels: ['Initial', 'After 1s', 'After 2s', 'After 3s'],
                datasets: [{
                    label: 'Load Time (seconds)',
                    data: [0, data.load_time / 3, data.load_time / 2, data.load_time],
                    borderColor: '#3498db',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    if (ctx.elements && data.element_counts) {
        charts.elements = new Chart(ctx.elements, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.element_counts).map(key => key.replace('_', ' ')),
                datasets: [{
                    data: Object.values(data.element_counts),
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#f1c40f',
                        '#e74c3c',
                        '#9b59b6'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    if (ctx.performance) {
        const score = calculatePerformanceScore(data);
        document.getElementById('performance-score').textContent = score;
        
        charts.performance = new Chart(ctx.performance, {
            type: 'gauge',
            data: {
                datasets: [{
                    value: score,
                    data: [20, 40, 60, 80, 100],
                    backgroundColor: ['#e74c3c', '#f1c40f', '#2ecc71'],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

function calculatePerformanceScore(data) {
    // Complex performance calculation based on multiple factors
    let score = 100;
    
    if (data.load_time > 3) score -= 20;
    if (data.load_time > 5) score -= 20;
    
    const totalElements = Object.values(data.element_counts || {}).reduce((a, b) => a + b, 0);
    if (totalElements > 1000) score -= 10;
    if (totalElements > 2000) score -= 10;
    
    return Math.max(0, score);
}

// Example Scenarios Management
const examples = {
    'simple': `wait for 2 seconds
type "test" into search box
click on search button
wait for 2 seconds
verify that results appear`,
    
    'infinite-scroll': `wait for 2 seconds
scroll down till end
wait for 2 seconds
verify that new content appears
scroll down till end
wait for 2 seconds
verify that more content appears`,
    
    'dynamic': `wait for 2 seconds
click on load more button
wait for 2 seconds
verify that new items appear`
};

function loadExample(type) {
    const testSteps = document.getElementById('test_steps');
    if (testSteps && examples[type]) {
        const testRunnerNav = document.querySelector('.nav-item[onclick*="test-runner"]');
        showSection('test-runner', testRunnerNav);
        testSteps.value = examples[type];
        testSteps.focus();
    }
}

// Analysis Form Handler
document.getElementById('analyzeForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const analyzing = document.getElementById('analyzing');
    const results = document.getElementById('analysis-results');
    
    if (!analyzing || !results) return;
    
    analyzing.style.display = 'block';
    results.style.display = 'none';
    
    const progressBar = analyzing.querySelector('.progress-bar-fill');
    let progress = 0;
    
    const progressInterval = setInterval(() => {
        progress += 5;
        if (progress <= 90) {
            progressBar.style.width = progress + '%';
        }
    }, 500);
    
    try {
        const response = await fetch('/analyze_site', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: form.url.value
            })
        });
        
        const data = await response.json();
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        if (data.success) {
            initCharts(data.analysis.structure.page_metrics);
            
            // Update Forms Analysis
            const formsContainer = document.querySelector('.forms-container');
            if (formsContainer && data.analysis.structure.forms) {
                formsContainer.innerHTML = data.analysis.structure.forms.map(form => `
                    <div class="card">
                        <h5>${form.id || 'Unnamed Form'}</h5>
                        <div class="metrics-details">
                            <small>Method: ${form.method}</small>
                            <small>Inputs: ${form.inputs.length}</small>
                        </div>
                        <div class="form-inputs">
                            ${form.inputs.map(input => `
                                <div class="input-item">
                                    <i class="fas fa-input"></i>
                                    ${input.type}
                                    ${input.required ? '<span class="required-badge">Required</span>' : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('') || '<p>No forms found</p>';
            }

            // Update Navigation Structure
            const navContainer = document.querySelector('.navigation-container');
            if (navContainer && data.analysis.structure.navigation) {
                navContainer.innerHTML = data.analysis.structure.navigation.map(nav => `
                    <div class="card">
                        <h5>${nav.type} Navigation</h5>
                        <div class="nav-items">
                            ${nav.items.map(item => `
                                <div class="nav-item-analysis">
                                    <i class="fas fa-link"></i>
                                    <span>${item.text}</span>
                                    <small>${item.href}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('') || '<p>No navigation structure found</p>';
            }

            // Update Dynamic Content Analysis
            const dynamicContainer = document.querySelector('.dynamic-container');
            if (dynamicContainer && data.analysis.structure.dynamic_content) {
                const dynamic = data.analysis.structure.dynamic_content;
                dynamicContainer.innerHTML = `
                    <div class="feature-grid">
                        <div class="feature-item ${dynamic.infinite_scroll ? 'feature-detected' : 'feature-not-detected'}">
                            <i class="fas fa-infinity"></i>
                            <span>Infinite Scroll</span>
                        </div>
                        <div class="feature-item ${dynamic.load_more ? 'feature-detected' : 'feature-not-detected'}">
                            <i class="fas fa-plus"></i>
                            <span>Load More</span>
                        </div>
                        <div class="feature-item ${dynamic.auto_refresh ? 'feature-detected' : 'feature-not-detected'}">
                            <i class="fas fa-sync"></i>
                            <span>Auto Refresh</span>
                        </div>
                    </div>
                `;
            }

            // Update Suggested Scenarios
            const suggestedContainer = document.querySelector('.suggestions-container');
            if (suggestedContainer && data.analysis.structure.suggested_scenarios) {
                suggestedContainer.innerHTML = data.analysis.structure.suggested_scenarios
                    .map(scenario => `
                        <div class="card scenario-card">
                            <div class="scenario-header">
                                <h4>${scenario.name}</h4>
                                <button class="btn btn-primary try-it-btn" 
                                        data-scenario="${encodeURIComponent(JSON.stringify(scenario.steps))}"
                                        data-tooltip="Try this scenario">
                                    <i class="fas fa-play"></i>
                                </button>
                            </div>
                            <p>${scenario.description}</p>
                            <div class="scenario-steps">
                                <pre class="steps-code">${scenario.steps.join('\n')}</pre>
                            </div>
                        </div>
                    `).join('');
            }

            results.style.display = 'block';
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
    } catch (error) {
        clearInterval(progressInterval);
        results.innerHTML = `
            <div class="card error">
                <h3><i class="fas fa-exclamation-triangle"></i> Error:</h3>
                <p>${error.message}</p>
            </div>
        `;
        results.style.display = 'block';
    } finally {
        setTimeout(() => {
            analyzing.style.display = 'none';
        }, 500);
    }
});

// Test Runner Form Handler
document.getElementById('testForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    if (!loading || !results) return;
    
    loading.style.display = 'block';
    results.style.display = 'none';
    
    const progressBar = loading.querySelector('.progress-bar-fill');
    let progress = 0;
    
    const progressInterval = setInterval(() => {
        progress += 5;
        if (progress <= 90) {
            progressBar.style.width = progress + '%';
        }
    }, 500);
    
    try {
        const steps = document.getElementById('test_steps').value
            .split('\n')
            .filter(step => step.trim())
            .map(step => `      - ${step.trim()}`);
        
        const yamlContent = `scenarios:
  - name: User Test Case
    description: User provided test case
    tags: [user-test]
    steps:
${steps.join('\n')}`;
        
        const response = await fetch('/run_test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: form.url.value,
                test_yaml: yamlContent
            })
        });
        
        const data = await response.json();
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        if (data.success) {
            results.innerHTML = `
                <div class="card result-success">
                    <h3><i class="fas fa-check-circle"></i> Tests Passed!</h3>
                    <p>All steps completed successfully.</p>
                    ${data.screenshots ? `
                        <div class="screenshots-grid">
                            ${data.screenshots.map(screenshot => `
                                <div class="screenshot-item">
                                    <img src="${screenshot}" alt="Test screenshot" loading="lazy">
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            results.innerHTML = `
                <div class="card result-error">
                    <h3><i class="fas fa-exclamation-circle"></i> Test Failed</h3>
                    <div class="error-details">
                        ${data.errors.map(error => `<p>${error}</p>`).join('')}
                    </div>
                    ${data.screenshots ? `
                        <div class="screenshots-grid">
                            ${data.screenshots.map(screenshot => `
                                <div class="screenshot-item">
                                    <img src="${screenshot}" alt="Error screenshot" loading="lazy">
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        }
        results.style.display = 'block';
    } catch (error) {
        clearInterval(progressInterval);
        results.innerHTML = `
            <div class="card result-error">
                <h3><i class="fas fa-exclamation-triangle"></i> Error:</h3>
                <p>${error.message}</p>
            </div>
        `;
        results.style.display = 'block';
    } finally {
        setTimeout(() => {
            loading.style.display = 'none';
        }, 500);
    }
});

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl + Space for test step suggestions
    if (e.ctrlKey && e.code === 'Space') {
        const testSteps = document.getElementById('test_steps');
        if (document.activeElement === testSteps) {
            e.preventDefault();
            showStepSuggestions(testSteps);
        }
    }
    
    // Ctrl + 1/2/3 for quick navigation
    if (e.ctrlKey && e.key >= '1' && e.key <= '3') {
        e.preventDefault();
        const sections = ['getting-started', 'analyze', 'test-runner'];
        const index = parseInt(e.key) - 1;
        const navButton = document.querySelector(`.nav-item[onclick*='${sections[index]}']`);
        if (navButton) {
            showSection(sections[index], navButton);
        }
    }
});

// Navigation
function showSection(sectionId, button) {
    // Hide all sections
    document.querySelectorAll('.tutorial-section').forEach(section => {
        section.classList.remove('active');
    });

    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
    });

    // Show selected section and activate button
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
        section.scrollIntoView({ behavior: 'smooth' });
    }
    
    if (button) {
        button.classList.add('active');
        button.setAttribute('aria-pressed', 'true');
    }
}

// Load Custom Scenario
function loadCustomScenario(steps) {
    try {
        const testSteps = document.getElementById('test_steps');
        if (!testSteps) return;
        
        let stepsArray;
        if (typeof steps === 'string') {
            const decodedSteps = decodeURIComponent(steps);
            stepsArray = JSON.parse(decodedSteps);
        } else {
            stepsArray = steps;
        }
        
        if (!Array.isArray(stepsArray)) return;
        
        const testRunnerNav = document.querySelector('.nav-item[onclick*="test-runner"]');
        if (testRunnerNav) {
            showSection('test-runner', testRunnerNav);
            testSteps.value = stepsArray.join('\n');
            testSteps.focus();
        }
        
    } catch (error) {
        console.error('Error loading scenario:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    
    // Theme toggle handler
    document.querySelector('.theme-toggle')?.addEventListener('click', toggleTheme);
    
    // Scenario button handler
    document.body.addEventListener('click', (event) => {
        const button = event.target.closest('.try-it-btn');
        if (button) {
            const scenarioData = button.getAttribute('data-scenario');
            if (scenarioData) {
                event.preventDefault();
                loadCustomScenario(scenarioData);
            }
        }
    });
    
    // Show initial section
    showSection('getting-started', document.querySelector('.nav-item'));
});