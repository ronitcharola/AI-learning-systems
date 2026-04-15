// SPA Router and Core UI Logic

class App {
    constructor() {
        this.root = document.getElementById('root');
        this.theme = localStorage.getItem('theme') || 'dark';
        this.applyTheme();
        
        // Auto-login flow
        if (window.api && window.api.token) {
            this.renderAppView();
            this.loadDashboardData();
        } else {
            this.renderAuthView();
        }
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
    }
    
    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        this.applyTheme();
        localStorage.setItem('theme', this.theme);
        
        const icon = document.getElementById('theme-icon');
        if (icon) icon.className = `fa-solid ${this.theme === 'dark' ? 'fa-sun' : 'fa-moon'}`;
    }

    logout() {
        window.api.logout();
        this.renderAuthView();
        this.showToast("Logged out successfully.", "success");
    }

    renderAuthView() {
        this.root.innerHTML = `
            <div class="auth-layout">
                <div class="card auth-card animate-fade-in">
                    <h1 class="auth-title">AI Productivity OS</h1>
                    <p style="color: var(--text-secondary); margin-bottom: 2rem;">Welcome back, let's get things done.</p>
                    <form id="login-form">
                        <div class="form-group">
                            <label>Email Address</label>
                            <input type="email" id="emailInput" class="form-control" value="test@example.com" required>
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" id="passwordInput" class="form-control" value="password" required>
                        </div>
                        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 0.5rem;">Log In</button>
                        <p style="margin-top: 1.5rem; font-size: 0.85rem;">Don't have an account? <br><a href="#" id="dev-signup" style="color: var(--accent-primary); font-weight: bold;">Create mock test user</a></p>
                    </form>
                </div>
            </div>
        `;
        
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Authenticating...';
            btn.disabled = true;

            const email = document.getElementById('emailInput').value;
            const pass = document.getElementById('passwordInput').value;
            try {
                const data = await window.api.login(email, pass);
                window.api.setToken(data.token, data.user);
                this.showToast("Logged in successfully!", "success");
                this.renderAppView();
                this.loadDashboardData();
            } catch (err) {
                btn.innerHTML = 'Log In';
                btn.disabled = false;
                this.showToast(err.message, "warning");
            }
        });

        document.getElementById('dev-signup').addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await window.api.signup('test@example.com', 'password', 'Test User');
                this.showToast("Mock user created! Please click Log In.", "success");
            } catch (err) {
                this.showToast(err.message, "warning");
            }
        });
    }

    renderAppView() {
        const themeIconClass = this.theme === 'dark' ? 'fa-sun' : 'fa-moon';
        const userName = window.api.user ? window.api.user.name : 'U';
        const intial = userName.charAt(0).toUpperCase();

        this.root.innerHTML = `
            <div class="app-layout">
                <nav class="sidebar">
                    <div class="sidebar-header">
                        <i class="fa-solid fa-bolt" style="font-size: 1.5rem;"></i> AI OS
                    </div>
                    <ul class="nav-links">
                        <li class="nav-item active"><i class="fa-solid fa-chart-pie"></i> Dashboard</li>
                        <li class="nav-item" onclick="app.showToast('Tasks view coming soon!')"><i class="fa-solid fa-list-check"></i> Tasks</li>
                        <li class="nav-item" onclick="app.showToast('Planner coming soon!')"><i class="fa-solid fa-calendar-alt"></i> AI Planner</li>
                        <li class="nav-item" onclick="app.showToast('Settings coming soon!')"><i class="fa-solid fa-gear"></i> Settings</li>
                        <li class="nav-item" style="color: var(--danger); margin-top: auto;" onclick="app.logout()"><i class="fa-solid fa-sign-out-alt"></i> Logout</li>
                    </ul>
                </nav>
                
                <div class="main-wrapper">
                    <header class="topbar">
                        <h2 style="font-size: 1.25rem;">Dashboard Overview</h2>
                        <div style="display: flex; gap: 1rem; align-items: center;">
                            <button class="theme-toggle" onclick="app.toggleTheme()">
                                <i id="theme-icon" class="fa-solid ${themeIconClass}"></i>
                            </button>
                            <div style="width: 40px; height: 40px; background: var(--accent-secondary); box-shadow: var(--shadow-sm); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">
                                ${intial}
                            </div>
                        </div>
                    </header>
                    
                    <main class="page-content" id="page-content">
                        <!-- Polished Skeleton Loaders while fetching API Data -->
                        <div class="grid-3 animate-fade-in">
                            <div class="card"><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-block"></div></div>
                            <div class="card"><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-block"></div></div>
                            <div class="card"><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-block"></div></div>
                        </div>
                        <div class="grid-2-1 animate-fade-in delay-1">
                            <div class="card" style="min-height: 300px;"><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-block" style="height: 200px;"></div></div>
                            <div class="card"><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-block" style="margin-top: 2rem;"></div></div>
                        </div>
                    </main>
                </div>
            </div>
        `;
    }

    async loadDashboardData() {
        try {
            const insights = await window.api.getInsights();
            const recs = await window.api.getRecommendations();

            // Simulate slight network delay just to show off the pretty skeletons
            setTimeout(() => {
                this.renderDashboardContent(insights, recs);
                this.renderChart(insights.trends);
            }, 600);
            
            try { await window.api.generateSchedule(); } catch(e){}

        } catch (error) {
            const main = document.getElementById('page-content');
            if (main) {
                main.innerHTML = `
                    <div style="text-align: center; margin-top: 3rem; color: var(--danger);" class="animate-fade-in">
                        <i class="fa-solid fa-triangle-exclamation fa-2x"></i>
                        <p style="margin-top: 1rem;">Failed to connect to AI Backend.</br>Please ensure the Flask server is running on port 5000.</p>
                        <button class="btn btn-primary" style="margin-top: 1rem;" onclick="app.loadDashboardData()"><i class="fa-solid fa-rotate-right"></i> Retry Connection</button>
                    </div>
                `;
            }
        }
    }

    renderDashboardContent(insights, recs) {
        const main = document.getElementById('page-content');
        if(!main) return;

        const nextTaskHtml = recs.next_task 
            ? `
                <strong style="font-size: 1.05rem;">${recs.next_task.title}</strong>
                <p style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.75rem;">
                    <i class="fa-solid fa-clock" style="margin-right: 0.25rem;"></i> Est: ${recs.next_task.estimated_time} mins • Priority: <span style="text-transform: capitalize;">${recs.next_task.priority}</span>
                </p>
                <button class="btn btn-primary" style="width: 100%; margin-top: 1.5rem;" onclick="app.showToast('Focus session started!', 'success')">
                    <i class="fa-solid fa-play"></i> Start Focus Session
                </button>
            `
            : `
                <strong style="font-size: 1.05rem;">No Pending Tasks</strong>
                <p style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.75rem;">
                    Time to relax or plan your week.
                </p>
                <button class="btn btn-primary" style="width: 100%; margin-top: 1.5rem;" onclick="app.showToast('Add task functionality coming soon!', 'info')">
                    <i class="fa-solid fa-plus"></i> Add New Task
                </button>
            `;

        const warningHtml = recs.warnings && recs.warnings.length > 0
            ? `<div class="animate-fade-in" style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid var(--warning); padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1.5rem; color: var(--warning);">
                <strong><i class="fa-solid fa-triangle-exclamation"></i> AI Alert:</strong> ${recs.warnings[0]}
               </div>`
            : '';

        main.innerHTML = `
            ${warningHtml}
            <div class="grid-3 animate-fade-in">
                <div class="card">
                    <h3>Productivity Score</h3>
                    <div class="stat-value" style="color: var(--accent-primary);">${insights.productivity_score}%</div>
                    <p style="font-size: 0.85rem; color: var(--success); margin-top: 0.5rem;"><i class="fa-solid fa-arrow-up"></i> ML Tracking active</p>
                </div>
                <div class="card">
                    <h3>Focus Hours</h3>
                    <div class="stat-value" style="color: var(--accent-secondary);">${insights.focus_hours}h</div>
                    <p style="font-size: 0.85rem; color: var(--text-tertiary); margin-top: 0.5rem;">Time spent on tasks targeting deep work</p>
                </div>
                <div class="card">
                    <h3>Tasks Pending</h3>
                    <div class="stat-value" style="color: var(--warning);">${insights.total_tasks - insights.completed_tasks}</div>
                    <p style="font-size: 0.85rem; color: var(--success); margin-top: 0.5rem;">${insights.completed_tasks} completed successfully</p>
                </div>
            </div>
            
            <div class="grid-2-1 animate-fade-in delay-1">
                <div class="card" style="min-height: 300px;">
                    <h3 style="margin-bottom: 1rem;">Performance Trend</h3>
                    <div style="height: 250px; position: relative;">
                        <canvas id="trendChart"></canvas>
                    </div>
                </div>
                
                <div class="card" style="border: 1px solid var(--accent-primary);">
                    <h3><i class="fa-solid fa-wand-magic-sparkles" style="color: var(--accent-primary);"></i> Recommended Next Task</h3>
                    <div style="margin-top: 1.5rem; padding: 1.25rem; background: var(--bg-primary); border-radius: var(--radius-md); border-left: 4px solid var(--accent-primary);">
                        ${nextTaskHtml}
                    </div>
                    
                    <p style="font-size: 0.8rem; text-align: center; color: var(--text-tertiary); margin-top: 1rem;">
                        <i class="fa-solid fa-bolt" style="color: var(--warning);"></i> Optimal time block: ${recs.optimal_work_time || 'N/A'}
                    </p>
                </div>
            </div>
            
            <div class="card animate-fade-in delay-2" style="margin-top: 1.5rem; background: var(--bg-tertiary);">
                 <h3 style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 50%; background: var(--accent-primary); color: white;">
                        <i class="fa-solid fa-robot"></i>
                    </span>
                    Ask your AI Coach
                 </h3>
                 <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                    <input type="text" id="coach-input" class="form-control" placeholder="E.g., Why am I not productive today?">
                    <button class="btn btn-primary" onclick="app.askCoach()">Ask <i class="fa-solid fa-paper-plane"></i></button>
                 </div>
                 <p id="coach-reply" style="margin-top: 1rem; color: var(--accent-primary); font-style: italic;"></p>
            </div>
        `;
    }

    async askCoach() {
        const input = document.getElementById('coach-input');
        const replyTag = document.getElementById('coach-reply');
        if(!input.value.trim()) return;
        
        replyTag.style.opacity = 0;
        setTimeout(() => {
            replyTag.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing...';
            replyTag.style.opacity = 1;
        }, 150);
        
        try {
            const res = await window.api.askCoach(input.value);
            setTimeout(() => {
                replyTag.innerHTML = `<i class="fa-solid fa-message"></i> Coach: "${res.reply}"`;
            }, 500); // UI delay for 'thinking' feel
            input.value = '';
        } catch (err) {
            replyTag.innerHTML = `<span style="color: var(--danger)"><i class="fa-solid fa-triangle-exclamation"></i> Error connecting to AI coach.</span>`;
        }
    }

    renderChart(trends) {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;
        
        const labels = trends.map(t => t.day);
        const data = trends.map(t => t.score);
        
        const style = getComputedStyle(document.documentElement);
        const primaryColor = style.getPropertyValue('--accent-primary').trim();
        const gridColor = style.getPropertyValue('--border-color').trim();
        const textColor = style.getPropertyValue('--text-secondary').trim();

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Productivity',
                    data: data,
                    borderColor: primaryColor,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: primaryColor,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: style.getPropertyValue('--bg-secondary').trim(),
                        titleColor: style.getPropertyValue('--text-primary').trim(),
                        bodyColor: style.getPropertyValue('--text-secondary').trim(),
                        borderColor: gridColor,
                        borderWidth: 1,
                        padding: 12,
                        boxPadding: 6,
                        usePointStyle: true,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: textColor }
                    }
                }
            }
        });
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if(!container) return;
        
        const toast = document.createElement('div');
        toast.className = 'toast';
        
        let icon = 'fa-info-circle';
        let color = 'var(--accent-primary)';
        if(type === 'success') { icon = 'fa-check-circle'; color = 'var(--success)'; }
        if(type === 'warning') { icon = 'fa-exclamation-triangle'; color = 'var(--warning)'; }
        
        toast.innerHTML = `<i class="fa-solid ${icon}" style="color: ${color}; margin-right: 0.75rem; font-size: 1.1rem;"></i> ${message}`;
        container.appendChild(toast);
        
        setTimeout(() => toast.style.opacity = '1', 50); // slight delay to trigger CSS transition
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
}

// Ensure execution waits until DOM is ready
window.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
