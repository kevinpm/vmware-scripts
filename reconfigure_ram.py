#!/usr/bin/env python
"""
Script to modify the RAM size of an existing VM
This is for demonstration purposes only.
Unless Memory Hot Plug is enabled, the VM must be powered off in order to change the RAM settings
"""
from pyVmomi import vim
from pyVmomi import vmodl
from pyVim.connect import SmartConnect, Disconnect
import atexit
import argparse
import getpass


def get_args():
    parser = argparse.ArgumentParser(
        description='Arguments for talking to vCenter')

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSpehre service to connect to')

    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use')

    parser.add_argument('-v', '--vm-name',
                        required=False,
                        action='store',
                        help='name of the vm')

    parser.add_argument('--uuid',
                        required=False,
                        action='store',
                        help='vmuuid of vm')

    parser.add_argument('--ram-size',
                        required=True,
                        action='store',
                        help='RAM size, in GB, to add to the VM')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password')

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


def add_ram(vm, si, ram_size):
    config = vim.vm.ConfigSpec()
    config.memoryMB = (ram_size * 1024)
    # Enable memory and CPU Hot Plug 
    config.cpuHotRemoveEnabled = True
    config.cpuHotAddEnabled = True
    config.memoryHotAddEnabled = True

    task = vm.ReconfigVM_Task(spec=config)


def main():
    args = get_args()

    # connect this thing
    si = SmartConnect(
        host=args.host,
        user=args.user,
        pwd=args.password,
        port=args.port)
    # disconnect this thing
    atexit.register(Disconnect, si)

    vm = None
    if args.uuid:
        search_index = si.content.searchIndex
        vm = search_index.FindByUuid(None, args.uuid, True)
    elif args.vm_name:
        content = si.RetrieveContent()
        vm = get_obj(content, [vim.VirtualMachine], args.vm_name)

    if vm:
        add_ram(vm, si, int(args.ram_size))
    else:
        print ("VM not found")


# start this thing
if __name__ == "__main__":
    main()
