document.addEventListener('DOMContentLoaded', function() {
    const checkoutForm = document.getElementById('checkout-form');
    const placeOrderBtn = document.getElementById('place-order-btn');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    const paymentMethod = document.getElementById('payment_method');
    const paymentDescription = document.getElementById('payment-description');
    
    // Handle payment method change
    if (paymentMethod) {
        paymentMethod.addEventListener('change', function() {
            if (this.value === 'online') {
                paymentDescription.textContent = 'Secure online payment with Razorpay';
            } else {
                paymentDescription.textContent = 'Pay when your order is delivered';
            }
        });
    }

    if (checkoutForm && placeOrderBtn) {
        checkoutForm.addEventListener('submit', function(e) {
            // Validate address selection
            const selectedAddress = document.querySelector('input[name="address_id"]:checked');
            if (!selectedAddress) {
                e.preventDefault();
                showAlert('Please select a delivery address.', 'warning');
                return;
            }

            // Validate payment method
            const paymentMethod = document.getElementById('payment_method');
            if (!paymentMethod.value) {
                e.preventDefault();
                showAlert('Please select a payment method.', 'warning');
                return;
            }

            // Show loading modal
            loadingModal.show();
            
            // Disable the button to prevent multiple submissions
            placeOrderBtn.disabled = true;
            placeOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing Order...';
            
            // Form will continue to submit normally
        });
    }

    // Add address selection validation and styling
    const addressRadios = document.querySelectorAll('input[name="address_id"]');
    addressRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            // Remove previous selections
            document.querySelectorAll('.address-card').forEach(card => {
                card.classList.remove('border-success', 'selected-address');
            });
            
            // Highlight selected address
            if (this.checked) {
                const selectedCard = this.closest('.address-card');
                selectedCard.classList.add('border-success', 'selected-address');
            }
        });
    });

    // Initialize address cards based on default selection
    function initializeAddressCards() {
        const defaultAddress = document.querySelector('input[name="address_id"]:checked');
        if (defaultAddress) {
            const selectedCard = defaultAddress.closest('.address-card');
            selectedCard.classList.add('border-success', 'selected-address');
        }
    }

    // Show custom alert function
    function showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert after the main heading
        const heading = document.querySelector('h2.fw-bold');
        heading.parentNode.insertBefore(alertDiv, heading.nextSibling);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Initialize on page load
    initializeAddressCards();
});