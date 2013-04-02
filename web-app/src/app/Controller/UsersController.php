<?php
    class UsersController extends AppController {    
    var $name = 'Users';



    public function index() {

       // Host model
       $params = array(
           //'fields' => array('hostID', 'name', 'addr'),
           //'fields' => array('Post.title', ),
           //'conditions' => array('title' => 'hehe'),
           //'conditions' => array('hoge' => array('$gt' => '10', '$lt' => '34')),
           //'order' => array('title' => 1, 'body' => 1),
           //'order' => array('_id' => -1),
           'limit' => 35,
           'page' => 1,
       );
        $users = $this->User->find('all', $params);

//$options['joins'] = array(
//    array('table' => 'group_host_memberships',
//        //'alias' => 'BooksTag',
//        'type' => 'inner',
//        'conditions' => array(
//            'Host.hostID = group_host_memberships.host_id'
//        )
//    ),
//    array('table' => 'group_user_memberships',
//        //'alias' => 'Tag',
//        'type' => 'inner',
//        'conditions' => array(
//            'group_host_memberships.group_id = group_user_memberships.group_id'
//        )
//    ),
//    array('table' => 'users',
//        //'alias' => 'Tag',
//        'type' => 'inner',
//        'conditions' => array(
//            'group_user_memberships.user_id = users.id'
//        )
//    )
//);
//$options['fields'] = array('users.username', 'users.id','hostID', 'name', 'addr');
//$hostsDB = $this->Host->find('all', $options);

        $this->set(compact('users'));
        //var_export($hostsDB);
        $this->pretty_var($users);
    }


    private function pretty_var($myArray){
        print str_replace(array("\n"," "),array("<br>","&nbsp;"), var_export($myArray,true))."<br>";
    } 


    // Pas nécessaire si déclaré dans votre contrôleur app        
    /**    * Le Composant Auth fournit la fonctionnalité nécessaire    
    * pour le login, donc vous pouvez laisser cette fonction vide.    */    
    function logout() {        
        $this->Session->destroy();
        $this->redirect($this->Auth->logout());
    }

    public function beforeFilter() {
            parent::beforeFilter();
            //$this->Auth->allow('add'); // Letting users register themselves
    }
    
    public function login() {
            if ($this->request->is('post')) {
                if ($this->Auth->login()) {
                    //Write group in session
                    $params = array('conditions' => array('User.id' => $this->Session->read('Auth.User.id')));
                    $groups = array();
                    foreach( $this->User->find('first', $params)['Group'] as $value) {
                        array_push($groups,array( 'id' => $value['id'], "name" => $value['name']));
                    }
                    $this->Session->write('Auth.Group', $groups);
                    $this->redirect($this->Auth->redirect());
                } else {
                    $this->Session->setFlash(__('Invalid username or password, try again'));
                }
            }
    }

    // Refresh user session infos
    private function userReload() { 
        $this->Session->write('Auth', $this->User->read(null, $this->Auth->user('id')));
    } 

    public function profile() {
        
        $this->set('authUser', $this->Auth->user());

        // Get graph display
        Configure::load('graph');
        $graphConfig = Configure::read('Graph');
        $this->set('graphs',$graphConfig["display"]);

        if($this->request->is('post')) {
            //$User = $this->Auth->user();
            //$this->User->create();
            //$toto = $this->User->find('first', array('conditions' => array('User.username' => 'test')));
            //$this->User->id = $toto['User']['id'];
            //$this->User->id = $this->Session->read('Auth.User.id');
            $this->User->set('id', $this->Session->read('Auth.User.id'));
            $this->User->set('graph', $this->data['Profile']['Graph']);
            $this->User->save($this->User);
            // reload for $this->Auth->user('graph')
            $this->userReload();
        }
    }
}
