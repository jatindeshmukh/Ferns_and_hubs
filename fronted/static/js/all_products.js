// fronted/static/js/all_products.js
document.addEventListener('DOMContentLoaded', function() {
    const sortSelect = document.getElementById('sortSelect');
    const productsGrid = document.getElementById('productsGrid');
    const productCards = document.querySelectorAll('.product-card');
    const applyFiltersBtn = document.getElementById('applyFilters');
    const productCount = document.getElementById('productCount');
    
    // Sort functionality
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const sortValue = this.value;
            const productsArray = Array.from(productCards);
            
            productsArray.sort((a, b) => {
                switch(sortValue) {
                    case 'price_low':
                        return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
                    case 'price_high':
                        return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
                    case 'name_asc':
                        return a.dataset.name.localeCompare(b.dataset.name);
                    case 'name_desc':
                        return b.dataset.name.localeCompare(a.dataset.name);
                    default:
                        return 0; // Keep original order for "featured"
                }
            });
            
            // Clear the grid and re-append sorted products
            productsGrid.innerHTML = '';
            productsArray.forEach(card => {
                productsGrid.appendChild(card);
            });
            
            // Update product count display
            updateProductCount();
        });
    }
    
    // Filter functionality
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            const categoryFilter = document.getElementById('categoryFilter').value;
            const minPrice = parseFloat(document.getElementById('minPrice').value) || 0;
            const maxPrice = parseFloat(document.getElementById('maxPrice').value) || Infinity;
            const inStockOnly = document.getElementById('inStockOnly').checked;
            
            let visibleCount = 0;
            
            productCards.forEach(card => {
                let show = true;
                const price = parseFloat(card.dataset.price);
                const category = card.dataset.category;
                const inStock = card.querySelector('.badge.bg-success') !== null;
                
                // Apply category filter
                if (categoryFilter !== 'all' && category !== categoryFilter) {
                    show = false;
                }
                
                // Apply price filter
                if (price < minPrice || price > maxPrice) {
                    show = false;
                }
                
                // Apply stock filter
                if (inStockOnly && !inStock) {
                    show = false;
                }
                
                // Show or hide the card
                if (show) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Update product count
            productCount.textContent = `${visibleCount} product${visibleCount !== 1 ? 's' : ''} available`;
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('filterModal'));
            if (modal) {
                modal.hide();
            }
        });
    }
    
    // Add to cart functionality with feedback
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const button = this.querySelector('.add-to-cart-btn');
            const originalText = button.innerHTML;
            
            // Show loading state
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';
            button.disabled = true;
            
            // Submit the form
            fetch(this.action, {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    button.innerHTML = '<i class="fas fa-check me-2"></i>Added!';
                    button.classList.remove('btn-success');
                    button.classList.add('btn-primary');
                    
                    // Update cart count in navbar if exists
                    const cartCount = document.querySelector('.cart-count');
                    if (cartCount) {
                        cartCount.textContent = data.cart_count;
                    }
                    
                    // Show toast notification if available
                    showToast('Product added to cart successfully!', 'success');
                } else {
                    // Show error message
                    button.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Error';
                    button.classList.remove('btn-success');
                    button.classList.add('btn-danger');
                    showToast('Failed to add product to cart', 'error');
                }
                
                // Reset button state after a delay
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                    button.classList.remove('btn-primary', 'btn-danger');
                    button.classList.add('btn-success');
                }, 2000);
            })
            .catch(error => {
                console.error('Error:', error);
                button.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Error';
                button.classList.remove('btn-success');
                button.classList.add('btn-danger');
                showToast('Network error occurred', 'error');
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                    button.classList.remove('btn-danger');
                    button.classList.add('btn-success');
                }, 2000);
            });
        });
    });
    
    // Function to update product count
    function updateProductCount() {
        const visibleProducts = document.querySelectorAll('.product-card[style="display: block"], .product-card:not([style])');
        if (productCount) {
            productCount.textContent = `${visibleProducts.length} product${visibleProducts.length !== 1 ? 's' : ''} available`;
        }
    }
    
    // Toast notification function
    function showToast(message, type = 'info') {
        // Check if toast container exists, if not create one
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        const toastId = 'toast-' + Date.now();
        const bgColor = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
        
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgColor} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
        toast.show();
        
        // Remove toast from DOM after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function () {
            this.remove();
        });
    }
    
    // Initialize product count
    updateProductCount();
    
    // Add smooth scrolling for category links
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
});