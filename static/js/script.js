/**
 * TrustMark - Main JavaScript
 */

// Detect MetaMask
function detectMetaMask() {
    return window.ethereum && window.ethereum.isMetaMask;
}

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check for MetaMask
    if (window.location.pathname.includes('login') && detectMetaMask()) {
        // Add a "Connect with MetaMask" button if we detect MetaMask is installed
        const loginForm = document.querySelector('form');
        if (loginForm) {
            const metaMaskBtn = document.createElement('button');
            metaMaskBtn.type = 'button';
            metaMaskBtn.className = 'btn btn-warning w-100 mb-3';
            metaMaskBtn.innerHTML = '<i class="fa fa-external-link me-2"></i>Connect with MetaMask';
            
            metaMaskBtn.addEventListener('click', async function() {
                try {
                    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                    const account = accounts[0];
                    document.getElementById('wallet_address').value = account;
                    loginForm.submit();
                } catch (error) {
                    console.error(error);
                    alert('Failed to connect to MetaMask. Please try again or enter your address manually.');
                }
            });
            
            loginForm.insertBefore(metaMaskBtn, loginForm.firstChild);
        }
    }
    
    // Handle transaction hovering
    const txRows = document.querySelectorAll('tr[id^="tx-"]');
    txRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.classList.add('bg-dark-subtle');
        });
        
        row.addEventListener('mouseleave', function() {
            this.classList.remove('bg-dark-subtle');
        });
    });
});

// Helper function to truncate Ethereum addresses
function truncateAddress(address, prefixLength = 6, suffixLength = 4) {
    if (!address) return '';
    if (address.length <= prefixLength + suffixLength) return address;
    
    return `${address.slice(0, prefixLength)}...${address.slice(-suffixLength)}`;
}

// For copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(
        function() {
            // Success
            const tooltip = document.createElement('div');
            tooltip.className = 'position-fixed top-0 end-0 p-3';
            tooltip.style.zIndex = '1070';
            
            tooltip.innerHTML = `
                <div class="toast show" role="alert">
                    <div class="toast-header">
                        <strong class="me-auto">TrustMark</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        Copied to clipboard!
                    </div>
                </div>
            `;
            
            document.body.appendChild(tooltip);
            
            setTimeout(() => {
                tooltip.remove();
            }, 2000);
        },
        function() {
            // Error
            console.error('Failed to copy text');
        }
    );
}

/**
 * TrustMark - Modern JavaScript Enhancements
 */

// Modern page transition system
class PageTransitions {
    constructor() {
        this.init();
    }

    init() {
        // Add page transition class to body
        document.body.classList.add('page-transition');
        
        // Remove transition class after page loads
        window.addEventListener('load', () => {
            setTimeout(() => {
                document.body.classList.add('loaded');
            }, 100);
        });
    }
}

// Enhanced scroll animations
class ScrollAnimations {
    constructor() {
        this.init();
    }

    init() {
        // Smooth scroll for anchor links
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

        // Parallax effect for hero section
        this.initParallax();
        
        // Intersection Observer for scroll animations
        this.initIntersectionObserver();
    }

    initParallax() {
        const hero = document.querySelector('.hero-3d');
        if (hero) {
            window.addEventListener('scroll', () => {
                const scrolled = window.pageYOffset;
                const rate = scrolled * -0.5;
                hero.style.transform = `translateY(${rate}px)`;
            });
        }
    }

    initIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe all cards and sections
        document.querySelectorAll('.glass-card, .card, section').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            observer.observe(el);
        });
    }
}

// Modern form enhancements
class FormEnhancements {
    constructor() {
        this.init();
    }

    init() {
        // Add floating labels
        this.initFloatingLabels();
        
        // Add input animations
        this.initInputAnimations();
        
        // Add form validation feedback
        this.initFormValidation();
    }

