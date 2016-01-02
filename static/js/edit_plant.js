$(function() {
  var t = document.getElementById('deletePlant');
    t.addEventListener('click', function () {
    deletePlant(t.dataset.link);
  });
  function deletePlant(url) {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", url, true);
    xhr.onload = function (e) {
      // Redirect
      window.location.replace('/');
    };
    xhr.onerror = function (e) {
      console.error(xhr.statusText);
    };
    xhr.send(null);
  }
});