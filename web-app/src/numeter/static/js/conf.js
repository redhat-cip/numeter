// PROFILE
// UPDATE PROFILE
$(document).on('submit', '#profile-update-form', function() {
  var url = $(this).attr('action');
  $.ajax({
    type: 'POST', url: url, async: true,
    data: $('#profile-update-form').serialize(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
    },
  });
  return false;
});

// UPDATE PASSWORD
$(document).on('submit', '#profile-update-password-form', function() {
  var url = $(this).attr('action');
  $.ajax({
    type: 'POST', url: url, async: true,
    data: $('#profile-update-password-form').serialize(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
    },
  });
  return false;
});

// GET MENU INDEX
$(document).on('shown', '.ajax-tabs li a', function(e) {
  e.target;
  var url = $(this).attr('data-url');
  var target = $(this).attr('data-target');
  $(target).empty();
  print_loading_gif(target, 50, 50);
  $.ajax({type:'GET', url: url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(target).html(data);
    },
  });
});


// SEARCH IN LIST BY PRESS ENTER
$(document).on('keypress', '.q', function(e) {
  if (e.which == 13 ) {
    var url = $(this).attr('data-url');
    var into = $(this).attr('data-into');
    var data = { q: $(this).val() };
    $.ajax({url:url, async:true, data:data,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $(into).html(data);
      },
    });
  }
});

// USER-LIST GET PAGE
// $(document).on('click', '.get-page', function() {
//   var url = $(this).attr('data-url');
//   var into = $(this).attr('href');
//   $.ajax({type:'GET', url:url, async:true,
//     error: function(data, status, xhr) { error_modal() },
//     success: function(data, status, xhr) {
//       $(into).html(data);
//     },
//   });
//   return false;
// });

// CHOOSING SUB-MENU
$(document).on('shown', '.sub-menu-tabs li a', function() {
  var url = $(this).attr('data-url');
  var target = $(this).attr('data-target');
  console.log(target);
  $(target).empty();
  print_loading_gif(target, 50, 50);
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(target).html(data);
    },
  });
});

// GET OBJECT
$(document).on('click', '[class*="get-"]', function() {
  var url = $(this).attr('data-url');
  var target = $(this).attr('data-into');
  var cur_tab = $(this).parentsUntil('.tab-pane').parent().attr('id')
  $('a[data-target="#'+cur_tab+'"]').parent().removeClass('active');
  print_loading_gif(target, 50, 50);
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(target).html(data);
    },
  });
});


// BACK TO LIST
$(document).on('click', 'input[type="button"][name="back"]', function() {
  var url = $(this).attr('data-url');
  var into = $(this).parentsUntil('.tab-pane').parent();
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
    },
  });
});

// GET EMPTY FORM
$(document).on('click', '.ajax-tab-add', function (e) {
  var url = $(this).attr('url');
  $.ajax({type: 'GET', url: url, async: true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('#'+menu+'-content').html(data);
    },
  });
  $(this).parent().tab('show');
  $(this).parent().addClass('active');
});

// SUBMIT FORM
$(document).on('submit', '.ajax-form', function() {
  var form = $(this);
  var url = $(this).attr('action');
  $.ajax({
    type: 'POST', url: url, async: true,
    data: $(form).serialize(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
    },
  });
  return false;
});

// DELETE BUTTON
$(document).on('click', 'input[name="delete"]', function() {
  var url = $(this).attr('data-url');
  var next_tab = $(this).attr('data-next-tab');
  $.ajax({
    type: 'POST', url: url, async: true,
    data: {'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val()},
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
      $(next_tab).tab('show');
    },
  });
  return false;
});

// BTN CREATE HOST
$(document).on('click', 'input[name="create-hosts"]', function() {
  var url = $(this).attr('data-url');
  $.ajax({
    type: 'POST', url: url, async: true,
    data: {'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val()},
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
    },
  });
  return false;
});

// BUTTON REPAIR HOSTS
$(document).on('click', '#repair-hosts', function() {
  var url = $(this).attr('data-url');
  var into = $(this).parent();
  $.ajax({
    type: 'POST', url: url, async: true,
    data: {'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val()},
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
    },
  });
});

