document.addEventListener('DOMContentLoaded', function () {

    /* ── Toggle affichage mot de passe ── */
    const toggleIcons = document.querySelectorAll('.toggle-icon');

    toggleIcons.forEach(function (icon) {
        icon.addEventListener('click', function () {
            const input = this.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                this.classList.remove('fa-eye');
                this.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                this.classList.remove('fa-eye-slash');
                this.classList.add('fa-eye');
            }
        });
    });

    /* ── Switch vers le formulaire inscription ── */
    const toSignup = document.getElementById('switch-to-signup');
    if (toSignup) {
        toSignup.addEventListener('click', function () {
            document.getElementById('auth-container').classList.add('signup-active');
        });
    }

    /* ── Switch vers le formulaire connexion ── */
    const toLogin = document.getElementById('switch-to-login');
    if (toLogin) {
        toLogin.addEventListener('click', function () {
            document.getElementById('auth-container').classList.remove('signup-active');
        });
    }

});
