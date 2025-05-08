// Global variables
let statsChartInitialized = false;
let countdownInterval;

// Global variables to store chart instances
let lineChartInstance = null;
let pieChartInstance = null;

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

    // Handle stats tab specifically
    if (tabId === 'stats') {
        // Initialize charts with server-side data
        initializeChartsWithServerData();
    }
}

// Initialize charts with data from server-side rendering
function initializeChartsWithServerData() {
    try {
        // Get the chart data from the template
        const chartDataElement = document.getElementById('chart-data');
        if (!chartDataElement) { 
            renderNoStatsMessage();
            return;
        }
        
        const chartData = JSON.parse(chartDataElement.textContent); 

        // Destroy existing charts if they exist
        if (lineChartInstance) lineChartInstance.destroy();
        if (pieChartInstance) pieChartInstance.destroy();

        // Check if we have valid monthly data
        const hasMonthlyData = chartData && 
                              chartData.monthly_wins && 
                              chartData.monthly_wins.months && 
                              chartData.monthly_wins.months.length > 0 &&
                              chartData.monthly_wins.wins.some(win => win > 0);

        // Create line chart if we have monthly data
        if (hasMonthlyData) {
            document.getElementById('lineChart').style.display = 'block';
            document.getElementById('lineChartMessage').style.display = 'none';
            lineChartInstance = createLineChart(chartData.monthly_wins);
        } else {
            document.getElementById('lineChart').style.display = 'none';
            document.getElementById('lineChartMessage').textContent = 'No wins recorded for previous months';
            document.getElementById('lineChartMessage').style.display = 'block';
        }

        // Check if we have win/loss data for previous month
        const hasWinLossData = chartData && 
                              chartData.win_loss_ratio && 
                              (chartData.win_loss_ratio.wins > 0 || chartData.win_loss_ratio.losses > 0);

        // Create pie chart if we have win/loss data
        if (hasWinLossData) {
            pieChartInstance = createPieChart(chartData.win_loss_ratio);
        } else {
            document.getElementById('pieChart').style.display = 'none';
            document.getElementById('pieChartMessage').textContent = 'No wins or losses recorded for the previous month';
            document.getElementById('pieChartMessage').style.display = 'block';
        }
             
    } catch (error) { 
        console.error('Error initializing charts:', error);
        renderNoStatsMessage();
    }
}

// Create a line chart for "Previous Months Wins"
function createLineChart(data) { 
    const canvas = document.getElementById('lineChart'); 
    const ctx = canvas.getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.months || [],
            datasets: [{
                label: 'Wins',
                data: data.wins || [],
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true },
            },
            scales: {
                x: { title: { display: true, text: 'Months' } },
                y: { title: { display: true, text: 'Wins' } }
            }
        }
    });
}

// Create a pie chart for "Win/Loss Ratio"
function createPieChart(data) {
    const canvas = document.getElementById('pieChart');
    const ctx = canvas.getContext('2d');

    // Check if there is no data or if both wins and losses are 0
    if (!data || (data.wins === 0 && data.losses === 0)) {
        // Hide the chart canvas
        canvas.style.display = 'none';
        
        // Display the fallback message
        const messageElement = document.getElementById('pieChartMessage');
        messageElement.textContent = 'No wins or losses recorded for the previous month.';
        messageElement.style.display = 'block'; // Make sure the message is visible
        return null; // Return null since we're not creating a chart
    }

    // If we have data, show the canvas and hide the message
    canvas.style.display = 'block';
    document.getElementById('pieChartMessage').style.display = 'none';

    // Create the pie chart
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Wins', 'Losses'],
            datasets: [{
                data: [data.wins || 0, data.losses || 0],
                backgroundColor: ['#4caf50', '#f44336'],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true },
            }
        }
    });
}

// Fetch dashboard data from the `/dashboard` route
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
 
// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initial data fetch
    refreshDashboardData();
    
    // Initialize countdown logic
    initializeTimeRemaining();
    
    // If stats tab is active by default, load data
    if (document.getElementById('stats').style.display === 'block') {
        initializeChartsWithServerData();
    }
});