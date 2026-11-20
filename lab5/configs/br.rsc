# 2026-11-20 12:36:38 by RouterOS 7.23.8
# system id = GSHWXsxMKwN
#
/interface ethernet set [ find default-name=ether1 ] disable-running-check=no
/interface ethernet set [ find default-name=ether2 ] disable-running-check=no
/interface ethernet set [ find default-name=ether3 ] disable-running-check=no
/interface wireguard add listen-port=13003 mtu=1420 name=wg-hq
/interface wireguard peers add allowed-address=10.3.254.1/32,10.3.100.0/24 endpoint-address=100.64.1.2 endpoint-port=13003 interface=wg-hq name=peer1 persistent-keepalive=25s public-key="bWKV48qQinsOLvwJoQlas/0zIZXMv4zuoD47iRW1gwU="
/ip address add address=172.31.255.30/30 interface=ether1 network=172.31.255.28
/ip address add address=100.64.2.2/30 comment=wan interface=ether2 network=100.64.2.0
/ip address add address=10.3.200.1/24 comment=branch-lan interface=ether3 network=10.3.200.0
/ip address add address=10.3.254.2/30 comment=wg-branch interface=wg-hq network=10.3.254.0
/ip dhcp-client add interface=ether1 name=client1
/ip firewall nat add action=masquerade chain=srcnat comment=branch-to-internet out-interface=ether2
/ip route add comment=clab-mgmt dst-address=10.105.3.0/24 gateway=172.31.255.29
/ip route add comment=isp dst-address=0.0.0.0/0 gateway=100.64.2.1
/ip route add comment=dc-through-wg dst-address=10.3.100.0/24 gateway=wg-hq
/system identity set name=br-panina
