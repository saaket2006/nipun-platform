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
    const section = document.getElementById('story');
    const storyElements = gsap.utils.toArray('.story-element');
    if (!section || storyElements.length === 0) return;
    if (storyElements[0].offsetWidth === 0 || storyElements[0].offsetParent === null) return;

    // Clean up any existing ScrollTriggers on this section
    ScrollTrigger.getAll().forEach(t => {
        if (t.trigger === section || storyElements.includes(t.trigger) || t.pin === section) {
            t.kill(true);
        }
    });

    // Accessibility: Reduced Motion
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        gsap.set(storyElements, { opacity: 1, filter: 'none', scale: 1, y: 0, clearProps: 'all' });
        return;
    }

    const isDesktop = window.innerWidth >= 768;
    const num0 = storyElements[0].querySelector('.num');

    // Initial state:
    // Line 0 is active (dark primary ink #1A1917, bold, scale 1.02)
    // Inner .num in Line 0 is active deep forest green #1E3A2F
    // Inactive lines (1, 2, 3) are visually subdued (muted ink #7A746B, regular 500, scale 0.98, WCAG AA 4.54:1 contrast)
    storyElements[0].classList.add('is-active');
    gsap.set(storyElements[0], {
        opacity: 1,
        color: '#1A1917',
        scale: 1.02,
        fontWeight: '700',
        y: 0,
        filter: 'none'
    });
    if (num0) {
        gsap.set(num0, {
            color: '#1E3A2F',
            fontWeight: '700'
        });
    }
    for (let i = 1; i < storyElements.length; i++) {
        storyElements[i].classList.remove('is-active');
        gsap.set(storyElements[i], {
            opacity: 1,
            color: '#7A746B',
            scale: 0.98,
            fontWeight: '500',
            y: 8,
            filter: 'none'
        });
    }

    // Fast, brisk scrub timeline: moves swiftly through the dilemmas
    const tl = gsap.timeline({
        scrollTrigger: {
            trigger: section,
            start: 'top top',
            end: isDesktop ? '+=80%' : '+=60%',
            pin: true,
            scrub: 0.35,
            anticipatePin: 1
        }
    });

    // Beat 1: Line 0 becomes subdued (including .num), Line 1 becomes dark & emphasized
    tl.to(storyElements[0], {
        color: '#7A746B',
        scale: 0.98,
        fontWeight: '500',
        duration: 0.6,
        ease: 'power1.inOut'
    }, 0.2);
    if (num0) {
        tl.to(num0, {
            color: '#7A746B',
            fontWeight: '500',
            duration: 0.6,
            ease: 'power1.inOut'
        }, 0.2);
    }
    tl.to(storyElements[1], {
        color: '#1A1917',
        scale: 1.02,
        fontWeight: '700',
        y: 0,
        duration: 0.6,
        ease: 'power2.out'
    }, 0.2);

    // Beat 2: Line 1 becomes subdued, Line 2 becomes dark & emphasized
    tl.to(storyElements[1], {
        color: '#7A746B',
        scale: 0.98,
        fontWeight: '500',
        duration: 0.6,
        ease: 'power1.inOut'
    }, 1.0);
    tl.to(storyElements[2], {
        color: '#1A1917',
        scale: 1.02,
        fontWeight: '700',
        y: 0,
        duration: 0.6,
        ease: 'power2.out'
    }, 1.0);

    // Beat 3: Line 2 becomes subdued, Line 3 becomes deep forest green & emphasized
    tl.to(storyElements[2], {
        color: '#7A746B',
        scale: 0.98,
        fontWeight: '500',
        duration: 0.6,
        ease: 'power1.inOut'
    }, 1.8);
    tl.to(storyElements[3], {
        color: '#1E3A2F',
        scale: 1.04,
        fontWeight: '700',
        y: 0,
        duration: 0.6,
        ease: 'power2.out'
    }, 1.8);

    // Short hold beat before swiftly releasing
    tl.to({}, { duration: 0.5 });
}

