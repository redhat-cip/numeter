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

// STORAGE
$(document).on('click', '.ajax-tabs li a', function() {
});
