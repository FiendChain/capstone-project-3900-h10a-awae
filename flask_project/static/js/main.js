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
    let data = form.serializeArray();

    switch (action) 
    {
    case 'cart_add':
      $.ajax({
        url, data, type: 'POST',
        success: () => location.reload(),
        error: () => location.reload(),
      })
      break;

    // Buying now lets the browser redirect us to stripe page
    // For $.redirect, we need to flatten form data into a json
    case 'buy_now':
      let json = data.reduce((m, o) => {  
        m[o.name] = o.value; 
        return m;
      }, {});
      $.redirect(url, json, "POST")
      break;
    }
  });
})