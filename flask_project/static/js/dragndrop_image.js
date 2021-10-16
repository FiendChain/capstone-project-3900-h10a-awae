// A jquery library for an image drag and drop field

// Minimum expected html layout
// <div class="dragndrop-image">
//   <!--Image preview-->
//   <div class="preview">
//     <!--Overlay to show edit buttons-->
//     <div class="overlay">
//        <div id="delete">Delete</div>
//     </div>
//     <img src="" default-src="{{ insert your default url }}"/>
//     <p class="filename"></p>
//   </div>
//
//   <!--Image drop zone-->
//   <div class="dropzone">
//     <!--Reset to original source if provided-->
//     <div class="overlay">
//       <div id="reset">Reset</div>
//     </div>
//     <div class="dropzone-description"></div>
//     <!--If there was an original src image, store its url here-->
//     <input type="checkbox" checked=false class="dropzone-dirty" required hidden>
//     <!--Input that actually handles the drag and drop-->
//     <input type="file" accept="image/*" class="dropzone-input">
//   </div>
// </div>


$("document").ready(() => {
    $(".dragndrop-image").each(function() {
        let e = $(this);

        let dropzone = e.find(".dropzone").first();
        let preview = e.find(".preview").first();

        // controls
        let reset_btn = dropzone.find("[id='reset']");
        let delete_btn = preview.find("[id='delete']");

        // preview
        let preview_image = preview.find("img");
        let name_field = preview.find(".filename");

        // image data elements 
        // includes upload image file, url to default image
        let el_default_url = preview.find("img");
        let image_changed = dropzone.find("input.dropzone-dirty");

        function get_default_url() {
            return el_default_url.attr('default-src');
        }

        console.log(el_default_url);

        // hide the drop zone and show the preview
        function show_image(src, filename) {
            preview_image.attr("src", src);
            name_field.html(filename);
            dropzone.addClass("d-none");
            preview.removeClass("d-none");

            image_changed.val(true);
        }

        // hide the preview, and show the drop zone
        function remove_image() {
            preview_image.attr("src", "");
            name_field.html("");
            preview.addClass("d-none");
            dropzone.removeClass("d-none");

            image_changed.val(true);
        }

        // handle loading a file from input
        function on_file_load(file) {
            var reader = new FileReader();
            reader.onload = e => {
                let src = e.target.result;
                show_image(src, file.name);
            };
            reader.readAsDataURL(file);
        }

        // if there was a default source image, reset to that
        // otherwise, just show the dropzone
        function reset_image() {
            let default_url = get_default_url();
            if (default_url) {
                show_image(default_url, '');
                image_changed.val(false);
            } else {
                remove_image();
            }
        }

        // bind button controls
        delete_btn.click(function () {
            remove_image();
        });

        reset_btn.click(function() {
            reset_image();
        });

        // on image drag and drop, update the preview
        e.find("input.dropzone-input").first().change(function() {
            let input = $(this)[0];
            let file = input.files && input.files[0];
            if (file) {
                on_file_load(file);
            } else {
                remove_image();
            }
        });

        // if the src url was provided display it
        if (get_default_url()) {
            dropzone.find('.overlay').removeClass('d-none');
            reset_image();
        }
    });
})