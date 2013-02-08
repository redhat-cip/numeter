<?
// create the admin_top_menu block.
$this->start('admin_top_menu');
echo $this->element('admin_top_menu');
$this->end();

// Display admin_top_menu
echo $this->fetch('admin_top_menu');
?>
<h3> Group add</h3>

<div class="row">
    <div class="span12">
        <div class='span4 offset4'>
            <div class="posts form"> 
                <form class="form-horizontal" action="/admin/groupadd" id="PostGroupmodForm" method="post" accept-charset="utf-8">
                    <input type="hidden" name="_method" value="POST"/>
                    <div class="control-group<? if($status=='nokname') echo ' error';?>">
                        <label class="control-label" for="PostName">Name</label>
                        <div class="controls">
                            <input name="data[Post][name]" type="text" id="PostName" placeholder="Name" value="<?=$groups['name']; ?>"/>
                            <? if($status=='nokname') echo '<span class="help-inline">Change your group name</span>';?>
                        </div>
                    </div>
                    <div class="control-group">
                        <div class="controls">
                            <button type="submit" class="btn">Add</button>
                        </div>
                    </div>
                </form>
                <ul>
                    <li><?php echo $this->Html->link(__('Group list', true), array('action'=>'groups'));?></li>
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
<? elseif ($status == 'nokname'):  ?>
    <div class="alert alert-info">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Warning!</h4>
        Group name already exist
    </div>
<? endif; ?>
