// Parse GET for host / server
function getQuerystring(key, default_)
{
  if (default_==null) default_=""; 
  key = key.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regex = new RegExp("[\\?&]"+key+"=([^&#]*)");
  var qs = regex.exec(window.location.href);
  if(qs == null)
    return default_;
  else
    return qs[1];
}

function formatValue(value, base) {

    base = typeof base !== 'undefined' ? base : 1000;

    var M = Math.pow(base,2);
    var G = Math.pow(base,3);
    var T = Math.pow(base,4);
    var P = Math.pow(base,5);

    switch(true) {
        case (Math.abs(value) >= P):
            var label = value / P,
                unit  = 'P';
            break
        case (Math.abs(value) >= T):
            var label = value / T,
                unit  = 'T';
            break
        case (Math.abs(value) >= G):
            var label = value / G,
                unit  = 'G';
            break
        case (Math.abs(value) >= M):
            var label = value / M,
                unit  = 'M';
            break
        case (Math.abs(value) >= base):
            var label = value / base,
                unit  = 'K';
            break
        default:
            var label = value,
                unit  = '';
            break
    }

    result = label.toFixed(1); // 2 number after ,
    return result+' '+unit;
}


// Adjust time :
// CET UTC+1       CEST    UTC+2
//return this.value; // clean, unformatted number for year
// string = Highcharts.dateFormat('%e. %b', this.x) + ' : ';
// format date and add 3600*1000 to Unix timestamp (GMT +1h) 
// and (*1000 convert Unix timestamp for JavaScript Date)
var currentTime = new Date();
var tzInHour = currentTime.getTimezoneOffset()/-60;
var timeGap = 3600000 * tzInHour;

var chart;

var serverURL='';
var host=getQuerystring('host');

//reset bouton set_daily ... and set selected
function resetSetAll(graphName,selected) {
    var set_all = ["Daily","Weekly","Monthly","Yearly"]; 
    for (var set in set_all){
        if (set_all[set] == selected) {
            $('#set_'+set_all[set]+'_'+graphName).attr('style','background: #666666;');
        } else {
            $('#set_'+set_all[set]+'_'+graphName).attr('style','');
        }
    }
}


