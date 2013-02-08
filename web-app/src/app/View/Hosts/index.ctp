<h1>Hosts Listing</h1><br>
<div class=row>
<div class=span12>
<div class='span4 offset4'>
    <form class="well form-search">
        <input type="text" class="input-medium search-query">
        <button type="submit" class="btn">Search</button>
    </form>
    <br>
    <?php foreach ($hosts as $value): //for each groups ?>
        <div style="padding-top: 15px; padding-bottom: 5px; ">
            <button type="button" class="btn btn-inverse btn-mini" disabled>Group : <?php echo $value['Group']['name']; ?></button>
        </div>
        <table class="table table-condensed table-striped">
            <tr>
                <th>Storage</th>
                <th>Name</th>
                <th>IP</th>
                <th>Go on Host Page</th>
            </tr>
            <? //Sort host name
               foreach ($value['Host'] as $key => $row) { $host_name[$key]  = $row['name']; }
               array_multisort($host_name, SORT_ASC, $value['Host']); $i=0;  ?>

            <?php foreach ($value['Host'] as $hostInfos): // for each hosts in group?>
                <tr>
                    <td><?php echo $hostInfos['storageID']; ?></td>
                    <td><?php echo $hostInfos['name']; ?></td>
                    <td><?php echo $hostInfos['addr'] ?></td>
                    <td><a href=/hosts/listplugins/<?php echo $hostInfos['storageID']."/".$hostInfos['hostID']; ?> class="btn btn-mini">View</a></td>
                </tr>
            <?php endforeach; ?>
        </table>
    <?php endforeach; ?>
</div>
</div>
</div>
