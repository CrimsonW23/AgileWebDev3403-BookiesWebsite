document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    
    const showError = (message) => {
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.color = 'red';
        form.insertBefore(errorDiv, form.firstChild);
    };
    
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        // Clear previous errors
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        
        // Basic validation
        if (!username.value.trim() || !password.value.trim()) {
            showError('Please fill in all fields');
            return;
        }
        
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams(new FormData(form))
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                // Handle validation errors
                if (data.errors) {
                    for (const field in data.errors) {
                        showError(data.errors[field][0]);
                    }
                } else {
                    showError(data.message || 'Login failed');
                }
                return;
            }
            
            if (data.success) {
                window.location.href = data.redirect;
            } else {
                showError(data.message || 'Login failed');
            }
        } catch (error) {
            console.error("Error:", error);
            showError("An unexpected error occurred. Please try again.");
        }
    });
});