# polka-eBPF

## Building environment for eBPF:
1. Required compilation libraries:
```
sudo apt update
sudo apt install -y clang llvm libbpf-dev libbpfcc-dev gcc make pkg-config \
                   linux-headers-$(uname -r) bpftool
```
2. How to compile:
```
sudo clang -O2 -g -target bpf -c <arquivo.c> -o <arquivo.o>
```
**Exemple:**
```
sudo clang -O2 -g -target bpf -c custom_header.c -o custom_header.o
sudo clang -O2 -target bpf -c xdp_ip_filter_source.c -o xdp_ip_filter_source.o
```

3. Load the program into traffic (tc):
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
