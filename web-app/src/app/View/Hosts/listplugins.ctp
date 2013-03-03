<div class=row>
<div class='span3'>
<ul class="well nav nav-list">
    <li class="nav-header">
        Plugins
    </li>
    <?php function sortTitle($a, $b) {
        return (strcmp (strtolower($a['Title']), strtolower($b['Title'])));
    } ?>$
    <?php foreach ($plugins as $category => $cat_contenent): 
            $plugin = json_decode($plugin,true);
            echo $category;
            uasort($cat_contenent, 'sortTitle');
        foreach ($cat_contenent as $plugin):
            if( $plugin['Plugin'] == $cur_plugin)
                echo "<li style='padding-left: 20px' class=active>";
            else
                echo "<li style='padding-left: 20px'>";	
            ?>
                <a href=/hosts/listplugins/<?php echo "$storageID/$hostID/".$plugin['Plugin'] ?>><?php echo $plugin['Title'] ?></a>
            </li>
        <?php endforeach;
    endforeach; ?>
</ul>
</div>
<div class='span9'>
<ul class="breadcrumb">
  <li>
    <a href="/hosts">Host</a> <span class="divider">/</span>
  </li>
  <li>
    <a href="#"><?php echo $host_name ?></a><?php if($cur_plugin) {echo '<span class="divider">/</span>';} ?>
  </li>
        <?php 
                if($cur_plugin) {
                        echo "<li>$cur_plugin</li>";
                }
        ?>
</ul><br>
<?
if ($graphType) { //if highcharts
    echo "<!-- Graphs config and div -->";
    echo "<script language='javascript' type='text/javascript'>";
    echo "    var config_host    ='$hostID';";
    echo "    var config_storage ='$storageID';";
    echo "    var config_plugin  =['$cur_plugin'];";
    echo "</script>";
    echo '<div id="numeter_web_app_content">';
    echo '</div>';
} else { // if dygraphs
?>

    <ul class="nav nav-tabs">
      <?php if($period=="Daily") { echo '<li class="active">'; } else { echo "<li>"; } echo "<a href='/hosts/listplugins/$storageID/$hostID/$cur_plugin/Daily'>Daily</a></li>\n";  ?>
      <?php if($period=="Weekly") { echo '<li class="active">'; } else { echo "<li>"; } echo "<a href='/hosts/listplugins/$storageID/$hostID/$cur_plugin/Weekly'>Weekly</a></li>\n"; ?>
      <?php if($period=="Monthly") { echo '<li class="active">'; } else { echo "<li>"; } echo "<a href='/hosts/listplugins/$storageID/$hostID/$cur_plugin/Monthly'>Monthly</a></li>\n"; ?>
      <?php if($period=="Yearly") { echo '<li class="active">'; } else { echo "<li>"; } echo "<a href='/hosts/listplugins/$storageID/$hostID/$cur_plugin/Yearly'>Yearly</a></li>\n"; ?>
    </ul>
    <br>
    <?php	
    	if ($datas) {
    		echo '<div class=well><div id="graphdiv" style="width:800px; height:300px;"></div><div id=graphleg></div></div>';
    		echo '<script type="text/javascript">g = new Dygraph(document.getElementById("graphdiv"),';
    		
    		$start=$datas['TS_start'];
    		$inc=$datas['TS_step'];
    		$header="Date";
    		$formatted_data=array();
    		foreach ($datas['DATAS'] as $key => $value)
    		{
    			$header="$header,$key";
    			foreach ( $value as $key2 => $value2 )
    			{	
    				if(!$formatted_data[$key2]){
    					$cal_date=date('Y/m/d H:i:s',$start+($inc*$key2));
    					$formatted_data[$key2]="$cal_date,$value2";
    				}
    				else
    					$formatted_data[$key2]="$formatted_data[$key2],$value2";
    			}
    		}
    		
    		echo "\"$header\\n\" +";
    		foreach ($formatted_data as $value)
    			echo "\"$value\\n\" +";
    		echo "\"\"";
    		echo ",{legend: 'always',labelsDiv: 'graphleg', labelsSeparateLines: true, fillGraph: true, labelsDivWidth: 100, pixelsPerLabel: 60, gridLineWidth: 0.1,title: '$cur_plugin ($period)',labelsKMG2: true  });</script>";
    	}
}
?>

</div>
</div>
