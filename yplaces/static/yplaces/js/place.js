/*
 * Initialize Map.
 */
function initializeMap(){

    // Load the map with the restaurant's coordinates
    var latlng = new google.maps.LatLng(place.latitude, place.longitude);
    var myOptions = {
        zoom: 15,
        center: latlng,
        navigationControl: true,
        scrollwheel: false,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
    };
    var map = new google.maps.Map(document.getElementById('map'), myOptions);

    // Place a marker
    var marker = new google.maps.Marker({
        position: latlng,
        map: map,
        title: place.name
    });
}


/*
 * Initialize Review Modal.
 */
function initializeReviewModal() {

    // Clear form when modal is closed.
    $('#addReview').on('hidden.bs.modal', function(e) {
        $('#addReview .messages').html('');
        $('#addReview #rating').val('');
        $('#addReview #comment').val('');
        $('#addReview .star-rating-dynamic').find('span').each(function() { $(this).removeClass('star-rating-dynamic-active'); });
    });

    // Set number of stars.
    $('#addReview .star-rating-dynamic span').on('click', function() {
        $('#addReview #rating').val($(this).attr('value'));
    });

    // Hovering out, displays current selection.
    $('#addReview .star-rating-dynamic').mouseleave(function() {
        var stars = $('#addReview #rating').val();
        for(var i=0; i<stars; i++) {
            $($('#addReview .star-rating-dynamic').find('span')[4-i]).addClass('star-rating-dynamic-active');  
        }
    });

    // Hovering in, hides current selection.
    $('#addReview .star-rating-dynamic').mouseenter(function() {
        $('#addReview .star-rating-dynamic').find('span').each(function() { $(this).removeClass('star-rating-dynamic-active'); });
    });

    // Listen to submit.
    $('#addReview #submit').on('click', function() {

        $(this).attr('disabled', true);

        // Clear messages.
        $('#addReview .messages').html('');

        // Validate mandatory parameters.
        var rating = parseInt($('#addReview #rating').val()); 
        var comment = $('#addReview #comment').val();
        if(rating == '' || isNaN(rating) || comment == '') {
            var html = '<div class="alert alert-warning">';
            html += '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>';
            html += gettext('Please provide a rating and a comment');
            html += '</div>';
            $('#addReview .messages').prepend(html);
            $(this).attr('disabled', false);
            return;
        }

        // Review data.
        var data = {
            rating: rating,
            comment: comment
        }

        // Submit review.
        $.ajax({
            url: reviews_api_url,
            type: 'POST',
            data: JSON.stringify(data),
            dataType: 'JSON',
            success: function(data, status, xhr) {

                // Message.
                alert(gettext('Thank you for your review'));

                // Render comment.
                var html = '<li><div class="avatar">';
                html += '<img src="' + data.user.photo_url + '" class="img-rounded"></div>';
                html += '<div class="comment"><div class="star-rating-sm"><div style="width:' + (data.rating*100/5) + '%"></div></div>';
                html += '<div class="message">' + data.comment + '<br>';
                html += '<span>' + data.user.name + ' // ' + data.date + '</span></div></div>';
                html += '<div class="clear"></div></li>';
                $('.place .left-container .reviews ul').prepend(html);
                $('.place .left-container .reviews ul').show();

                // Update Place's average rating.
                var placeAverageRating = data.place.rating.average*100/5;
                $('.place .rating .star-rating div').css('width', placeAverageRating+'%');

                // Close modal.
                $('#addReview').modal('hide');

                // Re-enable submit button.
                $(this).attr('disabled', false);

            }.bind(this),
            error: function(xhr, status, err) {
                var html = '<div class="alert alert-danger">';
                html += '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>';
                html += gettext('Unable to add review');
                html += '</div>';
                $('#addReview .messages').prepend(html);
                $(this).attr('disabled', false);
            }.bind(this)
        });
    });
}