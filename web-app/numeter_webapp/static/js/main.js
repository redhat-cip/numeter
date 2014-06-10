$(document).ready(function () {
  $(".pretty-select").select2();
  // GET APROPOS
  $(document).on('click', '[href="/apropos"]', function () {
    $.ajax({
      type: 'GET',
      url: '/apropos',
      async: true,
      error: function (data, status, xhr) {
        numeter.error_modal();
      },
      success: function (data, status, xhr) {
        $('#myModal').html(data);
        $('#myModal').modal('show');
      }
    });
    return false;
  });

  // REGEX SELECTOR
  $.expr[':'].regex = function (elem, index, match) {
    var matchParams = match[3].split(','),
    validLabels = /^(data|css):/,
    attr = {
      method: matchParams[0].match(validLabels) ?
      matchParams[0].split(':')[0] : 'attr',
      property: matchParams.shift().replace(validLabels, '')
    },
    regexFlags = 'ig',
    regex = new RegExp(matchParams.join('').replace(/^\s+|\s+$/g, ''), regexFlags);
    return regex.test($(elem)[attr.method](attr.property));
  };

  // MULTIPLE CHECKBOX SELECT
  var lastChecked = null;

  $(document).on('click', 'tr td input[type="checkbox"]', function (e) {
    var $chkboxes = $('tr td input[type="checkbox"]');
    if (!lastChecked) {
      lastChecked = this;
      return;
    }
    if (e.shiftKey) {
      var start = $chkboxes.index(this);
      var end = $chkboxes.index(lastChecked);
      $chkboxes.slice(Math.min(start, end), Math.max(start, end) + 1).attr('checked', lastChecked.checked);
    }
    lastChecked = this;
  });

  // SHOW PREVIEW ON TOOLTIP
  $(document).on('mouseover', "a:regex(class, preview-(source|view))", function () {
    var pop = $(this);
    var url = $(this).attr('data-data-url');
    $(pop).popover({
      content: '<div id="preview-graph"></div>',
      html: true,
      trigger: 'manual',
      delay: {'show': 1000, 'hide': 250}
    });

    $(pop).popover('show');
    numeter.print_loading_gif('#preview-graph', 150, 150);
    numeter.get_simple_graph(url, '#preview-graph');
  });
  $(document).on('mouseout', "a:regex(class, preview-(source|view))", function () {
    $(this).popover('hide');
    $(this).popover('destroy');
    // Disable abort causing graph not display in multiview source edit and view edit
    //numeter.preview_request.abort();
  });

  // MOVE OPTIONS BETWEEN SELECT INPUT
  $(document).on('click', '.move-option', function (e) {
    e.preventDefault();
    var from = $(this).attr('data-from');
    var to = $(this).attr('data-to');
    var html = $(from + ' option:selected').detach();
    $(html).appendTo(to);
  });

  // SEARCH IN LIST BY PRESS ENTER
  $(document).on('keypress', '.q', function (e) {
    if (e.which === 13) {
      var th = $(this);
      var url = th.data('url');
      var into = th.data('into');
      var data = {q: th.val()};
      $.ajax({
        url: url,
        async: true,
        data: data,
        error: function (data, status, xhr) { numeter.error_modal(); },
        success: function (data, status, xhr) {
          $(into).html(data);
        }
      });
    }
  });

  $(document).on('keypress', '.q-opt', function(e) {
    if (e.which == 13 ) {
      e.preventDefault();
      var th = $(this)
      var form = th.closest('form');
      var url = th.data('url');
      var into = th.next();
      var chosen = form.find( th.data('chosen') );
      var exclude = $.map( chosen.children('option'), function(e) { return $(e).val(); });
      var data = { 'q' : th.val() };
      $.ajax({ url:url, async:true, data:data,
        error: function(data, status, xhr) { error_modal() },
        success: function(data) {
          $(into).empty();
          $(data['results']).each( function() {
            console.log(this)
            if ( $.inArray(this['id'].toString(), exclude) == -1 ) {
              var opt = '<option value="'+this['id']+'">'+this['fullname']+'</option>';
              $(into).append(opt);
            }
          });
        },
      });
    }

  });

  // SHOW MODAL
  $(document).on('click', '.use_modal', function(e) {
    e.preventDefault();
    var url = $(this).data('url');
    $.ajax({ url:url, async:true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data) {
        $('#myModal').html(data);
        $('#myModal').modal('show');
      },
    });
  });

  // SHOW PREVIEW ON TOOLTIP
  $(document).on('mouseover', "a:regex(class, preview-(source|view))", function() {
    var pop = $(this);
    var url = pop.data('data-url');
    pop.popover({
      content: '<div id="preview-graph"></div>',
      html: true,
      trigger: 'manual',
      delay: {'show':1000, 'hide':250},
    })
  
    pop.popover('show');
    numeter.print_loading_gif('#preview-graph', 150, 150);
    numeter.get_simple_graph(url, '#preview-graph');
  });
  $(document).on('mouseout', "a:regex(class, preview-(source|view))", function() {
    $(this).popover('hide');
    $(this).popover('destroy');
  });

  // AJAX BTN
  $(document).on('click', '.ajax-btn', function(e) {
    e.preventDefault();
    var btn = $(this)
    var url = btn.data('url');
    var method = btn.data('method');
    var name = btn.data('name');
    var data = {} 
    data[name] = $(btn.data('data')).val() || [];
    $.ajax({
      async: true,
      type: method,
      url: url,
      data: JSON.stringify(data),
      dataType: 'json',
      contentType: 'application/json; charset=utf-8',
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) { },
    });
  });

  // BULK
  $(document).on('click', '.bulk-action', function() {
    var btn = $(this);
    var use_modal = btn.data('use-modal')
    var option = $( btn.data('select') + ' option:selected');
    var url = option.data('url');
    var method = option.data('method');

    var checkbox_class = btn.data('checkbox-class');
    var ids = [];
    $(checkbox_class+':checked').each( function() {
       ids.push( $(this).attr('name') );
    });
    var data = {id: ids}
    $.ajax({
      type: method,
      url: url,
      data: JSON.stringify(data),
      dataType: 'json',
      contentType: 'application/json; charset=utf-8',
      async: true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        if ( use_modal == 'true' ) {
          $('#myModal').html(data);
          $('#myModal').modal('show');
        }
      }
    })
  })

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

});
