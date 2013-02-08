<h1>Groups Listing</h1><br>
<div class=row>
<div class=span12>
<div class='span4 offset4'>
    <form class="well form-search">
        <input type="text" class="input-medium search-query">
        <button type="submit" class="btn">Search</button>
    </form>
    <br>
    <table class="table table-condensed table-striped">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Users</th>
            <th>Hosts</th>
        </tr>
        <?php foreach ($groups as $values): ?>
            <? $groupInfos = $values['Group']; ?>
            <? $userGroup = $values['User']; ?>
            <? $hostGroup = $values['Host']; ?>
            <? $userList=""; ?>
            <?php foreach ($userGroup as $userInfos):
                      $userList .= $userInfos['username']."<br>";
                  endforeach; ?>
            <? $hostList=""; ?>
            <?php foreach ($hostGroup as $hostInfos):
                      $hostList .= $hostInfos['name']."<br>";
                  endforeach; ?>
            <tr>
                <td><?php echo $groupInfos['id']; ?></td>
                <td><?php echo $groupInfos['name']; ?></td>
                <td><?php echo $userList; ?></td>
                <td><?php echo $hostList; ?></td>
                <td><a href=/groups/listplugins/<?php echo $storage."/".$groupInfos['ID']; ?> class="btn btn-mini">Editer</a></td>
            </tr>
        <?php endforeach; ?>
    </table>
</div>
</div>
</div>
