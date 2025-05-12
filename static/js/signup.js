document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('signup-form');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm-password');
    const passwordError = document.getElementById('password-error');
    const dob = document.getElementById('dob');
    const dobError = document.getElementById('dob-error');
    const phone = document.getElementById('phone');
    const phoneError = document.getElementById('phone-error');
    
    // Create email error element if it doesn't exist
    let emailError = document.getElementById('email-error');
    if (!emailError) {
        emailError = document.createElement('p');
        emailError.id = 'email-error';
        emailError.style.color = 'red';
        emailError.style.display = 'none';
        email.parentNode.appendChild(emailError);
    }
    
    // Ensure all form fields have proper IDs
    const formFields = form.querySelectorAll('input, select');
    formFields.forEach(field => {
        if (!field.id && field.name) {
            field.id = field.name;
        }
    });
    
    // Disable future dates in the DOB calendar
    const today = new Date().toISOString().split('T')[0];
    if (dob) {
        dob.setAttribute('max', today);
    }
    
    form.addEventListener('submit', (event) => {
        let isValid = validateForm();
        
        // Check for DOB validation specifically
        if (dob && dob.value) {
            const dobDate = new Date(dob.value);
            if (dobDate >= new Date()) {
                dobError.textContent = 'Date of birth must be in the past.';
                dobError.style.display = 'block';
                isValid = false;
            }
        }
        
        if (!isValid) {
            event.preventDefault();
        } else {
            const csrfToken = document.querySelector('input[name="csrf_token"]');
            if (csrfToken) {
                csrfToken.disabled = false;
            }
            return true;
        }
    });
    
    function validateForm() {
        let isValid = true;
        
        // Validate email format
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (email && !emailPattern.test(email.value)) {
            emailError.textContent = 'Please enter a valid email address. Example: user@example.com';
            emailError.style.display = 'block';
            isValid = false;
        } else if (email) {
            emailError.style.display = 'none';
        }
        
        // Validate passwords match and are at least 6 characters
        if (password && password.value.length < 6) {
            passwordError.textContent = 'Password must be at least 6 characters long.';
            passwordError.style.display = 'block';
            isValid = false;
        } else if (password && confirmPassword && password.value !== confirmPassword.value) {
            passwordError.textContent = 'Passwords do not match.';
            passwordError.style.display = 'block';
            isValid = false;
        } else if (passwordError) {
            passwordError.style.display = 'none';
        }
        
        // Validate date of birth (must be in the past)
        if (dob && dob.value) {
            const dobDate = new Date(dob.value);
            if (dobDate >= new Date()) {
                dobError.textContent = 'Date of birth must be in the past.';
                dobError.style.display = 'block';
                isValid = false;
            } else if (dobError) {
                dobError.style.display = 'none';
            }
        }
        
        // Validate phone number (must be exactly 10 digits)
        if (phone && !/^\d{10}$/.test(phone.value)) {
            phoneError.textContent = 'Phone number must be exactly 10 digits.';
            phoneError.style.display = 'block';
            isValid = false; 
        } else if (phoneError) {
            phoneError.style.display = 'none';
        }
        
        // Check for CSRF token
        const csrfToken = document.querySelector('input[name="csrf_token"]');
        if (!csrfToken || !csrfToken.value) { 
            isValid = false;
        }
        
        // Check for any empty required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    // Real-time validation for phone input
    if (phone) {
        phone.addEventListener('input', () => {
            phone.value = phone.value.replace(/\D/g, '');  
            if (phone.value.length > 10) {
                phone.value = phone.value.slice(0, 10);  
            }
            
            // Show/hide error message in real-time
            if (phone.value.length !== 0 && phone.value.length !== 10) {
                phoneError.textContent = 'Phone number must be exactly 10 digits.';
                phoneError.style.display = 'block';
            } else {
                phoneError.style.display = 'none';
            }
        });
    }
    
    // Real-time validation for password matching
    function checkPasswordsMatch() {
        if (password && confirmPassword && password.value && confirmPassword.value) {
            if (password.value !== confirmPassword.value) {
                passwordError.textContent = 'Passwords do not match.';
                passwordError.style.display = 'block';
            } else {
                passwordError.style.display = 'none';
            }
        }
    }
    
    if (password && confirmPassword) {
        password.addEventListener('input', checkPasswordsMatch);
        confirmPassword.addEventListener('input', checkPasswordsMatch);
    }
});