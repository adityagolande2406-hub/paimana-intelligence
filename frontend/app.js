document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const elements = {
        totalProjects: document.getElementById('val-total'),
        extensions: document.getElementById('val-extensions'),
        lowProgress: document.getElementById('val-low-progress'),
        unavailable: document.getElementById('val-unavailable'),
        systemMessage: document.getElementById('system-message'),
        mobileMenuBtn: document.getElementById('mobile-menu-btn'),
        sidebar: document.getElementById('sidebar')
    };

    // Mobile Menu Toggle
    if (elements.mobileMenuBtn && elements.sidebar) {
        elements.mobileMenuBtn.addEventListener('click', () => {
            elements.sidebar.classList.toggle('open');
        });
    }

    // Function to update the dashboard with fetched data
    function updateDashboard(data) {
        elements.totalProjects.textContent = data.total_projects.toLocaleString();
        elements.extensions.textContent = data.schedule_extension_recorded.toLocaleString();
        elements.lowProgress.textContent = data.low_progress_projects.toLocaleString();
        elements.unavailable.textContent = data.schedule_data_unavailable.toLocaleString();
    }

    // Function to show error message
    function showError(message) {
        elements.systemMessage.className = 'system-message error';
        elements.systemMessage.innerHTML = `⚠️ <strong>Connection Error:</strong> ${message}`;
    }

    // Fetch data from the FastAPI backend
    async function fetchSummaryData() {
        try {
            // The API is hosted on the same server, so we can use a relative path
            const response = await fetch('/summary');
            
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Hide loading message and update UI
            elements.systemMessage.style.display = 'none';
            updateDashboard(data);
            
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
            showError('Unable to load live statistics. Please ensure the backend server is running and the data files exist.');
            
            // Set values to 'N/A' on error
            elements.totalProjects.textContent = 'N/A';
            elements.extensions.textContent = 'N/A';
            elements.lowProgress.textContent = 'N/A';
            elements.unavailable.textContent = 'N/A';
        }
    }

    // View Management
    const dashboardView = document.getElementById('dashboard-view');
    const detailView = document.getElementById('project-detail-view');
    const detailContent = document.getElementById('project-detail-content');
    const detailMessage = document.getElementById('detail-system-message');
    
    const analyticsView = document.getElementById('analytics-view');
    const analyticsContent = document.getElementById('analytics-content');
    const analyticsMessage = document.getElementById('analytics-system-message');
    
    const dataManagementView = document.getElementById('data-management-view');
    
    function showDashboard() {
        dashboardView.style.display = 'block';
        detailView.style.display = 'none';
        analyticsView.style.display = 'none';
        dataManagementView.style.display = 'none';
        
        // Update active nav
        document.getElementById('nav-dashboard').classList.add('active');
        document.getElementById('nav-project-explorer').classList.remove('active');
        document.getElementById('nav-analytics').classList.remove('active');
        document.getElementById('nav-data-management').classList.remove('active');
    }
    
    function showDetailView() {
        dashboardView.style.display = 'none';
        analyticsView.style.display = 'none';
        dataManagementView.style.display = 'none';
        detailView.style.display = 'block';
        detailContent.style.display = 'none';
        detailMessage.style.display = 'block';
        detailMessage.className = 'system-message loading';
        detailMessage.innerHTML = 'Loading project details...';
        
        // Update active nav
        document.getElementById('nav-dashboard').classList.remove('active');
        document.getElementById('nav-project-explorer').classList.add('active');
        document.getElementById('nav-analytics').classList.remove('active');
        document.getElementById('nav-data-management').classList.remove('active');
    }
    
    function showAnalyticsView() {
        dashboardView.style.display = 'none';
        detailView.style.display = 'none';
        dataManagementView.style.display = 'none';
        analyticsView.style.display = 'block';
        
        // Update active nav
        document.getElementById('nav-dashboard').classList.remove('active');
        document.getElementById('nav-project-explorer').classList.remove('active');
        document.getElementById('nav-analytics').classList.add('active');
        document.getElementById('nav-data-management').classList.remove('active');
        
        if (analyticsContent.style.display === 'none') {
            fetchAnalyticsData();
        }
    }
    
    function showDataManagementView() {
        dashboardView.style.display = 'none';
        detailView.style.display = 'none';
        analyticsView.style.display = 'none';
        dataManagementView.style.display = 'block';
        
        // Update active nav
        document.getElementById('nav-dashboard').classList.remove('active');
        document.getElementById('nav-project-explorer').classList.remove('active');
        document.getElementById('nav-analytics').classList.remove('active');
        document.getElementById('nav-data-management').classList.add('active');
        
        fetchHistoryData();
    }

    // Navigation Events
    document.getElementById('nav-dashboard').addEventListener('click', (e) => {
        e.preventDefault();
        showDashboard();
    });
    
    document.getElementById('nav-project-explorer').addEventListener('click', (e) => {
        e.preventDefault();
        showDashboard(); 
        // Reset filters when clicking sidebar link to see all projects
        document.getElementById('btn-clear-filters').click();
    });
    
    document.getElementById('btn-back-to-projects').addEventListener('click', () => {
        showDashboard();
    });
    
    document.getElementById('nav-analytics').addEventListener('click', (e) => {
        e.preventDefault();
        showAnalyticsView();
    });
    
    document.getElementById('nav-data-management').addEventListener('click', (e) => {
        e.preventDefault();
        showDataManagementView();
    });
    
    document.getElementById('btn-analytics-back').addEventListener('click', () => {
        showDashboard();
    });

    // Fetch and display individual project details
    async function fetchProjectDetails(projectCode) {
        showDetailView();
        
        // Reset risk UI state
        document.getElementById('risk-system-message').style.display = 'block';
        document.getElementById('risk-system-message').className = 'system-message loading';
        document.getElementById('risk-system-message').innerHTML = 'Evaluating project risk...';
        document.getElementById('risk-assessment-content').style.display = 'none';
        
        // Reset history UI state
        document.getElementById('history-system-message').style.display = 'block';
        document.getElementById('history-system-message').className = 'system-message loading';
        document.getElementById('history-system-message').innerHTML = 'Loading historical trends...';
        document.getElementById('history-assessment-content').style.display = 'none';
        document.getElementById('history-empty-state').style.display = 'none';
        document.getElementById('history-charts-container').style.display = 'none';
        
        // Reset analytics UI state
        document.getElementById('analytics-system-message').style.display = 'block';
        document.getElementById('analytics-system-message').className = 'system-message loading';
        document.getElementById('analytics-system-message').innerHTML = 'Analyzing historical trends...';
        document.getElementById('analytics-content-container').style.display = 'none';
        
        try {
            const [detailResponse, riskResponse, historyResponse] = await Promise.all([
                fetch(`/projects/${projectCode}`),
                fetch(`/projects/${projectCode}/risk`).catch(() => null),
                fetch(`/projects/${projectCode}/history`).catch(() => null)
            ]);
            
            if (!detailResponse.ok) throw new Error(`Status: ${detailResponse.status}`);
            const p = await detailResponse.json();
            
            // Populate basic fields
            document.getElementById('detail-project-name').textContent = p.project_details.replace(/\\n/g, ' ').replace(/\(\d{6}\)/, '').trim() || 'Project Name Unavailable';
            document.getElementById('detail-project-code').textContent = p.project_code;
            document.getElementById('detail-state').textContent = p.state;
            
            document.getElementById('detail-original-cost').textContent = p.original_cost_crore ? p.original_cost_crore.toLocaleString() : 'N/A';
            document.getElementById('detail-expenditure').textContent = p.expenditure ? p.expenditure.toLocaleString() : 'N/A';
            document.getElementById('detail-physical-progress').textContent = (p.physical_progress || 0) + '%';
            
            document.getElementById('detail-schedule-extension').textContent = p.schedule_extension_months !== null ? `${p.schedule_extension_months} months` : 'N/A';
            
            // Map status
            let statusClass = 'safe';
            if (p.schedule_monitoring_class === 'Schedule Extension Recorded') statusClass = 'alert';
            else if (p.schedule_monitoring_class === 'Schedule Data Unavailable') statusClass = 'warning';
            else if (p.schedule_monitoring_class === 'Earlier Revised Completion') statusClass = 'warning';
            
            const classEl = document.getElementById('detail-classification');
            classEl.textContent = p.schedule_monitoring_class;
            classEl.className = `status-pill ${statusClass}`;
            
            document.getElementById('detail-explanation').textContent = p.monitoring_explanation;
            
            // Populate Risk fields
            if (riskResponse && riskResponse.ok) {
                const risk = await riskResponse.json();
                document.getElementById('risk-system-message').style.display = 'none';
                document.getElementById('risk-assessment-content').style.display = 'block';
                
                document.getElementById('risk-schedule').textContent = risk.schedule_assessment || 'Not available';
                document.getElementById('risk-financial').textContent = risk.financial_assessment || 'Not available';
                document.getElementById('risk-progress').textContent = risk.progress_assessment || 'Not available';
                
                const execEl = document.getElementById('risk-execution');
                execEl.textContent = risk.execution_indicator || 'No indicator triggered';
                execEl.style.color = risk.execution_indicator ? 'var(--status-alert)' : 'var(--text-primary)';
                
                const warnEl = document.getElementById('risk-warnings');
                if (risk.data_quality_warnings && risk.data_quality_warnings.length > 0) {
                    warnEl.innerHTML = risk.data_quality_warnings.map(w => `<li>${w}</li>`).join('');
                } else {
                    warnEl.innerHTML = '<li style="color: var(--text-secondary);">None</li>';
                }
                
                const evEl = document.getElementById('risk-evidence');
                if (risk.evidence && risk.evidence.length > 0) {
                    evEl.innerHTML = risk.evidence.map(e => `<li>${e}</li>`).join('');
                } else {
                    evEl.innerHTML = '<li>--</li>';
                }
                
                document.getElementById('risk-limitations').textContent = risk.limitations || '--';
            } else {
                document.getElementById('risk-system-message').className = 'system-message error';
                document.getElementById('risk-system-message').innerHTML = '⚠️ <strong>Error:</strong> Risk assessment unavailable for this project.';
            }
            
            // Populate History fields
            if (historyResponse && historyResponse.ok) {
                const hist = await historyResponse.json();
                document.getElementById('history-system-message').style.display = 'none';
                document.getElementById('history-assessment-content').style.display = 'block';
                
                document.getElementById('history-obs-count').textContent = hist.observation_count;
                
                if (hist.observation_count === 0) {
                    document.getElementById('history-months').textContent = '--';
                    document.getElementById('history-empty-state').style.display = 'block';
                    document.getElementById('history-charts-container').style.display = 'none';
                } else {
                    document.getElementById('history-empty-state').style.display = 'none';
                    document.getElementById('history-charts-container').style.display = 'block';
                    
                    const months = hist.observations.map(o => o.report_month).join(', ');
                    document.getElementById('history-months').textContent = months;
                    
                    const progData = {};
                    const expData = {};
                    const extData = {};
                    
                    hist.observations.forEach(o => {
                        if (o.physical_progress !== null) progData[o.report_month] = o.physical_progress;
                        if (o.expenditure !== null) expData[o.report_month] = o.expenditure;
                        if (o.schedule_extension_months !== null) {
                            // Safe width bounds will be handled by HTML ignoring negative width %
                            extData[o.report_month] = o.schedule_extension_months;
                        }
                    });
                    
                    renderChart('chart-history-progress', progData);
                    renderChart('chart-history-expenditure', expData);
                    renderChart('chart-history-extension', extData);
                }
                
                // Populate Analytics fields
                if (hist.analytics) {
                    document.getElementById('analytics-system-message').style.display = 'none';
                    document.getElementById('analytics-content-container').style.display = 'block';
                    
                    document.getElementById('analytics-status-banner').style.display = 'block';
                    document.getElementById('analytics-status').textContent = hist.analytics.status;
                    document.getElementById('analytics-message').textContent = hist.analytics.message;
                    
                    if (hist.analytics.metrics) {
                        document.getElementById('analytics-metrics-grid').style.display = 'grid';
                        document.getElementById('analytics-trend-container').style.display = 'block';
                        
                        const m = hist.analytics.metrics;
                        
                        document.getElementById('analytics-progress-change').textContent = m.progress_change !== null ? (m.progress_change > 0 ? '+' : '') + m.progress_change : '--';
                        document.getElementById('analytics-exp-change').textContent = m.expenditure_change_crore !== null ? (m.expenditure_change_crore > 0 ? '+' : '') + m.expenditure_change_crore : '--';
                        document.getElementById('analytics-exp-pct').textContent = m.expenditure_change_pct !== null ? (m.expenditure_change_pct > 0 ? '+' : '') + m.expenditure_change_pct + '%' : '--';
                        document.getElementById('analytics-ext-change').textContent = m.schedule_extension_change !== null ? (m.schedule_extension_change > 0 ? '+' : '') + m.schedule_extension_change : '--';
                        
                        document.getElementById('analytics-trend').textContent = m.trend_indicator || '--';
                        document.getElementById('analytics-risk').textContent = m.risk_movement || '--';
                        
                        if (m.risk_movement === 'Escalated') {
                            document.getElementById('analytics-risk').style.color = 'var(--status-alert)';
                        } else if (m.risk_movement === 'Recovering') {
                            document.getElementById('analytics-risk').style.color = 'var(--status-safe)';
                        } else {
                            document.getElementById('analytics-risk').style.color = 'var(--text-primary)';
                        }
                    } else {
                        document.getElementById('analytics-metrics-grid').style.display = 'none';
                        document.getElementById('analytics-trend-container').style.display = 'none';
                    }
                } else {
                    document.getElementById('analytics-system-message').className = 'system-message error';
                    document.getElementById('analytics-system-message').innerHTML = '⚠️ <strong>Error:</strong> Historical intelligence unavailable.';
                }
                
            } else {
                document.getElementById('history-system-message').className = 'system-message error';
                document.getElementById('history-system-message').innerHTML = '⚠️ <strong>Error:</strong> Historical trends unavailable for this project.';
            }
            
            // Show content
            detailMessage.style.display = 'none';
            detailContent.style.display = 'block';
            
        } catch (error) {
            console.error('Failed to fetch project details:', error);
            detailMessage.className = 'system-message error';
            detailMessage.innerHTML = `⚠️ <strong>Error:</strong> Unable to load details for Project ${projectCode}.`;
        }
    }

    // Function to render projects into the table
    function renderProjects(projects) {
        const tbody = document.getElementById('projects-table-body');
        
        if (!projects || projects.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2rem;">No projects found.</td></tr>`;
            return;
        }
        
        tbody.innerHTML = '';
        
        projects.forEach(project => {
            const tr = document.createElement('tr');
            tr.style.cursor = 'pointer'; // Make it clickable
            
            // Hover effect
            tr.addEventListener('mouseenter', () => tr.style.backgroundColor = '#f8fafc');
            tr.addEventListener('mouseleave', () => tr.style.backgroundColor = 'transparent');
            
            // Click to open detail view
            tr.addEventListener('click', () => fetchProjectDetails(project.project_code));
            
            // Map status to CSS classes
            let statusClass = 'safe';
            let statusText = project.schedule_monitoring_class;
            
            if (statusText === 'Schedule Extension Recorded') {
                statusClass = 'alert';
                statusText = 'Extension Recorded';
            } else if (statusText === 'Schedule Data Unavailable') {
                statusClass = 'warning';
                statusText = 'Data Unavailable';
            } else if (statusText === 'No Recorded Extension') {
                statusClass = 'safe';
                statusText = 'No Extension';
            } else if (statusText === 'Earlier Revised Completion') {
                statusClass = 'warning';
                statusText = 'Earlier Completion';
            }
            
            tr.innerHTML = `
                <td><span class="code-badge">${project.project_code}</span></td>
                <td>${project.state}</td>
                <td>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${project.physical_progress || 0}%;"></div>
                    </div>
                    <span style="font-size: 0.75rem; color: #64748b; margin-top: 4px; display: inline-block;">${project.physical_progress || 0}%</span>
                </td>
                <td><span class="status-pill ${statusClass}">${statusText}</span></td>
                <td class="placeholder-text" style="font-style: normal; font-size: 0.8rem; color: #475569;">
                    ${project.monitoring_explanation}
                </td>
            `;
            
            tbody.appendChild(tr);
        });
    }

    // State Variables for Pagination & Filtering
    let currentPage = 1;
    let currentLimit = 10;
    let currentSearch = '';
    let currentStateStr = '';

    // Fetch and populate states dropdown
    async function fetchStatesData() {
        try {
            const response = await fetch('/states');
            if (response.ok) {
                const states = await response.json();
                const select = document.getElementById('state-select');
                states.forEach(state => {
                    const option = document.createElement('option');
                    option.value = state;
                    option.textContent = state;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to fetch states:', error);
        }
    }

    // Fetch project data from the backend
    async function fetchProjectsData() {
        const tbody = document.getElementById('projects-table-body');
        const prevBtn = document.getElementById('btn-prev-page');
        const nextBtn = document.getElementById('btn-next-page');
        const info = document.getElementById('pagination-info');
        
        try {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2rem;">Loading projects...</td></tr>`;
            
            // Construct query URL
            const url = new URL('/projects', window.location.origin);
            url.searchParams.append('limit', currentLimit);
            url.searchParams.append('page', currentPage);
            if (currentSearch) url.searchParams.append('q', currentSearch);
            if (currentStateStr) url.searchParams.append('state', currentStateStr);
            
            const response = await fetch(url);
            if (!response.ok) throw new Error(`Status: ${response.status}`);
            
            const data = await response.json();
            renderProjects(data.items);
            
            // Update pagination UI
            const totalPages = Math.ceil(data.total / currentLimit) || 1;
            
            if (data.total === 0) {
                info.textContent = `Showing 0 of 0 projects`;
            } else {
                const start = ((currentPage - 1) * currentLimit) + 1;
                const end = Math.min(currentPage * currentLimit, data.total);
                info.textContent = `Showing ${start}-${end} of ${data.total} projects (Page ${currentPage} of ${totalPages})`;
            }
            
            prevBtn.disabled = currentPage <= 1;
            prevBtn.style.opacity = prevBtn.disabled ? '0.5' : '1';
            prevBtn.style.cursor = prevBtn.disabled ? 'not-allowed' : 'pointer';
            
            nextBtn.disabled = currentPage >= totalPages;
            nextBtn.style.opacity = nextBtn.disabled ? '0.5' : '1';
            nextBtn.style.cursor = nextBtn.disabled ? 'not-allowed' : 'pointer';
            
        } catch (error) {
            console.error('Failed to fetch projects:', error);
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2rem; color: #ef4444;">Error loading projects.</td></tr>`;
        }
    }

    // Pagination Events
    document.getElementById('btn-prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchProjectsData();
        }
    });

    document.getElementById('btn-next-page').addEventListener('click', () => {
        currentPage++;
        fetchProjectsData();
    });

    // Search and Filter Events
    const searchInput = document.getElementById('search-input');
    const stateSelect = document.getElementById('state-select');
    const clearBtn = document.getElementById('btn-clear-filters');
    
    // Debounce timer for search
    let typingTimer;
    searchInput.addEventListener('input', () => {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => {
            currentSearch = searchInput.value.trim();
            currentPage = 1;
            fetchProjectsData();
        }, 300);
    });

    stateSelect.addEventListener('change', () => {
        currentStateStr = stateSelect.value;
        currentPage = 1;
        fetchProjectsData();
    });

    clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        stateSelect.value = '';
        currentSearch = '';
        currentStateStr = '';
        currentPage = 1;
        fetchProjectsData();
    });

    // Analytics Logic
    function renderChart(containerId, dataObj) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        let maxVal = 0;
        for (const key in dataObj) {
            if (dataObj[key] > maxVal) maxVal = dataObj[key];
        }
        
        if (maxVal === 0) {
            container.innerHTML = '<p style="color: #64748b; font-size: 0.85rem;">No data available</p>';
            return;
        }
        
        for (const [key, value] of Object.entries(dataObj)) {
            const pct = (value / maxVal) * 100;
            const row = document.createElement('div');
            row.className = 'chart-row';
            row.innerHTML = `
                <div class="chart-label" title="${key}">${key}</div>
                <div class="chart-bar-bg">
                    <div class="chart-bar-fill" style="width: ${pct}%;"></div>
                </div>
                <div class="chart-value">${value.toLocaleString()}</div>
            `;
            container.appendChild(row);
        }
    }

    async function fetchAnalyticsData() {
        analyticsMessage.style.display = 'block';
        analyticsContent.style.display = 'none';
        analyticsMessage.className = 'system-message loading';
        analyticsMessage.innerHTML = 'Loading analytics data...';
        
        try {
            const response = await fetch('/analytics');
            if (!response.ok) throw new Error(`Status: ${response.status}`);
            
            const data = await response.json();
            
            renderChart('chart-progress', data.progress_categories);
            renderChart('chart-extensions', data.schedule_extensions);
            renderChart('chart-states', data.top_states);
            renderChart('chart-monitoring', data.monitoring_classifications);
            
            analyticsMessage.style.display = 'none';
            analyticsContent.style.display = 'block';
        } catch (error) {
            console.error('Failed to fetch analytics:', error);
            analyticsMessage.className = 'system-message error';
            analyticsMessage.innerHTML = '⚠️ <strong>Error:</strong> Unable to load analytics data.';
        }
    }

    // Data Management Logic
    let currentUploadFilename = '';
    
    async function fetchHistoryData() {
        const tbody = document.getElementById('history-table-body');
        try {
            const response = await fetch('/data/history');
            const data = await response.json();
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem;">No history found.</td></tr>';
                return;
            }
            
            tbody.innerHTML = '';
            data.reverse().forEach(row => {
                tbody.innerHTML += `
                    <tr>
                        <td>${row.timestamp}</td>
                        <td>${row.filename}</td>
                        <td>${row.record_count}</td>
                        <td><span class="status-pill safe">${row.status}</span></td>
                    </tr>
                `;
            });
        } catch (error) {
            console.error('Failed to fetch history:', error);
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem; color: var(--status-alert);">Error loading history.</td></tr>';
        }
    }
    
    document.getElementById('btn-upload-preview').addEventListener('click', async () => {
        const fileInput = document.getElementById('file-upload');
        const msg = document.getElementById('upload-message');
        const previewSec = document.getElementById('upload-preview-section');
        
        if (!fileInput.files || fileInput.files.length === 0) {
            msg.className = 'system-message error';
            msg.innerHTML = 'Please select a CSV file first.';
            msg.style.display = 'block';
            return;
        }
        
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
        msg.className = 'system-message loading';
        msg.innerHTML = 'Validating dataset...';
        msg.style.display = 'block';
        previewSec.style.display = 'none';
        
        try {
            const response = await fetch('/upload-preview', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (!data.valid) {
                msg.className = 'system-message error';
                msg.innerHTML = `⚠️ <strong>Validation Failed:</strong><br> - ${data.errors.join('<br> - ')}`;
                return;
            }
            
            // Valid dataset
            msg.className = 'system-message';
            msg.style.backgroundColor = 'var(--accent-teal-light)';
            msg.style.color = 'var(--accent-teal)';
            msg.style.border = '1px solid rgba(13, 148, 136, 0.2)';
            msg.innerHTML = `✅ <strong>Validation Passed:</strong> Dataset contains ${data.record_count} valid records. Ready to import.`;
            
            currentUploadFilename = data.filename;
            
            const tbody = document.getElementById('preview-table-body');
            tbody.innerHTML = '';
            data.preview.forEach(row => {
                tbody.innerHTML += `
                    <tr>
                        <td><span class="code-badge">${row.project_code}</span></td>
                        <td>${row.state}</td>
                        <td>${row.physical_progress || 0}%</td>
                        <td>${row.schedule_monitoring_class}</td>
                    </tr>
                `;
            });
            
            previewSec.style.display = 'block';
        } catch (error) {
            console.error(error);
            msg.className = 'system-message error';
            msg.innerHTML = '⚠️ <strong>Server Error:</strong> Unable to process the file.';
        }
    });
    
    document.getElementById('btn-upload-cancel').addEventListener('click', () => {
        document.getElementById('upload-preview-section').style.display = 'none';
        document.getElementById('upload-message').style.display = 'none';
        document.getElementById('file-upload').value = '';
        currentUploadFilename = '';
    });
    
    document.getElementById('btn-upload-confirm').addEventListener('click', async () => {
        const btn = document.getElementById('btn-upload-confirm');
        const msg = document.getElementById('upload-message');
        
        btn.disabled = true;
        btn.textContent = 'Applying Update...';
        
        try {
            const response = await fetch(`/upload-confirm?filename=${encodeURIComponent(currentUploadFilename)}`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (response.ok && data.success) {
                document.getElementById('upload-preview-section').style.display = 'none';
                document.getElementById('file-upload').value = '';
                
                msg.className = 'system-message';
                msg.style.backgroundColor = 'var(--accent-teal-light)';
                msg.style.color = 'var(--accent-teal)';
                msg.innerHTML = `✅ <strong>Success:</strong> ${data.message}`;
                
                // Refresh data
                fetchHistoryData();
                fetchSummaryData();
                fetchProjectsData();
                fetchStatesData();
                fetchAnalyticsData();
            } else {
                throw new Error(data.detail || 'Unknown error during confirmation.');
            }
        } catch (error) {
            console.error(error);
            msg.className = 'system-message error';
            msg.innerHTML = `⚠️ <strong>Update Failed:</strong> ${error.message}`;
        } finally {
            btn.disabled = false;
            btn.textContent = 'Confirm & Apply Update';
        }
    });

    // History Upload Logic
    let currentHistoryStagingId = '';
    
    document.getElementById('btn-history-upload-preview').addEventListener('click', async () => {
        const fileInput = document.getElementById('history-file-upload');
        const msg = document.getElementById('history-upload-message');
        const previewSec = document.getElementById('history-upload-preview-section');
        const confirmBtn = document.getElementById('btn-history-upload-confirm');
        const errorsList = document.getElementById('history-errors-list');
        const errorsContainer = document.getElementById('history-errors-container');
        
        if (!fileInput.files || fileInput.files.length === 0) {
            msg.className = 'system-message error';
            msg.innerHTML = 'Please select a CSV file first.';
            msg.style.display = 'block';
            return;
        }
        
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
        msg.className = 'system-message loading';
        msg.innerHTML = 'Validating historical dataset...';
        msg.style.display = 'block';
        previewSec.style.display = 'none';
        
        try {
            const response = await fetch('/history/upload-preview', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            document.getElementById('history-valid-count').textContent = data.valid_count || 0;
            document.getElementById('history-invalid-count').textContent = data.invalid_count || 0;
            
            if (data.errors && data.errors.length > 0) {
                errorsList.innerHTML = data.errors.map(e => `<li>Row ${e.row}: ${e.msg}</li>`).join('');
                errorsContainer.style.display = 'block';
            } else {
                errorsContainer.style.display = 'none';
            }
            
            if (!data.valid) {
                msg.className = 'system-message error';
                msg.innerHTML = `⚠️ <strong>Validation Failed:</strong> Please correct the errors below and try again.`;
                confirmBtn.disabled = true;
                confirmBtn.style.opacity = '0.5';
                confirmBtn.style.cursor = 'not-allowed';
            } else {
                msg.className = 'system-message';
                msg.style.backgroundColor = 'var(--accent-teal-light)';
                msg.style.color = 'var(--accent-teal)';
                msg.style.border = '1px solid rgba(13, 148, 136, 0.2)';
                msg.innerHTML = `✅ <strong>Validation Passed:</strong> Ready to import.`;
                
                currentHistoryStagingId = data.staging_id;
                confirmBtn.disabled = false;
                confirmBtn.style.opacity = '1';
                confirmBtn.style.cursor = 'pointer';
                
                const tbody = document.getElementById('history-preview-table-body');
                tbody.innerHTML = '';
                if (data.preview && data.preview.length > 0) {
                    data.preview.forEach(row => {
                        tbody.innerHTML += `
                            <tr>
                                <td><span class="code-badge">${row.project_code}</span></td>
                                <td>${row.report_month}</td>
                                <td>${row.physical_progress !== null ? row.physical_progress + '%' : '--'}</td>
                                <td>${row.expenditure !== null ? row.expenditure : '--'}</td>
                                <td>${row.schedule_extension_months ?? '--'}</td>
                            </tr>
                        `;
                    });
                } else {
                     tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No valid records.</td></tr>';
                }
            }
            
            previewSec.style.display = 'block';
        } catch (error) {
            console.error(error);
            msg.className = 'system-message error';
            msg.innerHTML = '⚠️ <strong>Server Error:</strong> Unable to process the file.';
        }
    });
    
    document.getElementById('btn-history-upload-cancel').addEventListener('click', () => {
        document.getElementById('history-upload-preview-section').style.display = 'none';
        document.getElementById('history-upload-message').style.display = 'none';
        document.getElementById('history-file-upload').value = '';
        currentHistoryStagingId = '';
    });
    
    document.getElementById('btn-history-upload-confirm').addEventListener('click', async () => {
        const btn = document.getElementById('btn-history-upload-confirm');
        const msg = document.getElementById('history-upload-message');
        
        if (!currentHistoryStagingId) return;
        
        btn.disabled = true;
        btn.textContent = 'Importing...';
        
        try {
            const response = await fetch(`/history/upload-confirm?staging_id=${encodeURIComponent(currentHistoryStagingId)}`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (response.ok && data.success) {
                document.getElementById('history-upload-preview-section').style.display = 'none';
                document.getElementById('history-file-upload').value = '';
                
                msg.className = 'system-message';
                msg.style.backgroundColor = 'var(--accent-teal-light)';
                msg.style.color = 'var(--accent-teal)';
                msg.innerHTML = `✅ <strong>Success:</strong> Inserted ${data.inserted} and updated ${data.updated} records (Total Processed: ${data.total_processed}).`;
                
                currentHistoryStagingId = '';
            } else {
                throw new Error(data.detail || 'Unknown error during confirmation.');
            }
        } catch (error) {
            console.error(error);
            msg.className = 'system-message error';
            msg.innerHTML = `⚠️ <strong>Import Failed:</strong> ${error.message}`;
        } finally {
            btn.disabled = false;
            btn.textContent = 'Confirm Import';
        }
    });

    // Initiate data fetch on load
    fetchSummaryData();
    fetchStatesData();
    fetchProjectsData();
});
