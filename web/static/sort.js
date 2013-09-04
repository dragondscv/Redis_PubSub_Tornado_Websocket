
function sortHandler(data) {
  $(".event_tbody").replaceWith(data);
}

$(document).ready(function(){
  $("#passed_events>thead td").addClass("sort_desc");

  $("#filter #host").change( function(e) {
    var host = $(this).val();
    $.get("/filter/host/"+host+"/html", sortHandler, "html");
  })

  $("#filter #age").bind('keypress', function(e) {
    if ((e.keyCode || e.which) == 13) {
      var age = $(this).val();
      $.get("/filter/age/"+age+"/html", sortHandler, "html");
    }
  });

  $("#filter #job_name").bind('keypress', function(e) {
    if ((e.keyCode || e.which) == 13) {
      var job_name = $(this).val();
      $.get("/filter/job_name/"+encodeURIComponent(job_name)+"/html", sortHandler, "html");
    }
  });

  $("#filter #status").change( function(e) {
    var status = $(this).val();
    $.get("/filter/status/"+status+"/html", sortHandler, "html");
  });


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
