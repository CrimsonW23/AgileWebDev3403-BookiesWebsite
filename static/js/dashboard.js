// Global variables 
let statsChartInitialized = false;
let countdownInterval; 

// Show the selected tab and hide others
function showTab(tabId) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
    const activeTab = document.getElementById(tabId);
    if (activeTab) activeTab.style.display = 'block';

    // Update menu highlighting
    document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
    const activeMenuItem = Array.from(document.querySelectorAll('.menu-item'))
        .find(item => item.getAttribute('onclick').includes(tabId));
    if (activeMenuItem) activeMenuItem.classList.add('active');

    // Initialize stats charts if needed
    if (tabId === 'stats') {
        fetchStatsData()
            .then(data => {
                createLineChart(data.monthly_wins);
                createPieChart(data.win_loss_ratio);
            })
            .catch(error => console.error('Error fetching stats data:', error));
    }
}

// Fetch dashboard data from server
function refreshDashboardData() {
    fetch('/dashboard/data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            updateDashboardTables(data); // Update all tables
            initializeTimeRemaining(); // Reinitialize countdown logic
        })
        .catch(error => console.error('Error fetching dashboard data:', error));
}

// Periodically refresh the dashboard data
setInterval(() => {
    refreshDashboardData();
}, 10000); // Refresh every 10 seconds

// Update all dashboard tables with data
function updateDashboardTables(data) {
    // Update Ongoing Bets table
    updateTable(
        '#ongoing .widget-table tbody',
        data.ongoing_bets,
        bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type_description}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>$${bet.potential_winnings}</td>
            <td class="time-remaining" data-end-time="${bet.scheduled_time}" data-duration="${bet.duration}"></td>
        </tr>
        `,
        "No ongoing bets"
    );

    // Update Upcoming Bets table
    updateTable(
        '#upcoming tbody',
        data.upcoming_bets,
        bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type_description}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${new Date(bet.scheduled_time).toLocaleString()}</td>
            <td>$${bet.potential_winnings}</td>
        </tr>
        `,
        "No upcoming bets"
    );

    // Update Past Bets table
    updateTable(
        '#past tbody',
        data.past_bets,
        bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type_description}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${bet.actual_winnings > 0 ? "Win" : "Loss"}</td>
            <td>$${bet.actual_winnings}</td>
            <td>${bet.date_settled ? new Date(bet.date_settled).toLocaleString() : 'N/A'}</td>
        </tr>
        `,
        "No past bets"
    );

    // Update Created Bets table
    updateTable(
        '#created-body',
        data.created_bets,
        bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type_description}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.max_stake || bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${new Date(bet.scheduled_time).toLocaleString()}</td>
            <td>${bet.duration}</td>
            <td>${bet.status}</td>  
        </tr>
        `,
        "No created bets"
    );
}

// Helper function to update table content
function updateTable(selector, data, rowTemplate, noDataMessage) {
    const tableBody = document.querySelector(selector);
    if (!tableBody) return; // Skip if table doesn't exist on the current page

    tableBody.innerHTML = ''; // Clear existing rows

    if (data && data.length > 0) {
        data.forEach(item => tableBody.innerHTML += rowTemplate(item));
    } else {
        // Show a custom "No data" message
        const columnCount = tableBody.closest('table').querySelectorAll('thead th').length;
        tableBody.innerHTML = `<tr><td colspan="${columnCount}" class="no-data">${noDataMessage}</td></tr>`;
    }
}
 

// Initialize countdown for "Time Remaining" cells
function initializeTimeRemaining() {
    if (countdownInterval) clearInterval(countdownInterval);

    countdownInterval = setInterval(() => {
        let refreshNeeded = false;

        document.querySelectorAll('.time-remaining').forEach(cell => {
            const endTimeAttr = cell.getAttribute('data-end-time');
            const durationAttr = cell.getAttribute('data-duration');

            if (!endTimeAttr || !durationAttr) {
                cell.textContent = "Invalid Data";
                return;
            }

            const endTime = new Date(endTimeAttr);
            const duration = parseInt(durationAttr) * 60 * 60 * 1000; // Convert hours to milliseconds
            const finalEndTime = new Date(endTime.getTime() + duration);
            const now = new Date();
            const diff = finalEndTime - now;

            if (diff <= 0) {
                // Mark that a refresh is needed to move the bet to the next table
                refreshNeeded = true;
            } else {
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                cell.textContent = `${hours}h ${minutes}m ${seconds}s`;
            }
        });

        if (refreshNeeded) {
            refreshDashboardData(); // Refresh dashboard data to update tables
        }
    }, 1000); // Update every second
}
 

// Fetch statistics data from the server
function fetchStatsData() {
    return fetch('/dashboard/stats')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        });
}

// Create a line chart for "Previous Months Wins"
function createLineChart(data) {
    const ctx = document.getElementById('lineChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.months, // e.g., ['January', 'February', 'March']
            datasets: [{
                label: 'Wins',
                data: data.wins, // e.g., [5, 10, 7]
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                }
            }
        }
    });
}

// Create a pie chart for "Last Month Win/Loss"
function createPieChart(data) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Wins', 'Losses'],
            datasets: [{
                data: [data.wins, data.losses], // e.g., [15, 5]
                backgroundColor: ['#4caf50', '#f44336'],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                }
            }
        }
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Determine current page
    const currentPath = window.location.pathname;

    // Initialize functionality based on current page
    if (currentPath.includes('/dashboard')) {
        refreshDashboardData(); // Initial data fetch
        initializeTimeRemaining(); // Initialize countdown logic
    }
});