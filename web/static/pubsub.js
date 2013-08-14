$(document).ready(function(){

  function createWebSocket() {
    if (WebSocket) {
      var ws = new WebSocket("ws://" + location.host+ "/realtime");

      ws.onopen = function() {
        console.log("open websocket.");
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
    }
    else {
      alert("WebSocket not supported.");
    }
  }

  // create web socket after page is loaded
  createWebSocket();

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

    $.post("/subscribe", {"func": "sub", "channelName": channelName}, subHandler, "json");
  })



});

