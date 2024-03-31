

function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tab-content");
  for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tab-link");
  for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

function calcSlipRatio(tireSpeed, vehSpeed) {
  return (vehSpeed - tireSpeed) / vehSpeed;
}

var ws_connected = false

var ws = null

function tyre_speed_rad_to_m(speed_rad) {
  var radius = 0.310;
  // 角速度（单位：弧度/秒）
  var angular_speed = speed_rad;
  // 线速度（单位：米/秒）
  var linear_speed = radius * angular_speed;
  return linear_speed;
}

function setStatusDotColor(objDict, greenValue, name) {
  if(document.getElementById(`${name}dot`) == null) return;
  if(objDict[name] == greenValue) {
    document.getElementById(`${name}dot`).style.backgroundColor = "#76f976";
  } else {
    document.getElementById(`${name}dot`).style.backgroundColor = "#ff7373";
  }
}

var lastMessageTime = Date.now();


function handleWSMessage(message_content) {
  let jObj = JSON.parse(message_content);
  if(jObj != {}) {
    lastMessageTime = Date.now();
  }
  if(jObj["eye_planner_state"] != undefined) {
    setStatusDotColor(jObj["eye_planner_state"], 1, "localization_received_");
    setStatusDotColor(jObj["eye_planner_state"], 1, "race_control_report_received_");
    setStatusDotColor(jObj["eye_planner_state"], 1, "loc_status_received_");
    setStatusDotColor(jObj["eye_planner_state"], 1, "bsu_status_recived_");
    setStatusDotColor(jObj["eye_planner_state"], 0, "loc_timeout");
    setStatusDotColor(jObj["eye_planner_state"], 0, "rc_timeout");
    setStatusDotColor(jObj["eye_planner_state"], 0, "bsu_status_timeout");
  }
  if(jObj["ego_loc"] != undefined) {
    document.getElementById("veh_pos_X").innerText = `X: ${jObj["ego_loc"]["position"]["x"].toFixed(3)}`;
    document.getElementById("veh_pos_Y").innerText = `Y: ${jObj["ego_loc"]["position"]["y"].toFixed(3)}`;
    document.getElementById("veh_pos_Z").innerText = `Z: ${jObj["ego_loc"]["position"]["z"].toFixed(3)}`;
    updateCarPosition({
      x: jObj["ego_loc"]["position"]["x"],
      y: jObj["ego_loc"]["position"]["y"],
    });
    document.getElementById("orientation_X").innerText = `X: ${jObj["ego_loc"]["orientation_ypr"]["x"].toFixed(3)}`;
    document.getElementById("orientation_Y").innerText = `Y: ${jObj["ego_loc"]["orientation_ypr"]["y"].toFixed(3)}`;
    document.getElementById("orientation_Z").innerText = `Z: ${jObj["ego_loc"]["orientation_ypr"]["z"].toFixed(3)}`;
    setCompassDirection(jObj["ego_loc"]["orientation_ypr"]["z"]);
  }
  if(jObj["controller_debug"] != undefined) {
    globalChart.leteral_error_chart.refresh(Math.abs(jObj["controller_debug"]["leteral_error"]));
    globalChart.yaw_error_chart.refresh(Math.abs(jObj["controller_debug"]["yaw_error"]));
    globalChart.speed_error_chart.refresh(Math.abs(jObj["controller_debug"]["speed_error"]));
  }
  if(jObj["ego_state"] != undefined) {
    globalChart.speed_chart.refresh(Math.abs(jObj["ego_state"]["velocity"]["x"]));
    updateSpeedTextPlot(Math.abs(jObj["ego_state"]["velocity"]["x"]), Math.abs(jObj["ego_state"]["acceleration"]["x"]));
    globalChart.acc_chart.refresh(Math.abs(jObj["ego_state"]["acceleration"]["x"]));
    globalChart.ang_rate_chart.refresh(Math.abs(jObj["ego_state"]["angular_rate"]["z"]))
  }
  if(jObj["ice_status_01"] != undefined) {
    document.getElementById("actual_gear").innerText = `actual_gear: ${jObj["ice_status_01"]["ice_actual_gear"]}`;
    document.getElementById("current_gear_show").innerText = `${jObj["ice_status_01"]["ice_actual_gear"]}`;
    document.getElementById("actual_throttle").innerText = `actual_throttle: ${jObj["ice_status_01"]["ice_actual_throttle"].toFixed(2)} %`;
  }
  if(jObj["ice_status_02"] != undefined) {
    globalChart.oil_temp_chart.refresh(jObj["ice_status_02"]["ice_oil_temp_deg_c"]);
    globalChart.engine_speed_chart.refresh(jObj["ice_status_02"]["ice_engine_speed_rpm"]);
    globalChart.water_temp_chart.refresh(jObj["ice_status_02"]["ice_water_temp_deg_c"]);
  }
  if(jObj["psa_status_01"] != undefined) {
    document.getElementById("actual_psa").innerText = `actual_psa: ${jObj["psa_status_01"]["psa_actual_pos_rad"].toFixed(3)} °`;
  }
  if(jObj["hlmsg_01"] != undefined) {
    globalChart.fl_target_pressure_chart.refresh(jObj["hlmsg_01"]["hl_target_pressure_fl"]);
    globalChart.fr_target_pressure_chart.refresh(jObj["hlmsg_01"]["hl_target_pressure_fr"]);
    globalChart.rl_target_pressure_chart.refresh(jObj["hlmsg_01"]["hl_target_pressure_rl"]);
    globalChart.rr_target_pressure_chart.refresh(jObj["hlmsg_01"]["hl_target_pressure_rr"]);
    document.getElementById("target_throttle").innerText = `target_throttle: ${jObj["hlmsg_01"]["hl_target_throttle"].toFixed(2)}%`;
    document.getElementById("target_gear").innerText = `target_gear: ${jObj["hlmsg_01"]["hl_target_gear"]}`;
  }
  if(jObj["hlmsg_02"] != undefined) {
    document.getElementById("target_psa").innerText = `target_psa: ${jObj["hlmsg_02"]["hl_target_psa_control"].toFixed(3)} °`
  }
  if(jObj["wheel_speed_01"] != undefined && jObj["ego_state"] != undefined) {
    var car_speed = jObj["ego_state"]["velocity"]["x"];
    var slip_fl = calcSlipRatio(tyre_speed_rad_to_m(jObj["wheel_speed_01"]["wss_speed_fl_rad_s"]), car_speed) * 100;
    var slip_fr = calcSlipRatio(tyre_speed_rad_to_m(jObj["wheel_speed_01"]["wss_speed_fr_rad_s"]), car_speed) * 100;
    var slip_rl = calcSlipRatio(tyre_speed_rad_to_m(jObj["wheel_speed_01"]["wss_speed_rl_rad_s"]), car_speed) * 100;
    var slip_rr = calcSlipRatio(tyre_speed_rad_to_m(jObj["wheel_speed_01"]["wss_speed_rr_rad_s"]), car_speed) * 100;

    document.getElementById("fl_slip_ratio").innerText = `slip_ratio: ${slip_fl.toFixed(2)} %`;
    document.getElementById("fr_slip_ratio").innerText = `slip_ratio: ${slip_fr.toFixed(2)} %`;
    document.getElementById("rl_slip_ratio").innerText = `slip_ratio: ${slip_rl.toFixed(2)} %`;
    document.getElementById("rr_slip_ratio").innerText = `slip_ratio: ${slip_rr.toFixed(2)} %`;
  }
  if(jObj["wheel_speed_01"] != undefined) {
    document.getElementById("fl_speed_rad").innerText = `speed_rad: ${jObj["wheel_speed_01"]["wss_speed_fl_rad_s"].toFixed(2)} rad/s`;
    document.getElementById("fl_speed_m").innerText = `speed_m: ${tyre_speed_rad_to_m(jObj["wheel_speed_01"]["wss_speed_fl_rad_s"]).toFixed(2)} m/s`;

    document.getElementById("fr_speed_rad").innerText = `speed_rad: ${jObj["wheel_speed_01"]["wss_speed_fr_rad_s"].toFixed(2)} rad/s`;
    document.getElementById("fr_speed_m").innerText = `speed_m: ${tyre_speed_rad_to_m(jObj["wheel_speed_01"]["wss_speed_fr_rad_s"]).toFixed(2)} m/s`;

    document.getElementById("rl_speed_rad").innerText = `speed_rad: ${jObj["wheel_speed_01"]["wss_speed_rl_rad_s"].toFixed(2)} rad/s`;
    document.getElementById("rl_speed_m").innerText = `speed_m: ${tyre_speed_rad_to_m(jObj["wheel_speed_01"]["wss_speed_rl_rad_s"]).toFixed(2)} m/s`;

    document.getElementById("rr_speed_rad").innerText = `speed_rad: ${jObj["wheel_speed_01"]["wss_speed_rr_rad_s"].toFixed(2)} rad/s`;
    document.getElementById("rr_speed_m").innerText = `speed_m: ${tyre_speed_rad_to_m(jObj["wheel_speed_01"]["wss_speed_rr_rad_s"]).toFixed(2)} m/s`;
  }
  // console.log(JSON.parse(message_content));
}

