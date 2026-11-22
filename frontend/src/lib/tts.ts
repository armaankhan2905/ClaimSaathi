import { useCallback, useEffect, useState } from "react";

type SpeechListener = (id: string | null) => void;

/** Language of the text being read: "en" English, "hi" Hindi (Devanagari), "hn" Hinglish (Roman script). */
export type SpeechLang = "en" | "hi" | "hn";

export const speechSupported = typeof window !== "undefined" && "speechSynthesis" in window;

// Chrome's online voices stop after about 15 seconds of speech and then never fire "end", which
// left the button stuck on "Stop". Reading short pieces one after another avoids that.
const MAX_CHUNK = 180;

function chunks(text: string): string[] {
  const sentences = text.replace(/\s+/g, " ").trim().match(/[^.!?।;:\n]+[.!?।;:]*\s*/g) ?? [text];
  const out: string[] = [];
  let cur = "";
  for (const s of sentences) {
    if (s.length > MAX_CHUNK) {
      if (cur) out.push(cur), (cur = "");
      // a very long sentence: split it at the last space before the limit
      let rest = s;
      while (rest.length > MAX_CHUNK) {
        const cut = rest.lastIndexOf(" ", MAX_CHUNK) > 40 ? rest.lastIndexOf(" ", MAX_CHUNK) : MAX_CHUNK;
        out.push(rest.slice(0, cut));
        rest = rest.slice(cut);
      }
      cur = rest;
    } else if ((cur + s).length > MAX_CHUNK) {
      out.push(cur);
      cur = s;
    } else {
      cur += s;
    }
  }
  if (cur.trim()) out.push(cur);
  return out.map((c) => c.trim()).filter(Boolean);
}

function pickVoice(lang: SpeechLang): { voice: SpeechSynthesisVoice | null; bcp47: string } {
  // Hinglish is written in English letters, so an Indian English voice reads it far better than a
  // Hindi voice; Hindi in Devanagari needs a Hindi voice.
  const bcp47 = lang === "hi" ? "hi-IN" : "en-IN";
  const voices = window.speechSynthesis.getVoices();
  const exact = voices.find((v) => v.lang.replace("_", "-").toLowerCase() === bcp47.toLowerCase());
  const family = voices.find((v) => v.lang.toLowerCase().startsWith(bcp47.slice(0, 2)));
  return { voice: exact ?? family ?? null, bcp47 };
}

class TextToSpeech {
  private activeId: string | null = null;
  private listeners = new Set<SpeechListener>();
  private run = 0; // bumped on every speak/stop so events from an older reading are ignored

  /** Returns false when this device has no voice for the language (e.g. no Hindi voice installed). */
  speak(id: string, text: string, lang: SpeechLang = "en"): boolean {
    if (!speechSupported || !text.trim()) return true;
    this.stop();
    const run = ++this.run;
    const { voice, bcp47 } = pickVoice(lang);
    // Voices load asynchronously; only when the list is known and has no Hindi voice do we know
    // Devanagari text would come out silent or garbled.
    if (lang === "hi" && !voice && window.speechSynthesis.getVoices().length > 0) return false;
    const parts = chunks(text);

    this.activeId = id;
    this.notify();

    const finish = () => {
      if (this.run === run) {
        this.activeId = null;
        this.notify();
      }
    };
    parts.forEach((part, i) => {
      const u = new SpeechSynthesisUtterance(part);
      u.lang = bcp47;
      if (voice) u.voice = voice;
      u.rate = 0.95;
      if (i === parts.length - 1) u.onend = finish;
      u.onerror = (e) => {
        // "interrupted"/"canceled" come from our own stop(); anything else ends this reading
        if (e.error !== "interrupted" && e.error !== "canceled") {
          window.speechSynthesis.cancel();
          finish();
        }
      };
      window.speechSynthesis.speak(u);
    });
    window.speechSynthesis.resume(); // Chrome sometimes starts paused after a cancel()
    return true;
  }

  stop() {
    this.run++;
    if (speechSupported) window.speechSynthesis.cancel();
    if (this.activeId !== null) {
      this.activeId = null;
      this.notify();
    }
  }

  getActiveId(): string | null {
    return this.activeId;
  }

  subscribe(listener: SpeechListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    for (const listener of this.listeners) listener(this.activeId);
  }
}

export const tts = new TextToSpeech();

if (speechSupported) {
  window.speechSynthesis.getVoices(); // voices load asynchronously in Chrome; ask early
  window.addEventListener("pagehide", () => tts.stop());
}

export function useSpeech() {
  const [activeId, setActiveId] = useState<string | null>(tts.getActiveId());
  const [noVoice, setNoVoice] = useState(false); // set briefly when a Hindi voice was needed but missing

  useEffect(() => tts.subscribe(setActiveId), []);
  useEffect(() => {
    if (!noVoice) return;
    const timer = setTimeout(() => setNoVoice(false), 7000);
    return () => clearTimeout(timer);
  }, [noVoice]);

  const toggle = useCallback((id: string, text: string, lang: SpeechLang = "en") => {
    if (tts.getActiveId() === id) tts.stop();
    else setNoVoice(!tts.speak(id, text, lang));
  }, []);

  return { activeId, toggle, noVoice, stop: useCallback(() => tts.stop(), []), supported: speechSupported };
}

/** Stops reading aloud when the screen using it goes away (tab change, another page). */
export function useStopSpeechOnLeave() {
  useEffect(() => () => tts.stop(), []);
}
