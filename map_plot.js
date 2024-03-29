// var trackPoints = [
//   {x: 20, y: 20},
//   {x: 100, y: 100},
//   {x: 200, y: 50},
// ];

// 设置D3曲线生成器
var lineGenerator = d3
  .line()
  .x(function (d) {
    return d.x;
  })
  .y(function (d) {
    return d.y;
  })
  .curve(d3.curveBasis); // 这里使用curveBasis生成平滑曲线

// 在SVG容器中绘制曲线
var svg = d3.select("svg"),
  margin = { top: 20, right: 20, bottom: 20, left: 20 },
  width = +svg.attr("width") - margin.left - margin.right,
  height = +svg.attr("height") - margin.top - margin.bottom;

function updateCarPosition(newPosition) {
  // 计算新位置的x和y坐标
  var newX = xScale(newPosition.x);
  var newY = yScale(newPosition.y);

  // 选择红点并更新其位置
  svg
    .select("#carPosition")
    // .transition() // 使用过渡效果平滑更新位置
    // .duration(500) // 过渡时间为500毫秒
    .attr("cx", newX)
    .attr("cy", newY);
}


var trackPoints = [];

var xScale, yScale;

d3.json("./track_south.json")
  .then(function (jsonResult) {
    for (let i = 0; i < jsonResult["ReferenceLine"].length; i++) {
      trackPoints.push({
        x: jsonResult["ReferenceLine"][i][0],
        y: jsonResult["ReferenceLine"][i][1],
      });
    }

    var xExtent = d3.extent(trackPoints, function (d) {
        return d.x;
      }),
      yExtent = d3.extent(trackPoints, function (d) {
        return d.y;
      });

    xScale = d3.scaleLinear().domain(xExtent).range([0, width]);
    yScale = d3.scaleLinear().domain(yExtent).range([height, 0]);

    // 设置D3曲线生成器
    var lineGenerator = d3
      .line()
      .x(function (d) {
        return xScale(d.x);
      })
      .y(function (d) {
        return yScale(d.y);
      });
    // .curve(d3.curveBasis);
    console.log(trackPoints);
    svg
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .append("path")
      .datum(trackPoints)
      .attr("fill", "none")
      .attr("stroke", "white")
      .attr("stroke-width", 10)
      .attr("d", lineGenerator);

    // 假设赛车当前位置在轨迹点数组的中间
    var carPosition = trackPoints[0];
    svg
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .append("circle")
      .attr("id", "carPosition")
      .attr("cx", xScale(carPosition.x))
      .attr("cy", yScale(carPosition.y))
      .attr("r", 7)
      .attr("fill", "#0cff0c");
  })
  .catch(function (error) {
    console.log("Error loading the file: ", error);
  });
