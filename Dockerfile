FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ASTERISK_VERSION=20.10.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    libssl-dev \
    libncurses5-dev \
    libnewt-dev \
    libxml2-dev \
    libsqlite3-dev \
    uuid-dev \
    libjansson-dev \
    libedit-dev \
    libsrtp2-dev \
    libgsm1-dev \
    libspeex-dev \
    libspeexdsp-dev \
    libcurl4-openssl-dev \
    sox \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Download and compile PJSIP
WORKDIR /usr/src
RUN wget https://github.com/pjsip/pjproject/archive/refs/tags/2.13.tar.gz -O pjproject-2.13.tar.gz && \
    tar -xzf pjproject-2.13.tar.gz && \
    cd pjproject-2.13 && \
    ./configure --prefix=/usr --libdir=/usr/lib64 --enable-shared --disable-video --disable-sound --disable-opencore-amr && \
    make dep && make && make install && \
    ldconfig

# Download and compile Asterisk
RUN wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-${ASTERISK_VERSION}.tar.gz && \
    tar -xzf asterisk-${ASTERISK_VERSION}.tar.gz && \
    cd asterisk-${ASTERISK_VERSION} && \
    contrib/scripts/install_prereq install && \
    ./configure --with-jansson-bundled --with-pjproject-bundled && \
    make menuselect.makeopts && \
    menuselect/menuselect --enable-category MENUSELECT_ADDONS menuselect.makeopts && \
    menuselect/menuselect --enable-category MENUSELECT_APPS menuselect.makeopts && \
    menuselect/menuselect --enable-category MENUSELECT_CDR menuselect.makeopts && \
    menuselect/menuselect --enable-category MENUSELECT_CHANNELS menuselect.makeopts && \
    menuselect/menuselect --enable-category MENUSELECT_CODECS menuselect.makeopts && \
    menuselect/menuselect --enable-category MENUSELECT_FORMATS menuselect.makeopts && \
    menuselect/menuselect --enable-category MENUSELECT_FUNCS menuselect.makeopts && \
    menuselect/menuselect --enable-category MENUSELECT_PBX menuselect.makeopts && \
    menuselect/menuselect --enable-category MENUSELECT_RES menuselect.makeopts && \
    make -j$(nproc) && \
    make install && \
    make samples && \
    make install-sounds-en-gsm && \
    make install-sounds-en-wav

# Create Asterisk user
RUN useradd -r -d /var/lib/asterisk -s /usr/sbin/nologin asterisk && \
    chown -R asterisk:asterisk /etc/asterisk /var/lib/asterisk /var/log/asterisk /var/spool/asterisk /usr/lib/asterisk

# Setup Python environment
WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

# Copy application files
COPY ai_agent.py .
COPY asterisk_config /etc/asterisk/

# Expose ports
EXPOSE 5060/udp 5060/tcp 8088 8089 10000-20000/udp

# Create startup script
RUN echo '#!/bin/bash\n\
asterisk -c &\n\
sleep 5\n\
python3 /app/ai_agent.py\n\
' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]
