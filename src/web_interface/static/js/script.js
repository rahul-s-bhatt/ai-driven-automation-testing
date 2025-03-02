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
    if (icon) {
        icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

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
    }
    
    if (button) {
        button.classList.add('active');
        button.setAttribute('aria-pressed', 'true');
    }
}

// Example Scenarios
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
            progressBar.style.width = `${progress}%`;
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
            // Update metrics
            if (data.analysis.structure.page_metrics) {
                const metrics = data.analysis.structure.page_metrics;
                
                // Update load time display
                const loadTimeElement = document.getElementById('load-time');
                if (loadTimeElement) {
                    loadTimeElement.textContent = metrics.load_time + 's';
                }

                // Create charts if Chart.js is available
                if (window.Chart) {
                    try {
                        // Load time chart
                        const loadTimeCanvas = document.getElementById('loadTimeChart');
                        if (loadTimeCanvas) {
                            new Chart(loadTimeCanvas, {
                                type: 'line',
                                data: {
                                    labels: ['Initial', 'After 1s', 'After 2s', 'After 3s'],
                                    datasets: [{
                                        label: 'Load Time (seconds)',
                                        data: [0, metrics.load_time / 3, metrics.load_time / 2, metrics.load_time],
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

                        // Element distribution chart
                        const elementCanvas = document.getElementById('elementChart');
                        if (elementCanvas && metrics.element_counts) {
                            new Chart(elementCanvas, {
                                type: 'doughnut',
                                data: {
                                    labels: Object.keys(metrics.element_counts).map(key => key.replace('_', ' ')),
                                    datasets: [{
                                        data: Object.values(metrics.element_counts),
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

                        // Performance score chart
                        const score = 100 - (metrics.load_time > 3 ? 20 : 0) - (metrics.load_time > 5 ? 20 : 0);
                        const scoreElement = document.getElementById('performance-score');
                        if (scoreElement) {
                            scoreElement.textContent = score;
                        }

                        const performanceCanvas = document.getElementById('performanceChart');
                        if (performanceCanvas) {
                            new Chart(performanceCanvas, {
                                type: 'bar',
                                data: {
                                    labels: ['Performance Score'],
                                    datasets: [{
                                        data: [score],
                                        backgroundColor: score > 80 ? '#2ecc71' : score > 60 ? '#f1c40f' : '#e74c3c'
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            max: 100
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: false
                                        }
                                    }
                                }
                            });
                        }
                    } catch (chartError) {
                        console.error('Error creating charts:', chartError);
                    }
                }
            }

            // Update forms analysis
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

            // Update navigation structure
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

            // Update dynamic content section
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

            // Update suggested scenarios
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

            // Update dual-mode test results
            if (data.analysis.dual_mode_tests) {
                const dualModeSection = document.getElementById('dual-mode-tests');
                if (dualModeSection) {
                    // Update human instructions
                    const humanInstructions = dualModeSection.querySelector('.test-instructions');
                    if (humanInstructions && data.analysis.dual_mode_tests.outputs?.human_instructions) {
                        fetch(data.analysis.dual_mode_tests.outputs.human_instructions)
                            .then(response => response.text())
                            .then(text => {
                                humanInstructions.innerHTML = marked(text); // Using marked.js for markdown rendering
                                humanInstructions.querySelectorAll('pre code').forEach((block) => {
                                    if (window.hljs) {
                                        hljs.highlightElement(block);
                                    }
                                });
                            });
                    }

                    // Update automation script
                    const automationCode = dualModeSection.querySelector('.code-preview code');
                    if (automationCode && data.analysis.dual_mode_tests.outputs?.automation_script) {
                        fetch(data.analysis.dual_mode_tests.outputs.automation_script)
                            .then(response => response.text())
                            .then(text => {
                                automationCode.textContent = text;
                                if (window.hljs) {
                                    hljs.highlightElement(automationCode);
                                }
                            });
                    }

                    dualModeSection.style.display = 'block';
                }
            }

            // Show results
            results.style.display = 'block';
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
    } catch (error) {
        results.innerHTML = `
            <div class="card result-error">
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

// Test Form Handler
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
            progressBar.style.width = `${progress}%`;
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

// Tab Management for Dual-Mode Tests
function switchTab(mode) {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.onclick.toString().includes(mode)) {
            btn.classList.add('active');
        }
    });
    
    tabPanes.forEach(pane => {
        pane.classList.remove('active');
        if (pane.id === `${mode}-tests`) {
            pane.classList.add('active');
        }
    });
}

// Download Handlers for Test Instructions
function downloadInstructions(mode) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    let content, filename;
    
    if (mode === 'human') {
        content = document.querySelector('.test-instructions').innerText;
        filename = `human_test_instructions_${timestamp}.md`;
    } else {
        content = document.querySelector('.code-preview code').innerText;
        filename = `automated_test_script_${timestamp}.py`;
    }
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    
    // Theme toggle handler
    document.querySelector('.theme-toggle')?.addEventListener('click', toggleTheme);
    
    // Show initial section
    showSection('getting-started', document.querySelector('.nav-item'));
    
    // Initialize first tab for dual-mode tests
    switchTab('human');
});