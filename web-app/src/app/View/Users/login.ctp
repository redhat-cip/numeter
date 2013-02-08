<h1>Login</h1>
<div class="span3 offset5">
<?php echo $this->Session->flash('auth'); ?>
<?php echo $this->Form->create('User', array('class' => 'well')); ?>
    <?php
        echo $this->Form->input('username');
        echo $this->Form->input('password');
    ?>
<?php	echo $this->Form->button('Log in', array('type'=>'submit','class' => 'btn')); ?>
</div>
