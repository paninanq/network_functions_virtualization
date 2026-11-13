FROM public.ecr.aws/ubuntu/ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i \
      -e 's|http://archive.ubuntu.com/ubuntu/|http://mirror.yandex.ru/ubuntu/|g' \
      -e 's|http://security.ubuntu.com/ubuntu/|http://mirror.yandex.ru/ubuntu/|g' \
      /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates ethtool iproute2 iputils-ping openvswitch-switch \
    && rm -rf /var/lib/apt/lists/*

COPY ovs-entrypoint.sh /usr/local/sbin/ovs-entrypoint.sh
RUN chmod 0755 /usr/local/sbin/ovs-entrypoint.sh

EXPOSE 6653
ENTRYPOINT ["/usr/local/sbin/ovs-entrypoint.sh"]
