// Initialize navigation functionality
document.addEventListener('DOMContentLoaded', () => {
    // Set up navigation click handlers
    document.querySelectorAll('.nav-item').forEach(button => {
        button.addEventListener('click', () => {
            const sectionId = button.getAttribute('data-section');
            if (sectionId) {
                // Hide all sections
                document.querySelectorAll('.tutorial-section').forEach(section => {
                    section.classList.remove('active');
                });

                // Remove active class from all nav items
                document.querySelectorAll('.nav-item').forEach(btn => {
                    btn.classList.remove('active');
                });

                // Show selected section and activate button
                const targetSection = document.getElementById(sectionId);
                if (targetSection) {
                    targetSection.classList.add('active');
                }
                button.classList.add('active');
            }
        });
    });

    // Show initial section
    const initialButton = document.querySelector('.nav-item[data-section="getting-started"]');
    if (initialButton) {
        initialButton.click();
    }
});

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
    if (!examples[type]) return;
    
    const testSteps = document.getElementById('test_steps');
    if (!testSteps) return;

    // Switch to test runner section and set example
    const testRunnerNav = document.querySelector('.nav-item[data-section="test-runner"]');
    if (testRunnerNav) {
        testRunnerNav.click();
        testSteps.value = examples[type];
    }
}

// Handle analyze form submission
const analyzeForm = document.getElementById('analyzeForm');
if (analyzeForm) {
    analyzeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
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
                    url: e.target.url.value
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const structureInfo = document.querySelector('.structure-info');
                if (structureInfo) {
                    structureInfo.innerHTML = `
                        <div class="structure-item">
                            <h4>Forms</h4>
                            <p>${data.analysis.structure.forms.length} detected</p>
                        </div>
                        <div class="structure-item">
                            <h4>Navigation</h4>
                            <p>${data.analysis.structure.navigation.length} elements</p>
                        </div>
                        <div class="structure-item">
                            <h4>Dynamic Content</h4>
                            <p class="${data.analysis.structure.dynamic_content.infinite_scroll || data.analysis.structure.dynamic_content.load_more ? 'feature-detected' : 'feature-not-detected'}">
                                ${data.analysis.structure.dynamic_content.infinite_scroll ? '✓ Infinite Scroll' : ''}
                                ${data.analysis.structure.dynamic_content.load_more ? '✓ Load More' : ''}
                                ${!data.analysis.structure.dynamic_content.infinite_scroll && !data.analysis.structure.dynamic_content.load_more ? '✗ Not Detected' : ''}
                            </p>
                        </div>
                    `;
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
}

// Handle scraping form submission
const scrapingForm = document.getElementById('scrapingForm');
if (scrapingForm) {
    scrapingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const loading = document.getElementById('scraping-loading');
        const results = document.getElementById('scraping-results');
        
        if (!loading || !results) return;
        
        loading.style.display = 'block';
        results.style.display = 'none';
        
        try {
            const response = await fetch('/analyze_scraping', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: e.target.url.value
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const tagStats = document.getElementById('tag-stats');
                if (tagStats) {
                    tagStats.innerHTML = Object.entries(data.analysis.page_structure.tags)
                        .map(([tag, count]) => `
                            <div class="tag-item">
                                <span class="tag-name">${tag}</span>
                                <span class="tag-count">${count}</span>
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
            loading.style.display = 'none';
        }
    });
}

// Handle test form submission
const testForm = document.getElementById('testForm');
if (testForm) {
    testForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        
        if (!loading || !results) return;
        
        loading.style.display = 'block';
        results.style.display = 'none';
        
        try {
            const steps = document.getElementById('test_steps')?.value
                .split('\n')
                .filter(step => step.trim())
                .map(step => `      - ${step.trim()}`) || [];
            
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
                    url: e.target.url.value,
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
}

// Copy to clipboard utility
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        const notification = document.createElement('div');
        notification.className = 'copy-notification';
        notification.textContent = 'Copied!';
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 2000);
    });
}