  function draw_d3map(){
  
    $.ajax({
      url: 'http://127.0.0.1:8000/api/geo/',
      type: "GET",
      contentType: "application/json; charset=utf-8",
      dataType: 'json',
      data: {
        id_filter: "",
        start:"",
        end:"",
      },
      success: function (result) {
        
        draw_d3geo(result)
      }
    })
  }

  function draw_d3geo(){

    var data = new Array(100).fill(null).map(m=>[Math.random(),Math.random()]);
    var w = 960;
    var h = 500;
    var r = 3.5;

    var svg = d3.select("#d3Map").append("svg")
        .attr("width",w)
        .attr("height",h);
    
    var circles = svg.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx",d=>d[0]*w)
        .attr("cy",d=>d[1]*h)
        .attr("r",r);
    
    // Lasso functions
    var lasso_start = function() {
        lasso.items()
            .attr("r",3.5) // reset size
            .classed("not_possible",true)
            .classed("selected",false);
    };

    var lasso_draw = function() {
    
        // Style the possible dots
        lasso.possibleItems()
            .classed("not_possible",false)
            .classed("possible",true);

        // Style the not possible dot
        lasso.notPossibleItems()
            .classed("not_possible",true)
            .classed("possible",false);
    };

    var lasso_end = function() {
        // Reset the color of all dots
        lasso.items()
            .classed("not_possible",false)
            .classed("possible",false);

        // Style the selected dots
        lasso.selectedItems()
            .classed("selected",true)
            .attr("r",7);

        // Reset the style of the not selected dots
        lasso.notSelectedItems()
            .attr("r",3.5);

    };
    
    var lasso = d3.lasso()
        .closePathSelect(true)
        .closePathDistance(100)
        .items(circles)
        .targetArea(svg)
        .on("start",lasso_start)
        .on("draw",lasso_draw)
        .on("end",lasso_end);
    
    svg.call(lasso);
  }