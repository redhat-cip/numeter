// GLOBAL VARS
cancelable_request = [];
res = 'Daily';

// ABORT GRAPH PREVIEW
var stop_request = function() {
  $.each( cancelable_request, function(i,xhr) {
    xhr.abort();
  });
}

// SEARCH MULTIVIEW
$(document).on('submit', '#main-q', function(e) {
  e.preventDefault();
  var url = $(this).attr('action');
  var into = $(this).attr('data-into');
  var data = { q: $(this).children('input').val() };
  $(into).empty();
  print_loading_gif(into, '25%', '25%')
  $.ajax({url:url, async:true, data:data,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
    },
  });
});

// GET MULTIVIEW
$(document).on('shown', '.collapse', function() {
  $(this).children('div.accordion-inner').find('.graph').each( function(index,value) {
    var view_id = $(this).attr('data-id');
    var view_div = $(this).attr('id');
    var data_url = $(this).attr('data-url');
    if ( $('#'+view_div).html() == '' ) print_loading_gif(this, '200px', '200px');
    graphs = [];
    Get_Graph(data_url, view_div);
  })
});

// SET RESOLUTION
$(document).on('click', '#resolution-pills li a', function() {
  $('#resolution-pills li').removeClass('active');
  $(this).parent().addClass('active');
  res = $(this).parent().attr('data-value');
  // Walk on graphs for update
  $.each(graphs, function(i,g) {
    Update_Graph(g);
  });
});

//// CUSTOMIZE MENU
// TOGGLE MENU
$(document).on('click', '#toggle-editor', function() {
  if (! $(this).parent().hasClass('active') ) {
    $('#multiview-index').empty();
    print_loading_gif('#multiview-index', '200px', '200px');
    var url = $(this).attr('data-url');
    $('#multiview-index').show(300);
    $.ajax({type:'GET', url:url, async:true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $('#multiview-index').html(data);
	source_mode = 'normal';
      },
    });
    $(this).parent().addClass('active');
    $(".btn-add-multiview").show(250);
    $(".btn-add-view").show();
  } else {
    $('#multiview-index').hide(300);
    $(this).parent().removeClass('active');
    $('#multiview-index').empty();
    $(".btn-add-multiview").hide(250);
    $(".btn-add-view").hide();
  }
});
//

// MENU TABS
$(document).on('click', '.ajax-tabs li a', function(e) {
  var url = $(this).attr('data-url');
  var target = $(this).attr('data-target');
  $(this).tab('show');
  // DONT AJAX IF ALREADY
  if ( $(target).html() != '' ) return false;
  print_loading_gif(target, 250, 250);
  $.ajax({type:'GET', url: url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(target).html(data);
    },
  });
});

// CHOOSING SUB-MENU
$(document).on('click', '.sub-menu-tabs li a', function() {
  var url = $(this).attr('data-url');
  var target = $(this).attr('data-target');
  $(this).tab('show');
  // DONT AJAX IF ALREADY
  if ( $(target).html() != '' ) return false;
  print_loading_gif(target, 250, 250);
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(target).html(data);
    },
  });
});


// GET PAGE
$(document).on('click', '.get-page', function() {
  var url = $(this).attr('data-url');
  var into = $(this).attr('data-into');
  //var into = $(this).parentsUntil('div').parent();
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
    },
  });
  return false;
});

// EDIT SOURCE
$(document).on('click', ".edit-source", function() {
  if ( source_mode == 'normal' ) {
    var url = $(this).attr('data-url');
    var data_url = $(this).attr('data-data-url');
    var into = $(this).attr('data-into');
    var name = $(this).attr('data-name');
    // GET FORM
    print_loading_gif(into, '25%', '25%');
    $.ajax({type:'GET', url:url, async:true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $(into).html(data);
        $("#edit-source-tab a").html(name)
        $("#edit-source-tab a").tab('show');
        $("#edit-source-tab a").show(250);
        // ADD PREVIEW
        print_loading_gif('#source-preview', '10%', '10%');
        Get_Simple_Graph(data_url, 'source-preview');
      },
    });
  }
});
// ADD/UPDATE SOURCE
$(document).on('submit', "#source-form", function() {
    var url = $(this).attr('action');
    var form = $(this);
    var method = $(this).attr('method');
    $.ajax({type:method, url:url, async:true,
      data: $(this).serialize(),
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $('.messages').append(data['html']);
      },
    });
    return false;
});

// EDIT VIEW
$(document).on('click', ".edit-view", function() {
  // SET VARS
  var url = $(this).attr('data-url');
  var data_url = $(this).attr('data-data-url');
  var into = $(this).attr('data-into');
  var name = $(this).attr('data-name');
  var view_id = $(this).attr('data-id');
  // RENDER
  $(into).empty();
  $("#edit-view-tab a").html(name);
  $("#edit-view-tab a").show(250);
  print_loading_gif(into, '25%', '25%');
  $("#edit-view-tab a").tab('show');
  // GET FORM
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
      // ADD PREVIEW
      print_loading_gif('#view-preview', '10%', '10%');
      Get_Simple_Graph(data_url, 'view-preview');
    },
  });
});

