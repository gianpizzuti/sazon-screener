/**
 * Voice for "Try the agent" (ADR 0011). The browser listens (Web Speech API, so the candidate's
 * audio never reaches our server); the server says what to speak: ElevenLabs audio when a key is
 * configured, otherwise speakable text for the browser's own voice.
 */

type RecognitionResult = { isFinal: boolean; 0: { transcript: string } };
type Recognition = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult: ((e: { resultIndex: number; results: ArrayLike<RecognitionResult> }) => void) | null;
  onend: (() => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
};

const RecognitionCtor = (window as unknown as { SpeechRecognition?: new () => Recognition; webkitSpeechRecognition?: new () => Recognition })
  .SpeechRecognition ?? (window as unknown as { webkitSpeechRecognition?: new () => Recognition }).webkitSpeechRecognition;

export const voiceSupported = () => !!RecognitionCtor && "speechSynthesis" in window;

/** The browser's language tag for Sofía's locale ("es" before the city is known: Spain's Spanish). */
export function speechLang(locale: string): string {
  return { "es-MX": "es-MX", en: "en-US" }[locale] ?? "es-ES";
}

/** Listen until the candidate stops talking. Resolves with what they said ("" if nothing). */
export function listen(locale: string, onInterim: (text: string) => void): { done: Promise<string>; stop: () => void } {
  const rec = new RecognitionCtor!();
  rec.lang = speechLang(locale);
  rec.interimResults = true;
  rec.continuous = false; // ends on a pause: one turn per utterance
  let finalText = "";
  const done = new Promise<string>((resolve, reject) => {
    rec.onresult = (e) => {
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) finalText += r[0].transcript;
        else interim += r[0].transcript;
      }
      onInterim((finalText + interim).trim());
    };
    rec.onerror = (e) => (e.error === "no-speech" || e.error === "aborted" ? resolve("") : reject(new Error(e.error)));
    rec.onend = () => resolve(finalText.trim());
  });
  rec.start();
  return { done, stop: () => rec.stop() };
}

let current: HTMLAudioElement | null = null;

/** Chrome loads its voices asynchronously: the first call can return none. */
function browserVoices(): Promise<SpeechSynthesisVoice[]> {
  const now = window.speechSynthesis.getVoices();
  if (now.length) return Promise.resolve(now);
  return new Promise((resolve) => {
    const done = () => resolve(window.speechSynthesis.getVoices());
    window.speechSynthesis.addEventListener("voiceschanged", done, { once: true });
    setTimeout(done, 1000);
  });
}

export function stopSpeaking() {
  current?.pause();
  current = null;
  window.speechSynthesis.cancel();
}

/** Say one of Sofía's messages. Resolves when it has been spoken; reports which voice spoke. */
export async function speak(conversationId: string, text: string): Promise<"elevenlabs" | "browser"> {
  const response = await fetch("/api/voice/speech", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id: conversationId, text }),
  });
  if (!response.ok) throw new Error(`speech failed: ${response.status}`);
  if (response.headers.get("content-type")?.startsWith("audio/")) {
    const url = URL.createObjectURL(await response.blob());
    const audio = new Audio(url);
    current = audio;
    await new Promise<void>((resolve) => {
      audio.onended = audio.onerror = audio.onpause = () => resolve();
      audio.play().catch(() => resolve());
    });
    URL.revokeObjectURL(url);
    return "elevenlabs";
  }
  const { speech, locale } = (await response.json()) as { speech: string; locale: string };
  const voices = await browserVoices();
  if (!voices.length) return "browser"; // no voice installed: the text is on screen, the conversation goes on
  await new Promise<void>((resolve) => {
    const utterance = new SpeechSynthesisUtterance(speech);
    const lang = speechLang(locale);
    utterance.lang = lang;
    utterance.voice = voices.find((v) => v.lang === lang) ?? voices.find((v) => v.lang.startsWith(lang.slice(0, 2))) ?? null;
    utterance.onend = utterance.onerror = () => resolve();
    // Chrome sometimes never fires `end` on long sentences: never let a lost event freeze the call
    setTimeout(resolve, 2000 + speech.length * 90);
    window.speechSynthesis.speak(utterance);
  });
  return "browser";
}
