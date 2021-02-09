$(start).datepicker('setStartDate', '01-01-2015');
$(start).datepicker('setEndDate', '06-09-2018');
$(end).datepicker('setStartDate', '01-01-2015');
$(end).datepicker('setEndDate', '06-09-2018');

var svg_t,
// define top focus size parameters
margin_t,
// define bottom context size parameters
margin2_t, 
width_t,
height_t,
height2_t;


var parseDate = d3.timeParse("%Y-%m-%d");
// var formatTime = d3.timeParse("%Y/%m/%d");
var toDate = d3.timeFormat("%Y-%m-%d"); // reverse of parseDate

var x,x2,y,y2;

var xAxis,xAxis2,yAxis;

var brush, zoom;
var area, area2;
var curvedLine;
// Top line chart
var focus ;
// Bottom whole timeline for zoom and brush
var context;

var avgCount, avgData;
var jsonObject;
var lines;

function extractCount(data,neighbors){
  return data.map(function(a) {return a.count;});
}

// data[{date:xxx, count:xxx}]
function movingAvg(data, neighbors) {
  return data.map((val, idx, arr) => {
    let start = Math.max(0, idx - neighbors), end = Math.min(arr.length, idx + neighbors)
    let subset = arr.slice(start, end + 1)
    let sum = subset.reduce((a,b) => a + b)
    return sum / subset.length
  })
}



var term_type = 'all';
// display all counts initially
draw_timeline(term_type)

function draw_timeline(term_type){
		d3.selectAll("#timeline > *").remove();
		//change timeline's title
		document.getElementById("timeline-title").innerHTML = ' Tweets Frequency('+term_type+')'; //.toUpperCase()
		
		svg_t = d3.select("#timeline")
		.append("svg")
		.attr("width", 960)
		.attr("height", 500);

		// define top focus size parameters
		margin_t = {top: 20, right: 20, bottom: 110, left: 40};
		// define bottom context size parameters
		margin2_t = {top: 430, right: 20, bottom: 30, left: 40};
		width_t = +svg_t.attr("width") - margin_t.left - margin_t.right;
		height_t = +svg_t.attr("height") - margin_t.top - margin_t.bottom;
		height2_t = +svg_t.attr("height") - margin2_t.top - margin2_t.bottom;

		x = d3.scaleTime().range([0, width_t]);
		x2 = d3.scaleTime().range([0, width_t]);
		y = d3.scaleLinear().range([height_t, 0]);
		y2 = d3.scaleLinear().range([height2_t, 0]);

		xAxis = d3.axisBottom(x),
		xAxis2 = d3.axisBottom(x2),
		yAxis = d3.axisLeft(y);

		brush = d3.brushX()
		.extent([[0, 0], [width_t, height2_t]]) //movable range in x axis
		.on("brush end", brushed);

		zoom = d3.zoom()
		.scaleExtent([1, Infinity])
		.translateExtent([[0, 0], [width_t, height_t]])
		.extent([[0, 0], [width_t, height_t]])
		.on("zoom", zoomed);
		// focus
		curvedLine = d3.line()
		.curve(d3.curveBasis)
		// .curve(d3.curveMonotoneX)
		.x(function(d) { return x(d.date);})
		.y(function(d) { return y(d.count);})

		area = d3.area()
		.curve(d3.curveBasis)
		// .curve(d3.curveMonotoneX)
		.x(function(d) { return x(d.date); })
		.y0(height_t)
		.y1(function(d) { return y(d.count); });

		area2 = d3.area()
		.curve(d3.curveMonotoneX)
		.x(function(d) { return x2(d.date); })
		.y0(height2_t)
		.y1(function(d) { return y2(d.count); });

		svg_t.append("defs")
		.append("clipPath")
		.attr("id", "clip")
		.append("rect")
		.attr("width", width_t)
		.attr("height", height_t);

		// Top line chart
		focus = svg_t.append("g")
		.attr("class", "focus")
		.attr("transform", "translate(" + margin_t.left + "," + margin_t.top + ")");

		// Bottom whole timeline for zoom and brush
		context = svg_t.append("g")
		.attr("class", "context")
		.attr("transform", "translate(" + margin2_t.left + "," + margin2_t.top + ")");

  		mouseG = svg_t.append("g")
        .attr("class", "mouse-over-effects")
        .attr("transform", "translate(" + (margin_t.left) + "," + margin_t.top + ")");




		$.ajax({
				url: '',
				data: {
					'termtype': term_type,
				},
				dataType: 'json',
				success: function (data) {
						var jsonObject;
						jsonObject  = data["response"].map(function(d) { return {date: parseDate(d.pub_date), count:d.count}; }) //reformat data 
						
						// Prepare data for moving average line
						avgData = data["response"].map(function(d) { return {date: parseDate(d.pub_date), count:d.count}; })
						avgCount = movingAvg(extractCount(avgData),10) // neighborhood is 10
						// // Generate moving average data
				        avgData.forEach(function(data, index){
				          data.count = avgCount[index];
				        });

				
						build_timeline(jsonObject);
		
				}
			});

}





