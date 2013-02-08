<?php
class Group extends AppModel {

    public $primaryKey = 'id';

    //public $hasMany = array(
    //    'GroupMembership'
    //);

    public $hasAndBelongsToMany = array(                                                                                                                                                                                                
        'User' =>
            array(
                'className'              => 'User',
                'joinTable'              => 'group_user_memberships',
                'foreignKey'             => 'group_id',
                'associationForeignKey'  => 'user_id',
                'unique'                 => true,
                'conditions'             => '',
                'fields'                 => '',
                'order'                  => '',
                'limit'                  => '',
                'offset'                 => '',
                'finderQuery'            => '',
                'deleteQuery'            => '',
                'insertQuery'            => ''
            ),
        'Host' =>
            array(
                'className'              => 'Host',
                'joinTable'              => 'group_host_memberships',
                'foreignKey'             => 'group_id',
                'associationForeignKey'  => 'host_id',
                'unique'                 => true,
                'conditions'             => '',
                'fields'                 => '',
                'order'                  => '',
                'limit'                  => '',
                'offset'                 => '',
                'finderQuery'            => '',
                'deleteQuery'            => '',
                'insertQuery'            => ''
            )
    );

    //public $hasMany = 'Host';
    //public $hasMany = array(
    //    'Host' => array(
    //        'className'  => 'Host',
    //        'foreignKey'    => 'hostID',
    //        //'conditions'    => array('Host.hostID' => '1'),
    //        //'foreignKey'    => 'hostID',
    //        //'conditions' => array('Recette.approvee' => '1'),
    //        //'order'      => 'Recette.created DESC'
    //    )
    //);
    //public $hasAndBelongsToMany = array(
    //    'host' =>
    //        array(
    //            'className'              => 'Host',
    //            'joinTable'              => 'ingredients_recipes',
    //            'foreignKey'             => 'recipe_id',
    //            'associationForeignKey'  => 'ingredient_id',
    //            //'unique'                 => true,
    //            'conditions'             => '',
    //            'fields'                 => '',
    //            'order'                  => '',
    //            'limit'                  => '',
    //            'offset'                 => '',
    //            'finderQuery'            => '',
    //            'deleteQuery'            => '',
    //            'insertQuery'            => ''
    //        )
    //);
    //var $useDbConfig = 'mongo';
    /* var $mongoSchema = array(
                    'name' => array('type'=>'string'),
                    'hosts' => array('type'=>'array'),
                    );
    */


    public function parentNode() {
        return null;
    }
}
