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
    __u32 tun_hdr_len = 20; // tamanho do cabeçalho customizado

    if (data + sizeof(*eth) > data_end)
        return XDP_PASS;

    __u16 h_proto = bpf_ntohs(eth->h_proto);
    if (h_proto != 0x1234)
        return XDP_PASS;

    if (data + sizeof(*eth) + tun_hdr_len > data_end)
        return XDP_DROP;

    /* === Salvar o cabeçalho Ethernet original === */
    struct ethhdr eth_backup;
    __builtin_memcpy(&eth_backup, eth, sizeof(struct ethhdr));

    /* === Avançar o início do pacote para remover cabeçalho Ethernet + tunelamento === */
    if (bpf_xdp_adjust_head(ctx, sizeof(struct ethhdr) + tun_hdr_len))
        return XDP_ABORTED;

    /* === Cria espaço para o cabeçalho Ethernet original === */
    if (bpf_xdp_adjust_head(ctx, -14))
        return XDP_ABORTED;

    /* === Recarregar ponteiros === */
    data = (void *)(long)ctx->data;
    data_end = (void *)(long)ctx->data_end;

    /* === Restaurar o cabeçalho Ethernet === */
    if (data + sizeof(struct ethhdr) > data_end)
        return XDP_ABORTED;

    eth = data;
    __builtin_memcpy(eth, &eth_backup, sizeof(struct ethhdr));

    /* === Corrigir Ethertype para IPv4 === */
    eth->h_proto = bpf_htons(ETH_P_IP);

    bpf_printk("Removed 20-byte tunnel header after Ethernet\n");

    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
