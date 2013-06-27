// MESSAGES
// BASIC FUNC
var print_message = function(msg,tag,into) {
  var html = '<div id="msg-'+tag+'" class="alert alert-'+tag+'" style="display: block;"><p class="pull-right"><button class="close" onclick="$(this).parent().parent().hide(250)">×</button></p><div>'+msg+'</div></div>';
  $(into).append(html);
}

var print_reload = function(into) {
  print_message("Utilisateur actif modifié.<br>La page va être rechargée.",'warning',into);
}

// ADD LOADING GIF
var print_loading_gif = function(into, heigth, width) {
  if(typeof(heigth)==='undefined') heigth = 100;
  if(typeof(width)==='undefined') width = 100;
  $(into).append('<img class="loader" src="/static/img/ajax-loader.gif" height="'+heigth+'%" width="'+width+'%">' );
}
var remove_loading_gif = function(from) {
  $(from+ ' .loader').remove();
}

// SEARCH PAGE
$(document).on('keypress', '#page_q', function(e) {
    if (e.which == 13 && $(this).val().length ) {
      print_loading_gif('#action-msg-box',50,50);
      $.ajax({url:'/search_page', async:true,
        data:{q:$(this).val(), type:$('#search-type').val()},
        success: function(data, status, xhr) {
          $('#search-pages').html(data);
        },
        complete: function(data, status, xhr) {
          remove_loading_gif('#action-msg-box');
        },
      });
    }
});

// GET PAGES LINKS
var get_page_links = function(pages,into) {
    print_loading_gif(into,50,50);
    $.ajax({url:'/get_page_links', async:true,
      data:{pages:pages},
      success: function(data, status, xhr) {
        $(into).append(data);
	  },
      complete: function(data, status, xhr) {
        remove_loading_gif(into);
      },
    })
}


// CHOOSE AN ACTION FOR SEARCHED PAGES
$(document).on('change', '#search-pages-action', function() {
    if ( $(this).val() == 'add' ) {
        $('#search-pages :selected').appendTo('#pages');
    } else if ( $(this).val() == 'delete' ) {
        $('#search-pages :selected').remove();
    } else if ( $(this).val() == 'delete-all' ) {
        $('#search-pages option').remove();
    } else if ( $(this).val() == 'select-all' ) {
        $('#search-pages option').prop('selected', true);
    } else if ( $(this).val() == 'unselect-all' ) {
        $('#search-pages option').prop('selected', false);
    } else if ( $(this).val() == 'get-page-links' ) {
        var pages = $('#search-pages').val(); 
        get_page_links(pages, '#action-msg-box');
    }
    $(this).val('---');
});
// WHY DOESN'T WORK ??
$(document).on('dbclick', '#search-pages', function() {
    $('#search-pages').children(':selected').appendTo('#pages');
});

// CHOOSE A META-ACTION FOR SELECTED PAGES
$(document).on('change', '#pages-meta-action', function() {
    if ( $(this).val() == 'delete' ) {
        $('#pages option:selected').remove();
    } else if ( $(this).val() == 'delete-all' ) {
        $('#pages option').remove();
    } else if ( $(this).val() == 'select-all' ) {
        $('#pages option').prop('selected', true);
    } else if ( $(this).val() == 'get-page-links' ) {
        var pages = $('#pages').val(); 
        get_page_links(pages, '#action-msg-box');
    }
    $(this).val('---');
});

// CHOOSE ACTION FOR SELECTED PAGES
$(document).on('change', '#pages-action', function() {
    var action = $(this).val();
    $('[id*=div-action]').hide(250);
    $('#div-action-'+action).show(250);
});

// REMOVE SELECTED PAGES
$(document).on('click', '#btn-delete-pages', function() {
    $('#pages').children(':selected').remove();
});

