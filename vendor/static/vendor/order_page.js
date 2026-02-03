// Handle the dropdown toggle
function toggleDetails(orderId) {
    const detailsRow = document.getElementById(`details-${orderId}`);
    const icon = document.getElementById(`icon-${orderId}`);
    
    const isHidden = detailsRow.classList.contains('hidden');
    
    if (isHidden) {
        detailsRow.classList.remove('hidden');
        icon.style.transform = 'rotate(180deg)';
    } else {
        detailsRow.classList.add('hidden');
        icon.style.transform = 'rotate(0deg)';
    }
}

function updateOrderStatus(orderId, status) {
    const row = document.getElementById(`order-row-${orderId}`);
    const details = document.getElementById(`details-${orderId}`);
    const csrftoken = getCSRFCookie()
    
    row.style.opacity = '0.5';
    if (details) details.style.opacity = '0.5';

    fetch(`/vendor/orders/${orderId}/update-status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // If it was dispatched or finished, remove it. 
            // Otherwise, reload to update the action button state
            location.reload(); 
        }
    });
}

function filterOrders() {
    const input = document.getElementById("orderSearch");
    const filter = input.value.toUpperCase();
    const table = document.getElementById("ordersTable");
    const rows = table.getElementsByClassName("group"); // Selecting main rows only
    let foundCount = 0;

    for (let i = 0; i < rows.length; i++) {
        // We check the ID span and the Name paragraph inside the first <td>
        const textContent = rows[i].getElementsByTagName("td")[0].textContent.toUpperCase();
        const detailsRow = document.getElementById(`details-${rows[i].id.split('-').pop()}`);

        if (textContent.indexOf(filter) > -1) {
            rows[i].style.display = "";
            foundCount++;
        } else {
            rows[i].style.display = "none";
            // Also hide the expanded details if the main row is hidden
            if (detailsRow) detailsRow.classList.add('hidden');
        }
    }

    // Toggle "No Results" message
    document.getElementById("noResults").classList.toggle('hidden', foundCount > 0);
}

function quickFilter(type) {
    const rows = document.getElementById("ordersTable").getElementsByClassName("group");
    const searchInput = document.getElementById("orderSearch");
    
    // Clear search bar when using quick filters
    searchInput.value = ""; 

    for (let i = 0; i < rows.length; i++) {
        const paymentBadge = rows[i].querySelector('.badge').textContent.toUpperCase();
        const detailsRow = document.getElementById(`details-${rows[i].id.split('-').pop()}`);

        if (type === 'all' || paymentBadge.includes(type.toUpperCase())) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
            if (detailsRow) detailsRow.classList.add('hidden');
        }
    }
}

// This function matches the check in the global script above
function refreshOrderTable(order) {
    const tableBody = document.querySelector("tbody");
    
    // Clear "No Active Orders" if it exists
    if(tableBody.innerText.includes("No Active Orders")) tableBody.innerHTML = "";
    

    // 2. Insert the HTML string as actual DOM elements
    // 'afterbegin' puts it at the very top of the <tbody>
    tableBody.insertAdjacentHTML('afterbegin', order.html);

    // 3. Target the newly injected row
    const newRow = tableBody.firstElementChild;


    const newOrderElement = tableBody.firstElementChild;

    newOrderElement.classList.add("new-order-flash");

    // 6. Update the Order Count badge at the top of the page
    const badge = document.querySelector("#number-of-active-order");
    if (badge) {
        let currentCount = parseInt(badge.innerText) || 0;
        badge.innerText = `${currentCount + 1} Orders`;
    }

    // newOrderElement.classList.add("new-order-flash", "bg-orange-50", "border-primary");
    // // 4. Remove the animation after exactly 5 seconds
    // setTimeout(() => {
    //     newOrderElement.classList.remove("animate-pulse", "bg-orange-50", "border-primary");
        
    //     // Optional: Add a smooth transition class so the color fade is gentle
    //     newOrderElement.classList.add("transition-colors", "duration-1000");
    // }, 5000);
    
}