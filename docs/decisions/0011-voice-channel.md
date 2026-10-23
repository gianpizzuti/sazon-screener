# ADR 0011: Voice as one more channel on the same engine

> The assessment's "Great" bonus: a browser-based voice agent that handles the same screening process.

**Status:** accepted

## Context
- Some candidates would rather talk than type, and the brief suggests ElevenLabs.
- The engine is already API-first (ADR 0008): channels only send a message and show the replies.
- A voice must not change who decides: the rules decide, Haiku reads, Sonnet writes (ADR 0001).

## Decision
1. **Same API, a `voice` channel.** "Try the agent" has a Chat / Voice switch. A voice conversation is an ordinary conversation with `channel: "voice"`: same policy, same data, same recruiter view.
2. **The browser listens.** The Web Speech API transcribes the candidate in their browser, and the transcript is sent as a normal message, so the candidate's audio never reaches our server. The conversation is hands-free: Sofía speaks, then listens again if she asked something. The microphone button stops or restarts listening, and typing or tapping still works.
3. **The writer knows it is spoken.** The turn instructions say "voice": no emojis or symbols, options said in words, dates and times as people say them, at most two short sentences. The message limit is 20% shorter, because listening is slower than reading.
4. **Speakable text is built by code.** `channels/voice.py` turns the display text into speech:
   - "21/10 a las 16:00" becomes "21 de octubre a las cuatro de la tarde";
   - "1)" becomes "opción 1";
   - bullets become sentences, "repartidor/a" becomes "repartidor o repartidora", and emojis are dropped.

   Templates (greeting, recap, interview times) are spoken too, without writing a second version of each.
5. **ElevenLabs gives Sofía her voice.**
   - Voices come from its library, chosen per locale for a native accent: Carolina for Spain, Ana María for Mexico, Sarah for English. They are configuration (`client.yaml: voice`).
   - The model is `eleven_flash_v2_5`: low latency, multilingual, and half the credits per character.
   - Only Sofía's text is sent to ElevenLabs.
6. **Never silent.** Without `ELEVENLABS_API_KEY`, or when ElevenLabs fails, the server returns the speakable text and the browser's own voice reads it. A lost "end of speech" event can't freeze the call either, because there is a time limit based on the length of the text.
7. **Spoken numbers pick an interview time.** In a short reply, "la uno" or "la dos" chooses that option, as the digits "1" and "2" already did.

## Alternatives considered
| Option | Why not |
|---|---|
| ElevenLabs Agents (their full conversational platform) | Better turn-taking and barge-in, but their agent's model would drive the conversation. Keeping "code decides" would mean wrapping our engine as their custom LLM, behind a public URL and a tunnel: about 5–6 hours and a new failure point, for a demo due in two days. The right next step for a production voice channel |
| The browser's voice only | Free, but robotic, and it varies by machine. The voice is the first thing a candidate (and a reviewer) hears |
| Speech-to-text on our server (ElevenLabs Scribe, Whisper) | It would avoid Chrome's speech service. But the candidate's audio would then reach our server and one more vendor, and every turn would gain an upload. For a demo the browser is enough. In production a speech-to-text provider under a data-processing agreement, in the EU, is the cleaner choice |
| A second set of voice templates | Twice the copy to maintain; code turns the same text into speech |

## Trade-offs accepted
- **Chrome's speech recognition sends the audio to Google**, so it works in Chrome and Edge only. Fine for a demo; not for production (see above).
- **Latency.** Each turn needs understanding, writing and speech: about 3–4 s. Text chat hides this; a call does not.
- **Cost.** About 1,500 credits per screening, roughly $0.25–0.30 on the Starter plan, against $0.04 of language models. Voice costs about 7× the brain, so at 10,000 applications a week it should be offered to those who prefer it, not to everyone.

## Revisit when
- **Voice goes to production** (a phone line or WhatsApp voice notes). Then:
  - use a streaming speech-to-text and text-to-speech provider under a data-processing agreement;
  - add barge-in;
  - possibly merge understanding and writing into one model call for voice only, to cut latency.
- **Usage data shows who picks voice**, and whether they complete more often than in chat.
