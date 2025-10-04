# Architecture and Technical Details

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        External World                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ SIP Phones   │  │ Soft Phones  │  │ SIP Trunks   │          │
│  │ (Hardware)   │  │ (Software)   │  │ (Providers)  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │      SIP/RTP Protocol (UDP/TCP)     │
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────────┐
│                     Firewall / Router                            │
│              Ports: 5060, 8088, 10000-20000                      │
└─────────┬────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────┐
│                    Asterisk PBX Server                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    PJSIP Stack                            │   │
│  │  - SIP Registration                                       │   │
│  │  - Call Routing                                           │   │
│  │  - Media Processing                                       │   │
│  │  - Codec Transcoding (ulaw, alaw, g722, opus)           │   │
│  └──────────────┬──────────────┬────────────────────────────┘   │
│                 │              │                                 │
│  ┌──────────────▼─────────┐   │ ┌────────────────────────────┐ │
│  │   Dialplan Engine      │   │ │    ARI WebSocket Server   │ │
│  │   (extensions.conf)    │   │ │    (Port 8088)            │ │
│  │                        │   │ │                            │ │
│  │  - Route to extension  │◄──┼─┤  - Event streaming        │ │
│  │  - Execute Stasis app  │   │ │  - Channel control        │ │
│  │  - Handle transfers    │   │ │  - Media manipulation     │ │
│  └────────────────────────┘   │ └──────────────┬─────────────┘ │
└───────────────────────────────┼────────────────┼───────────────┘
                                │                │
                    ┌───────────▼────────────────▼───────────────┐
                    │     WebSocket Connection (ARI Events)      │
                    └───────────┬────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                  AI Call Center Agent (Python)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Event Handler                          │  │
│  │  - StasisStart (incoming call)                           │  │
│  │  - StasisEnd (call ended)                                │  │
│  │  - ChannelDtmfReceived (keypad input)                    │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │              Conversation Manager                         │  │
│  │  - Track active calls                                     │  │
│  │  - Maintain conversation history                          │  │
│  │  - Manage call flow                                       │  │
│  └──────┬───────────────────┬──────────────────┬─────────────┘  │
│         │                   │                  │                │
│  ┌──────▼──────┐  ┌─────────▼────────┐  ┌─────▼──────────┐    │
│  │   Speech    │  │   AI Response    │  │  Lead Data     │    │
│  │  Processing │  │   Generation     │  │  Extraction    │    │
│  └──────┬──────┘  └─────────┬────────┘  └─────┬──────────┘    │
└─────────┼──────────────────┼──────────────────┼────────────────┘
          │                  │                  │
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼────────────────┐
│                      External APIs                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Deepgram    │  │   OpenAI     │  │   Data Storage       │ │
│  │     STT      │  │  GPT-4 + TTS │  │  (leads_data.json)   │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Asterisk PBX Server

**Purpose**: Handles all telephony operations

**Key Components**:
- **PJSIP**: Modern SIP stack for VoIP communication
- **Dialplan**: Call routing logic (extensions.conf)
- **ARI (Asterisk REST Interface)**: HTTP/WebSocket API for external control
- **RTP Engine**: Real-time media streaming
- **Codec Support**: ulaw, alaw, g722, gsm, opus

**Configuration Files**:
```
asterisk_config/
├── ari.conf          # ARI users and permissions
├── asterisk.conf     # Main Asterisk configuration
├── extensions.conf   # Dialplan and call routing
├── http.conf         # HTTP server for ARI
├── logger.conf       # Logging configuration
├── pjsip.conf        # SIP endpoints and transport
└── rtp.conf          # RTP media settings
```

### 2. AI Call Center Agent (Python)

**Purpose**: Intelligent call handling and conversation management

**Core Modules**:

#### a. Event Handler
- Listens to ARI WebSocket for Asterisk events
- Handles `StasisStart`, `StasisEnd`, `ChannelDtmfReceived`
- Manages call lifecycle

