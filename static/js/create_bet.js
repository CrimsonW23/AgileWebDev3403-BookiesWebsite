document.addEventListener('DOMContentLoaded', function () {
    const scheduledTimeInput = document.getElementById('scheduled_time');

    // Set the minimum value for the scheduled time to the current local time
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are 0-based
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');

    const localDateTime = `${year}-${month}-${day}T${hours}:${minutes}`; // Format as YYYY-MM-DDTHH:MM
    scheduledTimeInput.setAttribute('min', localDateTime);

    // Add an event listener to validate the input
    document.getElementById('create-bet-form').addEventListener('submit', function (event) {
        const selectedTime = new Date(scheduledTimeInput.value);
        const currentTime = new Date();

        if (selectedTime <= currentTime) {
            alert('Scheduled time must be in the future.');
            event.preventDefault(); 
        }
    });
});

const form = document.getElementById('create-bet-form');  
const eventNameInput = document.getElementById('event-name');  
const betTypeInput = document.getElementById('bet-type'); 
const stakeAmountInput = document.getElementById('stake-amount');  
const oddsInput = document.getElementById('odds');   

// Handle form submission
form.addEventListener('submit', (event) => { 
    // Collect form data
    const eventName = eventNameInput.value.trim();
    const betType = betTypeInput.value.trim();
    const stakeAmount = parseFloat(stakeAmountInput.value);
    const odds = parseFloat(oddsInput.value);
    const scheduledTime = scheduledTimeInput.value;

    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const currentTime = `${year}-${month}-${day}T${hours}:${minutes}`; // Current time in "YYYY-MM-DDTHH:mm" format

    if (scheduledTimeInput.value === '' || scheduledTimeInput.value < currentTime) {
        alert('Please enter a valid scheduled time in the future.');
        event.preventDefault();
        return;
    }

    if (!eventName || !betType || isNaN(stakeAmount) || isNaN(odds)) {
        alert('All fields are required and must be valid.');
        event.preventDefault();
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