# 2026-11-20 12:36:36 by RouterOS 7.23.8
# system id = dfqTYRi79qJ
#
/interface ethernet set [ find default-name=ether1 ] disable-running-check=no
/interface ethernet set [ find default-name=ether2 ] disable-running-check=no
/interface ethernet set [ find default-name=ether3 ] disable-running-check=no
/interface wireguard add listen-port=13003 mtu=1420 name=wg-br
/routing bgp instance add as=65103 name=hq
/interface wireguard peers add allowed-address=10.3.254.2/32,10.3.200.0/24 endpoint-address=100.64.2.2 endpoint-port=13003 interface=wg-br name=peer1 persistent-keepalive=25s public-key="5ysf0uqtpVliEnFVn2mRWk3DhadNOVer9tTU4cIBiBM="
/ip address add address=172.31.255.30/30 interface=ether1 network=172.31.255.28
/ip address add address=10.3.1.2/30 comment=to-dc interface=ether2 network=10.3.1.0
/ip address add address=100.64.1.2/30 comment=wan interface=ether3 network=100.64.1.0
/ip address add address=10.3.254.1/30 comment=wg-hq interface=wg-br network=10.3.254.0
/ip dhcp-client add interface=ether1 name=client1
/ip firewall address-list add address=10.3.200.0/24 comment=branch-prefix list=to-dc
/ip firewall filter add action=accept chain=input comment=input-established connection-state=established,related
/ip firewall filter add action=drop chain=input comment=input-invalid connection-state=invalid
/ip firewall filter add action=accept chain=input comment=input-icmp protocol=icmp
/ip firewall filter add action=accept chain=input comment=input-mgmt in-interface=ether1
/ip firewall filter add action=accept chain=input comment=input-bgp dst-port=179 in-interface=ether2 protocol=tcp
/ip firewall filter add action=accept chain=input comment=input-wireguard dst-port=13003 protocol=udp
/ip firewall filter add action=drop chain=input comment=input-wan-deny in-interface=ether3
/ip firewall filter add action=drop chain=input comment=input-default-deny
/ip firewall filter add action=accept chain=forward comment=forward-established connection-state=established,related
/ip firewall filter add action=drop chain=forward comment=forward-invalid connection-state=invalid
/ip firewall filter add action=accept chain=forward comment=dc-to-internet in-interface=ether2 out-interface=ether3
/ip firewall filter add action=accept chain=forward comment=branch-to-dc in-interface=wg-br out-interface=ether2
/ip firewall filter add action=accept chain=forward comment=dc-to-branch in-interface=ether2 out-interface=wg-br
/ip firewall filter add action=drop chain=forward comment=forward-default-deny
/ip firewall nat add action=masquerade chain=srcnat comment=inside-to-internet out-interface=ether3
/ip route add comment=clab-mgmt dst-address=10.105.3.0/24 gateway=172.31.255.29
/ip route add comment=isp dst-address=0.0.0.0/0 gateway=100.64.1.1
/ip route add comment=branch-through-wg dst-address=10.3.200.0/24 gateway=wg-br
/routing bgp connection add instance=hq local.role=ebgp name=to-dc output.default-originate=if-installed .network=to-dc remote.address=10.3.1.1 .as=65003
/system identity set name=hq-panina
