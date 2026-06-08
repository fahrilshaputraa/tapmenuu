function togglePassword() {
            const passwordInput = document.getElementById('password');
            const passwordIcon = document.getElementById('password-icon');
            const isHidden = passwordInput.type === 'password';

            passwordInput.type = isHidden ? 'text' : 'password';
            passwordIcon.className = isHidden ? 'fa-regular fa-eye-slash' : 'fa-regular fa-eye';
        }
