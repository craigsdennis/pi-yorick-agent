# random-moves

## User Request
"I've want to run yorick.move_randomly() in a loop  while the agent is talking. So I think if we use callback_user_transcript and callback_agent_response. I think we can figure that out. Can you help?"

## Work Summary
- Added an `AgentMotionController` background thread that repeatedly triggers `yorick.move_randomly()` on a timer while letting the audio pipeline keep running.
- Wired the motion controller into the ElevenLabs `Conversation` callbacks so movement begins whenever the agent speaks and pauses as soon as a user transcript arrives, with cleanup on session end and Ctrl+C.
