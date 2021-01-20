$(start).datepicker('setStartDate', '01-01-2015');
$(start).datepicker('setEndDate', '06-09-2018');
$(end).datepicker('setStartDate', '01-01-2015');
$(end).datepicker('setEndDate', '06-09-2018');

var svg_t = d3.select("#timeline")
			.append("svg")
			.attr("width", 960)
            .attr("height", 500),

    // define top focus size parameters
    margin_t = {top: 20, right: 20, bottom: 110, left: 40},
    // define bottom context size parameters
    margin2_t = {top: 430, right: 20, bottom: 30, left: 40}, 
    width_t = +svg_t.attr("width") - margin_t.left - margin_t.right,
    height_t = +svg_t.attr("height") - margin_t.top - margin_t.bottom,
    height2_t = +svg_t.attr("height") - margin2_t.top - margin2_t.bottom;

// var parseDate = d3.timeParse("%b %Y");
var parseDate = d3.timeParse("%Y/%m/%d");
// var formatTime = d3.timeParse("%Y/%m/%d");

var x = d3.scaleTime().range([0, width_t]),
    x2 = d3.scaleTime().range([0, width_t]),
    y = d3.scaleLinear().range([height_t, 0]),
    y2 = d3.scaleLinear().range([height2_t, 0]);

var xAxis = d3.axisBottom(x),
    xAxis2 = d3.axisBottom(x2),
    yAxis = d3.axisLeft(y);

var brush = d3.brushX()
    .extent([[0, 0], [width_t, height2_t]]) //movable range in x axis
    .on("brush end", brushed);

var zoom = d3.zoom()
    .scaleExtent([1, Infinity])
    .translateExtent([[0, 0], [width_t, height_t]])
    .extent([[0, 0], [width_t, height_t]])
    .on("zoom", zoomed);

var area = d3.area()
    .curve(d3.curveMonotoneX)
    .x(function(d) { return x(d.date); })
    .y0(height_t)
    .y1(function(d) { return y(d.count); });

var area2 = d3.area()
    .curve(d3.curveMonotoneX)
    .x(function(d) { return x2(d.date); })
    .y0(height2_t)
    .y1(function(d) { return y2(d.count); });

svg_t.append("defs").append("clipPath")
    .attr("id", "clip")
  .append("rect")
    .attr("width", width_t)
    .attr("height", height_t);

// Top line chart
var focus = svg_t.append("g")
    .attr("class", "focus")
    .attr("transform", "translate(" + margin_t.left + "," + margin_t.top + ")");

// Bottom whole timeline for zoom and brush
var context = svg_t.append("g")
    .attr("class", "context")
    .attr("transform", "translate(" + margin2_t.left + "," + margin2_t.top + ")");

d3.csv("/static/data/datecount.csv", type, function(error, data) {
  if (error) throw error;

  x.domain(d3.extent(data, function(d) { return d.date; }));
  y.domain([0, d3.max(data, function(d) { return d.count; })]);
  x2.domain(x.domain());
  y2.domain(y.domain());

  focus.append("path")
      .datum(data)
      .attr("class", "area")
      // .style("fill", "yellow")
      .attr("d", area);

  focus.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + height_t + ")")
      .call(xAxis);

  focus.append("g")
      .attr("class", "axis axis--y")
      .call(yAxis);

  context.append("path")
      .datum(data)
      .attr("class", "area")
      .attr("d", area2);

  context.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + height2_t + ")")
      .call(xAxis2);

  context.append("g")
      .attr("class", "brush")
      //Right click to update calendars and wordcloud;
      // .on("mousedown", function(){
      //     if(d3.event.button === 2){  
      //         update_calendar_cloud();
      //     };
      // })
      .call(brush)
      .call(brush.move, x.range());

  var rect = svg_t.append("rect")
      .attr("class", "zoom")
      .attr("width", width_t)
      .attr("height", height_t)
      .attr("transform", "translate(" + margin_t.left + "," + margin_t.top + ")")
      .call(zoom);
});

