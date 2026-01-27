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
var svg = d3.select("#global_map_svg"),
  margin = { top: 60, right: 60, bottom: 60, left: 60 },
  width = +svg.attr("width") - margin.left - margin.right,
  height = +svg.attr("height") - margin.top - margin.bottom;

function updateSpeedTextPlot(speed, acce) {
  svg.select("#speedText").text(`${speed.toFixed(2)} m/s`);
  svg.select("#acceText").text(`${acce.toFixed(2)} m/s^2`);
}

var offsetX = 30,
  offsetY = 30;

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

  svg
    .select("#speedBackground")
    // .transition() // 使用过渡效果平滑更新位置
    // .duration(500) // 过渡时间为500毫秒
    .attr("x", newX - 60 + offsetX)
    .attr("y", newY - 35 + offsetY);

  svg
    .select("#speedText")
    // .transition() // 使用过渡效果平滑更新位置
    // .duration(500) // 过渡时间为500毫秒
    .attr("x", newX + 10 + offsetX)
    .attr("y", newY - 15 + offsetY);
  svg
    .select("#acceText")
    // .transition() // 使用过渡效果平滑更新位置
    // .duration(500) // 过渡时间为500毫秒
    .attr("x", newX + 10 + offsetX)
    .attr("y", newY + offsetY);
}

var trackPoints = [];

var xScale, yScale;

d3.json("./track_full.json")
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
    // console.log(trackPoints);
    svg
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .append("path")
      .datum(trackPoints)
      .attr("fill", "none")
      .attr("stroke", "white")
      .attr("stroke-width", 5)
      .attr("d", lineGenerator);

    // 假设赛车当前位置在轨迹点数组的中间
    var carPosition = trackPoints[0];

    svg
      .append("rect")
      .attr("id", "speedBackground")
      .attr("x", xScale(carPosition.x) - 60 + offsetX) // 以车辆位置为基准进行偏移
      .attr("y", yScale(carPosition.y) - 35 + offsetY)
      .attr("width", 150) // 设定宽高
      .attr("height", 45)
      .attr("fill", "rgba(255,255,255,0.7)")
      .attr("rx", 5) // x轴方向圆角半径
      .attr("ry", 5); // y轴方向圆角半径

    // 添加速度指示的文本
    svg
      .append("text")
      .attr("id", "speedText")
      .attr("x", xScale(carPosition.x) + 10 + offsetX) // 以车辆位置为基准
      .attr("y", yScale(carPosition.y) - 15 + offsetY)
      .attr("text-anchor", "middle") // 文本居中对齐
      .attr("fill", "white") // 文本颜色
      .style("font-weight", "bold")
      .attr("filter", "url(#textShadow)")
      .text("speed: 0m/s"); // 初始文本内容
    svg
      .append("text")
      .attr("id", "acceText")
      .attr("x", xScale(carPosition.x) + 10 + offsetX) // 以车辆位置为基准
      .attr("y", yScale(carPosition.y) + offsetY)
      .attr("text-anchor", "middle") // 文本居中对齐
      .attr("fill", "white") // 文本颜色
      .style("font-weight", "bold")
      .attr("filter", "url(#textShadow)")
      .text("acce: 0m/s^2"); // 初始文本内容
    svg
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .append("circle")
      .attr("id", "carPosition")
      .attr("cx", xScale(carPosition.x))
      .attr("cy", yScale(carPosition.y))
      .attr("r", 3)
      .attr("fill", "red")
      .attr("filter", "url(#shadow)");
  })
  .catch(function (error) {
    console.log("Error loading the file: ", error);
  });

var miniMapEnable = true;
function switchMiniMap() {
  if(miniMapEnable) {
    miniMapEnable = false;
    localStorage["miniMapEnable"] = 'false';
    document.getElementById("map_container_card").style.display = "none";
  } else {
    miniMapEnable = true;
    localStorage["miniMapEnable"] = 'true';
    document.getElementById("map_container_card").style.display = "";
  }
}

var logWindowEnable = true;
function switchLog() {
  if(logWindowEnable) {
    logWindowEnable = false;
    localStorage["logWindowEnable"] = 'false';
    document.getElementById("floating_log_card").style.display = "none";
  } else {
    logWindowEnable = true;
    localStorage["logWindowEnable"] = 'true';
    document.getElementById("floating_log_card").style.display = "";
  }
}
