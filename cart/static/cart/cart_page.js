async function updateCartPage(itemId, action, packID, button) {
    const qtySpan = document.getElementById(`cart-qty-${packID}-${itemId}`)
    const quantity = qtySpan ? Number(qtySpan.innerHTML) : 0
    button.disabled = true
    let new_quantity = 0
    const csrftoken = getCSRFCookie()

    if (action === "increase") {
        new_quantity = quantity + 1
    }
    else if (action === "decrease") {
        new_quantity = quantity - 1
    }

    else if (action === "remove") {
        new_quantity = 0
    }

    try {
        response = await fetch("", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({id:itemId, quantity:new_quantity, pack_id: packID})
        })
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        if (data.success === true) {
            const menu_list = document.getElementById('cart-wrapper')
            const cart = document.getElementById("cart_item_number")
            const grandTotal = document.getElementById('grand-total');
            grandTotal.innerHTML = `₦${data.total.toLocaleString()}`;
            menu_list.innerHTML = data.html
            cart.innerHTML = data.cart
        }
    } catch (error) {
        console.log("Error:", error)
    } finally {
        button.disabled = false
    }

}