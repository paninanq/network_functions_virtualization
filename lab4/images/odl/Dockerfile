FROM public.ecr.aws/ubuntu/ubuntu:24.04

ARG ODL_VERSION=0.24.0
ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i \
      -e 's|http://archive.ubuntu.com/ubuntu/|http://mirror.yandex.ru/ubuntu/|g' \
      -e 's|http://security.ubuntu.com/ubuntu/|http://mirror.yandex.ru/ubuntu/|g' \
      /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates curl openjdk-21-jre-headless tar \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 4 \
      "https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/karaf/${ODL_VERSION}/karaf-${ODL_VERSION}.tar.gz" \
      -o /tmp/odl.tar.gz \
    && mkdir -p /opt/odl \
    && tar -xzf /tmp/odl.tar.gz -C /opt/odl --strip-components=1 \
    && rm /tmp/odl.tar.gz

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH=/opt/odl/bin:$PATH

EXPOSE 6653 8181
ENTRYPOINT ["/opt/odl/bin/karaf"]
CMD ["server"]
