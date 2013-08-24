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

// ABORT GRAPH PREVIEW
preview_requests = [];
var stop_preview = function() {
  $.each( preview_requests, function(i,xhr) {
    xhr.abort();
  });
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
  xhr = $.getJSON(url, function(data) {
    for (i in data['datas']){
      data['datas'][i][0] = new Date(data['datas'][i][0] * 1000);
    }
    g = new Dygraph(document.getElementById('preview-graph'), data['datas'], {
      labels: data['labels'],
      colors: data['colors'],
      pixelsPerLabel: 60,
      gridLineWidth: 0.1,
      labelsKMG2: true,
      height: 150,
      width: 300,
    });
  });
  preview_requests.push(xhr);
});
$(document).on('mouseout', "a:regex(class, preview-(source|view))", function() {
  $(this).popover('hide');
  $(this).popover('destroy');
  stop_preview();
});

// MOVE OPTIONS BETWEEN SELECT INPUT
$(document).on('click', '.move-option', function(e) {
  e.preventDefault();
  var from = $(this).attr('data-from');
  var to = $(this).attr('data-to');
  var html = $(from+' option:selected').detach();
  $(html).appendTo(to);
})

