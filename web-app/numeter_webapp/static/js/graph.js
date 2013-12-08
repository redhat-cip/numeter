/*global jQuery, console, window, document*/
(function ($, window, document) {
  'use strict';
  var stop_request, insert_graph,
    graph_request = [],
    numeter;
    // res = 'Daily';

  numeter = window.numeter = window.numeter || {};
  // ABORT GRAPH REQUEST  
  stop_request = function () {
    var i, xhr, length = graph_request.length;
    for (i = 0; i < length; i = i + 1) {
      xhr = graph_request[i];
      if (xhr.state() === 'rejected') {
        console.log('xhr request was rejected');
      } else {
        xhr.abort();
        $(xhr).trigger('abort');
      }
    }
  };


  // HOST TREE
  // GET HOSTS FROM GROUP
  $('.accordion-body').on('shown', function () {
    var id = $(this).attr('group-id');
    $.ajax({
      type: 'GET',
      url: '/hosttree/group/' + id,
      async: true,
      error: function () { numeter.error_modal(); },
      success: function (data) {
        $('#group-' + id).html(data);
      }
    });
  });

  // GET CATEGORIES FROM HOST
  $(document).on('click', '.hosttree-host-li', function () {
    var element = $(this),
      id = element.parent().data('host-id'),
      host_content = element.siblings('.content');

    if (!host_content.text().length) {
      $.ajax({
        type: 'GET',
        url: '/hosttree/host/' + id,
        async: true,
        error: function () { numeter.error_modal(); },
        success: function (data) {
          host_content.html(data);
          host_content.show(250);
        }
      });
    } else {
      host_content.hide(250);
      host_content.empty();
    }
    element.children('i').toggleClass('icon-minus icon-plus');
  });

  // AJAX AND MAKE GRAPH
  insert_graph = function (host, plugin, into) {
    var url = '/get/graph/' + host + '/' + plugin,
      resolution = $('#resolution-pills li.active').attr('data-value'),
      graph_div =
        $(document.createElement('div')).attr({
          'id': 'graph-' + plugin + '-container',
          'class': 'well row-fluid'
        });

    $(into).append(graph_div);

    graph_div.append([
      $(document.createElement('div'))
        .attr({
          id: 'graph-' + plugin,
          class: 'span9',
          style: 'height: 320px;'
        }),

      $(document.createElement('div'))
        .attr({
          id: 'graph-labels-' + plugin,
          class: 'span3',
        })
    ]);
    numeter.get_graph(url, 'graph-' + plugin, resolution);
  };

  // GET PLUGIN LIST FROM CATEGORY
  $(document).on('click', '.hosttree-category-li', function () {
    var element = $(this),
      category = element.parent().data('category-name'),
      id = element.closest('li[data-host-id]').data('hostId'),
      content = element.siblings('.content');

    stop_request();
    if (!element.hasClass('active')) {
      $.ajax({
        type: 'GET',
        url: '/hosttree/category/' + id,
        async: true,
        data: {category: category },
        error: function () { numeter.error_modal(); },
        success: function (data) {
          content.html(data);
          content.show(250);

          $('#graphs').empty();
          numeter.graphs = [];

          content.find('li').each(function () {
            var plugin = $(this).data('plugin-name');
            insert_graph(id, plugin, '#graphs');
          });
        }
      });
    } else {
      $(content).hide(250);
      $(content).empty();
    }
    element.children('i').toggleClass('icon-minus icon-plus');
    element.toggleClass('active');
  });

  // GET PLUGIN
  $(document).on('click', 'li[data-plugin-name]', function () {
    var plugin = $(this).data('plugin-name'),
      host = $(this).closest('li[data-host-id]').data('hostId');

    $('#graphs').html('');
    stop_request();
    numeter.graphs = [];
    insert_graph(host, plugin, '#graphs');
  });

}(jQuery, window, document));
