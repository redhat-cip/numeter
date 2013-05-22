<?php
/**
 *
 * PHP 5
 *
 * CakePHP(tm) : Rapid Development Framework (http://cakephp.org)
 * Copyright 2005-2012, Cake Software Foundation, Inc. (http://cakefoundation.org)
 *
 * Licensed under The MIT License
 * Redistributions of files must retain the above copyright notice.
 *
 * @copyright     Copyright 2005-2012, Cake Software Foundation, Inc. (http://cakefoundation.org)
 * @link          http://cakephp.org CakePHP(tm) Project
 * @package       Cake.View.Layouts
 * @since         CakePHP(tm) v 0.10.0.1076
 * @license       MIT License (http://www.opensource.org/licenses/mit-license.php)
 */

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<?php echo $this->Html->charset(); ?>
	<title>
		<?php echo $cakeDescription ?>:
		<?php echo $title_for_layout; ?>
	</title>
	<?php
		echo $this->Html->meta('icon');

		//echo $this->Html->script('jquery');
		echo $this->Html->script('jquery-1.8.0.min');
		echo $this->Html->script('jquery-ui-1.8.23.custom.min');
		echo $this->Html->css('ui-lightness/jquery-ui-1.8.23.custom');
		echo $this->Html->css('bootstrap.min');
		echo $this->Html->css('bootstrap-responsive.min');
		echo $this->Html->script('bootstrap.min');


        if ($graphType) { // 1 highcharts
            echo '<script type="text/javascript" src="/highcharts/js/highstock.js"></script>';
            echo '<script type="text/javascript" src="/highcharts/js/modules/exporting.js"></script>';
            echo '<script type="text/javascript" src="/highcharts/js/themes/gray.js"></script>'; // Comment for default theme
		    echo $this->Html->script('numeter');
        } else {  // 0 dygraphs
		    echo $this->Html->script('dygraph-combined');
        }

		echo $this->Html->css('numeter');
		echo $this->fetch('meta');
		echo $this->fetch('css');
		echo $this->fetch('script');
	?>
	<style type="text/css">
      		body {
        		padding-top: 60px;
        		padding-bottom: 40px;
      		}
		.sidebar-nav {
        		padding: 9px 0;
      		}
    	</style>
    <link rel="apple-touch-icon" href="img/glyphicons-halflings-white.png">
    <link rel="apple-touch-icon" href="img/glyphicons-halflings.png">
</head>
<body>
    <div class="navbar navbar-inverse navbar-fixed-top"> 
      		<div class="navbar-inner">
        		<div class="container-fluid">
        			<a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
        				<span class="icon-bar"></span>
        				<span class="icon-bar"></span>
        				<span class="icon-bar"></span>
        			</a>
       				<a class="brand" href="/">Numeter Dashboard</a>
        			<div class="nav-collapse">
        			
<?php if ($authUser) { echo'
				<ul class="nav pull-right">
  					<li class="dropdown" id="menu1">
    <a class="dropdown-toggle" data-toggle="dropdown" href="#">'.$authUser['username'].'<b class="caret"></b></a>
    <ul class="dropdown-menu">';
      if ($authUser['isadmin']) {echo '<li><a href="/admin">Admin</a></li>';}
	echo '<li><a href="/users/profile">Profile</a></li>
      <li><a href="/users/logout">Log Out</a></li>
    </ul>
  </li>
</ul>'; } ?>
				</div><!--/.nav-collapse -->
			</div>
		</div>
	</div>
    	
	<div class="container-fluid">
		<div id="content">
			<?php echo $this->Session->flash(); ?>
			<?php echo $this->fetch('content'); ?>
		</div>
	</div>
	<hr>
	<footer>
	&nbsp;&nbsp;&nbsp;&nbsp;&copy; Numeter <?php echo date('Y'); ?><br><br>
	<?php echo $this->element('sql_dump'); ?>
    </footer>
	<!--<script type="text/javascript" src="/js/bootstrap-dropdown.js"></script>
	<script type="text/javascript">
		$(document).ready(function () {  
            $('.dropdown-toggle').dropdown();  
        });
	</script>-->
</body>
</html>
