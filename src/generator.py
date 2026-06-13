import os
import json
from jinja2 import Template

TEMPLATE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Radar AI - Matches Dashboard</title>
    <!-- Inter Font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: #0b0f19;
            --bg-gradient: radial-gradient(circle at 50% 50%, #0f1626, #07090e);
            --card-bg: rgba(22, 28, 45, 0.4);
            --card-border: rgba(255, 255, 255, 0.08);
            --card-hover-bg: rgba(28, 38, 60, 0.6);
            --card-hover-border: rgba(255, 255, 255, 0.15);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
            --accent-emerald: #10b981;
            --accent-emerald-glow: rgba(16, 185, 129, 0.15);
            --accent-amber: #f59e0b;
            --accent-amber-glow: rgba(245, 158, 11, 0.15);
            --accent-rose: #f43f5e;
            --accent-rose-glow: rgba(244, 63, 94, 0.15);
            --accent-blue: #3b82f6;
            --accent-blue-glow: rgba(59, 130, 246, 0.15);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-color);
            background-image: var(--bg-gradient);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
        }

        header {
            padding: 2rem 4rem 1.5rem 4rem;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
            background: rgba(11, 15, 25, 0.7);
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .header-title-container h1 {
            font-size: 1.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #3b82f6, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .header-title-container p {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: 0.2rem;
        }

        .stats-summary {
            display: flex;
            gap: 1.5rem;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            text-align: center;
            min-width: 100px;
        }

        .stat-num {
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .stat-num.emerald { color: var(--accent-emerald); }
        .stat-num.amber { color: var(--accent-amber); }
        .stat-num.blue { color: var(--accent-blue); }

        .stat-label {
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 0.1rem;
        }

        .main-container {
            display: flex;
            flex: 1;
            padding: 2rem 4rem;
            gap: 2rem;
            max-width: 1800px;
            width: 100%;
            margin: 0 auto;
        }

        .sidebar {
            width: 320px;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .search-box {
            position: relative;
        }

        .search-box input {
            width: 100%;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1rem 1rem 1rem 2.8rem;
            color: var(--text-primary);
            font-family: inherit;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.3s ease;
        }

        .search-box input:focus {
            border-color: var(--accent-blue);
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.15);
            background: rgba(22, 28, 45, 0.6);
        }

        .search-icon {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            width: 18px;
            height: 18px;
            pointer-events: none;
        }

        .filter-section {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .filter-title {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 0.5rem;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .filter-btn {
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-secondary);
            padding: 0.6rem 1rem;
            border-radius: 8px;
            text-align: left;
            font-family: inherit;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .filter-btn:hover {
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-primary);
        }

        .filter-btn.active {
            background: rgba(59, 130, 246, 0.15);
            border-color: rgba(59, 130, 246, 0.3);
            color: var(--text-primary);
            font-weight: 600;
        }

        .filter-badge {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-secondary);
            padding: 0.15rem 0.5rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .filter-btn.active .filter-badge {
            background: var(--accent-blue);
            color: white;
        }

        .content-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .jobs-list {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.25rem;
        }

        .job-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .job-card:hover {
            transform: translateY(-3px);
            border-color: var(--card-hover-border);
            background: var(--card-hover-bg);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }

        .job-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
        }

        .job-details-brief {
            flex: 1;
        }

        .job-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.3;
        }

        .company-name {
            font-size: 0.95rem;
            color: var(--accent-blue);
            font-weight: 500;
            margin-top: 0.25rem;
        }

        .score-badge-container {
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }

        .score-pill {
            padding: 0.5rem 1rem;
            border-radius: 30px;
            font-weight: 800;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }

        .score-pill.high {
            background: var(--accent-emerald-glow);
            color: var(--accent-emerald);
            border-color: rgba(16, 185, 129, 0.3);
        }

        .score-pill.medium {
            background: var(--accent-amber-glow);
            color: var(--accent-amber);
            border-color: rgba(245, 158, 11, 0.3);
        }

        .score-pill.low {
            background: var(--accent-rose-glow);
            color: var(--accent-rose);
            border-color: rgba(244, 63, 94, 0.3);
        }

        .score-label {
            font-size: 0.7rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            margin-top: 0.25rem;
            letter-spacing: 0.5px;
        }

        .job-meta-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            align-items: center;
        }

        .meta-tag {
            font-size: 0.8rem;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
            border: 1px solid rgba(255, 255, 255, 0.03);
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }

        .meta-tag.location {
            color: #60a5fa;
            background: rgba(96, 165, 250, 0.07);
        }

        .meta-tag.job-type {
            color: #c084fc;
            background: rgba(192, 132, 252, 0.07);
        }

        .meta-tag.experience {
            color: #f472b6;
            background: rgba(244, 114, 182, 0.07);
        }

        .job-explanation {
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.5;
            background: rgba(255, 255, 255, 0.02);
            padding: 0.75rem 1rem;
            border-radius: 10px;
            border-left: 3px solid var(--text-muted);
        }

        .job-card.high-match .job-explanation {
            border-left-color: var(--accent-emerald);
        }
        .job-card.medium-match .job-explanation {
            border-left-color: var(--accent-amber);
        }
        .job-card.low-match .job-explanation {
            border-left-color: var(--accent-rose);
        }

        .skills-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .skill-badge {
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-secondary);
            border-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.02);
        }

        .job-card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 0.75rem;
            margin-top: 0.25rem;
        }

        .received-date {
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .action-buttons {
            display: flex;
            gap: 0.5rem;
        }

        .btn {
            font-family: inherit;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            outline: none;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        .btn-apply {
            background: var(--accent-blue);
            color: white;
            border: 1px solid transparent;
        }

        .btn-apply:hover {
            background: #2563eb;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.4);
        }

        .btn-status-apply {
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--card-border);
        }

        .btn-status-apply:hover {
            background: rgba(16, 185, 129, 0.1);
            color: var(--accent-emerald);
            border-color: rgba(16, 185, 129, 0.3);
        }

        .btn-status-reject {
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--card-border);
        }

        .btn-status-reject:hover {
            background: rgba(244, 63, 94, 0.1);
            color: var(--accent-rose);
            border-color: rgba(244, 63, 94, 0.3);
        }

        .status-indicator-pill {
            font-size: 0.75rem;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .status-indicator-pill.applied {
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .status-indicator-pill.rejected {
            background: rgba(244, 63, 94, 0.15);
            color: var(--accent-rose);
            border: 1px solid rgba(244, 63, 94, 0.3);
        }

        .status-indicator-pill.new {
            background: rgba(59, 130, 246, 0.15);
            color: var(--accent-blue);
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        /* Slide-over details panel */
        .details-panel-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            z-index: 100;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }

        .details-panel-backdrop.open {
            opacity: 1;
            pointer-events: auto;
        }

        .details-panel {
            position: fixed;
            top: 0;
            right: -600px;
            width: 600px;
            max-width: 100vw;
            height: 100vh;
            background: #0e1322;
            border-left: 1px solid var(--card-border);
            z-index: 101;
            box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
            transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
        }

        .details-panel.open {
            right: 0;
        }

        .panel-header {
            padding: 1.5rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .panel-close-btn {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 1.5rem;
            cursor: pointer;
            transition: color 0.2s;
        }

        .panel-close-btn:hover {
            color: var(--text-primary);
        }

        .panel-content {
            padding: 2rem;
            overflow-y: auto;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .panel-section-title {
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--accent-blue);
            margin-bottom: 0.5rem;
        }

        .email-body-container {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 1.25rem;
            font-family: inherit;
            font-size: 0.9rem;
            line-height: 1.6;
            color: #d1d5db;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }

        .email-body-container a {
            color: var(--accent-blue);
            text-decoration: underline;
        }

        .toast {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: rgba(14, 19, 34, 0.9);
            border: 1px solid var(--accent-blue);
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            z-index: 200;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            backdrop-filter: blur(10px);
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .toast.show {
            transform: translateX(-50%) translateY(0);
        }

        .toast-icon {
            color: var(--accent-emerald);
        }

        .no-jobs-state {
            grid-column: 1 / -1;
            text-align: center;
            padding: 4rem 2rem;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            color: var(--text-secondary);
        }

        .no-jobs-state h3 {
            font-size: 1.3rem;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }

        /* Responsive */
        @media (max-width: 1024px) {
            .main-container {
                flex-direction: column;
                padding: 1.5rem;
            }
            .sidebar {
                width: 100%;
            }
            header {
                padding: 1.5rem;
            }
        }
    </style>
</head>
<body>

    <header>
        <div class="header-title-container">
            <h1>Job Radar AI</h1>
            <p>Smart product management job email parsing & matching agent</p>
        </div>
        <div class="stats-summary">
            <div class="stat-card">
                <div class="stat-num blue" id="stat-total">0</div>
                <div class="stat-label">Total Parsed</div>
            </div>
            <div class="stat-card">
                <div class="stat-num emerald" id="stat-high">0</div>
                <div class="stat-label">High Match (8+)</div>
            </div>
            <div class="stat-card">
                <div class="stat-num amber" id="stat-applied">0</div>
                <div class="stat-label">Applied</div>
            </div>
        </div>
    </header>

    <div class="main-container">
        
        <!-- Sidebar filters -->
        <div class="sidebar">
            
            <div class="search-box">
                <!-- Simple SVG Search Icon -->
                <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
                <input type="text" id="search-input" placeholder="Search title, company, skills...">
            </div>

            <div class="filter-section">
                <div class="filter-title">Inbox Status</div>
                <div class="filter-group">
                    <button class="filter-btn active" data-filter="status" data-val="all">
                        <span>All Items</span> <span class="filter-badge" id="badge-status-all">0</span>
                    </button>
                    <button class="filter-btn" data-filter="status" data-val="new">
                        <span>New Matches</span> <span class="filter-badge" id="badge-status-new">0</span>
                    </button>
                    <button class="filter-btn" data-filter="status" data-val="applied">
                        <span>Applied</span> <span class="filter-badge" id="badge-status-applied">0</span>
                    </button>
                    <button class="filter-btn" data-filter="status" data-val="rejected">
                        <span>Rejected / Archived</span> <span class="filter-badge" id="badge-status-rejected">0</span>
                    </button>
                </div>

                <div class="filter-title">Match Quality</div>
                <div class="filter-group">
                    <button class="filter-btn active" data-filter="score" data-val="all">
                        <span>All Scores</span> <span class="filter-badge" id="badge-score-all">0</span>
                    </button>
                    <button class="filter-btn" data-filter="score" data-val="high">
                        <span>Strong Match (8+)</span> <span class="filter-badge" id="badge-score-high">0</span>
                    </button>
                    <button class="filter-btn" data-filter="score" data-val="medium">
                        <span>Medium Match (6-7)</span> <span class="filter-badge" id="badge-score-medium">0</span>
                    </button>
                    <button class="filter-btn" data-filter="score" data-val="low">
                        <span>Poor Match (<6)</span> <span class="filter-badge" id="badge-score-low">0</span>
                    </button>
                </div>
            </div>

        </div>

        <!-- Main content list -->
        <div class="content-area">
            <div class="jobs-list" id="jobs-list-container">
                <!-- Rendered dynamically -->
            </div>
        </div>

    </div>

    <!-- Side Slide-over Panel -->
    <div class="details-panel-backdrop" id="panel-backdrop"></div>
    <div class="details-panel" id="details-panel">
        <div class="panel-header">
            <div class="panel-title-area">
                <h2 id="panel-title" style="font-size: 1.4rem; font-weight: 800;">Job Title</h2>
                <div id="panel-company" style="color: var(--accent-blue); font-weight: 600; margin-top: 0.25rem;">Company Name</div>
            </div>
            <button class="panel-close-btn" id="panel-close-btn">&times;</button>
        </div>
        <div class="panel-content">
            <div>
                <div class="panel-section-title">Evaluation Analysis</div>
                <div id="panel-explanation" class="job-explanation" style="font-size: 0.95rem;">
                    Relevance evaluation from Gemini goes here.
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <div class="panel-section-title">Location & Type</div>
                    <div id="panel-location" style="font-size: 0.95rem; font-weight: 500;">Location details</div>
                </div>
                <div>
                    <div class="panel-section-title">Salary & Comp</div>
                    <div id="panel-salary" style="font-size: 0.95rem; font-weight: 500;">Salary details</div>
                </div>
            </div>

            <div>
                <div class="panel-section-title">Required Experience</div>
                <div id="panel-experience" style="font-size: 0.95rem; font-weight: 500;">Experience details</div>
            </div>

            <div>
                <div class="panel-section-title">Key Skills</div>
                <div id="panel-skills" class="skills-badges">
                    <!-- Badge elements -->
                </div>
            </div>

            <div>
                <div class="panel-section-title">Email Metadata</div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); background: rgba(255, 255, 255, 0.02); padding: 0.75rem; border-radius: 8px;">
                    <div style="margin-bottom: 0.25rem;"><strong>From:</strong> <span id="panel-meta-sender">sender@example.com</span></div>
                    <div style="margin-bottom: 0.25rem;"><strong>Date:</strong> <span id="panel-meta-date">Date</span></div>
                    <div><strong>Subject:</strong> <span id="panel-meta-subject">Subject</span></div>
                </div>
            </div>

            <div>
                <div class="panel-section-title">Cleaned Email Description</div>
                <div id="panel-email-body" class="email-body-container">
                    Full body contents...
                </div>
            </div>
        </div>
    </div>

    <!-- Toast container -->
    <div class="toast" id="toast">
        <svg class="toast-icon" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
        </svg>
        <span id="toast-message">Status updated successfully</span>
    </div>

    <script>
        // Injected data from generator.py
        const jobs = {{ jobs_json_raw }};
        
        let activeFilters = {
            status: 'all',
            score: 'all',
            search: ''
        };

        // Initialize App
        document.addEventListener('DOMContentLoaded', () => {
            renderDashboard();
            setupFilterListeners();
            setupSearchListener();
            setupPanelListeners();
        });

        function renderDashboard() {
            const container = document.getElementById('jobs-list-container');
            container.innerHTML = '';

            // Filter jobs
            const filteredJobs = jobs.filter(job => {
                // Status Filter
                if (activeFilters.status !== 'all' && job.status !== activeFilters.status) {
                    return false;
                }
                
                // Score Filter
                if (activeFilters.score !== 'all') {
                    if (activeFilters.score === 'high' && job.relevance_score < 8) return false;
                    if (activeFilters.score === 'medium' && (job.relevance_score < 6 || job.relevance_score > 7)) return false;
                    if (activeFilters.score === 'low' && job.relevance_score >= 6) return false;
                }

                // Search Filter
                if (activeFilters.search) {
                    const query = activeFilters.search.toLowerCase();
                    const titleMatch = job.job_title.toLowerCase().includes(query);
                    const companyMatch = job.company.toLowerCase().includes(query);
                    const explanationMatch = job.explanation.toLowerCase().includes(query);
                    const skillsMatch = job.skills.some(skill => skill.toLowerCase().includes(query));
                    if (!titleMatch && !companyMatch && !explanationMatch && !skillsMatch) return false;
                }

                return true;
            });

            // Update badges and stats
            updateStatsAndBadges();

            if (filteredJobs.length === 0) {
                container.innerHTML = `
                    <div class="no-jobs-state">
                        <h3>No Job Matches Found</h3>
                        <p>Try clearing your filters or running the email parsing client to retrieve new listings.</p>
                    </div>
                `;
                return;
            }

            // Render cards
            filteredJobs.forEach(job => {
                const card = document.createElement('div');
                card.className = `job-card ${getMatchClass(job.relevance_score)}-match`;
                card.setAttribute('data-id', job.id);
                
                // Set click event to open details (but exclude button clicks)
                card.addEventListener('click', (e) => {
                    if (!e.target.closest('.btn')) {
                        openJobDetails(job);
                    }
                });

                // Generate skills tags (up to 4)
                const skillsHtml = job.skills.slice(0, 4).map(skill => `<span class="skill-badge">${escapeHtml(skill)}</span>`).join('');
                
                // Action Buttons or status indicators
                let footerActions = '';
                if (job.status === 'new') {
                    footerActions = `
                        <div class="action-buttons">
                            <button class="btn btn-status-apply" onclick="updateStatus(${job.id}, 'applied')">
                                <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                </svg> Applied
                            </button>
                            <button class="btn btn-status-reject" onclick="updateStatus(${job.id}, 'rejected')">
                                <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg> Reject
                            </button>
                        </div>
                    `;
                } else {
                    footerActions = `
                        <div>
                            <span class="status-indicator-pill ${job.status}">${escapeHtml(job.status)}</span>
                        </div>
                        <div class="action-buttons">
                            ${job.status === 'applied' ? 
                                `<button class="btn btn-status-reject" onclick="updateStatus(${job.id}, 'rejected')">Archive</button>` :
                                `<button class="btn btn-status-apply" onclick="updateStatus(${job.id}, 'new')">Move to Inbox</button>`
                            }
                        </div>
                    `;
                }

                const scoreClass = getScoreClass(job.relevance_score);

                card.innerHTML = `
                    <div class="job-card-header">
                        <div class="job-details-brief">
                            <h3 class="job-title">${escapeHtml(job.job_title)}</h3>
                            <div class="company-name">${escapeHtml(job.company)}</div>
                        </div>
                        <div class="score-badge-container">
                            <div class="score-pill ${scoreClass}">${job.relevance_score}/10</div>
                            <div class="score-label">Match Score</div>
                        </div>
                    </div>
                    
                    <div class="job-meta-row">
                        <span class="meta-tag location">📍 ${escapeHtml(job.location)}</span>
                        <span class="meta-tag job-type">💼 ${escapeHtml(job.job_type)}</span>
                        <span class="meta-tag experience">🎓 Exp: ${escapeHtml(job.experience_required)}</span>
                    </div>

                    <p class="job-explanation">${escapeHtml(job.explanation)}</p>

                    <div class="skills-badges">
                        ${skillsHtml}
                    </div>

                    <div class="job-card-footer">
                        <span class="received-date">Received: ${formatDate(job.email_date)}</span>
                        ${footerActions}
                    </div>
                `;
                container.appendChild(card);
            });
        }

        function getMatchClass(score) {
            if (score >= 8) return 'high';
            if (score >= 6) return 'medium';
            return 'low';
        }

        function getScoreClass(score) {
            if (score >= 8) return 'high';
            if (score >= 6) return 'medium';
            return 'low';
        }

        function escapeHtml(unsafe) {
            if (!unsafe) return '';
            return unsafe
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        }

        function formatDate(dateStr) {
            try {
                const date = new Date(dateStr);
                if (isNaN(date.getTime())) return dateStr;
                return date.toLocaleDateString('en-IN', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (e) {
                return dateStr;
            }
        }

        function updateStatsAndBadges() {
            // Stats summary count
            const total = jobs.length;
            const high = jobs.filter(j => j.relevance_score >= 8).length;
            const applied = jobs.filter(j => j.status === 'applied').length;
            const rejected = jobs.filter(j => j.status === 'rejected').length;
            const news = jobs.filter(j => j.status === 'new').length;

            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-high').textContent = high;
            document.getElementById('stat-applied').textContent = applied;

            // Sidebar Status badges
            document.getElementById('badge-status-all').textContent = total;
            document.getElementById('badge-status-new').textContent = news;
            document.getElementById('badge-status-applied').textContent = applied;
            document.getElementById('badge-status-rejected').textContent = rejected;

            // Sidebar Score badges
            document.getElementById('badge-score-all').textContent = total;
            document.getElementById('badge-score-high').textContent = high;
            document.getElementById('badge-score-medium').textContent = jobs.filter(j => j.relevance_score >= 6 && j.relevance_score <= 7).length;
            document.getElementById('badge-score-low').textContent = jobs.filter(j => j.relevance_score < 6).length;
        }

        function setupFilterListeners() {
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const currentBtn = e.currentTarget;
                    const groupType = currentBtn.getAttribute('data-filter');
                    const value = currentBtn.getAttribute('data-val');

                    // Remove active class from brothers in the same group
                    const groupButtons = document.querySelectorAll(`.filter-btn[data-filter="${groupType}"]`);
                    groupButtons.forEach(b => b.classList.remove('active'));

                    // Add active class
                    currentBtn.classList.add('active');

                    // Set filter state
                    activeFilters[groupType] = value;
                    renderDashboard();
                });
            });
        }

        function setupSearchListener() {
            const searchInput = document.getElementById('search-input');
            searchInput.addEventListener('input', (e) => {
                activeFilters.search = e.target.value;
                renderDashboard();
            });
        }

        function openJobDetails(job) {
            const panel = document.getElementById('details-panel');
            const backdrop = document.getElementById('panel-backdrop');

            // Populate panel
            document.getElementById('panel-title').textContent = job.job_title;
            document.getElementById('panel-company').textContent = job.company;
            document.getElementById('panel-explanation').textContent = job.explanation;
            
            // Score border color mapping
            const scoreClass = getScoreClass(job.relevance_score);
            const explanationPanel = document.getElementById('panel-explanation');
            explanationPanel.className = `job-explanation`;
            explanationPanel.style.borderLeft = `3px solid var(--accent-${scoreClass === 'high' ? 'emerald' : scoreClass === 'medium' ? 'amber' : 'rose'})`;

            document.getElementById('panel-location').textContent = `📍 ${job.location} (${job.job_type})`;
            document.getElementById('panel-salary').textContent = `💵 ${job.salary || 'Not Specified'}`;
            document.getElementById('panel-experience').textContent = `🎓 ${job.experience_required}`;

            // Render skills badges in panel
            const skillsContainer = document.getElementById('panel-skills');
            skillsContainer.innerHTML = '';
            job.skills.forEach(skill => {
                const badge = document.createElement('span');
                badge.className = 'skill-badge';
                badge.textContent = skill;
                skillsContainer.appendChild(badge);
            });

            // Metadata
            document.getElementById('panel-meta-sender').textContent = job.sender;
            document.getElementById('panel-meta-date').textContent = formatDate(job.email_date);
            document.getElementById('panel-meta-subject').textContent = job.subject;

            // Render email body (parse markdown links to actual links if they exist)
            const bodyContainer = document.getElementById('panel-email-body');
            bodyContainer.innerHTML = parseMarkdownLinks(escapeHtml(job.body));

            // Open panel
            panel.classList.add('open');
            backdrop.classList.add('open');
        }

        function parseMarkdownLinks(text) {
            // Convert markdown style [Link Text](URL) to actual anchor tags
            const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
            return text.replace(linkRegex, (match, linkText, url) => {
                // Return anchor tag
                return `<a href="${url}" target="_blank" rel="noopener noreferrer">${linkText}</a>`;
            });
        }

        function setupPanelListeners() {
            const closeBtn = document.getElementById('panel-close-btn');
            const backdrop = document.getElementById('panel-backdrop');

            const closePanel = () => {
                document.getElementById('details-panel').classList.remove('open');
                backdrop.classList.remove('open');
            };

            closeBtn.addEventListener('click', closePanel);
            backdrop.addEventListener('click', closePanel);
        }

        // Action API updates (fully dynamic)
        function updateStatus(jobId, newStatus) {
            const jobIndex = jobs.findIndex(j => j.id === jobId);
            if (jobIndex === -1) return;

            // Update locally first for snappy UI
            const oldStatus = jobs[jobIndex].status;
            jobs[jobIndex].status = newStatus;
            
            // Show toast message
            showToast(`Job status updated to "${newStatus}"`);
            renderDashboard();

            // Send POST request to backend server (if served locally via python server)
            fetch(`/api/jobs/${jobId}/status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: newStatus })
            }).then(response => {
                if (!response.ok) {
                    console.log('Static fallback mode: API offline, updated locally in memory.');
                }
            }).catch(err => {
                console.log('Static fallback mode: Running without active local server.');
            });
        }

        function showToast(message) {
            const toast = document.getElementById('toast');
            document.getElementById('toast-message').textContent = message;
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
    </script>
</body>
</html>
"""

def generate_dashboard(jobs_data, output_path="dashboard.html"):
    """
    Renders the dashboard.html with injected jobs data.
    """
    # Convert list of dicts to a JSON string safe for script injection
    jobs_json = json.dumps(jobs_data)
    
    # Render template using Jinja2
    template = Template(TEMPLATE_HTML)
    rendered_html = template.render(jobs_json_raw=jobs_json)
    
    # Save file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)
        
    print(f"Successfully generated dashboard at: {output_path}")
