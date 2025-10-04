# AI Call Center Agent - Investment Advisor

A professional AI-powered call center agent built with Asterisk ARI, Deepgram (Speech-to-Text), and OpenAI (GPT-4 + TTS). This system is designed to qualify investment leads through natural conversations and generate hot leads for financial advisors.

## 🌟 Features

- **Asterisk ARI Integration**: Uses modern ARI (Asterisk REST Interface) instead of AGI for better performance
- **AI-Powered Conversations**: OpenAI GPT-4 for intelligent, context-aware responses
- **Advanced Speech Processing**: 
  - Deepgram for real-time speech-to-text transcription
  - OpenAI TTS for natural-sounding voice responses
- **Lead Qualification**: Automatically qualifies investment leads by gathering:
  - Investment interests (stocks, bonds, real estate, crypto)
  - Investment amount
  - Risk tolerance
  - Investment timeline
- **Professional Setup**: Production-ready configuration with all Asterisk modules
- **Internal Testing**: Pre-configured extensions for testing and development

## 📋 Requirements

- Ubuntu 22.04 LTS (recommended)
- Root/sudo access
- Internet connection for downloading packages
- API Keys:
  - OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
  - Deepgram API key ([Get one here](https://console.deepgram.com/))

## 🚀 Quick Start

### 1. Install Asterisk

Run the installation script to install Asterisk with all modules and dependencies:

```bash
sudo bash install_asterisk_ubuntu22.sh
```

This will install:
- Asterisk 20 with all modules
- PJSIP library
- All required dependencies
- Sound files
- System service configuration

⏱️ **Installation time**: 15-30 minutes

### 2. Setup the AI Agent

Run the setup script to configure everything:

```bash
bash setup.sh
```

This will:
- Copy Asterisk configuration files
- Create Python virtual environment
- Install Python dependencies
- Setup environment configuration template

### 3. Configure API Keys

Edit the `.env` file and add your API keys:

```bash
nano .env
```

Required configuration:
```env
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
```

### 4. Start the AI Agent

Activate the virtual environment and run the agent:

```bash
source venv/bin/activate
python3 ai_agent.py
```

## 📞 Testing

### Test Extensions

The system comes with pre-configured test extensions:

| Extension | Description | Credentials |
|-----------|-------------|-------------|
| 1000 | Test User 1 | Username: 1000, Password: test1000 |
| 1001 | Test User 2 | Username: 1001, Password: test1001 |
| 9000 | AI Investment Advisor | Connects to AI agent |
| 9001 | Echo Test | Tests audio quality |
| 9002 | Music on Hold | Tests audio playback |

### Using a SIP Client

1. **Download a SIP client**:
   - Desktop: [Zoiper](https://www.zoiper.com/), [MicroSIP](https://www.microsip.org/)
   - Mobile: Zoiper, Linphone

2. **Configure the client**:
   - Server: Your server IP address
   - Port: 5060
   - Username: 1000 (or 1001)
   - Password: test1000 (or test1001)

3. **Make a test call**:
   - Dial 9000 to speak with the AI Investment Advisor
   - Dial 9001 for echo test
   - Dial 1000 or 1001 to call another extension

### Internal Testing

Call extension 9000 from extension 1000:

```
Extension 1000 -> Dials 9000 -> AI Agent answers and starts conversation
```

## 🏗️ Architecture

```
┌─────────────────┐
│   SIP Client    │
│  (Extension)    │
└────────┬────────┘
         │
         │ SIP/RTP
         │
┌────────▼────────┐
│   Asterisk      │
│   PJSIP + ARI   │
└────────┬────────┘
         │
         │ WebSocket (ARI)
         │
┌────────▼────────┐
│   AI Agent      │
│   (Python)      │
└────┬────────┬───┘
     │        │
     │        └──────────────┐
     │                       │
┌────▼──────┐      ┌────────▼─────┐
│  Deepgram │      │    OpenAI    │
│    STT    │      │  GPT-4 + TTS │
└───────────┘      └──────────────┘
```

## 📁 Project Structure

```
autoai/
├── install_asterisk_ubuntu22.sh  # Asterisk installation script
├── setup.sh                       # AI agent setup script
├── ai_agent.py                    # Main AI agent application
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── asterisk_config/               # Asterisk configuration files
│   ├── ari.conf                  # ARI configuration
│   ├── asterisk.conf             # Main Asterisk config
│   ├── extensions.conf           # Dialplan
│   ├── http.conf                 # HTTP/WebSocket config
│   ├── logger.conf               # Logging config
│   ├── pjsip.conf                # PJSIP/SIP config
│   └── rtp.conf                  # RTP/media config
├── leads_data.json               # Saved lead data (created at runtime)
└── README.md                     # This file
```

## 🔧 Configuration

### Asterisk Configuration

All configuration files are in the `asterisk_config/` directory:

- **ari.conf**: ARI user credentials and settings
- **pjsip.conf**: SIP endpoints, authentication, and transport
- **extensions.conf**: Dialplan and routing logic
- **http.conf**: HTTP server for ARI WebSocket
- **rtp.conf**: RTP settings for audio streams

### Customization

#### Change Public IP (for remote access)

Edit `asterisk_config/pjsip.conf`:

```ini
[transport-udp]
external_media_address=YOUR_PUBLIC_IP
external_signaling_address=YOUR_PUBLIC_IP
```

#### Add More Extensions

Edit `asterisk_config/pjsip.conf`:

```ini
[1002]
type=endpoint
context=internal
aors=1002
auth=1002
; ... other settings

[1002]
type=auth
auth_type=userpass
password=test1002
username=1002

[1002]
type=aor
max_contacts=1
```

#### Customize AI Personality

Edit `ai_agent.py`, find the `system_prompt` in `generate_ai_response()`:

```python
system_prompt = """You are Alex, a professional investment advisor...
[Customize the prompt here]
"""
```

## 🎯 AI Agent Capabilities

The AI Investment Advisor is designed to:

1. **Greet callers professionally**
2. **Ask qualifying questions**:
   - Type of investments interested in
   - Investment amount
   - Risk tolerance
   - Investment timeline
3. **Extract lead information** from natural conversation
4. **Qualify leads** based on gathered information
5. **Schedule follow-ups** for qualified leads
6. **Save lead data** for review

### Lead Qualification Criteria

A lead is considered "qualified" when the AI has collected:
- ✅ Investment interest type
- ✅ Approximate investment amount
- ✅ Risk tolerance level

Qualified leads receive a callback promise from a human advisor.

## 📊 Viewing Lead Data

All qualified leads are saved to `leads_data.json`:

```bash
cat leads_data.json | python3 -m json.tool
```

Example lead data:
```json
{
  "caller_number": "1000",
  "call_time": "2024-01-15T10:30:00",
  "investment_interest": "stocks",
  "investment_amount": "50000",
  "risk_tolerance": "moderate",
  "qualified": true
}
```

## 🔍 Troubleshooting

### Asterisk won't start

```bash
# Check logs
sudo journalctl -u asterisk -n 50

# Check configuration
sudo asterisk -rx "core show settings"

# Test configuration
sudo asterisk -rx "core reload"
```

### AI Agent connection issues

```bash
# Check Asterisk ARI status
sudo asterisk -rx "ari show status"

# Verify HTTP server is running
sudo asterisk -rx "http show status"

# Check WebSocket endpoint
curl -u ai_agent:ai_agent_secure_password_123 \
  http://localhost:8088/ari/applications
```

### Audio issues

```bash
# Check RTP ports are open
sudo netstat -tulpn | grep asterisk

# Verify codec configuration
sudo asterisk -rx "core show codecs"

# Test audio
sudo asterisk -rx "core show channels"
```

### Python dependencies

```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Check for errors
python3 -c "import aiohttp, websockets, deepgram; print('OK')"
```

## 🛡️ Security Considerations

### Production Deployment

1. **Change default passwords** in all configuration files
2. **Use TLS/SSL** for SIP and HTTP (configure in pjsip.conf and http.conf)
3. **Configure firewall** rules:
   ```bash
   sudo ufw allow 5060/udp  # SIP
   sudo ufw allow 10000:20000/udp  # RTP
   sudo ufw allow 8088/tcp  # ARI (restrict to localhost in production)
   ```
4. **Secure API keys** - never commit .env to version control
5. **Use strong passwords** for all SIP accounts
6. **Enable fail2ban** for Asterisk
7. **Regular updates**: Keep Asterisk and dependencies updated

## 📚 Additional Resources

- [Asterisk Documentation](https://wiki.asterisk.org/)
- [Asterisk ARI Documentation](https://wiki.asterisk.org/wiki/display/AST/Asterisk+REST+Interface)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Deepgram API Documentation](https://developers.deepgram.com/)

## 🤝 Support

For issues and questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Asterisk logs: `tail -f /var/log/asterisk/full`
3. Check AI agent logs: `tail -f ai_agent.log`

## 📝 License

This project is provided as-is for educational and commercial use.

## 🚀 Advanced Features

### Scaling for Production

- Use Redis for session management across multiple instances
- Implement database backend (PostgreSQL) for lead storage
- Add load balancing for multiple Asterisk servers
- Implement CDR (Call Detail Records) analysis
- Add real-time dashboard for monitoring calls

### Integrations

- **CRM Integration**: Export leads to Salesforce, HubSpot, etc.
- **Calendar Integration**: Auto-schedule callbacks
- **SMS Notifications**: Send follow-up texts to leads
- **Email Reports**: Daily lead summaries
- **Analytics**: Track conversion rates and call metrics

---

**Built with ❤️ for professional AI call center operations**