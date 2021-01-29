
function update_menu(selected_event){
  $.ajax({
    url: '',
    data: {
      'selected_event':selected_event
    },
    dataType: 'json',
    success: function (data) {
      console.log(selected_event);
      var topic_text = data['topics'];

      var min = Math.min.apply(Math, topic_text.map(function(o) { return o.prob; }))
      var max = Math.max.apply(Math, topic_text.map(function(o) { return o.prob; }))
      
      var extrem = [];
      // Handle log(0) error;
      if(min == 0){min = "1e-6"}
      if(max == 0){max = "1e-6"}
      extrem.push(min.toString(),max.toString())
      
      update_relevant_terms(selected_event);
      display_topics(topic_text,extrem);
      draw_timeline(selected_event); //Update timeline with relevant tweets count data


    }
  });
}


function update_relevant_terms(event){
  for ( var i=0; i<merged_terms.length; i++){
    if (merged_terms[i].event === event){
      // console.log(merged_terms[i].keywords);
      document.getElementById("term-dict").innerHTML = merged_terms[i].keywords;

      // Update wordcloud
      var cw = d3.selectAll("#my_cloudviz text")
                 .style('opacity', 0.1);      
      var sp = merged_terms[i].keywords.split(",").forEach(function(d){topic2cloud(d);});
     
    }
  }
}

// Visualize topics and terms in table form
function display_topics(data,extrem){

  //clear old vis chart
  d3.selectAll("#topic-div > *").remove();

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
  var colorbar = ["#FFFFFF","#0497cc","#FFFFBF", "#5E4FA2", "#66C2A5", "#3288BD", "#ABDDA4", "#E6F598", "#FEE08B", "#FDAE61", "#F46D43", "#D53E4F", "#9E0142"]
  // Build color scale
  var myColor = d3.scaleLog()// Options: d3.scalePow(), d3.scaleLinear()
    .range([colorbar[0],colorbar[1]])
    .domain([extrem[0],extrem[1]])


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


