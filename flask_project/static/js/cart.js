$('document').ready(() => {
    let el_total_cost = $("#cart-summary-total-cost");
    let el_total_items = $("#cart-summary-total-items");
    let el_cart_count = $("#navbar-cart-count");

    // on quantity change, submit changes
    $('.quantity_form').find('input[id="quantity"]').change(ev => {
        let input = $(ev.currentTarget);
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

                el_total_cost.html(`${total_cost.toFixed(2)}`);
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
                console.log(product_entry);
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
            success: data => update_quantity_from_res(data),
            error: xhr => location.reload(),
        });
    })
})