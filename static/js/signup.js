document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('signup-form');
    const errorContainer = document.getElementById('form-errors');
    const dob = document.getElementById('dob');
    const phone = document.getElementById('phone');

    // Function to display error messages
    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    }

    // Function to clear error messages
    function clearError() {
        errorContainer.textContent = '';
        errorContainer.style.display = 'none';
    }

    // Disable future dates in the DOB field
    if (dob) {
        const today = new Date().toISOString().split('T')[0];
        dob.setAttribute('max', today);
    }

    // Real-time validation for phone input (only numeric, max 10 digits)
    if (phone) {
        phone.addEventListener('input', () => {
            phone.value = phone.value.replace(/\D/g, '').slice(0, 10);
        });
    }

    // Form submission handler
    if (form) {
        form.addEventListener('submit', (event) => {
            clearError();
            let isValid = true;

            // Check required fields
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    showError(`Please fill in the ${field.labels[0].textContent} field.`);
                    isValid = false;
                }
            });

            if (!isValid) {
                event.preventDefault();
            }
        });
    }
});