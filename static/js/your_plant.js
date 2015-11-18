function set_popover(states, elem_id) {
  $('#' + elem_id).popover();
  $('#' + elem_id).on('show.bs.popover', function() {
    states[elem_id] = true;
  });
  $('#' + elem_id).on('hide.bs.popover', function() {
    states[elem_id] = false;
  });
  if (states[elem_id]) {
    $('#' + elem_id).popover("show");
  }
}

$(function() {
  var states = {"Humidity" : false, "pH" : false}
  $(".dial").knob();
  set_popover(states, "Humidity");
  set_popover(states, "pH");
  namespace = "";
  var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
  socket.on("new-data", function(stat) {
    $("#vitals").html(stat["new-page"]);
    set_popover(states, "Humidity");
    set_popover(states, "pH");
  });
});
