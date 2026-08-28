/**
 * Web Speech Synthesis (TTS) Utility for UniMock AI
 * Speaks interview questions in Traditional Chinese (zh-TW) via SpeechSynthesisUtterance.
 */

export class TextToSpeechEngine {
  constructor() {
    this.utterance = null;
    this.isSpeaking = false;
    this.currentText = '';
  }

  isSupported() {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }

  speak(text, { onStart, onEnd, onError, lang = 'zh-TW', rate = 0.95, pitch = 1.05 } = {}) {
    if (!this.isSupported() || !text) {
      if (onEnd) onEnd();
      return;
    }

    // Deduplication guard: if already speaking the exact same text, ignore
    if (this.isSpeaking && this.currentText === text) {
      return;
    }

    // Stop any active speech before starting new utterance
    this.stop();

    this.currentText = text;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = rate;
    utterance.pitch = pitch;

    utterance.onstart = () => {
      this.isSpeaking = true;
      if (onStart) onStart();
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.currentText = '';
      if (onEnd) onEnd();
    };

    utterance.onerror = (event) => {
      this.isSpeaking = false;
      this.currentText = '';
      console.warn('TTS Error:', event.error);
      if (onError) onError(event.error);
    };

    this.utterance = utterance;
    // Brief setTimeout to ensure window.speechSynthesis.cancel() finishes clearing queue in Chrome
    setTimeout(() => {
      window.speechSynthesis.speak(utterance);
    }, 50);
  }

  stop() {
    if (this.isSupported()) {
      window.speechSynthesis.cancel();
      this.isSpeaking = false;
      this.currentText = '';
    }
  }
}

export const ttsEngine = new TextToSpeechEngine();
