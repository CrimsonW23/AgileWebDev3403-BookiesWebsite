// Global variables 
let statsChartInitialized = false;
let countdownInterval;

// ===== DASHBOARD PAGE FUNCTIONALITY =====

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
    if (tabId === 'stats' && !statsChartInitialized) {
        fetchStatsData()
            .then(data => {
                createLineChart(data.monthly_wins);
                createPieChart(data.win_loss_ratio);
                statsChartInitialized = true;
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
            updateDashboardTables(data);
            initializeTimeRemaining(); // Reinitialize countdown logic
        })
        .catch(error => console.error('Error fetching dashboard data:', error));
}

// Update all dashboard tables with data
function updateDashboardTables(data) {
    // Update Ongoing Bets table
    updateTable('#ongoing .widget-table tbody', data.ongoing_bets, bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>$${bet.potential_winnings}</td>
            <td class="time-remaining" data-end-time="${bet.scheduled_time}" data-duration="${bet.duration}"></td>
        </tr>
    `);

    // Update Upcoming Bets table
    updateTable('#upcoming tbody', data.upcoming_bets, bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${new Date(bet.scheduled_time).toLocaleString()}</td>
            <td>$${bet.potential_winnings}</td>
        </tr>
    `);

    // Update Past Bets table
    updateTable('#past tbody', data.past_bets, bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${bet.actual_winnings > 0 ? "Win" : "Loss"}</td>
            <td>$${bet.actual_winnings}</td>
            <td>${bet.date_settled ? new Date(bet.date_settled).toLocaleString() : 'N/A'}</td>
        </tr>
    `);

    // Update Created Bets table
    updateTable('#created-body', data.created_bets, bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.max_stake || bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${new Date(bet.scheduled_time).toLocaleString()}</td>
            <td>${bet.duration}</td>
        </tr>
    `);
}

// Helper function to update table content
function updateTable(selector, data, rowTemplate) {
    const tableBody = document.querySelector(selector);
    if (!tableBody) return; // Skip if table doesn't exist on current page
    
    tableBody.innerHTML = ''; // Clear existing rows
    
    if (data && data.length > 0) {
        data.forEach(item => tableBody.innerHTML += rowTemplate(item));
    } else {
        // Show "No data" message
        const columnCount = tableBody.closest('table').querySelectorAll('thead th').length;
        tableBody.innerHTML = `<tr><td colspan="${columnCount}" class="no-data">No bets found</td></tr>`;
    }
}

// ===== TIME REMAINING FUNCTIONALITY =====

// Initialize countdown for "Time Remaining" cells
function initializeTimeRemaining() {
    if (countdownInterval) clearInterval(countdownInterval);

    countdownInterval = setInterval(() => {
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
                cell.textContent = "0h 0m 0s";
            } else {
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                cell.textContent = `${hours}h ${minutes}m ${seconds}s`;
            }
        });
    }, 1000); // Update every second
}

// ===== STATISTICS CHARTS =====

// Fetch stats data from server
function fetchStatsData() {
    // In a real app, this would fetch from an endpoint like '/dashboard/stats'
    // For now, we'll use dummy data to match the backend structure
    return new Promise((resolve) => {
        // Sample data - in real app would come from server
        const data = {
            monthly_wins: [
                { month: 'Jan', winnings: 10 },
                { month: 'Feb', winnings: 15 },
                { month: 'Mar', winnings: 8 },
                { month: 'Apr', winnings: 20 },
                { month: 'May', winnings: 12 }
            ],
            win_loss_ratio: {
                wins: 70,
                losses: 30
            }
        };
        resolve(data);
    });
}

// Create a line chart for monthly wins
function createLineChart(monthlyData) {
    const canvas = document.getElementById('lineChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Extract data from monthlyData
    const data = monthlyData.map(item => item.winnings);
    const labels = monthlyData.map(item => item.month);

    // Draw axes
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(30, 10);
    ctx.lineTo(30, 190);
    ctx.lineTo(390, 190);
    ctx.stroke();

    // Plot data points
    ctx.beginPath();
    ctx.strokeStyle = '#4caf50';
    ctx.lineWidth = 2;
    data.forEach((value, index) => {
        const x = 50 + index * 70;
        const y = 190 - value * 5;
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);

        // Draw point
        ctx.fillStyle = '#4caf50';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();

        // Add label
        ctx.fillStyle = '#fff';
        ctx.font = '12px Arial';
        ctx.fillText(value, x - 10, y - 10);
    });
    ctx.stroke();

    // Add month labels
    ctx.fillStyle = '#aaa';
    ctx.font = '12px Arial';
    labels.forEach((label, index) => {
        const x = 50 + index * 70;
        ctx.fillText(label, x - 10, 210);
    });
}

// Create a pie chart for win/loss ratio
function createPieChart(ratioData) {
    const canvas = document.getElementById('pieChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const data = [ratioData.wins, ratioData.losses]; // Win/Loss percentages
    const colors = ['#4caf50', '#f44336'];
    const labels = ['Wins', 'Losses'];

    let total = data.reduce((a, b) => a + b, 0);
    let startAngle = 0;

    // Draw pie slices
    data.forEach((value, index) => {
        const sliceAngle = (value / total) * 2 * Math.PI;
        ctx.beginPath();
        ctx.moveTo(150, 150);
        ctx.arc(150, 150, 100, startAngle, startAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = colors[index];
        ctx.fill();
        startAngle += sliceAngle;
    });

    // Add legend
    let legendY = 250;
    labels.forEach((label, index) => {
        ctx.fillStyle = colors[index];
        ctx.fillRect(10, legendY, 20, 20);
        ctx.fillStyle = '#000';
        ctx.fillText(`${label}: ${data[index]}%`, 40, legendY + 15);
        legendY += 30;
    });
} 

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Determine current page
    const currentPath = window.location.pathname;
    
    // Initialize functionality based on current page
    if (currentPath.includes('/dashboard')) {
        refreshDashboardData();
        initializeTimeRemaining();
        setInterval(refreshDashboardData, 30000); 
    }})