let dashboardData = null;

const CATEGORY_COLORS = [
    '#4e79a7', '#f28e2b', '#e15759', '#76b7b2',
    '#59a14f', '#edc948', '#b07aa1', '#ff9da7'
];

async function loadDashboard() {
    let data = sessionStorage.getItem('predictionResult');

    if (data) {
        dashboardData = JSON.parse(data);
        sessionStorage.removeItem('predictionResult');
    } else {
        const response = await fetch('/api/dashboard/data');
        const result = await response.json();

        if (!result.has_data) {
            window.location.href = '/upload';
            return;
        }
        dashboardData = result;
    }

    renderDashboard(dashboardData);
}

function renderDashboard(data) {
    document.getElementById('loading').classList.add('d-none');
    document.getElementById('dashboard-content').classList.remove('d-none');

    renderStatCards(data.summary);
    renderDonutChart(data.summary.spend_by_category);
    renderConfidenceChart(data.rows);
    renderAccountChart(data.summary.spend_by_account);
    renderTransactionTable(data.rows);
}

function renderStatCards(summary) {
    const cards = [
        { label: 'Total spend', value: '₹' + summary.total_spend.toLocaleString() },
        { label: 'Transactions', value: summary.total_transactions || dashboardData.total_transactions },
        { label: 'Top category', value: summary.top_category },
        { label: 'Avg confidence', value: (summary.avg_confidence_score * 100).toFixed(0) + '%' }
    ];

    const container = document.getElementById('stat-cards');
    container.innerHTML = cards.map(c => `
        <div class="col-6 col-md-3">
            <div class="card p-3 text-center">
                <div class="text-muted small mb-1">${c.label}</div>
                <div class="fw-bold fs-5">${c.value}</div>
            </div>
        </div>
    `).join('');
}

function renderDonutChart(spendByCategory) {
    const labels = Object.keys(spendByCategory);
    const values = Object.values(spendByCategory);

    new Chart(document.getElementById('donut-chart'), {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: CATEGORY_COLORS,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function renderConfidenceChart(rows) {
    const buckets = { '0-50%': 0, '50-70%': 0, '70-85%': 0, '85-100%': 0 };

    rows.forEach(r => {
        const score = r.confidence_score * 100;
        if (score < 50) buckets['0-50%']++;
        else if (score < 70) buckets['50-70%']++;
        else if (score < 85) buckets['70-85%']++;
        else buckets['85-100%']++;
    });

    new Chart(document.getElementById('confidence-chart'), {
        type: 'bar',
        data: {
            labels: Object.keys(buckets),
            datasets: [{
                label: 'Number of transactions',
                data: Object.values(buckets),
                backgroundColor: ['#e15759', '#f28e2b', '#4e79a7', '#59a14f'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

function renderAccountChart(spendByAccount) {
    const labels = Object.keys(spendByAccount);
    const values = Object.values(spendByAccount);

    new Chart(document.getElementById('account-chart'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total spend',
                data: values,
                backgroundColor: '#4e79a7',
                borderWidth: 0,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}
let currentPage = 1;
const rowsPerPage = 10;

function renderTransactionTable(rows) {
    const totalPages = Math.ceil(rows.length / rowsPerPage);
    const start = (currentPage - 1) * rowsPerPage;
    const pageRows = rows.slice(start, start + rowsPerPage);

    const tbody = document.getElementById('transaction-table');
    tbody.innerHTML = pageRows.map(r => {
        const score = (r.confidence_score * 100).toFixed(0);
        const badgeColor = score >= 85 ? 'success' : score >= 70 ? 'warning' : 'danger';
        return `
            <tr>
                <td>${r.description}</td>
                <td>₹${r.amount.toLocaleString()}</td>
                <td>${r.account_number}</td>
                <td>${r.category}</td>
                <td><span class="badge bg-${badgeColor}">${score}%</span></td>
            </tr>
        `;
    }).join('');

    renderPagination(totalPages, rows);
}

function renderPagination(totalPages, rows) {
    const existing = document.getElementById('pagination');
    if (existing) existing.remove();

    const nav = document.createElement('nav');
    nav.id = 'pagination';
    nav.className = 'mt-3 d-flex justify-content-between align-items-center';
    nav.innerHTML = `
        <small class="text-muted">
            Showing ${((currentPage-1)*rowsPerPage)+1}–${Math.min(currentPage*rowsPerPage, rows.length)} of ${rows.length} transactions
        </small>
        <ul class="pagination pagination-sm mb-0">
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="changePage(-1, event)">Previous</a>
            </li>
            <li class="page-item disabled">
                <span class="page-link">${currentPage} / ${totalPages}</span>
            </li>
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="changePage(1, event)">Next</a>
            </li>
        </ul>
    `;

    document.querySelector('.card.p-3.mb-4').appendChild(nav);
}

function changePage(direction, event) {
    event.preventDefault();
    currentPage += direction;
    renderTransactionTable(dashboardData.rows);
}

function exportCSV() {
    if (!dashboardData) return;

    const headers = ['description', 'amount', 'account_number', 'category', 'confidence_score'];
    const rows = dashboardData.rows.map(r =>
        headers.map(h => r[h]).join(',')
    );

    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'expense_analysis.csv';
    a.click();
    URL.revokeObjectURL(url);
}

if (typeof Chart !== 'undefined') {
    loadDashboard();
} else {
    window.addEventListener('load', loadDashboard);
}