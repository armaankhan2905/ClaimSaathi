import { useCallback, useEffect, useState } from "react";

type SpeechListener = (id: string | null) => void;

class TextToSpeech {
  private activeId: string | null = null;
  private listeners = new Set<SpeechListener>();

  speak(id: string, text: string, lang = "en") {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      console.warn("SpeechSynthesis is not supported in this environment");
      return;
    }

    this.stop();

    const utterance = new SpeechSynthesisUtterance(text);
    // Language mapping: 'en' -> 'en-IN', 'hi' -> 'hi-IN', 'hn' -> 'hi-IN'
    utterance.lang = lang === "hi" || lang === "hn" ? "hi-IN" : "en-IN";
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    this.activeId = id;
    this.notify();

    utterance.onend = () => {
      if (this.activeId === id) {
        this.activeId = null;
        this.notify();
      }
    };

    utterance.onerror = () => {
      if (this.activeId === id) {
        this.activeId = null;
        this.notify();
      }
    };

    window.speechSynthesis.speak(utterance);
  }

  stop() {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    this.activeId = null;
    this.notify();
  }

  getActiveId(): string | null {
    return this.activeId;
  }

  subscribe(listener: SpeechListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    for (const listener of this.listeners) {
      listener(this.activeId);
    }
  }
}

export const tts = new TextToSpeech();

export function useSpeech() {
  const [activeId, setActiveId] = useState<string | null>(tts.getActiveId());

  useEffect(() => {
    return tts.subscribe(setActiveId);
  }, []);

  const toggle = useCallback((id: string, text: string, lang?: string) => {
    if (tts.getActiveId() === id) {
      tts.stop();
    } else {
      tts.speak(id, text, lang);
    }
  }, []);

  return { activeId, toggle, stop: tts.stop.bind(tts) };
}
