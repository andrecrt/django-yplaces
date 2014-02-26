/*
 * Initialize Add Photo Modal.
 */
function initializePhotoModal() {

    // Listen to file selection.
    $('#addPhoto input').on('change', function() {
        var input = this;
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#addPhoto #preview').html('<img src="' + e.target.result + '" class="img-thumbnail">');
                $($('#addPhoto #preview').parent()).show();
            }
            reader.readAsDataURL(input.files[0]);
        }  
    });

    //Listen to click on upload button.
    $('#addPhoto #submit').on('click', function() {

        $(this).attr('disabled', true);
        
        // Build formdata.
        var formData = new FormData($('#addPhoto form').get(0));
        var file = $('#addPhoto input').get(0).files[0];
        formData.append('file', file);

        // Upload picture.
        $.ajax({
            url: photos_api_url,
            type: 'POST',
            data: formData,
            // Options to tell JQuery not to process data or worry about content-type.
            cache: false,
            contentType: false,
            processData: false,
            success: function(data) {
                alert(gettext('Picture uploaded'));
                $(this).attr('disabled', false);
                window.location = request_path;
            }.bind(this),
            error: function(err) {
                alert(gettext('Unable to upload picture'));
                $(this).attr('disabled', false);
            }.bind(this)
        });
    });
}