function brushed() {
  if (d3.event.sourceEvent && d3.event.sourceEvent.type === "zoom") return; // ignore brush-by-zoom
  var s = d3.event.selection || x2.range(); // plot width of event selection or whole context range
  x.domain(s.map(x2.invert, x2)); // invert: numerical range to date range

  focus.select(".area").attr("d", area);
  focus.select(".axis--x").call(xAxis);
  svg_t.select(".zoom").call(zoom.transform, d3.zoomIdentity
      .scale(width_t / (s[1] - s[0]))
      .translate(-s[0], 0));


}

function zoomed() {
  if (d3.event.sourceEvent && d3.event.sourceEvent.type === "brush") return; // ignore zoom-by-brush
  var t = d3.event.transform;
  // console.log(d3.event, t);
  x.domain(t.rescaleX(x2).domain());
  // console.log('zoom',x2.domain()); //[Thu Jan 01 2015 00:00:00 GMT+0100 (Central European Standard Time), Thu Sep 06 2018 00:00:00 GMT+0200 (Central European Summer Time)]
  focus.select(".area").attr("d", area);
  focus.select(".axis--x").call(xAxis);
  context.select(".brush").call(brush.move, x.range().map(t.invertX, t));

  update_calendar_cloud();
}

function type(d) {
  d.date = parseDate(d.date); //convert to Date type
  d.count = +d.count;
  return d;
}

function update_slider(){
  var parseCalender = d3.timeParse("%Y-%m-%d")
  var parseCalender2 = d3.timeParse("%d-%m-%Y")
  var first = parseCalender('2015-01-01')
  var last = parseCalender('2018-09-06')
  var totalDuration = Math.floor((last-first)/(1000 * 60 * 60 * 24)); //1343 days in total

  var startDate = parseCalender2(document.getElementById("start").value);
  var endDate = parseCalender2(document.getElementById("end").value);
  var selectedDuration = Math.floor((endDate-startDate)/(1000 * 60 * 60 * 24))/totalDuration*(x.range()[1]-x.range()[0]);
  console.log(document.getElementById("start").value, startDate);
  var start2first = Math.floor((startDate-first)/(1000 * 60 * 60 * 24)) ;
  var startIndex = start2first/totalDuration*(width_t-20); //width_t+2
  var sliderbutton = document.getElementById("sliderButton").value;

  x.domain([startDate,endDate])
  console.log(x.domain);

  focus.select(".area").attr("d", area);
  focus.select(".axis--x").call(xAxis);
  svg_t.select(".zoom").call(zoom.transform, d3.zoomIdentity
      .scale((width_t-20) / selectedDuration)
      .translate(-startIndex, 0));

}

function update_calendar_cloud(){

  // Click slider2DatesButton; OR mouseup event?(later)
  // Get domain of focus
  // Convert domain to YYYY-mm-dd
  // Pass dates to calendars' values
  // Trigger update_cloud(); 

  console.log(x.domain());
  var brush_start = new Date(x.domain()[0]);
  var input_start = brush_start.getFullYear()+'-'+("0"+(brush_start.getMonth()+1)).slice(-2)+'-'+("0"+brush_start.getDate()).slice(-2);
  var input_start_picker = ("0"+brush_start.getDate()).slice(-2)+'-'+("0"+(brush_start.getMonth()+1)).slice(-2)+'-'+brush_start.getFullYear();
 
  // document.getElementById("start").value = input_start_picker;
  $("#start").datepicker("update", input_start_picker);

  var brush_end = new Date(x.domain()[1]);
  var input_end = brush_end.getFullYear()+'-'+("0"+(brush_end.getMonth()+1)).slice(-2)+'-'+("0"+brush_end.getDate()).slice(-2);
  var input_end_picker = ("0"+brush_end.getDate()).slice(-2)+'-'+("0"+(brush_end.getMonth()+1)).slice(-2)+'-'+brush_end.getFullYear();
 
  console.log(input_start_picker, input_end_picker);
  // document.getElementById("end").value = input_end_picker;
  $("#end").datepicker("update", input_end_picker);
  update_cloud();

}


