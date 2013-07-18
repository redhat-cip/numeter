function get_data(url, { hostid: hostid, plugin: plugin, ds: ds, res: res }, into) {
  $.getJSON(url, function(data) {
    return data;
  });
}

g = new Dygraph(document.getElementById("demodiv"), get_data, {
  title: 'Stacked chart w/ Total',
  legend: 'always',
  labelsDiv: 'graphleg',
  labelsSeparateLines: true,
  fillGraph: true,
  labelsDivWidth: 100,
  pixelsPerLabel: 60,
  gridLineWidth: 0.1,
  labelsKMG2: true,
  stackedGraph: true,
  axes: {
    x: {
      valueFormatter: function(val, opts, series_name, dygraph) {
        for (var i = 0; i < dygraph.numRows(); i++) {
          if (dygraph.getValue(i, 0) != val) continue;
          var total = 0;
          for (var j = 1; j < dygraph.numColumns(); j++) {
            total += dygraph.getValue(i, j);
          }
          return Dygraph.dateString_(val) + ' (total: ' + total.toFixed(2) + ')';
        }
      }
    }
  }
});
