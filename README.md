# polka-eBPF
![Setup de testes](figures/Polka-eBPF.jpg)
## Building environment for eBPF:
### 1. To run, simply:
```
cd polka-eBPF/
sudo python3 topo_2h-eBPF.py
```
```
mininet> h1 ping h2
mininet> h2 ping h1
```
### 2. POLKA implementation on the host using eBPF:
Source codes **encap_map-h _x_ .c** and **decap.c** codes, respectively using tc anchored in the egress, and xdp.

To compile encap using maps (**encap_map-h _x_ .c**), a targeted compilation is required, which becomes:
```
sudo clang -O2 -g -target bpf -D__TARGET_ARCH_x86 -c encap_map.c -o encap_map.o
```
And, to compile encap using maps (**decap.c**), a targeted compilation is required, which becomes:
```
sudo clang -O2 -target bpf -c decap.c -o decap.o
```

#### 3. Ex.: Loading values ​​into eBPF/TC maps encap_maps-h1.o:
0A 00 02 02 -> IP Address in hex
48 82 03 80 00 00 00 00 00 00 -> Polka key in hex
```
h1 bpftool map update name ip_key_map key hex 0A 00 02 02 value hex 48 82 03 80 00 00 00 00 00 00
```

#### 4. Listing the contents of the maps:
```
h1 bpftool map dump name ip_key_map
```
#### 5. Deleting map content:
```
h1 bpftool map delete name ip_key_map_h1 key hex 0A 00 02 02
```

_ _**Note: In a Mininet emulation, it is necessary to create, for each host, a separate eBPF object file (e.g., `encap_map_h1.o` for `h1-eth0`, `encap_map_h2.o` for `h2-eth0`). For each object, a distinct map must also be created — for example, `ip_key_map_h1` for `h1-eth0` (`encap_map_h1.o`) and `ip_key_map_h2` for `h2-eth0` (`encap_map_h2.o`). This is required because the namespaces of `h1` and `h2` share the same maps; therefore, by using different names, each host/interface maintains its own independent map table.**_ _
