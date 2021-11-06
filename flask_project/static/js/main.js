// replace invalid image urls with placeholder
$("img").on("error", function() {
  $(this).attr("src", "/static/images/image_not_found.png");
});

// reload window on form submission if we get a particular status code
$("document").ready(function() {
  $("[data-bs-form-reload]").submit(function(ev) {
    ev.preventDefault();

    let status_code = $(this).attr("data-bs-form-reload");
    let data = new FormData(this);

    let url = $(this).attr("action");
    let method = $(this).attr("method");

    console.log({url, method, data, status_code});

    let req = fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      redirect: 'manual',
      body: new URLSearchParams(data),
    });

    req
      .then(res => {
        if (res.redirected) {
          window.location.href = res.url;
          return Promise.reject();
        } else if (res.status == status_code) {
          location.reload();
          return Promise.reject();
        } else {
          return res.text();
        }
      })
      .then(text => {
        document.write(text);
      })
  });

})