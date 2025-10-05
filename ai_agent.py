"""
AI Call Center Agent - Investment Advisor
Uses Asterisk ARI, Deepgram for STT, OpenAI for AI responses

This is a professional AI call center agent designed to qualify investment leads.
"""

import asyncio
import os
import json
import logging
import signal
import sys
from datetime import datetime
from typing import Optional, Dict, Any

import aiohttp
from dotenv import load_dotenv
import websockets
from deepgram import Deepgram

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AICallCenterAgent:
    """Main AI Call Center Agent using Asterisk ARI"""
    
    def __init__(self):
        # Asterisk ARI Configuration
        self.ari_url = os.getenv('ARI_URL', 'http://localhost:8088')
        self.ari_username = os.getenv('ARI_USERNAME', 'ai_agent')
        self.ari_password = os.getenv('ARI_PASSWORD', 'ai_agent_secure_password_123')
        self.ari_app = os.getenv('ARI_APP', 'ai-call-center')
        
        # API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
        
        # Validate configuration
        if not self.openai_api_key:
            logger.error("OPENAI_API_KEY not set in environment")
            raise ValueError("OPENAI_API_KEY required")
        
        if not self.deepgram_api_key:
            logger.error("DEEPGRAM_API_KEY not set in environment")
            raise ValueError("DEEPGRAM_API_KEY required")
        
        # Initialize services
        self.deepgram = Deepgram(self.deepgram_api_key)
        self.session: Optional[aiohttp.ClientSession] = None
        self.openai_session: Optional[aiohttp.ClientSession] = None
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.running = True
        
        logger.info("AI Call Center Agent initialized")
    
    async def start(self):
        """Start the AI agent"""
        logger.info("Starting AI Call Center Agent...")
        
        # Create HTTP session for ARI requests (with BasicAuth)
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(self.ari_username, self.ari_password)
        )
        
        # Create separate HTTP session for OpenAI API requests (no auth in session)
        self.openai_session = aiohttp.ClientSession()
        
        # Connect to ARI WebSocket
        ws_url = f"ws://localhost:8088/ari/events?app={self.ari_app}&api_key={self.ari_username}:{self.ari_password}"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                logger.info(f"Connected to ARI WebSocket: {self.ari_app}")
                
                # Listen for events
                while self.running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        event = json.loads(message)
                        await self.handle_event(event)
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("WebSocket connection closed")
                        break
                    
        except Exception as e:
            logger.error(f"Error in ARI connection: {e}")
        finally:
            await self.cleanup()
    
    async def handle_event(self, event: Dict[str, Any]):
        """Handle ARI events"""
        event_type = event.get('type')
        logger.info(f"Received event: {event_type}")
        
        if event_type == 'StasisStart':
            await self.handle_stasis_start(event)
        elif event_type == 'StasisEnd':
            await self.handle_stasis_end(event)
        elif event_type == 'ChannelDtmfReceived':
            await self.handle_dtmf(event)
        else:
            logger.debug(f"Unhandled event type: {event_type}")
    
    async def handle_stasis_start(self, event: Dict[str, Any]):
        """Handle incoming call"""
        channel = event.get('channel', {})
        channel_id = channel.get('id')
        caller_number = channel.get('caller', {}).get('number', 'Unknown')
        
        logger.info(f"Incoming call from {caller_number} on channel {channel_id}")
        
        # Store call information
        self.active_calls[channel_id] = {
            'caller_number': caller_number,
            'start_time': datetime.now(),
            'conversation_history': [],
            'lead_data': {
                'caller_number': caller_number,
                'call_time': datetime.now().isoformat(),
                'investment_interest': None,
                'investment_amount': None,
                'risk_tolerance': None,
                'timeline': None,
                'qualified': False
            }
        }
        
        # Answer the call
        await self.ari_request('POST', f'/channels/{channel_id}/answer')
        
        # Start the conversation
        await self.start_conversation(channel_id)
    
    async def handle_stasis_end(self, event: Dict[str, Any]):
        """Handle call end"""
        channel = event.get('channel', {})
        channel_id = channel.get('id')
        
        logger.info(f"Call ended on channel {channel_id}")
        
        if channel_id in self.active_calls:
            call_data = self.active_calls[channel_id]
            
            # Save lead data
            await self.save_lead_data(call_data['lead_data'])
            
            # Log conversation
            duration = (datetime.now() - call_data['start_time']).total_seconds()
            logger.info(f"Call duration: {duration:.2f} seconds")
            
            # Cleanup
            del self.active_calls[channel_id]
    
    async def handle_dtmf(self, event: Dict[str, Any]):
        """Handle DTMF input"""
        channel_id = event.get('channel', {}).get('id')
        digit = event.get('digit')
        
        logger.info(f"DTMF received on {channel_id}: {digit}")
        
        # Handle menu options if needed
        if channel_id in self.active_calls:
            # You can implement DTMF-based menu navigation here
            pass
    
    async def start_conversation(self, channel_id: str):
        """Start the AI conversation"""
        logger.info(f"Starting conversation on channel {channel_id}")
        
        # Welcome message
        greeting = (
            "Hello! Thank you for calling our investment advisory service. "
            "My name is Alex, and I'm here to help you explore investment opportunities. "
            "I have a few quick questions to understand your investment goals better. "
            "First, what type of investments are you interested in? "
            "For example, stocks, bonds, real estate, or cryptocurrency?"
        )
        
        # Play greeting using text-to-speech
        await self.speak(channel_id, greeting)
        
        # Start listening for response
        await self.listen_and_respond(channel_id)
    
    async def speak(self, channel_id: str, text: str):
        """Convert text to speech and play to caller"""
        logger.info(f"Speaking to {channel_id}: {text[:50]}...")
        
        try:
            # Generate speech using OpenAI TTS
            response = await self.generate_speech_openai(text)
            
            if response:
                # Save audio temporarily
                audio_file = f"/tmp/ai_agent_{channel_id}_{datetime.now().timestamp()}.wav"
                with open(audio_file, 'wb') as f:
                    f.write(response)
                
                # Play audio through Asterisk
                await self.play_audio(channel_id, audio_file)
                
                # Clean up
                try:
                    os.remove(audio_file)
                except:
                    pass
        except Exception as e:
            logger.error(f"Error in speak: {e}")
    
    async def generate_speech_openai(self, text: str) -> Optional[bytes]:
        """Generate speech using OpenAI TTS API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'tts-1',
                'input': text,
                'voice': 'alloy',
                'response_format': 'wav'
            }
            
            async with self.openai_session.post(
                'https://api.openai.com/v1/audio/speech',
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logger.error(f"OpenAI TTS error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    async def play_audio(self, channel_id: str, audio_file: str):
        """Play audio file to channel"""
        try:
            # Create playback
            playback_id = f"playback_{datetime.now().timestamp()}"
            await self.ari_request(
                'POST',
                f'/channels/{channel_id}/play',
                params={'media': f'sound:{audio_file}'}
            )
            logger.info(f"Playing audio on channel {channel_id}")
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    async def listen_and_respond(self, channel_id: str):
        """Listen to caller and generate AI response"""
        logger.info(f"Listening on channel {channel_id}")
        
        try:
            # Start recording
            recording_name = f"recording_{channel_id}_{datetime.now().timestamp()}"
            await self.ari_request(
                'POST',
                f'/channels/{channel_id}/record',
                params={
                    'name': recording_name,
                    'format': 'wav',
                    'maxDurationSeconds': 30,
                    'maxSilenceSeconds': 3,
                    'ifExists': 'overwrite',
                    'beep': 'false',
                    'terminateOn': '#'
                }
            )
            
            # Wait for recording to complete (simulate - in production use event-based)
            await asyncio.sleep(5)
            
            # Transcribe using Deepgram
            transcript = await self.transcribe_audio(recording_name)
            
            if transcript and channel_id in self.active_calls:
                logger.info(f"Caller said: {transcript}")
                
                # Add to conversation history
                self.active_calls[channel_id]['conversation_history'].append({
                    'role': 'user',
                    'content': transcript
                })
                
                # Generate AI response
                ai_response = await self.generate_ai_response(channel_id, transcript)
                
                if ai_response:
                    # Add to conversation history
                    self.active_calls[channel_id]['conversation_history'].append({
                        'role': 'assistant',
                        'content': ai_response
                    })
                    
                    # Speak response
                    await self.speak(channel_id, ai_response)
                    
                    # Continue conversation or end call
                    if self.should_continue_conversation(channel_id):
                        await self.listen_and_respond(channel_id)
                    else:
                        await self.end_call(channel_id)
        except Exception as e:
            logger.error(f"Error in listen_and_respond: {e}")
    
    async def transcribe_audio(self, recording_name: str) -> Optional[str]:
        """Transcribe audio using Deepgram"""
        try:
            # In production, you would get the actual recording file
            # For now, return a placeholder
            logger.info(f"Transcribing recording: {recording_name}")
            
            # Deepgram transcription would happen here
            # audio_file = f'/var/spool/asterisk/recording/{recording_name}.wav'
            # with open(audio_file, 'rb') as audio:
            #     source = {'buffer': audio, 'mimetype': 'audio/wav'}
            #     response = await self.deepgram.transcription.prerecorded(source)
            #     transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
            
            return "Sample transcribed text"  # Placeholder
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def generate_ai_response(self, channel_id: str, user_input: str) -> Optional[str]:
        """Generate AI response using OpenAI"""
        try:
            call_data = self.active_calls[channel_id]
            conversation_history = call_data['conversation_history']
            
            # System prompt for investment advisor
            system_prompt = """You are Alex, a professional investment advisor AI assistant. 
            Your goal is to qualify leads by understanding their investment interests and financial goals.
            
            Ask targeted questions to determine:
            1. Type of investments they're interested in
            2. Investment amount they're considering
            3. Risk tolerance (conservative, moderate, aggressive)
            4. Investment timeline
            5. Current financial situation
            
            Be friendly, professional, and conversational. Keep responses concise (2-3 sentences).
            After gathering information, qualify the lead and offer to connect them with a human advisor.
            """
            
            # Build messages for OpenAI
            messages = [
                {'role': 'system', 'content': system_prompt}
            ]
            messages.extend(conversation_history)
            
            # Call OpenAI API
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-4-turbo-preview',
                'messages': messages,
                'max_tokens': 150,
                'temperature': 0.7
            }
            
            async with self.openai_session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ai_response = data['choices'][0]['message']['content']
                    
                    # Extract lead qualification data
                    await self.extract_lead_data(channel_id, user_input, ai_response)
                    
                    return ai_response
                else:
                    logger.error(f"OpenAI API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None
    
    async def extract_lead_data(self, channel_id: str, user_input: str, ai_response: str):
        """Extract and update lead qualification data"""
        if channel_id not in self.active_calls:
            return
        
        lead_data = self.active_calls[channel_id]['lead_data']
        user_lower = user_input.lower()
        
        # Simple keyword extraction (in production, use NLP)
        if any(word in user_lower for word in ['stock', 'equity', 'shares']):
            lead_data['investment_interest'] = 'stocks'
        elif any(word in user_lower for word in ['bond', 'fixed income']):
            lead_data['investment_interest'] = 'bonds'
        elif any(word in user_lower for word in ['real estate', 'property', 'reits']):
            lead_data['investment_interest'] = 'real_estate'
        elif any(word in user_lower for word in ['crypto', 'bitcoin', 'ethereum']):
            lead_data['investment_interest'] = 'cryptocurrency'
        
        # Extract investment amount mentions
        import re
        amounts = re.findall(r'\$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|million)?', user_lower)
        if amounts:
            lead_data['investment_amount'] = amounts[0]
        
        # Risk tolerance
        if any(word in user_lower for word in ['conservative', 'safe', 'low risk']):
            lead_data['risk_tolerance'] = 'conservative'
        elif any(word in user_lower for word in ['aggressive', 'high risk', 'growth']):
            lead_data['risk_tolerance'] = 'aggressive'
        elif any(word in user_lower for word in ['moderate', 'balanced']):
            lead_data['risk_tolerance'] = 'moderate'
        
        # Qualify lead
        if (lead_data['investment_interest'] and 
            lead_data['investment_amount'] and 
            lead_data['risk_tolerance']):
            lead_data['qualified'] = True
    
    def should_continue_conversation(self, channel_id: str) -> bool:
        """Determine if conversation should continue"""
        if channel_id not in self.active_calls:
            return False
        
        call_data = self.active_calls[channel_id]
        conversation_length = len(call_data['conversation_history'])
        lead_qualified = call_data['lead_data']['qualified']
        
        # Continue if not qualified and conversation is less than 10 exchanges
        return not lead_qualified and conversation_length < 20
    
    async def end_call(self, channel_id: str):
        """End the call gracefully"""
        logger.info(f"Ending call on channel {channel_id}")
        
        if channel_id in self.active_calls:
            lead_data = self.active_calls[channel_id]['lead_data']
            
            # Closing message
            if lead_data['qualified']:
                closing = (
                    "Thank you so much for sharing that information! "
                    "You sound like a great fit for our services. "
                    "I'll have one of our senior advisors give you a call within 24 hours "
                    "to discuss your investment options in detail. "
                    "Have a wonderful day!"
                )
            else:
                closing = (
                    "Thank you for your time today. "
                    "If you'd like to learn more about our investment services, "
                    "feel free to call us back anytime. Have a great day!"
                )
            
            await self.speak(channel_id, closing)
            await asyncio.sleep(2)
        
        # Hang up
        await self.ari_request('DELETE', f'/channels/{channel_id}')
    
    async def save_lead_data(self, lead_data: Dict[str, Any]):
        """Save lead data to file/database"""
        try:
            # Save to JSON file (in production, save to database)
            leads_file = 'leads_data.json'
            leads = []
            
            if os.path.exists(leads_file):
                with open(leads_file, 'r') as f:
                    leads = json.load(f)
            
            leads.append(lead_data)
            
            with open(leads_file, 'w') as f:
                json.dump(leads, f, indent=2)
            
            logger.info(f"Lead data saved: {lead_data['caller_number']} - Qualified: {lead_data['qualified']}")
        except Exception as e:
            logger.error(f"Error saving lead data: {e}")
    
    async def ari_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None):
        """Make ARI HTTP request"""
        url = f"{self.ari_url}/ari{endpoint}"
        
        try:
            async with self.session.request(
                method,
                url,
                params=params,
                json=data
            ) as response:
                if response.status in [200, 204]:
                    return await response.json() if response.status == 200 else None
                else:
                    logger.error(f"ARI request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error in ARI request: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up...")
        
        # Hangup active calls
        for channel_id in list(self.active_calls.keys()):
            try:
                await self.ari_request('DELETE', f'/channels/{channel_id}')
            except:
                pass
        
        # Close sessions
        if self.session:
            await self.session.close()
        if self.openai_session:
            await self.openai_session.close()
        
        logger.info("Cleanup complete")
    
    def stop(self):
        """Stop the agent"""
        logger.info("Stopping AI Call Center Agent...")
        self.running = False


async def main():
    """Main entry point"""
    agent = AICallCenterAgent()
    
    # Setup signal handlers
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        logger.info("Received shutdown signal")
        agent.stop()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await agent.cleanup()


if __name__ == '__main__':
    print("=" * 60)
    print("AI Call Center Agent - Investment Advisor")
    print("=" * 60)
    print()
    
    asyncio.run(main())
