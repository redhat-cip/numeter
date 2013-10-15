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
  numeter.print_loading_gif(target, 250, 250);
  $.ajax({type:'GET', url: url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(target).html(data);
    },
  });
});

// CHOOSING SUB-MENU
$(document).on('shown', '.sub-menu-tabs li a', function() {
  var url = $(this).attr('data-url');
  var target = $(this).attr('data-target');
  $(target).empty();
  numeter.print_loading_gif(target, 250, 250);
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
  $(target).html('')
  numeter.print_loading_gif(target, 250, 250);
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
  var cur_tab_container = $(this).parentsUntil('.tab-pane').parent()
  var cur_tab = $(this).parentsUntil('.tab-pane').parent().attr('id')
  $.ajax({
    type: 'POST', url: url, async: true,
    data: $(form).serialize(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      // OK
      if ( data['response'] == 'ok' ) {
        $('.messages').append(data['html']);
        $('a[data-target="#'+cur_tab+'"]').parent().removeClass('active');
        numeter.print_loading_gif(cur_tab, 250, 250);
        // Reload form
        if ( data['callback-url'] ) {
          $.ajax({type:'GET', url:data['callback-url'], async:true,
            error: function(data, status, xhr) { error_modal() },
            success: function(data, status, xhr) {
              $(cur_tab_container).html(data);
            },
          });
        }
      } else if ( data['response'] == 'error' ) {
        $('.messages').append(data['html']);
      }
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

// BUTTON CHOOSE HOST FOR PLUGINS
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
