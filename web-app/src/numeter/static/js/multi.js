// GLOBAL VARS
graphs = {};

// AJAX AND MAKE GRAPH
var get_graph = function(view_id, into) {
  last_view_id = view_id;
  last_into = into;
  var graph_div = '<div id="view-'+view_id+'-container" class="well"><div id="view-'+view_id+'" class="" style="text-align: left; width: 100%; height: 320px; position: relative;"></div><div id="graphleg-'+view_id+'"></div></div>';
  var res = $('#resolution-pills li.active').attr('data-value');

  $(into).append(graph_div);
  $.getJSON('/multiviews/get-data/'+view_id+'?res='+res, function(data) {

    // Make date
    for (var i in data['datas']){
      data['datas'][i][0] = new Date(data['datas'][i][0] * 1000);
    }

    g = new Dygraph(document.getElementById('view-'+view_id), data['datas'], {
      title: data['name'],
      legend: 'always',
      fillGraph: true,
      pixelsPerLabel: 60,
      gridLineWidth: 0.1,
      strokeWidth: 1.5,
      colors: data['colors'],
      showRangeSelector: true,
      highlightCircleSize: 4.0,
      labels: data['labels'],
      labelsKMG2: true,
      labelsSeparateLines: true,
      labelsDivWidth: 300,
      labelsDivStyles: {
        backgroundColor: 'rgba(200, 200, 200, 0.20)',
        borderRadius: '10px',
        padding: '4px',
      },
      axes: {
        y: {
          axisLabelWidth: 30000,
        }
      },
      series: {
        warning: {
          fillGraph: false,
          strokeWidth: 1.0,
          highlightCircleSize: 0.0,
        },
        critical: {
          fillGraph: false,
          strokeWidth: 1.0,
          highlightCircleSize: 0.0,
        },
      }
    });
    graphs[view_id] = [g,'/multiviews/get-data/'+view_id+'?res='];
  });
}

// GET VIEW
$(document).on('click', '.get-view', function() {
  var view_id = $(this).attr('data-id');
  $('#graphs').html('');
  graphs = {};
  get_graph(view_id, '#graphs');
});

// GET MULTIVIEW
$(document).on('click', '.get-multiview', function() {
  $('#graphs').html('');
  graphs = {};
  $(this).parent().children('ul').children('li').children('.get-view').each( function(index,value) {
    var view_id = $(this).attr('data-id');
    get_graph(view_id, '#graphs');
  })
});

// SET RESOLUTION
$(document).on('click', '#resolution-pills li a', function() {
  $('#resolution-pills li').removeClass('active');
  $(this).parent().addClass('active');
  res = $(this).parent().attr('data-value');
  // Walk on graphs for update
  $.each(graphs, function(view_id,v) {
    $.getJSON(graphs[view_id][1]+res, function(data) {
      for (j in data['datas']) {
        data['datas'][j][0] = new Date(data['datas'][j][0] * 1000);
      }
      graphs[view_id][0].updateOptions({file: data['datas']})
    });
  });
});
