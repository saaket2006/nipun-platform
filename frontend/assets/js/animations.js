/* GSAP Scroll Animations & Timelines Module */

export function initHeroAnimation() {
    // 1. Title fade, blur, and slide up (smooth container animation - avoids DOM text splitting layout shifts)
    const headline = document.querySelector('.hero-headline');
    if (headline) {
        gsap.fromTo(headline,
            { opacity: 0, y: 30, filter: 'blur(10px)' },
            { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.8, ease: 'power3.out' }
        );
    }

    // 2. Terminal typewriter
    const terminalText = document.querySelector('.terminal-typewriter');
    if (terminalText) {
        const text = terminalText.textContent;
        terminalText.textContent = '';
        let i = 0;
        function type() {
            if (i < text.length) {
                terminalText.textContent += text.charAt(i);
                i++;
                setTimeout(type, 45);
            }
        }
        type();
    }

    // 3. Parallax mouse move for hero mockup
    const heroMockup = document.querySelector('.hero-mockup-wrapper');
    if (heroMockup) {
        document.addEventListener('mousemove', (e) => {
            const xAxis = (window.innerWidth / 2 - e.pageX) / 45;
            const yAxis = (window.innerHeight / 2 - e.pageY) / 45;
            gsap.to(heroMockup, {
                rotationY: xAxis,
                rotationX: -yAxis,
                ease: 'power2.out',
                duration: 0.5
            });
        });
        
        document.addEventListener('mouseleave', () => {
            gsap.to(heroMockup, {
                rotationY: 0,
                rotationX: 0,
                ease: 'power2.out',
                duration: 0.8
            });
        });
    }

    // 4. Floating badges animation
    gsap.to('.floating-badge-1', { y: -12, duration: 2.2, repeat: -1, yoyo: true, ease: 'sine.inOut' });
    gsap.to('.floating-badge-2', { y: 12, duration: 2.6, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: 0.3 });
    gsap.to('.floating-badge-3', { y: -8, duration: 2.0, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: 0.6 });
}

export function initStoryAnimation() {
    const storyElements = gsap.utils.toArray('.story-element');
    if (storyElements.length === 0) return;
    if (storyElements[0].offsetWidth === 0 || storyElements[0].offsetParent === null) return;

    ScrollTrigger.getAll().forEach(t => {
        if (storyElements.includes(t.trigger)) t.kill();
    });

    storyElements.forEach((el) => {
        gsap.fromTo(el, 
            { opacity: 0.1, y: 30, scale: 0.95 },
            { 
                opacity: 1, 
                y: 0, 
                scale: 1,
                scrollTrigger: {
                    trigger: el,
                    start: 'top 80%',
                    end: 'top 50%',
                    scrub: true,
                    toggleActions: 'play reverse play reverse'
                }
            }
        );
    });
}

export function initFeatureStack() {
    const cards = gsap.utils.toArray('.feature-card-wrapper');
    if (cards.length === 0) return;
    if (cards[0].offsetWidth === 0 || cards[0].offsetParent === null) return;

    ScrollTrigger.getAll().forEach(t => {
        if (cards.includes(t.trigger)) t.kill();
    });

    cards.forEach((card, index) => {
        if (index === cards.length - 1) return;

        gsap.to(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 120px',
                end: 'bottom 100px',
                scrub: true,
                pin: false
            },
            scale: 0.92,
            opacity: 0.6,
            filter: 'blur(3px)',
            ease: 'none'
        });
    });
}

