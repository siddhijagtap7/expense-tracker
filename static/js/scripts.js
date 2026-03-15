let currentPage = 1;
let rowsPerPage = 10;

// The expanded global color palette
const chartColors = [
    '#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c', '#e67e22',
    '#34495e', '#d35400', '#c0392b', '#8e44ad', '#27ae60', '#16a085', '#2980b9',
    '#f39c12', '#7f8c8d', '#ff9ff3', '#feca57', '#ff6b6b', '#48dbfb'
];

/**
 * Global Chart Creator
 */
/**
 * Global Chart Creator
 * Handles instance cleanup and dynamic data binding
 */
function createChart(id, data, type) {
    const el = document.getElementById(id);
    if (!el) return null;

    // 1. CLEANUP: Destroy existing chart instance to prevent hover/rendering glitches
    const existingChart = Chart.getChart(id); 
    if (existingChart) {
        existingChart.destroy();
    }

    // 2. CONFIG: Set color logic
    // Line charts usually look better with a single color/fill
    // Pie/Bar charts use our global chartColors array
    const backgroundColors = type === 'line' ? 'rgba(52, 152, 219, 0.2)' : chartColors;
    const borderColors = type === 'line' ? '#3498db' : '#ffffff';

    // 3. INITIALIZE: Create and return the new instance
    return new Chart(el, {
        type: type,
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Spending (₹)',
                data: Object.values(data),
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1,
                fill: type === 'line',
                tension: 0.4 // Makes line charts smooth (curved)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    display: (type !== 'bar'), // Hide legend for bars to save vertical space
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            let value = context.parsed.y || context.parsed || 0;
                            return `${label}: ₹${value.toLocaleString('en-IN')}`;
                        }
                    }
                }
            },
            scales: (type === 'bar' || type === 'line') ? {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) { return '₹' + value; }
                    }
                }
            } : {}
        }
    });
}

/**
 * Updates the rows per page and resets to page 1
 */
function updatePageSize(tableBodyId) {
    const selector = document.getElementById('pageSize');
    if (selector) {
        rowsPerPage = parseInt(selector.value);
        currentPage = 1;
        paginateTable(tableBodyId);
    }
}
function downloadExcel() {
    // Use the value from the dropdown
    const month = document.getElementById('dashboardMonthFilter').value;
    
    // Trigger the download by navigating to the download URL
    window.location.href = `/download-expenses?month=${month}`;
}

/**
 * Changes page index
 */
function changePage(direction, tableBodyId) {
    currentPage += direction;
    paginateTable(tableBodyId);
}

/**
 * Table Search/Filter Logic
 */
function filterTable() {
    const input = document.getElementById("tableSearch");
    const filter = input.value.toUpperCase();
    const table = document.getElementById("expenseTableBody");
    const tr = table.getElementsByTagName("tr");

    for (let i = 0; i < tr.length; i++) {
        const textContent = tr[i].textContent || tr[i].innerText;
        if (textContent.toUpperCase().indexOf(filter) > -1) {
            tr[i].classList.remove("filtered-out");
        } else {
            tr[i].classList.add("filtered-out");
        }
    }
    currentPage = 1; 
    paginateTable("expenseTableBody");
}

/**
 * Core Pagination logic
 */
function paginateTable(tableBodyId) {
    const table = document.getElementById(tableBodyId);
    if (!table) return;

    const allRows = Array.from(table.getElementsByTagName("tr"));
    const visibleRows = allRows.filter(row => !row.classList.contains("filtered-out"));
    
    const totalRows = visibleRows.length;
    const totalPages = Math.ceil(totalRows / rowsPerPage) || 1;

    if (currentPage < 1) currentPage = 1;
    if (currentPage > totalPages) currentPage = totalPages;

    allRows.forEach(row => row.style.display = "none");

    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;

    visibleRows.forEach((row, i) => {
        if (i >= start && i < end) {
            row.style.display = "";
        }
    });

    // Update UI elements safely
    const pageDisplay = document.getElementById("pageDisplay");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");

    if (pageDisplay) pageDisplay.innerText = `Page ${currentPage} of ${totalPages}`;
    if (prevBtn) prevBtn.disabled = (currentPage === 1);
    if (nextBtn) nextBtn.disabled = (currentPage === totalPages);
}