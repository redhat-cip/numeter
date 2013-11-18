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

// MULTIPLE CHECKBOX SELECT
var lastChecked = null;
$(document).on('click', 'tr td input[type="checkbox"]', function(e) {
  var $chkboxes = $('tr td input[type="checkbox"]');
  if (!lastChecked) {
    lastChecked = this;
    return;
  }
  if (e.shiftKey) {
    var start = $chkboxes.index(this);
    var end = $chkboxes.index(lastChecked);
    $chkboxes.slice(Math.min(start,end), Math.max(start,end)+ 1).attr('checked', lastChecked.checked);
  }
  lastChecked = this;
});

// SHOW PREVIEW ON TOOLTIP
$(document).on('mouseover', "a:regex(class, preview-(source|view))", function() {
  var pop = $(this);
  var url = $(this).attr('data-data-url');
  $(pop).popover({
    content: '<div id="preview-graph"></div>',
    html: true,
    trigger: 'manual',
    delay: {'show':1000, 'hide':250},
  })

  $(pop).popover('show');
  numeter.print_loading_gif('#preview-graph', 150, 150);
  numeter.get_simple_graph(url, 'preview-graph');
});
$(document).on('mouseout', "a:regex(class, preview-(source|view))", function() {
  $(this).popover('hide');
  $(this).popover('destroy');
  // preview_request.abort()
});

// MOVE OPTIONS BETWEEN SELECT INPUT
$(document).on('click', '.move-option', function(e) {
  e.preventDefault();
  var from = $(this).attr('data-from');
  var to = $(this).attr('data-to');
  var html = $(from+' option:selected').detach();
  $(html).appendTo(to);
})

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

$(document).on('keypress', '.q-opt', function(e) {
  if (e.which == 13 ) {
    e.preventDefault();
    var form = $(this).closest('form');
    var url = $(this).attr('data-url');
    var into = $(this).next();
    var chosen = $(form).find( $(this).attr('data-chosen') );
    var exclude = $.map( $(chosen).children('option'), function(e) { return $(e).val(); });
    var data = { 'q' : $(this).val() };
    $.ajax({ url:url, async:true, data:data,
      error: function(data, status, xhr) { error_modal() },
      success: function(data) {
        $(into).empty();
        $(data['results']).each( function() {
          if ( $.inArray(this['id'].toString(), exclude) == -1 ) {
            var opt = '<option value="'+this['id']+'">'+this['fullname']+'</option>';
            $(into).append(opt);
          }
        });
      },
    });
  }
});

$(document).ready(function () {
  // SHOW MODAL
  $(document).on('click', '.use_modal', function(e) {
    e.preventDefault();
    var url = $(this).attr('data-url');
    $.ajax({ url:url, async:true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data) {
        $('#myModal').html(data);
        $('#myModal').modal('show');
      },
    });
  });
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

  // AJAX BTN
  $(document).on('click', '.ajax-btn', function() {
    e.preventDefault();
    var btn = $(this)
    var url = btn.data('url');
    var method = btn.data('method');
    var next_tab = btn.data('next-tab');
    $.ajax({
      type: method, url: url, async: true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) { },
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
