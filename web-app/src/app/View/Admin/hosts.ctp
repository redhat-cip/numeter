<?
// create the admin_top_menu block.
$this->start('admin_top_menu');
echo $this->element('admin_top_menu');
$this->end();

// Display admin_top_menu
echo $this->fetch('admin_top_menu');
?>
<h3>Host list</h3>


<div class=row>
    <div class=span12>
        <div class='span7 offset4'>
            <h4>Hosts in Database</h4>
            <table class="table table-condensed table-striped">
                <tr>
                    <th>storage</th>
                    <th>name</th>
                    <th>address</th>
                    <th>id</th>
                    <th><a href="/admin/hosts/hostrefreshall" ><i class="icon-repeat"></i></a></th>
                </tr>
                <?  $hostIDinDB = array();
                    foreach ($hosts as $host): 
                        array_push($hostIDinDB,$host['Host']['storageID'].$host['Host']['hostID']);
                ?>
                    <tr>
                        <td><?=$host['Host']['storageID'];?></td>
                        <td><?=$host['Host']['name'];?></td>
                        <td><?=$host['Host']['addr'];?></td>
                        <td><?=$host['Host']['hostID'];?></td>
                        <td>
                            <div class="btn-group">
                              <a class="btn btn-primary dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
                              <ul class="dropdown-menu">
                                <li><a href="/admin/hosts/hostrefresh/<?=$host['Host']['id'];?>/<?=$host['Host']['hostID'];?>"><i class="icon-repeat"></i> Refresh</a></li>
                                <li><a href="#" OnClick="(delConfirm(<?="'".$host['Host']['id']."','".$host['Host']['name']."'"; ?>));"><i class="icon-trash"></i> Delete</a></li>

                              </ul>
                            </div>
                        </td>
                    </tr>
                <? endforeach; ?>
            </table>
            <div style="padding-top: 19px;"></div>
            <h4>Hosts not referenced</h4>
            <table class="table table-condensed table-striped">
                <tr>
                    <th>storage</th>
                    <th>name</th>
                    <th>address</th>
                    <th>id</th>
                    <th>&nbsp;</th>
                </tr>
                <? foreach ($hostsInStorage as $storageID => $storages): ?>
                    <? foreach ($storages as $host): 
                        if (in_array($storageID.$host['ID'],$hostIDinDB))
                            continue;
                    ?>
                        <tr>
                            <td><?=$storageID;?></td>
                            <td><?=$host['Name'];?></td>
                            <td><?=$host['Address'];?></td>
                            <td><?=$host['ID'];?></td>
                            <td>
                                <div class="btn-group">
                                  <a class="btn btn-primary dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
                                  <ul class="dropdown-menu">
                                    <li><a href="/admin/hosts/hostadd/<?=$storageID;?>/<?=$host['ID'];?>"><i class="icon-plus"></i> Ajouter</a></li>
                                  </ul>
                                </div>
                            </td>
                        </tr>
                    <? endforeach; ?>
                <? endforeach; ?>
            </table>
        </div>
    </div>
</div>

<!-- Modal Delete confirm-->
<div class="modal hide" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true"></button>
    <h3 id="myModalLabel">Delete host</h3>
  </div>
  <div class="modal-body">
    <p>Delete host : <div id="delHost"></div></p>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">Cancel</button>
    <a id="yesButton" href="/admin/hosts" class="btn btn-primary">Yes</a>
  </div>
</div>


<? if( $status == 'nok'): ?>
    <div class="alert alert-error">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Error!</h4>
        No host id
    </div>
<? elseif ($status == 'okdel'):  ?>
    <div class="alert alert-success">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Success!</h4>
        Host deleted
    </div>
<? elseif ($status == 'okadd'):  ?>
    <div class="alert alert-success">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Success!</h4>
        Host added
    </div>
<? elseif ($status == 'okref'):  ?>
    <div class="alert alert-success">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <h4>Success!</h4>
        Host refresh
    </div>
<? endif; ?>


<script type="text/javascript">
    function delConfirm(id,name) {
        $('#myModal').modal('show');
        $("#delHost").html('<b>'+name+'</b>');
        $("#yesButton").attr('href', '/admin/hosts/hostdel/'+id);
    }
</script>  
