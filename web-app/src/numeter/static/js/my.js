// MESSAGES
// BASIC FUNC
var print_message = function(msg,tag,into) {
  var html = '<div id="msg-'+tag+'" class="alert alert-'+tag+'" style="display: block;"><p class="pull-right"><button class="close" onclick="$(this).parent().parent().hide(250)">×</button></p><div>'+msg+'</div></div>';
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

// HOST TREE
// GET HOSTS FROM GROUP
$('.accordion-body').on('shown', function() {
  var id = $(this).attr('group-id');
  $.ajax({type:'GET', url:'/hosttree/group/'+id, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
       $('#group-'+id).html(data);
    }
  });
});

// GET CATEGORIES FROM HOST
$(document).on('click', '.accordion-host', function() {
  var id = $(this).attr('host-id');

  if ( $('#host-'+id+'-content').html() == "" ) {
    $.ajax({type:'GET', url:'/hosttree/host/'+id, async:true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $('#host-'+id+'-content').html(data);
        $('#host-'+id+'-content').show(250);
        $('#host-'+id+'-content').parent().children('i').attr('class', 'icon-minus');
      }
    });
  } else {
    $('#host-'+id+'-content').html('')
    $('#host-'+id+'-content').hide(250);
    $('#host-'+id+'-content').parent().children('i').attr('class', 'icon-plus');
  }
});


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
