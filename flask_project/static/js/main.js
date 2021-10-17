// replace invalid image urls with placeholder
$("img").on("error", function() {
  $(this).attr("src", "/static/images/image_not_found.png");
});