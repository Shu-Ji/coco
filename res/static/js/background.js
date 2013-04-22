DEBUG = false;
DEBUG = true;


if(!DEBUG){
    window.console = {log: function(){}}
}


$(function(){
})


function playSound(snd_str){
    $('#' + snd_str + '-snd')[0].play()
}
