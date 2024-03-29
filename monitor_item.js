control_tab = {
  id: "control_tab",
  chinese: "控制监控",
  english: "ControllerInfo"
}

const control_tab_monitor = [
  {
    id: "lateralError",
    chinese: "横向误差",
    english: "leteral_eror"
  },
  {
    id: "yawError",
    chinese: "航向误差(yaw_error)",
    english: "yaw_error"
  },
  {
    id: "speedError",
    chinese: "速度误差",
    english: "speed_error"
  },
  {
    id: "vehSpeed",
    chinese: "车辆速度",
    english: "vehicle_velocity"
  },
  {
    id: "vehLocation",
    chinese: "车辆位置",
    english: "vehicle_position"
  },
  {
    id: "orientation_yaw",
    chinese: "车辆航向",
    english: "orientation_yaw"
  },
  {
    id: "angular_rate_z",
    chinese: "转向角速度",
    english: "angular_rate_z"
  },
  {
    id: "acceleration",
    chinese: "车辆加速度",
    english: "acceleration"
  }
]

const engine_tab_monitor = [
  {
    id: "waterTemp",
    chinese: "水温",
    english: "water_temperature"
  },
  {
    id: "oilTemp",
    chinese: "油温",
    english: "oil_temperature"
  },
  {
    id: "engineRPM",
    chinese: "发动机转速",
    english: "engine_speed_rpm"
  }
]

const actuator_tab_monitor = [
  {
    id: "wss_speed_fl_rad_s",
    chinese: "前左轮轮速",
    english: "speed_front_left"
  },
  {
    id: " wss_speed_fr_rad_s",
    chinese: "前右轮轮速",
    english: "speed_front_right"
  },
  {
    id: "wss_speed_rl_rad_s",
    chinese: "后左轮轮速",
    english: "speed_rear_left"
  },
  {
    id: " wss_speed_rr_rad_s",
    chinese: "后右轮轮速",
    english: "speed_rear_right"
  },
]


language = "english"

function insertSimpleItem(parent, itemInfo) {
  var pp = document.createElement("p");
  pp.className = "control_item";
  let title = (language == "chinese" ? itemInfo.chinese : itemInfo.english)
  pp.innerHTML = `${title}: <span id="${itemInfo.id}">Loading...</span>`;
  parent.appendChild(pp);
}

function ReloadEveryTab() {
  // control
  // document.getElementById("ControlMonitor").innerHTML = "";
  // control_tab_monitor.forEach((item)=> {
  //   insertSimpleItem(document.getElementById("ControlMonitor"), item);
  // });
  // engine
  // document.getElementById("Engine").innerHTML = "";
  // engine_tab_monitor.forEach((item)=> {
  //   // console.log(item);
  //   insertSimpleItem(document.getElementById("Engine"), item);
  // });
  // // actuator
  // document.getElementById("Actuator").innerHTML = "";
  // actuator_tab_monitor.forEach((item)=> {
  //   console.log(item);
  //   insertSimpleItem(document.getElementById("Actuator"), item);
  // });
}

ReloadEveryTab();

function switchLanguage(param) {
  if(param == 'en') {
    language = "english";
    ReloadEveryTab()
  } else {
    language = "chinese";
    ReloadEveryTab()
  }
}