// GLOBAL VARS
graphs = {};
cancelable_request = [];
res = 'Daily';

// ABORT GRAPH PREVIEW
var stop_request = function() {
  $.each( cancelable_request, function(i,xhr) {
    xhr.abort();
  });
}

// AJAX AND MAKE GRAPH
var get_graph = function(view_id, into) {

  $.getJSON('/multiviews/view/'+view_id+'/data?res='+res, function(data) {

    // Compute width
    var width = $('.collapse').css('width').replace('px','') / 2 - 50
    // Make date
    for (var i in data['datas']){
      data['datas'][i][0] = new Date(data['datas'][i][0] * 1000);
    }

    g = new Dygraph(document.getElementById(into), data['datas'], {
      title: data['name'],
      height: 250,
      width: width,
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
    graphs[view_id] = [g,'/multiviews/view/'+view_id+'/data?res='];
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
$(document).on('shown', '.collapse', function() {
  graphs = {};
  $(this).children('div.accordion-inner').children('.graph').each( function(index,value) {
    var view_id = $(this).attr('data-id');
    var view_div = $(this).attr('id');
    print_loading_gif(this, '200px', '200px');
    get_graph(view_id, view_div);
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
      graphs[view_id][0].updateOptions({
        file: data['datas'],
        labels: data['labels'],
        colors: data['colors'],
      });
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
	source_mode = 'normal';
      },
    });
    $(this).parent().addClass('active');
    $(".btn-add-multiview").show(250);
    $(".btn-add-view").show();
  } else {
    $('#multiview-index').hide(300);
    $(this).parent().removeClass('active');
    $('#multiview-index').empty();
    $(".btn-add-multiview").hide(250);
    $(".btn-add-view").hide();
  }
});
//

// MENU TABS
$(document).on('click', "#menu-tabs li a", function(e) {
 e.preventDefault();
 $(this).tab('show');
});
$(document).on('click', "#view-mode-pills li a", function(e) {
 e.preventDefault();
 $(this).tab('show');
});
$(document).on('click', "#multiview-mode-pills li a", function(e) {
 e.preventDefault();
 $(this).tab('show');
});


// SET SOURCE MODE
$(document).on('click', "#source-mode-pills li a", function() {
  $("#source-mode-pills li").removeClass('active');
  $('.to-add').removeClass('to-add');
  $('.to-remove').removeClass('to-remove');
  if ( source_mode == $(this).attr('data-source-mode') ) {
    source_mode = 'normal';
  } else {
    $(this).tab('show');
    source_mode = $(this).attr('data-source-mode');
  }
});
// SEARCH IN LIST BY PRESS ENTER
$(document).on('keypress', '.q', function(e) {
  if (e.which == 13 ) {
    var url = $(this).attr('data-url');
    var into = $(this).attr('data-into');
    var data = { q: $(this).val() };
    $.ajax({url:url, async:true, data:data,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $(into).html(data);
      },
    });
  }
});

// GET PAGE
$(document).on('click', '.get-page', function() {
  var url = $(this).attr('data-url');
  var into = $(this).attr('data-into');
  //var into = $(this).parentsUntil('div').parent();
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
    },
  });
  return false;
});

