document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput'); // Search input field
    const betCards = Array.from(document.querySelectorAll('.bet-card')); // All bet cards

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

// ===== PLACE BET FUNCTIONALITY =====

// Initialize place bet functionality
function initializePlaceBetForms() {
  document.querySelectorAll('.place-bet-form').forEach(form => {
      form.addEventListener('submit', function(event) {
          const stakeInput = this.querySelector('input[name="stake_amount"]');
          const maxStake = parseFloat(stakeInput.getAttribute('max'));
          const stakeAmount = parseFloat(stakeInput.value);
          
          if (stakeAmount > maxStake) {
              event.preventDefault();
              alert('Insufficient funds to place this bet.');
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