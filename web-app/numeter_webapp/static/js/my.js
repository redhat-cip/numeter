// REGEX SELECTOR
jQuery.expr[':'].regex = function(elem, index, match) {
  var matchParams = match[3].split(','),
  validLabels = /^(data|css):/,
  attr = {
    method: matchParams[0].match(validLabels) ? 
    matchParams[0].split(':')[0] : 'attr',
    property: matchParams.shift().replace(validLabels,'')
  },
  regexFlags = 'ig',
  regex = new RegExp(matchParams.join('').replace(/^\s+|\s+$/g,''), regexFlags);
  return regex.test(jQuery(elem)[attr.method](attr.property));
}

// MOVE OPTIONS BETWEEN SELECT INPUT
$(document).on('click', '.move-option', function(e) {
  e.preventDefault();
  var from = $(this).attr('data-from');
  var to = $(this).attr('data-to');
  var html = $(from+' option:selected').detach();
  $(html).appendTo(to);
})

$(document).ready(function () {
  // PROFILE
  // UPDATE PROFILE
  $(document).on('submit', '#profile-update-form', function(e) {
    e.preventDefault();
    var url = $(this).attr('action');
    $.ajax({
      type: 'POST', url: url, async: true,
      data: $('#profile-update-form').serialize(),
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $('.messages').append(data);
      },
    });
  });
  
  // UPDATE PASSWORD
  $(document).on('submit', '#profile-update-password-form', function(e) {
    e.preventDefault();
    var url = $(this).attr('action');
    $.ajax({
      type: 'POST', url: url, async: true,
      data: $('#profile-update-password-form').serialize(),
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $('.messages').append(data);
      },
    });
  });

});

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i])
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');
  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }
  $.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type)) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  })
