// MESSAGES
// BASIC FUNC
var print_message = function(msg,tag,into) {
  var html = '<div id="msg-'+tag+'" class="alert alert-block alert-'+tag+'"><a href="#" data-dismiss="alert" class="close">×</a><div>'+msg+'</div></div>';
  $(into).append(html);
}

var error_modal = function() {
  $('#myModal').modal('show');
  $('#myModal').html('<center><h4>Connection error !</h4></center>');
}

// ADD LOADING GIF
var print_loading_gif = function(into, heigth, width) {
  if(typeof(heigth)==='undefined') heigth = 100;
  if(typeof(width)==='undefined') width = 100;
  $(into).append('<img class="loader" src="/static/img/ajax-loader.gif" height="'+heigth+'%" width="'+width+'%">' );
}
var remove_loading_gif = function(from) {
  $(from+ ' .loader').remove();
}


// MISC
// GET APROPOS
$(document).on('click', '[href="/apropos"]', function() {
  $.ajax({type:'GET', url:'/apropos', async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('#myModal').html(data);
      $('#myModal').modal('show');
    },
  });
  return false;
});
