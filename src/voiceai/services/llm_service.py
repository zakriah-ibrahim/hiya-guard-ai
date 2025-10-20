import json
import asyncio
from openai import AsyncOpenAI
from voiceai import config

class ConversationEngine:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.conversation_history = []
        self.user_name = config.USER_NAME
        self.system_prompt = self._build_system_prompt()
        self.current_intent = "unclear"
        self.confidence = 0.0
        
    def _build_system_prompt(self):
        return f"""You are Hiya Guard, an assistant answering calls for {self.user_name}.

YOUR ROLE:
- Be professional, polite, and concise
- Determine if the caller is legitimate or spam/scam
- For legitimate calls: understand their purpose and offer to schedule a callback
- For spam/scam: politely decline and end the call

SPAM/SCAM INDICATORS:
- Unsolicited sales offers (car warranties, insurance, timeshares, solar panels)
- Prize/lottery/sweepstakes notifications
- Urgent account verification or security threats
- Requests for sensitive information (SSN, credit card, banking details)
- Robocall scripts or overly scripted language
- Vague statements about "your account" without specifics

LEGITIMATE INDICATORS:
- Specific purpose mentioned (partnership, project, scheduled meeting)
- Professional tone and clear communication
- Named companies or references to real interactions
- Reasonable requests for callbacks or meetings

CONVERSATION GUIDELINES:
1. Start: "Hello, you've reached {self.user_name}'s assistant. How can I help you?"
2. If unclear: "Could you tell me what this is regarding?"
3. If spam detected: "I appreciate you calling, but we're not interested. Have a great day." [END]
4. If legitimate: "Let me check {self.user_name}'s calendar... I'll find available times."
5. When user confirms a time: "Perfect! I've scheduled that. Thank you for calling!" [END]

RESPONSE STYLE:
- Keep responses under 25 words when possible
- Speak naturally (use contractions, casual phrasing)
- Don't repeat the same information multiple times
- Don't over-explain or apologize excessively
- If caller becomes hostile, remain calm: "I understand. I'll pass your message along."

OUTPUT FORMAT (JSON):
{{
  "response": "Your spoken response here",
  "intent": "spam" | "legitimate" | "unclear",
  "action": "continue" | "schedule" | "decline" | "confirm" | "end_call",
  "confidence": 0.0-1.0
}}

IMPORTANT: 
- Use "confirm" action when user confirms a time slot
- Use "end_call" action after confirmation to end the conversation
- Don't repeat calendar information if already provided"""
    
    def initialize_conversation(self):
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    async def process_transcript(self, transcript):
        self.conversation_history.append({
            "role": "user",
            "content": transcript
        })
        
        try:
            response = await self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=self.conversation_history,
                temperature=config.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            assistant_message = response.choices[0].message.content
            
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            parsed = self._parse_response(assistant_message)
            return parsed
            
        except Exception as e:
            return {
                "response": "I apologize, could you repeat that?",
                "intent": self.current_intent,
                "action": "continue",
                "confidence": 0.5
            }
    
    def _parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            
            self.current_intent = data.get("intent", "unclear")
            self.confidence = float(data.get("confidence", 0.5))
            
            return {
                "response": data.get("response", ""),
                "intent": self.current_intent,
                "action": data.get("action", "continue"),
                "confidence": self.confidence
            }
        except json.JSONDecodeError:
            return {
                "response": response_text,
                "intent": self.current_intent,
                "action": "continue",
                "confidence": 0.5
            }
    
    def update_conversation_state(self, intent, confidence):
        self.current_intent = intent
        self.confidence = confidence
    
    async def generate_summary(self, full_transcript):
        try:
            summary_prompt = f"""Based on this call transcript, generate a structured summary.

Transcript:
{full_transcript}

Provide a JSON summary with these fields:
- caller_intent: Brief description of why they called
- classification: "spam" or "legitimate"
- outcome: What happened (declined, scheduled, unclear)
- scheduled_callback: DateTime if scheduled, null otherwise
- key_details: Important info mentioned
- confidence_score: 0.0-1.0"""
            
            response = await self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a call summarization assistant."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            summary = json.loads(response.choices[0].message.content)
            return summary
            
        except Exception as e:
            return {
                "caller_intent": "Unknown",
                "classification": "unclear",
                "outcome": "error generating summary",
                "scheduled_callback": None,
                "key_details": "",
                "confidence_score": 0.0
            }

