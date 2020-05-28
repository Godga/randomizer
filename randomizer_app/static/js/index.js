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

// Таймер
$( document ).ready(function() {
    if ($("#raffle_date").val() != "none") {
        var countDownDate = new Date($("#raffle_date").val()).getTime();
        //console.log($("#raffle_date").val())
        var st = srvTime();
        var date = new Date(st);
        //console.log(date)
        var x = setInterval(function() {
            var now = date.getTime()
            var distance = countDownDate - now;
            var days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            $("#timer").html(days + "d " + hours + "h "
            + minutes + "m " + seconds + "s ");
            date.setSeconds(date.getSeconds() + 1);
            if (distance < 0) {
                clearInterval(x);
                $("#timer").text("Обновите страницу");
                $("#timer").on('click', function(){
                    location.reload();
                })
            }   
        }, 1000);
    }
    else {
        $("#timer").text("Нет запланированных розыгрышей");
    }

    jQuery.easing['easeOutCirc'] = function (x, t, b, c, d) {
        return c * Math.sqrt(1 - (t=t/d-1)*t) + b;
    }
    
    members = $("#boxes li").length/5;

    $(function() {
        var option = {
            speed: 2,
            duration: 8,
            stopImageNumber: members*3+parseInt($("#winner_id").val())-2,
            elementSize: 160
        };
        
        $("#go").click(function() {
            $("#go").remove();
            $("#timer").show();
            $("#boxes li").removeClass("tape_center");
            //$("#config").text(JSON.stringify(option));
            $("#boxes").animate({
                //left: 1 * option.speed + 160 * (option.stopImageNumber)
                right: 160 * (option.stopImageNumber)
            }, 
            {
                duration: option.duration * 1000,
                easing: "easeOutCirc",
                step: function(a) {
                    //$("#boxes").css("transform", "translateX(-" + a % 160 + "px)");
                },
                complete: function() {
                    $("#boxes li:not(:nth-child("+String(option.stopImageNumber+3)+"))").addClass("tape_center");
                    $("#timer").fadeTo(1000, 1);
                    $(".result").fadeTo(1000, 1);
                }
            });
        })
        });
});