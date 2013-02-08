<?php
class GroupsController extends AppController {
    public $helpers = array('Html', 'Form');

    public function index() {
        $this->set('authUser', $this->Auth->user());

       // Group model
       $params = array(
           //'fields' => array('name', 'hosts'),
           //'conditions' => array('title' => 'hehe'),
           //'conditions' => array('hoge' => array('$gt' => '10', '$lt' => '34')),
           //'order' => array('title' => 1, 'body' => 1),
           'order' => array('id' => -1),
           'limit' => 0,
           'page' => 1,
       );
        //$groups = $this->Group->find('all', $params);
        $groups = $this->Group->find('all');
        //$groups = $this->Group->find();
        $this->set(compact('groups'));
        var_dump($groups);
    }

}
