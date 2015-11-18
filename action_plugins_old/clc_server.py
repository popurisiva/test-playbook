__author__ = 'brianalbrecht'

from ansible.utils.plugins import action_loader
import os

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

        for server in module_return.result['servers']:
            print '---> Returned server object : {0} <---'.format(str(server))
            server_name = server['name']

            ansible_ssh_user, ansible_ssh_pass = self._find_credentials(server_name)
            server_ip = server['ipaddress']
            data_center = server['locationId']

            print '---> Server IP: {0}'.format(server_ip)
            print '---> Server Location: {0}'.format(data_center)

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

            self._add_ssh_config(server_ip, data_center)

        return module_return

    @staticmethod
    def _add_ssh_config(host_ip, data_center):
        fp = open(os.path.join(os.pardir, 'ssh_config'), 'a+')
        #ssh_bastion_host = 'SBAST-{0}.service.consul'.format(data_center)
        ssh_bastion_host = 'SBAST-UC1-WFTC.service.consul'
        fp.write('Host {0}\n'.format(host_ip))
        fp.write('ProxyCommand ssh -o StrictHostKeyChecking=no -q -A root@{0} nc %h %p\n\n'.format(
            ssh_bastion_host))
        fp.close()

    def _find_credentials(self, server_name):
        clc_credentials = action_loader.get("clc_credentials", self.runner)
        return clc_credentials.find_credentials(server_name)
