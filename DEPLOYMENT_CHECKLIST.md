# Production Deployment Checklist

Use this checklist when deploying the AI Call Center Agent to production.

## Pre-Deployment

### Infrastructure
- [ ] Server meets minimum requirements (2GB RAM, 2 CPU cores, Ubuntu 22.04)
- [ ] Static IP address assigned
- [ ] DNS configured (if using domain name)
- [ ] Firewall configured (UFW or iptables)
- [ ] Backup system in place
- [ ] Monitoring tools installed (optional but recommended)

### Security
- [ ] Change ALL default passwords in configuration files
- [ ] Generate strong password for ARI (ari.conf)
- [ ] Update SIP extension passwords (pjsip.conf)
- [ ] Configure TLS/SSL certificates (optional but recommended)
- [ ] Set up fail2ban for Asterisk (recommended)
- [ ] Configure SSH key-based authentication
- [ ] Disable root SSH login

### API Keys
- [ ] OpenAI API key obtained and tested
- [ ] Deepgram API key obtained and tested
- [ ] API keys stored securely in .env file
- [ ] Billing alerts configured for API usage
- [ ] Rate limits understood and documented

## Installation

### Asterisk Installation
- [ ] Run `install_asterisk_ubuntu22.sh` as root
- [ ] Verify Asterisk is running: `systemctl status asterisk`
- [ ] Check Asterisk CLI: `asterisk -rvvv`
- [ ] Verify modules loaded: `module show like res_ari`

### AI Agent Setup
- [ ] Run `setup.sh` script
- [ ] Python virtual environment created
- [ ] All dependencies installed without errors
- [ ] Configuration files copied to /etc/asterisk/
- [ ] Asterisk restarted after config update

### Network Configuration
- [ ] Update external IP in pjsip.conf
- [ ] Configure router port forwarding if needed
- [ ] Open required firewall ports:
  ```bash
  sudo ufw allow 5060/udp    # SIP
  sudo ufw allow 5060/tcp    # SIP over TCP
  sudo ufw allow 10000:20000/udp  # RTP
  # sudo ufw allow 8088/tcp  # Only if ARI needs external access
  ```

## Configuration

### Asterisk Configuration Review
- [ ] Review and update pjsip.conf
  - [ ] Update external_media_address
  - [ ] Update external_signaling_address
  - [ ] Review local_net settings
  - [ ] Change extension passwords
  
- [ ] Review extensions.conf
  - [ ] Verify dialplan logic
  - [ ] Test extension routing
  - [ ] Add custom extensions if needed

- [ ] Review ari.conf
  - [ ] Change ARI password
  - [ ] Restrict allowed_origins in production

- [ ] Review http.conf
  - [ ] Consider enabling TLS
  - [ ] Bind to localhost if not needed externally

### AI Agent Configuration
- [ ] Edit .env file with production values
- [ ] Test API connections manually
- [ ] Review ai_agent.py system prompt
- [ ] Customize AI personality if needed
- [ ] Adjust conversation length limits

## Testing

### Basic Functionality
- [ ] Register test SIP client (extension 1000)
- [ ] Test echo (dial 9001)
- [ ] Test music on hold (dial 9002)
- [ ] Test inter-extension calling (1000 → 1001)

### AI Agent Testing
- [ ] Start AI agent: `python3 ai_agent.py`
- [ ] Call extension 9000 from test phone
- [ ] Verify AI answers and speaks
- [ ] Test conversation flow
- [ ] Verify audio quality
- [ ] Check lead data is saved
- [ ] Review logs for errors

### Load Testing (if high traffic expected)
- [ ] Test with multiple concurrent calls
- [ ] Monitor CPU and memory usage
- [ ] Check network bandwidth usage
- [ ] Verify API rate limits not exceeded

## Production Deployment

### Run as Service
- [ ] Copy systemd service file:
  ```bash
  sudo cp systemd/ai-agent.service /etc/systemd/system/
  ```
- [ ] Update paths in service file if needed
- [ ] Enable service: `sudo systemctl enable ai-agent`
- [ ] Start service: `sudo systemctl start ai-agent`
- [ ] Verify service running: `sudo systemctl status ai-agent`

### Monitoring Setup
- [ ] Configure log rotation for Asterisk logs
- [ ] Configure log rotation for AI agent logs
- [ ] Set up log monitoring (optional)
- [ ] Configure alerting for service failures
- [ ] Set up uptime monitoring
- [ ] Monitor disk space usage

### Documentation
- [ ] Document custom configuration changes
- [ ] Create runbook for common issues
- [ ] Document emergency contacts
- [ ] Create backup and restore procedures
- [ ] Document scaling strategy

