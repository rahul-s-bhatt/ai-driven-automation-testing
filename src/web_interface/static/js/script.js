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
        showSection(document.querySelector('button[onclick="showSection(this, \'test-runner\')"]'), 'test-runner');
        testSteps.value = examples[type];
    }
}

// Handle analyze form submission
document.getElementById('analyzeForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const analyzing = document.getElementById('analyzing');
    const results = document.getElementById('analysis-results');
    
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
            // Update structure info with metrics
            const structureInfo = document.querySelector('.structure-info');
            structureInfo.innerHTML = `
                <div class="structure-item">
                    <h4>Forms</h4>
                    <p>${data.analysis.structure.forms.length} detected</p>
                    <small>${data.analysis.structure.forms.reduce((acc, form) => acc + form.inputs.length, 0)} total inputs</small>
                </div>
                <div class="structure-item">
                    <h4>Navigation</h4>
                    <p>${data.analysis.structure.navigation.length} elements</p>
                    <small>${data.analysis.structure.navigation.reduce((acc, nav) => acc + nav.items.length, 0)} total links</small>
                </div>
                <div class="structure-item">
                    <h4>Dynamic Content</h4>
                    <p class="${data.analysis.structure.dynamic_content.infinite_scroll || data.analysis.structure.dynamic_content.load_more ? 'feature-detected' : 'feature-not-detected'}">
                        ${data.analysis.structure.dynamic_content.infinite_scroll ? '✓ Infinite Scroll' : ''}
                        ${data.analysis.structure.dynamic_content.load_more ? '✓ Load More' : ''}
                        ${!data.analysis.structure.dynamic_content.infinite_scroll && !data.analysis.structure.dynamic_content.load_more ? '✗ Not Detected' : ''}
                    </p>
                </div>
                <div class="structure-item">
                    <h4>Page Metrics</h4>
                    <p>Load Time: ${data.analysis.structure.page_metrics.load_time}s</p>
                    <div class="metrics-details">
                        <small>Images: ${data.analysis.structure.page_metrics.elements.images}</small>
                        <small>Scripts: ${data.analysis.structure.page_metrics.elements.scripts}</small>
                        <small>Styles: ${data.analysis.structure.page_metrics.elements.styles}</small>
                    </div>
                </div>
            `;
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

// Handle scraping form submission
document.getElementById('scrapingForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const loading = document.getElementById('scraping-loading');
    const results = document.getElementById('scraping-results');
    
    loading.style.display = 'block';
    results.style.display = 'none';
    
    try {
        const response = await fetch('/analyze_scraping', {
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
            // Update tag statistics
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

            // Update recommended selectors
            const selectors = document.getElementById('recommended-selectors');
            if (selectors) {
                selectors.innerHTML = data.analysis.recommended_selectors
                    .map(rec => `
                        <div class="selector-card">
                            <div class="selector-purpose">${rec.purpose}</div>
                            <code class="selector-code">${rec.selector}</code>
                            <div class="selector-note">${rec.note}</div>
                            <button class="copy-btn" onclick="copyToClipboard('${rec.selector}')">
                                Copy Selector
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
        loading.style.display = 'none';
    }
});

// Handle test form submission
document.getElementById('testForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
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

// Navigation handling is in the HTML template