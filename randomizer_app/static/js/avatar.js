$( document ).ready(function() {
    var canvas = document.getElementById('jdenticon');
    var dataURL = canvas.toDataURL();
    $.ajax({
        type: "POST",
        url: $(location).attr('protocol') + "//" + $(location).attr('host') + "/avatar/godjan",
        data: {
           img_string: dataURL
        },
        dataType: "json",
        success: function(response) {
            window.location.href = $(location).attr('protocol') + "//" + $(location).attr('host') + "/admin";            
        },
        error: function(jqXHR) {
            console.log("error: " + jqXHR.status);
        }
      }).done(function(o) {
        console.log('done'); 
        // If you want the file to be visible in the browser 
        // - please modify the callback in javascript. All you
        // need is to return the url to the file, you just saved 
        // and than put the image in your browser.
      });
})