
$(document).ready(function() {
    $('.comment').submit(ajaxComment);
});

var ajaxComment = function(e) {
    e.preventDefault();

    var commentForm = $(this);
    console.log('[ajax for commentForm]' + commentForm.attr('method'));
    console.log('[ajax for commentForm]' + commentForm.attr('action'));

    $.ajax({
        type: commentForm.attr('method'),
        url: commentForm.attr('action'),
        data: commentForm.serialize(),
        dataType : "html",
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(errorThrown);
        },
        success: function(html) {
            console.log('[ajax for comment]')
            console.log(html);
            //#var commentList;
            //commentList = commentForm.siblings('.comments');
            $('#commentslist').append(html);
            
            commentForm.find('textarea').val("");

        }
    });
};