const decoder = new TextDecoder("utf-8");
function checkWsStatus() {
  var nd = document.getElementById("ws_status");
  var now_ms = Date.now();
  if(ws_connected) {
    if(now_ms - lastMessageTime > 1000) {
      nd.innerHTML = "Timeout";
      nd.style = "background-color: rgb(231 29 255); margin-left: 20px;";
    } else {
      nd.innerHTML = "Connected";
      nd.style = "background-color: rgb(0, 185, 15); margin-left: 20px;";
    }
  }else{
    nd.innerHTML = "Connecting";
    nd.style = "background-color: orange; margin-left: 20px;";
    ws = new WebSocket(get_storage_server_ip());
    ws.onopen = () => {
      ws_connected = true;
    }
    ws.onmessage = (event) => {
      handleWSMessage(event.data);
    }
    ws.onclose = () => {
      ws_connected = false;
    }
    ws.onerror = (error) => {
      ws_connected = false;
    }
  }
}

setInterval(checkWsStatus, 1000)

var globalChart = {};

function setCardClick() {
  var cards = document.getElementsByClassName("card");
  for(let i=0;i<cards.length;i++) {
    if(cards[i].getAttribute("note") == "no_strength") continue;
    cards[i].onclick = () => {
      if(cards[i].style.background == '') {
        cards[i].style.background = "#2d491e";
      } else {
        cards[i].style.background = '';
      }
    }
  }
}