export function initFeatureStack() {
    const section = document.getElementById('features');
    const header = document.querySelector('.features-header');
    const container = document.querySelector('.features-container');
    const cards = gsap.utils.toArray('.feature-card-wrapper');

    if (!section || !header || cards.length === 0) return;
    if (cards[0].offsetWidth === 0 || cards[0].offsetParent === null) return;

    // Clean up any existing ScrollTriggers on this section
    ScrollTrigger.getAll().forEach(t => {
        if (cards.includes(t.trigger) || t.trigger === header || t.trigger === section || t.pin === header || cards.some(c => t.pin === c)) {
            t.kill(true);
        }
    });

    // Accessibility: Reduced Motion
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        gsap.set(header, { clearProps: 'all' });
        cards.forEach(card => {
            gsap.set(card, { clearProps: 'all' });
            card.style.position = 'relative';
            card.style.top = 'auto';
        });
        return;
    }

    const isDesktop = window.innerWidth >= 768;

    // Dynamic navbar height calculation
    const navbar = document.getElementById('navbar-landing');
    function getScrolledNavbarHeight() {
        if (!navbar) return 70;
        if (navbar.classList.contains('py-3')) return navbar.offsetHeight;
        return Math.min(navbar.offsetHeight, 77);
    }

    const getHeaderOffset = () => getScrolledNavbarHeight() + 10;
    const headerHeight = header.offsetHeight || 80;
    const getCardDockTop = () => isDesktop ? (getHeaderOffset() + headerHeight + 20) : 90;

    // Set CSS variable for card dock position
    document.documentElement.style.setProperty('--card-dock-top', `${getCardDockTop()}px`);

    // Ensure explicit z-index layering for stacking cards
    cards.forEach((card, index) => {
        card.style.position = 'relative';
        card.style.top = 'auto';
        card.style.zIndex = index + 1;
    });

    // Stage 2: Pin the Section Heading beneath fixed navbar on desktop
    if (isDesktop) {
        ScrollTrigger.create({
            trigger: header,
            start: () => `top ${getHeaderOffset()}px`,
            endTrigger: container,
            end: () => `bottom ${getCardDockTop() + 350}px`,
            pin: true,
            pinSpacing: false,
            anticipatePin: 1
        });
    }

    // Stage 3: Scroll-Driven Card Stacking with generous reading time and progressive blur
    cards.forEach((card, index) => {
        // Pin each card at the dock position until container ends
        ScrollTrigger.create({
            trigger: card,
            start: () => `top ${getCardDockTop()}px`,
            endTrigger: container,
            end: () => `bottom ${getCardDockTop() + 350}px`,
            pin: true,
            pinSpacing: false,
            anticipatePin: 1
        });

        // Depth transition: as next card approaches dock within final 160px, smoothly blur and recede the current card
        if (index < cards.length - 1) {
            const nextCard = cards[index + 1];
            gsap.fromTo(card,
                {
                    scale: 1,
                    opacity: 1,
                    filter: 'blur(0px)'
                },
                {
                    scrollTrigger: {
                        trigger: nextCard,
                        start: () => `top ${getCardDockTop() + 160}px`,
                        end: () => `top ${getCardDockTop()}px`,
                        scrub: true
                    },
                    scale: 0.92,
                    opacity: 0.15,
                    filter: 'blur(12px)',
                    ease: 'none'
                }
            );
        }

        // Deep recede transition: as future card (index + 2) approaches dock, fade out card completely
        if (index < cards.length - 2) {
            const futureCard = cards[index + 2];
            gsap.to(card, {
                scrollTrigger: {
                    trigger: futureCard,
                    start: () => `top ${getCardDockTop() + 160}px`,
                    end: () => `top ${getCardDockTop() + 40}px`,
                    scrub: true
                },
                scale: 0.88,
                opacity: 0,
                filter: 'blur(20px)',
                ease: 'none',
                immediateRender: false
            });
        }
    });
}

