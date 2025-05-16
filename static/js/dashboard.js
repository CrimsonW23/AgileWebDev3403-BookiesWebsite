// Global variables
let countdownInterval; 
let statsChartInitialized = false;
let netProfitChartInstance = null; 
let winRateChartInstance = null;    
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
        if (netProfitChartInstance) netProfitChartInstance.destroy(); 
        if (winRateChartInstance) winRateChartInstance.destroy();      
        if (lineChartInstance) lineChartInstance.destroy();
        if (pieChartInstance) pieChartInstance.destroy();

        
        // NET PROFIT CHART 
        const netProfitContainer = document.querySelector('#netProfitChart').closest('.widget');
        if (chartData?.net_profit?.overall !== undefined && chartData.net_profit.overall !== null) {
            document.getElementById('netProfitChart').style.display = 'block';
            document.getElementById('netProfitChartMessage').style.display = 'none';
            netProfitChartInstance = createOverallNetProfitBar(
                chartData.net_profit.overall,
                chartData.net_profit.is_positive
            );
        } else {
            document.getElementById('netProfitChart').style.display = 'none';
            document.getElementById('netProfitChartMessage').textContent = 'No net profit recorded';
            document.getElementById('netProfitChartMessage').style.display = 'block';
            if (netProfitChartInstance) {
                netProfitChartInstance.destroy();
                netProfitChartInstance = null;
            }
        }

        // WIN RATE CHART 
        const winRateContainer = document.querySelector('#winRateChart').closest('.widget');
        if (chartData?.win_rate?.rate !== undefined && chartData.win_rate.rate !== null) {
            document.getElementById('winRateChart').style.display = 'block';
            document.getElementById('winRateChartMessage').style.display = 'none';
            winRateChartInstance = createOverallWinRateChart(chartData.win_rate);
        } else {
            document.getElementById('winRateChart').style.display = 'none';
            document.getElementById('winRateChartMessage').textContent = 'No win rate recorded';
            document.getElementById('winRateChartMessage').style.display = 'block';
            if (winRateChartInstance) {
                winRateChartInstance.destroy();
                winRateChartInstance = null;
            }
        }

        // LINE CHART 
        const hasMonthlyData = chartData && 
                              chartData.monthly_wins && 
                              chartData.monthly_wins.months && 
                              chartData.monthly_wins.months.length > 0 &&
                              chartData.monthly_wins.wins.some(win => win > 0);
        if (hasMonthlyData) {
            document.getElementById('lineChart').style.display = 'block';
            document.getElementById('lineChartMessage').style.display = 'none';
            lineChartInstance = createLineChart(chartData.monthly_wins);
        } else {
            document.getElementById('lineChart').style.display = 'none';
            document.getElementById('lineChartMessage').textContent = 'No wins recorded for previous months';
            document.getElementById('lineChartMessage').style.display = 'block';
        }

        // PIE CHART 
        const hasWinLossData = chartData && 
                              chartData.win_loss_ratio && 
                              (chartData.win_loss_ratio.wins > 0 || chartData.win_loss_ratio.losses > 0);
        if (hasWinLossData) {
            document.getElementById('pieChart').style.display = 'block';
            document.getElementById('pieChartMessage').style.display = 'none';
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

// Helper function to show "no stats" message
function renderNoStatsMessage() {
    document.querySelectorAll('.widget canvas').forEach(canvas => {
        canvas.style.display = 'none';
    });
    document.querySelectorAll('.fallback-message').forEach(msg => {
        msg.textContent = 'No statistics data available';
        msg.style.display = 'block';
    }); 
 
        }
 
// Create a horizontal bar chart for "Overall Net Profit"
function createOverallNetProfitBar(overallNetProfit, isPositive) {
    const canvas = document.getElementById('netProfitChart');
    const ctx = canvas.getContext('2d');

    // Determine the color based on the isPositive flag
    const displayColor = isPositive ? '#158c35' : '#ce2d22'; // Green for positive, red for negative 
    
    // Determine the display symbol for the value (+ or - or empty)
    const displaySymbol = isPositive ? '+' : '-';

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [''],  
            datasets: [{
                data: [Math.abs(overallNetProfit)],  
                backgroundColor: displayColor,  
                borderColor: displayColor, 
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },  
                tooltip: {
                    callbacks: {
                        label: function (context) { 
                            return `Net Profit: ${displaySymbol}$${Math.abs(context.raw)}`;
                        }
                    }
                },
                title: {
                    display: true,
                    text: `Net Profit: ${displaySymbol}$${Math.abs(overallNetProfit)}`,  
                    font: {
                        size: 16
                    },
                    color: displayColor  
                }
            },
            indexAxis: 'y',  
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Amount ($)'
                    },
                    ticks: {
                        callback: function (value) {
                            return `$${value}`; 
                        }
                    }, 
                    suggestedMin: 0
                },
                y: {
                    title: {
                        display: true,
                        text: 'Net Profit'
                    }
                }
            }
        }
    });
}

