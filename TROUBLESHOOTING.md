# Troubleshooting Guide

This guide covers common issues and their solutions.

## Quick Diagnostics

Run these commands to get an overview of system status:

```bash
# Check all services
./manage.sh status

# Check recent logs
./manage.sh logs

# Check lead data
./manage.sh leads
```

---

## Installation Issues

### Issue: Asterisk compilation fails

**Symptoms**: 
- `make` command fails during installation
- Missing dependency errors

**Solutions**:
```bash
# Ensure all dependencies are installed
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev libncurses5-dev

# Check available disk space (need at least 2GB)
df -h

# Check for previous failed installations
cd /usr/src
sudo rm -rf asterisk-* pjproject-*

# Re-run installation script
sudo bash install_asterisk_ubuntu22.sh
```

### Issue: Python dependencies fail to install

**Symptoms**:
- `pip install` errors
- Package conflicts

**Solutions**:
```bash
# Upgrade pip
python3 -m pip install --upgrade pip

# Install system dependencies
sudo apt-get install -y python3-dev build-essential

# Create fresh virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies one by one to identify problem
pip install aiohttp
pip install websockets
pip install deepgram-sdk
pip install openai
pip install python-dotenv
```

---

## Asterisk Issues

### Issue: Asterisk won't start

**Symptoms**:
- `systemctl start asterisk` fails
- Service shows as "failed"

**Diagnosis**:
```bash
# Check status
sudo systemctl status asterisk

# Check logs
sudo journalctl -u asterisk -n 100

# Check configuration
sudo asterisk -rx "core show settings"
```

**Common Solutions**:

1. **Configuration Error**:
```bash
# Test configuration files
sudo asterisk -c  # Start in console mode
# Look for errors in output
# Press Ctrl+C to stop
```

2. **Port Already in Use**:
```bash
# Check what's using port 5060
sudo netstat -tulpn | grep 5060

# Kill the process if needed
sudo kill <PID>
```

3. **Permission Issues**:
```bash
# Fix permissions
sudo chown -R asterisk:asterisk /etc/asterisk
sudo chown -R asterisk:asterisk /var/lib/asterisk
sudo chown -R asterisk:asterisk /var/log/asterisk
```

### Issue: SIP registration fails

**Symptoms**:
- Can't register SIP client
- "401 Unauthorized" errors

**Solutions**:
```bash
# Check PJSIP endpoints
sudo asterisk -rx "pjsip show endpoints"

# Check authentication
sudo asterisk -rx "pjsip show auths"

# Verify passwords in pjsip.conf
sudo cat /etc/asterisk/pjsip.conf | grep -A5 "\[1000\]"

# Check if PJSIP is loaded
sudo asterisk -rx "module show like pjsip"

# Reload PJSIP configuration
sudo asterisk -rx "module reload res_pjsip.so"
```

### Issue: No audio in calls

**Symptoms**:
- Call connects but no audio
- One-way audio only

**Diagnosis**:
```bash
# Check RTP configuration
sudo asterisk -rx "rtp show settings"

# Check active channels
sudo asterisk -rx "core show channels"

# Check codec negotiation
sudo asterisk -rx "core show channel <channel-id>"
```

**Solutions**:

1. **Firewall Blocking RTP**:
```bash
# Open RTP ports
sudo ufw allow 10000:20000/udp

# Check firewall status
sudo ufw status
```

2. **NAT Issues**:
```bash
# Update pjsip.conf with correct external IP
sudo nano /etc/asterisk/pjsip.conf

# Find and update:
external_media_address=YOUR_PUBLIC_IP
external_signaling_address=YOUR_PUBLIC_IP

# Restart Asterisk
sudo systemctl restart asterisk
```

3. **Codec Mismatch**:
```bash
# Check supported codecs
sudo asterisk -rx "core show codecs"

# Ensure common codec (ulaw) is enabled in pjsip.conf
allow=ulaw
```

---

## AI Agent Issues

### Issue: AI Agent won't start

**Symptoms**:
- Python script crashes on start
- "Connection refused" errors

**Diagnosis**:
```bash
# Check if Asterisk is running
sudo systemctl status asterisk

# Check ARI is enabled
sudo asterisk -rx "ari show status"

# Check HTTP server
sudo asterisk -rx "http show status"
```

**Solutions**:

1. **Asterisk Not Running**:
```bash
sudo systemctl start asterisk
```

