// Helpers
const qs = (s, p = document) => p.querySelector(s);
const qsa = (s, p = document) => [...p.querySelectorAll(s)];
const notify = (msg, type = "success") => {
  const n = qs("#notification");
  n.textContent = msg;
  n.className = `notification ${type} show`;
  setTimeout(() => n.classList.remove("show"), 3000);
};

// User Data
let userData = {
  firstName: "Nikhil",
  lastName: "Jogi",
  email: "njogi16@gmail.com",
  contact: "",
  birthDate: { day: "", month: "", year: "" },
  gender: "male",
  loyaltyPoints: 25,
  addresses: [{
    id: 1, name: "Home Address", fullName: "Nikhil Jogi",
    phone: "+91 98765 43210", pincode: "400001",
    addressLine1: "123 Main Street, Apt 4B", city: "Mumbai", state: "Maharashtra",
    landmark: "Near Central Park"
  }],
  orders: [],
  recentItems: [
    { id: 1, name: "Garden Tool Kit", price: "₹102", image: "C:\Users\HP\OneDrive\Desktop\ferns And Hub\gardening product\1.png" },
    { id: 2, name: "Foliage  plants", price: "₹300", image: "C:\Users\HP\OneDrive\Desktop\ferns And Hub\plants image\Foliage Plants.png" },
    { id: 3, name: "Falling Plants", price: "₹499", image: "C:\Users\HP\OneDrive\Desktop\ferns And Hub\plants image\Falling Plants.png" }
  ]
};

// Init
document.addEventListener("DOMContentLoaded", () => {
  setupBirthDate();
  loadProfile();
  renderAddresses();
  renderOrders();
  renderRecent();
  setupEvents();
});

// Populate Birthdate
function setupBirthDate() {
  const days = Array.from({ length: 31 }, (_, i) => i + 1);
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const yearNow = new Date().getFullYear();
  const years = Array.from({ length: 101 }, (_, i) => yearNow - i);

  fillSelect("birthDay", days);
  fillSelect("birthMonth", months.map((m,i) => [i+1, m]));
  fillSelect("birthYear", years);

  let { day, month, year } = userData.birthDate;
  if(day) qs("#birthDay").value = day;
  if(month) qs("#birthMonth").value = month;
  if(year) qs("#birthYear").value = year;
}

function fillSelect(id, arr) {
  const sel = qs(`#${id}`);
  arr.forEach(v => {
    let val = Array.isArray(v) ? v[0] : v;
    let text = Array.isArray(v) ? v[1] : v;
    sel.insertAdjacentHTML("beforeend", `<option value="${val}">${text}</option>`);
  });
}

// Load Profile Info
function loadProfile() {
  qs("#firstName").value = userData.firstName;
  qs("#lastName").value = userData.lastName;
  qs("#email").value = userData.email;
  qs("#contact").value = userData.contact;
  qs(`[name="gender"][value="${userData.gender}"]`).checked = true;
  qs("#pointsValue").textContent = `₹${userData.loyaltyPoints}`;
  updateCounts();
}

function updateCounts() {
  qs('a[data-tab="address"] .menu-count').textContent = userData.addresses.length;
  qs('a[data-tab="orders"] .menu-count').textContent = userData.orders.length;
}

// Render Sections
function renderAddresses() {
  const list = qs("#addressList");
  list.innerHTML = userData.addresses.length ? userData.addresses.map(a => `
    <div class="address-item" data-id="${a.id}">
      <div class="address-header">
        <h3>${a.name}</h3>
        <div>
          <button class="btn btn-primary edit">Edit</button>
          <button class="btn btn-danger delete">Delete</button>
        </div>
      </div>
      <p>${a.fullName}</p>
      <p>${a.addressLine1}</p>
      <p>${a.city}, ${a.state} - ${a.pincode}</p>
      <p>Phone: ${a.phone}</p>
      ${a.landmark ? `<p>Landmark: ${a.landmark}</p>` : ""}
    </div>
  `).join("") : `<div class="empty-state"><i class="fas fa-map-marker-alt"></i><h3>No addresses saved</h3></div>`;
}

function renderOrders() {
  qs("#ordersList").innerHTML = userData.orders.length ? "" : `
    <div class="empty-state">
      <i class="fas fa-shopping-bag"></i>
      <h3>No orders yet</h3>
      <button class="btn btn-primary" id="startShoppingBtn">Start Shopping</button>
    </div>`;
}

function renderRecent() {
  const c = qs("#recentItems");
  c.innerHTML = userData.recentItems.length ? userData.recentItems.map(i => `
    <div class="recent-item">
      <img src="${i.image}" alt="${i.name}"/>
      <h4>${i.name}</h4><p>${i.price}</p>
      <button class="btn btn-primary">View Again</button>
    </div>`).join("") :
    `<div class="empty-state"><i class="fas fa-history"></i><h3>No recently viewed items</h3></div>`;
}

// Events
function setupEvents() {
  // Tabs
  qsa(".sidebar-menu a").forEach(link => link.addEventListener("click", e => {
    e.preventDefault();
    if (link.classList.contains("logout")) return logout();
    qsa(".sidebar-menu a").forEach(l => l.classList.remove("active"));
    link.classList.add("active");
    qsa(".tab-content").forEach(t => t.classList.remove("active"));
    qs(`#${link.dataset.tab}`).classList.add("active");
  }));

  // Profile Save
  qs("#profileForm").addEventListener("submit", e => {
    e.preventDefault();
    Object.assign(userData, {
      firstName: qs("#firstName").value,
      lastName: qs("#lastName").value,
      email: qs("#email").value,
      contact: qs("#contact").value,
      birthDate: { day: qs("#birthDay").value, month: qs("#birthMonth").value, year: qs("#birthYear").value },
      gender: qs("[name='gender']:checked").value
    });
    qs(".user-avatar").textContent = userData.firstName[0] + userData.lastName[0];
    qs(".user-info div:last-child").textContent = `${userData.firstName} ${userData.lastName}`;
    notify("Profile updated!");
  });

  // Password Change
  qs("#passwordForm").addEventListener("submit", e => {
    e.preventDefault();
    let p1 = qs("#newPassword").value, p2 = qs("#confirmPassword").value;
    if (p1 !== p2) return notify("Passwords don't match!", "error");
    if (p1.length < 6) return notify("Password too short!", "error");
    notify("Password changed!");
    e.target.reset();
  });

  // Address actions
  qs("#addressList").addEventListener("click", e => {
    const id = +e.target.closest(".address-item")?.dataset.id;
    if (e.target.classList.contains("delete")) {
      userData.addresses = userData.addresses.filter(a => a.id !== id);
      renderAddresses(); updateCounts(); notify("Address deleted");
    }
    if (e.target.classList.contains("edit")) {
      notify("Address edit modal open"); // Here you’d open modal
    }
  });

  // Referral
  qs("#copyLinkBtn")?.addEventListener("click", () => {
    navigator.clipboard.writeText("https://example.com/ref/123").then(() => notify("Referral link copied!"));
  });
}

// Logout
function logout() {
  if (confirm("Are you sure you want to log out?")) {
    notify("You have been logged out.", "success");
    window.location.href = "index.html"; // redirect
  }
}
