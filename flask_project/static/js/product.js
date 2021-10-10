$(($) => {
    $('.product_form').submit(e => {
        e.preventDefault();
        let form = $(e.currentTarget);
        
        let btn = $(e.originalEvent.submitter)
        let action = btn.attr('id');
        let url = btn.attr('href');
        let data = form.serializeArray();

        switch (action) 
        {
        case 'cart_add':
            $.ajax({
                url, data, type: 'POST',
                success: location.reload(),
                failure: location.reload(),
            })
            break;

        case 'buy_now':
            $.ajax({
                url, data, type: 'POST',
                success: location.reload(),
                failure: location.reload(),
            })
            break;
        }
    })
})