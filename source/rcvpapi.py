import requests, json

class CVPSWITCH():
    def __init__(self,sw):
        self.serial_num = sw['serialNumber']
        self.fqdn = sw['fqdn']
        self.hostname = sw['hostname']
        self.ip = sw['ipAddress']
        self.com_code = sw['complianceCode']
        self.com_status = sw['complianceIndication']
        self.eos_version = sw['version']
        self.streaming = sw['streamingStatus']
        self.sys_mac = sw['systemMacAddress']
        self.status = sw['status']
        self.all_data = sw

class CVPCON():
    def __init__(self,cvp_url,c_user,c_pwd):
        self.cvp_url = cvp_url
        self.cvp_user = c_user
        self.cvp_pwd = c_pwd
        self.cvp_headers = {
            'Content-Type':'application/json',
            'Accept':'application/json'
        }
        self.cur_sid = self.getSID(c_user,c_pwd)
        self.cvp_version = self._checkVersion()
        self.cvp_inventory = []
        self.cvp_inventory_sn = []

    def _sendRequest(self,c_meth,url,payload={}):
        response = requests.request(c_meth,"https://{}/".format(self.cvp_url) + url,json=payload,headers=self.cvp_headers,verify=False)
        return(response.json())

    def getSID(self,c_user,c_pwd):
        url = 'cvpservice/login/authenticate.do'
        payload = {
            'userId':c_user,
            'password':c_pwd
            }
        response = self._sendRequest("POST",url,payload)
        self.cvp_headers['Cookie'] = 'session_id={}'.format(response['sessionId'])
        return(response['sessionId'])

    def _checkSession(self):
        url = 'cvpservice/login/home.do'
        if 'Cookie' in self.cvp_headers.keys():
            pass
        else:
            pass
        response = self._sendRequest("GET",url)
        if type(response) == dict:
            if response['data'] == 'success':
                return(True)
            else:
                return(False)
        else:
            return(False)

    def _checkVersion(self):
        url = 'cvpservice/cvpInfo/getCvpInfo.do'
        if self._checkSession():
            return(self._sendRequest("GET",url))

    def getDevices(self):
        url = 'cvpservice/inventory/devices'
        if self._checkSession():
            response = self._sendRequest("GET",url)
            for device in response:
                if device['serialNumber'] not in self.cvp_inventory_sn:
                    self.cvp_inventory.append({device['serialNumber']:CVPSWITCH(device)})
                    self.cvp_inventory_sn.append(device['serialNumber'])

    def getConfiglets(self):
        url = 'cvpservice/configlet/getConfiglets.do?startIndex=0&endIndex=0'
        if self._checkSession():
            response = self._sendRequest("GET",url)
            return(response)
        else:
            return({
                "status":"failed"
            })

