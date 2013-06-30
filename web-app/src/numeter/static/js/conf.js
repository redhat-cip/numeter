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

// USER AND GROUPS
$(document).on('click', '.ajax-tabs li a', function() {
  model = $(this).attr('model');
  $.ajax({type:'GET', url:'/'+model, async:true,
    success: function(data, status, xhr) {
      $('#'+model+'-index').append(data);
    },
  });
});
