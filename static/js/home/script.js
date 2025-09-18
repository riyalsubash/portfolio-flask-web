/*=============== LOADER ===============*/
        window.addEventListener('load', () => {
            const loader = document.getElementById('loader');
            setTimeout(() => {
                loader.classList.add('hide');
            }, 1000);
        });

        /*=============== SHOW/HIDE MOBILE MENU ===============*/
        const navMenu = document.getElementById('nav-menu'),
              navToggle = document.getElementById('nav-toggle'),
              navClose = document.getElementById('nav-close'),
              navLinks = document.querySelectorAll('.nav__link');

        // Show menu
        if (navToggle) {
            navToggle.addEventListener('click', (e) => {
                e.preventDefault();
                navMenu.classList.add('show-menu');
                document.body.style.overflow = 'hidden'; // Prevent scrolling
            });
        }

        // Hide menu
        if (navClose) {
            navClose.addEventListener('click', (e) => {
                e.preventDefault();
                navMenu.classList.remove('show-menu');
                document.body.style.overflow = 'auto'; // Restore scrolling
            });
        }

        // Close menu when clicking on overlay
        navMenu.addEventListener('click', (e) => {
            if (e.target === navMenu) {
                navMenu.classList.remove('show-menu');
                document.body.style.overflow = 'auto';
            }
        });

        /*=============== REMOVE MENU ON MOBILE LINK CLICK ===============*/
        function linkAction() {
            navMenu.classList.remove('show-menu');
            document.body.style.overflow = 'auto';
        }
        navLinks.forEach(n => n.addEventListener('click', linkAction));

        /*=============== CHANGE HEADER BACKGROUND ON SCROLL ===============*/
        function scrollHeader() {
            const header = document.getElementById('header');
            if (window.scrollY >= 100) {
                header.classList.add('scroll-header');
            } else {
                header.classList.remove('scroll-header');
            }
        }
        window.addEventListener('scroll', scrollHeader);

        /*=============== SCROLL SECTIONS ACTIVE LINK ===============*/
        const sections = document.querySelectorAll('section[id]');

        function scrollActive() {
            const scrollY = window.pageYOffset;

            sections.forEach(current => {
                const sectionHeight = current.offsetHeight,
                      sectionTop = current.offsetTop - 100,
                      sectionId = current.getAttribute('id');

                if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                    document.querySelector('.nav__menu a[href*=' + sectionId + ']').classList.add('active');
                } else {
                    document.querySelector('.nav__menu a[href*=' + sectionId + ']').classList.remove('active');
                }
            });
        }
        window.addEventListener('scroll', scrollActive);

    

        /*=============== SMOOTH SCROLLING ===============*/
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        /*=============== CONTACT FORM ===============*/
        const contactForm = document.getElementById('contact-form');
const contactButton = document.querySelector('.contact__button');
const buttonText = document.querySelector('.button-text');

if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();

        buttonText.textContent = 'Sending...';
        contactButton.disabled = true;

        const formData = new FormData(contactForm);

        fetch('/send_mail', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response not ok');
            }
            return response.text(); // or response.json() if you return JSON
        })
        .then(data => {
            showFlashMessage('Message saved successfully!', 'success');
            contactForm.reset();
        })
        .catch(error => {
            console.error('Error:', error);
            showFlashMessage('Failed to send message. Please try again.', 'danger');
        })
        .finally(() => {
            buttonText.textContent = 'Send Message';
            contactButton.disabled = false;
        });
    });
}


        /*=============== FLASH MESSAGES ===============*/
        function showFlashMessage(message, type) {
            const flashContainer = document.getElementById('flash-messages');
            const flashMessage = document.createElement('div');
            flashMessage.className = `flash-message flash-${type}`;
            flashMessage.textContent = message;
            
            flashContainer.appendChild(flashMessage);
            
            setTimeout(() => {
                flashMessage.remove();
            }, 5000);
        }

        /*=============== INTERSECTION OBSERVER FOR ANIMATIONS ===============*/
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.skills__card, .project__card, .about__stat').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });

        /*=============== TYPING ANIMATION ===============*/
        const typingElement = document.querySelector('.home__subtitle');
        const titles = ['ML Engineer', 'Full Stack Dev', 'IoT'];
        let titleIndex = 0;
        let charIndex = 0;
        let isDeleting = false;

        function typeWriter() {
            const currentTitle = titles[titleIndex];
            
            if (isDeleting) {
                typingElement.textContent = currentTitle.substring(0, charIndex - 1);
                charIndex--;
            } else {
                typingElement.textContent = currentTitle.substring(0, charIndex + 1);
                charIndex++;
            }

            let typeSpeed = 150;

            if (isDeleting) {
                typeSpeed /= 2;
            }

            if (!isDeleting && charIndex === currentTitle.length) {
                typeSpeed = 2000;
                isDeleting = true;
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                titleIndex = (titleIndex + 1) % titles.length;
                typeSpeed = 500;
            }

            setTimeout(typeWriter, typeSpeed);
        }

        // Start typing animation after page load
        setTimeout(typeWriter, 2000);

        /*=============== PARALLAX EFFECT ===============*/
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallaxElements = document.querySelectorAll('.home__img::before');
            
            parallaxElements.forEach(el => {
                const speed = 0.5;
                el.style.transform = `translateY(${scrolled * speed}px)`;
            });
        });

        /*=============== THEME PARTICLES EFFECT ===============*/
        function createParticle() {
            const particle = document.createElement('div');
            particle.style.position = 'fixed';
            particle.style.width = '4px';
            particle.style.height = '4px';
            particle.style.background = '#6366f1';
            particle.style.borderRadius = '50%';
            particle.style.pointerEvents = 'none';
            particle.style.opacity = '0.6';
            particle.style.zIndex = '1';
            particle.style.left = Math.random() * window.innerWidth + 'px';
            particle.style.top = '100vh';
            particle.style.animation = 'floatUp 6s linear forwards';
            
            document.body.appendChild(particle);
            
            setTimeout(() => {
                particle.remove();
            }, 6000);
        }

        // Add particle animation keyframes
        const style = document.createElement('style');
        style.textContent = `
            @keyframes floatUp {
                to {
                    transform: translateY(-100vh) rotate(360deg);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);

        // Create particles periodically
        setInterval(createParticle, 3000);