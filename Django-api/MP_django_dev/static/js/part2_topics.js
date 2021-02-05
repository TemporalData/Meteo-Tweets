function check_selection(){
  var choice = $('#selectButton').val();
  
  if (choice !== null){
    generate_topics(choice);
  }
  else{
    alert('Please select at least one event.');
  }
};


function generate_topics(selected_event){

  // Should be constrained by time and geolocation(as a list doc_id)
  var start_picker = $("#start").datepicker("getDate");
  var end_picker  = $("#end").datepicker("getDate");
  console.log(start_picker, end_picker);
  // var location = 0; 

  if (start_picker == null){
    var startDate = "2015-01-01"
  }
  else{
    var startDate = start_picker.getFullYear()+'-'+("0"+(start_picker.getMonth()+1)).slice(-2)+'-'+("0"+start_picker.getDate()).slice(-2);
  }

  if (end_picker == null){
    var endDate = "2018-09-06"
  }
  else{
    var endDate = end_picker.getFullYear()+'-'+("0"+(end_picker.getMonth()+1)).slice(-2)+'-'+("0"+end_picker.getDate()).slice(-2);
  }


  $.ajax({
    url: '',
    type: 'GET',
    data: {
      'selected_event':String(selected_event),
      'start':startDate,
      'end':endDate,
    },
    dataType: 'json',
    success: function (data) {
      if(data['topics'] !== false){
        var topic_text = jQuery.parseJSON(data['topics']);
        console.log(topic_text);

        var min = Math.min.apply(Math, topic_text.map(function(o) { return o.prob; }))
        var max = Math.max.apply(Math, topic_text.map(function(o) { return o.prob; }))
        

        var extrem = [];
        // Handle log(0) error;
        if(min == 0){min = "1e-6"}
        if(max == 0){max = "1e-6"}
        extrem.push(min.toString(),max.toString())
        
        // Update terms, cloud, timeline
        update_relevant_terms(selected_event);
        display_topics(topic_text,extrem);
        
        // draw_timeline(selected_event);
      }
      else{
        alert('No enough data!'); // When capture error returned by LDA modeling
      }

    }
  });
}

// Display related terms and update the wordcloud
function update_relevant_terms(events){
  var strList = '';
  for ( var i=0; i<merged_terms.length; i++){
    console.log(events, merged_terms[i].event);
    if (events.includes(merged_terms[i].event)){
      console.log(merged_terms[i].keywords);
      strList += merged_terms[i].keywords;
      strList += ',';
    }
    document.getElementById("term-dict").innerHTML = strList;
    // Update wordcloud
    d3.selectAll("#my_cloudviz text")
      .style('opacity', 0.1);      
    strList.split(",").forEach(function(d){topic2cloud(d);});

  }
}

