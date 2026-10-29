// Dashboard functionality
document.addEventListener("DOMContentLoaded", () => {
    initializeDashboard();
    addSmoothAnimations();
});

function initializeDashboard() {
    setupTabNavigation();
    setupMobileMenu();
    setupOrderDetails();
    setupAddressActions();
    initializeCounters();
}

function addSmoothAnimations() {
    // Add entrance animations for dashboard cards
    const cards = document.querySelectorAll('.summary-box, .overview-card, .order-item, .address-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function initializeCounters() {
    // Animate counter numbers
    const numbers = document.querySelectorAll('.number');
    numbers.forEach(number => {
        const finalValue = parseInt(number.textContent);
        let currentValue = 0;
        const duration = 1000; // 1 second
        const increment = finalValue / (duration / 16); // 60fps

        function updateCounter() {
            if (currentValue < finalValue) {
                currentValue = Math.min(currentValue + increment, finalValue);
                number.textContent = Math.round(currentValue);
                requestAnimationFrame(updateCounter);
            }
        }

        updateCounter();
    });
}

// Tab Navigation
function setupTabNavigation() {
    const tabs = document.querySelectorAll(".sidebar-menu a[data-tab]");
    const contents = document.querySelectorAll(".tab-content");
    const tabLinks = document.querySelectorAll(".tab-link");

    // Function to switch tabs
    function switchTab(tabName) {
        tabs.forEach(t => t.classList.remove("active"));
        contents.forEach(c => c.classList.remove("active"));

        const activeTab = document.querySelector(`[data-tab="${tabName}"]`);
        const activeContent = document.getElementById(tabName);
        
        if (activeTab && activeContent) {
            activeTab.classList.add("active");
            activeContent.classList.add("active");
        }

        // Close sidebar on mobile after clicking a tab
        if (window.innerWidth <= 768) {
            toggleSidebar();
        }
    }

    // Sidebar tab click event
    tabs.forEach(tab => {
        tab.addEventListener("click", e => {
            e.preventDefault();
            switchTab(tab.dataset.tab);
        });
    });

    // Quick action tab links
    tabLinks.forEach(link => {
        link.addEventListener("click", e => {
            e.preventDefault();
            const tabName = link.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Check if there's a tab in URL hash
    const hash = window.location.hash.substring(1);
    if (hash) {
        switchTab(hash);
    }
}

// Mobile Menu
function setupMobileMenu() {
    // Close sidebar when clicking on overlay
    document.querySelector('.sidebar-overlay').addEventListener('click', toggleSidebar);

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            const sidebar = document.querySelector('.sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    });
}

// Order Details
function setupOrderDetails() {
    const orderItems = document.querySelectorAll('.order-item');
    orderItems.forEach(item => {
        item.addEventListener('click', function() {
            const orderId = this.dataset.orderId;
            if (orderId) {
                window.location.href = `/order/${orderId}/`;
            }
        });
    });
}

// Address Actions
function setupAddressActions() {
    // Confirm delete address
    const deleteButtons = document.querySelectorAll('.delete-address-btn');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this address?')) {
                e.preventDefault();
            }
        });
    });
}

// Toggle Mobile Sidebar
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

// Show Order Details
function showOrderDetails(orderId) {
    window.location.href = `/order/${orderId}/`;
}