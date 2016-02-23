
var width = 600,
    height = 400;

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height)
  .append("g")
    .attr("transform", "translate(32," + (height / 2) + ")");

function update(data) {

  // DATA JOIN
  // Join new data with old elements, if any.
  var t = svg.selectAll("text")
      .data(data);

  // UPDATE
  // Update old elements as needed.
  t.attr("class", "update");

  // ENTER
  // Create new elements as needed.
  t.enter().append("text")
      .attr("class", "enter")
      .attr("x", function(d, i) { return i * 64; })
      .attr("dy", ".35em");

  // ENTER + UPDATE
  // Appending to the enter selection expands the update selection to include
  // entering elements; so, operations on the update selection after appending to
  // the enter selection will apply to both entering and updating nodes.
  t.text(function(d) { return d; });

  // EXIT
  // Remove old elements as needed.
  t.exit().remove();
}

// Grab json from the flask-powered RESTful api
function RetriveData() {
  d3.json("http://127.0.0.1:5656/api/1", function(err, response) {
    console.log(response);
    update(response['packet_queue_size']);
  });
}

// The initial display.
update([1]);


setInterval(function() {
  RetriveData();
}, 1000);

