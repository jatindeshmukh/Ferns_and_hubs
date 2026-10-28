// ===== CSRF TOKEN FUNCTION =====
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

// ===== TOAST FUNCTIONS =====
function showSuccessToast(message) {
  const toast = document.getElementById('successToast');
  if (toast) {
    if (message) {
      toast.querySelector('.toast-body').textContent = message;
    }
    new bootstrap.Toast(toast).show();
  }
}

function showErrorToast(message) {
  const toast = document.getElementById('errorToast');
  if (toast) {
    if (message) {
      document.getElementById('errorToastMessage').textContent = message;
    }
    new bootstrap.Toast(toast).show();
  }
}

function showOutOfStockToast() {
  const toast = document.getElementById('outOfStockToast');
  if (toast) {
    new bootstrap.Toast(toast).show();
  }
}

// ===== CART FUNCTIONS =====
function addToCart(productId) {
  fetch('/cart/add/' + productId + '/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      'quantity': 1
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Update cart count
      const cartCount = document.getElementById('cart-count');
      if (cartCount) {
        cartCount.textContent = data.cart_items_count;
      }
      
      // Show success message
      showSuccessToast('Product added to cart successfully!');
      
      // Send notification
      sendNotification('A new product has been added to your cart.');
    } else {
      showErrorToast(data.error || 'Failed to add product to cart');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showErrorToast('An error occurred while adding to cart');
  });
}

// ===== NOTIFICATION FUNCTIONS =====
function markNotificationAsRead(notificationId) {
  fetch('/notifications/mark-read/' + notificationId + '/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Remove unread styling
      const notificationItem = document.querySelector(`[data-notification-id="${notificationId}"]`);
      if (notificationItem) {
        notificationItem.classList.remove('unread');
      }
      
      // Update notification count
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
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function markAllNotificationsAsRead() {
  fetch('/notifications/mark-all-as-read/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Remove unread styling from all notifications
      const notificationItems = document.querySelectorAll('.notification-item');
      notificationItems.forEach(item => {
        item.classList.remove('unread');
      });
      
      // Remove notification count badge
      const notificationCount = document.querySelector('.badge-notification');
      if (notificationCount) {
        notificationCount.remove();
      }
      
      // Hide mark all button
      const markAllButton = document.querySelector('.mark-all-read');
      if (markAllButton) {
        markAllButton.style.display = 'none';
      }
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function sendNotification(message) {
  fetch('/notifications/send/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      'message': message
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Notification sent successfully');
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

// ===== SEARCH AND SORT FUNCTIONS =====
function filterProducts(searchInput, products) {
  const term = searchInput.value.toLowerCase().trim();
  products.forEach(product => {
    const productName = product.dataset.name.toLowerCase();
    const match = productName.includes(term);
    product.style.display = match ? 'block' : 'none';
  });
}

function sortProducts(sortSelect, products, productList) {
  const option = sortSelect.value;
  const sortedProducts = [...products];

  switch(option) {
    case 'price-asc':
      sortedProducts.sort((a, b) => parseFloat(a.dataset.price) - parseFloat(b.dataset.price));
      break;
    case 'price-desc':
      sortedProducts.sort((a, b) => parseFloat(b.dataset.price) - parseFloat(a.dataset.price));
      break;
    case 'name-asc':
      sortedProducts.sort((a, b) => a.dataset.name.localeCompare(b.dataset.name));
      break;
    case 'name-desc':
      sortedProducts.sort((a, b) => b.dataset.name.localeCompare(a.dataset.name));
      break;
    default:
      return;
  }

  // Clear and re-append sorted products
  productList.innerHTML = '';
  sortedProducts.forEach(product => {
    productList.appendChild(product);
  });
}

// ===== MOBILE RESPONSIVE FUNCTIONS =====
function handleMobileResize() {
  const isMobile = window.innerWidth <= 768;
  
  if (isMobile) {
    // Add mobile-specific classes
    document.body.classList.add('mobile-view');
    
    // Ensure navbar doesn't overflow
    const navbarCollapse = document.getElementById('navbarContent');
    if (navbarCollapse) {
      navbarCollapse.style.maxHeight = 'calc(100vh - 100px)';
      navbarCollapse.style.overflowY = 'auto';
    }
    
    // Adjust card heights for mobile
    const cards = document.querySelectorAll('.card, .product-card, .service-card');
    cards.forEach(card => {
      card.style.marginBottom = '15px';
    });
  } else {
    // Remove mobile-specific classes
    document.body.classList.remove('mobile-view');
    
    // Reset navbar styles
    const navbarCollapse = document.getElementById('navbarContent');
    if (navbarCollapse) {
      navbarCollapse.style.maxHeight = '';
      navbarCollapse.style.overflowY = '';
    }
  }
}

// ===== BASE DOM READY FUNCTION =====
document.addEventListener('DOMContentLoaded', function() {
  // Initialize toasts
  const successToast = new bootstrap.Toast(document.getElementById('successToast'));
  const errorToast = new bootstrap.Toast(document.getElementById('errorToast'));
  const outOfStockToast = new bootstrap.Toast(document.getElementById('outOfStockToast'));

  // Check URL parameters for messages
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('error') === 'out_of_stock') {
    showOutOfStockToast();
  }

  // Add to cart buttons event listeners
  document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', function() {
      const productId = this.getAttribute('data-product-id');
      addToCart(productId);
    });
  });

  // Notification click handlers
  const notificationItems = document.querySelectorAll('.notification-item');
  notificationItems.forEach(item => {
    item.addEventListener('click', function() {
      const notificationId = this.getAttribute('data-notification-id');
      markNotificationAsRead(notificationId);
    });
  });

  // Search functionality
  const searchInput = document.querySelector('input[name="q"]');
  const productItems = Array.from(document.querySelectorAll('.product-item'));
  if (searchInput && productItems.length > 0) {
    searchInput.addEventListener('input', () => filterProducts(searchInput, productItems));
  }

  // Sort functionality
  const sortSelect = document.getElementById('sort-select');
  const productList = document.getElementById('product-list');
  if (sortSelect && productItems.length > 0 && productList) {
    sortSelect.addEventListener('change', () => sortProducts(sortSelect, productItems, productList));
  }

  // Handle mobile responsiveness
  handleMobileResize();
  window.addEventListener('resize', handleMobileResize);
  
  // Prevent horizontal scrolling on mobile
  document.body.addEventListener('touchmove', function(e) {
    if (e.touches.length > 1) {
      e.preventDefault();
    }
  }, { passive: false });
});

// Additional utility functions
function debounce(func, wait, immediate) {
  let timeout;
  return function executedFunction() {
    const context = this;
    const args = arguments;
    const later = function() {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
}