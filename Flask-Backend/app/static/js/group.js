document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.status-dropdown').forEach(dropdown => {
        dropdown.addEventListener('change', function () {
            const taskId = this.dataset.taskId;
            const groupId = this.dataset.groupId;
            const newStatus = this.value;

            // Send the status update via fetch
            fetch(`/group/${groupId}/update_task_status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: taskId, status: newStatus })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Task status updated successfully!');
                } else {
                    alert('Error updating task status.');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

