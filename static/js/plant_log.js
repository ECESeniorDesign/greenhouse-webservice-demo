var ctx = $("#plant_ideal").get(0).getContext("2d");
// Why does this feel like a hack?
var slot_id = $("#slot_id").get(0).getAttribute("slot_id");
namespace = "/plants"
plant_namespace = "/plants/" + slot_id;
var plant_socket = io.connect('http://' + document.domain + ':' + location.port + plant_namespace);
var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
var myNewChart = null;
plant_socket.on("chart-data", function(stat) {
  var data = stat["chart-content"];
  if (myNewChart) {
    myNewChart.destroy()
  }
  myNewChart = new Chart(ctx).Pie(data, {animateRotate : false});
});
socket.on("data-update", function (msg) {
  socket.emit("request-chart", slot_id);
});
// Send the initial request for chart data
socket.emit("request-chart", slot_id);