#### b. Conversation Manager
- Tracks active calls with unique channel IDs
- Maintains conversation history per call
- Implements conversation flow logic
- Determines when to end calls

#### c. Speech Processing
- **Input**: Audio from caller (via Asterisk recording)
- **Processing**: Deepgram STT API for transcription
- **Output**: Text transcript

#### d. AI Response Generation
- **Input**: Conversation history + user transcript
- **Processing**: OpenAI GPT-4 for intelligent responses
- **Output**: Natural language response

#### e. Text-to-Speech
- **Input**: AI-generated text response
- **Processing**: OpenAI TTS API
- **Output**: Audio file (WAV format)
- **Playback**: Streamed to caller via Asterisk

#### f. Lead Qualification
- Extracts key information from conversation
- Tracks: investment type, amount, risk tolerance, timeline
- Qualifies leads based on completeness
- Saves data to JSON (or database)

### 3. External APIs

#### Deepgram (Speech-to-Text)
- **Model**: Nova-2 (latest)
- **Features**: Real-time or batch transcription
- **Language**: English (configurable)
- **Accuracy**: 95%+ for clear audio

#### OpenAI
- **GPT-4**: Conversation AI
  - Model: `gpt-4-turbo-preview`
  - Context: System prompt + conversation history
  - Temperature: 0.7 (balanced creativity)
  
- **TTS (Text-to-Speech)**:
  - Model: `tts-1`
  - Voice: `alloy` (configurable: alloy, echo, fable, onyx, nova, shimmer)
  - Format: WAV (compatible with Asterisk)

## Data Flow

### Incoming Call Flow

```
1. Phone rings → Asterisk receives SIP INVITE
   ↓
2. Dialplan matches extension (9000)
   ↓
3. Executes Stasis(ai-call-center) application
   ↓
4. StasisStart event sent to AI Agent via WebSocket
   ↓
5. AI Agent answers call (ARI: POST /channels/{id}/answer)
   ↓
6. AI Agent speaks greeting (OpenAI TTS → Asterisk playback)
   ↓
7. AI Agent starts recording (ARI: POST /channels/{id}/record)
   ↓
8. Caller speaks → Audio recorded
   ↓
9. Recording complete → Transcribed by Deepgram
   ↓
10. Transcript sent to OpenAI GPT-4
    ↓
11. GPT-4 generates response
    ↓
12. Response converted to speech (OpenAI TTS)
    ↓
13. Audio played to caller
    ↓
14. Repeat steps 7-13 until conversation complete
    ↓
15. AI Agent ends call (ARI: DELETE /channels/{id})
    ↓
16. StasisEnd event → Save lead data
```

### Lead Qualification Flow

```
Conversation Start
    ↓
Ask about investment interest → Extract keywords (stocks, bonds, etc.)
    ↓
Ask about investment amount → Extract numbers ($50k, $100k, etc.)
    ↓
Ask about risk tolerance → Extract preference (conservative, moderate, aggressive)
    ↓
Ask about timeline → Extract duration (short-term, long-term)
    ↓
Check if all data collected
    ↓
    ├─ YES: Mark as "qualified" → Offer callback → End call
    └─ NO:  Continue asking questions → Loop back
```

## Technology Stack

### Backend
- **Python 3.10+**: Main programming language
- **asyncio**: Asynchronous I/O for concurrent call handling
- **aiohttp**: Async HTTP client for API calls
- **websockets**: WebSocket client for ARI events

### Telephony
- **Asterisk 20**: Open-source PBX
- **PJSIP 2.13**: SIP protocol implementation
- **ARI**: REST API for call control

### AI & ML
- **OpenAI GPT-4**: Natural language understanding and generation
- **OpenAI TTS**: Text-to-speech synthesis
- **Deepgram**: Speech-to-text transcription

### Infrastructure
- **Ubuntu 22.04 LTS**: Operating system
- **systemd**: Service management
- **Docker** (optional): Containerization

## Scalability Considerations

