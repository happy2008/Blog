var t = new Date();
window.setInterval(function () {
    var pre = t; 
    var data = {}
    t = new Date();

    console.log('test>>>')
    console.log(t.getTime());
    console.log(pre.getTime());
    console.log('test<<<')
    data.currenttime = pre.getTime();
    $.ajax({
        type: 'GET',
        url: "/ajax_update",
        data : data,
        dataType : "html",
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(errorThrown);
        },
        success: function(html) {
            $('.panel-body').prepend(html);
            //$('.comment').submit(ajaxComment);
        }
    });
}, 5000);
