let statsChartInitialized = false;

function showTab(tabId) {
    // Hide all tab contents
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.style.display = 'none');

    // Show the selected tab content
    const activeTab = document.getElementById(tabId);
    if (activeTab) {
        activeTab.style.display = 'block';
    }

    // Remove "active" class from all menu items
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => item.classList.remove('active'));

    // Add "active" class to the clicked menu item
    // Find the menu-item whose onclick attribute matches the tabId
    const activeMenuItem = Array.from(menuItems).find(item => item.getAttribute('onclick').includes(tabId));
    if (activeMenuItem) {
        activeMenuItem.classList.add('active');
    }

    if (tabId === 'stats' && !statsChartInitialized) {
        createLineChart();
        createPieChart();
        statsChartInitialized = true; // Prevent re-creating the chart every click
    }
}

function initializeTimeRemaining() {
  const timeRemainingCells = document.querySelectorAll('.time-remaining');

  timeRemainingCells.forEach(cell => {
      const endTime = new Date(cell.getAttribute('data-end-time'));
      const duration = parseInt(cell.getAttribute('data-duration')) * 60 * 60 * 1000; // Convert hours to milliseconds
      const finalEndTime = new Date(endTime.getTime() + duration);

      const interval = setInterval(() => {
          const now = new Date();
          const diff = finalEndTime - now;

          if (diff <= 0) {
              cell.textContent = "0h 0m 0s";
              clearInterval(interval);
          } else {
              const hours = Math.floor(diff / (1000 * 60 * 60));
              const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
              const seconds = Math.floor((diff % (1000 * 60)) / 1000);
              cell.textContent = `${hours}h ${minutes}m ${seconds}s`;
          }
      }, 1000);
  });
}

// Initialize time remaining logic on page load
document.addEventListener('DOMContentLoaded', initializeTimeRemaining);

function refreshTables() {
  fetch('/dashboard_data')  // Fetch updated bet data from the backend
      .then(response => response.json())
      .then(data => {
          
          // Update Upcoming Bets Table
          const upcomingTableBody = document.querySelector('#ubets tbody');
          upcomingTableBody.innerHTML = ''; // Clear existing rows
          data.upcoming_bets.forEach(bet => {
              const row = `
                  <tr>
                      <td>${bet.event_name}</td>
                      <td>${bet.bet_type}</td>
                      <td>$${bet.stake_amount}</td>
                      <td>${bet.odds}</td>
                      <td>${bet.scheduled_time}</td>
                      <td>$${bet.potential_winnings}</td>
                  </tr>
              `;
              upcomingTableBody.innerHTML += row;
          });

          // Update Ongoing Bets Table
          const ongoingTableBody = document.querySelector('#overview .widget-table tbody');
          ongoingTableBody.innerHTML = ''; // Clear existing rows
          data.ongoing_bets.forEach(bet => {
              const row = `
                  <tr>
                      <td>${bet.event_name}</td>
                      <td>${bet.bet_type}</td>
                      <td>$${bet.stake_amount}</td>
                      <td>${bet.odds}</td>
                      <td>$${bet.potential_winnings}</td>
                      <td class="time-remaining" data-end-time="${bet.scheduled_time}" data-duration="${bet.duration}"></td>
                  </tr>
              `;
              ongoingTableBody.innerHTML += row;
          });

          // Update Past Bets Table
          const pastTableBody = document.querySelector('#pbets tbody');
          pastTableBody.innerHTML = ''; // Clear existing rows
          data.past_bets.forEach(bet => {
              const row = `
                  <tr>
                      <td>${bet.event_name}</td>
                      <td>${bet.bet_type}</td>
                      <td>$${bet.stake_amount}</td>
                      <td>${bet.odds}</td>
                      <td>${bet.actual_winnings > 0 ? "Win" : "Loss"}</td>
                      <td>$${bet.actual_winnings}</td>
                      <td>${bet.date_settled}</td>
                  </tr>
              `;
              pastTableBody.innerHTML += row;
          });
          
          // Update Available Bets Table
          const availableTableBody = document.querySelector('#available-bets-table-body');
          availableTableBody.innerHTML = ''; // Clear existing rows
          data.available_bets.forEach(bet => {
              const row = `
                  <tr>
                      <td>${bet.event_name}</td>
                      <td>
                          <a href="/place_bet_form/${bet.event_name}">
                              <button class="place-bet-btn">Place Bet</button>
                          </a>
                      </td>
                  </tr>
              `;
              availableTableBody.innerHTML += row;
          });

          // Reinitialize time remaining logic
          initializeTimeRemaining();
      })
      .catch(error => console.error('Error fetching dashboard data:', error));
}

// Call refreshTables every 30 seconds
setInterval(refreshTables, 30000);

function fetchEventOutcome(eventName) {
  // Query the EventResult table for the given event name
  const eventResult = EventResult.query.filterBy(event_name=eventName).first();
  if (eventResult) {
      return eventResult.outcome; // Return the outcome (e.g., "win" or "loss")
  }
  return null; // Return null if the event result is not found
}

document.addEventListener("DOMContentLoaded", () => {
  // Data passed from the backend
  const monthlyWins = JSON.parse(document.getElementById("monthlyWinsData").textContent);
  const winLossRatio = JSON.parse(document.getElementById("winLossRatioData").textContent);

});

function createLineChart() {
    const canvas = document.getElementById('lineChart');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  
    const data = [10, 15, 8, 20, 12]; // Fake winnings
    const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May'];
  
    // Axis settings
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(30, 10);
    ctx.lineTo(30, 190);
    ctx.lineTo(390, 190);
    ctx.stroke();
  
    // Plot points
    ctx.beginPath();
    ctx.strokeStyle = '#4caf50';
    ctx.lineWidth = 2;
  
    data.forEach((value, index) => {
      const x = 50 + index * 70;
      const y = 190 - value * 5;
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      // draw small dot
      ctx.fillStyle = '#4caf50';
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();
  
      // Add numerical label for each point
      ctx.fillStyle = '#fff'; // White for contrast
      ctx.font = '12px Arial';
      ctx.fillText(value, x - 10, y - 10); // Positioning label above the point
    });
  
    ctx.stroke();
  
    // Add labels for months
    ctx.fillStyle = '#aaa';
    ctx.font = '12px Arial';
    labels.forEach((label, index) => {
      const x = 50 + index * 70;
      ctx.fillText(label, x - 10, 210);
    });
}

function createPieChart() {
    const canvas = document.getElementById('pieChart');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  
    const data = [70, 30]; // Example: 70% Wins, 30% Losses
    const colors = ['#4caf50', '#f44336']; // green for wins, red for losses
    const labels = ['Wins', 'Losses'];
  
    let total = data.reduce((a, b) => a + b, 0);
    let startAngle = 0;
  
    // Create the pie slices
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
  
    // Add labels to the legend
    let legendY = 250;
    labels.forEach((label, index) => {
      ctx.fillStyle = colors[index];
      ctx.fillRect(10, legendY, 20, 20);
  
      ctx.fillStyle = '#aaa'; // lighter text
      ctx.font = '14px Arial';
      ctx.fillText(label, 40, legendY + 15);
  
      legendY += 30;
    });
}

