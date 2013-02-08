<?php
class AdminController extends AppController {

   public $helpers = array('Html', 'Form');

   public function index() {
       //$this->redirect('/admin/edit/users');    
       $this->set('authUser', $this->Auth->user());
       $context = "index";
       $this->set(compact('context'));
   }

//    public function edit() {
//        $this->set('authUser', $this->Auth->user());
//        $host=$this->params['pass'];
//        if($host[0]){
//            $context = $host[0];
//            $this->set('context', $host[0]);
//        } else {
//            $this->set('context','users');
//            $context = "users";
//        }
//    
//        if( $context == "users" ) {
//            //$this->User->create();
//        }
//    }

   public function users() {

        $context = "users";
        $this->set(compact('context'));
        $this->set('authUser', $this->Auth->user());

        //Get user liste
        $this->User = ClassRegistry::init('User');
        $users = $this->User->find('all');

        // Get url _GET
        $getParams = $this->params['pass'];
        if ($getParams[0] == 'userdel') {
            $userID = $getParams[1];
            if (! $userID) {
                $status = 'nok';
            } else {
                $this->User->delete($userID);
                $this->redirect('/admin/users/confirm');
            }
        } elseif ($getParams[0] == 'confirm') {
                $status = 'ok';
        }
        
        $this->set(compact('status'));
        $this->set(compact('users'));

   }

   public function useradd() {
        $context = "users";
        $this->set(compact('context'));
        $this->set('authUser', $this->Auth->user());

        // Get url _GET
        $getParams = $this->params['pass'];

        //Get user
        $this->User = ClassRegistry::init('User');
        $params =  array('fields' => 'User.username');
        $userInDb = $this->User->find('all', $params);

        if($this->request->is('post')) {
            if ($this->data['Post']['isadmin'] == 'on')
                $isadmin = 1;
            else
                $isadmin = 0;

            $this->User->create();
            //$this->User->set(array(
            $changes = array(
                'username' => $this->data['Post']['name'],
                'isadmin' => $isadmin
            );

            // If password change
            if ($this->data['Post']['password'] == $this->data['Post']['password_confirm'] && $this->data['Post']['password'] != "") {
                //$this->User->set('password',$this->data['Post']['password']);
                $changes['password'] = $this->data['Post']['password'];
            } else {
                $users['username'] = $this->data['Post']['name'];
                $users['isadmin'] = $isadmin;
                $status = 'nokpassword';
            }

            if ($this->data['Post']['name'] != '') {
                // Check username
                foreach($userInDb as $user) {
                    if ($user['User']['username'] == $this->data['Post']['name']) {
                        $status = 'noklogin';
                    }
                }
            } else {
                $status = 'noklogin';
            }

            // If no password error and login error, add user
            if ($status != 'nokpassword' && $status != 'noklogin') {
                $this->User->save($changes);
                //$this->User->save($this->User);
                $status = 'ok';
                $users = array();
            }
        }

        $this->set(compact('users'));
        $this->set(compact('status'));
   }

   public function usermod() {
        $context = "users";
        $this->set(compact('context'));
        $this->set('authUser', $this->Auth->user());

        // Get url _GET
        $getParams = $this->params['pass'];
        $userID = $getParams[0];

        //Get user liste
        $this->User = ClassRegistry::init('User');
        $params =  array('conditions' => array('User.id' => $userID));
        $users = $this->User->find('first', $params)['User'];

        if($this->request->is('post')) {
            if ($this->data['Post']['isadmin'] == 'on')
                $isadmin = 1;
            else
                $isadmin = 0;
            //$this->User->set(array(
            $changes = array(
                'id' => $this->data['Post']['id'],
                'username' => $this->data['Post']['name'],
                'isadmin' => $isadmin
            );

            // If password change
            if ($this->data['Post']['password'] != '') {
                if ($this->data['Post']['password'] == $this->data['Post']['password_confirm'] ) {
                    //$this->User->set('password',$this->data['Post']['password']);
                    $changes['password'] = $this->data['Post']['password'];
                } else {
                    $users['username'] = $this->data['Post']['name'];
                    $users['isadmin'] = $isadmin;
                    $status = 'nok';
                }
            }

            // If no password error, update and set ok
            if ($status != 'nok') {
                //$this->User->save($this->User);
                $this->User->save($changes);
                $status = 'ok';
                $users = $this->User->find('first', $params)['User'];
            }
        }

        $this->set(compact('users'));
        $this->set(compact('status'));
   }



