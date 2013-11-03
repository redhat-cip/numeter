/*global window, document, jQuery, angular*/
(function (window, $, angular) {
  'use strict';

  angular.module('numeter', []);


  window.numeter = {
    graphs: [],
    load_requests: [],
    print_message: function (msg, tag, into) {
      $(into).append([
        '<div id="msg-',
        tag,
        '" class="alert alert-block alert-',
        tag,
        '"><a href="#" data-dismiss="alert" class="close">×</a><div>',
        msg,
        '</div></div>'].join('')
        );
    },
    error_modal: function (err) {
      var my_modal = $('#myModal');
      my_modal.modal('show');
      my_modal.html('<center><h4>Connection error !</h4></center>');
      my_modal.append('<div class="span"><pre>' + err + '</pre></div>');
    },
    print_loading_gif: function (into, heigth, width) {
      if (heigth === 'undefined') { heigth = '100%'; }
      if (width === 'undefined') { width = '100%'; }
      $(into).append([
        '<div class="loader" style="text-align:center;">',
        '<img src="/static/img/ajax-loader.gif" height="',
        heigth,
        '" width="',
        width,
        '">'].join('')
        );
    },
    // REMOVE LOAD GIF
    remove_loading_gif: function (from) {
      $(from + ' .loader').remove();
    },
    // ABORT GRAPH PREVIEW
    stop_request: function () {
      var i, length = this.load_requests.length;
      for (i = 0; i < length; i = i + 1) {
        this.load_requests[i].abort();
      }
    }
  };
}(window, jQuery, angular));