// Visualize topics and terms in table form
function display_topics(data,extrem){

  //clear old vis chart
  d3.selectAll("#topic-div > *").remove();
  d3.selectAll("#topic-legend > *").remove();

  var margin = {top: 80, right: 25, bottom: 30, left: 40},
  width = 450 - margin.left - margin.right,
  height = 450 - margin.top - margin.bottom;

  // append the svg object to the body of the page
  var t_svg = d3.select("#topic-div")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

  
  // Labels of row and columns -> unique identifier of the column called 'group' and 'variable'
  var myGroups = d3.map(data, function(d){return d.group;}).keys()
  var myVars = d3.map(data, function(d){return d.variable;}).keys()

  // Build X scales and axis:
  var x = d3.scaleBand()
    .range([ 0, width ])
    .domain(myGroups)
    .padding(0.05);

  t_svg.append("g")
    .style("font-size", 30)
    .attr("transform", "translate(0,0)")
    .call(d3.axisTop(x).tickSize(0))
    .select(".domain").remove()

  // Build Y scales and axis:
  var y = d3.scaleBand()
   .range([ 0,height])
    .domain(myVars)
    .padding(0.05);
  t_svg.append("g")
    .style("font-size", 15)
    .call(d3.axisLeft(y).tickSize(0))
    .select(".domain").remove()

  // Color codes
  var colorbar = ["#FFFFFF","#0497cc","#FFFFBF", "#5E4FA2", "#66C2A5", "#3288BD", "#ABDDA4", "#E6F598", "#FEE08B", "#FDAE61", "#F46D43", "#D53E4F", "#9E0142"]
  // Build color scale
  var myColor = d3.scaleLog()// Options: d3.scalePow(), d3.scaleLinear()
    .range([colorbar[0],colorbar[1]])
    .domain([extrem[0],extrem[1]])

  // Add color scale legend
  continuous("#topic-legend", myColor);

  // create a tooltip
  var tooltip = d3.select("#topic-div")
    .append("div")
    .style("opacity", 0)
    .attr("class", "tooltip")
    .style("background-color", "white")
    .style("border", "solid")
    .style("border-width", "2px")
    .style("border-radius", "5px")
    .style("padding", "5px")

  // Three function that change the tooltip when user hover / move / leave a cell
  var mouseover = function(d) {
    tooltip
      .style("opacity", 1)
    d3.select(this)
      .style("stroke", "black")
      .style("opacity", 1)
  }
  var mousemove = function(d) {
    tooltip
      .html("The exact probability of<br>this term in this topic is: " +d.prob)
      .style("left", (d3.mouse(this)[0]+70) + "px")
      .style("top", (d3.mouse(this)[1]) + "px")
  }
  var mouseleave = function(d) {
    tooltip
      .style("opacity", 0)
    d3.select(this)
      .style("stroke", "none")
      .style("opacity", 0.8)
  }


  // add the squares
  t_svg.selectAll()
    .data(data, function(d) {return d.group+':'+d.variable;})
    .enter()
    .append("rect")
      .attr("x", function(d) { return x(d.group) })
      .attr("y", function(d) { return y(d.variable) })
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("width", x.bandwidth() )
      .attr("height", y.bandwidth() )
      // .style("fill", function(d,i) { return myColor2[i%10]} )
      .style("fill", function(d) { return myColor(d.prob)} )
      .style("stroke-width", 4)
      .style("stroke", "none")
      .style("opacity", 0.8)
    .on("mouseover", mouseover)
    .on("mousemove", mousemove)
    .on("mouseleave", mouseleave);

    // console.log(x.bandwidth(),y.bandwidth())

  var topicText = t_svg.selectAll()
    .data(data)
    .enter()
    .append('text')
    .text(function(d) { return d.text; })
    .attr("x", function(d) { return x(d.group)+x.bandwidth()/2; })
    .attr("y", function(d) { return y(d.variable)+y.bandwidth()/2; })
    .attr('text-anchor', 'middle')
    .style("font-size", "14px")


}


// create continuous color legend
function continuous(selector_id, colorscale) {
  var legendheight = 430,
      legendwidth = 80,
      margin_l = {top: 80, right: 60, bottom: 10, left: 2}; //{top: 10, right: 60, bottom: 10, left: 2}
  var canvas = d3.select(selector_id)
    .style("height", legendheight + "px")
    .style("width", legendwidth + "px")
    .style("position", "relative")
    .append("canvas")
    .attr("height", legendheight - margin_l.top - margin_l.bottom)
    .attr("width", 1)
    .style("height", (legendheight - margin_l.top - margin_l.bottom) + "px")
    .style("width", (legendwidth - margin_l.left - margin_l.right) + "px")
    .style("border", "1px solid #000")
    .style("position", "absolute")
    .style("top", (margin_l.top) + "px")
    .style("left", (margin_l.left) + "px")
    .node();

  var ctx = canvas.getContext("2d");

  var legendscale = d3.scaleLinear()
    .range([1, legendheight - margin_l.top - margin_l.bottom])
    .domain(colorscale.domain());

  // image data hackery based on http://bl.ocks.org/mbostock/048d21cf747371b11884f75ad896e5a5
  var image = ctx.createImageData(1, legendheight);
  d3.range(legendheight).forEach(function(i) {
    var c = d3.rgb(colorscale(legendscale.invert(i)));
    image.data[4*i] = c.r;
    image.data[4*i + 1] = c.g;
    image.data[4*i + 2] = c.b;
    image.data[4*i + 3] = 255;
  });
  ctx.putImageData(image, 0, 0);


  var legendaxis = d3.axisRight()
    .scale(legendscale)
    .tickSize(6)
    .ticks(8);

  var svg = d3.select(selector_id)
    .append("svg")
    .attr("height", (legendheight) + "px")
    .attr("width", (legendwidth) + "px")
    .style("position", "absolute")
    .style("left", "0px")
    .style("top", "0px")

  svg
    .append("g")
    .attr("class", "axis")
    .attr("transform", "translate(" + (legendwidth - margin_l.left - margin_l.right + 3) + "," + (margin_l.top) + ")")
    .call(legendaxis);
};




