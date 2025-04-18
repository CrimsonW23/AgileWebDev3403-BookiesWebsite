document.addEventListener("DOMContentLoaded", () => {
    // Highlight the active navigation link
    const navLinks = document.querySelectorAll("nav a");
    navLinks.forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add("active");
        }
    });

    // Fetch and update stats dynamically
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById("total-users").textContent = data.totalUsers || "N/A";
            document.getElementById("total-bets").textContent = data.totalBets || "N/A";
            document.getElementById("total-wins").textContent = data.totalWins || "N/A";
            document.getElementById("biggest-win").textContent = `$${data.biggestWin || "N/A"}`;
        })
        .catch(error => {
            console.error("Error fetching stats:", error);
            document.getElementById("total-users").textContent = "Error";
            document.getElementById("total-bets").textContent = "Error";
            document.getElementById("total-wins").textContent = "Error";
            document.getElementById("biggest-win").textContent = "Error";
        });
});