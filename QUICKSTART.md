# Quick Start Guide

## Step-by-Step Installation (Ubuntu 22.04)

### 1. Prepare Your Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install git
sudo apt install -y git

# Clone the repository
git clone https://github.com/Pormetrixx/autoai.git
cd autoai
```

### 2. Install Asterisk

```bash
# Run the installation script (takes 15-30 minutes)
sudo bash install_asterisk_ubuntu22.sh
```

☕ **Grab a coffee** - This will take a while!

### 3. Setup the AI Agent

```bash
# Run setup script
bash setup.sh

# Edit configuration file and add your API keys
nano .env
```

Add your API keys:
```
OPENAI_API_KEY=sk-your-key-here
DEEPGRAM_API_KEY=your-key-here
```

### 4. Start Everything

```bash
# Start Asterisk
sudo systemctl start asterisk

# Check status
sudo systemctl status asterisk

# Activate Python environment
source venv/bin/activate

# Start AI Agent
python3 ai_agent.py
```

### 5. Test the System

#### Option A: Using a SoftPhone (Recommended)

1. Download [Zoiper](https://www.zoiper.com/) or [MicroSIP](https://www.microsip.org/)

2. Configure account:
   - **Server**: Your server IP
   - **Port**: 5060
   - **Username**: 1000
   - **Password**: test1000

3. Dial **9000** to talk to the AI Investment Advisor!

#### Option B: Using Asterisk CLI

```bash
# Connect to CLI
sudo asterisk -rvvv

# Originate a test call
channel originate Local/9000@internal application Playback demo-congrats
```

## Common Commands

```bash
# Check Asterisk status
sudo systemctl status asterisk

# View Asterisk logs
sudo tail -f /var/log/asterisk/full

# View AI Agent logs
tail -f ai_agent.log

# Connect to Asterisk CLI
sudo asterisk -rvvv

# Restart Asterisk
sudo systemctl restart asterisk

# View lead data
cat leads_data.json | python3 -m json.tool
```

## Testing Extensions

| Extension | Purpose |
|-----------|---------|
| **9000** | AI Investment Advisor (main feature) |
| **9001** | Echo test (audio quality check) |
| **9002** | Music on hold test |
| **1000/1001** | Call between test extensions |

## Management Script

Use the management script for easy administration:

```bash
# Interactive menu
./manage.sh

# Or use commands directly
./manage.sh status    # Show system status
./manage.sh logs      # View logs
./manage.sh leads     # View lead data
./manage.sh restart   # Restart Asterisk
./manage.sh start     # Start AI agent
./manage.sh cli       # Connect to Asterisk CLI
```

## Troubleshooting Quick Fixes

### Asterisk won't start
```bash
# Check for errors
sudo journalctl -u asterisk -n 50

# Verify configuration
sudo asterisk -rx "core show settings"
```

### Can't connect to ARI
```bash
# Check if HTTP is enabled
sudo asterisk -rx "http show status"

# Should show: HTTP Server Status: Enabled
```

### No audio in calls
```bash
# Check RTP configuration
sudo asterisk -rx "rtp show settings"

# Verify firewall allows RTP ports
sudo ufw status
```

### AI Agent can't connect
```bash
# Verify .env file exists and has API keys
cat .env

# Check Python dependencies
source venv/bin/activate
pip list | grep -E "(aiohttp|websockets|deepgram|openai)"
```

## Running as a Service

To run the AI agent as a systemd service:

```bash
# Copy service file
sudo cp systemd/ai-agent.service /etc/systemd/system/

# Edit paths if needed
sudo nano /etc/systemd/system/ai-agent.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable ai-agent
sudo systemctl start ai-agent

# Check status
sudo systemctl status ai-agent

# View logs
sudo journalctl -u ai-agent -f
```

## Docker Deployment (Alternative)

If you prefer Docker:

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Next Steps

1. ✅ Test internal calls (1000 → 9000)
2. ✅ Review lead data in `leads_data.json`
3. 🔧 Customize AI personality in `ai_agent.py`
4. 🔧 Add more extensions in `asterisk_config/pjsip.conf`
5. 🔒 Secure your deployment (change passwords, enable TLS)
6. 🚀 Connect to external SIP trunk for real calls
7. 📊 Set up monitoring and analytics

## Getting API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy and save in `.env`

### Deepgram API Key
1. Go to https://console.deepgram.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy and save in `.env`

## Performance Tips

- Use at least **2GB RAM** for smooth operation
- **2 CPU cores** recommended
- **SSD storage** for better I/O
- Open **UDP ports 10000-20000** for RTP
- Use **wired network** connection when possible
- Consider **dedicated server** for production

## Success Indicators

You'll know everything is working when:

1. ✅ Asterisk service is running: `systemctl status asterisk`
2. ✅ AI agent connects without errors
3. ✅ You can register a SIP client (extension 1000)
4. ✅ Calling 9000 connects to the AI agent
5. ✅ AI agent speaks and responds to your voice
6. ✅ Lead data is saved to `leads_data.json`

Enjoy your AI Call Center! 🎉
