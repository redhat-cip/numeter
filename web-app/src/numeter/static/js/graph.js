graphs = {};
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
  r = $.getJSON('/get/graph/'+host+'/'+plugin+'?res='+res, function(data) {
    for (i in data['datas']){
      data['datas'][i][0] = new Date(data['datas'][i][0] * 1000);
    }
    g = new Dygraph(document.getElementById('graph-'+plugin), data['datas'], {
      title: data['name'],
      labels: data['labels'],
      legend: 'always',
      labelsSeparateLines: true,
      labelsDiv: 'graphleg-'+plugin,
      fillGraph: true,
      labelsDivWidth: 100,
      pixelsPerLabel: 60,
      gridLineWidth: 0.1,
      labelsKMG2: true,
      showRangeSelector: true,
      axes: {
        y: {
          axisLabelWidth: 30000,
        }
      },
    });
    graphs[host+plugin] = [g,'/get/graph/'+host+'/'+plugin+'?res='];
  });
  $(r).bind('abort', function () {
    if (r.state() == 'pending') $('#graph-'+plugin+'-container').hide(250);
  });
  graph_request.push(r);
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
  get_graph(host, plugin, '#graphs');
});

// SET RESOLUTION
$(document).on('click', '#resolution-pills li a', function() {
  $('#resolution-pills li').removeClass('active');
  $(this).parent().addClass('active');
  res = $(this).parent().attr('data-value');
  // Walk on graphs for update
  stop_request();
  $.each(graphs, function(view_id,v) {
    var r = $.getJSON(graphs[view_id][1]+res, function(data) {
      for (j in data['datas']) {
        data['datas'][j][0] = new Date(data['datas'][j][0] * 1000);
      }
      graphs[view_id][0].updateOptions({
        file: data['datas'],
        labels: data['labels'],
        colors: data['colors'],
      });
    });
    $(r).bind('abort', function () { 
      if (r.state() == 'pending') $('#graph-'+plugin+'-container').hide(250);
    });
    graph_request.push(r);
  });
});
