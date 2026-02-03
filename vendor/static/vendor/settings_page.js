function toggleTimeInputs(checkbox) {
    // Find the row container
    const row = checkbox.closest('.grid');
    const timeInputs = row.querySelectorAll('.time-input');
    const statusLabel = row.querySelector('.status-label');
    const closedMessage = row.querySelector('.closed');
    
    if (checkbox.checked) {
        // Enable inputs
        timeInputs.forEach(input => {
            input.closest("div").classList.remove('hidden');
        });
        closedMessage.classList.add("hidden")
        statusLabel.innerText = 'Open';
        statusLabel.classList.add('text-primary');
        statusLabel.classList.remove('text-gray-400');
    } else {
        // Disable inputs
        timeInputs.forEach(input => {
            input.closest("div").classList.add('hidden');
        });
        closedMessage.classList.remove("hidden")
        statusLabel.innerText = 'Closed';
        statusLabel.classList.remove('text-primary');
        statusLabel.classList.add('text-gray-400');
    }

}

const delivery_zone_formset_total_input = document.getElementById("id_delivery_zone-TOTAL_FORMS");
const formset_container = document.getElementById('formset_container');

function addLineItem() {
    const empty_form = document.querySelector(".empty-form").cloneNode(true);
    // Find the current form index
    let currentFormCount = parseInt(delivery_zone_formset_total_input.value);

    // 1. Check for duplicates among forms NOT marked for deletion
    const existingLines = formset_container.querySelectorAll('.selected-line-item');

    // Set the item details and item-specific attributes
    empty_form.id = empty_form.id.replace(/__prefix__/g, `${currentFormCount}`);
    empty_form.innerHTML = empty_form.innerHTML.replace(/__prefix__/g, `${currentFormCount}`)
    empty_form.classList.remove("hidden")
    empty_form.classList.remove("empty-form")
    empty_form.classList.add("grid")
    

    // 3. Append to container and update TOTAL_FORMS
    formset_container.append(empty_form);
    delivery_zone_formset_total_input.value = currentFormCount + 1;

    updateManagementForm();
}

function deleteLineItem(formPrefix) {
    const formElement = document.getElementById(formPrefix);
    if (!formElement) return;

    // Check if the form has an ID field (meaning it's an existing saved line)
    const idInput = formElement.querySelector('input[id$="-id"]');
    
    if (idInput && idInput.value) {
        // Existing item: Mark for deletion by checking the DELETE checkbox and hiding the element
        const deleteCheckbox = formElement.querySelector('input[id$="-DELETE"]');
        if (deleteCheckbox) {
            deleteCheckbox.checked = true;
            formElement.style.display = 'none';
        }
    } else {
        // New item (no ID): Simply remove from the DOM
        formElement.remove();
    }

    updateManagementForm();
}

function updateManagementForm() {
    const lineItems = formset_container.querySelectorAll('.selected-line-item');
    let formCount = 0;
    
    lineItems.forEach(line => {
        // Only count forms that are NOT marked for deletion (not hidden and doesn't contain a checked DELETE box)
        const deleteCheckbox = line.querySelector('input[type="checkbox"][id$="-DELETE"]');
        if (line.style.display !== 'none' && (!deleteCheckbox || !deleteCheckbox.checked)) {
            formCount++;
        }
    });
    
    // This is the true number of forms that will be submitted
    delivery_zone_formset_total_input.value = formCount; 

}

// Run on page load to set initial states
document.querySelectorAll('.day-toggle').forEach(toggle => toggleTimeInputs(toggle));
