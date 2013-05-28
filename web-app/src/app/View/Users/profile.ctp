<h1>Profile</h1>
<div class="span3 offset5">
<?php echo $this->Form->create('Profile', array('class' => 'well')); ?>
<?php
    echo $this->Form->input('Graph', array('options' => $graphs, 'default' => $authUser['graph']));
?>
<?php	echo $this->Form->button('Submit', array('type'=>'submit','class' => 'btn')); ?>
</div>