// ADD OR UPDATE VIEW
$(document).on('submit', ".view-form", function() {
  // SET VARS
  var url = $(this).attr('action');
  var data_url = $(this).attr('data-data-url');
  var method = $(this).attr('method');
  var form = $(this);
  var name = $(this).find('input[name="name"]').val();
  var into = '#edit-view-content';
  // RENDER
  $("#edit-view-tab a").html(name);
  $("#edit-view-tab a").show(250);
  $("#edit-view-tab a").tab('show');
  // POST FORM
  $.ajax({type:method, url:url, async:true,
    data: $(form).serialize(),
    error: function(data, status, xhr) { error_modal(data) },
    success: function(data, status, xhr) {
      $('.messages').append(data['html']);
      // IF FORM IS VALIDATE
      if ( data['response'] == 'ok' ) {
        var view_id = data['id'];
        var url = 'customize/view/'+view_id;
        $(into).empty();
        print_loading_gif(into, '25%', '25%');
        $.ajax({type:'GET', url:url, async:true,
          error: function(data, status, xhr) { error_modal(data) },
          success: function(data, status, xhr) {
            $(into).html(data);
            // ADD PREVIEW
            print_loading_gif('#view-preview', '10%', '10%');
            data_url = data_url || '/multiviews/view/'+view_id+'/data';
            Get_Simple_Graph(data_url, 'view-preview');
          },
        });
      } 
    },
  });
  return false;
});
// DELETE VIEWS
$(document).on('click', "#btn-delete-view", function(e) {
  e.preventDefault();
  // SET VARS
  var url = $(this).attr('data-url');
  var into = $(this).attr('data-into');
  var id = $(this).attr('data-id');
  // SET RENDER
  $("#edit-view-tab a").hide(250);
  $("#list-view-tab a").tab('show');
  $('.get-view[data-id="'+id+'"]').hide(250);
  // SEND DEL REQUEST
  $.ajax({type:'POST', url:url, async:true,
    data: $(this).serialize()+'csrfmiddlewaretoken='+$('[name="csrfmiddlewaretoken"]').val(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
      // HIDE CURRENT MULTIVIEW
      $("#list-view-content .q").trigger({
        type: "keypress",
        which: 13,
        KeyCode: 13,
      });
    },
  });
});

//// MULTIVIEW
// EDIT MULTIVIEW
$(document).on('click', ".edit-multiview", function() {
  // SET VARS
  var url = $(this).attr('data-url');
  var data_url = $(this).attr('data-data-url');
  var into = $(this).attr('data-into');
  var name = $(this).attr('data-name');
  // RENDER
  $(into).empty();
  $("#edit-multiview-tab a").html(name)
  $("#edit-multiview-tab a").show(250);
  print_loading_gif(into, 60, 60);
  $("#edit-multiview-tab a").tab('show');
  // GET FORM
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
    },
  });
});

// ADD OR UPDATE MULTIVIEW
$(document).on('submit', ".multiview-form", function(e) {
  e.preventDefault();
  var url = $(this).attr('action');
  var form = $(this);
  var method = $(this).attr('method');
  var name = $(this).find('input[name="name"]').val();
  var into = '#edit-multiview-content';
  // RENDER
  $("#edit-multiview-tab a").html(name);
  $("#edit-multiview-tab a").show(250);
  $("#edit-multiview-tab a").tab('show');
  // POST FORM
  $.ajax({type:'POST', url:url, async:true,
    data: $(form).serialize(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data['html']);
      // IF FORM IS VALIDATE
      if ( data['response'] == 'ok' ) {
        var multiview_id = data['id'];
        var url = 'customize/multiview/'+multiview_id;
        $(into).empty();
        print_loading_gif(into, '25%', '25%');
        $.ajax({type:'GET', url:url, async:true,
          error: function(data, status, xhr) { error_modal() },
          success: function(data, status, xhr) {
            $(into).html(data);
          },
        });
      }
    },
  });
  return false;
});
// DELETE MULTIVIEWS
$(document).on('click', "#btn-delete-multiview", function(e) {
  e.preventDefault();
  // SET VARS
  var url = $(this).attr('data-url');
  var into = $(this).attr('data-into');
  var id = $(this).attr('data-id');
  // SET RENDER
  $("#edit-multiview-tab a").hide(250);
  $("#list-multiview-tab a").tab('show');
  $('.get-multiview[data-id="'+id+'"]').hide(250);
  // SEND DEL REQUEST
  $.ajax({type:'POST', url:url, async:true,
    data: $(this).serialize()+'csrfmiddlewaretoken='+$('[name="csrfmiddlewaretoken"]').val(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
      // HIDE CURRENT MULTIVIEW
      $("#list-multiview-content .q").trigger({
        type: "keypress",
        which: 13,
        KeyCode: 13,
      });
    },
  });
});

