<?
// create the admin_top_menu block.
$this->start('admin_top_menu');
echo $this->element('admin_top_menu');
$this->end();

// Display admin_top_menu
echo $this->fetch('admin_top_menu');
?>
<h3> User modification</h3>

<div class=row>
    <div class=span12>
        <div class='span4 offset4'>
            <div class="posts form"> 
                <form class="form-horizontal" action="/admin/useradd" id="PostUsermodForm" method="post" accept-charset="utf-8">
                    <input type="hidden" name="_method" value="POST"/>
                    <div class="control-group<? if($status=='noklogin') echo ' error';?>">
                        <label class="control-label" for="PostName">Name</label>
                        <div class="controls">
                            <input name="data[Post][name]" type="text" id="PostName" placeholder="Name" value="<?=$users['username']; ?>"/>
                            <? if($status=='noklogin') echo '<span class="help-inline">Change your user name</span>';?>
                        </div>
                    </div>
                    <div class="control-group<? if($status=='nokpassword') echo ' error';?>">
                        <label class="control-label" for="PostPassword">Password</label>
                        <div class="controls">
                            <input name="data[Post][password]" type="password" id="PostPassword" placeholder="Password"/>
                            <? if($status=='nokpassword') echo '<span class="help-inline">Password confirmation error</span>';?>
                        </div>
                    </div>
                    <div class="control-group<? if($status=='nokpassword') echo ' error';?>">
                        <label class="control-label" for="PostPasswordConfirm">Confirm password</label>
                        <div class="controls">
                            <input name="data[Post][password_confirm]" type="password" id="PostPasswordConfirm" placeholder="Password"/>
                            <? if($status=='nokpassword') echo '<span class="help-inline">Password confirmation error</span>';?>
                        </div>
                    </div>
                    <div class="control-group">
                        <div class="controls">
                            <label class="checkbox">
                                <input name="data[Post][isadmin]" id="PostIsadmin" type="checkbox" <? if ($users['isadmin']) { echo 'checked'; } ?> > Administrateur
                            </label>
                            <button type="submit" class="btn">Add</button>
                        </div>
                    </div>
                </form>
                <ul>
                    <li><?php echo $this->Html->link(__('User list', true), array('action'=>'users'));?></li>
                </ul>
            </div>
        </div>
    </div>
</div>


<? if ($status == 'ok'):  ?>
    <div class="alert alert-success">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Success!</h4>
        Add user success
    </div>
<? elseif ($status == 'nokpassword'):  ?>
    <div class="alert alert-info">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Warning!</h4>
        Incorrect informations
    </div>
<? elseif ($status == 'noklogin'):  ?>
    <div class="alert alert-info">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Warning!</h4>
        User name already exist
    </div>
<? endif; ?>