// Create a doughnut chart for "Overall Win Rate"
function createOverallWinRateChart(data) {
    const canvas = document.getElementById('winRateChart');
    const ctx = canvas.getContext('2d');
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Wins', 'Losses'],
            datasets: [{
                data: [data.wins || 0, data.losses || 0],
                backgroundColor: ['#158c35', '#ce2d22'],
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
                borderColor: 'rgb(49, 169, 69)',
                backgroundColor: 'rgba(26, 219, 84, 0.2)',
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
                backgroundColor: ['#158c35', '#ce2d22'],
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
            console.log("Raw data:", data);
            updateDashboardTables(data); // Update all tables
            initializeTimeRemaining(); // Reinitialize countdown logic
            
        })
        .catch(error => console.error('Error fetching dashboard data:', error));
}

// Periodically refresh the dashboard data
setInterval(() => {
    refreshDashboardData();
}, 30000); // Refresh every 10 seconds

 
// Update all dashboard tables with data
function updateDashboardTables(data) {
    // Format date and time
    function formatDateTime(datetimeStr) {
        try {
            const d = new Date(datetimeStr);
            if (isNaN(d.getTime())) return 'Invalid Date';
            const pad = n => String(n).padStart(2, '0');
            return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
        } catch (e) {
            console.error('Error formatting date:', datetimeStr, e);
            return 'Invalid Date';
        }
    }

    // Sort Ongoing Bets by time remaining (ascending - soonest ending first)
    const sortedOngoingBets = (data.ongoing_bets || []).sort((a, b) => {
        const endTimeA = new Date(a.scheduled_time).getTime() + a.duration * 60 * 60 * 1000;
        const endTimeB = new Date(b.scheduled_time).getTime() + b.duration * 60 * 60 * 1000;
        const timeRemainingA = endTimeA - Date.now();
        const timeRemainingB = endTimeB - Date.now();
        return timeRemainingA - timeRemainingB; // Ascending order
    });

    // Sort Upcoming Bets by scheduled time (soonest first)
    const sortedUpcomingBets = data.upcoming_bets.sort((a, b) => new Date(a.scheduled_time) - new Date(b.scheduled_time));
    const sortedUpcomingBetswidget = data.upcoming_bets.sort((a, b) => new Date(a.scheduled_time) - new Date(b.scheduled_time));
    console.log(sortedUpcomingBetswidget);
    // Sort Past Bets by date settled (latest finished first)
    const sortedPastBets = data.past_bets.sort((a, b) => new Date(b.date_settled) - new Date(a.date_settled));

    // Update Ongoing Bets table
    updateTable(
        '#mybets .widget:nth-child(2) table tbody',
        sortedOngoingBets,
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
        '#mybets .widget:nth-child(3) table tbody',
        sortedUpcomingBetswidget,
        bet => `
        <tr data-bet-id="${bet.id}" data-max-stake="${bet.max_stake}">
            <td>${bet.event_name}</td>
            <td>${bet.bet_type_description}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${formatDateTime(bet.scheduled_time)}</td>
            <td>$${bet.potential_winnings}</td>
        </tr>
        `,
        "No upcoming bets"
    );

    // Update Past Bets table
    updateTable(
        '#mybets .widget:nth-child(4) table tbody',
        sortedPastBets,
        bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type_description}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${bet.actual_winnings > 0 ? "Win" : "Loss"}</td>
            <td>$${bet.actual_winnings}</td>
            <td>${bet.date_settled ? formatDateTime(bet.date_settled) : 'N/A'}</td>
        </tr>
        `,
        "No past bets"
    );

    

    // Update Upcoming Bets table
    updateTable(
        '#upcoming tbody',
        sortedUpcomingBets,
        bet => `
        <tr data-bet-id="${bet.id}" data-max-stake="${bet.max_stake}">
            <td>${bet.event_name}</td>
            <td>${bet.bet_type_description}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${formatDateTime(bet.scheduled_time)}</td>
            <td>$${bet.potential_winnings}</td>
        </tr>
        `,
        "No upcoming bets"
    );

    

    // Update Past Bets table
    updateTable(
        '#past tbody',
        sortedPastBets,
        bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type_description}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${bet.actual_winnings > 0 ? "Win" : "Loss"}</td>
            <td>$${bet.actual_winnings}</td>
            <td>${bet.date_settled ? formatDateTime(bet.date_settled) : 'N/A'}</td>
        </tr>
        `,
        "No past bets"
    );

    // Sort Created Bets by status (upcoming → ongoing → past) and then by time
    const sortedCreatedBets = data.created_bets.sort((a, b) => {
        // First sort by status priority
        const statusOrder = { 'upcoming': 1, 'ongoing': 2, 'past': 3 };
        const statusComparison = statusOrder[a.status] - statusOrder[b.status];
        if (statusComparison !== 0) return statusComparison;
        
        // Then sort by time within each status group
        if (a.status === 'past') {
            // For past bets, show most recent first
            return new Date(b.scheduled_time) - new Date(a.scheduled_time);
        } else {
            // For upcoming/ongoing, show soonest first
            return new Date(a.scheduled_time) - new Date(b.scheduled_time);
        }
    });

    // Update Created Bets table
    updateTable(
        '#created-body',
        sortedCreatedBets,
        bet => `
        <tr>
            <td>${bet.event_name}</td>
            <td>${bet.bet_type_description}</td>
            <td>${bet.bet_type}</td>
            <td>$${bet.max_stake || bet.stake_amount}</td>
            <td>${bet.odds}</td>
            <td>${formatDateTime(bet.scheduled_time)}</td>
            <td>${bet.duration}</td>
            <td>${bet.status}</td>
        </tr>
        `,
        "No created bets"
    );
    applyRowClickHandlers()
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