## Post-Deployment

### Monitoring (First 24 Hours)
- [ ] Monitor system resources (CPU, RAM, disk)
- [ ] Check Asterisk logs: `tail -f /var/log/asterisk/full`
- [ ] Check AI agent logs: `tail -f ai_agent.log`
- [ ] Monitor API usage and costs
- [ ] Test from external network
- [ ] Verify call quality

### Data Management
- [ ] Set up automatic backup of leads_data.json
- [ ] Configure database if using (instead of JSON)
- [ ] Set up data export/reporting
- [ ] Implement data retention policy
- [ ] Configure GDPR/privacy compliance

### Optimization
- [ ] Review and optimize system prompt based on conversations
- [ ] Adjust lead qualification criteria if needed
- [ ] Fine-tune conversation timeout settings
- [ ] Optimize RTP settings for network
- [ ] Review and adjust codec priorities

## Security Hardening

### System Security
- [ ] Install and configure fail2ban
- [ ] Set up automatic security updates
- [ ] Configure intrusion detection (optional)
- [ ] Regular security audits scheduled
- [ ] Implement least-privilege access

### Application Security
- [ ] Validate all input from callers
- [ ] Implement rate limiting
- [ ] Regular password rotation
- [ ] API key rotation schedule
- [ ] Regular dependency updates

### Compliance
- [ ] GDPR compliance review (if applicable)
- [ ] HIPAA compliance review (if applicable)
- [ ] PCI compliance review (if handling payments)
- [ ] Call recording consent (if recording enabled)
- [ ] Privacy policy updated

## Backup and Disaster Recovery

### Backup Configuration
- [ ] Asterisk configuration files backed up
- [ ] AI agent application backed up
- [ ] Lead data backed up regularly
- [ ] Backup restoration tested
- [ ] Offsite backup configured

### Disaster Recovery Plan
- [ ] Recovery time objective (RTO) defined
- [ ] Recovery point objective (RPO) defined
- [ ] Failover procedure documented
- [ ] Emergency contact list created
- [ ] DR plan tested

## Scaling Preparation

### Current Capacity Documented
- [ ] Maximum concurrent calls documented
- [ ] Average call duration documented
- [ ] Peak usage times identified
- [ ] Resource utilization baseline established

### Scaling Strategy
- [ ] Vertical scaling plan (when to upgrade server)
- [ ] Horizontal scaling plan (when to add servers)
- [ ] Load balancer configuration prepared
- [ ] Database migration plan (if moving from JSON)
- [ ] Cost projections for scaling

## Maintenance Schedule

### Daily
- [ ] Check service status
- [ ] Review error logs
- [ ] Monitor API usage
- [ ] Check lead data

### Weekly
- [ ] Review call quality
- [ ] Analyze lead qualification rate
- [ ] Check disk space
- [ ] Review system performance

### Monthly
- [ ] Update dependencies
- [ ] Security patch review
- [ ] Performance optimization
- [ ] Cost analysis
- [ ] Backup restoration test

### Quarterly
- [ ] Full system audit
- [ ] Disaster recovery drill
- [ ] Capacity planning review
- [ ] Security assessment
- [ ] Documentation update

## Troubleshooting Quick Reference

### Service Won't Start
```bash
# Check logs
sudo journalctl -u ai-agent -n 50
sudo journalctl -u asterisk -n 50

# Verify configuration
sudo asterisk -rx "core show settings"

# Test manually
source venv/bin/activate
python3 ai_agent.py
```

### No Audio in Calls
```bash
# Check RTP configuration
sudo asterisk -rx "rtp show settings"

# Verify codecs
sudo asterisk -rx "core show codecs"

# Check firewall
sudo ufw status
```

### API Errors
```bash
# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Test Deepgram
curl https://api.deepgram.com/v1/projects \
  -H "Authorization: Token $DEEPGRAM_API_KEY"
```

### High Resource Usage
```bash
# Check processes
top
htop

# Check Asterisk channels
sudo asterisk -rx "core show channels"

# Check connections
sudo netstat -tnlp | grep asterisk
```

## Contact Information

**System Administrator**: _____________________

**On-Call Contact**: _____________________

**Escalation Contact**: _____________________

**Vendor Support**: 
- Asterisk: https://www.asterisk.org/community/
- OpenAI: https://help.openai.com/
- Deepgram: https://support.deepgram.com/

---

## Sign-Off

**Deployed By**: _____________________

**Date**: _____________________

**Reviewed By**: _____________________

**Date**: _____________________

**Production Approval**: _____________________

**Date**: _____________________

---

*Keep this checklist updated as the system evolves.*
