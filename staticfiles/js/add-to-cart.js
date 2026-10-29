// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get all add to cart forms
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');

    // Add submit event listener to each form
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent normal form submission

            const productId = this.querySelector('.add-to-cart-btn').getAttribute('data-product-id');
            const submitButton = this.querySelector('.add-to-cart-btn');
            
            // Show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';

            // Get form data
            const formData = new FormData(this);
            
            // Send AJAX request
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update cart count
                    const cartCount = document.getElementById('cart-count');
                    const mobileCartCount = document.getElementById('mobile-cart-count');
                    if (cartCount) cartCount.textContent = data.cart_items_count;
                    if (mobileCartCount) mobileCartCount.textContent = data.cart_items_count;

                    // Show success message
                    showSuccessToast('Product added to cart successfully!');
                } else {
                    // Show error message
                    showErrorToast(data.error || 'Error adding product to cart');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showErrorToast('An error occurred while adding to cart');
            })
            .finally(() => {
                // Reset button state
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-cart-plus me-2"></i>Add to Cart';
            });
        });
    });
});

// Toast functions
function showSuccessToast(message) {
    const toastEl = document.getElementById('successToast');
    if (toastEl) {
        const toast = new bootstrap.Toast(toastEl);
        toastEl.querySelector('.toast-body').textContent = message;
        toast.show();
    }
}

function showErrorToast(message) {
    const toastEl = document.getElementById('errorToast');
    if (toastEl) {
        const toast = new bootstrap.Toast(toastEl);
        toastEl.querySelector('#errorToastMessage').textContent = message;
        toast.show();
    }
}