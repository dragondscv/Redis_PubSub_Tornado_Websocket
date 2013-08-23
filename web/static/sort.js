
function sortHandler(data) {
  $("tbody").replaceWith(data);
}

$(document).ready(function(){
  $("#passed_events>thead td").addClass("sort_desc");

  $("thead>tr td").click(function() {
    var reverse = "False";

    if ($(this).hasClass("sort_asc")) {
      $(this).removeClass("sort_asc");
      $(this).addClass("sort_desc");
      reverse = "False";
    } else {
      $(this).removeClass("sort_desc");
      $(this).addClass("sort_asc");
      reverse = "True";
    }
    var field = $(this).attr('id');

    $.get("/"+field+"/"+reverse, sortHandler, "html");
  })

});
