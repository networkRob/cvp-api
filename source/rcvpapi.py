import requests, json


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
    def _sendRequest(self,c_meth,url,payload={}):
        response = requests.request(c_meth,url,json=payload,headers=self.cvp_headers,verify=False)
        return(response.json())
    def getSID(self,c_user,c_pwd):
        url = 'https://{0}/cvpservice/login/authenticate.do'.format(self.cvp_url)
        payload = {
            'userId':c_user,
            'password':c_pwd
            }
        response = self._sendRequest("POST",url,payload)
        self.cvp_headers['Cookie'] = 'session_id={}'.format(response['sessionId'])
        return(response['sessionId'])
    def _checkSession(self):
        url = 'https://{0}/cvpservice/login/home.do'.format(self.cvp_url)
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
        url = 'https://{0}/cvpservice/cvpInfo/getCvpInfo.do'.format(self.cvp_url)
        if self._checkSession():
            return(self._sendRequest("GET",url))