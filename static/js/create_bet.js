document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('create-bet-form'); // Form element
    const eventNameInput = document.getElementById('event-name'); // Event Name input
    const betTypeInput = document.getElementById('bet-type'); // Bet Type dropdown
    const stakeAmountInput = document.getElementById('stake-amount'); // Stake Amount input
    const oddsInput = document.getElementById('odds'); // Odds input
    const scheduledTimeInput = document.getElementById('scheduled-time'); // Scheduled Time input

    // Handle form submission
    form.addEventListener('submit', (event) => { 

        // Collect form data
        const eventName = eventNameInput.value.trim();
        const betType = betTypeInput.value.trim();
        const stakeAmount = parseFloat(stakeAmountInput.value);
        const odds = parseFloat(oddsInput.value);
        const scheduledTime = scheduledTimeInput.value;
        
        const currentTime = new Date().toISOString().slice(0, 16); // Current time in "YYYY-MM-DDTHH:mm" format
        if (scheduledTimeInput.value === '' || scheduledTimeInput.value < currentTime) {
            alert('Please enter a valid scheduled time in the future.');
            return;
        }

        if (!eventName || !betType || isNaN(stakeAmount) || isNaN(odds)) {
            alert('All fields are required and must be valid.');
            return;
        }

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
                scheduled_time: scheduledTime,
            }),
        });

        // Redirect to the dashboard after submission
        window.location.href = '/dashboard';
    });
});