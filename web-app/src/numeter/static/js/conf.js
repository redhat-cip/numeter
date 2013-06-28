$(document).on('click', '.ajax-tabs li a', function() {
  model = $(this).attr('model');
  $.ajax({type:'GET', url:'/'+model+, async:true,
    success: function(data, status, xhr) {
      $('#'+model+'-index').html(data);
    },
  });
});
