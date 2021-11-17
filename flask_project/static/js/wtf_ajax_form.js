// A small jquery library for handling serialized wtform errors over ajax
// For a form marked as wtf-ajax-form, we dynamically add in bootstrap validation 
// For an input to display an error, it must have an associated .wtf-ajax-error with id='input.name'

// The expected wtform error response looks like
// responseJSON = {
//    'bad_field' : {name:'field.name', value: 'field.value', 'errors': ['An error', 'Another error']},
//    'good_field': {name:'field.name', value: 'field.value', 'errors': []},
// }
// status_code = 400 (Must be this to show errors on the form)
// If the status code is not 400, then we refresh the page

// On a successful form submission, wtform expects the following to redirect
// If the responseJSON doesn't have a redirect field, then we just reload the page
// status_code = 200
// responseJSON = {'redirect': 'url to redirect to'}

$("document").ready(function() {
  $("form.wtf-ajax-form").submit(function(ev) {
    ev.preventDefault();

    let form = $(this);
    let data = new FormData(this);
    let url = $(this).attr("action");
    let method = $(this).attr("method") || "POST";
    let enctype = $(this).attr("enctype") || "multipart/form";

    // if we recieved a wtform response
    function update_from_json(data) {
      for (let field of data) {
        let name = field.name;
        let value = field.value;
        let errors = field.errors;

        let el_sel = `[name='${name}']`;
        let el_input = form.find(el_sel);
        let el_error = form.find(`.wtf-ajax-error[id='${name}']`);

        // show validation errors
        if (errors && errors.length && errors.length > 0) {
          el_input.addClass("is-invalid");
          el_error.html(errors[0]);
          el_error.removeClass("d-none");
        // hide validation errors
        } else {
          el_input.removeClass("is-invalid");
          el_error.html("");
          el_error.addClass("d-none");
        }
      }
    }
    
    // if we successfully sent the form we can redirect or reload
    function on_success(data, textStatus, xhr) {
      if (xhr.status == 302) {
        window.location = data.location;
      } else {
        location.reload();
      }
    }

    // if we got an error, check to see if it is a form error
    function on_error(xhr, options, error) {
      if (xhr.status == 400) {
        update_from_json(xhr.responseJSON);
      } else if (xhr.status == 302) {
        window.location = xhr.responseJSON.location;
      } else {
        location.reload();
      }
    }

    // TODO: Allow for custom submit handlers
    $.ajax({
      url, data, type: method, enctype,
      cache: false,
      processData: false,
      contentType: false,
      success: on_success,
      error: on_error,
    });
  });
});