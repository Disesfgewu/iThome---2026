# 【Day 23】開口說話：前端整合 Web Speech API 語音輸入（STT）

真實面試是靠「口說」進行的。今天我們要整合瀏覽器原生 **Web Speech API (SpeechRecognition)**，實現即時語音轉文字（STT）輸入。

---

## 1. Web Speech STT 模組實作 (`frontend/speech_to_text.js`)

```javascript
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
  alert("您的瀏覽器不支援 Web Speech API，請使用 Chrome 瀏覽器。");
} else {
  const recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'zh-TW';

  const transcriptBox = document.getElementById('candidate-answer-box');
  const micBtn = document.getElementById('btn-mic');

  let isListening = false;

  micBtn.addEventListener('click', () => {
    if (!isListening) {
      recognition.start();
      micBtn.classList.add('bg-red-500', 'animate-pulse');
      isListening = true;
    } else {
      recognition.stop();
      micBtn.classList.remove('bg-red-500', 'animate-pulse');
      isListening = false;
    }
  });

  recognition.onresult = (event) => {
    let currentText = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      currentText += event.results[i][0].transcript;
    }
    transcriptBox.value = currentText;
  };
}
```

---

## 結語與明天預告

今天我們為 UniMock AI 賦予了即時口語聽覺（STT）能力。

明天 **【Day 24】**，我們將整合 TTS 語音合成朗讀，讓 AI 面試官用擬真語音發問並連動音波動畫！
