/**
 * Initializes generic modals like Contact modal.
 */
export function initModals() {
    const contactModal = document.getElementById('contact-modal');
    const contactTriggerBtn = document.getElementById('contact-trigger-btn');
    const closeContactBtn = document.getElementById('close-contact-btn');

    // Show/Hide Contact Modal
    if (contactTriggerBtn && contactModal && closeContactBtn) {
        contactTriggerBtn.addEventListener('click', () => {
            contactModal.classList.remove('hidden');
        });

        closeContactBtn.addEventListener('click', () => {
            contactModal.classList.add('hidden');
        });

        contactModal.addEventListener('click', (e) => {
            if (e.target === contactModal) {
                contactModal.classList.add('hidden');
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !contactModal.classList.contains('hidden')) {
                contactModal.classList.add('hidden');
            }
        });
    }

    // Hide Name modal / Change name elements as custom name editing is replaced in Phase 1
    const changeNameBtn = document.getElementById('change-name-btn');
    if (changeNameBtn) {
        changeNameBtn.style.display = "none";
    }

    // Close Auth Modal
    const authModal = document.getElementById('auth-modal');
    const authCloseBtn = document.getElementById('auth-close-btn');
    if (authModal) {
        if (authCloseBtn) {
            authCloseBtn.addEventListener('click', () => {
                authModal.classList.add('hidden');
                window.location.hash = '';
            });
        }

        // Close on clicking the backdrop outside of the auth card
        authModal.addEventListener('click', (e) => {
            if (e.target === authModal) {
                authModal.classList.add('hidden');
                window.location.hash = '';
            }
        });

        // Close on Escape keypress
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !authModal.classList.contains('hidden')) {
                authModal.classList.add('hidden');
                window.location.hash = '';
            }
        });
    }
}
