/* Анимация загрузки */
$( document ).ready(function() {
    $(".loader").css("display", "none");
    $(".form-container").submit(function( event ) {
        $(".loader").css("display", "block");
      });
});

/* Анимация ошибок и результатов */
$(function() {
  setTimeout(function() { 
    $(".error").fadeOut(1500); 
    $(".result").fadeOut(1500);
  }, 5000)
})
