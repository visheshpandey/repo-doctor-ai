document.addEventListener('DOMContentLoaded', () => {
    // Determine base URL dynamically (handles localhost and production)
    const API_BASE = window.location.origin;

    const form = document.getElementById('analyze-form');
    const input = document.getElementById('repo-url');
    const submitBtn = document.getElementById('submit-btn');
    
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');
    const reportView = document.getElementById('report-view');
    const markdownContent = document.getElementById('markdown-content');
    
    // Select elements that must be hidden on reset
    const panels = [loadingState, errorState, reportView];

    // Theme logic
    const themeToggle = document.getElementById('theme-toggle');
    const root = document.documentElement;

    function toggleTheme() {
        const currentTheme = root.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', newTheme);
        themeToggle.textContent = newTheme === 'dark' ? '🌓' : '☀️';
        localStorage.setItem('repodoctor-theme', newTheme);
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('repodoctor-theme');
    if (savedTheme) {
        root.setAttribute('data-theme', savedTheme);
        themeToggle.textContent = savedTheme === 'dark' ? '🌓' : '☀️';
    }

    themeToggle.addEventListener('click', toggleTheme);

    function hideAllPanels() {
        panels.forEach(p => p.classList.add('hidden'));
    }

    async function pollReport(reportId) {
        try {
            const response = await fetch(`${API_BASE}/report/${reportId}`);
            
            if (response.status === 200) {
                const markdownText = await response.text();
                hideAllPanels();
                
                // Parse markdown using Marked.js safely
                markdownContent.innerHTML = marked.parse(markdownText);
                reportView.classList.remove('hidden');
                submitBtn.disabled = false;
            } else if (response.status === 404) {
                // Not ready yet, keep polling
                setTimeout(() => pollReport(reportId), 2000);
            } else {
                throw new Error("Unexpected response from server.");
            }
        } catch (error) {
            showError("Failed to fetch report", error.message);
        }
    }

    function showError(title, message) {
        hideAllPanels();
        document.getElementById('error-title').textContent = title;
        document.getElementById('error-message').textContent = message;
        errorState.classList.remove('hidden');
        submitBtn.disabled = false;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const repoUrl = input.value.trim();
        if (!repoUrl) return;

        // Reset UI
        hideAllPanels();
        submitBtn.disabled = true;
        loadingState.classList.remove('hidden');

        try {
            // Initiate Analysis
            const initResponse = await fetch(`${API_BASE}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ repo_url: repoUrl })
            });

            if (!initResponse.ok) {
                const errData = await initResponse.json();
                throw new Error(errData.detail || "Server returned an error");
            }

            const data = await initResponse.json();
            const reportId = data.report_id;

            if (reportId) {
                // Begin polling
                setTimeout(() => pollReport(reportId), 2000);
            } else {
                throw new Error("No report ID returned from server.");
            }

        } catch (error) {
            showError("Connection Error", error.message);
        }
    });
});
