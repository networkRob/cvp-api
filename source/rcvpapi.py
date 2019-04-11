import requests, json

class CVPSWITCH():
    def __init__(self,host,vx_ip,t_cnt):
        self.serial_num = ""
        self.fqdn = ""
        self.hostname = host
        self.ip = vx_ip
        self.targetContainerName = t_cnt
        self.parentContainer = ""
        self.sys_mac = ""
        self.configlets = {"keys":[],"names":[]}
    
    def updateContainer(self,CVPOBJ):
        """
        Function that updates the container information for the EOS device.
        Parameters:
        CVPOBJ = CVPCON class object that contains information about CVP (required)
        """
        CVPOBJ.getDeviceInventory()
        self.sys_mac = CVPOBJ.inventory[self.hostname]["systemMacAddress"]
        self.parentContainer = CVPOBJ.getContainerInfo(CVPOBJ.inventory[self.hostname]["parentContainerKey"])

# ==================================
# Class definition for working with CVP
# ==================================
class CVPCON():
    def __init__(self,cvp_url,c_user,c_pwd):
        self.cvp_url = cvp_url
        self.cvp_user = c_user
        self.cvp_pwd = c_pwd
        self.inventory = {}
        self.tasks = {}
        self.cvp_api = {
            'authenticate': 'cvpservice/login/authenticate.do',
            'logout': 'cvpservice/login/logout.do',
            'checkSession': 'cvpservice/login/home.do',
            'checkVersion': 'cvpservice/cvpInfo/getCvpInfo.do',
            'searchTopo': 'cvpservice/provisioning/searchTopology.do',
            'getContainer': 'cvpservice/inventory/containers?name=',
            'getContainerInfo': '/cvpservice/provisioning/getContainerInfoById.do',
            'addTempAction': 'cvpservice/provisioning/addTempAction.do',
            'deviceInventory': 'cvpservice/inventory/devices',
            'saveTopo': 'cvpservice/provisioning/v2/saveTopology.do',
            'getAllTemp': 'cvpservice/provisioning/getAllTempActions.do?startIndex=0&endIndex=0',
            'getAllTasks': 'cvpservice/task/getTasks.do',
            'executeAllTasks': 'cvpservice/task/executeTask.do',
            'getTaskStatus': 'cvpservice/task/getTaskStatusById.do',
            'generateCB': 'cvpservice/configlet/autoConfigletGenerator.do',
            'getTempConfigs': 'cvpservice/provisioning/getTempConfigsByNetElementId.do',
            'createSnapshot': 'cvpservice/snapshot/templates/schedule',
            'getAllSnapshots': 'cvpservice/snapshot/templates'
        }
        self.headers = {
            'Content-Type':'application/json',
            'Accept':'application/json'
        }
        self.SID = self.getSID()
        self.containers = {
            'Tenant': {'name':'Tenant','key':self.getContainerId('Tenant')[0]["Key"]},
            'Undefined': {'name':'Undefined','key':self.getContainerId('Undefined')[0]["Key"]}
        }
        self.getDeviceInventory()
        self.getAllSnapshots()

    def _sendRequest(self,c_meth,url,payload={}):
        """
        Generic function that will send the API call to CVP. 
        Parameters:
        c_meth = API method, ie "GET or "POST" (required)
        url = The API url that is located in self.cvp_api (required)
        payload = data/payload required for the API call, if needed (optional)
        """
        response = requests.request(c_meth,"https://{}/".format(self.cvp_url) + url,json=payload,headers=self.headers,verify=False)
        return(response.json())
    
    def _checkSession(self):
        if 'Cookie' in self.headers.keys():
            pass
        else:
            pass
        response = self._sendRequest("GET",self.cvp_api['checkSession'])
        if type(response) == dict:
            if response['data'] == 'success':
                return(True)
            else:
                return(False)
        else:
            return(False)

    def checkVersion(self):
        if self._checkSession():
            return(self._sendRequest("GET",self.cvp_api['cvpservice/checkVersion']))
    
    def saveTopology(self):
        """
        Function that saves all Temporary Provisioning Actions/Tasks
        """
        payload = self._sendRequest("GET",self.cvp_api['getAllTemp'])['data']
        response = self._sendRequest("POST",self.cvp_api['saveTopo'],payload)
        return(response)
        
    def getSID(self):
        """
        Function that authenticates to CVP and stores the session_id cookie to the headers for future calls.
        """
        payload = {
            'userId':self.cvp_user,
            'password':self.cvp_pwd
        }
        response = self._sendRequest("POST",self.cvp_api['authenticate'],payload)
        self.headers['Cookie'] = 'session_id={}'.format(response['sessionId'])
        return(response['sessionId'])
    
    def execLogout(self):
        """
        Function to terminate CVP Session
        """
        response = self._sendRequest("POST",self.cvp_api['logout'])
        pS("OK","Logged out of CVP")
        return(response)
    
    def saveTopo(self):
        payload = []
        response = self._sendRequest("POST",self.cvp_api['saveTopo'],payload)
        return(response)
    
    def getContainerId(self,cnt_name):
        """
        Function to get the key for a container
        Parameters:
        cnt_name = container name (required)
        """
        response = self._sendRequest("GET",self.cvp_api['getContainer'] + cnt_name)
        return(response)
    
    def getContainerInfo(self,cnt_key):
        """
        Function to get all information on a container.
        Parameters:
        cnt_key = Container key/id (required)
        """
        response = self._sendRequest("GET",self.cvp_api['getContainerInfo'] + '?containerId={0}'.format(cnt_key))
        return(response)

    def addContainer(self,cnt_name,pnt_name):
        """
        Function to add a new container.
        Parameters:
        cnt_name = New Container to be created (required)
        pnt_name = Parent container where the new container should be nested within (required)
        """
        msg = "Creating {0} container under the {1} container".format(cnt_name,pnt_name)
        payload = {
            'data': [
                {
                    'info': msg,
                    'infoPreview': msg,
                    'action': 'add',
                    'nodeType': 'container',
                    'nodeId': 'new_container',
                    'toId': self.containers[pnt_name]["key"],
                    'fromId': '',
                    'nodeName': cnt_name,
                    'fromName': '',
                    'toName': self.containers[pnt_name]["name"],
                    'childTasks': [],
                    'parentTask': '',
                    'toIdType': 'container'
                }
            ]
        }
        response = self._sendRequest("POST",self.cvp_api['addTempAction'] + "?format=topology&queryParam=&nodeId=root",payload)
        return(response)

    def addDeviceInventory(self,eos_ip):
        """
        Function that adds a device to inventory
        Parameters:
        eos_ip = MGMT IP address for the EOS device (required)
        """
        payload = {
            "hosts": [eos_ip]
        }
        response = self._sendRequest("POST",self.cvp_api['deviceInventory'],payload)
        return(response)
    
    def getDeviceInventory(self):
        """ 
        Function that gets all Provisioned devices within CVP.
        """
        response = self._sendRequest("GET",self.cvp_api['deviceInventory'] + "?provisioned=true")
        for res in response:
            self.inventory[res['hostname']] = {"fqdn":res['fqdn'],'ipAddress':res['ipAddress'],'parentContainerKey':res['parentContainerKey'],"systemMacAddress":res["systemMacAddress"]}
    
    def moveDevice(self,eos_obj):
        """
        Function that moves a device from one container to another container.
        Parameters:
        eos_obj = CVPSWITCH class object that contains relevant device info (required)
        """
        msg = "Moving {0} device under the {1} container".format(eos_obj.hostname,eos_obj.targetContainerName)
        payload = {
            'data': [
                {
                    'info': msg,
                    'infoPreview': msg,
                    'action': 'update',
                    'nodeType': 'netelement',
                    'nodeId': eos_obj.sys_mac,
                    'toId': self.containers[eos_obj.targetContainerName]["key"],
                    'fromId': self.containers[eos_obj.parentContainer["name"]]["key"],
                    'nodeName': eos_obj.hostname,
                    'fromName': eos_obj.parentContainer["name"],
                    'toName': eos_obj.targetContainerName,
                    'childTasks': [],
                    'parentTask': '',
                    'toIdType': 'container'
                }
            ]
        }
        response = self._sendRequest("POST",self.cvp_api['addTempAction'] + "?format=topology&queryParam=&nodeId=root",payload)
        return(response)

    def getAllTasks(self,t_type):
        """
        Function that gets all Tasks.
        Parameters:
        t_type = Task type to query on, ie "Pending" (required)
        """
        response = self._sendRequest("GET",self.cvp_api['getAllTasks'] + "?queryparam={0}&startIndex=0&endIndex=0".format(t_type))
        self.tasks[t_type] = response['data']
    
    def execAllTasks(self,t_type):
        """
        Function that executes all tasks
        Parameters:
        t_type = Task type to execute on, ie "Pending" (required)
        """
        data = []
        if t_type in self.tasks.keys():
            if self.tasks[t_type]:
                for task in self.tasks[t_type]:
                    data.append(task['workOrderId'])
        if data:
            payload = {"data": data }
            response = self._sendRequest("POST",self.cvp_api['executeAllTasks'],payload)
            for task in data:
                while True:
                    t_response = self.getTaskStatus(task)
                    if 'Task Update In Progress' not in t_response['taskStatus']:
                        pS("OK","Task Id: {0} has {1}".format(task,t_response['taskStatus']))
                        break
                    else:
                        pS("INFO","Task Id: {0} Still in progress....sleeping".format(task))
                        sleep(10)
            self.getAllTasks(t_type)
            return(response)
    
    def getTaskStatus(self,t_id):
        """
        Function to get teh status of a particular Task ID.
        Parameters:
        t_id = Task Id (required)
        """
        response = self._sendRequest("GET",self.cvp_api['getTaskStatus'] + "?taskId={0}".format(t_id))
        return(response)
    
    def getTempConfigs(self,eos_obj,c_type):
        """
        Function that gets all configs assigned to a device.
        Parameters:
        eos_obj = CVPSWITCH class object that contains relevant EOS device info (required)
        c_type = Configlet type, ie "Builder", "Static" (required)
        """
        ret_configs = []
        cnvt_id = eos_obj.sys_mac.replace(":","%3A")
        response = self._sendRequest("GET",self.cvp_api['getTempConfigs'] + "?netElementId={0}".format(cnvt_id))
        for p_config in response['proposedConfiglets']:
            if p_config['type'] == c_type:
                ret_configs.append(p_config['key'])
            if p_config['type'] != "Builder":
                eos_obj.configlets["keys"].append(p_config['key'])
                eos_obj.configlets["names"].append(p_config['name'])
        return(ret_configs)
    
    def genConfigBuilders(self,eos_obj):
        """
        Function to generate all ConfigletBuilders assigned to a particular device.
        Parameters:
        eos_obj = CVPSWICH class object that contains all relevant EOS device info (required)
        """
        payload = {
            'netElementIds':[eos_obj.sys_mac],
            'containerId': self.containers[eos_obj.targetContainerName]['key'],
            'pageType': 'netelement'
        }
        tmp_cb = self.getTempConfigs(eos_obj,"Builder")
        for cb in tmp_cb:
            payload['configletBuilderId'] = cb
            response = self._sendRequest("POST",self.cvp_api['generateCB'],payload)
            eos_obj.configlets["keys"].append(response['data'][0]['configlet']['key'])
            eos_obj.configlets["names"].append(response['data'][0]['configlet']['name'])
        return(response)
    
    def applyConfiglets(self,eos_obj):
        """ 
        Function that applies all configlets assigned to a device.
        Parameters:
        eos_obj = CVPSWITCH class object that contails all relevant EOS device info (required)
        """
        msg = "Applying configlets to {0}".format(eos_obj.hostname)
        payload = {
            'data': [
                {
                    'info': msg,
                    'infoPreview': msg,
                    'action': 'associate',
                    'nodeType': 'configlet',
                    'configletList': eos_obj.configlets["keys"],
                    'configletNamesList': eos_obj.configlets["names"],
                    'ignoreConfigletNamesList': [],
                    'ignoreConfigletList': [],
                    'configletBuilderList': [],
                    'configletBuilderNamesList': [],
                    'ignoreConfigletBuilderList': [],
                    'ignoreConfigletBuilderNamesList': [],
                    'nodeId': '',
                    'toId': eos_obj.sys_mac,
                    'fromId': '',
                    'nodeName': '',
                    'fromName': '',
                    'toName': eos_obj.fqdn,
                    'nodeIpAddress': eos_obj.ip,
                    'nodeTargetIpAddress': eos_obj.ip,
                    'childTasks': [],
                    'parentTask': '',
                    'toIdType': 'netelement'
                }
            ]
        }
        response = self._sendRequest("POST",self.cvp_api['addTempAction'] + "?format=topology&queryParam=&nodeId=root",payload)
        return(response)
    
    def createSnapshot(self,snap_name,snap_cmds,snap_devices=[]):
        """
        Function that creates snapshot templates.
        Parameters:
        snap_name = Name of the snapshot (required)
        snap_cmds = All commands to be included in snapshot (required)
        snap_devices = Devices to be included on the snapshot (optional)
        """
        payload = {
            'name': snap_name,
            'commands': snap_cmds,
            'deviceList': snap_devices,
            'frequency': '300'
        }
        response = self._sendRequest("POST",self.cvp_api['createSnapshot'],payload)
        self.getAllSnapshots()
        return(response)

    def getAllSnapshots(self):
        """
        Function to get all configured snapshots on CVP
        """
        response = self._sendRequest("GET",self.cvp_api['getAllSnapshots'] + "?startIndex=0&endIndex=0")
        self.snapshots = response['templateKeys']