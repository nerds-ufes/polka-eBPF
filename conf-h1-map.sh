#!/bin/bash

# Script para executar comandos no host h1 do Mininet

echo "*** Iniciando configuração do host h1..."

# Iniciar Mininet CLI e executar comandos
# mn << EOF
mkdir -p /sys/fs/bpf
mount -t bpf bpf /sys/fs/bpf
tc qdisc add dev h1-eth0 clsact
tc filter add dev h1-eth0 egress bpf obj encap_map_h1.o sec tc
#sudo python3 pop_map.py
#tc filter add dev h1-eth0 ingress bpf obj decap.o sec tc
ip link set dev h1-eth0 xdp off
ip link set dev h1-eth0 xdp obj decap_h1.o sec xdp

echo "Configuração concluída!"


# Opção de compilação
# clang -O2 -g -target bpf -D__TARGET_ARCH_x86 -c encap_map.c -o encap_map.o
