function appendSubscribedChannel($channelName, $websocket) {
  var channelName = $channelName;
  var unsubButton = $("<input type='button' value='unsubscribe'/>");
  var channelDiv  = $("<div><span>"+channelName+"</span></div>");

  channelDiv.append(unsubButton);
  $("#channelList").append(channelDiv);

  // add click event on unsubscribe button
  unsubButton.click(function() {
    console.log("unsubscribe "+channelName);
    var self = this;

    //$websocket.close();
    $websocket.send(JSON.stringify({'func': 'unsubscribe', 'channelName':channelName}));

    $(self).parent().remove();
  });
}

function createWebSocket() {

  if (WebSocket) {
    var ws = new WebSocket("ws://" + location.host+ "/realtime");

    ws.onopen = function() {
      console.log("open websocket.");
      //appendSubscribedChannel($channelName);
    };

    ws.onmessage = function (event) {
        console.log("client receives new message.");
        var message = event.data;
        var node = $("<div>"+message+"</div>");
        $("#eventstream").append(node);
    };

    ws.onclose = function() {
      console.log("close websocket.");
    };

    return ws;

  }
  else {
    alert("WebSocket not supported.");
    return null;
  }

}



$(document).ready(function(){

  var websocket = createWebSocket();

  function subHandler($data) {
    console.log($data);

    if ($data.status == "success") {
      var channelName = $data.channelName;
      var unsubButton = $("<input type='button' value='unsubscribe'/>");
      var channelDiv  = $("<div><span>"+channelName+"</span></div>");


      channelDiv.append(unsubButton);
      $("#channelList").append(channelDiv);

      // add click event on unsubscribe button
      unsubButton.click(function() {
        console.log("unsubscribe "+channelName);
        var self = this;

        $.post("/unsubscribe", {"func": "unsub", "channelName": channelName}, function($data) {
          if ($data.status == "success") {
            $(self).parent().remove();
          }
          else {
            alert("unsubscribe error.");
          }
        }, "json");

      });

    }
    else {
      alert("subscribe error.");
    }

  }


  // add subscribe event handler
  $("#subButton").click(function() {
    var channelName = $("#channelName").val();

    //$.post("/subscribe", {"func": "sub", "channelName": channelName}, subHandler, "json");
    //var message = '{"func": "subscribe", "channelName": "'+channelName+'"}';
    websocket.send(JSON.stringify({'func': 'subscribe', 'channelName':channelName}));
    // TODO: append unsubscribe button after server side success
    appendSubscribedChannel(channelName, websocket);
  })



});


