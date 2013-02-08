<?php
class HostsController extends AppController {
    public $helpers = array('Html', 'Form');

    public function index() {
        
        $this->set('authUser', $this->Auth->user());

        // Get group in session
        $sessionGroup = $this->Session->read('Auth.Group');
        $arrayGroup = array();
        foreach( $sessionGroup as $value ) {
            array_push($arrayGroup, $value['id']); 
        }

        // Get Group model
        $this->Group = ClassRegistry::init('Group');
        
        // Get hosts in groups
        // if admin no params (list all groups)
        if ($this->Auth->user()['isadmin']) {
            $params = array();
        } else {
            $params = array(
                'conditions' => array(
                    'Group.id' => $arrayGroup
                )
            );
        }
        $hosts = $this->Group->find('all',$params);

//        // Make array of all hosts
//        $hosts = array();
//        foreach ($groups as $value) {
//            foreach ($value['Host'] as $host) {
//                array_push($hosts, $host);
//            }
//        }

        $this->set(compact('hosts'));

        //$this->pretty_var($hosts);

        //$hostsDB = $this->Host->find('all', $params);

        //$this->set(compact('hostsDB'));
        //var_export($hostsDB);
        //$this->pretty_var($hostsDB);
    }



// Disable (no view)
//    public function host() {
//        App::uses('HttpSocket', 'Network/Http');
//        $HttpSocket = new HttpSocket();
//        $results = $HttpSocket->get('http://127.0.0.1:8080/numeter-storage/hosts');
//        $this->set('hosts', json_decode($results,true));
//        $this->set('authUser', $this->Auth->user());
//    }

    private function pretty_var($myArray){
        print str_replace(array("\n"," "),array("<br>","&nbsp;"), var_export($myArray,true))."<br>";
    } 

    public function listplugins() {
        // /listplugins/<storageID>/<hostID>/[Plugin]/[Periode]
        App::import('Controller', 'Storageapi');
        $storageAPI = new StorageapiController;
        $getParams=$this->params['pass'];
        $storageID = $getParams[0];
        $hostID = $getParams[1];
        $this->set('authUser', $this->Auth->user());
        // Get host infos
        $host_info = json_decode($storageAPI->get(array('hinfo',$storageID,$hostID)), true);
        $host_name = ($host_info['Name'] != "") ? $host_info['Name'] : $hostID;
        // get plugin list
        $results = json_decode($storageAPI->get(array('list',$storageID,$hostID)),true);
        // Sort plugins by category
        $plugins = array();
        foreach ($results["list"] as $plugin){
            $plugin = json_decode($plugin,true);
            if ($plugin['Category'] != '')
                $category=$plugin['Category'];
            else
                $category="other";

            if (empty($plugins[$category]))
                $plugins[$category]=array(); 

            array_push($plugins[$category], $plugin); 
        }
        ksort($plugins);

        if($getParams[2]) {
            if($getParams[3])
                $period=$getParams[3];
            else
                $period="Daily";
            $cur_plugin = $getParams[2];
            $this->set(compact('period'));
            $this->set(compact('cur_plugin'));
            $this->set(compact('plugins'));
            // Get plugin infos
            $plugin_info = json_decode($storageAPI->get(array('info',$storageID,$hostID,$cur_plugin)),true);
            $this->set(compact('plugin_info'));
            $infos=$plugin_info;
            $allDS="";
            foreach ($infos['Infos'] as $key => $value) {
                if(!$allDS)
                    $allDS=$key;
                else
                    $allDS="$key,$allDS";
            }
            // Get plugin data
            $datas = json_decode($storageAPI->get(array('data',$storageID,$hostID,$cur_plugin,$allDS,$period)),true);
            $this->set(compact('datas'));
        }
        else {
            reset($plugins);
            $first = current($plugins);
            $this->redirect("/hosts/listplugins/$storageID/$hostID/".$first[0]['Plugin']);
        }

        $this->set('graphType', $this->Auth->user('graph'));
        $this->set(compact('host_name'));
        $this->set(compact('hostID'));
        $this->set(compact('storageID'));
    }
}
