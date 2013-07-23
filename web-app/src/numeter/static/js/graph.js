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
  var success = false;
  var graph_div = '<div id="graph-'+plugin+'-container" class="well"><div id="graph-'+plugin+'" class="" style="text-align: left; width: 100%; height: 320px; position: relative;"></div><div id="graphleg-'+plugin+'"></div></div>';
  var res = $('#resolution-pills li.active').attr('data-value');

  $(into).append(graph_div);
  $.getJSON('/get/graph/'+host+'/'+plugin+'?res='+res, function(data) {
    for (i in data){
      data[i][0] = new Date(data[i][0]);
    }
    g = new Dygraph(document.getElementById('graph-'+plugin), data, {
      title: plugin,
      labels: ['Date',plugin],
      legend: 'always',
      labelsSeparateLines: true,
      labelsDiv: 'graphleg-'+plugin,
      fillGraph: true,
      labelsDivWidth: 100,
      pixelsPerLabel: 60,
      gridLineWidth: 0.1,
      labelsKMG2: true,
      stackedGraph: true,
      axes: {
        y: {
          axisLabelWidth: 30000,
        }
      },
    });
  });
}

// GET PLUGIN LIST FROM CATEGORY
$(document).on('click', '.accordion-category', function() {
  var a = $(this)
  var category = $(this).parent().attr('category-name');
  var id = $(this).parentsUntil('.hosttree-host-li').parent().children('[host-id]').attr('host-id')
  var content = $(this).parent().children('div.category-content');

  if (! $(this).hasClass('active') ) {
    $.ajax({type:'GET', url:'/hosttree/category/'+id, async:true,
      data: {category: category },
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $(content).html(data);
        $(content).show(250);
        $(content).parent().children('i').attr('class', 'icon-minus');

        $('#graphs').html('');
        $('.get-plugin').each( function(index,value) {
          var plugin = $(this).attr('plugin-name');
          var host = $(this).parentsUntil('.hosttree-host-li').parent().children('a').attr('host-id');
          get_graph(host, plugin, '#graphs');
          a.toggleClass('active');
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
  var plugin = $(this).html();
  var host = $('.accordion-body a').attr('host-id');
  $('#graphs').html('');
  get_graph(host, plugin, '#graphs');
});

// SET RESOLUTION
$(document).on('click', '#resolution-pills li a', function() {
  $('#resolution-pills li').removeClass('active');
  $(this).parent().addClass('active');
});
