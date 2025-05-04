let statsChartInitialized = false;
let countdownInterval; // Global interval variable

// Show the selected tab and hide others
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
    const activeTab = document.getElementById(tabId);
    if (activeTab) activeTab.style.display = 'block';

    document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
    const activeMenuItem = Array.from(document.querySelectorAll('.menu-item'))
        .find(item => item.getAttribute('onclick').includes(tabId));
    if (activeMenuItem) activeMenuItem.classList.add('active');

    if (tabId === 'stats' && !statsChartInitialized) {
        createLineChart();
        createPieChart();
        statsChartInitialized = true; // Prevent re-creating the chart
    }
}

// Refresh tables with updated data
function refreshTables() {
    fetch('/dashboard_data')
        .then(response => response.json())
        .then(data => {
            updateTable('#ubets tbody', data.upcoming_bets, bet => `
                <tr>
                    <td>${bet.event_name}</td>
                    <td>${bet.bet_type}</td>
                    <td>$${bet.stake_amount}</td>
                    <td>${bet.odds}</td>
                    <td>${bet.scheduled_time}</td>
                    <td>$${bet.potential_winnings}</td>
                </tr>
            `);

            updateTable('#overview .widget-table tbody', data.ongoing_bets, bet => `
                <tr>
                    <td>${bet.event_name}</td>
                    <td>${bet.bet_type}</td>
                    <td>$${bet.stake_amount}</td>
                    <td>${bet.odds}</td>
                    <td>${bet.potential_winnings}</td>
                    <td class="time-remaining" data-end-time="${bet.scheduled_time}" data-duration="${bet.duration}"></td>
                </tr>
            `);

            updateTable('#pbets tbody', data.past_bets, bet => `
                <tr>
                    <td>${bet.event_name}</td>
                    <td>${bet.bet_type}</td>
                    <td>$${bet.stake_amount}</td>
                    <td>${bet.odds}</td>
                    <td>${bet.actual_winnings > 0 ? "Win" : "Loss"}</td>
                    <td>$${bet.actual_winnings}</td>
                    <td>${bet.date_settled}</td>
                </tr>
            `);

            updateTable('#available-bets-table-body', data.available_bets, bet => `
                <tr>
                    <td>${bet.event_name}</td>
                    <td>
                        <a href="/place_bet_form/${bet.event_name}">
                            <button class="place-bet-btn">Place Bet</button>
                        </a>
                    </td>
                </tr>
            `);

            initializeTimeRemaining(); // Reinitialize countdown logic
        })
        .catch(error => console.error('Error fetching dashboard data:', error));
}

// Helper function to update table content
function updateTable(selector, data, rowTemplate) {
    const tableBody = document.querySelector(selector);
    tableBody.innerHTML = ''; // Clear existing rows
    data.forEach(item => tableBody.innerHTML += rowTemplate(item));
}

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

// Create a line chart for monthly wins
function createLineChart() {
    const canvas = document.getElementById('lineChart');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const data = [10, 15, 8, 20, 12]; // Fake winnings
    const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May'];

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
function createPieChart() {
    const canvas = document.getElementById('pieChart');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const data = [70, 30]; // Example: 70% Wins, 30% Losses
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

// Initialize countdown and refresh tables periodically
document.addEventListener('DOMContentLoaded', () => {
    initializeTimeRemaining();
    setInterval(refreshTables, 30000); // Refresh tables every 30 seconds
});


