// PROFILE
// UPDATE PROFILE
$(document).on('submit', '#profile-update-form', function() {
  var url = $(this).attr('action');
  $.ajax({
    type: 'POST', url: url, async: true,
	data: $('#profile-update-form').serialize(),
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
    success: function(data, status, xhr) {
      $('#'+menu+'-index').html(data);
    },
  });
});

// GET MODEL INSTANCE
$(document).on('click', '.ajax-tabs-list li a', function() {
  model = $(this).parent().parent().parent().attr('model');
  id = $(this).attr('model-id');
  $.ajax({type:'GET', url:'/configuration/'+model+'/'+id, async:true,
    success: function(data, status, xhr) {
      $('#'+menu+'-content').html(data);
    },
  });
});

// GET EMPTY FORM
$(document).on('click', '.ajax-tab-add', function (e) {
  var url = $(this).attr('url');
  $.ajax({type: 'GET', url: url, async: true,
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
    success: function(data, status, xhr) {
      form.children('div').children('div').children('.message-container').append(data);
    },
  });
  return false;
});
