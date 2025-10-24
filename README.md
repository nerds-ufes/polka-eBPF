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
**encap_map-h _x_ .c** and **decap.c** codes, respectively using tc anchored in the egress, and xdp.

To compile encap using maps (encap_maps.c), a targeted compilation is required, which becomes:
