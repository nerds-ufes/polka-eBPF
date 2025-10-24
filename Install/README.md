# polka-eBPF

## Building environment for eBPF:
### 1. Required compilation libraries:
```
sudo apt update
sudo apt install -y clang llvm libbpf-dev libbpfcc-dev gcc make pkg-config \
                   linux-headers-$(uname -r) bpftool
```

```
sudo apt-get install -y gcc-multilib
sudo apt install pkg-config
sudo apt install m4
sudo apt install libelf-dev
sudo apt install libpcap-dev
sudo apt install gcc-multilib
```

### 2. How to compile:
```
sudo clang -O2 -g -target bpf -c <arquivo.c> -o <arquivo.o>
```
**Example:**
```
sudo clang -O2 -g -target bpf -c custom_header.c -o custom_header.o
sudo clang -O2 -target bpf -c xdp_ip_filter_source.c -o xdp_ip_filter_source.o
```

### 3. Load the program into traffic (tc):

**First, clean up any previous programs.**
```
sudo tc qdisc del dev eth0 clsact 2>/dev/null
```
**Adds qdisc clsact hook**
```
sudo tc qdisc add dev eth0 clsact
```
**Attach the eBPF program to the egress**
```
sudo tc filter add dev eth0 egress bpf obj custom_header.o sec classifier
```
#### 3.1. Useful commands - Checking if something is loaded in the interface:
```
ip link show dev <nome-interface>
```
**Example:**
```
ip link show dev enp0s3
```
**or List all loaded eBPF programs**
```
sudo bpftool prog list
```
**Filter by name or tag**
```
sudo bpftool prog list | grep -i rtt
sudo bpftool prog list | grep -i classifier
```
**Show program details**
```
sudo bpftool prog show name tc_rtt_monitor
```

### 4. Loading program into interface::
```
sudo ip link set dev <interface> xdp obj <arquivo.o> sec xdp
```
**Example:**
```
sudo ip link set dev enp0s3 xdp obj xdp_ip_filter.o sec xdp
```

### 5. Deleting program from interface:
```
sudo ip link set dev <interface> xdp off
```
**Example:**
```
sudo ip link set dev enp0s3 xdp off
```


## Loading eBPF program into mininet:

When adding eBPF programs to the Mininet host interface, for example, **h1-eth0**, you must create a mount point for eBPF (**bpffs mountpoint**). Otherwise, you will receive the error message _ _"mkdir /sys/fs/bpf/tc/ failed: No such file or directory. Continuing without mounted eBPF fs. Too old kernel? mkdir (null)/globals failed: No such file or directory." _ _

The message indicates that the BPF filesystem (bpffs) is not mounted within the h1 host namespace. This means that the **'ip link set dev ... xdp obj ...'** command needs to access the BPF filesystem (**/sys/fs/bpf**) to map programs, maps, etc., but within the network namespace (such as Mininet hosts), this directory may not be automatically mounted.

### 1. How to solve: Mount bpffs globally (on the real host):
On the main host (outside Mininet), run:
```
sudo mount bpffs /sys/fs/bpf -t bpf
```
On Mininet host:
```
h1 mkdir -p /sys/fs/bpf
h1 mount -t bpf bpf /sys/fs/bpf
```
On the main host (outside Mininet), run:
```
sudo mount bpffs /sys/fs/bpf -t bpf
```
**Example**
```
(on mininet)> h1 ip link show
(on mininet)> h1 ip link set dev h1-eth0 xdp obj xdp_ip_filter.o sec xdp
(Deleting the program from the interface)
(on mininet)> h1 ip link set dev h1-eth0 xdp off
```
```
*** Starting CLI:
mininet> h1 mkdir -p /sys/fs/bpf
mininet> h1 mount -t bpf bpf /sys/fs/bpf
mininet> h1 tc qdisc add dev h1-eth0 clsact
mininet> h1 tc filter add dev h1-eth0 egress bpf obj encap.o sec tc
mininet> h1 tc filter add dev h1-eth0 ingress bpf obj decap.o sec tc
mininet> h1 ping h2
```

## OBS:
1. In the script topo_2h-eBPF.py BMv2 + P4 is used, so it is necessary to add the bmv2.py library to the "/mininet/mininet/" directory 
```
sudo cp bmv2.py /mininet/mininet/
```
and reinstall mininet: 
```
./mininet/util/install.sh -nv
```
2. Another alternative is to use mininet-wifi: (https://mininet-wifi.github.io/) ; (https://github.com/intrig-unicamp/mininet-wifi)
