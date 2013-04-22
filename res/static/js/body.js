DEBUG = false;
DEBUG = true;


if(!DEBUG){
    window.console = {log: function(){}}
}


$(function(){
    var $document = $(document)
    var $html = $('html, body').animate({scrollTop: $document.height()}, 0)
    var $content = $('#content')
    var $editor = $('#editor').focus()

    $('#gotop, #gotop_i').click(function(){
        $html.animate({
            scrollTop: $document.scrollTop() < 5 ? $document.height() : 0
        })
    })
})
