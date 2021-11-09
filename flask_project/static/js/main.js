// replace invalid image urls with placeholder
$("img").on("error", function() {
  $(this).attr("src", "/static/images/image_not_found.png");
});


// Script for adding product to cart, or immediate purchase
$("document").ready(function() {
  // add items to cart or buy them
  $('.product-buy-or-add-form').submit(function(ev) {
    ev.preventDefault();

    let form = $(this);
    let btn = $(ev.originalEvent.submitter)
    let action = btn.attr('id');
    let url = btn.attr('v-link');

    let data = new FormData(this);
    let json_data = Array.from(data).reduce((m, [k,v]) => { 
      m[k] = v; 
      return m; 
    }, {});

    switch (action) 
    {
    // Use vue store to dispatch cart item add
    case 'cart_add':
      let req = store.dispatch('add_item', {
        product_id: json_data.id, 
        quantity: json_data.quantity
      });

      // if adding item failed, then reload page
      // this is probably due to out of stock error
      req.then(res => {
        if (!res.ok) {
          location.reload();
        }
      })
      break;

    // Buying now lets the browser redirect us to stripe page
    case 'buy_now':
      $.redirect(url, json_data, "POST");
      break;
    }
  });
})