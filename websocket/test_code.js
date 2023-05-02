let webSocket = new WebSocket('ws://127.0.0.1:8000/ws?username=01');
webSocket.onmessage = function(e) { console.log(e) }
webSocket.send("sasdfas")
webSocket.close();

let webSocket = new WebSocket('ws://127.0.0.1:8000/ws?username=01&data={"parameter1":"START"}');


//데모용
let webSocket = new WebSocket('ws://127.0.0.1:8000/ws?username=01&data=OBU_DATA,obu_info,21352436531,issue_info,3252421');