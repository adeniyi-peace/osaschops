function toggleAvailability(itemId, isChecked, checkbox) {
    const label = event.target.closest('label').querySelector('.label-text');
    const csrftoken = getCSRFCookie()

    // Optimistic UI Update
    label.innerText = isChecked ? 'Available' : 'Unavailable';
    label.className = `label-text font-bold text-[10px] uppercase ${isChecked ? 'text-primary' : 'text-gray-400'}`;

    fetch("", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ available: isChecked, itemId:itemId })
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .catch(error => {
        alert("Failed to update status. Please try again.");
        // Revert on failure
        checkbox.checked = !isChecked
        label.innerText = !isChecked ? 'Available' : 'Unavailable';
        label.className = `label-text font-bold text-[10px] uppercase ${isChecked ? 'text-primary' : 'text-gray-400'}`;

    });
}

async function openFormModal(productId = null) {
    const container = document.getElementById('modal_content_container');
    const loader = document.getElementById('loader_template').innerHTML;
    const modal = document.getElementById('form_modal');

    // 1. Show loader and open modal
    container.innerHTML = loader;
    modal.showModal();

    // 2. Build URL (If ID exists, it's Edit; else it's Add)
    const url = productId ? `/vendor/menu/edit-menu/${productId}/` : `/vendor/menu/add-menu/`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        if (data.success)  container.innerHTML = data.html;
    } catch (error) {
        container.innerHTML = `
            <div class="modal-box text-center">
                <p class="text-error font-bold">Failed to load content.</p>
                <button class="btn btn-sm mt-4" onclick="form_modal.close()">Close</button>
            </div>`;
    }
}

async function openDeleteModal(productId) {
    const container = document.getElementById('delete_content_container');
    const loader = document.getElementById('loader_template').innerHTML;
    const modal = document.getElementById('delete_modal');

    container.innerHTML = loader;
    modal.showModal();

    try {
        // Fetch the delete confirmation partial from Django
        const response = await fetch(`/vendor/menu/delete-menu/${productId}/`);
        if (!response.ok) throw new Error('Failed to fetch');
        
        const data = await response.json();
        if (data.success) container.innerHTML = data.html;
    } catch (error) {
        container.innerHTML = `
            <div class="modal-box text-center">
                <p class="text-error font-bold">Failed to load content.</p>
                <button class="btn btn-sm mt-4" onclick="delete_modal.close()">Close</button>
            </div>`;
    }
}

async function handleSubmit(e) {
    e.preventDefault()
    const form = e.currentTarget

    const container = document.getElementById('modal_content_container');
    const loader = document.getElementById('loader_template').innerHTML;
    const modal = document.getElementById('form_modal');

    container.innerHTML = loader;

    
    const form_data = new FormData(form)
    const url = form.getAttribute("action")


    fetch(url, {
        method: "POST",
        // headers: {
        //     "Content-Type": "application/json"
        // },
        body: form_data
    }).then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json()
    }).then(data => {
        
        if (data.success) {
            location.reload(); 
        }
        else {
            container.innerHTML = data.html
        }
    }).catch(error =>{
        console.error("Error during POST request:", error)
    })
}