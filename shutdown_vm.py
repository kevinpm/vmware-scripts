#!/usr/bin/env python
"""
vSphere Python SDK program for shutting down VMs
"""
from __future__ import print_function

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl

import argparse
import atexit
import getpass
import sys
import ssl



def GetArgs():
   """
   Supports the command-line arguments listed below.
   """

   parser = argparse.ArgumentParser(description='Process args for shutting down a Virtual Machine')
   parser.add_argument('-s', '--host', required=True, action='store', help='Remote host to connect to')
   parser.add_argument('-o', '--port', type=int, default=443, action='store', help='Port to connect on')
   parser.add_argument('-u', '--user', required=True, action='store', help='User name to use when connecting to host')
   parser.add_argument('-p', '--password', required=False, action='store', help='Password to use when connecting to host')
   parser.add_argument('-v', '--vm-name', required=True, action='store', help='Names of the Virtual Machines to shutdown')
   args = parser.parse_args()
   return args


def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def main():
    """
   Simple command-line program for shutting down virtual machines on a system. 
   """

    args = GetArgs()
    if args.password:
      password = args.password
    else:
      password = getpass.getpass(prompt='Enter password for host %s and user %s: ' % (args.host,args.user))

    service_instance = None

    try:
        service_instance = SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port))
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1

        atexit.register(Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        # Search for all VMs
        vm = None

        if args.vm_name:
            content = service_instance.RetrieveContent()
            vm = get_obj(content, [vim.VirtualMachine], args.vm_name)

        if vm:
            print("Shutting down VM: %s" % vm.name)
            vm.ShutdownGuest()
        else:
            print ("VM not found")

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + e.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()
