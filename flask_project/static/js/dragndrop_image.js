$("document").ready(() => {
    $(".dragndrop-image").each(function() {
        let e = $(this);

        let dropzone = e.find(".dropzone").first();
        let reset_btn = dropzone.find("[id='reset']");

        let preview = e.find(".preview").first();
        let preview_image = preview.find("img");
        let name_field = preview.find(".filename");
        let delete_btn = preview.find("[id='delete']");


        let default_url = dropzone.find("input.dropzone-src-url").val();
        let image_changed = dropzone.find("input.dropzone-dirty");

        function show_image(src, filename) {
            console.log("Updating image with: ", filename);
            preview_image.attr("src", src);
            name_field.html(filename);
            dropzone.addClass("d-none");
            preview.removeClass("d-none");

            image_changed.val(true);
        }

        function remove_image() {
            preview_image.attr("src", "");
            name_field.html("");
            preview.addClass("d-none");
            dropzone.removeClass("d-none");

            image_changed.val(true);
        }

        function on_file_load(file) {
            var reader = new FileReader();
            reader.onload = e => {
                let src = e.target.result;
                show_image(src, file.name);
            };
            reader.readAsDataURL(file);
        }

        function reset_image() {
            if (default_url) {
                show_image(default_url, '');
                image_changed.val(false);
            }
        }

        // remove the image
        delete_btn.click(function () {
            remove_image();
        });

        // reset the image to its source
        reset_btn.click(function() {
            reset_image();
        });

        // on image drag and drop, update the preview
        e.find("input.dropzone-input").first().change(function() {
            let input = $(this)[0];
            let file = input.files && input.files[0];
            if (file) {
                on_file_load(file);
            }
        });

        // if the src url was provided display it
        if (default_url) {
            dropzone.find('.overlay').removeClass('d-none');
            reset_image();
        }
    });
})