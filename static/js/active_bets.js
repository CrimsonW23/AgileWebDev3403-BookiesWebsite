document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput'); 
    const betCards = Array.from(document.querySelectorAll('.bet-card'));  

    // Add an event listener to the search input
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase(); // Get the search query in lowercase

        // Loop through all bet cards and check if they match the query
        betCards.forEach(card => {
            const matches = card.dataset.search.toLowerCase().includes(query); // Check if the query matches the card's data-search attribute
            card.style.display = matches ? '' : 'none'; // Show or hide the card based on the match
            });
        });
    });
 
// Initialize place bet functionality
function initializePlaceBetForms() {
  document.querySelectorAll('.place-bet-form').forEach(form => {
      form.addEventListener('submit', function(event) {
        const stakeInput = this.querySelector('input[name="stake_amount"]');
        const maxStake = parseFloat(this.querySelector('.max-stake-value').textContent);
        const stakeAmount = parseFloat(stakeInput.value);
        
        if (isNaN(stakeAmount)) {
            event.preventDefault();
            alert('Please enter a valid number');
            return;
        }

        if (stakeAmount > maxStake) {
            event.preventDefault();
            alert(`Stake amount cannot exceed $${maxStake}`);
            return;
        }

        if (stakeAmount <= 0) {
            event.preventDefault();
            alert('Stake amount must be greater than 0');
            return;
        }
      });
  });
} 

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Determine current page
  const currentPath = window.location.pathname;
  
  if (currentPath.includes('/active_bets')) {
      initializePlaceBetForms();
  }
})