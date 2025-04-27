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
  
  