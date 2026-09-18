import {
    initHeroAnimation,
    initStoryAnimation,
    initFeatureStack,
    initWalkthrough,
    initCounters,
    initNavbarEffects
} from './animations.js?v=7';

// Prevent browser scroll restoration from skewing initial ScrollTrigger layout calculations
if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
}

export function initAllLandingAnimations() {
    const landingContainer = document.getElementById('landing-container');
    if (!landingContainer || landingContainer.classList.contains('hidden') || landingContainer.offsetWidth === 0) {
        return;
    }

    initHeroAnimation();
    initStoryAnimation();
    initFeatureStack();
    initWalkthrough();
    initCounters();
    initNavbarEffects();

    if (window.ScrollTrigger) {
        ScrollTrigger.refresh();
    }
}
window.initAllLandingAnimations = initAllLandingAnimations;

document.addEventListener('DOMContentLoaded', () => {
    const pathname = window.location.pathname;
    if (pathname.endsWith('index.html') || pathname === '/') {
        window.scrollTo(0, 0);

        // Ensure landing container is rendered and unhidden
        const landingContainer = document.getElementById('landing-container');
        if (landingContainer) {
            landingContainer.classList.remove('hidden');

            // Initialize animations on next animation frame after browser layout calculation
            requestAnimationFrame(() => {
                initAllLandingAnimations();
            });

            // React whenever landing container visibility or layout changes
            const observer = new MutationObserver(() => {
                if (!landingContainer.classList.contains('hidden') && landingContainer.offsetWidth > 0) {
                    requestAnimationFrame(() => {
                        initAllLandingAnimations();
                    });
                }
            });
            observer.observe(landingContainer, { attributes: true, attributeFilter: ['class', 'style'] });
        }

        // Refresh ScrollTrigger when webfonts and external assets finish loading
        window.addEventListener('load', () => {
            if (window.ScrollTrigger) {
                ScrollTrigger.refresh();
            }
        });

        // 2. Simple Scroll Fade-In Observer for Sections
        const fadeObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    fadeObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        const fadeElements = document.querySelectorAll('.fade-in-section');
        fadeElements.forEach(el => fadeObserver.observe(el));

        // 3. Interactive Walkthrough/Mockup logic
        const analyzeBtn = document.getElementById('mock-analyze-btn');
        const progressBar = document.getElementById('mock-progress');
        const badgeScore = document.getElementById('mock-badge-score');
        const analysisGrid = document.querySelector('.analysis-grid');

        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => {
                analyzeBtn.textContent = 'Analyzing...';
                progressBar.style.width = '0%';

                // Simulate progressive loading
                let progress = 0;
                const interval = setInterval(() => {
                    progress += 10;
                    progressBar.style.width = `${progress}%`;
                    if (progress >= 100) {
                        clearInterval(interval);
                        analyzeBtn.textContent = 'Analysis Complete';
                        analyzeBtn.classList.add('opacity-50');
                        analyzeBtn.disabled = true;

                        // Show mock analysis grid
                        if (analysisGrid) {
                            analysisGrid.classList.remove('hidden');
                        }

                        // Animate score increment
                        let score = 0;
                        const scoreInterval = setInterval(() => {
                            score += 1;
                            badgeScore.textContent = `${score}%`;
                            if (score >= 94) {
                                clearInterval(scoreInterval);
                            }
                        }, 20);
                    }
                }, 150);
            });
        }

        // 4. Hero Card Mouse Move Tilt Effect
        const heroCard = document.querySelector('.hero-mockup');
        if (heroCard) {
            document.addEventListener('mousemove', (e) => {
                // Check if device supports hover (not a touch screen)
                if (window.matchMedia("(hover: none)").matches) return;

                const xAxis = (window.innerWidth / 2 - e.pageX) / 50;
                const yAxis = (window.innerHeight / 2 - e.pageY) / 50;
                heroCard.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
            });

            // Reset position on mouse leave body
            document.addEventListener('mouseleave', () => {
                heroCard.style.transform = `rotateY(0deg) rotateX(0deg)`;
            });
        }

        // 5. FAQ Accordion Logic
        const faqCards = document.querySelectorAll('.faq-card');
        faqCards.forEach(card => {
            const header = card.querySelector('.faq-header');
            const content = card.querySelector('.faq-content');
            const icon = card.querySelector('.faq-icon');

            if (header && content && icon) {
                // Ensure smooth transition style is present on icon
                icon.style.transition = 'transform 0.2s ease';

                header.addEventListener('click', () => {
                    const isOpen = !content.classList.contains('hidden');

                    // Close all FAQs
                    faqCards.forEach(otherCard => {
                        const otherContent = otherCard.querySelector('.faq-content');
                        const otherIcon = otherCard.querySelector('.faq-icon');
                        if (otherContent) otherContent.classList.add('hidden');
                        if (otherIcon) otherIcon.style.transform = 'rotate(0deg)';
                    });

                    // Open this one if it was closed
                    if (!isOpen) {
                        content.classList.remove('hidden');
                        icon.style.transform = 'rotate(180deg)';
                    }
                });
            }
        });
    }
});
