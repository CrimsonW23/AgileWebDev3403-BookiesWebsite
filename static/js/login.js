document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const username = document.getElementById('username');
    const password = document.getElementById('password');

    form.addEventListener('submit', (event) => {
        let isValid = true;

        // Validate username/email is not empty
        if (username.value.trim() === '') {
            alert('Username/Email is required.');
            isValid = false;
        }

        // Validate password is not empty
        if (password.value.trim() === '') {
            alert('Password is required.');
            isValid = false;
        }

        // Prevent form submission if validation fails
        if (!isValid) {
            event.preventDefault();
            return;
        }

        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(form);

        fetch('/login', {
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
        .catch(error => console.error("Error during login:", error));
    });
});