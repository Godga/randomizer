

// Вкладки
$('.tabs_caption li').on('click', function() {
  parentId = $(this).parent().parent().attr('id');
  $(this).addClass('active');
  $(this).siblings().removeClass('active');
  $( "#" + parentId + " .tabs_content").find("textarea").val("");
  $( "#" + parentId + " .tabs_content").find(":input:not([type=hidden])").val("");
  $( "#" + parentId + " .tabs_content").find("input").attr("required", false);
  $( "#" + parentId + " .tabs_content").removeClass('active').eq($(this).index()).addClass('active');
  $( "#" + parentId + " .tabs_content").eq($(this).index()).find(':input:not([type=hidden])').attr('required', true);
  $( "#" + parentId + " .tabs_content").find("textarea").attr('required', true);
  //$( "#" + parentId + " .tabs_content").find("input").attr("required", true);
  
});

/* Анимация ошибок и результатов */
$(function() {
  setTimeout(function() { 
    $(".error").fadeOut(1500); 
    $(".result").fadeOut(1500);
  }, 5000)
})

/* Удаление купонов */
$('.delete_ticket').on('click', function() {
  var url = $(this).parent().find('input').val()
  var tr = $(this).parent().parent();
  var url = $(location).attr('protocol') + "//" + $(location).attr('host') + url;
  $.ajax({
    type: "GET",
    contentType: "application/json",
    cache: false,
    url: url,
    dataType: "json",
    success: function(response) {
        $(tr).remove();
        console.log(response);             
    },
    error: function(jqXHR) {
        alert("error: " + jqXHR.status);
        console.log(jqXHR);
    }
  })
})
