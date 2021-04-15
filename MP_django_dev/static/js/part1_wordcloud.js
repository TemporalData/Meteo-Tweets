var margin = {top: 30, right: 30, bottom: 30, left: 50},
    width = 800 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;


// Update wordcloud with time duration
function update_cloud(){
  
  var start_picker = $("#start").datepicker("getDate");
  var end_picker  = $("#end").datepicker("getDate");


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


  // Pass dates to views.py to process data; 
  $.ajax({
    url: '',
    data: {
      'start':startDate,
      'end':endDate,
      'apply_change': "apply_change" // singal for update wordcloud 
    },
    dataType: 'json',
    success: function (data) {

      var jsonObject = jQuery.parseJSON(data["response"][1]);//
      // console.log(jsonObject);

      var groupBy = function(xs, key) {
        return xs.reduce(function(rv, x) {
          (rv[x[key]] = rv[x[key]] || []).push(x['doc_idx']);
          return rv
        }, []);
      };

      // Reform document objects to term-doclist objects
      var groupedByTerm=groupBy(jsonObject, 'terms__term')

      var eventlist = [];
      for (var term_doc in groupedByTerm){
        var pair = {};
        pair.event = term_doc;
        pair.doc_list = groupedByTerm[term_doc];
        pair.size = pair.doc_list.length;
        eventlist.push(pair);
      }


      $("#my_cloudviz").data("value", eventlist);
      // draw_cloud(); // old method 
      draw_no_overlap_cloud();

    }
  });

};

