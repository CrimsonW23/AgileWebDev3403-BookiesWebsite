document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const betCards = Array.from(document.querySelectorAll('.bet-card'));

    searchInput.addEventListener('input', () => {
      const query = searchInput.value.toLowerCase();

      betCards.forEach(card => {
        const matches = card.dataset.search.toLowerCase().includes(query);
        card.style.display = matches ? '' : 'none';
      });
    });
  });