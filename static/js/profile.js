document.addEventListener("DOMContentLoaded", () => {
    console.log("User profile JS loaded");

    const toggleInputs = document.querySelectorAll(".toggle-switch input");

    toggleInputs.forEach(toggle => {
        toggle.addEventListener("change", () => {
            const label = toggle.closest(".toggle-group").querySelector("label").innerText;
            const state = toggle.checked ? "ON" : "OFF";
            console.log(`Privacy toggle for "${label}" is now ${state}`);
            // Optionally send to server via fetch() here
        });
    });

    const saveButton = document.querySelector(".profile-button");

    if (saveButton) {
        saveButton.addEventListener("click", () => {
            // Example of collecting input data
            const inputs = document.querySelectorAll(".profile-section input, .profile-section select, .profile-section textarea");
            let profileData = {};

            inputs.forEach(input => {
                if (input.name) {
                    profileData[input.name] = input.value;
                }
            });

            console.log("Saving user profile data:", profileData);

            // Simulate API call
            alert("Changes saved successfully!");
            // Replace alert with actual fetch() or AJAX call as needed
        });
    }

    const checkbox = document.getElementById("show-email");
    const emailDisplay = document.getElementById("email-input");
    const statsCheckbox = document.getElementById("show-stats");
    const pastBetsCheckbox = document.getElementById("show-bets");

    function toggleVisibility(inputType) {
        if (inputType == 'email'){
            emailDisplay.value = checkbox.checked ? userEmail : "*****";
        }
        else if (inputType == 'stats'){
            document.getElementById("stats-totalBets").value = statsCheckbox.checked ? userStats.totalBets : "*****";
            document.getElementById("stats-wins").value = statsCheckbox.checked ? userStats.wins : "*****";
            document.getElementById("stats-biggestWin").value = statsCheckbox.checked ? userStats.biggestWin : "*****";
            document.getElementById("stats-winRate").value = statsCheckbox.checked ? `${((userStats.wins / userStats.totalBets) * 100).toFixed(2)}%` : "*****";
        }
        else if (inputType === 'past-bets') {
            for (let i = 0; i < userBets.length; i++) {
                document.getElementById(`bet-game-${i}`).textContent = pastBetsCheckbox.checked ? userBets[i].game : "*****";
                document.getElementById(`bet-amount-${i}`).textContent = pastBetsCheckbox.checked ? `$${userBets[i].amount}` : "*****";
                document.getElementById(`bet-outcome-${i}`).textContent = pastBetsCheckbox.checked ? userBets[i].outcome : "*****";
                document.getElementById(`bet-date-${i}`).textContent = pastBetsCheckbox.checked ? userBets[i].date : "*****";
        
                // Changes outcome color based on win/loss
                const outcomeEl = document.getElementById(`bet-outcome-${i}`);
                outcomeEl.classList.remove("win", "loss");
                if (pastBetsCheckbox.checked) {
                    outcomeEl.classList.add(userBets[i].outcome === "Won" ? "win" : "loss");
                }
            }
        }
    }

    checkbox.addEventListener("change", () => toggleVisibility('email'));
    statsCheckbox.addEventListener("change", () => toggleVisibility('stats'));
    pastBetsCheckbox.addEventListener("change", () => toggleVisibility('past-bets'));

    toggleVisibility('email');
    toggleVisibility('stats');
    toggleVisibility('past-bets');

});

