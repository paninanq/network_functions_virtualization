FROM public.ecr.aws/ubuntu/ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i \
      -e 's|http://archive.ubuntu.com/ubuntu/|http://mirror.yandex.ru/ubuntu/|g' \
      -e 's|http://security.ubuntu.com/ubuntu/|http://mirror.yandex.ru/ubuntu/|g' \
      /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      bash ca-certificates curl ethtool iproute2 iputils-ping jq python3 \
    && rm -rf /var/lib/apt/lists/*

CMD ["sleep", "infinity"]
