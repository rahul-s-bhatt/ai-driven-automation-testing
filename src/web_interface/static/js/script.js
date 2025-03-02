
// Example test scenarios
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

// Load example into test runner
function loadExample(type) {
    const testSteps = document.getElementById('test_steps');
    if (testSteps && examples[type]) {
        const testRunnerNav = document.querySelector('.nav-item[onclick*="test-runner"]');
        showSection('test-runner', testRunnerNav);
        testSteps.value = examples[type];
    }
}

// Handle analyze form submission
document.getElementById('analyzeForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const analyzing = document.getElementById('analyzing');
    const results = document.getElementById('analysis-results');
    
    if (!analyzing || !results) return;
    
    analyzing.style.display = 'block';
    results.style.display = 'none';
    
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
        
        if (data.success) {
            // Update page statistics
            const statsContainer = document.querySelector('.stats-container');
            if (statsContainer && data.analysis.structure.page_metrics) {
                const metrics = data.analysis.structure.page_metrics;
                statsContainer.innerHTML = `
                    <div class="metric">
                        <span class="label">Load Time:</span>
                        <span class="value">${metrics.load_time}s</span>
                    </div>
                    ${Object.entries(metrics.element_counts).map(([type, count]) => `
                        <div class="metric">
                            <span class="label">${type.replace('_', ' ')}:</span>
                            <span class="value">${count}</span>
                        </div>
                    `).join('')}
                `;
            }

            // Update forms found
            const formsContainer = document.querySelector('.forms-container');
            if (formsContainer && data.analysis.structure.forms) {
                formsContainer.innerHTML = data.analysis.structure.forms.map(form => `
                    <div class="form-info">
                        <h5>${form.id}</h5>
                        <p>Method: ${form.method}</p>
                        <p>Inputs: ${form.inputs.length}</p>
                        <ul>
                            ${form.inputs.map(input => `
                                <li>${input.type}${input.required ? ' (required)' : ''}</li>
                            `).join('')}
                        </ul>
                    </div>
                `).join('') || '<p>No forms found</p>';
            }

            // Update navigation structure
            const navContainer = document.querySelector('.navigation-container');
            if (navContainer && data.analysis.structure.navigation) {
                navContainer.innerHTML = data.analysis.structure.navigation.map(nav => `
                    <div class="nav-info">
                        <h5>${nav.type} Navigation</h5>
                        <ul>
                            ${nav.items.map(item => `
                                <li>${item.text} (${item.href})</li>
                            `).join('')}
                        </ul>
                    </div>
                `).join('') || '<p>No navigation structure found</p>';
            }

            // Update dynamic content section
            const dynamicContainer = document.querySelector('.dynamic-container');
            if (dynamicContainer && data.analysis.structure.dynamic_content) {
                const dynamic = data.analysis.structure.dynamic_content;
                dynamicContainer.innerHTML = `
                    <ul>
                        ${dynamic.infinite_scroll ? '<li>✅ Infinite scroll detected</li>' : ''}
                        ${dynamic.load_more ? '<li>✅ Load more functionality detected</li>' : ''}
                        ${dynamic.auto_refresh ? '<li>✅ Auto refresh functionality detected</li>' : ''}
                        ${!dynamic.infinite_scroll && !dynamic.load_more && !dynamic.auto_refresh ?
                            '<li>No dynamic content features detected</li>' : ''}
                    </ul>
                `;
            }

            // Update suggested scenarios
            const suggestedContainer = document.querySelector('.suggestions-container');
            if (suggestedContainer && data.analysis.structure.suggested_scenarios) {
                suggestedContainer.innerHTML = data.analysis.structure.suggested_scenarios
                    .map(scenario => `
                        <div class="scenario-card">
                            <h4>${scenario.name}</h4>
                            <p>${scenario.description}</p>
                            <div class="scenario-steps">
                                <pre class="steps-code">${scenario.steps.join('\n')}</pre>
                            </div>
                            <button class="try-it-btn" data-scenario="${encodeURIComponent(JSON.stringify(scenario.steps))}">
                                Try This Scenario
                            </button>
                        </div>
                    `).join('');
            }

            results.style.display = 'block';
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
    } catch (error) {
        results.innerHTML = `
            <div class="error">
                <h3>❌ Error:</h3>
                <p>${error.message}</p>
            </div>
        `;
        results.style.display = 'block';
    } finally {
        analyzing.style.display = 'none';
    }
});

// Load custom scenario
function loadCustomScenario(steps) {
    try {
        console.log('loadCustomScenario called with:', steps);
        
        const testSteps = document.getElementById('test_steps');
        if (!testSteps) {
            console.error('test_steps element not found');
            return;
        }
        
        // Parse steps if they're passed as a string
        let stepsArray;
        if (typeof steps === 'string') {
            console.log('Decoding steps string:', steps);
            const decodedSteps = decodeURIComponent(steps);
            console.log('Decoded steps:', decodedSteps);
            stepsArray = JSON.parse(decodedSteps);
        } else {
            stepsArray = steps;
        }
        console.log('Parsed steps array:', stepsArray);
        
        if (!Array.isArray(stepsArray)) {
            console.error('Invalid steps format:', stepsArray);
            return;
        }
        
        // Navigate to test runner section and update test steps
        const testRunnerNav = document.querySelector('.nav-item[onclick*="test-runner"]');
        if (testRunnerNav) {
            console.log('Found test runner nav, showing section');
            showSection('test-runner', testRunnerNav);
            
            const stepsText = stepsArray.join('\n');
            console.log('Setting steps text:', stepsText);
            testSteps.value = stepsText;
            testSteps.focus();
            testSteps.scrollIntoView({ behavior: 'smooth' });
        } else {
            console.error('Test runner nav element not found');
        }
        
        // Hide any loading indicators
        const loadingElements = ['loading', 'analyzing'];
        loadingElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.style.display = 'none';
            }
        });
        
        console.log('Scenario loaded successfully');
    } catch (error) {
        console.error('Error loading scenario:', error);
        console.error('Error details:', error.message);
        console.error('Stack trace:', error.stack);
    }
}

// Handle test form submission
document.getElementById('testForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    if (!loading || !results) return;
    
    loading.style.display = 'block';
    results.style.display = 'none';
    
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
        
        if (data.success) {
            results.innerHTML = `
                <div class="success">
                    <h3>✅ Tests Passed!</h3>
                    <p>All steps completed successfully.</p>
                    ${data.screenshots ? `
                        <div class="screenshots">
                            <h4>Screenshots:</h4>
                            <ul>
                                ${data.screenshots.map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            results.innerHTML = `
                <div class="error">
                    <h3>❌ Test Failed</h3>
                    <p>${data.errors.join('<br>')}</p>
                    ${data.screenshots ? `
                        <div class="screenshots">
                            <h4>Error Screenshots:</h4>
                            <ul>
                                ${data.screenshots.map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        results.style.display = 'block';
    } catch (error) {
        results.innerHTML = `
            <div class="error">
                <h3>❌ Error:</h3>
                <p>${error.message}</p>
            </div>
        `;
        results.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
});

// Set up event delegation for scenario buttons
document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', (event) => {
        const button = event.target.closest('.try-it-btn');
        if (button) {
            console.log('Scenario button clicked');
            const scenarioData = button.getAttribute('data-scenario');
            if (scenarioData) {
                event.preventDefault();
                console.log('Found scenario data:', scenarioData);
                loadCustomScenario(scenarioData);
            }
        }
    });
});