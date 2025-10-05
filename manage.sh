#!/bin/bash
#
# Management script for AI Call Center Agent
#

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_status() {
    echo -e "${GREEN}=== System Status ===${NC}"
    echo ""
    
    echo -e "${YELLOW}Asterisk Service:${NC}"
    systemctl status asterisk --no-pager | head -5
    echo ""
    
    echo -e "${YELLOW}Active Channels:${NC}"
    sudo asterisk -rx "core show channels" | tail -3
    echo ""
    
    echo -e "${YELLOW}SIP Endpoints:${NC}"
    sudo asterisk -rx "pjsip show endpoints" | grep "Endpoint:" | head -5
    echo ""
    
    echo -e "${YELLOW}ARI Applications:${NC}"
    sudo asterisk -rx "ari show apps"
    echo ""
}

show_logs() {
    echo -e "${GREEN}=== Recent Logs ===${NC}"
    echo ""
    
    echo -e "${YELLOW}AI Agent Logs (last 20 lines):${NC}"
    if [ -f "ai_agent.log" ]; then
        tail -20 ai_agent.log
    else
        echo "No logs found"
    fi
    echo ""
    
    echo -e "${YELLOW}Asterisk Logs (last 10 lines):${NC}"
    sudo tail -10 /var/log/asterisk/full
}

show_leads() {
    echo -e "${GREEN}=== Lead Data ===${NC}"
    echo ""
    
    if [ -f "leads_data.json" ]; then
        python3 -m json.tool leads_data.json
    else
        echo "No leads data found"
    fi
}

restart_asterisk() {
    echo -e "${YELLOW}Restarting Asterisk...${NC}"
    sudo systemctl restart asterisk
    sleep 2
    
    if systemctl is-active --quiet asterisk; then
        echo -e "${GREEN}✓ Asterisk restarted successfully${NC}"
    else
        echo -e "${RED}✗ Asterisk failed to start${NC}"
    fi
}

start_agent() {
    echo -e "${YELLOW}Starting AI Agent...${NC}"
    
    if [ ! -d "venv" ]; then
        echo -e "${RED}Virtual environment not found. Run setup.sh first.${NC}"
        exit 1
    fi
    
    source venv/bin/activate
    python3 ai_agent.py
}

connect_cli() {
    echo -e "${YELLOW}Connecting to Asterisk CLI...${NC}"
    echo -e "${YELLOW}(Use 'exit' or Ctrl+C to quit)${NC}"
    echo ""
    sudo asterisk -rvvv
}

test_extensions() {
    echo -e "${GREEN}=== Test Extensions ===${NC}"
    echo ""
    echo "1000 - Test User 1 (password: test1000)"
    echo "1001 - Test User 2 (password: test1001)"
    echo "9000 - AI Investment Advisor"
    echo "9001 - Echo Test"
    echo "9002 - Music on Hold"
    echo ""
    echo -e "${YELLOW}SIP Server: $(hostname -I | awk '{print $1}'):5060${NC}"
}

show_menu() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}AI Call Center Management${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "1. Show System Status"
    echo "2. Show Logs"
    echo "3. Show Lead Data"
    echo "4. Restart Asterisk"
    echo "5. Start AI Agent"
    echo "6. Connect to Asterisk CLI"
    echo "7. Show Test Extensions"
    echo "8. Exit"
    echo ""
    echo -n "Select option: "
}

# Main menu loop
if [ "$1" == "" ]; then
    while true; do
        show_menu
        read option
        
        case $option in
            1) show_status ;;
            2) show_logs ;;
            3) show_leads ;;
            4) restart_asterisk ;;
            5) start_agent ;;
            6) connect_cli ;;
            7) test_extensions ;;
            8) echo "Goodbye!"; exit 0 ;;
            *) echo -e "${RED}Invalid option${NC}" ;;
        esac
        
        echo ""
        echo -n "Press Enter to continue..."
        read
        clear
    done
else
    # Handle command line arguments
    case $1 in
        status) show_status ;;
        logs) show_logs ;;
        leads) show_leads ;;
        restart) restart_asterisk ;;
        start) start_agent ;;
        cli) connect_cli ;;
        test) test_extensions ;;
        *) echo "Usage: $0 {status|logs|leads|restart|start|cli|test}" ;;
    esac
fi