// BTN GET PLUGINS
$(document).on('click', 'input[name="plugins"]', function() {
  if ( ! $('#host-data-container').html() ) {
    var url = $(this).attr('data-url');
    var into = $('#host-data-container');
    $.ajax({
      type: 'GET', url: url, async: true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $(into).html(data);
      },
    });
  } else {
    $('#host-data-container').toggle(250)
  }
});

// BUTTON CHOOSE NOST FOR PLUGINS
$(document).on('click', '#btn-choose-host', function() {
  var url = $(this).attr('data-url');
  $.ajax({
    type: 'GET', url: url, async: true,
    data: {'host_id': $('select[name="host_id"]').val()},
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('#myModal').html(data);
      $('#myModal').modal('show');
    },
  });
});
// BUTTON CREATE PLUGIN
$(document).on('click', '#btn-create-plugins', function() {
  var url = $(this).attr('data-url');
  $.ajax({
    type: 'POST', url: url, async: true,
    data: {
      'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
      'plugins': $('#chosen-plugins').val(),
      'host_id': $('select[name="host_id"]').val(),
    },
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
    },
  });
});

// BUTTON CHOOSE SOURCE
$(document).on('click', '#btn-choose-sources', function() {
  var url = $(this).attr('data-url');
  $.ajax({
    type: 'GET', url: url, async: true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('#myModal').html(data);
      $('#myModal').modal('show');
    },
  });
});
// BUTTON CREATE SOURCE
$(document).on('click', '#btn-create-sources', function() {
  var url = $(this).attr('data-url');
  $.ajax({
    type: 'POST', url: url, async: true,
    data: { 
      'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
      'sources': $('#chosen-sources').val()
    },
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
    },
  });
});

// SHOW PREVIEW ON TOOLTIP
$(document).on('mouseover', "a:regex('class,get-(source|view)')", function() {
  var pop = $(this);
  var url = $(this).attr('data-data-url');
  $(pop).popover({
    content: '<div id="preview-graph"></div>',
    html: true,
    trigger: 'manual',
    delay: {'show':1000, 'hide':250},
  })

  $(pop).popover('show');
  print_loading_gif('#preview-graph', 40, 40);
  $.getJSON(url, function(data) {
    for (i in data['datas']){
      data['datas'][i][0] = new Date(data['datas'][i][0] * 1000);
    }
    g = new Dygraph(document.getElementById('preview-graph'), data['datas'], {
      labels: data['labels'],
      colors: data['colors'],
      pixelsPerLabel: 60,
      gridLineWidth: 0.1,
      labelsKMG2: true,
      height: 150,
      width: 300,
    });
  });
});
$(document).on('mouseout', "a:regex('class,get-(source|view)')", function() {
  $(this).popover('hide');
  $(this).popover('destroy');
});

// USE BULK ACTION
$(document).on('click', '.bulk-action', function() {
  var action_element_id = $(this).attr('data-action-element');
  var checkboxes_class = $(this).attr('data-checkboxes');
  var action = $(action_element_id).val();
  var url = $(action_element_id+' option:selected').attr('data-url');
  var method = $(action_element_id+' option:selected').attr('data-method') || 'POST';
  var ids = [];
  $(checkboxes_class+':checked').each( function() {
    ids.push( $(this).attr('name') );
  });
  $.ajax({
    type: method, url: url, async: true,
    data: { 
      'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
      'ids': ids
    },
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      if ( action == 'delete' ) {
        $('.messages').append(data['html']);
        $(checkboxes_class+':checked').parent().parent().hide(250);
        $(checkboxes_class+':checked').parent().parent().remove();
      } else if ( action == 'add-to-view' ) {
        $('#myModal').html(data);
        $('#myModal').modal('show');
      }
    },
  });
});

// BTN ADD SOURCE TO VIEW
$(document).on('click', '#btn-add-sources-to-view', function() {
  var url = $(this).attr('data-url');
  var view_id = $('#chosen-view').val()
  var ids = [];
  $('.source-to-add-checkbox:checked').each( function() {
    ids.push( $(this).attr('name') );
  });
  $.ajax({
    type: 'POST', url: url, async: true,
    data: { 
      'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
      'view_id': view_id,
      'source_ids': ids
    },
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data['html']);
    },
  });
})