function setServerIP() {
  document.getElementById('serverIp').value = get_storage_server_ip();
}

window.onload = function(){
  setCardClick();
  setServerIP();
  $( "#map_container_card" ).draggable();
  $( "#floating_log_card" ).draggable();

  if(localStorage["miniMapEnable"] == 'false') {
    document.getElementById("map_container_card").style.display = "none";
    miniMapEnable = false;
  }
  if(localStorage["logWindowEnable"] == 'false') {
    document.getElementById("floating_log_card").style.display = "none";
    logWindowEnable = false;
  }

  const font_family = 'Courier New';
  globalChart.leteral_error_chart = new JustGage({
    id: "leteral_eror_card_content",
    value: 0,
    min: 0,
    max: 5,
    title: "leteral_eror",
    decimals: 4,
    label: "m",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "20px",
    titlePosition: "below",
  });
  globalChart.yaw_error_chart = new JustGage({
    id: "yaw_eror_card_content",
    value: 0,
    min: 0,
    max: 5,
    title: "yaw_eror",
    decimals: 4,
    label: "rad",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "20px",
    titlePosition: "below",
  });
  globalChart.speed_error_chart = new JustGage({
    id: "speed_eror_card_content",
    value: 0,
    min: 0,
    max: 30,
    title: "speed_eror",
    decimals: 2,
    label: "m/s",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "20px",
    titlePosition: "below",
  });
  globalChart.speed_chart = new JustGage({
    id: "vel_card_content",
    value: 0,
    min: 0,
    max: 90,
    title: "speed_x",
    decimals: 2,
    label: "m/s",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "20px",
    titlePosition: "below",
  });
  globalChart.acc_chart = new JustGage({
    id: "acc_card_content",
    value: 0,
    min: 0,
    max: 50,
    title: "acceleration_x",
    decimals: 2,
    label: "m/s^2",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "20px",
    titlePosition: "below",
  });
  globalChart.water_temp_chart = new JustGage({
    id: "water_temp_content",
    value: 20,
    min: 20,
    max: 100,
    title: "Water\nTemperature",
    decimals: 2,
    label: "°C",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "20px",
    titlePosition: "below",
  });
  globalChart.oil_temp_chart = new JustGage({
    id: "oil_temp_content",
    value: 20,
    min: 20,
    max: 100,
    title: "Oil\nTemperature",
    decimals: 2,
    label: "°C",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "20px",
    titlePosition: "below",
  });
  globalChart.engine_speed_chart = new JustGage({
    id: "engine_speed_content",
    value: 0,
    min: 0,
    max: 10000,
    title: "Engine\nSpeed",
    decimals: 2,
    label: "RPM",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "20px",
    titlePosition: "below",
  });
  globalChart.ang_rate_chart = new JustGage({
    id: "ang_rate_card_content",
    value: 0,
    min: 0,
    max: 3.14,
    title: "angular_rate_z",
    decimals: 2,
    label: "rad/s",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "20px",
    titlePosition: "below",
  });
  globalChart.fl_target_pressure_chart = new JustGage({
    id: "fl_target_pressure",
    value: 0,
    min: 0,
    max: 100,
    title: "target\npressure",
    decimals: 2,
    label: "%",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "10px",
    titlePosition: "below",
  });
  globalChart.fr_target_pressure_chart = new JustGage({
    id: "fr_target_pressure",
    value: 0,
    min: 0,
    max: 100,
    title: "target\npressure",
    decimals: 2,
    label: "%",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "10px",
    titlePosition: "below",
  });
  globalChart.rl_target_pressure_chart = new JustGage({
    id: "rl_target_pressure",
    value: 0,
    min: 0,
    max: 100,
    title: "target\npressure",
    decimals: 2,
    label: "%",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "10px",
    titlePosition: "below",
  });
  globalChart.rr_target_pressure_chart = new JustGage({
    id: "rr_target_pressure",
    value: 0,
    min: 0,
    max: 100,
    title: "target\npressure",
    decimals: 2,
    label: "%",
    valueFontColor: "white",
    titleFontColor: "#b8b8b8",
    titleFontFamily: font_family,
    titleMinFontSize: "10px",
    titlePosition: "below",
  });
  // document.getElementById("nodestatus_tab_link").click();
  // document.getElementById("global_map_link").click();
  
  document.getElementById("controller_tab_link").click();

}

