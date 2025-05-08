document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('signup-form');
    const email = document.getElementById('email');
    const emailError = document.getElementById('email-error');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm-password');
    const passwordError = document.getElementById('password-error');
    const dob = document.getElementById('dob');
    const dobError = document.getElementById('dob-error');
    const phone = document.getElementById('phone');
    const phoneError = document.getElementById('phone-error');

    // Disable future dates in the DOB calendar
    const today = new Date().toISOString().split('T')[0];
    dob.setAttribute('max', today);

    form.addEventListener('submit', (event) => {
        let isValid = true;

        // Validate email format
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Basic email regex
        if (!emailPattern.test(email.value)) {
            emailError.textContent = 'Please enter a valid email address.';
            emailError.style.display = 'block';
            isValid = false;
        } else {
            emailError.style.display = 'none';
        }

        // Validate passwords match and are at least 6 characters
        if (password.value.length < 6) {
            passwordError.textContent = 'Password must be at least 6 characters long.';
            passwordError.style.display = 'block';
            isValid = false;
        } else if (password.value !== confirmPassword.value) {
            passwordError.textContent = 'Passwords do not match.';
            passwordError.style.display = 'block';
            isValid = false;
        } else {
            passwordError.style.display = 'none';
        }

        // Validate date of birth (must be in the past)
        const dobDate = new Date(dob.value);
        if (dobDate >= new Date()) {
            dobError.textContent = 'Date of birth must be in the past.';
            dobError.style.display = 'block';
            isValid = false;
        } else {
            dobError.style.display = 'none';
        }

        // Validate phone number (must be exactly 10 digits)
        if (!/^\d{10}$/.test(phone.value)) {
            phoneError.textContent = 'Phone number must be exactly 10 digits.';
            phoneError.style.display = 'block';
            isValid = false;
        } else {
            phoneError.style.display = 'none';
        }

        // Prevent form submission if any validation fails
        if (!isValid) {
            event.preventDefault();
        }
    });

    // Restrict phone input to digits only and limit to 10 characters
    phone.addEventListener('input', () => {
        phone.value = phone.value.replace(/\D/g, ''); // Remove non-digit characters
        if (phone.value.length > 10) {
            phone.value = phone.value.slice(0, 10); // Limit to 10 digits
        }
    });
});