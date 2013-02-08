<ul class="nav nav-tabs">                                                                                                                                                                                                                   
  <li <?php if($context == 'index') { echo 'class="active"'; } ?>><a href="/admin">Index</a></li>
  <li <?php if($context == 'users') { echo 'class="active"'; } ?>><a href="/admin/users">Users</a></li>
  <li <?php if($context == 'groups') { echo 'class="active"'; } ?>><a href="/admin/groups">Groups</a></li>
  <li <?php if($context == 'hosts') { echo 'class="active"'; } ?>><a href="/admin/hosts">Hosts</a></li>
</ul>
