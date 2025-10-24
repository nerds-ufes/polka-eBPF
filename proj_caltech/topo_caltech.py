#!/usr/bin/python
# Copyright [2019-2022] Universidade Federal do Espirito Santo
#                       Instituto Federal do Espirito Santo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#############################################################################
################## TOPOLOGY with 5 SWITCHES CORE AND 5 HOSTS ################
#############################################################################
# 
# H1 (Polka-eBPF)     H3 (Polka-eBPF)
#       ||                  || 
#   SW POLKA 1 -------- SW POLKA 3 ---------------
#    |   |                     |                 |
#    |    =====================|========= SW POLKA 5 -------- H5 (Polka-eBPF)
#    |   |                     |                 |
#   SW POLKA 2 -------- SW POLKA 4 ---------------
#       ||                  ||
# H1 (Polka-eBPF)      H4 (Polka-eBPF)
#
#############################################################################
#############################################################################


import os
import sys
import subprocess
from subprocess import run

from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.bmv2 import P4Switch
from mininet.term import makeTerm
from mininet.node import RemoteController

# Kill BMv2 switch in use
os.system("sudo pkill -9 simple_switch")
os.system("sudo pkill -9 simple_switch_grpc")
os.system("sudo mn -c")

interfaces = ["s1-eth3", "s1-eth4", "s1-eth5", "s2-eth3", "s2-eth4", "s2-eth5",
 "s3-eth3", "s3-eth4", "s3-eth5", "s4-eth3", "s4-eth4", "s5-eth2", "s5-eth3",
 "s5-eth4"]

for interface in interfaces:
    subprocess.run(["sudo","ip","link","delete", interface])


n_switches = 5
BW = 10


def topology(remote_controller):
    "Create a network."
    net = Mininet()

    # linkopts = dict()
    switches = []
    edges = []
    hosts = []

    info("*** Adding hosts\n")
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')
    h5 = net.addHost('h5')


    info("*** Adding P4Switches (core)\n")
    for i in range(1, n_switches + 1):
        # read the network configuration
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = path + "/polka/polka-core.json"
        config = path + "/polka/config/s{}-commands.txt".format(i)
        # Add P4 switches (core)
        switch = net.addSwitch(
            "s{}".format(i),
            netcfg=True,
            json=json_file,
            thriftport=50000 + int(i),
            switch_config=config,
            loglevel='debug',
            cls=P4Switch,
        )
        switches.append(switch)

 

    info("*** Creating links\n")
    # for i in range(n_switches):
    net.addLink(h1, switches[0], bw=BW)
    net.addLink(h1, switches[0], bw=BW)
    net.addLink(h2, switches[1], bw=BW)
    net.addLink(h2, switches[1], bw=BW)
    net.addLink(h3, switches[2], bw=BW)
    net.addLink(h3, switches[2], bw=BW)
    net.addLink(h4, switches[3], bw=BW)
    net.addLink(h4, switches[3], bw=BW)
    net.addLink(h5, switches[4], bw=BW)

    net.addLink(switches[0], switches[1], bw=BW)
    net.addLink(switches[0], switches[2], bw=BW)
    net.addLink(switches[0], switches[4], bw=BW)

    net.addLink(switches[1], switches[3], bw=BW)
    net.addLink(switches[1], switches[4], bw=BW)

    net.addLink(switches[2], switches[3], bw=BW)
    net.addLink(switches[2], switches[4], bw=BW)

    net.addLink(switches[3], switches[4], bw=BW)


    info("*** Starting network\n")
    net.start()

    h1.setIP('10.0.1.1/32', intf='h1-eth0')
    h1.setMAC('00:00:00:00:01:01', intf='h1-eth0')
    h1.cmd("ip route add default dev h1-eth0")
    # h1.setIP('10.0.1.2/32', intf='h1-eth1')
    # h1.setMAC('00:00:00:00:01:02', intf='h1-eth1')

    h2.setIP('10.0.2.1/32', intf='h2-eth0')
    h2.setMAC('00:00:00:00:02:01', intf='h2-eth0')
    h2.cmd("ip route add default dev h2-eth0")
    # h2.setIP('10.0.2.2/32', intf='h2-eth1')
    # h2.setMAC('00:00:00:00:02:02', intf='h2-eth1')

    h3.setIP('10.0.3.1/32', intf='h3-eth0')
    h3.setMAC('00:00:00:00:03:01', intf='h3-eth0')
    h3.cmd("ip route add default dev h3-eth0")
    # h3.setIP('10.0.3.2/32', intf='h3-eth1')
    # h3.setMAC('00:00:00:00:03:02', intf='h3-eth1')

    h4.setIP('10.0.4.1/32', intf='h4-eth0')
    h4.setMAC('00:00:00:00:04:01', intf='h4-eth0')
    h4.cmd("ip route add default dev h4-eth0")
    # h4.setIP('10.0.4.2/32', intf='h4-eth1')
    # h4.setMAC('00:00:00:00:04:02', intf='h4-eth1')

    h5.setIP('10.0.5.1/32', intf='h5-eth0')
    h5.setMAC('00:00:00:00:05:01', intf='h5-eth0')
    h5.cmd("ip route add default dev h5-eth0")


    net.staticArp()

    # disabling offload for rx and tx on each host interface
    for host in h1, h2, h3, h4, h5:
        host.cmd("ethtool --offload {}-eth0 rx off tx off".format(host.name))
        host.cmd("./conf-{}-map.sh".format(host.name))
        host.cmd("sh < calc_key/{}-table.txt".format(host.name))

    info("*** Running CLI\n")
    CLI(net)

    os.system("pkill -9 -f 'xterm'")

    info("*** Stopping network\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    remote_controller = False
    topology(remote_controller)
