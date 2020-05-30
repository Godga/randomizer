$( document ).ready(function() {
    $(".loader").css("display", "none");
    $(".form-container").submit(function( event ) {
        $(".loader").css("display", "block");
      });
});


