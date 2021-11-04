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
      redirect: 'follow',
      body: new URLSearchParams(data),
    });

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
      redirect: 'follow',
      body: new URLSearchParams(data),
    });

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
})

store.dispatch("get_cart");

// Jquery handles cart deletion modal
$('document').ready(() => {
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