2. **ARI Not Configured**:
```bash
# Verify ari.conf
sudo cat /etc/asterisk/ari.conf

# Restart Asterisk
sudo systemctl restart asterisk
```

3. **Wrong Credentials**:
```bash
# Check .env file
cat .env | grep ARI

# Test ARI connection manually
curl -u ai_agent:ai_agent_secure_password_123 \
  http://localhost:8088/ari/applications
```

### Issue: API authentication errors

**Symptoms**:
- "Invalid API key" errors
- 401/403 responses from APIs

**Solutions**:

1. **Check API Keys**:
```bash
# Verify .env file exists
ls -la .env

# Check keys are set
cat .env | grep API_KEY
```

2. **Test OpenAI API**:
```bash
# Load environment
source venv/bin/activate

# Test manually
python3 << EOF
import os
from dotenv import load_dotenv
load_dotenv()
print("OpenAI Key:", os.getenv('OPENAI_API_KEY')[:10] + "...")
print("Deepgram Key:", os.getenv('DEEPGRAM_API_KEY')[:10] + "...")
EOF
```

3. **Test API Endpoints**:
```bash
# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Test Deepgram
curl https://api.deepgram.com/v1/projects \
  -H "Authorization: Token $DEEPGRAM_API_KEY"
```

### Issue: AI responses are slow

**Symptoms**:
- Long delays between caller speaking and AI responding
- Timeout errors

**Solutions**:

1. **Use Faster Models**:
```python
# In ai_agent.py, change to:
'model': 'gpt-3.5-turbo'  # Instead of gpt-4-turbo-preview
```

2. **Optimize Prompts**:
```python
# Reduce max_tokens
'max_tokens': 100  # Instead of 150
```

3. **Check Network Latency**:
```bash
# Test latency to APIs
ping api.openai.com
ping api.deepgram.com
```

### Issue: Transcription accuracy is poor

**Symptoms**:
- AI misunderstands what caller said
- Gibberish transcripts

**Solutions**:

1. **Check Audio Quality**:
```bash
# Test with echo (dial 9001)
# Speak clearly and check playback quality
```

2. **Adjust Recording Settings**:
```python
# In ai_agent.py, modify recording parameters
'maxSilenceSeconds': 2  # Instead of 3
```

3. **Use Better Codec**:
```bash
# In pjsip.conf, prioritize high-quality codecs
disallow=all
allow=opus  # HD audio
allow=g722  # Wideband
allow=ulaw  # Standard
```

---

## Call Quality Issues

### Issue: Choppy audio

**Symptoms**:
- Robotic-sounding voice
- Intermittent audio dropouts

**Solutions**:

1. **Check Network**:
```bash
# Test bandwidth
speedtest-cli

# Check packet loss
ping -c 100 8.8.8.8
```

2. **Adjust RTP Settings**:
```bash
# Edit rtp.conf
sudo nano /etc/asterisk/rtp.conf

# Increase buffer (if network is slow)
# Add: rtpbuffer=yes
```

3. **Change Codec**:
```bash
# Use ulaw instead of gsm for better quality
# Edit pjsip.conf
allow=ulaw
allow=alaw
```

### Issue: Echo on calls

**Symptoms**:
- Caller hears themselves
- Echo feedback

**Solutions**:

1. **Disable Direct Media**:
```bash
# In pjsip.conf
direct_media=no
```

2. **Enable Echo Cancellation**:
```bash
# In rtp.conf
sudo nano /etc/asterisk/rtp.conf
# Ensure it's enabled (should be by default)
```

---

## Performance Issues

### Issue: High CPU usage

**Symptoms**:
- System slows down
- Calls drop

**Diagnosis**:
```bash
# Check CPU usage
top
htop

# Check Asterisk specifically
ps aux | grep asterisk

# Check active calls
sudo asterisk -rx "core show channels"
```

**Solutions**:

1. **Too Many Concurrent Calls**:
```bash
# Limit concurrent calls in extensions.conf
# Add to [general] section:
maxcalls=10
```

2. **Codec Transcoding**:
```bash
# Use same codec for all endpoints
# In pjsip.conf, use only ulaw:
disallow=all
allow=ulaw
```

### Issue: High memory usage

**Symptoms**:
- System runs out of RAM
- OOM killer terminates processes

**Solutions**:

1. **Check Memory Usage**:
```bash
free -h
top
```