$(document).ready(function() {

    //Config from <!-- Graphs config and div -->
    // config_host    = hostID
    // config_storage = storageID
    // config_plugin  = ["cpu","numeter_test","swap"]

	// Defaults values
	var default_settings = { 
	            chart : {
	                renderTo : 'default',
	                //defaultSeriesType: 'spline',
	                animation : false, // effets de mouvements
	                zoomType: 'xy'
	            },
	            rangeSelector : {
	                selected : 1,
	                inputEnabled : false,
	                buttons: [{
	                    type: 'hour',
	                    count: 1,
	                    text: '1h'
	                }, {
	                    type: 'hour',
	                    count: 12,
	                    text: '12h'
	                }, {
	                    type: 'day',
	                    count: 1,
	                    text: '1d'
	                }, {
	                    type: 'day',
	                    count: 7,
	                    text: '1w'
	                }, {
	                    type: 'month',
	                    count: 1,
	                    text: '1m'
	                }, {
	                    type: 'all',
	                    text: 'All'
	                }]
	            },
	            title : {
	                text : 'Default title'
	            },
	            legend: {
	                enabled: true,
	                layout: 'vertical',
	                align: 'right',
	                verticalAlign: 'top',
	                x: -10,
	                y: 60,
	                borderWidth: 0,
	                itemWidth: 150
	            },
		    	xAxis: {
		    		labels: {
		    			formatter: function() {
	                        var d = new Date();
		    				return Highcharts.dateFormat('%e - %H:%M', this.value)
		    			}
		    		},
	                type: 'datetime'
		    	},
	            yAxis: {
	                title: {
	                    text: ''
	                },
	                labels: {
	                    formatter : function() {
	                        return this.value;
	                    }
	                }
	            },
		    	plotOptions: {
	                area : {
	                    fillOpacity: .30
	                },
	                series: {
	                    stacking: "normal",
	                    shadow: false,
	                    animation : false,
		    			marker: {
		    				enabled: false, // points sur le graph
		    				symbol: 'circle', // forme du curseur je pense
		    				radius: 2, // Taille du point qui suit le curseur
		    				states: {
		    					hover: {
		    						enabled: true // activer le point qui suit le curseur
		    					}
		    				}
		    			}
	                }
		    	},
	            series : [
	            ]
	};
	
	
	
	//gen graphs
	function genGraphs(graphInfos,storage,host,resolution) {
	
	    resolution = resolution ? resolution : "Daily";
	    var pluginName = graphInfos.Plugin;
	    var allDs = Object.keys(graphInfos.Infos);
	
	    // Get datas
        $.getJSON( serverURL + '/storageapi/get/data/'+storage+'/'+host+'/'+pluginName+'/'+allDs+'/'+resolution, {format: "json"},
	    //$.getJSON( serverURL + '/php_exec_cgi.php?host=' + host
	    //    + '&plugin=' + pluginName
	    //    + '&ds=' + allDs
	    //    + '&res=' + resolution , {format: "json"},
	        function(datas) {
	
	            var orderedName = graphInfos.Order ? graphInfos.Order.split(/ +/) : []
	            for (var dsName in graphInfos.Infos){
	                if ($.inArray(dsName, orderedName) == -1) {
	                    orderedName.push(dsName);
	                }
	            }
	
	            //var keys = Object.keys(graphInfos.Infos)
	
	            //make series
	            var allSeries = []
	            var stackID = 0
	            for (var index in orderedName) {
	                //dsName = orderedName[index].toLowerCase();
	                dsName = orderedName[index];
	                if (! dsName || ! graphInfos.Infos[dsName]) { continue; }
	
	                // Defaut
	                var wineWidth = null
	                var type = null
	
	                // Custom type of series
	                if ( typeof(graphInfos.Infos[dsName].draw)=='undefined' ) {
	                    type = null
	                } else if ( graphInfos.Infos[dsName].draw.toLowerCase() == "line1") {
	                    type = "line"
	                    wineWidth = 1
	                } else if ( graphInfos.Infos[dsName].draw.toLowerCase() == "line2") {
	                    type = "line"
	                    wineWidth = 2
	                } else if ( graphInfos.Infos[dsName].draw.toLowerCase() == "areastack") {
	                    stackID--
	                    if ( stackID < 0 ) { stackID = 0 }
	                    type = "area"
	                } else if ( graphInfos.Infos[dsName].draw.toLowerCase() == "linestack") {
	                    stackID--
	                    if ( stackID < 0 ) { stackID = 0 }
	                    type = "line"
	                } else if ( graphInfos.Infos[dsName].draw.toLowerCase() != "stack") {
	                    type = graphInfos.Infos[dsName].draw.toLowerCase()
	                } else if ( graphInfos.Infos[dsName].draw.toLowerCase() == "stack" ) {
	                    stackID--
	                    if ( stackID < 0 ) { stackID = 0 }
	                    //type = allSeries[stackID].type
                        // Get type of last ds for inverser stack view order
	                    type = allSeries[orderedName.length-index-1+1].type
	                }
	
	                var dsSerie = {
	                    name : dsName,
	                    type : type ? type : "spline",
	                    stack: stackID,
	                    lineWidth: wineWidth ? wineWidth : 1,
	                    color: graphInfos.Infos[dsName].color ? graphInfos.Infos[dsName].color : null,
	                    data: datas.DATAS[dsName]
	                }
	                //allSeries.push(dsSerie)
                    // Inverse stack view order
	                allSeries[orderedName.length-index-1] = dsSerie
	                stackID++
	            }
	
	            // Graphs settings
	            var graph_settings = {
		    	            plotOptions: {
	                            series: {
		    			            pointStart: datas.TS_start*1000+timeGap, //JSON
	                                pointInterval: datas.TS_step*1000, //JSON
	                            }
	                        },
	                        chart : {
	                            renderTo : pluginName,
	                            events: {
	                                    selection: function(event) {
	                                        if (event.xAxis) {
	                                            $('#reset_zoom_'+pluginName).show();
	                                            var extremes = this.xAxis[0].getExtremes();
	                                            if (! this.minBack && ! this.maxBack) {
	                                                this.minBack = extremes.min
	                                                this.maxBack = extremes.max
	                                            }
	                                        
	                                        }
	                                    }
	                            }
	                        },
	                        title : {
	                            text : graphInfos.Title ? graphInfos.Title : pluginName
	                        },
	                        subtitle: {
	                            // " " for css button position
	                            text: graphInfos.Describ ? graphInfos.Describ : " ",
	                            x: -20
	                        },
	                        tooltip: {
	                            shared: false,
	                            crosshairs: false,
	                            borderColor: null,
	                            borderWidth: 1,
		    	            	formatter: function() {
		    	            		//return this.series.name +' - <b>'+
		    	            		return '<span style="color:'+this.series.color+'">'+this.series.name + '</span> - <b>'+
		    	            			formatValue(this.y,graphInfos.Base) +'</b><br/>in '
		    	            			//Highcharts.numberFormat(this.y, 0) +'</b><br/>in '
	                                    + Highcharts.dateFormat('%e. %b %H:%M', this.x);
		    	            	}
	                        },
	                        /*yAxis: {
	                            title: {
	                                text: graphInfos.Vlabel
	                            },
	                        },*/
	                        yAxis: {
	                            title: {
	                                            text: graphInfos.Vlabel
	                            },
	                            labels: {
	                                formatter : function() {
	                                    return formatValue(this.value,graphInfos.Base);
	                                }
	                            }
	                        },
	                        series : allSeries
	            };
	
	        // Add defaults settings
	        var graph_ready = $.extend(true, {}, default_settings, graph_settings);
	
	        // Create graph
	        //chart = new Highcharts.Chart(graph_ready);
	        chart = new Highcharts.StockChart( graph_ready, function(chart){
	                $('#reset_zoom_'+pluginName).click(function() {
	                    chart.xAxis[0].setExtremes(chart.minBack,chart.maxBack);
	                    chart.minBack = chart.maxBack = null;
	                    chart.yAxis[0].setExtremes();
	                    $(this).hide();
	                }); }
	            );
	
	        chart.resetZoomEnabled = false;
	
	    });
	
	}
	
	


	function main(storage,host,plugList) {
        for(var i in plugList) {
            var plugin = plugList[i];
            // Get plugin info
            //$.getJSON( serverURL + '/php_exec_cgi.php?info='+plugList.list[i]+'&host='+host, 
            $.getJSON( serverURL + '/storageapi/get/info/'+storage+'/'+host+'/'+plugin, 
                {format: "json"},
                function(datas) {
                    // Add new div
                    $("#numeter_web_app_content").append('<h3>'+datas.Title+'</h3><div id="'+datas.Plugin
                        +'_content" style="width: 900px; height: 400px; margin: 0 auto"><div id="'
                        +datas.Plugin+'" ></div></div><p>&nbsp;</p>');
                    // Daily
                    $("#"+datas.Plugin+"_content").append('<button id="set_Daily_'
                        +datas.Plugin+'" style="background: #666666" class="Daily_button">Daily</button>');
                    // Weekly
                    $("#"+datas.Plugin+"_content").append('<button id="set_Weekly_'
                        +datas.Plugin+'" class="Weekly_button">Weekly</button>');
                    // Monthly
                    $("#"+datas.Plugin+"_content").append('<button id="set_Monthly_'
                        +datas.Plugin+'" class="Monthly_button">Monthly</button>');
                    // Yearly
                    $("#"+datas.Plugin+"_content").append('<button id="set_Yearly_'
                        +datas.Plugin+'" class="Yearly_button">Yearly</button>');
                    // Reset zoom
                    $("#"+datas.Plugin+"_content").append('<button id="reset_zoom_'
                        +datas.Plugin+'" class="zoom_button">Reset zoom</button>');
        
                    // Set_ function
                    // Daily
                    $('#set_Daily_'+datas.Plugin).click(function() {  
                        genGraphs(datas,storage,host,'Daily');
                        resetSetAll(datas.Plugin,"Daily");
                    });
                    // Weekly
                    $('#set_Weekly_'+datas.Plugin).click(function() {  
                        genGraphs(datas,storage,host,'Weekly');
                        resetSetAll(datas.Plugin,"Weekly");
                    });
                    // Monthly
                    $('#set_Monthly_'+datas.Plugin).click(function() {  
                        genGraphs(datas,storage,host,'Monthly');
                        resetSetAll(datas.Plugin,"Monthly");
                    });
                    // Yearly
                    $('#set_Yearly_'+datas.Plugin).click(function() {  
                        genGraphs(datas,storage,host,'Yearly');
                        resetSetAll(datas.Plugin,"Yearly");
                    });
        
                    // start gen graph
                    genGraphs(datas,storage,host);
                    //genGraphs(datas,storage,host,resolution);
            });
        }
    }
	

    // MAIN
    if (typeof(config_storage) !== 'undefined' && typeof(config_host) !== 'undefined' && typeof(config_plugin) !== 'undefined') {
        main(config_storage,config_host,config_plugin);
    }
	
	
//	// Get plugin list
//	$.getJSON( serverURL + '/php_exec_cgi.php?list='+host, 
//	    {format: "json"},
//	    function(datas) {
//	
//	        var plugList = datas;
//	        //plugList.list = ["cpu","numeter_test","swap"]
//	        //plugList.list = ["numeter_test"]
//	        // Plugin list
//	        for (var i in plugList.list) {
//	            // Get plugin info
//	            $.getJSON( serverURL + '/php_exec_cgi.php?info='+plugList.list[i]+'&host='+host, 
//	                {format: "json"},
//	                function(datas) {
//	                    // Add new div
//	                    $("#numeter_web_app_content").append('<h3>'+datas.Title+'</h3><div id="'+datas.Plugin
//	                        +'_content" style="width: 900px; height: 400px; margin: 0 auto"><div id="'
//	                        +datas.Plugin+'" ></div></div><p>&nbsp;</p>');
//	                    // Daily
//	                    $("#"+datas.Plugin+"_content").append('<button id="set_Daily_'
//	                        +datas.Plugin+'" style="background: #666666" class="Daily_button">Daily</button>');
//	                    // Weekly
//	                    $("#"+datas.Plugin+"_content").append('<button id="set_Weekly_'
//	                        +datas.Plugin+'" class="Weekly_button">Weekly</button>');
//	                    // Monthly
//	                    $("#"+datas.Plugin+"_content").append('<button id="set_Monthly_'
//	                        +datas.Plugin+'" class="Monthly_button">Monthly</button>');
//	                    // Yearly
//	                    $("#"+datas.Plugin+"_content").append('<button id="set_Yearly_'
//	                        +datas.Plugin+'" class="Yearly_button">Yearly</button>');
//	                    // Reset zoom
//	                    $("#"+datas.Plugin+"_content").append('<button id="reset_zoom_'
//	                        +datas.Plugin+'" class="zoom_button">Reset zoom</button>');
//	
//	                    // Set_ function
//	                    // Daily
//	                    $('#set_Daily_'+datas.Plugin).click(function() {  
//	                        genGraphs(datas,'Daily');
//	                        resetSetAll(datas.Plugin,"Daily");
//	                    });
//	                    // Weekly
//	                    $('#set_Weekly_'+datas.Plugin).click(function() {  
//	                        genGraphs(datas,'Weekly');
//	                        resetSetAll(datas.Plugin,"Weekly");
//	                    });
//	                    // Monthly
//	                    $('#set_Monthly_'+datas.Plugin).click(function() {  
//	                        genGraphs(datas,'Monthly');
//	                        resetSetAll(datas.Plugin,"Monthly");
//	                    });
//	                    // Yearly
//	                    $('#set_Yearly_'+datas.Plugin).click(function() {  
//	                        genGraphs(datas,'Yearly');
//	                        resetSetAll(datas.Plugin,"Yearly");
//	                    });
//	
//	                    // start gen graph
//	                    genGraphs(datas);
//	            });
//	        }
//	});

});

