$('document').ready(() => {
    let el_total_cost = $("#cart-summary-total-cost");
    let el_total_items = $("#cart-summary-total-items");
    let el_cart_count = $("#navbar-cart-count");

    // handle modal when confirming product deletion
    $("#cart-product-delete-modal").on('show.bs.modal', function (ev) {
        // we pass in a callback to continue form submission
        let button = $(ev.relatedTarget);
        let product_name = button.attr("data-bs-product-name");

        let description = $(this).find("#product-name");
        let confirm_btn = $(this).find("#delete-cart-product");

        description.html(product_name);
        confirm_btn.on("click", () => {
            // find form and edit value and submit
            let form = button.parents("#cart-controls:first").find("form");
            let quantity = form.find("input[name='quantity']");
            quantity.val(0)
            form.submit();
        });
    });
    
    // on quantity change, submit changes
    $('.quantity_form').find('input[id="quantity"]').change(function(ev) {
        let input = $(this);
        let form = input.parents('form:first');
        form.submit();
    });

    $('.quantity_form').submit(ev => {
        ev.preventDefault();
        let form = $(ev.currentTarget);
        let url = form.attr('action');
        let data = form.serializeArray();

        let quantity_field = form.find('input[id="quantity"]');

        // response from server is the correct quantity
        let update_quantity_from_res = (res) => {
            if (res.quantity === undefined) {
                return;
            } 

            // update the summary from the response
            if (res.summary !== undefined) {
                let total_cost = res.summary.total_cost;
                let total_items = res.summary.total_items;
                
                let cost_str = `${total_cost.toFixed(2)}`;
                const cost_parts = cost_str.split(".");
                let i = cost_parts[0];
                let d = cost_parts[1];

                el_total_cost.html(`$${i}.<small>${d}</small>`);
                el_total_items.html(`${total_items}`);
                el_cart_count.html(`${total_items}`);
            }

            let quantity = Number(res.quantity);
            if (!isFinite(quantity)) {
                return;
            }


            // if item was deleted, then remove entry
            if (quantity == 0) {
                let product_entry = form.parents(".cart-product:first");
                product_entry.remove();
            // update entry quantity
            } else {
                if (quantity.val != quantity) {
                    quantity_field.val(quantity);
                }
            }
        }
        
        $.ajax({
            url, data, type: 'POST',
            // success: data => update_quantity_from_res(data),
            success: xhr => location.reload(),
            error: xhr => location.reload(),
        });
    })
})