/// ACTIONS FOR SELECTED PAGES
// CHECK IF CATEGORY EXISTS
$(document).on('click', '.btn-check-page', function() {
    var into = '#'+$(this).parent().parent().attr('id');
    var pagename = $( '#'+$(this).attr('rel') ).val()
    if ( $(this).hasClass('btn-check-category') ) {
      pagename = 'Catégorie:'+pagename;
    }
    if ( pagename.length ) {
      print_loading_gif(into,50,50);
      $.ajax({url:'/check_page', data:{page:pagename}, async:true,
        success: function(data, status, xhr) {
          $(into).append(data);
        },
        complete: function(data, status, xhr) {
          remove_loading_gif(into);
        },
      });
    }
});

// RENAME PAGES
$(document).on('click', '#btn-rename-pages', function() {
    var into = '#div-action-rename-pages';
    if ( $('#rename-from').val().length ) {
      print_loading_gif(into,50,50);
      $.ajax({type:'POST', url:'/move_pages', async:true,
          data:{
              pages:$('#pages').val(), 
              pat:$('#rename-from').val(),
              repl:$('#rename-to').val(),
              redirect:$('#rename-redirect:checked').val() || '',
              csrfmiddlewaretoken:csrf
          },
          success: function(data, status, xhr) {
              $(into).append(data);
          },
          complete: function(data, status, xhr) {
            remove_loading_gif(into);
          },
      });
    }
});

// ADD CATEGORY TO PAGES
$(document).on('click', '#btn-add-category', function() {
    if ( $('#category-to-add').val().length ) {
      var into = '#div-action-add-category';
      print_loading_gif(into,50,50);
      $.ajax({type:'POST', url:'/add_category', async:true,
          data:{
              pages:$('#pages').val(),
			  category:'Catégorie:'+$('#category-to-add').val(),
			  csrfmiddlewaretoken:csrf
          },
          success: function(data, status, xhr) {
              $(into).append(data);
          },
          complete: function(data, status, xhr) {
            remove_loading_gif(into);
          },
      });
    }
});

// REMOVE CATEGORY
$(document).on('click', '#btn-remove-category', function() {
    if ( $('#category-to-remove').val().length ) {
	  var into = '#div-action-remove-category';
      print_loading_gif(into,50,50);
      $.ajax({type:'POST', url:'/remove_category', async:true,
          data:{
              pages:$('#pages').val(),
              category:'Catégorie:'+$('#category-to-remove').val(),
              csrfmiddlewaretoken:csrf
          },
          success: function(data, status, xhr) {
              $('#div-action-remove-category').append(data);
          },
          complete: function(data, status, xhr) {
            remove_loading_gif(into);
          },
      });
    }
});

// MOVE CATEGORY
$(document).on('click', '#btn-move-category', function() {
    if ( $('#category-move-to').val().length && $('#category-move-from').val().length) {
      var into = '#div-action-move-category';
      print_loading_gif(into,50,50);
      $.ajax({type:'POST', url:'move_category', async:true,
          data:{
              pages:$('#pages').val(), 
              from:'Catégorie:'+$('#category-move-from').val(),
              to:'Catégorie:'+$('#category-move-to').val(),
              csrfmiddlewaretoken:csrf
          },
          success: function(data, status, xhr) {
              $('#div-action-move-category').append(data);
          },
          complete: function(data, status, xhr) {
            remove_loading_gif(into);
          },
      });
    }
});

// ADD HYPERLINKS
$(document).on('click', '#btn-add-hyperlink', function() {
  if ( $('#link-to-add').val().length ) {
    var into = '#div-action-add-hyperlink';
    print_loading_gif(into,50,50);
    $.ajax({type:'POST', url:'/add_internal_link', async:true,
      data:{
        pages:$('#pages').val(), 
        link:$('#link-to-add').val(),
        link_text:$('#link-text').val(),
        csrfmiddlewaretoken:csrf
      },
      success: function(data, status, xhr) {
        $(into).append(data);
      },
      complete: function(data, status, xhr) {
        remove_loading_gif(into);
      },
    });
  }
});