   public function groups() {

        $context = "groups";
        $this->set(compact('context'));
        $this->set('authUser', $this->Auth->user());

        //Get group liste
        $this->Group = ClassRegistry::init('Group');
        $groups = $this->Group->find('all');

        // Get url _GET
        $getParams = $this->params['pass'];
        if ($getParams[0] == 'groupdel') {
            $groupID = $getParams[1];
            if (! $groupID) {
                $status = 'nok';
            } else {
                $this->Group->delete($groupID);
                $this->redirect('/admin/groups/confirm');
            }
        } elseif ($getParams[0] == 'confirm') {
                $status = 'ok';
        }
        
        $this->set(compact('status'));
        $this->set(compact('groups'));

   }

   public function groupadd() {
        $context = "groups";
        $this->set(compact('context'));
        $this->set('authUser', $this->Auth->user());

        // Get url _GET
        $getParams = $this->params['pass'];

        //Get user
        $this->Group = ClassRegistry::init('Group');
        $params =  array('fields' => 'Group.name');
        $groupInDb = $this->Group->find('all', $params);

        if($this->request->is('post')) {
            $this->Group->create();
            //$this->Group->name = $this->data['Post']['name'];
            $changes=array(
                'name' => $this->data['Post']['name']);

            if ($this->data['Post']['name'] != '') {
                // Check groupname
                foreach($groupInDb as $group) {
                    if ($group['Group']['name'] == $this->data['Post']['name']) {
                        $status = 'nokname';
                    }
                }
            } else {
                $status = 'nokname';
            }

            // if no name error add group
            if ($status != 'nokname') {
                $this->Group->save($changes);
                //$this->Group->save($this->Group);
                $status = 'ok';
                $groups = array();
            }
        }

        $this->set(compact('groups'));
        $this->set(compact('status'));
   }

   public function groupmod() {
        $context = "groups";
        $this->set(compact('context'));
        $this->set('authUser', $this->Auth->user());

        $this->Group = ClassRegistry::init('Group');

        // Get url _GET
        $getParams = $this->params['pass'];
        $groupID = $getParams[0];

        // if get post
        if($this->request->is('post')) {
            // Make host and user array
            $userArray = array(array());
            foreach($this->data['Post']['users'] as $value) {
                array_push($userArray, array('user_id' => $value));
            }
            $hostArray = array(array());
            foreach($this->data['Post']['hosts'] as $value) {
                array_push($hostArray, array('host_id' => $value));
            }

            $changes=array(
                'id' => $this->data['Post']['id'],
                'name' => $this->data['Post']['name'],
                'User' => $userArray,
                'Host' => $hostArray
            );

            // If no password error, update and set ok
            if ($status != 'nok') {
                $this->Group->save($changes);
                $status = 'ok';
            }
        }

        //Get group infos
        $params =  array('conditions' => array('Group.id' => $groupID));
        $groupInfos = $this->Group->find('first', $params);

        $group['Group'] = $groupInfos['Group'];

        // Get users in group
        $groupUsers = array();
        foreach ( $groupInfos['User'] as $value) {
            array_push( $groupUsers, $value['id'] );
        }

        // Get hosts in group
        $groupHosts = array();
        foreach ( $groupInfos['Host'] as $value) {
            array_push( $groupHosts, $value['id'] );
        }


        //Get all users
        $this->User = ClassRegistry::init('User');
        $params =  array('fields' => array('User.username','User.id'));
        $userInDb = $this->User->find('all', $params);
        //make user list
        $group['User_none'] = array();
        $group['User_selected'] = array();
        foreach($userInDb as $user) {   
            if (in_array($user['User']['id'], $groupUsers))
                $key = 'User_selected';
            else
                $key = 'User_none';

            array_push($group[$key], array( 
                    'username' => $user['User']['username'],
                    'id' => $user['User']['id']
            ));
        }
        // Modgroup with old select input
        //$group['User'] = array();
        //foreach($userInDb as $user) {   
        //    if (in_array($user['User']['id'], $groupUsers))
        //        $inGroup = 1;
        //    else
        //        $inGroup = 0;

        //    array_push($group['User'], array( 
        //            'username' => $user['User']['username'],
        //            'id' => $user['User']['id'],
        //            'inGroup' => $inGroup
        //    ));
        //}
        //$group['Host'] = array();
        //foreach($hostInDb as $host) {   
        //    if (in_array($host['Host']['id'], $groupHosts))
        //        $inGroup = 1;
        //    else
        //        $inGroup = 0;
        //    array_push($group['Host'], array( 
        //            'name' => $host['Host']['name'],
        //            'id' => $host['Host']['id'],
        //            'inGroup' => $inGroup
        //    ));
        //}

        //Get all hosts
        $this->Host = ClassRegistry::init('Host');
        $params =  array('fields' => array('Host.name','Host.id'));
        $hostInDb = $this->Host->find('all', $params);
        //make host list
        $group['Host_none'] = array();
        $group['Host_selected'] = array();
        foreach($hostInDb as $host) {   
            if (in_array($host['Host']['id'], $groupHosts))
                $key = 'Host_selected';
            else
                $key = 'Host_none';

            array_push($group[$key], array( 
                    'name' => $host['Host']['name'],
                    'id' => $host['Host']['id'],
                    'inGroup' => $inGroup
            ));
        }


        $this->set(compact('group'));
        $this->set(compact('status'));
   }

