// =====================
//  Amazon-Style Invoice
//  (Responsive & Friendly)
// =====================

// ✅ Setup Print Button
function setupPrintButton() {
    const printBtn = document.querySelector('.btn-print');
    if (printBtn) {
        printBtn.addEventListener('click', () => window.print());
    }
}

// ✅ Animate Invoice Load
function animateInvoice() {
    const container = document.querySelector('.invoice-container');
    if (container) {
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        setTimeout(() => {
            container.style.transition = 'all 0.6s ease';
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 150);
    }
}

// ✅ Format Amounts (if used dynamically)
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// ✅ Handle Table Responsiveness
function handleTableResponsive() {
    const tables = document.querySelectorAll('.items-table');
    tables.forEach(table => {
        const container = table.parentElement;
        if (table.scrollWidth > container.clientWidth) {
            container.classList.add('table-scroll');
        } else {
            container.classList.remove('table-scroll');
        }
    });
}

// ✅ Smooth Scroll to Top (optional UX)
function smoothScrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ✅ Initialize Everything
document.addEventListener('DOMContentLoaded', () => {
    console.log('Invoice page initialized ✅');
    setupPrintButton();
    animateInvoice();
    handleTableResponsive();
    window.addEventListener('resize', handleTableResponsive);
});

// ✅ Export for modular use (optional)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        setupPrintButton,
        animateInvoice,
        formatCurrency,
        handleTableResponsive,
        smoothScrollToTop
    };
}
