// GSAP Animations and Interactions
document.addEventListener('DOMContentLoaded', function() {
    // Register GSAP plugins
    gsap.registerPlugin(ScrollTrigger);
    
    // Navbar animation on scroll
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            gsap.to(navbar, { duration: 0.3, y: -100 });
        } else {
            // Scrolling up
            gsap.to(navbar, { duration: 0.3, y: 0 });
        }
        lastScrollTop = scrollTop;
    });
    
    // Hero section animations
    if (document.querySelector('.hero-section')) {
        gsap.timeline()
            .to('.hero-title', { duration: 1, opacity: 1, y: 0, ease: 'power3.out' })
            .to('.hero-subtitle', { duration: 1, opacity: 1, y: 0, ease: 'power3.out' }, '-=0.5')
            .to('.hero-buttons', { duration: 1, opacity: 1, y: 0, ease: 'power3.out' }, '-=0.5');
    }
    
    // Service cards animation
    gsap.utils.toArray('.service-card').forEach((card, index) => {
        gsap.fromTo(card, 
            { opacity: 0, y: 50 },
            {
                opacity: 1,
                y: 0,
                duration: 0.8,
                delay: index * 0.1,
                ease: 'power3.out',
                scrollTrigger: {
                    trigger: card,
                    start: 'top 80%',
                    toggleActions: 'play none none reverse'
                }
            }
        );
    });
    
    // Product cards hover effect
    gsap.utils.toArray('.product-card').forEach(card => {
        const image = card.querySelector('.product-image');
        const content = card.querySelector('.card-body');
        
        card.addEventListener('mouseenter', () => {
            gsap.to(card, { duration: 0.3, y: -10, boxShadow: '0 15px 30px rgba(0,0,0,0.2)' });
            gsap.to(image, { duration: 0.3, scale: 1.1 });
        });
        
        card.addEventListener('mouseleave', () => {
            gsap.to(card, { duration: 0.3, y: 0, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' });
            gsap.to(image, { duration: 0.3, scale: 1 });
        });
    });
    
    // Testimonials carousel animation
    if (document.querySelector('.testimonial-carousel')) {
        gsap.utils.toArray('.testimonial-card').forEach((card, index) => {
            gsap.fromTo(card,
                { opacity: 0, x: 100 },
                {
                    opacity: 1,
                    x: 0,
                    duration: 0.8,
                    delay: index * 0.2,
                    scrollTrigger: {
                        trigger: card,
                        start: 'top 80%',
                        toggleActions: 'play none none reverse'
                    }
                }
            );
        });
    }
    
    // Search autocomplete functionality
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length > 2) {
                searchTimeout = setTimeout(() => {
                    // Implement autocomplete functionality here
                    console.log('Searching for:', query);
                }, 300);
            }
        });
    }
    
    // Shopping cart updates
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const cartItemId = this.dataset.cartItemId;
            const quantity = this.value;
            
            // Update cart via AJAX
            fetch('/payments/update-cart/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    cart_item_id: cartItemId,
                    quantity: quantity
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update cart total
                    document.querySelector('.cart-total').textContent = data.cart_total;
                    // Update item total
                    const itemTotal = document.querySelector(`#item-total-${cartItemId}`);
                    if (itemTotal) {
                        itemTotal.textContent = data.item_total;
                    }
                }
            })
            .catch(error => {
                console.error('Error updating cart:', error);
            });
        });
    });
    
    // Add to cart animation
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productId = this.dataset.productId;
            const productCard = this.closest('.product-card');
            const cartIcon = document.querySelector('.navbar .fa-shopping-cart');
            
            // Animate button
            gsap.to(this, {
                scale: 0.95,
                duration: 0.1,
                yoyo: true,
                repeat: 1,
                ease: 'power2.inOut'
            });
            
            // Add to cart via AJAX
            fetch('/payments/add-to-cart/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: 1
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update cart count
                    const cartBadge = document.querySelector('.badge');
                    if (cartBadge) {
                        cartBadge.textContent = data.cart_count;
                    } else {
                        // Create badge if it doesn't exist
                        const badge = document.createElement('span');
                        badge.className = 'badge bg-danger';
                        badge.textContent = data.cart_count;
                        cartIcon.parentNode.appendChild(badge);
                    }
                    
                    // Success feedback
                    this.innerHTML = '<i class="fas fa-check"></i> Added!';
                    this.classList.add('btn-success');
                    this.classList.remove('btn-primary');
                    
                    setTimeout(() => {
                        this.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
                        this.classList.remove('btn-success');
                        this.classList.add('btn-primary');
                    }, 2000);
                } else {
                    // Error feedback
                    this.innerHTML = '<i class="fas fa-exclamation"></i> Error';
                    this.classList.add('btn-danger');
                    this.classList.remove('btn-primary');
                    
                    setTimeout(() => {
                        this.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
                        this.classList.remove('btn-danger');
                        this.classList.add('btn-primary');
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
            });
        });
    });
    
    // Wishlist functionality
    const wishlistButtons = document.querySelectorAll('.add-to-wishlist');
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productId = this.dataset.productId;
            const icon = this.querySelector('i');
            
            fetch('/products/toggle-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_id: productId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.added) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                        this.classList.add('text-danger');
                    } else {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                        this.classList.remove('text-danger');
                    }
                }
            })
            .catch(error => {
                console.error('Error toggling wishlist:', error);
            });
        });
    });
    
    // Product image gallery
    const productThumbnails = document.querySelectorAll('.product-thumbnail');
    productThumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            const mainImage = document.querySelector('.main-product-image');
            const newSrc = this.src;
            
            gsap.to(mainImage, {
                opacity: 0,
                duration: 0.2,
                onComplete: () => {
                    mainImage.src = newSrc;
                    gsap.to(mainImage, { opacity: 1, duration: 0.2 });
                }
            });
            
            // Update active thumbnail
            document.querySelectorAll('.product-thumbnail').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Price range slider
    const priceSliders = document.querySelectorAll('.price-range-slider');
    priceSliders.forEach(slider => {
        slider.addEventListener('input', function() {
            const display = document.querySelector(this.dataset.display);
            if (display) {
                display.textContent = `$${this.value}`;
            }
        });
    });
    
    // FAQ accordion with smooth animations
    const accordionButtons = document.querySelectorAll('.accordion-button');
    accordionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const content = this.nextElementSibling;
            
            if (this.classList.contains('collapsed')) {
                gsap.fromTo(content, 
                    { height: 0, opacity: 0 },
                    { height: 'auto', opacity: 1, duration: 0.3, ease: 'power2.out' }
                );
            }
        });
    });
    
    // Form validation enhancements
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Animate invalid fields
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    gsap.to(field, {
                        x: -10,
                        duration: 0.1,
                        yoyo: true,
                        repeat: 3,
                        ease: 'power2.inOut'
                    });
                });
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                gsap.to(window, {
                    duration: 1,
                    scrollTo: target,
                    ease: 'power2.inOut'
                });
            }
        });
    });
});

// Utility function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Loading state management
function showLoading(element) {
    element.classList.add('loading');
    element.style.pointerEvents = 'none';
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.style.pointerEvents = 'auto';
}

// Toast notification system
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 100px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
    
    // Animate in
    gsap.fromTo(toast, 
        { x: 100, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.3, ease: 'power2.out' }
    );
}