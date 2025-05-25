// static/js/modern-main.js

// =========== THEME MANAGEMENT ===========
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        // Apply saved theme
        document.documentElement.setAttribute('data-theme', this.theme);
        
        // Create theme toggle button
        this.createThemeToggle();
        
        // Listen for system theme changes
        this.watchSystemTheme();
    }

    createThemeToggle() {
        const toggleButton = document.createElement('div');
        toggleButton.className = 'theme-toggle';
        toggleButton.innerHTML = this.theme === 'dark' ? 
            '<i class="fas fa-sun"></i>' : 
            '<i class="fas fa-moon"></i>';
        
        document.body.appendChild(toggleButton);
        
        toggleButton.addEventListener('click', () => this.toggleTheme());
    }

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        
        // Update toggle icon with animation
        const toggle = document.querySelector('.theme-toggle');
        toggle.innerHTML = this.theme === 'dark' ? 
            '<i class="fas fa-sun"></i>' : 
            '<i class="fas fa-moon"></i>';
        
        // Add rotation animation
        toggle.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            toggle.style.transform = 'rotate(0deg)';
        }, 300);
    }

    watchSystemTheme() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.theme = e.matches ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', this.theme);
            }
        });
    }
}

// =========== SMOOTH SCROLL ===========
class SmoothScroll {
    constructor() {
        this.init();
    }

    init() {
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Parallax scrolling effect
        window.addEventListener('scroll', () => this.handleParallax());
    }

    handleParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    }
}

// =========== ANIMATIONS ON SCROLL ===========
class ScrollAnimations {
    constructor() {
        this.init();
    }

    init() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe all elements with animation classes
        const animatedElements = document.querySelectorAll('.fade-in, .slide-in, .scale-in');
        animatedElements.forEach(element => observer.observe(element));
    }
}

// =========== MICRO-INTERACTIONS ===========
class MicroInteractions {
    constructor() {
        this.init();
    }

    init() {
        this.initRippleEffect();
        this.initMagneticButtons();
        this.initTiltEffect();
        this.initHoverEffects();
    }

    initRippleEffect() {
        document.querySelectorAll('.ripple').forEach(element => {
            element.addEventListener('click', (e) => {
                const ripple = document.createElement('span');
                const rect = element.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;

                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple-effect');

                element.appendChild(ripple);

                setTimeout(() => ripple.remove(), 600);
            });
        });
    }

    initMagneticButtons() {
        document.querySelectorAll('.btn-modern, .neu-button').forEach(button => {
            button.addEventListener('mousemove', (e) => {
                const rect = button.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                
                button.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
            });

            button.addEventListener('mouseleave', () => {
                button.style.transform = 'translate(0, 0)';
            });
        });
    }

    initTiltEffect() {
        document.querySelectorAll('.card-modern, .room-card-modern').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width;
                const y = (e.clientY - rect.top) / rect.height;
                
                const tiltX = (y - 0.5) * 10;
                const tiltY = (x - 0.5) * -10;
                
                card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale(1.02)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
            });
        });
    }

    initHoverEffects() {
        // Add stagger animation to lists
        document.querySelectorAll('.stagger-list').forEach(list => {
            const items = list.querySelectorAll('li, .item');
            items.forEach((item, index) => {
                item.style.animationDelay = `${index * 0.1}s`;
            });
        });

        // Hover sound effects (optional)
        document.querySelectorAll('.hover-sound').forEach(element => {
            element.addEventListener('mouseenter', () => {
                // You can add sound effects here
                this.playHoverSound();
            });
        });
    }

    playHoverSound() {
        // Placeholder for hover sound
        // const audio = new Audio('/static/sounds/hover.mp3');
        // audio.volume = 0.1;
        // audio.play();
    }
}

// =========== FORM ANIMATIONS ===========
class FormAnimations {
    constructor() {
        this.init();
    }

    init() {
        this.initFloatingLabels();
        this.initFormValidation();
        this.initPasswordStrength();
    }

    initFloatingLabels() {
        document.querySelectorAll('.form-group-modern').forEach(group => {
            const input = group.querySelector('.form-input-modern');
            const label = group.querySelector('.form-label-modern');

            if (input && label) {
                // Check if input has value on load
                if (input.value) {
                    label.classList.add('active');
                }

                input.addEventListener('focus', () => {
                    label.classList.add('active');
                });

                input.addEventListener('blur', () => {
                    if (!input.value) {
                        label.classList.remove('active');
                    }
                });
            }
        });
    }

    initFormValidation() {
        document.querySelectorAll('.form-modern').forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                
                // Add loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner"></span> Traitement...';
                submitBtn.disabled = true;

                // Simulate form submission
                setTimeout(() => {
                    submitBtn.innerHTML = '<i class="fas fa-check"></i> Succès!';
                    submitBtn.classList.add('success');
                    
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                        submitBtn.classList.remove('success');
                    }, 2000);
                }, 1500);
            });
        });
    }

    initPasswordStrength() {
        document.querySelectorAll('input[type="password"]').forEach(input => {
            const strengthIndicator = document.createElement('div');
            strengthIndicator.className = 'password-strength';
            input.parentElement.appendChild(strengthIndicator);

            input.addEventListener('input', () => {
                const strength = this.calculatePasswordStrength(input.value);
                strengthIndicator.className = `password-strength ${strength}`;
                strengthIndicator.textContent = strength.charAt(0).toUpperCase() + strength.slice(1);
            });
        });
    }

    calculatePasswordStrength(password) {
        if (password.length < 6) return 'weak';
        if (password.length < 10) return 'medium';
        if (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/.test(password)) {
            return 'strong';
        }
        return 'medium';
    }
}

