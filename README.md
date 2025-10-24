# polka-eBPF

## Building environment for eBPF:
1. Required compilation libraries:
   """
   sudo apt update
   sudo apt install -y clang llvm libbpf-dev libbpfcc-dev gcc make pkg-config \
                   linux-headers-$(uname -r) bpftool

   """
