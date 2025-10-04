#!/bin/bash
#
# Asterisk Installation Script for Ubuntu 22.04
# Installs Asterisk with all modules and dependencies for AI Call Center Agent
#
# Usage: sudo bash install_asterisk_ubuntu22.sh
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Asterisk AI Call Center Installation${NC}"
echo -e "${GREEN}Ubuntu 22.04 LTS${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install build dependencies
echo -e "${YELLOW}[2/8] Installing build dependencies...${NC}"
apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    libssl-dev \
    libncurses5-dev \
    libnewt-dev \
    libxml2-dev \
    linux-headers-$(uname -r) \
    libsqlite3-dev \
    uuid-dev \
    libjansson-dev \
    libedit-dev \
    libsrtp2-dev \
    libgsm1-dev \
    libspeex-dev \
    libspeexdsp-dev \
    libcurl4-openssl-dev \
    libldap2-dev \
    libogg-dev \
    libvorbis-dev \
    libical-dev \
    libiksemel-dev \
    libneon27-dev \
    libgmime-3.0-dev \
    libunbound-dev \
    libpopt-dev \
    libsnmp-dev \
    libcorosync-common-dev \
    libbluetooth-dev \
    libradiusclient-ng-dev \
    freetds-dev \
    libpq-dev \
    libresample1-dev \
    libc-client2007e-dev \
    binutils-dev \
    libsrtp2-dev \
    libspandsp-dev \
    sox \
    libsox-fmt-all \
    ffmpeg \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv

# Install Node.js (for potential future extensions)
echo -e "${YELLOW}[3/8] Installing Node.js...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Download and install PJSIP
echo -e "${YELLOW}[4/8] Installing PJSIP...${NC}"
cd /usr/src
if [ ! -d "pjproject-2.13" ]; then
    wget https://github.com/pjsip/pjproject/archive/refs/tags/2.13.tar.gz -O pjproject-2.13.tar.gz
    tar -xzf pjproject-2.13.tar.gz
fi
cd pjproject-2.13
./configure --prefix=/usr --libdir=/usr/lib64 --enable-shared --disable-video --disable-sound --disable-opencore-amr
make dep
make
make install
ldconfig

# Download and install Asterisk
echo -e "${YELLOW}[5/8] Downloading and installing Asterisk 20...${NC}"
cd /usr/src
ASTERISK_VERSION="20.10.0"
if [ ! -d "asterisk-${ASTERISK_VERSION}" ]; then
    wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-${ASTERISK_VERSION}.tar.gz
    tar -xzf asterisk-${ASTERISK_VERSION}.tar.gz
fi
cd asterisk-${ASTERISK_VERSION}

# Install prerequisites
contrib/scripts/install_prereq install

# Configure Asterisk with all modules
echo -e "${YELLOW}[6/8] Configuring Asterisk with all modules...${NC}"
./configure --with-jansson-bundled --with-pjproject-bundled

# Select all modules using menuselect
make menuselect.makeopts
# Enable all modules by default
menuselect/menuselect \
    --enable-category MENUSELECT_ADDONS \
    --enable-category MENUSELECT_APPS \
    --enable-category MENUSELECT_BRIDGES \
    --enable-category MENUSELECT_CDR \
    --enable-category MENUSELECT_CEL \
    --enable-category MENUSELECT_CHANNELS \
    --enable-category MENUSELECT_CODECS \
    --enable-category MENUSELECT_FORMATS \
    --enable-category MENUSELECT_FUNCS \
    --enable-category MENUSELECT_PBX \
    --enable-category MENUSELECT_RES \
    --enable-category MENUSELECT_TESTS \
    --enable-category MENUSELECT_UTILS \
    menuselect.makeopts

# Compile and install
echo -e "${YELLOW}[7/8] Compiling Asterisk (this may take 15-30 minutes)...${NC}"
make -j$(nproc)
make install
make samples
make config

# Install Asterisk sound files
echo -e "${YELLOW}Installing sound files...${NC}"
make install-sounds-en-gsm
make install-sounds-en-wav

# Create Asterisk user
if ! id -u asterisk > /dev/null 2>&1; then
    useradd -r -d /var/lib/asterisk -s /usr/sbin/nologin asterisk
fi

# Set permissions
chown -R asterisk:asterisk /etc/asterisk
chown -R asterisk:asterisk /var/lib/asterisk
chown -R asterisk:asterisk /var/log/asterisk
chown -R asterisk:asterisk /var/spool/asterisk
chown -R asterisk:asterisk /usr/lib/asterisk
chmod -R 750 /etc/asterisk

# Configure Asterisk to run as asterisk user
sed -i 's/#AST_USER="asterisk"/AST_USER="asterisk"/' /etc/default/asterisk
sed -i 's/#AST_GROUP="asterisk"/AST_GROUP="asterisk"/' /etc/default/asterisk

# Enable and start Asterisk service
echo -e "${YELLOW}[8/8] Enabling Asterisk service...${NC}"
systemctl enable asterisk
systemctl stop asterisk 2>/dev/null || true

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Asterisk installation completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Copy configuration files to /etc/asterisk/"
echo -e "2. Install Python dependencies: pip3 install -r requirements.txt"
echo -e "3. Configure .env file with API keys"
echo -e "4. Start Asterisk: systemctl start asterisk"
echo -e "5. Run the AI agent: python3 ai_agent.py"
echo -e ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  Check status: systemctl status asterisk"
echo -e "  View logs: tail -f /var/log/asterisk/full"
echo -e "  Connect to CLI: asterisk -rvvv"
echo -e ""
