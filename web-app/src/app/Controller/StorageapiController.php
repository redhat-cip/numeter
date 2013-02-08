<?php
class StorageapiController extends AppController {

    public function index() {
        $this->layout = 'ajax';
        $result = "{}";
        $this->set(compact('result'));
    }

    private function getDefault() {
        return "{}";
    }

    // GET HOSTS
    private function getHosts($baseUrl, $storages) {
        // param /storageapi/get/hosts
        App::uses('HttpSocket', 'Network/Http');
        $HttpSocket = new HttpSocket();
        for ( $id=0 ; $id < count($storages) ; $id++ ) {
            $resultsJson = json_decode($HttpSocket->get("http://".$storages[$id]."/".$baseUrl."/hosts"));
            $results->{$id} = $resultsJson;
        }
        $results = json_encode($results);
        return $results; // return json of all hosts
    }

    // GET LIST
    private function getList($baseUrl, $storages, $args) {
        // args /storageapi/get/list/<storageID>/<hostID>
        if ($args[1] >= count($storages) || count($args) < 3 )  {
            return "{}";
        }
        // args filter
        $idStorage = $args[1];
        $idHost    = $args[2];
        if ( ! preg_match ('/^[0-9]+$/', $idStorage) 
          || ! preg_match ('/^[A-Za-z0-9_\-\.]+$/', $idHost)) {
            return "{}";
        }
        App::uses('HttpSocket', 'Network/Http');
        $HttpSocket = new HttpSocket();
        $results = $HttpSocket->get("http://".$storages[$idStorage]."/".$baseUrl."/list?host=".$idHost);
        return $results;
    }

    // GET HINFO
    private function getHinfo($baseUrl, $storages, $args) {
        // args /storageapi/get/hinfo/<storageID>/<hostID>
        if ($args[1] >= count($storages) || count($args) < 3 )  {
            return "{}";
        }
        // args filter
        $idStorage = $args[1];
        $idHost    = $args[2];
        if ( ! preg_match ('/^[0-9]+$/', $idStorage) 
          || ! preg_match ('/^[A-Za-z0-9_\-\.]+$/', $idHost)) {
            return "{}";
        }
        App::uses('HttpSocket', 'Network/Http');
        $HttpSocket = new HttpSocket();
        $results = $HttpSocket->get("http://".$storages[$idStorage]."/".$baseUrl."/hinfo?host=".$idHost);
        return $results;
    }

    // GET INFO
    private function getInfo($baseUrl, $storages, $args) {
        // args /storageapi/get/info/<storageID>/<hostID>/<plugin>
        if ($args[1] >= count($storages) || count($args) < 4 )  {
            return "{}";
        }
        // args filter
        $idStorage = $args[1];
        $idHost    = $args[2];
        $plugin    = $args[3];
        if ( ! preg_match ('/^[0-9]+$/', $idStorage) 
          || ! preg_match ('/^[A-Za-z0-9_\-\.]+$/', $idHost) 
          || ! preg_match ('/^[A-Za-z0-9_\-\.]+$/', $plugin)) {
            return "{}";
        }
        App::uses('HttpSocket', 'Network/Http');
        $HttpSocket = new HttpSocket();
        $results = $HttpSocket->get("http://".$storages[$idStorage]."/".$baseUrl."/info?host=".$idHost
                                                                                ."&plugin=".$plugin);
        return $results;
    }

    // GET DATA
    private function getData($baseUrl, $storages, $args) {
        // args /storageapi/get/data/<storageID>/<hostID>/<plugin>/<ds>,<ds>,.../<resolution> (Daily|Weekly|Monthly|Yearly)
        if ($args[1] >= count($storages) || count($args) < 6 )  {
            return "{}";
        }
        // args filter
        $idStorage  = $args[1];
        $idHost     = $args[2];
        $plugin     = $args[3];
        $ds         = $args[4];
        $resolution = $args[5];
        if ( ! preg_match ('/^[0-9]+$/', $idStorage) 
          || ! preg_match ('/^[A-Za-z0-9_\-\.]+$/', $idHost) 
          || ! preg_match ('/^[A-Za-z0-9_\-\.]+$/', $plugin) 
          || ! preg_match ('/^[A-Za-z0-9_\-\.,]+$/', $ds) 
          || ! preg_match ('/^(Daily|Weekly|Monthly|Yearly)$/', $resolution) ) {
            return "{}";
        }
        App::uses('HttpSocket', 'Network/Http');
        $HttpSocket = new HttpSocket();
        $results = $HttpSocket->get("http://".$storages[$idStorage]."/".$baseUrl."/data?host=".$idHost
                                                                                     ."&plugin=".$plugin
                                                                                     ."&ds=".$ds
                                                                                     ."&res=".$resolution);
        return $results;
    }


    // MAIN
    public function get($getParams) {
        // Load storage configuration
        Configure::load('storage');
        $storageConfig = Configure::read('Storage');
        // Disable default html head
        $this->layout = 'ajax';
        // URL : /storageapi/get/action/arg1/arg2/...
        //       /storageapi/get/[0]/[1][...]
        // getParams (import) = array | getParams (url) = string
        if (gettype($getParams) != 'array') {
            $getParams = $this->params['pass'];   
        }
        switch ($getParams[0]) {
            case 'hosts':
                $result = $this->getHosts($storageConfig['baseUrl'], $storageConfig['address']);
                break;
            case 'hinfo':
                $result = $this->getHinfo($storageConfig['baseUrl'], $storageConfig['address'], $getParams);
                break;
            case 'list':
                $result = $this->getList($storageConfig['baseUrl'], $storageConfig['address'], $getParams);
                break;
            case 'info':
                $result = $this->getInfo($storageConfig['baseUrl'], $storageConfig['address'], $getParams);
                break;
            case 'data':
                $result = $this->getData($storageConfig['baseUrl'], $storageConfig['address'], $getParams);
                break;
            default:
                $result = $this->getDefault();
       }
        $this->set(compact('result'));
        return $result;
    }
}


