AOS.init({ duration: 800, once: true, easing: 'ease-out-quad' });

// Navbar Scroll Effect
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    header.classList.toggle('shadow-soft', window.scrollY > 50);
});

// Toast Logic
document.addEventListener('DOMContentLoaded', () => {
    const toasts = document.querySelectorAll('.message-toast');
    toasts.forEach((toast) => {
        setTimeout(() => toast.classList.remove('translate-x-full', 'opacity-0'), 100);
        setTimeout(() => {
            toast.classList.add('translate-x-full', 'opacity-0');
            setTimeout(() => toast.remove(), 500);
        }, 10000);
    });
});



function toggleDrawer(open) {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('drawer-overlay');
    const content = document.getElementById('drawer-content');
    
    if (open) {
        drawer.classList.remove('invisible');
        setTimeout(() => {
            overlay.classList.add('opacity-100');
            content.classList.remove('translate-y-full');
        }, 10);
    } else {
        overlay.classList.remove('opacity-100');
        content.classList.add('translate-y-full');
        setTimeout(() => drawer.classList.add('invisible'), 300);
    }
}

document.getElementById('drawer-overlay').addEventListener('click', () => toggleDrawer(false));

// Update your existing updateCart function to trigger the drawer
//  async function updateCart(itemId, action) {
//     // ... your existing AJAX fetch logic here ...
    
//     // After a successful 'add' action:
//     if (action === 'add') {
//         toggleDrawer(true);
//     }
// }

function getCSRFCookie() {
        const name = "csrftoken"
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

async function renderDrawerItems(button) {
    const listContainer = document.getElementById('drawer-items-list');
    button.disabled = true

    toggleDrawer(true);
    
        try {
        response = await fetch(`/cart/cart-drawer/`)
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        if (data.success === true) {
            listContainer.innerHTML = data.html_drawer;
            document.getElementById('drawer-total').innerHTML = `₦${data.total}`;
        }
    } catch (error) {
        console.log("Error:". error)
        listContainer.innerHTML = `<div class="modal-box text-center">
                <p class="text-error font-bold">Failed to load content.</p>
                <p class="text-error font-bold">Please ensure you are connected to the internet.</p>
                <button class="btn btn-sm mt-4" onclick="toggleDrawer(false)">Close</button>
            </div>`
    } finally {
        button.disabled = false
    }
}

async function updateCart(itemId, action, button, itemName) {
    const buttonContainer = document.getElementById(`btn-container-${itemId}`)
    const qtySpan = document.getElementById(`qty-val-${itemId}`)
    const quantity = qtySpan ? Number(qtySpan.innerHTML) : 0
    let new_quantity = 0
    const csrftoken = getCSRFCookie()

    if (action === "increase") {
        new_quantity = quantity + 1
    }
    else if (action === "decrease") {
        new_quantity = quantity - 1
    }

    if (new_quantity > 0) {
        const buttonUpdate = `
            <div id="qty-ctrl-${itemId}" 
                class="flex items-center bg-primary text-soft-black h-12 transition-all duration-300">
                <button onclick="updateCart('${itemId}', 'decrease', this)" aria-label="Decrease quantity" class="px-3 h-full hover:bg-primary-dark active:bg-primary-dark transition-colors font-black text-lg">−</button>
                <span id="qty-val-${itemId}" class="px-2 font-black min-w-5 text-center">${ new_quantity }</span>
                <button onclick="updateCart('${itemId}', 'increase', this)" aria-label="Increase quantity" class="px-3 h-full hover:bg-primary-dark active:bg-primary-dark transition-colors font-black text-lg">+</button>
            </div>`
        buttonContainer.innerHTML = buttonUpdate
    } else {
        const buttonUpdate =` 
            <button  
                onclick="updateCart('${itemId}', 'increase', this)"
                aria-label="Add ${itemName} to cart"
                class="w-12 h-12 bg-charcoal text-white flex items-center justify-center hover:bg-primary hover:text-soft-black transition-all active:scale-95">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
                </svg>
            </button>`
        buttonContainer.innerHTML = buttonUpdate
    }

    buttonContainer.querySelectorAll("button").forEach(button => {button.disabled=true})

    try {
        response = await fetch(`/cart/add-to-cart/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({id:itemId, quantity:new_quantity})
        })
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        if (data.success === true) {
            const cart = document.getElementById("cart_item_number")

            
            cart.innerHTML = data.cart
        }
    } catch (error) {
        console.log("Error:". error)
        // revert back if there is an error
        if (quantity > 0) {
            const buttonUpdate = `
                <div id="qty-ctrl-${itemId}" 
                    class="flex items-center bg-primary text-soft-black h-12 transition-all duration-300">
                    <button onclick="updateCart('${itemId}', 'decrease', this)" aria-label="Decrease quantity" class="px-3 h-full hover:bg-primary-dark active:bg-primary-dark transition-colors font-black text-lg">−</button>
                    <span id="qty-val-${itemId}" class="px-2 font-black min-w-5 text-center">${ quantity }</span>
                    <button onclick="updateCart('${itemId}', 'increase', this)" aria-label="Increase quantity" class="px-3 h-full hover:bg-primary-dark active:bg-primary-dark transition-colors font-black text-lg">+</button>
                </div>`
            buttonContainer.innerHTML = buttonUpdate
        } else {
            const buttonUpdate =` 
                <button  
                    onclick="updateCart('${itemId}', 'increase', this)"
                    aria-label="Add ${itemName} to cart"
                    class="w-12 h-12 bg-charcoal text-white flex items-center justify-center hover:bg-primary hover:text-soft-black transition-all active:scale-95">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
                    </svg>
                </button>`
            buttonContainer.innerHTML = buttonUpdate
        }
    } finally {
        buttonContainer.querySelectorAll("button").forEach(button => {button.disabled=false})
    }

}

async function managePack(action, packId = null) {
    // Show a small loader in the drawer while processing
    const listContainer = document.getElementById('drawer-items-list');
    listContainer.style.opacity = '0.5';
    const csrftoken = getCSRFCookie()

    try {
        const response = await fetch(`/cart/manage-pack/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ action: action, pack_id: packId })
        });

        const data = await response.json();
        if (data.success) {
            // Update Drawer HTML
            listContainer.innerHTML = data.html_drawer;
            document.getElementById('drawer-total').innerHTML = `₦${data.total}`;
            
            // If we are on the menu page, we might need to refresh the menu cards 
            // because the 'active' pack has changed.
            if (data.reload) {
                // Logic to refresh all menu cards or just reload page if simpler
                location.reload(); 
            }
        }
    } catch (error) {
        console.error("Pack Management Error:", error);
    } finally {
        listContainer.style.opacity = '1';
    }
}