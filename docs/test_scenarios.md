# Hiya Guard - Test Scenarios

Use these scenarios to test the AI agent's capabilities.

## Test 1: Legitimate Business Call

**Scenario:** Professional partnership inquiry

**Script:**
```
You: "Hi, this is Sarah Johnson from TechCorp. I'm calling about the 
     partnership proposal we discussed via email last week. I wanted to 
     schedule a time to go over the details with [User Name]."

Expected Agent Response:
- Acknowledges the call professionally
- Asks clarifying questions if needed
- Checks calendar availability
- Offers specific time slots
- Confirms the callback appointment

Expected Outcome:
- Classification: Legitimate
- Action: Schedule callback
- Calendar event created
```

## Test 2: Car Warranty Spam

**Scenario:** Classic spam call

**Script:**
```
You: "Hello! We're calling about your car's extended warranty. This is 
     your final notice. Your warranty is about to expire and we need to 
     update your information immediately. Press 1 to speak with a 
     representative."

Expected Agent Response:
- Recognizes spam indicators (extended warranty, urgency, "final notice")
- Politely declines
- "I appreciate you calling, but we're not interested. Have a great day."
- Ends call

Expected Outcome:
- Classification: Spam
- Action: Decline
- No calendar event
```

## Test 3: Prize/Sweepstakes Scam

**Scenario:** Fake prize notification

**Script:**
```
You: "Congratulations! You've been selected as a winner in our customer 
     appreciation sweepstakes! You've won a free cruise to the Bahamas! 
     We just need to verify some information to claim your prize. Can 
     you confirm your social security number?"

Expected Agent Response:
- Detects scam indicators (prize, free cruise, requesting sensitive info)
- Politely declines
- Ends call quickly

Expected Outcome:
- Classification: Spam/Scam
- Action: Decline
- High confidence score
```

## Test 4: Ambiguous Account Call

**Scenario:** Vague reference that needs clarification

**Script:**
```
You: "Hello, I'm calling about your account. There's an issue that 
     needs attention."

Expected Agent Response:
- Asks clarifying questions
- "Could you tell me what this is regarding?"
- "Which account are you referring to?"
- May detect as spam if caller remains vague

Expected Outcome:
- Initial: Classification unclear
- After clarification: Either legitimate or spam
- Action depends on caller's follow-up responses
```

## Test 5: Legitimate Follow-up Call

**Scenario:** Returning a previous inquiry

**Script:**
```
You: "Hi, this is Michael Chen. I submitted a project proposal through 
     your website two days ago about the AI integration project. I wanted 
     to follow up and see if [User Name] had a chance to review it."

Expected Agent Response:
- Acknowledges legitimate nature
- Asks for details about the proposal
- Offers to schedule a callback
- Gets contact information

Expected Outcome:
- Classification: Legitimate
- Action: Schedule callback
- Calendar event with "Project proposal follow-up" details
```

## Test 6: Insurance Sales Call

**Scenario:** Unsolicited insurance offer

**Script:**
```
You: "Good afternoon! I'm calling from Premier Insurance Group. We're 
     offering special rates on life insurance policies in your area. 
     This is a limited-time offer and I'd love to discuss how we can 
     save you money on coverage."

Expected Agent Response:
- Identifies unsolicited sales pitch
- Politely declines
- Ends call

Expected Outcome:
- Classification: Spam
- Action: Decline
```

## Test 7: Recruiter Call

**Scenario:** Job opportunity inquiry

**Script:**
```
You: "Hello, my name is Jessica Williams, I'm a recruiter with Tech 
     Talents Agency. I came across [User Name]'s profile and wanted to 
     discuss an exciting opportunity that matches their experience. 
     Would they be available for a brief conversation this week?"

Expected Agent Response:
- Recognizes professional/legitimate nature
- Asks for details about the opportunity
- Checks calendar
- Schedules callback time

Expected Outcome:
- Classification: Legitimate
- Action: Schedule callback
- Calendar event created
```

## Test 8: Hostile Caller

**Scenario:** Caller becomes aggressive

**Script:**
```
You: "I need to speak with [User Name] RIGHT NOW! This is urgent and 
     I'm tired of dealing with assistants. Put them on the phone 
     immediately or I'll—"

Expected Agent Response:
- Remains calm and professional
- "I understand. I'll pass your message along."
- May ask for callback number
- Ends call if caller continues hostility

Expected Outcome:
- Classification: Unclear or legitimate (with notes about tone)
- Action: End call or offer callback
- Summary notes hostile behavior
```

## Evaluation Criteria

For each test, evaluate:

1. **Response Time:** <2.5 seconds per exchange
2. **Accuracy:** Correct classification (spam vs. legitimate)
3. **Naturalness:** Conversation flows smoothly
4. **Action Taken:** Appropriate outcome (schedule, decline, clarify)
5. **Summary Quality:** Accurate and actionable summary
6. **Calendar Integration:** Event created when appropriate

## Expected Success Rate

- Spam Detection: 90%+ accuracy
- Legitimate Calls: 95%+ correct handling
- Ambiguous Calls: Asks appropriate clarifying questions
- Overall: Natural, professional interactions

