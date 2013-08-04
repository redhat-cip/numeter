// GLOBAL VARS
graphs = {};

// AJAX AND MAKE GRAPH
var get_graph = function(view_id, into) {
  last_view_id = view_id;
  last_into = into;
  var graph_div = '<div id="view-'+view_id+'-container" class="well" data-view-id='+view_id+'><div id="view-'+view_id+'" class="" style="text-align: left; width: 100%; height: 320px; position: relative;"></div><div id="graphleg-'+view_id+'"></div></div>';
  res = $('#resolution-pills li.active').attr('data-value');

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

//// CUSTOMIZE MENU
// TOGGLE MENU
$(document).on('click', '#toggle-editor', function() {
  if (! $(this).parent().hasClass('active') ) {
    $('#multiview-index').empty();
    print_loading_gif('#multiview-index');
    var url = $(this).attr('data-url');
    $('#multiview-index').show(300);
    $.ajax({type:'GET', url:url, async:true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $('#multiview-index').html(data);
      },
    });
    $(this).parent().addClass('active');
  } else {
    $('#multiview-index').hide(300);
    $(this).parent().removeClass('active');
    $('#multiview-index').empty();
  }
});
//
// SHOW PREVIEW ON TOOLTIP
$(document).on('mouseover', ".addable-source", function() {
  var pop = $(this);
  var url = $(this).attr('data-data-url');
  $(pop).popover({
    content: '<div id="preview-graph"></div>',
    html: true,
    trigger: 'manual',
    delay: {'show':1000, 'hide':250},
  })

  $(pop).popover('show');
  print_loading_gif('#preview-graph', 40, 40);
  $.getJSON(url, function(data) {
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
});
$(document).on('mouseout', ".addable-source", function() {
  $(this).popover('hide');
  $(this).popover('destroy');
});

// ADDING SOURCE MODE
$(document).on('click', ".addable-source", function() {
  $(this).toggleClass('to-add');
});
$(document).on('click', "#graphs div", function() {
  if ( $('.to-add').size() && $(this).attr('data-view-id') ) {
    var view_id = $(this).attr('data-view-id');
    var url = "customize/view/"+view_id+"/add_source";
    var source_ids = [];
    $.each( $('.to-add'), function() { source_ids.push($(this).attr('source-id')) } ); 
    $.ajax({type:'POST', url:url, async:true,
      data: {
	'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
	'source_ids': source_ids,
      },
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $('.messages').append(data);
	var url = graphs[view_id][1]+res;
        $.getJSON(url, function(data) {
	  graphs[view_id][0].updateOptions({
	    file: data['datas'],
	    labels: data['labels'],
	    colors: data['colors'],
	  });
	});
      },
    });

  }
});
