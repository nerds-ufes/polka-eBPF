#!/bin/bash

# Script para executar comandos no host h4 do Mininet

echo "*** Iniciando configuração do host h4..."

# Iniciar Mininet CLI e executar comandos
# mn << EOF
mkdir -p /sys/fs/bpf
mount -t bpf bpf /sys/fs/bpf
tc qdisc add dev h4-eth0 clsact
tc filter add dev h4-eth0 egress bpf obj encap_map_h41.o sec tc
tc qdisc add dev h4-eth1 clsact
tc filter add dev h4-eth1 egress bpf obj encap_map_h42.o sec tc

ip link set dev h4-eth0 xdp off
ip link set dev h4-eth0 xdp obj decap.o sec xdp
ip link set dev h4-eth1 xdp off
ip link set dev h4-eth1 xdp obj decap.o sec xdp

echo "Configuração concluída!"


# Opção de compilação
# clang -O2 -g -target bpf -D__TARGET_ARCH_x86 -c encap_map.c -o encap_map.o

# Cada host preciso de um obj encap_map.o, do contrário haverá conflito das
# tabela de maps eBPF.