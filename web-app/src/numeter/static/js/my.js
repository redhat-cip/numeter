// MESSAGES
// BASIC FUNC
var print_message = function(msg,tag,into) {
  var html = '<div id="msg-'+tag+'" class="alert alert-block alert-'+tag+'"><a href="#" data-dismiss="alert" class="close">×</a><div>'+msg+'</div></div>';
  $(into).append(html);
}

var error_modal = function() {
  $('#myModal').modal('show');
  $('#myModal').html('<center><h4>Connection error !</h4></center>');
}

// ADD LOADING GIF
var print_loading_gif = function(into, heigth, width) {
  if(typeof(heigth)==='undefined') heigth = 100;
  if(typeof(width)==='undefined') width = 100;
  $(into).append('<img class="loader center" src="/static/img/ajax-loader.gif" height="'+heigth+'%" width="'+width+'%">' );
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
