# 【Day 24】擬真面試官：整合 TTS 語音朗讀與音波動畫反饋

有了語音輸入（STT）後，今天我們要讓 AI 面試官擁有「開口說話」的能力 — 整合 **Web Speech Synthesis API (TTS)** 語音合成，並搭配 **CSS 音波擺動動畫**，給予使用者明確的「AI 正在說話」視覺反饋。

---

## 1. 為什麼需要 TTS？

純文字打字機效果只有視覺反饋，搭配 TTS 後：

- 模擬真實面試「考官開口發問」的氛圍
- 不需盯著螢幕即可理解題目（解放視覺）
- 音波動畫提供即時「正在說話」的狀態感知

---

## 2. TextToSpeechEngine 模組

建立 `frontend/src/utils/textToSpeech.js`，封裝 `SpeechSynthesisUtterance`：

```javascript
export class TextToSpeechEngine {
  speak(text, { onStart, onEnd, onError, lang = 'zh-TW', rate = 0.95, pitch = 1.05 } = {}) {
    if (!('speechSynthesis' in window)) { if (onEnd) onEnd(); return; }

    window.speechSynthesis.cancel(); // 取消先前語音

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = rate;
    utterance.pitch = pitch;

    utterance.onstart = () => { this.isSpeaking = true; if (onStart) onStart(); };
    utterance.onend   = () => { this.isSpeaking = false; if (onEnd) onEnd(); };
    utterance.onerror = (e) => { this.isSpeaking = false; if (onError) onError(e.error); };

    window.speechSynthesis.speak(utterance);
  }

  stop() { window.speechSynthesis.cancel(); this.isSpeaking = false; }
}

export const ttsEngine = new TextToSpeechEngine();
```

---

## 3. 整合進 InterviewPage：打字機結束後自動朗讀

```javascript
import { ttsEngine } from '../utils/textToSpeech';

const [isSpeaking, setIsSpeaking] = useState(false);
const typewriterDoneRef = useRef(false);

useEffect(() => {
  if (!currentQ?.text) return;
  const fullText = currentQ.text;
  typewriterDoneRef.current = false;
  ttsEngine.stop();
  setIsSpeaking(false);

  let i = 0;
  const interval = setInterval(() => {
    i++;
    if (i <= fullText.length) {
      setDisplayedQuestion(fullText.slice(0, i));
    } else {
      clearInterval(interval);
      // ✅ 打字機結束 → 觸發 TTS 朗讀
      if (!typewriterDoneRef.current) {
        typewriterDoneRef.current = true;
        ttsEngine.speak(fullText, {
          onStart: () => setIsSpeaking(true),
          onEnd:   () => setIsSpeaking(false),
          onError: () => setIsSpeaking(false),
        });
      }
    }
  }, 20);

  return () => { clearInterval(interval); ttsEngine.stop(); setIsSpeaking(false); };
}, [currentIdx, currentQ?.text]);
```

---

## 4. WaveformBar 連接 isSpeaking 狀態

原本 WaveformBar 是固定動畫，現在改成根據 `isSpeaking` 狀態決定是否跳動：

```jsx
<WaveformBar isSpeaking={isSpeaking} />
<span class={`text-xs font-mono font-bold tracking-widest uppercase mt-2
  ${isSpeaking ? 'text-indigo-600' : 'text-slate-400'}`}>
  {isSpeaking ? 'Gemma-4-31B 面試官發話中' : '等待作答中'}
</span>
{isSpeaking && (
  <button onClick={() => { ttsEngine.stop(); setIsSpeaking(false); }}>
    停止語音朗讀
  </button>
)}
```

---

## 5. 實際效果展示

### 全流程實機動態操作展示（設定頁 → 立即跳轉 Loading → 面試艙與 TTS 發話）

![TTS Full Flow Live Demo](images/day24/demo.webp)

### AI 正在朗讀題目（音波跳動 + 發話標籤 + 停止按鈕）

![TTS Speaking Waveform](images/day24/02_interview_waveform_standby.png)

### 朗讀啟動後音波動畫與「面試官發話中」狀態

![TTS Active Speaking](images/day24/03_interview_waveform_speaking.png)

---

## 結語與明天預告

今天 UniMock AI 面試官不再只是「打字」，而是真正「開口說話」。音波動畫搭配 TTS 讓整個面試體驗更接近真實情境。

明天 **【Day 25】**，我們將整合 **Chart.js** 在前端動態渲染 STAR 多維度面試成績雷達圖！
