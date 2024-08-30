// Function to open a modal
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

// Function to close a modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Logout function (example; replace with actual implementation)
function logout() {
    // Call the logout route
    window.location.href = "{{ url_for('logout') }}";
}

// Add event listeners to close the modal when clicking outside of it
window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = 'none';
    }
}