// =========== LOADING STATES ===========
class LoadingStates {
    constructor() {
        this.init();
    }

    init() {
        // Add skeleton loading to dynamic content
        this.initSkeletonLoading();
        
        // Page transition effects
        this.initPageTransitions();
    }

    initSkeletonLoading() {
        // Replace content with skeleton while loading
        document.querySelectorAll('[data-skeleton]').forEach(element => {
            const skeleton = this.createSkeleton(element.dataset.skeleton);
            element.appendChild(skeleton);
        });
    }

    createSkeleton(type) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-wrapper';

        switch(type) {
            case 'card':
                skeleton.innerHTML = `
                    <div class="skeleton skeleton-image"></div>
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text" style="width: 80%"></div>
                `;
                break;
            case 'list':
                skeleton.innerHTML = `
                    <div class="skeleton skeleton-list-item"></div>
                    <div class="skeleton skeleton-list-item"></div>
                    <div class="skeleton skeleton-list-item"></div>
                `;
                break;
            default:
                skeleton.innerHTML = '<div class="skeleton"></div>';
        }

        return skeleton;
    }

    initPageTransitions() {
        // Add fade effect when navigating
        document.querySelectorAll('a:not([href^="#"])').forEach(link => {
            link.addEventListener('click', (e) => {
                if (link.hostname === window.location.hostname && !link.target) {
                    e.preventDefault();
                    const href = link.href;
                    
                    document.body.classList.add('fade-out');
                    
                    setTimeout(() => {
                        window.location.href = href;
                    }, 300);
                }
            });
        });
    }
}

// =========== NAVBAR EFFECTS ===========
class NavbarEffects {
    constructor() {
        this.init();
    }

    init() {
        const navbar = document.querySelector('.navbar-modern');
        if (!navbar) return;

        let lastScroll = 0;

        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;

            // Add/remove scrolled class
            if (currentScroll > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }

            // Hide/show navbar on scroll
            if (currentScroll > lastScroll && currentScroll > 300) {
                navbar.style.transform = 'translateY(-100%)';
            } else {
                navbar.style.transform = 'translateY(0)';
            }

            lastScroll = currentScroll;
        });
    }
}

// =========== ROOM GALLERY ===========
class RoomGallery {
    constructor() {
        this.init();
    }

    init() {
        document.querySelectorAll('.room-gallery').forEach(gallery => {
            const images = gallery.querySelectorAll('img');
            const indicators = this.createIndicators(images.length);
            gallery.appendChild(indicators);

            let currentIndex = 0;

            setInterval(() => {
                images[currentIndex].classList.remove('active');
                indicators.children[currentIndex].classList.remove('active');
                
                currentIndex = (currentIndex + 1) % images.length;
                
                images[currentIndex].classList.add('active');
                indicators.children[currentIndex].classList.add('active');
            }, 3000);
        });
    }

    createIndicators(count) {
        const indicators = document.createElement('div');
        indicators.className = 'gallery-indicators';

        for (let i = 0; i < count; i++) {
            const dot = document.createElement('span');
            dot.className = 'indicator-dot';
            if (i === 0) dot.classList.add('active');
            indicators.appendChild(dot);
        }

        return indicators;
    }
}

// =========== ANIMATED COUNTERS ===========
class AnimatedCounters {
    constructor() {
        this.init();
    }

    init() {
        const counters = document.querySelectorAll('.counter');
        const speed = 200;

        const animateCounter = (counter) => {
            const target = +counter.getAttribute('data-target');
            const count = +counter.innerText;
            const increment = target / speed;

            if (count < target) {
                counter.innerText = Math.ceil(count + increment);
                setTimeout(() => animateCounter(counter), 1);
            } else {
                counter.innerText = target;
            }
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });

        counters.forEach(counter => observer.observe(counter));
    }
}

// =========== NOTIFICATION SYSTEM ===========
class NotificationSystem {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        const container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
        return container;
    }

    show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} glass`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        this.container.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('show'), 10);

        // Close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.hide(notification);
        });

        // Auto hide
        setTimeout(() => this.hide(notification), duration);
    }

    hide(notification) {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }

    getIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// =========== INITIALIZE ALL ===========
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all modules
    const themeManager = new ThemeManager();
    const smoothScroll = new SmoothScroll();
    const scrollAnimations = new ScrollAnimations();
    const microInteractions = new MicroInteractions();
    const formAnimations = new FormAnimations();
    const loadingStates = new LoadingStates();
    const navbarEffects = new NavbarEffects();
    const roomGallery = new RoomGallery();
    const animatedCounters = new AnimatedCounters();
    const notificationSystem = new NotificationSystem();

    // Make notification system globally available
    window.notify = notificationSystem;

    // Add page load animation
    document.body.classList.add('loaded');

    // Example notification
    setTimeout(() => {
        window.notify.show('Bienvenue sur Hôtel Deluxe! ✨', 'success');
    }, 1000);
});