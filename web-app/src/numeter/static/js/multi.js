// AJAX AND MAKE GRAPH
var get_graph = function(view_id, into) {
  var graph_div = '<div id="view-'+view_id+'-container" class="well"><div id="view-'+view_id+'" class="" style="text-align: left; width: 100%; height: 320px; position: relative;"></div><div id="graphleg-'+view_id+'"></div></div>';
  var res = $('#resolution-pills li.active').attr('data-value');

  $(into).append(graph_div);
  $.getJSON('/multiviews/get-data/'+view_id+'?res='+res, function(data) {

    for (i in data['datas']){
      data['datas'][i][0] = new Date(data['datas'][i][0]);
    }

    g = new Dygraph(document.getElementById('view-'+view_id), data['datas'], {
      title: data['name'],
      labels: data['labels'],
      legend: 'always',
      labelsSeparateLines: true,
      labelsDiv: 'graphleg-'+view_id,
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

// GET VIEW
$(document).on('click', '.get-view', function() {
  var view_id = $(this).attr('data-id');
  $('#graphs').html('');
  get_graph(view_id, '#graphs');
});

// GET MULTIVIEW
$(document).on('click', '.get-multiview', function() {
  $('#graphs').html('');
  $('ul').children('.get-view').each( function(index,value) {
    alert(1);
    var view_id = $(this).attr('data-id');
    get_graph(view_id, '#graphs');
  })
});
