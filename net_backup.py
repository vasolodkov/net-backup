#!/usr/bin/env python3

#
# create file config.yaml with similar parameters
#
# 'tftp_server': '1.1.1.1'
# 'tftp_folder': 'net'
# 'rt_ips':
#     - '10.10.10.1'
#     - '10.10.10.2'
# 'rt_c800':
#     - '10.10.20.1'
#     - '10.10.20.2'
# 'sw_ips':
#     - '10.10.30.1'
#     - '10.10.30.2'
# 'nexus_ips':
#     - '10.10.40.1'
#     - '10.10.40.2'
# 'nxos_ips':
#     - '10.10.50.1'
#     - '10.10.50.2'
# 'forti_ips':
#     - '10.10.60.1'
#     - '10.10.60.2'
# 'ssh_user': 'user'
# 'ssh_pass': 'password'
#

import time
from netmiko import ConnectionHandler
import ruamel.yaml as yaml


def connection(devices):
    for device in devices:
        try:
            filename = device['ip'] + '-' + today + '.conf'
            save_cisco = 'copy running-config tftp://' \
                         + tftp_server + '/' + tftp_folder \
                         + '/' + filename
            save_forti = 'execute backup full-config tftp ' \
                         + tftp_folder + '/' + filename \
                         + ' ' + tftp_server
            net_connect = ConnectionHandler(**device)
            if devices == switches:
                output = net_connect.send_command(save_config)
                print(device['ip'], 'done', sep=': ')
            elif (devices == routers or devices == routers_c800 or
                  devices == nxos):
                output = net_connect.send_command(save_config,
                                                  expect_string=r']')
                output = net_connect.send_command('\n',
                                                  expect_string=r']',
                                                  delay_factor=3)
                print(device['ip'], 'done', sep=': ')
            elif devices == nexus:
                output = net_connect.send_command(save_config,
                                                  expect_string=r'Enter vrf')
                output = net_connect.send_command('\n',
                                                  expect_string=r'#',
                                                  delay_factor=3)
                print(device['ip'], 'done', sep=': ')
            elif devices == forti:
                output = net_connect.send_command(save_forti,
                                                  expect_string=r'\n')
                output = net_connect.send_command('\n',
                                                  expect_string=r'#')
                print(device['ip'], 'done', sep=': ')
            net_connect.disconnect()
        except Exception as e:
            print(e)
            print(f"check {device['ip']}")
            pass


def generate_devices(device_ips, device_type):
    devices = [{'device_type': device_type,
                'ip': device,
                'username': ssh_user,
                'password': ssh_pass} for device in device_ips]
    return devices

# Configuration options
with open('config.yaml') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

tftp_server = config['tftp_server']
tftp_folder = config['tftp_folder']
rt_ips = config['rt_ips']
rt_c800 = config['rt_c800']
sw_ips = config['sw_ips']
nexus_ips = config['nexus_ips']
nxos_ips = config['nxos_ips']
forti_ips = config['forti_ips']

# Specify the date and time for use in the filename created on the tftp server
hour = time.strftime('%H')
minute = time.strftime('%M')
day = time.strftime('%d')
month = time.strftime('%m')
year = time.strftime('%Y')
today = day + '-' + month + '-' + year + '-' + hour + minute

# Specify username and password for ssh
ssh_user = config['ssh_user']
ssh_pass = config['ssh_pass']

# Generating devices
switches = generate_devices(sw_ips, 'cisco_ios')
routers = generate_devices(rt_ips, 'cisco_ios')
routers_c800 = generate_devices(rt_c800, 'cisco_ios')
nexus = generate_devices(nexus_ips, 'cisco_xr')
nxos = generate_devices(nxos_ips, 'cisco_nxos')
forti = generate_devices(forti_ips, 'fortinet')

print('Backuping switches')
connection(switches)
print('Backuping routers')
connection(routers)
print('Backuping c800 routers')
connection(routers_c800)
print('Backuping nexuses')
connection(nexus)
print('Backuping nxos switches')
connection(nxos)
print('Backuping fortigates')
connection(forti)
