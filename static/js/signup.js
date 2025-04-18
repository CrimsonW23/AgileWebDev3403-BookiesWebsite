// Validate passwords match before submitting and handle form submission
document.addEventListener("DOMContentLoaded", () => {
    const signupForm = document.getElementById("signup-form");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirm-password");
    const passwordError = document.getElementById("password-error");

    signupForm.addEventListener("submit", (event) => {
        event.preventDefault(); // Prevent default form submission

        if (password.value !== confirmPassword.value) {
            passwordError.style.display = "block"; // Show error message
            return;
        } else {
            passwordError.style.display = "none"; // Hide error message
        }

        const formData = new FormData(signupForm);

        fetch('/signup', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/dashboard'; // Redirect to dashboard on success
            } else {
                alert(data.message); // Show error message
            }
        })
        .catch(error => console.error("Error during signup:", error));
    });
});