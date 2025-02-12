document.addEventListener('DOMContentLoaded', function() {
    // Handle booking form validation
    const bookingForm = document.querySelector('.booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            const dateField = document.querySelector('#id_booking_date');
            const timeField = document.querySelector('#id_booking_time');
            
            const selectedDate = new Date(dateField.value);
            const today = new Date();
            
            if (selectedDate < today) {
                e.preventDefault();
                alert('Please select a future date for booking.');
            }
        });
    }

    // Handle mobile menu toggle
    const menuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add animation to service cards
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.classList.add('animate-fade-in');
    });
});