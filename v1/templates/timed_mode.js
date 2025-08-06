// static/timed_mode.js
document.addEventListener('DOMContentLoaded', function() {
    var remaining = parseInt(document.getElementById('countdown').innerText);
    var timer = setInterval(function(){
        remaining -= 1;
        document.getElementById('countdown').innerText = remaining + "秒";
        if(remaining <= 0){
            clearInterval(timer);
            document.getElementById('examForm').submit();
        }
    }, 1000);
});
