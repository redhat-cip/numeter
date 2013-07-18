// PROFILE
// UPDATE PROFILE
$(document).on('submit', '#profile-update-form', function() {
  var url = $(this).attr('action');
  $.ajax({
    type: 'POST', url: url, async: true,
    data: $('#profile-update-form').serialize(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('#profile-update-info').append(data);
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
      $('#profile-update-password-info').append(data);
    },
  });
  return false;
});

// GET MENU INDEX
$(document).on('click', '.ajax-tabs li a', function() {
  menu = $(this).attr('menu');
  $.ajax({type:'GET', url:'/configuration/'+menu, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('#'+menu+'-index').html(data);
    },
  });
});


// SEARCH IN LIST BY PRESS ENTER
$(document).on('keypress', '.q', function(e) {
  if (e.which == 13 && $(this).val().length ) {
    var url = $(this).attr('data-url');
    var into = $(this).attr('href');
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
$(document).on('click', '.get-page', function() {
  var url = $(this).attr('data-url');
  var into = $(this).attr('href');
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
    },
  });
  return false;
});

// USER MENU
$(document).on('click', '.sub-menu-tabs li a', function() {
  var url = $(this).attr('data-url');
  var into = $(this).attr('href');
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
    },
  });
});

// GET USER
$(document).on('click', '[class*="get-"]', function() {
  var url = $(this).attr('href');
  var into = $(this).parentsUntil('div').parent();
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
    },
  });
  return false;
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
  return false;
});

// FOR STORAGE
// GET MODEL INSTANCE
$(document).on('click', '.ajax-tabs-list li a', function() {
  model = $(this).parent().parent().parent().attr('model');
  id = $(this).attr('model-id');
  $.ajax({type:'GET', url:'/configuration/'+model+'/'+id, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('#'+menu+'-content').html(data);
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

// ENABLE UPDATE BUTTON
$(document).on('keypress', 'form div dd input', function() {
  var form = $(this).parentsUntil('form').parent();
  form.children('div').children('div').children('p').children('input[name="update"]').removeAttr('disabled');
  form.children('div').children('div').children('p').children('input[name="cancel"]').show(250);
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
      form.children('div').children('div').children('.message-container').append(data);
    },
  });
  return false;
});

// DELETE BUTTON
$(document).on('click', 'input[name="delete"]', function() {
  var url = $(this).attr('data-url');
  if ( $(this).attr('disabled') == '' ) { return false ; }
  $.ajax({
    type: 'POST', url: url, async: true,
    data: {'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val()},
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('#'+menu+'-form .fields').html(data);
      $('#'+menu+'-form div div p input').attr('disabled','');
    },
  });
  return false;
});

// BTN CREATE HOST
$(document).on('click', 'input[name="create-hosts"]', function() {
  var url = $(this).attr('data-url');
  alert(url)
  $.ajax({
    type: 'POST', url: url, async: true,
    data: {'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val()},
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('#'+menu+'-form .fields').html(data);
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
      $(into).append(data);
    },
  });
});