export function initWalkthrough() {
    const section = document.querySelector('#walkthrough');
    const blocks = document.querySelectorAll('.walkthrough-text-block');
    const panels = document.querySelectorAll('.walkthrough-visual-panel');
    if (!section || blocks.length === 0 || panels.length === 0) return;

    // Safety check: Never pin or calculate triggers if section is hidden or unrendered
    if (section.offsetWidth === 0 || section.offsetHeight === 0 || section.offsetParent === null) {
        return;
    }

    let activeIndex = -1;

    function activateStepByIndex(index) {
        if (activeIndex === index || index < 0 || index >= blocks.length) return;
        activeIndex = index;

        const activeBlock = blocks[index];
        const targetId = activeBlock.getAttribute('data-visual-target');

        // 1. Highlight active text step block & dim inactive ones
        blocks.forEach((block, idx) => {
            if (idx === index) {
                block.classList.remove('border-slate-800', 'opacity-50');
                block.classList.add('border-emerald-500', 'opacity-100');
            } else {
                block.classList.remove('border-emerald-500', 'opacity-100');
                block.classList.add('border-slate-800', 'opacity-50');
            }
        });

        // 2. Animate corresponding visual panel on right side
        panels.forEach((panel) => {
            if (panel.id === targetId) {
                panel.style.display = 'block';
                gsap.fromTo(panel,
                    { opacity: 0, scale: 0.9, y: 15 },
                    {
                        opacity: 1,
                        scale: 1,
                        y: 0,
                        duration: 0.4,
                        ease: 'power2.out',
                        onStart: () => panel.classList.remove('pointer-events-none')
                    }
                );
            } else {
                gsap.to(panel, {
                    opacity: 0,
                    scale: 0.9,
                    y: -15,
                    duration: 0.25,
                    ease: 'power2.in',
                    onComplete: () => {
                        panel.style.display = 'none';
                        panel.classList.add('pointer-events-none');
                    }
                });
            }
        });
    }

    // Set initial step 1 active
    activateStepByIndex(0);

    // Clean up any existing trigger on this section first
    ScrollTrigger.getAll().forEach(t => {
        if (t.trigger === section) t.kill(true);
    });

    // Create GSAP ScrollTrigger Pinned Timeline for "#walkthrough" on desktop screens
    // On screens >= 1024px, the 2-column layout fits comfortably in the viewport
    let st = null;
    if (window.innerWidth >= 1024) {
        st = ScrollTrigger.create({
            trigger: section,
            start: 'top top+=80px',
            end: '+=180%',
            pin: true,
            pinSpacing: true,
            onUpdate: (self) => {
                const progress = self.progress;
                if (progress < 0.33) {
                    activateStepByIndex(0);
                } else if (progress < 0.66) {
                    activateStepByIndex(1);
                } else {
                    activateStepByIndex(2);
                }
            }
        });
    }

    // Add click listeners for step blocks
    blocks.forEach((block, idx) => {
        block.addEventListener('click', () => {
            activateStepByIndex(idx);
            if (st) {
                const targetProgress = idx === 0 ? 0.05 : (idx === 1 ? 0.45 : 0.85);
                const scrollPos = st.start + targetProgress * (st.end - st.start);
                window.scrollTo({ top: scrollPos, behavior: 'smooth' });
            }
        });
    });
}

export function initCounters() {
    const counters = document.querySelectorAll('.stat-counter');
    if (counters.length === 0) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const value = parseInt(target.getAttribute('data-value'));
                const duration = 2000;
                let start = 0;
                const timer = setInterval(() => {
                    start += Math.ceil(value / 40);
                    if (start >= value) {
                        target.textContent = value.toLocaleString();
                        clearInterval(timer);
                    } else {
                        target.textContent = start.toLocaleString();
                    }
                }, 30);
                observer.unobserve(target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(c => observer.observe(c));
}

export function initNavbarEffects() {
    const navbar = document.getElementById('navbar-landing');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('backdrop-blur-md', 'bg-[#070a13]/85', 'border-b', 'border-slate-800/80', 'py-3');
            navbar.classList.remove('py-5', 'bg-transparent', 'border-transparent');
        } else {
            navbar.classList.remove('backdrop-blur-md', 'bg-[#070a13]/85', 'border-slate-800/80', 'py-3');
            navbar.classList.add('py-5', 'bg-transparent', 'border-transparent');
        }
    });
}
