document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const errorContainer = document.getElementById('form-errors');
    
    const showError = (message) => {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    };
    
    const clearErrors = () => {
        errorContainer.textContent = '';
        errorContainer.style.display = 'none';
    };
    
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        clearErrors();
        
        if (!form.username.value.trim() || !form.password.value.trim()) {
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
            
            if (!data.success) {
                showError(data.message || 'Login failed');
                return;
            }
            
            window.location.href = data.redirect;
        } catch (error) {
            console.error("Error:", error);
            showError("An unexpected error occurred. Please try again.");
        }
    });
});