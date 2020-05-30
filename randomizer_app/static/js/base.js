
//Время сервера
var xmlHttp;
function srvTime(){
    try {
        xmlHttp = new XMLHttpRequest();
    }
    catch (err1) {
        try {
            xmlHttp = new ActiveXObject('Msxml2.XMLHTTP');
        }
        catch (err2) {
            try {
                xmlHttp = new ActiveXObject('Microsoft.XMLHTTP');
            }
            catch (eerr3) {
                alert("Устаревший браузер");
            }
        }
    }
    xmlHttp.open('HEAD',window.location.href.toString(),false);
    xmlHttp.setRequestHeader("Content-Type", "text/html");
    xmlHttp.send('');
    return xmlHttp.getResponseHeader("Date");
}


$( document ).ready(function() {
    
    // Таймер
    if ($("#nearest_raffle").val() != "none") {
        var countDownDate = new Date($("#nearest_raffle").val()).getTime();
        var st = srvTime();
        var date = new Date(st);
        var x = setInterval(function() {
            var now = date.getTime()
            var distance = countDownDate - now;
            var days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            if (distance < 0) {
                $("#navbar_time").text("Розыгрыш в процессе  " + "Время сервера: " + (date.getHours()<10?'0':'') + date.getHours() + ":"
                + (date.getMinutes()<10?'0':'') + date.getMinutes() + ":" + (date.getSeconds()<10?'0':'') + date.getSeconds());
            }
            else{
                $("#navbar_time").html("До следующего розыгрыша: " + days + "d " + hours + "h "
                + minutes + "m " + seconds + "s    " + "Время сервера: " + (date.getHours()<10?'0':'') + date.getHours() + ":"
                + (date.getMinutes()<10?'0':'') + date.getMinutes() + ":" + (date.getSeconds()<10?'0':'') + date.getSeconds());
            }   
            date.setSeconds(date.getSeconds() + 1);
        }, 1000);
    }
    else {
        var st = srvTime();
        var date = new Date(st);
        var x = setInterval(function() {
            $("#navbar_time").text("Розыгрышей нет  " + "Время сервера: " + (date.getHours()<10?'0':'') + date.getHours() + ":"
            + (date.getMinutes()<10?'0':'') + date.getMinutes() + ":" + (date.getSeconds()<10?'0':'') + date.getSeconds());
            date.setSeconds(date.getSeconds() + 1);
        }, 1000);
    }

    // Анимация загрузки
    $(".loader").css("display", "none");
    $("#sending_form").submit(function( event ) {
        $(".loader").css("display", "block");
      });
    // Открытие и закрытие бокового меню
    $("#show_menu").click(function() {
        $("#main_menu").addClass("show");
        $(".navbar_title").css({"display": "none"});
        $(".backdrop").css({"left": "0", "opacity": "1"});
      });
    $(document).on("click", function(event){
        if(!$(event.target).closest("#show_menu").length && !$(event.target).closest("#main_menu").length){
            $("#main_menu").removeClass("show");
            $(".navbar_title").css({"display": "block"});
            $(".backdrop").css({"left": "-100%", "opacity": "0"});
        }
    });
});

