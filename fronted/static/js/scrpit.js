document.addEventListener('DOMContentLoaded', () => {
  // Search bar functionality
  const searchAddon = document.getElementById('search-addon');
  const searchInput = document.getElementById('searchInput');

  searchAddon.addEventListener('click', (e) => {
    e.preventDefault(); // Prevent any default behavior
    const query = searchInput.value.trim();
    if (query) {
      alert(`Searching for: ${query}`);
      // Add actual search functionality here (e.g., filter products or redirect to search page)
    } else {
      alert('Please enter a search term.');
    }
  });

  // Contact form submission
  const contactForm = document.getElementById('contactForm');
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('nameInput').value.trim();
    const email = document.getElementById('emailInput').value.trim();
    const message = document.getElementById('messageInput').value.trim();

    if (name && email && message) {
      alert(`Message sent! Name: ${name}, Email: ${email}, Message: ${message}`);
      contactForm.reset();
      // Add actual form submission logic here (e.g., send to server)
    } else {
      alert('Please fill out all fields.');
    }
  });

  // Add click event listeners to category items
  const categoryItems = document.querySelectorAll('.category-item');

  categoryItems.forEach(item => {
    item.addEventListener('click', () => {
      const category = item.getAttribute('data-category');
      alert(`Selected category: ${category}`);
      // Add actual category selection logic here (e.g., redirect to category page or filter products)
    });
  });
});