### Current Capacity
- **Concurrent Calls**: ~10-20 (single server, 2GB RAM)
- **CPU**: 2 cores recommended
- **Network**: ~100 kbps per call

### Scaling Strategies

#### Vertical Scaling
- Increase RAM (4GB → 8GB → 16GB)
- Add CPU cores (2 → 4 → 8)
- Use SSD for faster I/O

#### Horizontal Scaling
- Multiple Asterisk instances behind load balancer
- Shared Redis for session management
- Database for lead storage (PostgreSQL)
- Message queue for event processing (RabbitMQ)

#### Production Architecture
```
                    ┌─────────────┐
                    │ Load Balance│
                    │  (HAProxy)  │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌────▼──────┐
    │ Asterisk 1│    │ Asterisk 2│    │Asterisk N │
    └─────┬─────┘    └─────┬─────┘    └────┬──────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼──────┐
                    │    Redis    │
                    │   (Session) │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌────▼──────┐
    │ AI Agent 1│    │ AI Agent 2│    │ AI Agent N│
    └───────────┘    └───────────┘    └───────────┘
                           │
                    ┌──────▼──────┐
                    │ PostgreSQL  │
                    │   (Leads)   │
                    └─────────────┘
```

## Security Architecture

### Network Security
- **Firewall**: UFW/iptables
- **Open Ports**: Minimal (5060, 8088, RTP range)
- **TLS/SSL**: For SIP and HTTP
- **VPN**: Recommended for admin access

### Application Security
- **Authentication**: Strong passwords (20+ chars)
- **API Keys**: Stored in `.env` (never in code)
- **Input Validation**: Sanitize all user inputs
- **Rate Limiting**: Prevent abuse
- **Logging**: Audit trail for all calls

### Data Security
- **Encryption**: TLS for all external APIs
- **PII Protection**: Comply with GDPR/CCPA
- **Data Retention**: Auto-delete after 90 days
- **Backup**: Encrypted backups to S3/similar

## Performance Metrics

### Key Metrics to Monitor

1. **Call Metrics**:
   - Total calls per day
   - Average call duration
   - Call completion rate
   - Failed calls (%)

2. **AI Performance**:
   - Average response time
   - Transcription accuracy
   - Lead qualification rate
   - API error rate

3. **System Health**:
   - CPU usage
   - Memory usage
   - Network bandwidth
   - Disk I/O

4. **Business Metrics**:
   - Qualified leads per day
   - Conversion rate
   - Cost per lead
   - ROI

### Monitoring Tools

- **Asterisk**: Built-in CLI monitoring
- **Prometheus + Grafana**: System metrics
- **ELK Stack**: Log aggregation and analysis
- **Custom Dashboard**: Real-time call statistics

## Cost Estimation

### API Costs (per call, ~3 min avg)

- **Deepgram STT**: $0.0043/min × 3 = $0.013
- **OpenAI GPT-4**: $0.03/1K tokens × ~2K = $0.06
- **OpenAI TTS**: $0.015/1K chars × ~500 = $0.008

**Total per call**: ~$0.08

### Infrastructure Costs (monthly)

- **VPS (2GB RAM, 2 CPU)**: $10-20
- **Domain + SSL**: $10
- **Backup storage**: $5

**Total monthly (100 calls/day)**: ~$275

## Future Enhancements

1. **Multi-language Support**: Detect and respond in caller's language
2. **Sentiment Analysis**: Adjust tone based on caller emotion
3. **CRM Integration**: Auto-create leads in Salesforce/HubSpot
4. **Voice Biometrics**: Caller identification
5. **Call Analytics**: Detailed conversation insights
6. **A/B Testing**: Test different AI prompts
7. **Real-time Dashboard**: Live call monitoring
8. **SMS Follow-up**: Send summary after call
9. **Email Reports**: Daily/weekly statistics
10. **Mobile App**: Admin panel for lead review

---

*This architecture is designed for production use with scalability, security, and performance in mind.*