function draw_cloud(){

  d3.selectAll("#my_cloudviz > *").remove();
  var mywords = $("#my_cloudviz").data("value");



// ================D3-Based WordCloud======================
  var cloud_svg = d3.select("#my_cloudviz")
    .append("svg")
    .attr("width", '100%')
    .attr("height",'100%')
      // .attr("width", width + margin.left + margin.right)
      // .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("width", 800)
      .attr("height",800)
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


function draw_no_overlap_cloud(){
  var width = 600;
  var height = 400;
  
  // Remove all elements in old wordcloud
  d3.selectAll("#my_cloudviz > *").remove();
  var mywords = $("#my_cloudviz").data("value");
  
  // console.log(mywords);

  var cloud_svg = d3.select("#my_cloudviz")
    .append("svg")
    .attr("width", '100%')
    .attr("height",'100%')
    .append("g")
      .attr("transform",
      "translate(" + margin.left + "," + margin.top + ")");


  var minsize = _.min(_.map(mywords, 'size'));
  var maxsize = _.max(_.map(mywords, 'size'));
  // Define the minimal and maximal font size
  var minfont = 18;
  var maxfont = 35;
  
  var fill = d3.scaleOrdinal(d3.schemeCategory20)
  
  // for small screens (and slow cpu's) limit retries
  // console.log(width)
  var MAX_TRIES = (width > 400) ? 6 : 3;

  // Draw initial cloud wilthout filters
  generateSkillCloud();

  function generateSkillCloud(retryCycle) {

      var skillsToDraw = transformToCloudLayoutObjects(filterSkills(mywords), retryCycle);
      var layout = d3.layout.cloud()
                      .size([width, height])
                      .words(skillsToDraw)
                      .rotate(function() {
                          return (~~(Math.random() * 6) - 2.5) * 30;
                      })
                      .font("Impact")
                      .fontSize(function(d) {
                          return d.size;
                      })
                      .on("end", function(fittedSkills) {
                          // check if all words fit and are included
                          if (fittedSkills.length == skillsToDraw.length) {
                              drawSkillCloud(fittedSkills); // finished
                          }
                          else if (!retryCycle || retryCycle < MAX_TRIES) {
                              // words are missing due to the random placement and limited room space
                              console.debug('retrying');
                              // try again and start counting retries
                              generateSkillCloud((retryCycle || 1) + 1);
                          }
                          else {
                              // retries maxed and failed to fit all the words
                              console.debug('gave up :(');
                              // just draw what we have
                              drawSkillCloud(fittedSkills);
                          }
                      })
                      .start();

      // Filter skills based on user input and transform to
      function filterSkills(skills) {
          // var textfilter = document.getElementById('filter').value;
          var textfilter = document.getElementById('my_cloudviz').value;
          return _.filter(skills, function(skill) {
              return !textfilter || skill.event.toLowerCase().indexOf(textfilter.toLowerCase()) >= 0;
          });
      }

      // Convert skill objects into cloud layout objects
      function transformToCloudLayoutObjects(skills, retryCycle) {
          return _.map(skills, function(skill) {
              return {
                  text: skill.event.toLowerCase(),
                  // size: toFontSize(skill.years, skill.relevancy, retryCycle),
                  size: toFontSize(skill.doc_list.length, 3, retryCycle),
                  list: skill.doc_list,
              };
          });
      }

      /**
       * 1. Determine font size based on years of experience relative to the skills with the least and most years of experience.
       * 2. Further increase / decrease font size based on relevancy (linux 20y is could less relevant than java 3y, so relevancy 
       *    .2 vs 1.5 could work for example).
       */
      function toFontSize(years, relevancy, retryCycle) {
        // console.log(years, relevancy, retryCycle);
          // translate years scale to font size scale and apply relevancy factor
          var linearSize = (((years - minsize+1) / (maxsize - minsize)) * (maxfont - minfont) * relevancy);
          // make the difference between small sizes and bigger sizes more pronounced for effect
          var polarizedSize = Math.log(linearSize*2 )*10+10;
          // reduce the size as the retry cycles ramp up (due to too many words in too small space)
          var reduceSize = polarizedSize * ((MAX_TRIES - retryCycle) / MAX_TRIES)+10;
          // console.log(lineairSize,polarizedSize,reduceSize);
          return ~~reduceSize;
      }

      // Main function to draw a wordcloud
      function drawSkillCloud(words) {


        // console.log(words);
        cloud_svg
          .append("g")
            .attr("transform", "translate(" + ~~(width / 2) + "," + ~~(height / 2) + ")")
            .selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", function(d) {
                return d.size + "px";
            })
            .style("-webkit-touch-callout", "none")
            .style("-webkit-user-select", "none")
            .style("-khtml-user-select", "none")
            .style("-moz-user-select", "none")
            .style("-ms-user-select", "none")
            .style("user-select", "none")
            .style("cursor", "default")
            .style("font-family", "Impact")
            .style("fill", function(d, i) {
                return fill(i);
            })
            .attr("text-anchor", "middle")
            .attr("transform", function(d) {
                return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
            })
            .text(function(d) {
                return d.text;
            })
            .on("click", function(d){ 
                console.log("onclick!");
                update_text(d); 
            })

            ;
              
              
      // set the viewbox to content bounding box (zooming in on the content, effectively trimming whitespace)
      var selected_svg = document.getElementsByTagName("svg")[1]; // cloud_svg
      var bbox = selected_svg.getBBox();
      var viewBox = [bbox.x, bbox.y, bbox.width, bbox.height].join(" ");
      selected_svg.setAttribute("viewBox", viewBox);
  
      }
  }
}

// Highlight word on click in the wordcloud and the heatmap
function update_text(data){

  // Mute all words
  d3.selectAll("#my_cloudviz text")
    .style('opacity', 0.1);

  d3.selectAll("#my_cloudviz text")
    .filter(function(){
        return d3.select(this).text() == data.text;
      })
    .style('opacity', 1);

  // Highlight clicked words in heatmap
  d3.selectAll("#topic-div text")
    .style("font-size", "14px") 
    .style("fill","black")  
    .style("font-weight", 400)

  d3.selectAll("#topic-div text")
    .filter(function(){
      return d3.select(this).text() == data.text;
    })
    .style("font-size", "20px")
    .style("font-weight", 700)
    .style("fill","orange")
    

}

// Filter words by seleted weather terms and change opacity to 1
function topic2cloud(term){
  d3.selectAll("#my_cloudviz text")
    .filter(function(){
        return d3.select(this).text() == term;
      })
    .style('opacity', 1);

}

// Click on blank area: Enable to revert to wordcloud with opacity 1
document.getElementById("cloud-body").addEventListener("click", check_cloud_click,false)
function check_cloud_click(e){
  if(e.type == "click"){
    if (e.target.nodeName !== "text"){
      d3.selectAll("#my_cloudviz text")
        .style('opacity', 1);
      // restore heatmap
      d3.selectAll("#topic-div text")
        .style("font-size", "14px") 
        .style("fill","black")  
        .style("font-weight", 400)
    }
  }
}