// CLICK ON SOURCE
$(document).on('click', ".addable-source", function() {
  if ( source_mode == 'add' ) {
    $(this).toggleClass('to-add');
  }
});
$(document).on('click', ".removable-source", function() {
  if ( source_mode == 'remove' ) {
    $(this).toggleClass('to-remove');
  }
});
// GET SOURCE
$(document).on('click', ".edit-source", function() {
  if ( source_mode == 'normal' ) {
    var url = $(this).attr('data-url');
    var data_url = $(this).attr('data-data-url');
    var into = $(this).attr('data-into');
    var name = $(this).attr('data-name');
    $.ajax({type:'GET', url:url, async:true,
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $(into).html(data);
        $("#edit-source-tab a").html(name)
        $("#edit-source-tab a").tab('show');
        $("#edit-source-tab").show(250);;
        // ADD PREVIEW
        print_loading_gif('#source-preview', 40, 40);
        $.getJSON(data_url, function(data) {
          for (i in data['datas']){
            data['datas'][i][0] = new Date(data['datas'][i][0] * 1000);
          }
          g = new Dygraph(document.getElementById('source-preview'), data['datas'], {
            labels: data['labels'],
            colors: data['colors'],
            pixelsPerLabel: 60,
            gridLineWidth: 0.1,
            labelsKMG2: true,
            height: 150,
            width: 300,
          });
        });
      },
    });
  }
});
// EDIT SOURCE
$(document).on('submit', "#source-form", function() {
    var url = $(this).attr('action');
    var form = $(this);
    $.ajax({type:'POST', url:url, async:true,
      data: $(this).serialize(),
      error: function(data, status, xhr) { error_modal() },
      success: function(data, status, xhr) {
        $('.messages').append(data);
      },
    });
    return false;
});
// ACTION WHEN CLICK ON GRAPHS
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
          for (j in data['datas']) {
            data['datas'][j][0] = new Date(data['datas'][j][0] * 1000);
          }
	  graphs[view_id][0].updateOptions({
	    file: data['datas'],
	    labels: data['labels'],
	    colors: data['colors'],
	  });
	});
      },
    });

  } else if ( source_mode == 'remove' && $(this).attr('data-view-id') ) {
    var view_id = $(this).attr('data-view-id');
    $('#chosen-view').html(graphs[view_id][0].user_attrs_.title);
    $('#source-to-remove').empty();
    $('#source-to-remove').attr('data-view-id', view_id);
    var j = 0;
    $.each(graphs[view_id][0].user_attrs_.labels, function(i,s) {
      if ( s != 'Date' && s != 'warning' && s != 'critical' ) {
        $('#source-to-remove').append(
	  '<li><a class="removable-source" data-num="'+j+'">'+s+'</a></li>'
	);
	j += 1
      }
    });
  }
});
// REMOVE SOURCE
$(document).on('click', "#btn-remove-source", function() {
  var source_nums = [];
  var view_id = $('#source-to-remove').attr('data-view-id');
  var url = '/multiviews/customize/view/'+view_id+'/remove_source';
  $.each( $('.to-remove'), function() { source_nums.push($(this).attr('data-num')) } ); 
  $.ajax({type:'POST', url:url, async:true,
    data: {
      'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
      'source_nums': source_nums,
    },
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
      $('.to-remove').hide(250);
      var url = graphs[view_id][1]+res;
      $.getJSON(graphs[view_id][1]+res, function(data) {
        for (j in data['datas']) {
          data['datas'][j][0] = new Date(data['datas'][j][0] * 1000);
        }
        graphs[view_id][0].updateOptions({
	  file: data['datas'],
	  labels: data['labels'],
	  colors: data['colors'],
        });
      });
    }
  });
});

// FAST ADD A VIEW
$(document).on('click', "#btn-add-view", function() {
  var name = $('#view-name').val();
  var url = $(this).attr('data-url');
  var multiview_id = $(this).parentsUntil(".dropdown-submenu").parent().children('a').attr('data-id')
  var view_list = $(this).parentsUntil(".view-list").parent('ul');
  var target = $(this).parent().parent().parent();
  $.ajax({type:'POST', url:url, async:true,
    data: {
      'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
      'view_name': name,
      'multiview_id':multiview_id,
      'res': res,
    },
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      var data = xhr.responseJSON
      var view_id = data['id'];
      // Add line
      var line = ' <li><a class="get-view" href="#" data-id="'+view_id+'" data-url="{{ view.get_data_url }}">'+name+'</a></li>';
      $(target).before(line);
      get_graph(view_id, '#graphs');
    }
  });
});
// FAST ADD A VIEW
$(document).on('click', "#btn-add-view", function() {
  var name = $('#view-name').val();
  var url = $(this).attr('data-url');
  var multiview_id = $(this).parentsUntil(".dropdown-submenu").parent().children('a').attr('data-id')
  var view_list = $(this).parentsUntil(".view-list").parent('ul');
  var target = $(this).parent().parent().parent();
  $.ajax({type:'POST', url:url, async:true,
    data: {
      'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
      'view_name': name,
      'multiview_id':multiview_id,
      'res': res,
    },
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      var data = xhr.responseJSON
      var view_id = data['id'];
      // Add line
      var line = ' <li><a class="get-view" href="#" data-id="'+view_id+'" data-url="{{ view.get_data_url }}">'+name+'</a></li>';
      $(target).before(line);
      get_graph(view_id, '#graphs');
    }
  });
});

