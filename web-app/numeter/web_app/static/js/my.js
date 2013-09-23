// MESSAGES
// BASIC FUNC
var print_message = function(msg,tag,into) {
  var html = '<div id="msg-'+tag+'" class="alert alert-block alert-'+tag+'"><a href="#" data-dismiss="alert" class="close">×</a><div>'+msg+'</div></div>';
  $(into).append(html);
}

var error_modal = function(err) {
  $('#myModal').modal('show');
  $('#myModal').html('<center><h4>Connection error !</h4></center>');
  //if ( err ) {
    $('#myModal').append('<div class="span"><pre>'+err+'</pre></div>');
  //}
}

// ADD LOADING GIF
var print_loading_gif = function(into, heigth, width) {
  if(typeof(heigth)==='undefined') heigth = '100%';
  if(typeof(width)==='undefined') width = '100%';
  $(into).append('<div class="loader" style="text-align:center;"><img src="/static/img/ajax-loader.gif" height="'+heigth+'" width="'+width+'">' );
}
var remove_loading_gif = function(from) {
  $(from+ ' .loader').remove();
}


// MISC
// GET APROPOS
$(document).on('click', '[href="/apropos"]', function() {
  $.ajax({type:'GET', url:'/apropos', async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('#myModal').html(data);
      $('#myModal').modal('show');
    },
  });
  return false;
});

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
  print_loading_gif('#preview-graph', 150, 150);
  Get_Simple_Graph(url, 'preview-graph');
});
$(document).on('mouseout', "a:regex(class, preview-(source|view))", function() {
  $(this).popover('hide');
  $(this).popover('destroy');
  preview_request.abort()
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
    var url = $(this).attr('data-url');
    var into = $(this).attr('data-into');
    var chosen = $(this).attr('data-chosen')
    var exclude = $.map( $(chosen+' option'), function(e) { return $(e).val(); });
    var data = { 'name__icontains' : $(this).val() };
    $.ajax({ url:url, async:true, data:data,
      error: function(data, status, xhr) { error_modal() },
      success: function(data) {
        $(into).empty();
        $(data['objects']).each( function() {
          if ( $.inArray(this['id'].toString(), exclude) == -1 ) {
            var opt = '<option value="'+this['id']+'">'+this['fullname']+'</option>';
            $(into).append(opt);
          }
        });
      },
    });
  }
});
