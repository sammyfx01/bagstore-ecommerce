document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('navToggle');
  const links = document.getElementById('navLinks');

  if (toggle && links) {
    toggle.addEventListener('click', function () {
      const isOpen = links.classList.toggle('nav-links-open');
      toggle.classList.toggle('nav-toggle-open');
      toggle.setAttribute('aria-expanded', isOpen);
    });

    links.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        links.classList.remove('nav-links-open');
        toggle.classList.remove('nav-toggle-open');
        toggle.setAttribute('aria-expanded', false);
      });
    });
  }

  document.querySelectorAll('[data-password-toggle]').forEach(function (button) {
    button.addEventListener('click', function () {
      const password = document.getElementById(button.dataset.passwordToggle);
      const isVisible = password.type === 'text';

      password.type = isVisible ? 'password' : 'text';
      button.classList.toggle('is-visible', !isVisible);
      button.setAttribute('aria-label', isVisible ? 'Show password' : 'Hide password');
      button.setAttribute('title', isVisible ? 'Show password' : 'Hide password');
    });
  });
});