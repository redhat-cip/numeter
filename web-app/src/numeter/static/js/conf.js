// PROFILE
// UPDATE PROFILE
$(document).on('submit', '#profile-update-form', function() {
  var url = $(this).attr('action');
  $.ajax({
    type: 'POST', url: url, async: true,
	data: $('#profile-update-form').serialize(),
    success: function(data, status, xhr) {
      $('#profile-update-info').html(data);
    },
  });
  return false;
});

// UPDATE PASSWORD

// USER AND GROUPS
$(document).on('click', '.ajax-tabs li a', function() {
  model = $(this).attr('model');
  $.ajax({type:'GET', url:'/'+model, async:true,
    success: function(data, status, xhr) {
      $('#'+model+'-index').html(data);
    },
  });
});
