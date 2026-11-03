import './style.css'

// Main JS interactions

document.addEventListener('DOMContentLoaded', () => {
    // Smooth scroll for anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Staggered Animation Logic
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
            }
        });
    }, { threshold: 0.1 });

    // Select elements to animate
    const sections = document.querySelectorAll('section');
    const cards = document.querySelectorAll('.card');
    const techItems = document.querySelectorAll('.tech-item');
    const teamMembers = document.querySelectorAll('.team-member');

    // Add initial hidden states
    sections.forEach(el => el.classList.add('hidden-up'));

    // Stagger interactions inside sections
    cards.forEach((el, index) => {
        el.classList.add('hidden-left');
        el.style.transitionDelay = `${index * 100}ms`; // Stagger delay
        observer.observe(el);
    });

    techItems.forEach((el, index) => {
        el.classList.add('hidden-right');
        el.style.transitionDelay = `${index * 150}ms`;
        observer.observe(el);
    });

    teamMembers.forEach((el, index) => {
        el.classList.add('hidden-up');
        el.style.transitionDelay = `${index * 100}ms`;
        observer.observe(el);
    });

    // Observe main sections too
    sections.forEach(section => observer.observe(section));
});