// d3.csv("/static/data/datecount.csv", type, function(error, data) {
	// if (error) throw error;
function build_timeline(data){

	// Clear timeline board
	focus.select(".area").remove();
	context.select(".area").remove(); 
	svg_t.select(".rect").remove(); 
	focus.select(".axis axis--y").remove();

	x.domain(d3.extent(data, function(d) { return d.date; }));
	y.domain([0, d3.max(data, function(d) { return d.count; })]);
	x2.domain(x.domain());
	y2.domain(y.domain());

	focus.append("path")
			.datum(data)
			.attr("class", "area")
			// .style("fill", "yellow")
			.style("opacity", 0.75)
			.attr("d", area);

	// Moving Average line
	focus.append('path')
	  .datum(avgData)
	  .attr("class", "avg")
	  .attr('d', curvedLine)
	  .attr('clip-path', 'url(#clip)') //make sure the line not exceed the xaxis
	  .style("stroke", "red")
	  .style("stroke-width", "2px")
	  .style("opacity", 0.5)
	  .style("fill","none");



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
	
	var rect = svg_t.append("rect") // conflict with mouseG rect; but necessary for zoom in context
	  .attr("class", "zoom")
	  .attr("width", width_t)
	  .attr("height", height_t)
	  // .attr("transform", "translate(" + margin_t.left + "," + margin_t.top + ")")
	  .attr("transform", "translate("+svg_t.attr("width")+"," + margin_t.top + ")") 
	  .call(zoom);
	add_mouseG();
	update_slider();
}
// }); //end of d3.csv function