// SUBSITUTION
$(document).on('click', '#btn-sub', function() {
  if ( $('#sub-from').val().length ) {
    var into = '#div-action-sub'
    print_loading_gif(into,50,50);
    $.ajax({type:'POST', url:'/sub', async:true,
      data:{
        pages:$('#pages').val(), 
        from:$('#sub-from').val(),
        to:$('#sub-to').val(),
        csrfmiddlewaretoken:csrf
      },
      success: function(data, status, xhr) {
        $(into).append(data);
      },
      complete: function(data, status, xhr) {
        remove_loading_gif(into);
      },
    });
  }
});

// SEARCH CONTRIBUTIONS
$(document).on('keypress', '#contrib_q', function(e) {
    if (e.which == 13 && $(this).val().length ) {
      var into = '#contribs';
      print_loading_gif(into,50,50);
      $.ajax({url:'/search_contribution', async:true,
          data:{q:$(this).val()},
          success: function(data, status, xhr) {
              $(into).html(data);
          },
          complete: function(data, status, xhr) {
            remove_loading_gif(into);
          },
      });
    }
});


// GET REGISTERED USER FORM
$(document).on('click', '#btn-get-wikiuser', function() {
  $.ajax({type:'GET', url:'/get_user', async:true,
    data:{id:$('input[name="user-chosen"]:checked').val()},
    success: function(data, status, xhr) {
      $('#user-form').html(data);
	}
  });
});

// GET NOT REGISTERED USER FORM
$(document).on('click', '#btn-get-form-wikiuser', function() {
  $.ajax({type:'GET', url:'/get_user', async:true,
    success: function(data, status, xhr) {
      $('#user-form').html(data);
	}
  });
});

// ADD USER
$(document).on('click', '#btn-add-wikiuser', function() {
  $.ajax({type:'POST', url:'/add_user', async:true,
    data:{
	  nick:$('#id_nick').val(),
	  family:$('#id_family').val(),
	  language:$('#id_language').val(),
	  url:$('#id_url').val(),
	  comment:$('#id_comment').val(),
	  active:($('#id_active:checked').val() || ''),
      csrfmiddlewaretoken:csrf
	},
    success: function(data, status, xhr) {
      $('#user-form-messages').prepend(data);
      if ( $('#id_active:checked').val() || null ) {
        print_reload('#user-form-messages');
        setTimeout(window.location.reload, 3000);
      } else {
        $.ajax({type:'GET', url:'/get_user_list', async:true,
          success: function(data, status, xhr) {
            $('#user-list').html(data);
	      }
        })
     }
	}
  });
});

// UPDATE USER
$(document).on('click', '#btn-update-wikiuser', function() {
  $.ajax({type:'POST', url:'/update_user', async:true,
    data:{
	  id:$('#id_id').val(),
	  nick:$('#id_nick').val(),
	  family:$('#id_family').val(),
	  language:$('#id_language').val(),
	  url:$('#id_url').val(),
	  comment:$('#id_comment').val(),
	  active:($('#id_active:checked').val() || ''),
      csrfmiddlewaretoken:csrf
	},
    success: function(data, status, xhr) {
      $('#user-form-messages').prepend(data);
      if ( $('#id_active:checked').val() || null ) {
        print_reload('#user-form-messages');
        setTimeout(window.location.reload, 3000);
      }
	}
  });
});

// DELETE USER
$(document).on('click', '#btn-delete-wikiuser', function() {
  $.ajax({type:'POST', url:'/delete_user', async:true,
    data:{
	  id:$('#id_id').val(),
      csrfmiddlewaretoken:csrf
	},
    success: function(data, status, xhr) {
      $('#user-list').html(data);
      $('#btn-get-form-wikiuser').click();
      print_message('Utilisateur supprimé.','error','#user-messages');
	}
  });
});

// CHOOSE USER
$('.accordion-body').on('shown', function() {
  var id = $(this).attr('group-id');
  $.ajax({type:'GET', url:'/get/hosts/'+id, async:true,
    success: function(data, status, xhr) {
       $('#group-'+id).html(data);
    }
  });
});

$('.dropdown-toggle').dropdown()
