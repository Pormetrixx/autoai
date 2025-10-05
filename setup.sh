#!/bin/bash
#
# Setup Script for AI Call Center Agent
# Run after installing Asterisk
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AI Call Center Agent Setup${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if Asterisk is installed
if ! command -v asterisk &> /dev/null; then
    echo -e "${YELLOW}Asterisk not found. Please run install_asterisk_ubuntu22.sh first${NC}"
    exit 1
fi

# Copy configuration files
echo -e "${YELLOW}[1/5] Copying Asterisk configuration files...${NC}"
sudo cp -f asterisk_config/*.conf /etc/asterisk/
sudo chown asterisk:asterisk /etc/asterisk/*.conf
sudo chmod 640 /etc/asterisk/*.conf

# Create Python virtual environment
echo -e "${YELLOW}[2/5] Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}[3/5] Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
echo -e "${YELLOW}[4/5] Setting up environment configuration...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file and add your API keys${NC}"
fi

# Restart Asterisk to apply configuration
echo -e "${YELLOW}[5/5] Restarting Asterisk...${NC}"
sudo systemctl restart asterisk
sleep 3

# Check Asterisk status
if systemctl is-active --quiet asterisk; then
    echo -e "${GREEN}✓ Asterisk is running${NC}"
else
    echo -e "${YELLOW}⚠ Asterisk failed to start. Check logs: sudo journalctl -u asterisk -n 50${NC}"
fi

echo -e ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Edit .env file with your API keys:"
echo -e "   nano .env"
echo -e ""
echo -e "2. Activate virtual environment:"
echo -e "   source venv/bin/activate"
echo -e ""
echo -e "3. Run the AI agent:"
echo -e "   python3 ai_agent.py"
echo -e ""
echo -e "4. Test by calling extension 9000 from a SIP client"
echo -e ""
echo -e "${YELLOW}Test Extensions:${NC}"
echo -e "  1000 - Test User 1"
echo -e "  1001 - Test User 2"
echo -e "  9000 - AI Investment Advisor"
echo -e "  9001 - Echo Test"
echo -e "  9002 - Music on Hold"
echo -e ""
