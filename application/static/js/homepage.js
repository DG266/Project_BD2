$(document).ready(function(){

    function like(event) {
        event.preventDefault();

        var form = $(this).closest(".like-form");
        var likeContainer = form.parent();

        var postId = $(this).siblings("input[name=id]").val();

        var counter = $("#like-counter-" + postId);

        $.ajax({
            type: "POST",
            url: "/" + postId + "/like",
            async: true,
            success: function(){
                // Increment like counter in the page
                var count = counter.text().replace(/[^0-9]/g, '');
                count = parseInt(count) + 1;
                counter.text("Likes: " + parseInt(count));

                // Remove old "like" form, add a new "unlike" form
                form.remove();

                unlikeUrl = "/" + postId + "/unlike"

                unlikeForm = $("<form action=\"" + unlikeUrl + "\" method=\"post\" class=\"unlike-form\"></form>");
                unlikeForm.append("<input type=\"hidden\" name=\"id\" value =\"" + postId +"\">");
                unlikeButton = $("<button class=\"btn btn-primary unlike-button\" type=\"submit\">Unlike</button>");
                unlikeButton.click(unlike);
                unlikeForm.append(unlikeButton);

                likeContainer.append(unlikeForm);
            },
            error: function(jqXHR, errorType, exception) {
                console.log("ERROR");
            }
        })
    }

    // AJAX like button
    $(".like-button").click(like);




    function unlike(event) {
        event.preventDefault();

        var form = $(this).closest(".unlike-form");
        var likeContainer = form.parent();

        var postId = $(this).siblings("input[name=id]").val();

        var counter = $("#like-counter-" + postId);

        $.ajax({
            type: "POST",
            url: "/" + postId + "/unlike",
            async: true,
            success: function(){
                // Decrement like counter in the page
                var count = counter.text().replace(/[^0-9]/g, '');
                count = parseInt(count) - 1;
                counter.text("Likes: " + parseInt(count));

                // Remove old "unlike" form, add a new "like" form
                form.remove();

                likeUrl = "/" + postId + "/like"

                likeForm = $("<form action=\"" + likeUrl + "\" method=\"post\" class=\"like-form\"></form>");
                likeForm.append("<input type=\"hidden\" name=\"id\" value =\"" + postId +"\">");
                likeButton = $("<button class=\"btn btn-primary like-button\" type=\"submit\">Like</button>");
                likeButton.click(like);
                likeForm.append(likeButton);

                likeContainer.append(likeForm);
            },
            error: function(jqXHR, errorType, exception) {
                console.log("ERROR");
            }
        })
    }

    // AJAX unlike button
    $(".unlike-button").click(unlike);

})