2. **Restart Services**:
```bash
sudo systemctl restart asterisk
sudo systemctl restart ai-agent
```

3. **Upgrade Server**:
```bash
# If consistently hitting limits, upgrade to 4GB+ RAM
```

---

## Data Issues

### Issue: Leads not being saved

**Symptoms**:
- leads_data.json is empty
- Lead data lost after calls

**Diagnosis**:
```bash
# Check file permissions
ls -la leads_data.json

# Check for errors in logs
tail -f ai_agent.log | grep -i error
```

**Solutions**:

1. **Permission Issues**:
```bash
# Ensure file is writable
touch leads_data.json
chmod 666 leads_data.json
```

2. **JSON Corruption**:
```bash
# Validate JSON
python3 -m json.tool leads_data.json

# If invalid, reset
echo "[]" > leads_data.json
```

---

## Network Issues

### Issue: Can't connect from external network

**Symptoms**:
- Internal calls work
- External calls fail

**Solutions**:

1. **Check Firewall**:
```bash
# Ensure ports are open
sudo ufw status

# Open if needed
sudo ufw allow 5060/udp
sudo ufw allow 10000:20000/udp
```

2. **Check Router Port Forwarding**:
- Forward port 5060 (UDP) to server
- Forward ports 10000-20000 (UDP) to server

3. **Update External IP**:
```bash
# Get your public IP
curl ifconfig.me

# Update pjsip.conf
sudo nano /etc/asterisk/pjsip.conf
# Update external_media_address and external_signaling_address
```

---

## Debugging Tools

### Enable Verbose Logging

```bash
# Asterisk
sudo asterisk -rvvvvv  # More v's = more verbose

# Or in CLI
asterisk -rx "core set verbose 5"
asterisk -rx "core set debug 5"
```

### Capture SIP Traffic

```bash
# Install tcpdump
sudo apt-get install tcpdump

# Capture SIP traffic
sudo tcpdump -i any -n port 5060 -w sip_capture.pcap

# Analyze with Wireshark (on your local machine)
```

### Monitor Calls in Real-Time

```bash
# Connect to CLI
sudo asterisk -rvvv

# In CLI, run:
core show channels verbose
pjsip show endpoints
ari show apps
```

### Test Components Individually

```bash
# Test Asterisk only
sudo asterisk -rvvv
# Make calls between extensions 1000 and 1001

# Test ARI connection
curl -u ai_agent:ai_agent_secure_password_123 \
  http://localhost:8088/ari/applications

# Test OpenAI
python3 << EOF
import os, openai
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
print(openai.Model.list())
EOF
```

---

## Getting Help

### Check Logs

Always check logs first:

```bash
# Asterisk logs
sudo tail -f /var/log/asterisk/full

# AI Agent logs
tail -f ai_agent.log

# System logs
sudo journalctl -u asterisk -n 100
sudo journalctl -u ai-agent -n 100
```

### Community Resources

- **Asterisk**: https://community.asterisk.org/
- **OpenAI**: https://community.openai.com/
- **Deepgram**: https://github.com/deepgram/deepgram-python-sdk/issues

### Create Debug Report

When asking for help, provide:

```bash
# System info
uname -a
lsb_release -a

# Asterisk version
asterisk -V

# Python version
python3 --version

# Last 50 lines of logs
sudo tail -50 /var/log/asterisk/full
tail -50 ai_agent.log

# Configuration (remove passwords first!)
sudo cat /etc/asterisk/pjsip.conf
sudo cat /etc/asterisk/ari.conf
```

---

## Emergency Recovery

### Complete Reset

If everything is broken:

```bash
# Stop all services
sudo systemctl stop ai-agent
sudo systemctl stop asterisk

# Backup current config
sudo tar -czf /tmp/asterisk-backup-$(date +%Y%m%d).tar.gz /etc/asterisk

# Restore original configs
sudo cp asterisk_config/*.conf /etc/asterisk/

# Restart
sudo systemctl start asterisk
sudo systemctl start ai-agent
```

### Restore from Backup

```bash
# Stop services
sudo systemctl stop asterisk ai-agent

# Restore configuration
sudo tar -xzf /path/to/backup.tar.gz -C /

# Restore data
cp /path/to/leads_data.json.backup leads_data.json

# Start services
sudo systemctl start asterisk ai-agent
```

---

*For issues not covered here, check logs and consult the community resources above.*