function showSetting() {
  document.getElementById('modalOverlay').style.display = 'block';
}

function hideSetting() {
  document.getElementById('modalOverlay').style.display = 'none';
}

function showAbout() {
  document.getElementById('modalOverlay_About').style.display = 'block';
}

function hideAbout() {
  document.getElementById('modalOverlay_About').style.display = 'none';
}

function saveSettings(){
  set_storage_server_ip(document.getElementById("serverIp").value);
  hideSetting();
}

function setIP(evt) {
  document.getElementById("serverIp").value = evt.getAttribute("ip");
}

function addLogMessage(title, message) {
  const logList = document.getElementById('logMessages');
  const newLogItem = document.createElement('li');
  
  // 获取当前时间并格式化
  const now = new Date();
  const timestamp = now.toLocaleTimeString(); // 格式化时间为本地时间字符串
  
  // 创建内容字符串，包括标题、消息和时间戳
  newLogItem.innerHTML = `<strong>${title}</strong><br>${message}<br><small>${timestamp}</small>`;
  
  // 将新日志项插入到列表最前面
  logList.insertBefore(newLogItem, logList.firstChild);
}

// addLogMessage('Test Log', 'Hello world');
function setCompassDirection(rad) {
  rad = -rad;
  var arrow = document.getElementById('compassArrow');
  // 由于初始箭头指向上方，我们需要将其旋转90度（π/2 rad）使其指向右方作为基准方向
  var rotation = rad + Math.PI / 2; // 加上90度的调整值
  arrow.style.transform = `rotate(${rotation}rad)`;
  arrow.style.transformOrigin = '50% 50%'; // 以箭头中心为旋转中心
}