function add_mouseG(){
  // for vertical line following mouse
  mouseG.append("path") 
        .attr("class", "mouse-line")
        .style("stroke", "black")
        .style("stroke-width", "1px")
        .style("opacity", "0");  
  
  lines = document.getElementsByClassName("avg");
  // console.log(lines, lines[0].getTotalLength());
  var mousePerLine = mouseG.selectAll('.mouse-per-line')
        .data([avgData]) //avgData.slice(0,-1)
        .enter()
        .append("g")
        .attr("class", "mouse-per-line");

  // console.log(mousePerLine);
  mousePerLine.append("circle")
  .attr("r", 7)      
  .style("stroke",'red')
  .style("fill", "none")
  .style("stroke-width", "1px")
  .style("opacity", "0");

  mousePerLine.append("text")
  // .attr("transform", "translate(" + margin_t.left + "," + margin_t.top + ")");
  // .attr("transform", "translate(10,-30)"); //location of label text



  mouseG.append('rect') // append a rect to catch mouse movements on canvas
    .attr('width', width_t) // can't catch mouse events on a g element
    .attr('height', height_t)
    .attr('fill', 'none')
    .attr('pointer-events', 'all')
    .on('mouseout', function() { // on mouse out hide line, circles and text
      // console.log("mouseout");
      d3.select(".mouse-line")
        .style("opacity", "0");
      d3.selectAll(".mouse-per-line circle")
        .style("opacity", "0");
      d3.selectAll(".mouse-per-line text")
        .style("opacity", "0");
    })
    .on('mouseover', function() { // on mouse in show line, circles and text
      // console.log("mouseover");
      d3.select(".mouse-line")
        .style("opacity", "1");
      d3.selectAll(".mouse-per-line circle")
        .style("opacity", "1");
      d3.selectAll(".mouse-per-line text")
        .style("opacity", "1");
    })
    .on('mousemove', function() { // mouse moving over canvas
      // console.log("mouse move");
      var mouse = d3.mouse(this);
      d3.select(".mouse-line")
        .attr("d", function() {
          var d = "M" + mouse[0] + "," + height_t;
          d += " " + mouse[0] + "," + 0;
          return d;
        });
      // console.log(lines);
      d3.selectAll(".mouse-per-line")
        .attr("transform", function(d, i) {
          // console.log(width_t/mouse[0]);
          // console.log(x.invert(mouse[0]));
          var xDate = x.invert(mouse[0]),
              bisect = d3.bisector(function(d) { return d.date; }).right;
              idx = bisect(avgData, xDate);
          // console.log(idx)
          
          var beginning = 0,
              // end = lines[i].getTotalLength(),
              end = lines[i].getTotalLength(),
              target = null;

          while (true){
            target = Math.floor((beginning + end) / 2);
            pos = lines[i].getPointAtLength(target);
            if ((target === end || target === beginning) && pos.x !== mouse[0]) {
                break;
            }
            if (pos.x > mouse[0])      end = target;
            else if (pos.x < mouse[0]) beginning = target;
            else break; //position found
          }
          
          d3.select(this).select('text')
            .text('MA-20 Value: '+y.invert(pos.y).toFixed(2)+', Date: '+toDate(x.invert(mouse[0])))
            // adjust hover text's location
            .attr("transform", function(){
              if (mouse[0]/width_t < 0.5){
                return "translate(10,-30)";
              }
              else {
                return "translate(-300,-30)";
              }
            });          


          // console.log(toDate(x.invert(mouse[0])));
          return "translate(" + mouse[0] + "," + pos.y +")";
        });
    });

}




function brushed() {
	if (d3.event.sourceEvent && d3.event.sourceEvent.type === "zoom") return; // ignore brush-by-zoom
	var s = d3.event.selection || x2.range(); // plot width of event selection or whole context range
	x.domain(s.map(x2.invert, x2)); // invert: numerical range to date range

	focus.select(".area").attr("d", area);
	focus.select(".avg").attr("d", curvedLine);
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
	focus.select(".avg").attr("d", curvedLine);
	focus.select(".axis--x").call(xAxis);
	context.select(".brush").call(brush.move, x.range().map(t.invertX, t));

	// update_calendar_cloud();
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
	var startIndex = start2first/totalDuration*(width_t); //width_t-20
	
	x.domain([startDate,endDate])
	console.log(x.domain);

	focus.select(".area").attr("d", area);
	focus.select(".axis--x").call(xAxis);
  	focus.select(".avg").attr("d", curvedLine);
	svg_t.select(".zoom").call(zoom.transform, d3.zoomIdentity
			.scale((width_t) / selectedDuration)
			.translate(-startIndex-0.5, 0));

}

function update_calendar_cloud(){

	// Click slider2DatesButton; OR mouseup event?(later)
	// Get domain of focus
	// Convert domain to YYYY-mm-dd
	// Pass dates to calendars' values
	// Trigger update_cloud(); 

	console.log(x.domain());
	var brush_start = new Date(x.domain()[0]);
	var input_start_picker = ("0"+brush_start.getDate()).slice(-2)+'-'+("0"+(brush_start.getMonth()+1)).slice(-2)+'-'+brush_start.getFullYear();
 
	// document.getElementById("start").value = input_start_picker;
	$("#start").datepicker("update", input_start_picker);

	var brush_end = new Date(x.domain()[1]);
	var input_end_picker = ("0"+brush_end.getDate()).slice(-2)+'-'+("0"+(brush_end.getMonth()+1)).slice(-2)+'-'+brush_end.getFullYear();
 
	console.log(input_start_picker, input_end_picker);
	// document.getElementById("end").value = input_end_picker;
	$("#end").datepicker("update", input_end_picker);
	update_cloud();

}


