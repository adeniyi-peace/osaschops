function toggleStoreStatus() {
        // Toggle opacity to give immediate feedback
        const hero = document.querySelector('.bg-charcoal');
        hero.style.opacity = '0.8';
        const csrftoken = getCSRFCookie()

        fetch('', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: 'toggle_status=true'
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                location.reload();
            }
        });
    }