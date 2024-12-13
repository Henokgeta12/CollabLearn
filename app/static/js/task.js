document.addEventListener("DOMContentLoaded", function() 
{
    // Add event listeners for all task status dropdowns
    const statusDropdowns = document.querySelectorAll('.status-dropdown');

    statusDropdowns.forEach(function(dropdown) {
        dropdown.addEventListener('change', function() {
            const taskId = dropdown.dataset.taskId;
            const groupId = dropdown.dataset.groupId;
            const newStatus = dropdown.value;

            // Send POST request to update task status
            fetch(`/group/${groupId}/tasks/${taskId}/update_status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')  // Include CSRF token if needed
                },
                body: `status=${newStatus}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);  // Optional: Display success message
                }
            })
            .catch(error => {
                console.error('Error updating task status:', error);
            });
        });
    });
});
