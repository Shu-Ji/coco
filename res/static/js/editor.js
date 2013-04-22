DEBUG = false;
DEBUG = true;


if(!DEBUG){
    window.console = {log: function(){}}
}


$(function(){
    var $editor = $('#editor').focus()
    // ctrl/shift+enter发送
    $editor.keydown(function(e){
        if((e.shiftKey || e.ctrlKey) && e.keyCode == 13){
            // 通知主窗口的槽
            mainwindow.webkit_enter_key_pressed()
            $editor.html('')
            return false
        }
    })
})


function formatMsg(){
    function _formatMsg(ele){
        var msg = ele.childNodes
        if(!msg){
            return
        }
        var result = ''
        for(var i = 0; i < msg.length; i++){
            if(msg[i].nodeType == 3){
                if(msg[i].nodeValue == '==allfaces=='){
                    result += sendAllFaces()
                    continue
                }
                result += '"' + msg[i].nodeValue + '",'
            }
            else if(msg[i].nodeName == 'IMG'){
                if(msg[i].getAttribute('imgtype') == 'offpic'){
                    result += '["offpic","' + msg[i].getAttribute('filepath') + '","' + msg[i].getAttribute('filename') + '",' + msg[i].getAttribute('filesize') + '],'
                }
                else{
                    result += '["face",' + msg[i].getAttribute('face') + '],'
                }
            }
            else{
                if(msg[i].nodeName == 'DIV'){
                    result += '"\\n",'
                }
                result += _formatMsg(msg[i])
            }
        }
        return result
    }
    return _formatMsg(document.getElementById('editor'))
}


function sendAllFaces(){
    var msg = ''
    for(var i = 0; i < 134; i++){
        msg += '[\\"face\\", ' + i + '],'
    }
    return msg
}
