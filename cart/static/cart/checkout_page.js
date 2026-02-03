// To future code reviewers
// this function wil be added to select input attributes in cart/forms.py
function handleDeliveryZoneChange(selectElement) {
    const cartDisplay = document.getElementById("cart-total")
    const deliveryDisplay = document.getElementById("delivery-fee")
    const totalDisplay = document.getElementById("total-cost")
    
    const selectedIndex = selectElement.selectedIndex
    const selectedOption = selectElement.options[selectedIndex]
    const selectedLabel = selectedOption.text
    const zone = selectedLabel
    const match = zone.match(/₦(\d+)/)
    const price = match ? Number(match[1]) : null
    console.log(match, price)

    if (price){
        deliveryDisplay.innerHTML = price
        totalDisplay.innerHTML = Number(cartDisplay.innerHTML) + price
    }
    else {
        deliveryDisplay.innerHTML = 0
        totalDisplay.innerHTML = cartDisplay.innerHTML
    }
}