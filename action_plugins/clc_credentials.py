__author__ = 'brianalbrecht'

import requests
import clc
import os
from ansible.runner.return_data import ReturnData

class ActionModule(object):
    ''' Create inventory hosts and groups in the memory inventory'''

    ### We need to be able to modify the inventory
#    BYPASS_HOST_LOOP = True
    TRANSFERS_FILES = False

    def __init__(self, runner):
        self.runner = runner
        self.clc = clc

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):

        # import pydevd
        # pydevd.settrace('localhost', port=5001, stdoutToServer=True, stderrToServer=True)

        hostname = inject["inventory_hostname"]

        ansible_ssh_user, ansible_ssh_password = self.find_credentials(hostname)
        creds_fact = {
                      "ansible_ssh_user": ansible_ssh_user,
                      "ansible_ssh_pass": ansible_ssh_password
                     }

        return ReturnData(conn=conn, comm_ok=True, result=dict(ansible_facts=creds_fact))

    def find_credentials(self, hostname):
        self._set_clc_credentials_from_env()
        creds = clc.v2.Server(hostname).Credentials()
        return creds["userName"], creds["password"]

    def _set_clc_credentials_from_env(self):
        """
        Set the CLC Credentials on the sdk by reading environment variables
        :return: none
        """
        env = os.environ
        v2_api_token = env.get('CLC_V2_API_TOKEN', False)
        v2_api_username = env.get('CLC_V2_API_USERNAME', False)
        v2_api_passwd = env.get('CLC_V2_API_PASSWD', False)
        clc_alias = env.get('CLC_ACCT_ALIAS', False)
        api_url = env.get('CLC_V2_API_URL', False)

        if api_url:
            self.clc.defaults.ENDPOINT_URL_V2 = api_url

        if v2_api_token and clc_alias:
            self.clc._LOGIN_TOKEN_V2 = v2_api_token
            self.clc._V2_ENABLED = True
            self.clc.ALIAS = clc_alias
        elif v2_api_username and v2_api_passwd:
            self.clc.v2.SetCredentials(
                api_username=v2_api_username,
                api_passwd=v2_api_passwd)
        # else:
        #     return self.module.fail_json(
        #         msg="You must set the CLC_V2_API_USERNAME and CLC_V2_API_PASSWD "
        #             "environment variables")