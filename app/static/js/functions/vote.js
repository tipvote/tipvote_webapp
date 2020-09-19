$(document).on('click', '#click-btn', function(event) {
    $.ajax({
        url : '/vote/upvote_post',
        type : "post",
        contentType: 'application/json;charset=UTF-8',
        dataType: "json",
        data : JSON.stringify({'postid' : $('#click-btn').data('postid')}),
        success : function(response) {
            console.log(response);  
        },
        error : function(xhr) {
            console.log(xhr);
        }
    });
    event.preventDefault();
});