function applyRowClickHandlers() {
    const closeModal = () => {
        document.getElementById('editBetModal').style.display = 'none';
    };

    // Store the clicked row reference for later update
    let currentEditedRow = null;

    // Make upcoming bets rows clickable
    document.querySelectorAll('#upcoming .widget-table tbody tr, #mybets .widget:nth-child(3) tbody tr').forEach(row => {
        row.style.cursor = 'pointer';
        
        row.addEventListener('click', (e) => {
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') return;
            
            const cells = row.cells;
            const betId = row.dataset.betId;
            console.log("Sending betId:", betId);
            const scheduledTime = new Date(cells[5].textContent);
            const currentTime = new Date();
            
            // Check if bet is editable
            if (scheduledTime <= currentTime) {
                alert("This bet can no longer be edited as it's in progress or completed.");
                return;
            }
            
            // Get max stake from the row data
            const maxStake = parseFloat(row.dataset.maxStake);

            // Populate modal
            document.getElementById('editBetId').value = betId;
            document.getElementById('editEventName').textContent = cells[0].textContent;
            document.getElementById('editBetType').textContent = cells[2].textContent;
            document.getElementById('editOdds').textContent = cells[4].textContent;
            document.getElementById('editScheduledTime').textContent = cells[5].textContent;
            document.getElementById('editStake').value = parseFloat(cells[3].textContent.replace('$', ''));
            document.getElementById('editMaxStake').value = maxStake;
            document.getElementById('maxStakeDisplay').textContent = maxStake.toFixed(2);
            
            // Set max attribute dynamically
            document.getElementById('editStake').max = maxStake;
            
            // Show modal
            document.getElementById('editBetModal').style.display = 'block';
        });
    });

    // Close modal when clicking X
    document.querySelector('.close-modal').addEventListener('click', closeModal);

    // Form submission handler
    document.getElementById('editBetForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const stakeInput = document.getElementById('editStake');
        const maxStake = parseFloat(document.getElementById('editMaxStake').value);
        const newStake = parseFloat(stakeInput.value);
        const betId = document.getElementById('editBetId').value;
        
        // Validate stake amount
        if (newStake > maxStake) {
            alert(`Stake cannot exceed $${maxStake.toFixed(2)}`);
            stakeInput.focus();
            return;
        }
        
        try {
            // 1. Check if user has enough currency
            const response = await fetch('/dashboard/check_currency', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    bet_id: betId,
                    new_stake: newStake
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to update bet');
            }
            
            if (!result.enough_currency) {
                alert("You don't have enough currency for this stake amount");
                return;
            }
            
            // 2. Update the bet in database
            const updateResponse = await fetch('/dashboard/update_bet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    bet_id: betId,
                    new_stake: newStake
                })
            });
            
            const updateResult = await updateResponse.json();
            
            if (!updateResponse.ok) {
                throw new Error(updateResult.error || 'Failed to update bet');
            }
            
            // 3. Update the frontend display
            if (currentEditedRow) {
                // Update stake amount cell
                currentEditedRow.cells[3].textContent = `$${newStake.toFixed(2)}`;
                
                // Update potential winnings if needed
                const odds = parseFloat(currentEditedRow.cells[4].textContent);
                currentEditedRow.cells[6].textContent = `$${(newStake * odds).toFixed(2)}`;
            }
            
            // Refresh dashboard data
            refreshDashboardData();
            
            // Close modal
            closeModal();
            
        } catch (error) {
            console.error('Error updating bet:', error);
            alert('Failed to update bet. Please try again.');
        }
    });
}