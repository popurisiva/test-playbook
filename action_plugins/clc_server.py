__author__ = 'brianalbrecht'

from ansible.utils.plugins import action_loader
from ansible.runner.return_data import ReturnData
import json

class ActionModule(object):

    BYPASS_HOST_LOOP = False
    TRANSFERS_FILES = False

    def __init__(self, runner):
        self.runner = runner

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):
    	print '---->Inside the action plugin for module : {0}<----'.format(module_name)
        module_return = self.runner._execute_module(conn=conn,
                                                    tmp=tmp,
                                                    module_name=module_name,
                                                    args=module_args,
                                                    inject=inject,
                                                    complex_args=complex_args,
                                                    **kwargs)
        # with open("response_payload.json") as fp:
        #     result = json.load(fp)
        # module_return = ReturnData(conn=conn, comm_ok=True, result=result)

        for server in module_return.result['servers']:
            server_name = server['name']

            ansible_ssh_user, ansible_ssh_pass = self._find_credentials(server_name)

            server_args = {
                "name": server['name'],
                "ansible_ssh_host": server['ipaddress'],
                "ansible_ssh_user": ansible_ssh_user,
                "ansible_ssh_pass": ansible_ssh_pass,
                "groupname": complex_args['group']
            }
            add_host = action_loader.get("add_host", self.runner)
            add_host.run(conn=conn,
                         tmp=tmp,
                         module_name="add_host",
                         module_args=None,
                         inject=inject,
                         complex_args=server_args,
                         **kwargs)

        return module_return

    def _find_credentials(self, server_name):
        clc_credentials = action_loader.get("clc_credentials", self.runner)
        return clc_credentials.find_credentials(server_name)
