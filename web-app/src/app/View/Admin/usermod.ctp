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
                <form class="form-horizontal" action="/admin/usermod/<?=$users['id']; ?>" id="PostUsermodForm" method="post" accept-charset="utf-8">
                    <input type="hidden" name="_method" value="POST"/>
                    <input type="hidden" name="data[Post][id]" id="PostId" value="<?=$users['id']; ?>" />
                    <div class="control-group">
                        <label class="control-label" for="PostName">Name</label>
                        <div class="controls">
                            <input name="data[Post][name]" type="text" id="PostName" placeholder="Name" value="<?=$users['username']; ?>"/>
                        </div>
                    </div>
                    <div class="control-group<? if($status=='nok') echo ' error';?>">
                        <label class="control-label" for="PostPassword">Password</label>
                        <div class="controls">
                            <input name="data[Post][password]" type="password" id="PostPassword" placeholder="Password"/>
                            <? if($status=='nok') echo '<span class="help-inline">Password confirmation error</span>';?>
                        </div>
                    </div>
                    <div class="control-group<? if($status=='nok') echo ' error';?>">
                        <label class="control-label" for="PostPasswordConfirm">Confirm password</label>
                        <div class="controls">
                            <input name="data[Post][password_confirm]" type="password" id="PostPasswordConfirm" placeholder="Password"/>
                            <? if($status=='nok') echo '<span class="help-inline">Password confirmation error</span>';?>
                        </div>
                    </div>
                    <div class="control-group">
                        <div class="controls">
                            <label class="checkbox">
                                <input name="data[Post][isadmin]" id="PostIsadmin" type="checkbox" <? if ($users['isadmin']) { echo 'checked'; } ?> > Administrateur
                            </label>
                            <button type="submit" class="btn">Modify</button>
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


<? if(! $users): ?>
    <div class="alert alert-error">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Error!</h4>
        No user id
    </div>
<? elseif ($status == 'ok'):  ?>
    <div class="alert alert-success">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Success!</h4>
        User modification success
    </div>
<? elseif ($status == 'nok'):  ?>
    <div class="alert alert-info">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Warning!</h4>
        Incorrect informations
    </div>
<? endif; ?>


<div class="well well-small">
    test
</div>


