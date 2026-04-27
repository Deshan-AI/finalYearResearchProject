// src/web/static/js/main.js
// Main JavaScript file for interactive features

document.addEventListener('DOMContentLoaded', function() {
    console.log('Student Burnout Detection System loaded');
    
    // Auto-refresh dashboard every 5 minutes
    if (window.location.pathname.includes('/student/')) {
        setTimeout(() => {
            location.reload();
        }, 300000); // 5 minutes
    }
});

// Format date helper
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Show toast notification
function showNotification(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove after 5 seconds
    setTimeout(() => toast.remove(), 5000);
}

// API helper functions
const api = {
    get: async (url) => {
        const response = await fetch(url);
        return response.json();
    },
    
    post: async (url, data) => {
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        return response.json();
    }
};