export function initWalkthrough() {
    const section = document.querySelector('#walkthrough');
    const blocks = document.querySelectorAll('.walkthrough-text-block');
    const panels = document.querySelectorAll('.walkthrough-visual-panel');
    if (!section || blocks.length === 0 || panels.length === 0) return;

    // Clean up any existing triggers on this section first
    ScrollTrigger.getAll().forEach(t => {
        if (t.trigger === section || t.pin === section || Array.from(blocks).includes(t.trigger)) {
            t.kill(true);
        }
    });

    let activeIndex = -1;

    function activateStepByIndex(index, force = false) {
        if ((!force && activeIndex === index) || index < 0 || index >= blocks.length) return;
        const prevIndex = activeIndex;
        activeIndex = index;

        const activeBlock = blocks[index];
        const targetId = activeBlock.getAttribute('data-visual-target');

        // 1. Highlight active text step block & distinguish inactive ones
        blocks.forEach((block, idx) => {
            if (idx === index) {
                block.classList.add('is-active');
            } else {
                block.classList.remove('is-active');
            }
        });

        // 2. Highlight corresponding workflow pipeline grid stage node
        const visualContainer = section.querySelector('.walkthrough-visual-container');
        if (visualContainer) {
            visualContainer.setAttribute('data-active-step', String(index));
        }
        const stageNodes = section.querySelectorAll('.workflow-grid-node');
        stageNodes.forEach((node, idx) => {
            if (idx === index) {
                node.classList.add('is-active');
            } else {
                node.classList.remove('is-active');
            }
        });

        // 3. Animate corresponding visual panel on right side with directional motion
        const isForward = prevIndex === -1 || index >= prevIndex;
        panels.forEach((panel) => {
            gsap.killTweensOf(panel);
            if (panel.id === targetId) {
                panel.style.display = 'block';
                panel.classList.remove('pointer-events-none');
                gsap.fromTo(panel,
                    {
                        opacity: 0,
                        scale: 0.96,
                        y: isForward ? 12 : -12
                    },
                    {
                        opacity: 1,
                        scale: 1,
                        y: 0,
                        duration: 0.35,
                        ease: 'power2.out'
                    }
                );
            } else {
                panel.classList.add('pointer-events-none');
                gsap.to(panel, {
                    opacity: 0,
                    scale: 0.96,
                    y: isForward ? -12 : 12,
                    duration: 0.2,
                    ease: 'power2.in',
                    onComplete: () => {
                        panel.style.display = 'none';
                    }
                });
            }
        });
    }

    function getActiveStepIndex() {
        const targetY = window.innerHeight * 0.48;
        const firstRect = blocks[0].getBoundingClientRect();
        if (firstRect.top > targetY) return 0;
        const lastRect = blocks[blocks.length - 1].getBoundingClientRect();
        if (lastRect.bottom < targetY) return blocks.length - 1;

        let closestIndex = 0;
        let minDistance = Infinity;
        blocks.forEach((block, idx) => {
            const rect = block.getBoundingClientRect();
            const blockCenter = rect.top + rect.height / 2;
            const distance = Math.abs(blockCenter - targetY);
            if (distance < minDistance) {
                minDistance = distance;
                closestIndex = idx;
            }
        });
        return closestIndex;
    }

    // Initialize step 0 (Document Ingestion)
    activateStepByIndex(0, true);

    // Coordinated GSAP ScrollTrigger across desktop, tablet, and mobile
    ScrollTrigger.create({
        trigger: section,
        start: 'top bottom',
        end: 'bottom top',
        onUpdate: () => {
            const nextIdx = getActiveStepIndex();
            activateStepByIndex(nextIdx);
        }
    });

    // Add click listeners for accessible navigation
    blocks.forEach((block, idx) => {
        block.addEventListener('click', () => {
            activateStepByIndex(idx);
            block.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
            navbar.classList.add('backdrop-blur-md', 'bg-dark/85', 'border-b', 'border-slate-800/80', 'py-3');
            navbar.classList.remove('py-5', 'bg-transparent', 'border-transparent');
        } else {
            navbar.classList.remove('backdrop-blur-md', 'bg-dark/85', 'border-slate-800/80', 'py-3');
            navbar.classList.add('py-5', 'bg-transparent', 'border-transparent');
        }
    });
}
