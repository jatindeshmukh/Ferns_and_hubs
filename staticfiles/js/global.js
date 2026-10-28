// static/js/global.js

// Global utility functions
const FernsNHerbs = {
  // Get CSRF token
  getCookie(name) {
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
  },

  // Show toast message
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    toast.setAttribute('role', 'alert');
    
    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
      document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
      toast.remove();
    });
  },

  // Add to cart function
  addToCart(productId, quantity = 1) {
    fetch('/cart/add/' + productId + '/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.getCookie('csrftoken')
      },
      body: JSON.stringify({ 'quantity': quantity })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        document.getElementById('cart-count').textContent = data.cart_items_count;
        this.showToast('Product added to cart successfully!', 'success');
      } else {
        this.showToast('Failed to add product to cart', 'error');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      this.showToast('An error occurred', 'error');
    });
  },

  // Initialize cart functionality
  initCart() {
    document.addEventListener('click', (e) => {
      if (e.target.closest('.add-to-cart')) {
        const button = e.target.closest('.add-to-cart');
        const productId = button.getAttribute('data-product-id');
        this.addToCart(productId);
      }
    });
  },

  // Initialize notifications
  initNotifications() {
    // Notification click handler
    document.addEventListener('click', (e) => {
      const notificationItem = e.target.closest('.notification-item');
      if (notificationItem) {
        const notificationId = notificationItem.getAttribute('data-notification-id');
        this.markNotificationAsRead(notificationId);
      }
    });
  },

  // Mark notification as read
  markNotificationAsRead(notificationId) {
    fetch('/notifications/mark-read/' + notificationId + '/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': this.getCookie('csrftoken')
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        const notificationItem = document.querySelector(`[data-notification-id="${notificationId}"]`);
        if (notificationItem) {
          notificationItem.classList.remove('unread');
        }
        this.updateNotificationCount();
      }
    });
  },

  // Update notification count
  updateNotificationCount() {
    const notificationCount = document.querySelector('.badge-notification');
    if (notificationCount) {
      const currentCount = parseInt(notificationCount.textContent);
      if (currentCount > 1) {
        notificationCount.textContent = currentCount - 1;
      } else {
        notificationCount.remove();
      }
    }
  }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  FernsNHerbs.initCart();
  FernsNHerbs.initNotifications();
});