graph_request = [];
res = 'Daily';
// ABORT GRAPH REQUEST
var stop_request = function() {
  $.each( graph_request, function(i,xhr) {
    if ( xhr.state() == 'rejected' ) { console; }
    else {
      xhr.abort();
      $(xhr).trigger('abort');
    }
  });
}


// HOST TREE
// GET HOSTS FROM GROUP
$('.accordion-body').on('shown', function() {
  var id = $(this).attr('group-id');
  $.ajax({type:'GET', url:'/hosttree/group/'+id, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
       $('#group-'+id).html(data);
    }
  });
});

// GET CATEGORIES FROM HOST
$(document).on('click', '.accordion-host', function() {
  var id = $(this).attr('host-id');

  if ( $('#host-'+id+'-content').html() == "" ) {
    $.ajax({type:'GET', url:'/hosttree/host/'+id, async:true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $('#host-'+id+'-content').html(data);
        $('#host-'+id+'-content').show(250);
        $('#host-'+id+'-content').parent().children('i').attr('class', 'icon-minus');
      }
    });
  } else {
    $('#host-'+id+'-content').html('')
    $('#host-'+id+'-content').hide(250);
    $('#host-'+id+'-content').parent().children('i').attr('class', 'icon-plus');
  }
});

// AJAX AND MAKE GRAPH
var get_graph = function(host, plugin, into) {
  var graph_div = '<div id="graph-'+plugin+'-container" class="well"><div id="graph-'+plugin+'" class="" style="text-align: left; width: 100%; height: 320px; position: relative;"></div><div id="graphleg-'+plugin+'"></div></div>';
  res = $('#resolution-pills li.active').attr('data-value');

  $(into).append(graph_div);
  var url = '/get/graph/'+host+'/'+plugin;
  Get_Graph(url, 'graph-'+plugin);
}

// GET PLUGIN LIST FROM CATEGORY
$(document).on('click', '.accordion-category', function() {
  var a = $(this)
  var category = $(this).parent().attr('category-name');
  var id = $(this).parentsUntil('.hosttree-host-li').parent().children('[host-id]').attr('host-id')
  var content = $(this).parent().children('div.category-content');

  stop_request();
  if (! $(this).hasClass('active') ) {
    $.ajax({type:'GET', url:'/hosttree/category/'+id, async:true,
      data: {category: category },
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $(content).html(data);
        $(content).show(250);
        $(content).parent().children('i').attr('class', 'icon-minus');

        $('#graphs').html('');
        a.toggleClass('active');
        graphs = [];
        $('.get-plugin').each( function(index,value) {
          var plugin = $(this).attr('plugin-name');
          var host = $(this).parentsUntil('.hosttree-host-li').parent().children('a').attr('host-id');
          get_graph(host, plugin, '#graphs');
        })
      }
    });
  } else {
    $(content).html('')
    $(content).hide(250);
    $(content).parent().children('i').attr('class', 'icon-plus');
    a.toggleClass('active');
  }
});

// GET PLUGIN
$(document).on('click', '.get-plugin', function() {
  var plugin = $(this).attr('plugin-name');
  var host = $(this).parent().parent().parent().parent().parent().parent().parent().children('.accordion-host').attr('host-id');
  $('#graphs').html('');
  stop_request();
  graphs = [];
  get_graph(host, plugin, '#graphs');
});

// SET RESOLUTION
$(document).on('click', '#resolution-pills li a', function() {
  $('#resolution-pills li').removeClass('active');
  $(this).parent().addClass('active');
  res = $(this).parent().attr('data-value');
  // Walk on graphs for update
  $.each(graphs, function(i,g) {
    Update_Graph(g);
  });
});
