// MESSAGES
// BASIC FUNC
var print_message = function(msg,tag,into) {
  var html = '<div id="msg-'+tag+'" class="alert alert-'+tag+'" style="display: block;"><p class="pull-right"><button class="close" onclick="$(this).parent().parent().hide(250)">×</button></p><div>'+msg+'</div></div>';
  $(into).append(html);
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

// GET PLUGIN LIST FROM CATEGORY
$(document).on('click', '.accordion-category', function() {
  var category = $(this).parent().attr('category-name');
  var id = $(this).parentsUntil('.hosttree-host-li').parent().children('[host-id]').attr('host-id')
  var content = $(this).parent().children('div.category-content');

  if ( $(content).html() == "" ) {
    $.ajax({type:'GET', url:'/hosttree/category/'+id, async:true,
      data: {category: category },
      success: function(data, status, xhr) {
        $(content).html(data);
        $(content).show(250);
        $(content).parent().children('i').attr('class', 'icon-minus');
      }
    });
  } else {
    $(content).html('')
    $(content).hide(250);
	$(content).parent().children('i').attr('class', 'icon-plus');
  }
});

// GET PLUGIN
$(document).on('click', '.get-plugin', function() {
  var plugin = $(this).html();
  var host = $('.accordion-body a').attr('host-id');
  $.ajax({type:'GET', url:'/get/graph/'+host+'/'+plugin, async:true,
    success: function(data, status, xhr) {
       $('#graphs').html(data);
    }
  });
});

// MISC
// GET APROPOS
$(document).on('click', '[href="/apropos"]', function() {
  $.ajax({type:'GET', url:'/apropos', async:true,
    success: function(data, status, xhr) {
      $('#myModal').html(data);
    },
    complete: function() {
      $('#myModal').modal('toggle');
    },
  });
  return false;
});
