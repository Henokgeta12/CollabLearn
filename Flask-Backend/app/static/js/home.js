function confirmLogout() {
    return confirm("Are you sure you want to logout?");
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('search-form').addEventListener('submit', function(event) {
        event.preventDefault();
        var query = document.getElementById('search').value;

        fetch(searchUrl + '?search=' + encodeURIComponent(query))
            .then(response => response.json())
            .then(data => {
                var resultsHtml = '<h4>Search Results</h4>';
                var foundResults = false;

                if (data.users.length > 0) {
                    resultsHtml += '<h5>Users</h5><ul>';
                    data.users.forEach(function(user) {
                        resultsHtml += '<li>' + user.username + '</li>';
                    });
                    resultsHtml += '</ul>';
                    foundResults = true;
                }

                if (data.groups.length > 0) {
                    resultsHtml += '<h5>Groups</h5><ul>';
                    data.groups.forEach(function(group) {
                        resultsHtml += '<li>' + group.name + '</li>';
                    });
                    resultsHtml += '</ul>';
                    foundResults = true;
                }

                if (!foundResults) {
                    resultsHtml += '<div class="alert alert-warning">No users or groups found for "<strong>' + query + '</strong>".</div>';
                }

                document.getElementById('search-results').innerHTML = resultsHtml;
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('search-results').innerHTML = '<div class="alert alert-danger">An error occurred while searching. Please try again.</div>';
            });
    });
});
