// From: https://css-tricks.com/rethinking-dynamic-page-replacing-content/
// Modified by Chase
$(function() {
    if(Modernizr.history){

    var newHash      = "",
        $mainContent = $("#body"),
        baseHeight   = 0,
        $el;
    
    $("a").on("click", function() {
        _link = $(this).attr("href");
        history.pushState(null, null, _link);
        loadContent(_link);
        return false;
    });

    // Somehow we are also sending a second delete request to "/"
    // Not related to the argument to loadContent
    function deleteButton(url) {
      var xhr = new XMLHttpRequest();
      xhr.open("DELETE", url, true);
      xhr.onload = function (e) {
        // Redirect
        loadContent('/');
      };
      xhr.onerror = function (e) {
        console.error(xhr.statusText);
      };
      xhr.send(null);
    }

    $('button[data-method="delete"]').on('click', function () {
      deleteButton($(this).attr("data-link"));
    });

    $('form[remote="true"]').submit(function (form) {
      var toRedirect = $(this).attr("redirect");
      $.ajax({
          type: 'POST',
          url: $(this).attr("action"),
          data: $(this).serialize(),
          success: function() {
            loadContent(toRedirect)
          }
        });
      return false;
    });

    function loadContent(href){
        $mainContent
              .find("#inner-content")
              .fadeOut(200, function() {
                    $mainContent.hide().load(href, function() {
                        $mainContent.fadeIn(200);
                        console.log(href);
                    });
                });
    }
    
    $(window).bind('popstate', function(){
       _link = location.pathname.replace(/^.*[\\\/]/, ''); //get filename only
       loadContent(_link);
    });

} // otherwise, history is not supported, so nothing fancy here.

    
});