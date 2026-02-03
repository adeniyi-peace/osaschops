// Determine ws:// or wss:// based on current protocol
const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
const orderSocket = new WebSocket(
    ws_scheme + '://' + window.location.host + '/ws/orders/updates/'
);

orderSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const order = data.data;

    // A. Play Sound
    const audio = document.getElementById("notificationSound");
    audio.play().catch(error => console.log("Audio play blocked by browser policy"));

    // B. Show Red Dot
    document.getElementById("nav-red-dot").classList.remove("hidden");

    // C. Add to Dropdown List
    const list = document.getElementById("notification-list");
    // Clear "No new orders" if it exists
    if(list.innerText.includes("No new orders")) list.innerHTML = "";
    
    const newItem = document.createElement("li");
    newItem.innerHTML = `
        <a href="${order.url}" class="flex flex-col items-start gap-1 bg-primary/10 rounded-lg mb-2">
            <span class="font-black text-xs uppercase text-primary">New Order #${order.id}</span>
            <span class="text-xs font-bold">${order.name} - ₦${order.total}</span>
        </a>
    `;
    list.prepend(newItem);

    // D. Show a Toast (Popup)
    showToast(order);

    // E. (Optional) If we are on the Orders Table page, reload the table
    if (typeof refreshOrderTable === "function") {
        refreshOrderTable(order);
    }
};

function showToast(order) {
    // Create a temporary visual popup
    const toast = document.createElement("div");
    toast.className = "fixed bottom-5 right-5 bg-charcoal text-white p-4 rounded-2xl shadow-heavy z-50 animate-bounce cursor-pointer";
    toast.innerHTML = `
        <div class="flex items-center gap-3">
            <span class="text-2xl">🔥</span>
            <div>
                <p class="text-[10px] font-bold uppercase tracking-widest text-primary">New Order Received</p>
                <p class="font-bold">#${order.id} | ₦${order.total}</p>
            </div>
        </div>
    `;
    document.body.appendChild(toast);
    
    // Remove after 5 seconds
    setTimeout(() => { toast.remove(); }, 5000);
}

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

function stopNotificationPulse(){
    const pulse = document.getElementById("nav-red-dot")
    if (!pulse.classList.contains("hidden")) {
        pulse.classList.add("hidden");
    }
}