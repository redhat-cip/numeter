<?
// create the admin_top_menu block.
$this->start('admin_top_menu');
echo $this->element('admin_top_menu');
$this->end();

// Display admin_top_menu
echo $this->fetch('admin_top_menu');
?>
<h3>User list</h3>

<div class=row>
    <div class=span12>
        <div class='span4 offset4'>
            <table class="table table-condensed table-striped">
                <tr>
                    <th>id</th>
                    <th>name</th>
                    <th>admin</th>
                    <th><a class="btn btn-inverse btn-small" href="/admin/useradd">Ajout</a></th>
                </tr>
                <? foreach ($users as $user): ?>
                    <tr>
                        <td><?=$user['User']['id'];?></td>
                        <td><?=$user['User']['username'];?></td>
                        <td><? if($user['User']['isadmin']) echo '<i class="icon-ok">'; else echo '<i class="icon-minus">'; ?></i></td>
                        <td>
                            <div class="btn-group">
                              <a class="btn btn-primary dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
                              <ul class="dropdown-menu">
                                <li><a href="/admin/usermod/<?=$user['User']['id'];?>"><i class="icon-pencil"></i> Edit</a></li>
                                <li><a href="#" OnClick="(delConfirm(<?="'".$user['User']['id']."','".$user['User']['username']."'"; ?>));"><i class="icon-trash"></i> Delete</a></li>
                              </ul>
                            </div>
                        </td>
                    </tr>
                <? endforeach; ?>
            </table>
        </div>
    </div>
</div>
<!-- Modal Delete confirm-->
<div class="modal hide" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true"></button>
    <h3 id="myModalLabel">Delete user</h3>
  </div>
  <div class="modal-body">
    <p>Delete user : <div id="delUser"></div></p>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">Cancel</button>
    <a id="yesButton" href="/admin/users" class="btn btn-primary">Yes</a>
  </div>
</div>


<? if( $status == 'nok'): ?>
    <div class="alert alert-error">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Error!</h4>
        No user id
    </div>
<? elseif ($status == 'ok'):  ?>  
    <div class="alert alert-success">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Success!</h4>
        User deleted
    </div>
<? endif; ?>

<script type="text/javascript">
    function delConfirm(id,name) {
        $('#myModal').modal('show');
        $("#delUser").html('<b>'+name+'</b>');
        $("#yesButton").attr('href', '/admin/users/userdel/'+id);
    }

</script>
