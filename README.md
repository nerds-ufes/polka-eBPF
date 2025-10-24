# polka-eBPF

## Building environment for eBPF:
### 1. Required compilation libraries:
```
sudo apt update
sudo apt install -y clang llvm libbpf-dev libbpfcc-dev gcc make pkg-config \
                   linux-headers-$(uname -r) bpftool
```
### 2. How to compile:
```
sudo clang -O2 -g -target bpf -c <arquivo.c> -o <arquivo.o>
```
**Exemple:**
```
sudo clang -O2 -g -target bpf -c custom_header.c -o custom_header.o
sudo clang -O2 -target bpf -c xdp_ip_filter_source.c -o xdp_ip_filter_source.o
```

### 3. Load the program into traffic (tc):
```
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
3.1. Useful commands - Checking if something is loaded in the interface:
```
ip link show dev <nome-interface>
```
Exemple:
```
ip link show dev enp0s3
```
or
List all loaded eBPF programs
```
sudo bpftool prog list
```

Filter by name or tag
```
sudo bpftool prog list | grep -i rtt
sudo bpftool prog list | grep -i classifier
```

Show program details
```
sudo bpftool prog show name tc_rtt_monitor
```
