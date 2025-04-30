/**
 * Hotel Reservation System - Main JavaScript
 * 
 * Ce fichier contient les fonctions JavaScript principales 
 * utilisées dans l'application de réservation d'hôtel.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des éléments d'interface
    initializeTooltips();
    initializeDatePickers();
    setupFormValidation();
    setupScrollEffects();
    
    // Fonctions spécifiques de page
    if (document.querySelector('.hero-section')) {
        initializeHeroSlider();
    }
    
    if (document.querySelector('.room-detail-slider')) {
        initializeRoomSlider();
    }
    
    if (document.getElementById('reservationForm')) {
        setupReservationCalculator();
    }
});

/**
 * Initialise les tooltips Bootstrap
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialise les sélecteurs de date
 */
function initializeDatePickers() {
    // Configuration pour les champs de date
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Définir la date minimale (aujourd'hui)
        if (input.getAttribute('min') === null) {
            const today = new Date().toISOString().split('T')[0];
            input.setAttribute('min', today);
        }
        
        // Gérer le changement de dates d'arrivée/départ
        if (input.name === 'check_in_date') {
            input.addEventListener('change', function() {
                const checkOutInput = document.querySelector('input[name="check_out_date"]');
                if (checkOutInput) {
                    // La date de départ doit être après la date d'arrivée
                    const checkInDate = new Date(this.value);
                    const nextDay = new Date(checkInDate);
                    nextDay.setDate(nextDay.getDate() + 1);
                    
                    const minDateStr = nextDay.toISOString().split('T')[0];
                    checkOutInput.setAttribute('min', minDateStr);
                    
                    // Si la date actuelle de départ est avant la nouvelle date d'arrivée, la mettre à jour
                    if (new Date(checkOutInput.value) <= checkInDate) {
                        checkOutInput.value = minDateStr;
                    }
                }
            });
        }
    });
}

/**
 * Configuration de la validation des formulaires
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Effets de défilement et animations
 */
function setupScrollEffects() {
    // Animation des éléments au défilement
    const fadeElements = document.querySelectorAll('.fade-in');
    
    if (fadeElements.length > 0) {
        const fadeInObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    fadeInObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });
        
        fadeElements.forEach(element => {
            fadeInObserver.observe(element);
        });
    }
    
    // Navbar qui change au défilement
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
}

/**
 * Initialisation du slider de la page d'accueil
 */
function initializeHeroSlider() {
    // Cette fonction peut être utilisée si vous ajoutez un slider à la section héro
    // Par exemple avec un carousel Bootstrap
    const heroSection = document.querySelector('.hero-section');
    if (!heroSection) return;
    
    // Animation du texte hero
    const heroTitle = heroSection.querySelector('.hero-title');
    const heroSubtitle = heroSection.querySelector('.hero-subtitle');
    const heroButtons = heroSection.querySelector('.hero-buttons');
    
    if (heroTitle) heroTitle.classList.add('fade-in');
    if (heroSubtitle) {
        heroSubtitle.style.opacity = '0';
        setTimeout(() => {
            heroSubtitle.classList.add('fade-in');
            heroSubtitle.style.opacity = '1';
        }, 300);
    }
    if (heroButtons) {
        heroButtons.style.opacity = '0';
        setTimeout(() => {
            heroButtons.classList.add('fade-in');
            heroButtons.style.opacity = '1';
        }, 600);
    }
}

/**
 * Initialisation du slider de détail de chambre
 */
function initializeRoomSlider() {
    // Si vous utilisez un carousel Bootstrap
    const roomSlider = document.querySelector('#roomPhotosCarousel');
    if (roomSlider) {
        new bootstrap.Carousel(roomSlider, {
            interval: 5000,
            ride: 'carousel'
        });
    }
}

/**
 * Configuration du calculateur de prix pour la réservation
 */
function setupReservationCalculator() {
    const reservationForm = document.getElementById('reservationForm');
    if (!reservationForm) return;
    
    const checkInDate = document.querySelector('input[name="check_in_date"]');
    const checkOutDate = document.querySelector('input[name="check_out_date"]');
    const roomCheckboxes = document.querySelectorAll('input[name="rooms"]');
    const serviceCheckboxes = document.querySelectorAll('input[name="services"]');
    const totalPriceElement = document.getElementById('totalPrice');
    
    // Fonction pour calculer le prix total
    function calculateTotal() {
        // Calcul du nombre de nuits
        const startDate = new Date(checkInDate.value);
        const endDate = new Date(checkOutDate.value);
        const nights = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
        
        // Si les dates ne sont pas valides, sortir
        if (isNaN(nights) || nights <= 0) return;
        
        let totalPrice = 0;
        
        // Ajouter le prix des chambres
        roomCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const roomPrice = parseFloat(checkbox.dataset.price || 0);
                totalPrice += roomPrice * nights;
            }
        });
        
        // Ajouter le prix des services
        serviceCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const servicePrice = parseFloat(checkbox.dataset.price || 0);
                totalPrice += servicePrice;
            }
        });
        
        // Afficher le prix total
        if (totalPriceElement) {
            totalPriceElement.textContent = totalPrice.toFixed(2) + ' €';
        }
    }
    
    // Attacher les écouteurs d'événements
    if (checkInDate) checkInDate.addEventListener('change', calculateTotal);
    if (checkOutDate) checkOutDate.addEventListener('change', calculateTotal);
    
    roomCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', calculateTotal);
    });
    
    serviceCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', calculateTotal);
    });
    
    // Calculer le prix initial
    calculateTotal();
}

/**
 * Formatage des dates pour l'affichage
 * @param {Date} date - L'objet Date à formater
 * @returns {string} La date formatée
 */
function formatDate(date) {
    if (!(date instanceof Date)) return '';
    
    const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
    return date.toLocaleDateString('fr-FR', options);
}

/**
 * Fonction pour afficher une alerte personnalisée
 * @param {string} message - Le message à afficher
 * @param {string} type - Le type d'alerte (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-suppression après 5 secondes
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            alertContainer.removeChild(alert);
        }, 150);
    }, 5000);
}

/**
 * Fonction pour gérer les paiements (simulée)
 * @param {number} amount - Le montant à payer
 * @param {string} method - La méthode de paiement
 * @returns {Promise} Une promesse qui résout avec un résultat de paiement
 */
function processPayment(amount, method) {
    return new Promise((resolve, reject) => {
        // Simuler un délai de traitement
        setTimeout(() => {
            // Simuler une réussite 90% du temps
            if (Math.random() > 0.1) {
                resolve({
                    success: true,
                    reference: 'PAY-' + Math.random().toString(36).substring(2, 10).toUpperCase(),
                    message: 'Paiement traité avec succès'
                });
            } else {
                reject({
                    success: false,
                    message: 'Erreur lors du traitement du paiement. Veuillez réessayer.'
                });
            }
        }, 1500);
    });
}