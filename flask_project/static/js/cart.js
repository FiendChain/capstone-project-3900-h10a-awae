/**
 * Javascript for cart api and Vue store
 * Javascript for handling buy-now and add-to-cart buttons 
 */

// Api for cart actions
const cart_api = {
  async fetch_cart() {
    let res = await fetch("/api_v1/cart");
    return res.json();
  },

  async add_product(id, quantity) {
    let data = new FormData();
    data.append('id', id);
    data.append('quantity', quantity);

    const res = await fetch("/api_v1/transaction/add", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams(data),
    });

    if (res.status === 302) {
      let data = await res.json();
      window.location.href = data.location;
    }

    return res;
  },
  
  async update_product(id, quantity) {
    let data = new FormData();
    data.append('id', id);
    data.append('quantity', quantity);

    const res = await fetch("/api_v1/transaction/update", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams(data),
    });

    if (res.status === 302) {
      let data = await res.json();
      window.location.href = data.location;
    }

    return res;
  },

  async delete_product(id) {
    return this.update_product(id, 0);
  }
}

// Vue store for cart
const store = Vuex.createStore({
  state: {
    cart_items: [],
  },
  actions: {
    async get_cart(context) {
      let data = await cart_api.fetch_cart();
      context.commit('set_products', data.cart_items);
    },
    async delete_item(context, product_id) {
      let res = await cart_api.delete_product(product_id);
      await context.dispatch('get_cart');
      return res;
    },
    async set_quantity(context, { product_id, quantity }) {
      let res = await cart_api.update_product(product_id, quantity);
      await context.dispatch('get_cart');
      return res;
    },
    async add_item(context, { product_id, quantity }) {
        let res = await cart_api.add_product(product_id, quantity);
        await context.dispatch('get_cart');
        return res;
    },
  },
  mutations: {
    set_products(state, cart_items) {
      state.cart_items = cart_items;
    }
  }
});
store.dispatch("get_cart");

// Jquery handles cart deletion modal
$('document').ready(() => {
  // update add to cart or buy now button quantity from form change
  $("[data-bs-action='product-form']").on("change", function(ev) {
    let quantity = ev.target.value;
    let target_id = $(this).attr("data-bs-product-form-target");
    let targets = $(`[data-bs-product-form-id='${target_id}']`);
    targets.attr('data-bs-quantity', quantity);
  });

  // add to cart button
  $("[data-bs-action='add-to-cart']").on('click', function(ev) {
    ev.preventDefault();
    let product_id = $(this).attr('data-bs-id');
    let quantity = $(this).attr('data-bs-quantity');

    let req = store.dispatch('add_item', {
      product_id: product_id, 
      quantity: quantity,
    });

    // if adding item failed, then reload page
    // this is probably due to out of stock error
    req.then(res => {
      if (res.status === 302) {
        res.json().then(data => {
          window.location.href = data.location;
        })
      } else if (!res.ok) {
        location.reload();
      }
    })
  });

  // buy now button
  $("[data-bs-action='buy-now']").on('click', function(ev) {
    ev.preventDefault();
    let product_id = $(this).attr('data-bs-id');
    let quantity = $(this).attr('data-bs-quantity');

    let data = new FormData();
    data.append("id", product_id);
    data.append("quantity", quantity);

    let req = fetch('/api_v1/transaction/buy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams(data),
    });
    
    req.then(res => {
      if (res.status === 302) {
        res.json().then(data => {
          window.location.href = data.location;
        })
      } else if (!res.ok) {
        location.reload();
      }
    });
  });

  // handle modal when confirming product deletion
  $("#cart-product-delete-modal").on('show.bs.modal', function (ev) {
      // we pass in a callback to continue form submission
      let button = $(ev.relatedTarget);
      let product_id = button.attr("data-bs-product-id");
      let product_name = button.attr("data-bs-product-name");

      let description = $(this).find("#product-name");
      let confirm_btn = $(this).find("#delete-cart-product");

      description.html(product_name);
      confirm_btn.on("click", () => {
          store.dispatch('delete_item', product_id);
      });
  });
});

// Render price tag in vue
const vue_price_item = {
  props: {
    'price': Number,
    'currency': { 
      type: String, 
      default: '$'
    }
  },
  computed: {
    price_parts() {
      return String(this.price.toFixed(2)).split('.');
    }
  },
  delimiters: ['[[', ']]'],
  template: `[[ currency ]][[ price_parts[0] ]].<small>[[ price_parts[1] ]]</small>`,
};