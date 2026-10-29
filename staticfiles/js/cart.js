document.addEventListener('DOMContentLoaded', function() {
    function showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        const toastId = `toast-${Date.now()}`;
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove the toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    function updateCartSummary(data) {
        const cartTotal = document.getElementById('cart-total');
        if (cartTotal) {
            cartTotal.textContent = `₹${data.total}`;
        }
        
        // Update cart count in header if it exists
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement && data.cart_items_count !== undefined) {
            if (data.cart_items_count > 0) {
                cartCountElement.textContent = data.cart_items_count;
                cartCountElement.style.display = 'inline';
            } else {
                cartCountElement.style.display = 'none';
            }
        }
    }

    function handleRemoveItem(e) {
        const button = e.target.closest('.remove-item-btn');
        if (!button) return;
        
        e.preventDefault();
        
        if (!confirm('Are you sure you want to remove this item from your cart?')) {
            return;
        }
        
        const itemId = button.dataset.itemId;
        const cartItem = document.getElementById(`cart-item-${itemId}`);
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Send remove request
        fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Fade out and remove the item
                cartItem.style.opacity = '0';
                setTimeout(() => {
                    cartItem.remove();
                    
                    // Update cart summary
                    updateCartSummary(data);
                    
                    // Show success message
                    showToast('Item removed from cart');
                    
                    // If cart is empty, show empty cart message
                    if (data.cart_empty) {
                        const cartContent = document.querySelector('.cart-content');
                        if (cartContent) {
                            cartContent.innerHTML = `
                                <div class="text-center py-5">
                                    <i class="fas fa-shopping-cart fa-3x text-muted mb-3"></i>
                                    <h4>Your cart is empty</h4>
                                    <p class="text-muted">Add some plants to your cart!</p>
                                    <a href="/products/" class="btn btn-success">Browse Products</a>
                                </div>
                            `;
                        }
                    }
                }, 300);
            } else {
                showToast(data.error || 'Error removing item from cart', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error removing item from cart', 'danger');
        });
    }

    function handleQuantityUpdate(e) {
        const form = e.target.closest('.quantity-update-form');
        if (!form) return;
        
        e.preventDefault();
        const itemId = form.dataset.itemId;
        const quantityInput = form.querySelector('[name=quantity]');
        const quantity = quantityInput.value;
        const submitButton = form.querySelector('.update-quantity-btn');
        
        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Send update request
        fetch(`/cart/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                quantity: parseInt(quantity)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update item total
                const itemTotal = document.getElementById(`item-total-${itemId}`);
                if (itemTotal) {
                    itemTotal.textContent = `₹${data.item_total}`;
                }
                
                // Update cart summary
                updateCartSummary(data);
                
                // Show success message
                showToast('Cart updated successfully');
                
                // Hide update button
                submitButton.style.display = 'none';
            } else {
                showToast(data.error || 'Error updating cart', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating cart', 'danger');
        })
        .finally(() => {
            // Reset button state
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-sync-alt"></i>';
        });
    }

    // Add event listeners
    document.addEventListener('click', handleRemoveItem);
    
    // Add submit event listeners to all quantity update forms
    const quantityForms = document.querySelectorAll('.quantity-update-form');
    quantityForms.forEach(form => {
        form.addEventListener('submit', handleQuantityUpdate);
        
        // Show update button when quantity changes
        const quantityInput = form.querySelector('input[name="quantity"]');
        const updateBtn = form.querySelector('.update-quantity-btn');
        const originalValue = quantityInput.value;
        
        if (quantityInput && updateBtn) {
            quantityInput.addEventListener('change', () => {
                updateBtn.style.display = this.value !== originalValue ? 'block' : 'none';
            });
            
            quantityInput.addEventListener('input', () => {
                updateBtn.style.display = this.value !== originalValue ? 'block' : 'none';
            });
        }
    });
});