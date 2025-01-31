FROM debian:bullseye-20230502-slim@sha256:249d9dc1b57918b203e45f647ea675cd940de5942863f35c979e5d926f024a7e

MAINTAINER victor@sunet.se

# Metadata
LABEL version="1.03"
LABEL description="pkcs11_ca test1"

# Set work dir
WORKDIR /app

# Copy the requirement.txt file needed to install deps
COPY ./requirements.txt /app/requirements.txt


# Install deps
RUN apt-get update \
    && apt-get install -y \
    python3-pip \
    netcat \
    dnsutils \
    git \
    openssl \
    vim-tiny \
    nano \
    emacs-nox \
    bsdmainutils \
    curl \
    && pip3 install --require-hashes -r /app/requirements.txt \
    && apt-get autoremove -y
    

# Remove setuid and setgid
RUN find / -xdev -perm /6000 -type f -exec chmod a-s {} \; || true

# Add user and add to softhsm group
RUN useradd pkcs11_ca_test1 -u 1501 -s /usr/sbin/nologin


COPY ./src /app/src
COPY ./tests /app/tests
COPY ./data/trusted_keys /app/data/trusted_keys
COPY ./containers/healthcheck.sh /app/healthcheck.sh
COPY ./containers/healthcheck.py /app/healthcheck.py
COPY ./data/tls_certificate.pem /app/tls_certificate.pem

RUN mkdir -p /var/www/dehydrated
RUN chown 1501 /var/www/dehydrated

RUN chown -R pkcs11_ca_test1 /app

# Run as user
USER pkcs11_ca_test1

# Add healthcheck
# HEALTHCHECK --interval=30s --timeout=15s --retries=1 --start-period=30s \
#     CMD sh healthcheck.sh || bash -c 'kill -s 15 1 && (sleep 7; kill -s 9 1)'

# ENTRYPOINT ["sleep", "300"]
ENTRYPOINT ["python3", "-m", "unittest"]
