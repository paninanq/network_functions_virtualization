# Course SONiC wrapper: upstream docker-sonic-vs plus CLI compatibility shims.
ARG BASE=docker-sonic-vs:202511
FROM ${BASE}
COPY sudo-shim /usr/local/bin/sudo
COPY docker-shim /usr/local/bin/docker
RUN chmod +x /usr/local/bin/sudo /usr/local/bin/docker \
 && ln -sf /usr/bin/vtysh /usr/local/bin/rvtysh
