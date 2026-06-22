// Centralized API Base URL
const API_BASE = "http://127.0.0.1:5000";

// Helper to check auth status and update UI
function checkAuth() {
    const token = localStorage.getItem("token");
    const navLinks = document.getElementById("nav-links");
    const authButtons = document.getElementById("auth-buttons");

    if (token) {
        if(navLinks) navLinks.style.display = "flex";
        if(authButtons) {
            authButtons.innerHTML = `<button class="btn btn-danger" onclick="logout()">Logout</button>`;
        }
    } else {
        if(navLinks) navLinks.style.display = "none";
        if(authButtons) {
            authButtons.innerHTML = `
                <a href="/login" class="btn btn-secondary" style="width: auto;">Login</a>
                <a href="/register" class="btn" style="width: auto;">Register</a>
            `;
        }
    }
}

// Redirect if not authenticated
function requireAuth() {
    if (!localStorage.getItem("token")) {
        window.location.href = "/login";
    }
}

// Custom Fetch with Auto Auth injection
async function authFetch(url, options = {}) {
    const token = localStorage.getItem("token");
    if (!options.headers) options.headers = {};
    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }
    
    // Automatically set Content-Type if body is JSON string
    if (typeof options.body === "string" && !options.headers["Content-Type"]) {
        options.headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`${API_BASE}${url}`, options);
    if (response.status === 401 || response.status === 422) {
        // Token invalid or expired
        localStorage.removeItem("token");
        window.location.href = "/login";
    }
    return response;
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/login";
}

// Generic Show Alert function
function showAlert(elementId, message, type='error') {
    const el = document.getElementById(elementId);
    if(el) {
        el.className = `msg-alert ${type}`;
        el.innerText = message;
    }
}

// Run auth check on load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    if (localStorage.getItem("token") && document.getElementById("notif-bell")) {
        fetchNotifications();
    }
});

// Notifications
async function fetchNotifications() {
    try {
        const res = await authFetch("/analysis/notifications");
        if (res.ok) {
            const data = await res.json();
            updateNotificationUI(data);
        }
    } catch(e) {}
}

function updateNotificationUI(notifs) {
    const badge = document.getElementById("notif-badge");
    const list = document.getElementById("notif-list");
    if(!badge || !list) return;

    if (notifs.length > 0) {
        badge.innerText = notifs.length;
        badge.style.display = 'block';
        list.innerHTML = notifs.map(n => 
            `<div class="notif-item ${n.type}"><strong>${new Date(n.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</strong><br>${n.message}</div>`
        ).join("");
    } else {
        badge.style.display = 'none';
        list.innerHTML = `<div class="notif-item text-muted">No new alerts.</div>`;
    }
}

function toggleNotifs() {
    const box = document.getElementById("notif-dropdown");
    if(box) box.classList.toggle("show");
}