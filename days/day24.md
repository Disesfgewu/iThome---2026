# 【Day 24】擬真面試官：整合 TTS 語音朗讀與音波動畫反饋

有了語音輸入後，今天我們要整合 **Text-to-Speech (TTS)** 語音合成，讓 AI 面試官具備開口發問的能力，並搭配 CSS 音波擺動視覺動畫！

---

## 1. Web Speech Synthesis (TTS) 模組 (`frontend/text_to_speech.js`)

```javascript
function speakQuestion(text, onEndCallback) {
  if (!('speechSynthesis' in window)) return;

  window.speechSynthesis.cancel(); // 停止先前的聲音

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'zh-TW';
  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  const waveform = document.getElementById('audio-waveform');

  utterance.onstart = () => {
    waveform.classList.remove('hidden');
  };

  utterance.onend = () => {
    waveform.classList.add('hidden');
    if (onEndCallback) onEndCallback();
  };

  window.speechSynthesis.speak(utterance);
}
```

---

## 2. CSS 動態音波效果 (`frontend/style.css`)

```css
.wave-bar {
  width: 4px;
  background-color: #22d3ee;
  border-radius: 2px;
  animation: wave 1.2s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% { height: 8px; }
  50% { height: 32px; }
}
```

---

## 結語與明天預告

今天我們讓 AI 面試官擁有了說話與聲音視覺反饋能力。

明天 **【Day 25】**，我們將整合 Chart.js 在前端動態渲染 STAR 多維度面試成績單雷達圖！