//// EVENT
// EDIT EVENT
$(document).on('click', ".edit-event", function() {
  // SET VARS
  var url = $(this).attr('data-url');
  var data_url = $(this).attr('data-data-url');
  var into = $(this).attr('data-into');
  var name = $(this).attr('data-name');
  // RENDER
  $(into).empty();
  $("#edit-event-tab a").html(name)
  $("#edit-event-tab a").show(250);
  print_loading_gif(into, 60, 60);
  $("#edit-event-tab a").tab('show');
  // GET FORM
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
    },
  });
});

// ADD OR UPDATE EVENT
$(document).on('submit', ".event-form", function(e) {
  e.preventDefault();
  var url = $(this).attr('action');
  var form = $(this);
  var method = $(this).attr('method');
  var name = $(this).find('input[name="name"]').val();
  var into = '#edit-event-content';
  // RENDER
  $("#edit-event-tab a").html(name);
  $("#edit-event-tab a").show(250);
  $("#edit-event-tab a").tab('show');
  // POST FORM
  $.ajax({type:'POST', url:url, async:true,
    data: $(form).serialize(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data['html']);
      // IF FORM IS VALIDATE
      if ( data['response'] == 'ok' ) {
        var event_id = data['id'];
        var url = 'customize/event/'+event_id;
        $(into).empty();
        print_loading_gif(into, '25%', '25%');
        $.ajax({type:'GET', url:url, async:true,
          error: function(data, status, xhr) { error_modal() },
          success: function(data, status, xhr) {
            $(into).html(data);
          },
        });
      }
    },
  });
  return false;
});
// DELETE EVENT
$(document).on('click', "#btn-delete-event", function(e) {
  e.preventDefault();
  // SET VARS
  var url = $(this).attr('data-url');
  var into = $(this).attr('data-into');
  var id = $(this).attr('data-id');
  // SET RENDER
  $("#edit-event-tab a").hide(250);
  $("#list-event-tab a").tab('show');
  $('.get-event[data-id="'+id+'"]').hide(250);
  // SEND DEL REQUEST
  $.ajax({type:'POST', url:url, async:true,
    data: $(this).serialize()+'csrfmiddlewaretoken='+$('[name="csrfmiddlewaretoken"]').val(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
      // HIDE CURRENT MULTIVIEW
      $("#list-event-content .q").trigger({
        type: "keypress",
        which: 13,
        KeyCode: 13,
      });
    },
  });
});

//// SOURCE FAST ADD
// CHOOSE HOST
$(document).on('change', '#chosen-host', function() {
  stop_request();
  var host_id = $(this).val();
  var url = $(this).attr('data-url');
  $('#chosen-plugin').empty();
  $('#chosen-sources').empty();
  $('#btn-add-sources').parent().hide(250);
  r = $.ajax({type:'GET', url:url, async:true,
    data: 'host='+host_id,
    success: function(data, status, xhr) {
      $('#chosen-plugin').parent().show(250);
      $.each(data, function(k, v) {
        $('#chosen-plugin').append('<option value="'+k+'">'+k+'</option>')
      })
    }
  });
  cancelable_request.push(r);
})
// CHOOSE PLUGIN
$(document).on('change', '#chosen-plugin', function() {
  stop_request();
  var host_id = $('#chosen-host').val();
  var plugin = $('#chosen-plugin').val();
  var url = $(this).attr('data-url');
  $('#chosen-sources').empty();
  $('#btn-add-sources').parent().hide(250);
  r = $.ajax({type:'GET', url:url, async:true,
    data: {
      host: host_id,
      plugin: plugin,
    },
    success: function(data, status, xhr) {
      $('#chosen-sources').parent().show(250);
      $.each(data, function(i, v) {
        $('#chosen-sources').append('<option value="'+v+'">'+v+'</option>')
      })
    }
  });
  cancelable_request.push(r);
})
// CHOOSE SOURCES
$(document).on('change', '#chosen-sources', function() {
  $('#btn-add-sources').parent().show(250);
})
// ADD SOURCES
$(document).on('click', '#btn-add-sources', function() {
  var data = {
    host: $('#chosen-host').val(),
    plugin: $('#chosen-plugin').val(),
    sources: $('#chosen-sources').val(),
    csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val()
  }
  var url = $(this).attr('data-url');
  $.ajax({type:'POST', url:url, async:true,
    data: data,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').html(data);
    }
  });
})