    initFloatingLabels() {
        document.querySelectorAll('.form-control').forEach(input => {
            const label = input.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
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

    initInputAnimations() {
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                input.parentElement.classList.remove('focused');
            });
        });
    }

    initFormValidation() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const inputs = form.querySelectorAll('input[required]');
                let isValid = true;
                
                inputs.forEach(input => {
                    if (!input.value.trim()) {
                        isValid = false;
                        this.showError(input, 'This field is required');
                    } else {
                        this.removeError(input);
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                }
            });
        });
    }

    showError(input, message) {
        const errorDiv = input.parentElement.querySelector('.error-message') || 
                        document.createElement('div');
        errorDiv.className = 'error-message text-danger small mt-1';
        errorDiv.textContent = message;
        
        if (!input.parentElement.querySelector('.error-message')) {
            input.parentElement.appendChild(errorDiv);
        }
        
        input.classList.add('is-invalid');
    }

    removeError(input) {
        const errorDiv = input.parentElement.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.remove();
        }
        input.classList.remove('is-invalid');
    }
}

// Enhanced table interactions
class TableEnhancements {
    constructor() {
        this.init();
    }

    init() {
        // Add hover effects to table rows
        document.querySelectorAll('.table tbody tr').forEach(row => {
            row.addEventListener('mouseenter', () => {
                row.style.transform = 'scale(1.01)';
                row.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)';
            });
            
            row.addEventListener('mouseleave', () => {
                row.style.transform = 'scale(1)';
                row.style.boxShadow = 'none';
            });
        });

        // Add click effects to buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Create ripple effect
                const ripple = document.createElement('span');
                const rect = btn.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                btn.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }
}

// Modern loading states
class LoadingStates {
    constructor() {
        this.init();
    }

    init() {
        // Add loading states to forms
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', () => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
                    submitBtn.disabled = true;
                }
            });
        });

        // Add loading shimmer to cards
        this.addLoadingShimmer();
    }

    addLoadingShimmer() {
        const cards = document.querySelectorAll('.glass-card');
        cards.forEach(card => {
            if (!card.querySelector('.card-body')) {
                card.classList.add('loading-shimmer');
            }
        });
    }
}

// Enhanced MetaMask detection and integration
class MetaMaskIntegration {
    constructor() {
        this.init();
    }

    init() {
        if (window.location.pathname.includes('login') && this.detectMetaMask()) {
            this.addMetaMaskButton();
        }
    }

    detectMetaMask() {
        return window.ethereum && window.ethereum.isMetaMask;
    }

    addMetaMaskButton() {
        const loginForm = document.querySelector('form');
        if (loginForm) {
            const metaMaskBtn = document.createElement('button');
            metaMaskBtn.type = 'button';
            metaMaskBtn.className = 'btn btn-warning w-100 mb-3 btn-3d';
            metaMaskBtn.innerHTML = '<i class="fa fa-external-link me-2"></i>Connect with MetaMask';
            
            metaMaskBtn.addEventListener('click', async () => {
                try {
                    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                    const account = accounts[0];
                    document.getElementById('wallet_address').value = account;
                    loginForm.submit();
                } catch (error) {
                    console.error(error);
                    this.showNotification('Failed to connect to MetaMask. Please try again or enter your address manually.', 'error');
                }
            });
            
            loginForm.insertBefore(metaMaskBtn, loginForm.firstChild);
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Utility functions
class Utils {
    static truncateAddress(address, prefixLength = 6, suffixLength = 4) {
        if (!address) return '';
        if (address.length <= prefixLength + suffixLength) return address;
        return `${address.slice(0, prefixLength)}...${address.slice(-suffixLength)}`;
    }

    static copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(
            () => {
                this.showNotification('Copied to clipboard!', 'success');
            },
            () => {
                console.error('Failed to copy text');
            }
        );
    }

    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize all enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new PageTransitions();
    new ScrollAnimations();
    new FormEnhancements();
    new TableEnhancements();
    new LoadingStates();
    new MetaMaskIntegration();
    
    // Add ripple effect styles
    const style = document.createElement('style');
    style.textContent = `
        .btn {
            position: relative;
            overflow: hidden;
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .form-control:focus {
            transform: scale(1.02);
        }
        
        .focused .form-control {
            border-color: #5f72ff;
            box-shadow: 0 0 0 0.2rem rgba(95, 114, 255, 0.25);
        }
    `;
    document.head.appendChild(style);
});

// Make utility functions globally available
window.TrustMarkUtils = Utils;
