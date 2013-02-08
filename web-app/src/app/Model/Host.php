<?php
class Host extends AppModel {
    public $name = 'Host';
    //public $primaryKey = 'hostID';
    public $primaryKey = 'id';
    //var $useDbConfig = 'mongo';
    /* var $mongoSchema = array(
                    'HostID' => array('type'=>'string'),
                    'name' => array('type'=>'string'),
                    'addr'=>array('type'=>'string'),
                    );
    */

    public $hasAndBelongsToMany = array(    
        'Group' =>
            array(
                'className'              => 'Group',
                'joinTable'              => 'group_host_memberships',
                'foreignKey'             => 'host_id',
                'associationForeignKey'  => 'group_id',
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
}
