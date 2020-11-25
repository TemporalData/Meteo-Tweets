function update_cloud(){
  var startDate = document.getElementById("start").value;
  var endDate = document.getElementById("end").value;

  // pass dates to views.py to process data; 
  // acquire new data results and generate graphs in template

  // console.log(String(startDate),String(endDate));
  document.getElementById("mytest2").innerHTML = 'From '+String(startDate)+' to '+String(endDate);

  $.ajax({
    url: '',
    data: {
      'start':startDate,
      'end':endDate
    },
    dataType: 'json',
    success: function (data) {
      console.log(data);
      // $('#map-text').html(data["response"][0]);

      var jsonObject = jQuery.parseJSON(data["response"][1]);//

      jsonObject.forEach(function(d){
        d.event = d.event;
        d.doc_list = d.doc_list;
      }
      );
      console.log(jsonObject);
      console.log(Object.keys(jsonObject[0]));
      console.log(jsonObject[5]["doc_list"].length);

      $("#my_cloudviz").data("value", jsonObject);
      draw_cloud();

    }
  });

};

function draw_cloud(){

  d3.selectAll("#my_cloudviz > *").remove();
  var mywords = $("#my_cloudviz").data("value");



// ================D3-Based WordCloud======================
  var cloud_svg = d3.select("#my_cloudviz")
    .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform",
      "translate(" + margin.left + "," + margin.top + ")");

  // Constructs a new cloud layout instance. It run an algorithm to find the position of words that suits your requirements
  // Wordcloud features that are different from one word to the other must be here

  var layout = d3.layout.cloud()
    .size([width, height])
    .words(mywords.map(function(d) { return {text: d.event, size:d.doc_list.length, list:d.doc_list}; }))
    .padding(15)        //space between words
    .rotate(function() { return ~~(Math.random() * 2) * 90; })
    // .rotate(0)
    .font("Impact")
    // .fontSize(20)
    .fontSize(function(d) { return d.size; })      // font size of words
    .text(function(d) { return d.text; })
    .on("end", draw);
  layout.start();

  // This function takes the output of 'layout' above and draw the words
  
  function draw(words) {

    var fill = d3.scaleOrdinal(d3.schemeSet2);
    cloud_svg
      .append("g")
        .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
        .selectAll("text")
          .data(words)
        .enter().append("text")
          .style("font-size", function(d) { return Math.log(d.size)*3+14; })
          // .style("font-size",20)
          .style("fill", function(d, i) { return fill(i); })//"#69b3a2")
          .attr("text-anchor", "middle")
          .style("font-family", "Impact")
          .attr("transform", function(d) {
            return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
          })
          .text(function(d) { return d.text; })
          // .on('mouseover',displayFreq)
          .on('mouseover', function(d,event){

            $('#word-doc-text').html('Corresponding documents are '+d.list+''); 
          })
          .on("mouseout", function(d,event){
            $('#word-doc-text').html('No relevant documents');
          });
  }

}