// EDIT VIEW
$(document).on('click', ".edit-view", function() {
  // SET VARS
  var url = $(this).attr('data-url');
  var data_url = $(this).attr('data-data-url');
  var into = $(this).attr('data-into');
  var name = $(this).attr('data-name');
  // RENDER
  $(into).empty();
  $("#edit-view-tab a").html(name)
  $("#edit-view-tab a").show(250);
  print_loading_gif(into, 60, 60);
  $("#edit-view-tab a").tab('show');
  // GET FORM
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
      // ADD PREVIEW
      print_loading_gif('#view-preview', 40, 40);
      $.getJSON(data_url, function(data) {
        for (i in data['datas']){
          data['datas'][i][0] = new Date(data['datas'][i][0] * 1000);
        }
        g = new Dygraph(document.getElementById('view-preview'), data['datas'], {
          labels: data['labels'],
          colors: data['colors'],
          pixelsPerLabel: 60,
          gridLineWidth: 0.1,
          labelsKMG2: true,
          height: 150,
          width: 300,
        });
      });
    },
  });
});
// ADD OR UPDATE VIEW
$(document).on('submit', "#view-form", function() {
  var url = $(this).attr('action');
  var form = $(this);
  $.ajax({type:'POST', url:url, async:true,
    data: $(this).serialize(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
    },
  });
  return false;
});
// DELETE VIEWS
$(document).on('click', "#btn-delete-view", function(e) {
  e.preventDefault();
  // SET VARS
  var url = $(this).attr('data-url');
  var into = $(this).attr('data-into');
  var id = $(this).attr('data-id');
  // SET RENDER
  $("#edit-view-tab a").hide(250);
  $("#list-view-tab a").tab('show');
  $('.get-view[data-id="'+id+'"]').hide(250);
  // SEND DEL REQUEST
  $.ajax({type:'POST', url:url, async:true,
    data: $(this).serialize()+'csrfmiddlewaretoken='+$('[name="csrfmiddlewaretoken"]').val(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
      // HIDE CURRENT MULTIVIEW
      $("#list-view-content .q").trigger({
        type: "keypress",
        which: 13,
        KeyCode: 13,
      });
    },
  });
});

//// MULTIVIEW
// EDIT MULTIVIEW
$(document).on('click', ".edit-multiview", function() {
  // SET VARS
  var url = $(this).attr('data-url');
  var data_url = $(this).attr('data-data-url');
  var into = $(this).attr('data-into');
  var name = $(this).attr('data-name');
  // RENDER
  $(into).empty();
  $("#edit-multiview-tab a").html(name)
  $("#edit-multiview-tab a").show(250);
  print_loading_gif(into, 60, 60);
  $("#edit-multiview-tab a").tab('show');
  // GET FORM
  $.ajax({type:'GET', url:url, async:true,
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $(into).html(data);
      // ADD PREVIEW
      print_loading_gif('#multiview-preview', 40, 40);
      $.getJSON(data_url, function(data) {
        for (i in data['datas']){
          data['datas'][i][0] = new Date(data['datas'][i][0] * 1000);
        }
        g = new Dygraph(document.getElementById('multiview-preview'), data['datas'], {
          labels: data['labels'],
          colors: data['colors'],
          pixelsPerLabel: 60,
          gridLineWidth: 0.1,
          labelsKMG2: true,
          height: 150,
          width: 300,
        });
      });
    },
  });
});

// ADD OR UPDATE MULTIVIEW
$(document).on('submit', ".multiview-form", function(e) {
  e.preventDefault();
  var url = $(this).attr('action');
  var form = $(this);
  $.ajax({type:'POST', url:url, async:true,
    data: $(this).serialize(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
    },
  });
  return false;
});
// DELETE MULTIVIEWS
$(document).on('click', "#btn-delete-multiview", function(e) {
  e.preventDefault();
  // SET VARS
  var url = $(this).attr('data-url');
  var into = $(this).attr('data-into');
  var id = $(this).attr('data-id');
  // SET RENDER
  $("#edit-multiview-tab a").hide(250);
  $("#list-multiview-tab a").tab('show');
  $('.get-multiview[data-id="'+id+'"]').hide(250);
  // SEND DEL REQUEST
  $.ajax({type:'POST', url:url, async:true,
    data: $(this).serialize()+'csrfmiddlewaretoken='+$('[name="csrfmiddlewaretoken"]').val(),
    error: function(data, status, xhr) { error_modal() },
    success: function(data, status, xhr) {
      $('.messages').append(data);
      // HIDE CURRENT MULTIVIEW
      $("#list-multiview-content .q").trigger({
        type: "keypress",
        which: 13,
        KeyCode: 13,
      });
    },
  });
});
