<?
// create the admin_top_menu block.
$this->start('admin_top_menu');
echo $this->element('admin_top_menu');
$this->end();

// Display admin_top_menu
echo $this->fetch('admin_top_menu');
?>
<h3>Group list</h3>


<div class=row>
    <div class=span12>
        <div class='span4 offset4'>
            <table class="table table-condensed table-striped">
                <tr>
                    <th>id</th>
                    <th>name</th>
                    <th><a class="btn btn-inverse btn-small" href="/admin/groupadd">Ajout</a></th>
                </tr>
                <? foreach ($groups as $group): ?>
                    <tr>
                        <td><?=$group['Group']['id'];?></td>
                        <td><?=$group['Group']['name'];?></td>
                        <td>
                            <div class="btn-group">
                              <a class="btn btn-primary dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
                              <ul class="dropdown-menu">
                                <li><a href="/admin/groupmod/<?=$group['Group']['id'];?>"><i class="icon-pencil"></i> Edit</a></li>
                                <li><a href="#" OnClick="(delConfirm(<?="'".$group['Group']['id']."','".$group['Group']['name']."'"; ?>));"><i class="icon-trash"></i> Delete</a></li>
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
    <h3 id="myModalLabel">Delete group</h3>
  </div>
  <div class="modal-body">
    <p>Delete group : <div id="delGroup"></div></p>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">Cancel</button>
    <a id="yesButton" href="/admin/groups" class="btn btn-primary">Yes</a>
  </div>
</div>

<? if( $status == 'nok'): ?>
    <div class="alert alert-error">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Error!</h4>
        No group id
    </div>
<? elseif ($status == 'ok'):  ?>  
    <div class="alert alert-success">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Success!</h4>
        Group deleted
    </div>
<? endif; ?>

<script type="text/javascript">
    function delConfirm(id,name) {
        $('#myModal').modal('show');
        $("#delGroup").html('<b>'+name+'</b>');
        $("#yesButton").attr('href', '/admin/groups/groupdel/'+id);
    }
</script>
