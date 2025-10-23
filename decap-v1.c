#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

/* ======= Definições endian (substitui <linux/bpf_endian.h>) ======= */
#ifndef __BPF_ENDIAN__
#define __BPF_ENDIAN__
#define bpf_htons(x) ((__u16)__builtin_bswap16(x))
#define bpf_ntohs(x) ((__u16)__builtin_bswap16(x))
#define bpf_htonl(x) ((__u32)__builtin_bswap32(x))
#define bpf_ntohl(x) ((__u32)__builtin_bswap32(x))
#endif
/* ================================================================== */

SEC("xdp")
int xdp_decap(struct xdp_md *ctx)
{
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;
    struct ethhdr *eth = data;

    if (data + sizeof(*eth) > data_end)
        return XDP_PASS;

    __u16 h_proto = bpf_ntohs(eth->h_proto);

    // só processa se for o ethertype 0x1234 (cabeçalho de tunelamento)
    if (h_proto != 0x1234)
        return XDP_PASS;

    __u32 tun_hdr_len = 20; // tamanho fixo do cabeçalho customizado

    if (data + sizeof(*eth) + tun_hdr_len > data_end)
        return XDP_DROP;

    // descarta 20 bytes após o cabeçalho Ethernet
    if (bpf_xdp_adjust_head(ctx, tun_hdr_len))
        return XDP_ABORTED;

    // reobter ponteiros após ajuste
    data = (void *)(long)ctx->data;
    data_end = (void *)(long)ctx->data_end;
    eth = data;

    if (data + sizeof(*eth) > data_end)
        return XDP_ABORTED;

    // Corrigir Ethertype para IPv4
    eth->h_proto = bpf_htons(ETH_P_IP);

    // Opcional: debug (use `sudo cat /sys/kernel/debug/tracing/trace_pipe`)
    bpf_printk("Decapsulated 20 bytes, Ethertype set to IPv4\n");

    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
