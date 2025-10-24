// encap_map.c - encapsula pacotes IP com chave lida de map
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>
#include <linux/pkt_cls.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

struct value160 {
    unsigned char bytes[20]; // 20 bytes = 160 bits
};

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 16);
    __type(key, __u32);       // IP destino
    __type(value, struct value160); // valor de 20 bytes
} ip_key_map_h31 SEC(".maps");

SEC("tc")
int encap_func(struct __sk_buff *skb) {
    void *data = (void *)(long)skb->data;
    void *data_end = (void *)(long)skb->data_end;

    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return TC_ACT_SHOT;

    if (eth->h_proto != bpf_htons(ETH_P_IP))
        return TC_ACT_OK;

    struct iphdr *iph = (struct iphdr *)(eth + 1);
    if ((void *)(iph + 1) > data_end)
        return TC_ACT_SHOT;

    __u32 dst_ip = iph->daddr;  // já em ordem de rede

    __u64 *key_val = bpf_map_lookup_elem(&ip_key_map_h31, &dst_ip);
    if (!key_val)
        return TC_ACT_OK;  // não há chave registrada para este IP

    // ajusta espaço para inserir os 20 bytes do header extra
    if (bpf_skb_adjust_room(skb, 20, BPF_ADJ_ROOM_MAC, 0))
        return TC_ACT_SHOT;

    // recarrega ponteiros
    data = (void *)(long)skb->data;
    data_end = (void *)(long)skb->data_end;
    eth = data;
    iph = (struct iphdr *)(eth + 1);
    if ((void *)(iph + 1) > data_end)
        return TC_ACT_SHOT;

    eth->h_proto = bpf_htons(0x1234);

    __u8 tunnel_id[20] = {0};
    __u64 val = *key_val;

    // converte o valor numérico (64 bits) para bytes big-endian nos últimos 8 bytes
    #pragma unroll
    for (int i = 0; i < 8; i++) {
        tunnel_id[12 + i] = (val >> (8 * (7 - i))) & 0xFF;
    }

    // grava os 20 bytes após o cabeçalho Ethernet
    if (bpf_skb_store_bytes(skb, sizeof(*eth), tunnel_id, sizeof(tunnel_id), 0))
        return TC_ACT_SHOT;

    return TC_ACT_OK;
}

char _license[] SEC("license") = "GPL";
