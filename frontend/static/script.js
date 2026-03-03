const API_BASE = '';  // empty for same origin

let token = localStorage.getItem('token');
let currentView = token ? 'dashboard' : 'login';

const app = document.getElementById('app');

function render() {
    if (currentView === 'login') {
        renderLogin();
    } else if (currentView === 'register') {
        renderRegister();
    } else if (currentView === 'dashboard') {
        renderDashboard();
    }
}

// ========== AUTH VIEWS ==========
function renderLogin() {
    app.innerHTML = `
        <div class="auth-container glass-card">
            <h1>🚀 Burnout Sentinel</h1>
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <input type="email" id="email" class="input-neon" placeholder="Email" />
                <input type="password" id="password" class="input-neon" placeholder="Password" />
                <button class="btn-neon" onclick="handleLogin()">Login</button>
                <p style="text-align: center;">New here? <span class="auth-switch" onclick="switchView('register')">Create account</span></p>
            </div>
        </div>
    `;
}

function renderRegister() {
    app.innerHTML = `
        <div class="auth-container glass-card">
            <h1>✨ Join the Future</h1>
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <input type="email" id="email" class="input-neon" placeholder="Email" />
                <input type="password" id="password" class="input-neon" placeholder="Password" />
                <button class="btn-neon" onclick="handleRegister()">Register</button>
                <p style="text-align: center;">Already have an account? <span class="auth-switch" onclick="switchView('login')">Login</span></p>
            </div>
        </div>
    `;
}

function switchView(view) {
    currentView = view;
    render();
}

async function handleLogin() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const res = await fetch(`${API_BASE}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.ok) {
        localStorage.setItem('token', data.token);
        token = data.token;
        currentView = 'dashboard';
        render();
    } else {
        alert('Login failed: ' + data.error);
    }
}

async function handleRegister() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const res = await fetch(`${API_BASE}/api/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.ok) {
        localStorage.setItem('token', data.token);
        token = data.token;
        currentView = 'dashboard';
        render();
    } else {
        alert('Registration failed: ' + data.error);
    }
}

// ========== DASHBOARD ==========
function renderDashboard() {
    app.innerHTML = `
        <div class="dashboard">
            <div class="dashboard-header glass-card">
                <div class="logo">🧠 Burnout Sentinel</div>
                <div style="display: flex; gap: 15px;">
                    <input type="text" id="github-username" class="input-neon" placeholder="GitHub username" style="width: 250px;" />
                    <button class="btn-neon" onclick="analyze()">Analyze</button>
                </div>
                <button class="btn-neon" onclick="logout()" style="background: linear-gradient(45deg, #ff416c, #ff4b2b);">Logout</button>
            </div>

            <div id="results" style="display: none;">
                <div class="meter-container glass-card" style="padding: 30px;">
                    <h2 style="font-weight: 300; margin-bottom: 20px;">Burnout Risk Meter</h2>
                    <div class="meter" id="meter">
                        <div class="meter-inner">
                            <span id="burnout-level">-</span>
                            <span id="confidence" style="font-size: 16px;"></span>
                        </div>
                    </div>
                </div>

                <div class="charts-grid">
                    <div class="chart-card">
                        <h3>📆 Weekly Commit Frequency</h3>
                        <canvas id="commitChart"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>📈 Sentiment Trend (Last 20 commits)</h3>
                        <canvas id="sentimentChart"></canvas>
                    </div>
                </div>

                <div class="recommendation-panel" id="recommendation"></div>
            </div>

            <div class="footer">
                <p>© 2026 Burnout Sentinel – AI-Powered Developer Wellness</p>
                <p>
                    <a href="#">Privacy</a> • <a href="#">Terms</a> • <a href="#">Contact</a>
                </p>
            </div>
        </div>
    `;
}

let commitChart, sentimentChart;

async function analyze() {
    const username = document.getElementById('github-username').value;
    if (!username) return alert('Enter a GitHub username');

    const res = await fetch(`${API_BASE}/api/analyze?github_username=${username}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    if (!res.ok) {
        alert('Analysis failed: ' + data.error);
        return;
    }

    document.getElementById('results').style.display = 'block';
    document.getElementById('burnout-level').innerText = data.burnout_level;
    document.getElementById('confidence').innerText = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
    document.getElementById('recommendation').innerText = data.recommendation;

    // Update meter color
    const meter = document.getElementById('meter');
    if (data.burnout_level === 'Low') meter.style.background = 'conic-gradient(#4caf50 0deg, #4caf50 360deg)';
    else if (data.burnout_level === 'Medium') meter.style.background = 'conic-gradient(#ff9800 0deg, #ff9800 360deg)';
    else meter.style.background = 'conic-gradient(#f44336 0deg, #f44336 360deg)';

    // Prepare data for charts
    const commitDates = data.commit_dates;
    // Group by week for commit frequency
    const weeks = {};
    commitDates.forEach(date => {
        const week = getWeekNumber(new Date(date));
        weeks[week] = (weeks[week] || 0) + 1;
    });
    const weekLabels = Object.keys(weeks).sort();
    const commitCounts = weekLabels.map(w => weeks[w]);

    // Sentiment per commit (limit to 20 for readability)
    const sentiments = data.sentiment_scores.slice(0, 20);
    const commitLabels = commitDates.slice(0, 20).map((d, i) => `${d} #${i+1}`);

    // Destroy existing charts if any
    if (commitChart) commitChart.destroy();
    if (sentimentChart) sentimentChart.destroy();

    // Commit chart
    const ctx1 = document.getElementById('commitChart').getContext('2d');
    commitChart = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: weekLabels,
            datasets: [{
                label: 'Commits per week',
                data: commitCounts,
                backgroundColor: 'rgba(43, 158, 255, 0.7)',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#a0a0c0' } }
            },
            scales: {
                y: { ticks: { color: '#a0a0c0' } },
                x: { ticks: { color: '#a0a0c0' } }
            }
        }
    });

    // Sentiment chart
    const ctx2 = document.getElementById('sentimentChart').getContext('2d');
    sentimentChart = new Chart(ctx2, {
        type: 'line',
        data: {
            labels: commitLabels,
            datasets: [{
                label: 'Sentiment polarity',
                data: sentiments,
                borderColor: '#0ef0f0',
                backgroundColor: 'rgba(14, 240, 240, 0.1)',
                tension: 0.2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#a0a0c0' } }
            },
            scales: {
                y: { ticks: { color: '#a0a0c0' } },
                x: { ticks: { color: '#a0a0c0', maxRotation: 45, minRotation: 45 } }
            }
        }
    });
}

function getWeekNumber(d) {
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    return `${d.getUTCFullYear()}-W${weekNo}`;
}

function logout() {
    localStorage.removeItem('token');
    token = null;
    currentView = 'login';
    render();
}

// Initial render
render();