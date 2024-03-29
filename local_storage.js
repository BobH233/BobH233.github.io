
function get_storage_server_ip() {
  if(localStorage["flyeagle_serverip"] == undefined) {
    return "ws://127.0.0.1:9604"
  }else {
    return localStorage["flyeagle_serverip"]
  }
}


function set_storage_server_ip(ip) {
  localStorage["flyeagle_serverip"] = ip;
}