    public function hosts() {
        $context = "hosts";
        $this->set(compact('context'));
        $this->set('authUser', $this->Auth->user());

        //Get host list
        $this->Host = ClassRegistry::init('Host');
        $hosts = $this->Host->find('all');

        //Get host list in storages
        App::import('Controller', 'Storageapi');
        $storageAPI = new StorageapiController;
        $results = $storageAPI->get(array('hosts'));
        $hostsInStorage = json_decode($results,true);

        // Get url _GET
        $getParams = $this->params['pass'];
        // IF delete host
        if ($getParams[0] == 'hostdel') {
            $hostID = $getParams[1];
            if (! $hostID) {
                $status = 'nok';
            } else {
                $this->Host->delete($hostID);
                $this->redirect('/admin/hosts/confirmdel');
            }
        // IF add host
        } elseif ($getParams[0] == 'hostadd' && $getParams[1] != "" && $getParams[2] != "") {
            $storageID  = $getParams[1];
            $hostID     = $getParams[2];
            $this->Host->create();
            $changes = array(
                'name' => $hostsInStorage[$storageID][$hostID]['Name'],
                'addr' => $hostsInStorage[$storageID][$hostID]['Address'],
                'hostID' => $hostsInStorage[$storageID][$hostID]['ID'],
                'storageID' => $storageID
            );
            $this->Host->save($changes);
            $this->redirect('/admin/hosts/confirmadd');
        // IF refresh host
        } elseif ($getParams[0] == 'hostrefresh' 
        && $getParams[1] != "" 
        && $getParams[2] != "") {
            $id         = $getParams[1];
            $hostID     = $getParams[2];
            $storageID = $this->find_storage_id($hostsInStorage,$hostID);
            $changes = array(
                'id' => $id,
                'name' => $hostsInStorage[$storageID][$hostID]['Name'],
                'addr' => $hostsInStorage[$storageID][$hostID]['Address'],
                //'hostID' => $hostsInStorage[$storageID][$hostID]['ID'],
                'storageID' => $storageID
            );
            $this->Host->save($changes);
            $this->redirect('/admin/hosts/confirmrefresh');
        // IF refresh all hosts
        } elseif ($getParams[0] == 'hostrefreshall') {
            foreach($hosts as $host) {
                $id = $host['Host']['id'];
                $hostID = $host['Host']['hostID'];
                $storageID = $this->find_storage_id($hostsInStorage,$hostID);
                $changes = array(
                    'id' => $id,
                    'name' => $hostsInStorage[$storageID][$hostID]['Name'],
                    'addr' => $hostsInStorage[$storageID][$hostID]['Address'],
                    //'hostID' => $hostsInStorage[$storageID][$hostID]['ID'],
                    'storageID' => $storageID
                );
                $this->Host->save($changes);
            }
            $this->redirect('/admin/hosts/confirmrefresh');
        } elseif ($getParams[0] == 'confirmrefresh') {
                $status = 'okref';
        } elseif ($getParams[0] == 'confirmadd') {
                $status = 'okadd';
        } elseif ($getParams[0] == 'confirmdel') {
                $status = 'okdel';
        }
        $this->set(compact('status'));
        $this->set(compact('hosts'));
        $this->set(compact('hostsInStorage'));
    }

    private function find_storage_id($hostsInStorage,$hostID) {
        foreach ($hostsInStorage as $storageID => $value){
            foreach ($value as $host){
                if ($host['ID'] == $hostID)
                    return $storageID;
            }
        }
        return null;
    }

    private function pretty_var($myArray){
        print str_replace(array("\n"," "),array("<br>","&nbsp;"), var_export($myArray,true))."<br>";
    }  
}
