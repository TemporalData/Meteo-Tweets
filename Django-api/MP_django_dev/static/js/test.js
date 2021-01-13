function update_timeline(){
    // var startDate = document.getElementById("start").value;
    // var endDate = document.getElementById("end").value;

    // pass dates to views.py to process data; 
    // acquire new data results and generate graphs in template
  
    // document.getElementById("timeperiod").innerHTML = 'From '+String(startDate)+' to '+String(endDate);
  
    $.ajax({
      url: 'http://127.0.0.1:8000/api/timeline/',
      type: "GET",
      contentType: "application/json; charset=utf-8",
      dataType: 'json',
      data: {
        id_filter: "",
        start:"2015-1-1",
        end:"2015-1-2",
      },
      success: function (result) {
        console.log(result);
        
        // draw_timeline(result)
      }
    })
  
  }

  function draw_timeline(dateDensities){

    $("#timeline").empty()

  // set the dimensions and margins of the graph
  var margin = {top: 10, right: 30, bottom: 30, left: 60},
  width = 460 - margin.left - margin.right,
  height = 400 - margin.top - margin.bottom;

  
  // Set the ranges
  var x = d3.time.scale().range([0, width]);
  var y = d3.scale.linear().range([height, 0]);

  // Define the axes
  var xAxis = d3.svg.axis().scale(x)
      .orient("bottom").ticks(5);

  var yAxis = d3.svg.axis().scale(y)
      .orient("left").ticks(5);

  // append the svg object to the body of the page
  var svg = d3.select("#timeline")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform",
        "translate(" + margin.left + "," + margin.top + ")");

        var line = d3.line()
        .x(function(d) { return x(d.date)})
        .y(function(d) { return y(d.value)})
        x.domain(d3.extent(data, function(d) { return d.date }));   y.domain(d3.extent(data, function(d) { return d.value }));
  }