document.addEventListener('DOMContentLoaded', () => {
    const stakeAmountInput = document.getElementById('stake-amount'); // Stake Amount input
    const oddsInput = document.getElementById('odds'); // Odds input
    const potentialWinningsInput = document.getElementById('potential-winnings'); // Potential Winnings input
    const form = document.getElementById('create-bet-form'); // Form element

    // Function to calculate potential winnings dynamically
    function calculatePotentialWinnings() {
        const stakeAmount = parseFloat(stakeAmountInput.value) || 0; // Get Stake Amount or default to 0
        const odds = parseFloat(oddsInput.value) || 0; // Get Odds or default to 0
        const potentialWinnings = stakeAmount * odds; // Calculate Potential Winnings

        potentialWinningsInput.value = potentialWinnings.toFixed(2); // Display with 2 decimal places
    }

    // Add event listeners to update potential winnings when inputs change
    stakeAmountInput.addEventListener('input', calculatePotentialWinnings);
    oddsInput.addEventListener('input', calculatePotentialWinnings);

    // Handle form submission
    form.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent default form submission behavior

        // Collect form data
        const eventName = document.getElementById('event-name').value;
        const betType = document.getElementById('bet-type').value;
        const stakeAmount = parseFloat(stakeAmountInput.value);
        const odds = parseFloat(oddsInput.value);
        const potentialWinnings = parseFloat(potentialWinningsInput.value);
        const scheduledTime = document.getElementById('scheduled-time').value;

        // Send form data to the server
        fetch('/create_bet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                event_name: eventName,
                bet_type: betType,
                stake_amount: stakeAmount,
                odds: odds,
                potential_winnings: potentialWinnings,
                scheduled_time: scheduledTime,
            }),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert('Bet placed successfully!');
                window.location.href = '/dashboard'; // Redirect to the dashboard
            } else {
                alert('Failed to place bet: ' + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while placing the bet.');
        });
    });
});