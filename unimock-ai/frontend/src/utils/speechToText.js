/**
 * Web Speech API (Speech-to-Text / STT) Utility for UniMock AI
 * Real-time Traditional Chinese Speech Recognition (zh-TW)
 */

export class SpeechToTextEngine {
  constructor(onResult, onError, onEnd) {
    this.onResult = onResult;
    this.onError = onError;
    this.onEnd = onEnd;
    this.recognition = null;
    this.isListening = false;
    this.initEngine();
  }

  initEngine() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'zh-TW';

      this.recognition.onresult = (event) => {
        let transcript = '';
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        if (this.onResult) {
          this.onResult(transcript);
        }
      };

      this.recognition.onerror = (event) => {
        console.warn('Web Speech STT Error:', event.error);
        this.isListening = false;
        if (this.onError) {
          this.onError(event.error);
        }
      };

      this.recognition.onend = () => {
        this.isListening = false;
        if (this.onEnd) {
          this.onEnd();
        }
      };
    } else {
      console.warn('Web Speech API is not supported in this browser environment.');
    }
  }

  isSupported() {
    return !!this.recognition;
  }

  start() {
    if (this.recognition && !this.isListening) {
      try {
        this.recognition.start();
        this.isListening = true;
        return true;
      } catch (err) {
        console.warn('Failed to start speech recognition:', err);
        return false;
      }
    }
    return false;
  }

  stop() {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
        this.isListening = false;
        return true;
      } catch (err) {
        console.warn('Failed to stop speech recognition:', err);
        return false;
      }
    }
    return false;
  }
}
