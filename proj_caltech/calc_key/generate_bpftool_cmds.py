#!/usr/bin/env python3
import sys
import ipaddress

TOTAL_BYTES = 20  # total de bytes na saída

def ip_to_hex(ip_str):
    """Converte endereço IP (ex: '10.0.2.2') em bytes hexadecimais no formato 0A 00 02 02"""
    ip = ipaddress.IPv4Address(ip_str)
    return " ".join(f"{b:02X}" for b in ip.packed)

def decimal_to_hex(n):
    """Converte número decimal para 20 bytes (big int), invertido (little endian total)"""
    # converte número para bytes, sem sinal, big endian (depois invertemos)
    hex_bytes = n.to_bytes(TOTAL_BYTES, byteorder="big", signed=False)
    # inverter a ordem dos bytes
    reversed_bytes = hex_bytes[::-1]
    return " ".join(f"{b:02X}" for b in reversed_bytes)

def process_file(filename):
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or "=>" not in line:
                continue

            # exemplo de linha: '10.0.2.2' => 2147713608
            ip_part, num_part = line.split("=>")
            ip_str = ip_part.strip().strip("'").strip('"')
            num_str = num_part.strip()

            try:
                n = int(num_str)
            except ValueError:
                print(f"Erro: valor inválido '{num_str}' em '{line}'")
                continue

            ip_hex = ip_to_hex(ip_str)
            val_hex = decimal_to_hex(n)

            print(f"bpftool map update name ip_key_map key hex {ip_hex} value hex {val_hex}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <arquivo.txt>")
        sys.exit(1)

    process_file(sys.argv[1])
