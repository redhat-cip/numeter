<?
// create the admin_top_menu block.
$this->start('admin_top_menu');
echo $this->element('admin_top_menu');
$this->end();

// Display admin_top_menu
echo $this->fetch('admin_top_menu');
?>
<h3> Group modification</h3>

<div class=row>
    <div class=span12>
        <div class='offset4'>
            <form class="form-horizontal" action="/admin/groupmod/<?=$group['Group']['id']; ?>" id="PostGroupmodForm" method="post" accept-charset="utf-8">
                <input type="hidden" name="_method" value="POST"/>
                <input type="hidden" name="data[Post][id]" id="PostId" value="<?=$group['Group']['id']; ?>" />
                <div class="control-group">
                    <label class="control-label" for="PostName">Name</label>
                    <div class="controls">
                        <input name="data[Post][name]" type="text" id="PostName" placeholder="Name" value="<?=$group['Group']['name']; ?>"/>
                    </div>
                </div>
                    <!--<label class="control-label" for="PostName">Users</label>-->
                    <!-- BEGIN: Users mod --> 
                    <div id="users_input"></div>
                    <div id="users-mod"> 
                        <div class="column left first"> 
                        <b style='padding-left: 10px'>Users</b>
                            <ul class="sortable-list"> 
                                <? foreach($group['User_none'] as $user): ?>
                                    <li class="sortable-item" id="<?=$user['id']; ?>"><?=$user['username']; ?></li> 
                                <? endforeach; ?>
                            </ul> 
                        </div> 
                        <div class="column left column_users"> 
                        <b style='padding-left: 10px'>Users in group</b>
                            <ul class="sortable-list sortable-selected-users" id="selected-users"> 
                                <? foreach($group['User_selected'] as $user): ?>
                                    <li class="sortable-item sortable-item-selected" id="<?=$user['id']; ?>"><?=$user['username']; ?></li> 
                                <? endforeach; ?>
                            </ul> 
                        </div> 
                    </div> 
                    <!-- END: Users mod -->
                    <!-- <label class="control-label" for="PostName">Hosts</label> -->
                    <!-- BEGIN: Hosts mod --> 
                    <div id="hosts_input"></div>
                    <div id="hosts-mod"> 
                        <div class="column left first column_hosts"> 
                        <b style='padding-left: 10px'>Hosts in group</b>
                            <ul class="sortable-list sortable-selected-hosts" id="selected-hosts"> 
                                <? foreach($group['Host_selected'] as $host): ?>
                                    <li class="sortable-item sortable-item-selected" id="<?=$host['id'];?>"><?=$host['name'];?></li> 
                                <? endforeach; ?>
                            </ul> 
                        </div> 
                        <div class="column left"> 
                        <b style='padding-left: 10px'>Hosts</b>
                            <ul class="sortable-list"> 
                                <? foreach($group['Host_none'] as $host): ?>
                                    <li class="sortable-item" id="<?=$host['id'];?>"><?=$host['name'];?></li> 
                                <? endforeach; ?>
                            </ul> 
                        </div> 
                        <div class="clearer">&nbsp;</div> 
                    </div> 
                    <!-- END: Hosts mod -->
                <div class="control-group">
                    <div class="controls">
                        <!--<button type="submit" class="btn">Modify</button>-->
                        <input type="submit" class="input-button" id="btn-get" value="Modify" />
                    </div>
                </div>
            </form>
            <ul>
                <li><?php echo $this->Html->link(__('Group list', true), array('action'=>'groups'));?></li>
            </ul>
        </div>
    </div>
</div>

<? if(! $group): ?>
    <div class="alert alert-error">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Error!</h4>
        No group id
    </div>
<? elseif ($status == 'ok'):  ?>
    <div class="alert alert-success">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Success!</h4>
        Group modification success
    </div>
<? elseif ($status == 'nok'):  ?>
    <div class="alert alert-info">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Warning!</h4>
        Incorrect informations
    </div>
<? endif; ?>
<!-- <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.0/jquery-ui.min.js"></script> -->
<script type="text/javascript"> 
    $(document).ready(function(){
        // Get items
        function getItems(idItem)
        {
            return $(idItem).sortable('toArray');
        }
        // get button
        $('#btn-get').click(function(){
            var selectedUser = getItems('#selected-users');
            for (var userID in selectedUser) {  
                $('#users_input').append('<input name="data[Post][users][]" value="'+selectedUser[userID]+'" type="hidden">');
            };
            var selectedUser = getItems('#selected-hosts');
            for (var userID in selectedUser) {  
                $('#hosts_input').append('<input name="data[Post][hosts][]" value="'+selectedUser[userID]+'" type="hidden">');
            };
            $('#PostGroupmodForm').submit();
        });

        // users: Sortable and connectable lists
        $('#users-mod .sortable-list').sortable({
            connectWith: '#users-mod .sortable-list'
        });
        // hosts: Sortable and connectable lists
        $('#hosts-mod .sortable-list').sortable({
            connectWith: '#hosts-mod .sortable-list'
        });
    });
</script> 
