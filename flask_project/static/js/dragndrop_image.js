$("document").ready(() => {
    $(".dragndrop-image").each(function() {
        let e = $(this);

        let dropzone = e.find(".dropzone").first();

        let preview = e.find(".preview").first();
        let preview_image = preview.find("img");
        let name_field = preview.find(".filename");
        let delete_btn = preview.find("[id='delete']");

        function show_image(src, filename) {
            preview_image.attr("src", src);
            name_field.html(filename);
            dropzone.addClass("d-none");
            preview.removeClass("d-none");
        }

        function remove_image() {
            preview_image.attr("src", "");
            name_field.html("");
            preview.addClass("d-none");
            dropzone.removeClass("d-none");
        }

        function on_file_load(file) {
            var reader = new FileReader();
            reader.onload = e => {
                let src = e.target.result;
                show_image(src, file.name);
            };
            reader.readAsDataURL(file);
        }

        delete_btn.click(function () {
            remove_image();
        });

        e.find("input").first().change(function() {
            let input = $(this)[0];
            let file = input.files && input.files[0];
            if (file) {
                on_file_load(file);
            }
        })
    });
})