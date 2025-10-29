const navToggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('.primary-nav');

if (navToggle && nav) {
  navToggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', isOpen);
  });

  nav.addEventListener('click', (event) => {
    if (event.target.classList.contains('nav-link') && nav.classList.contains('open')) {
      nav.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    }
  });
}
