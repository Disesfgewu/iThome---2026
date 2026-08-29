import React, { useState, useEffect, useRef } from 'react';
import WaveformBar from '../components/WaveformBar';
import { respondInterviewApi, respondInterviewStreamApi, getReportApi } from '../api/realApi';
import { checkSchoolTier } from '../api/mockApi';
import { SpeechToTextEngine } from '../utils/speechToText';
import { ttsEngine } from '../utils/textToSpeech';

export default function InterviewPage({ sessionData, setSessionData, onFinishInterview }) {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [candidateAnswer, setCandidateAnswer] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showHintModal, setShowHintModal] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(105);
  const [displayedQuestion, setDisplayedQuestion] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const sttEngineRef = useRef(null);
  const typewriterDoneRef = useRef(false);
  const spokenQuestionIndexRef = useRef(-1);

  const currentQ = sessionData.questions?.[currentIdx] || null;
  const tierInfo = checkSchoolTier(sessionData.targetSchool);

  // Initialize SpeechToTextEngine
  useEffect(() => {
    sttEngineRef.current = new SpeechToTextEngine(
      (text) => { if (text.trim()) setCandidateAnswer(text); },
      (err)  => { console.warn('STT Error:', err); setIsRecording(false); },
      ()     => { setIsRecording(false); }
    );
    // Stop TTS on unmount
    return () => ttsEngine.stop();
  }, []);

  // Timer countdown — only runs after question is ready
  useEffect(() => {
    if (sessionData.isGeneratingQuestion || !currentQ) return;
    const timer = setInterval(() => {
      setTimerSeconds((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [sessionData.isGeneratingQuestion, currentQ]);

  // Helper to sanitize leftover markdown asterisks, quotes, and bracket tags
  const sanitizeText = (str) => {
    if (!str) return '';
    return str
      .replace(/^#+\s*/g, '')
      .replace(/^(【[^】]+】|\[[^\]]+\]|問：|追問：|考官：|考官發問：)\s*/g, '')
      .replace(/[*`~"']/g, '')
      .replace(/^[「『"“'`](.*?)[」』"”'`]$/g, '$1')
      .trim();
  };

  // Streaming typewriter effect + TTS trigger when complete
  useEffect(() => {
    if (!currentQ || !currentQ.text) {
      setDisplayedQuestion('');
      return;
    }
    const fullText = sanitizeText(currentQ.text);
    setDisplayedQuestion('');
    typewriterDoneRef.current = false;

    // Only stop previous speech if question index changed
    if (spokenQuestionIndexRef.current !== currentIdx) {
      ttsEngine.stop();
      setIsSpeaking(false);
    }

    let i = 0;
    const interval = setInterval(() => {
      i++;
      if (i <= fullText.length) {
        setDisplayedQuestion(fullText.slice(0, i));
      } else {
        clearInterval(interval);
        // ✅ Typewriter done → trigger TTS to speak the question ONLY ONCE per question index
        if (spokenQuestionIndexRef.current !== currentIdx) {
          spokenQuestionIndexRef.current = currentIdx;
          typewriterDoneRef.current = true;
          ttsEngine.speak(fullText, {
            onStart: () => setIsSpeaking(true),
            onEnd:   () => setIsSpeaking(false),
            onError: () => setIsSpeaking(false),
          });
        }
      }
    }, 20);
    return () => {
      clearInterval(interval);
    };
  }, [currentIdx, currentQ?.text]);

  // ✅ Loading state guard: show spinner while generating report or question
  if (isGeneratingReport) {
    return (
      <div class="max-w-7xl mx-auto px-4 py-20 flex flex-col items-center justify-center gap-6 text-center">
        <div class="relative">
          <div class="w-20 h-20 rounded-full border-4 border-emerald-100 border-t-emerald-600 animate-spin"></div>
          <span class="absolute inset-0 flex items-center justify-center material-symbols-outlined text-emerald-600 text-2xl">analytics</span>
        </div>
        <div>
          <h2 class="text-xl font-bold text-slate-800 mb-2">正在為您生成「戰略評測診斷報告」...</h2>
          <p class="text-sm text-slate-500 font-mono">Gemma-4-31B 正在彙整對答歷程，進行 STAR 四大維度評分與潛在盲區分析...</p>
          <p class="text-xs text-slate-400 font-mono mt-1">{sessionData.targetSchool} · {sessionData.targetMajor}</p>
        </div>
        <div class="flex gap-1.5 mt-2">
          {[0, 1, 2].map(i => (
            <div key={i} class="w-2 h-2 rounded-full bg-emerald-400 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }}></div>
          ))}
        </div>
      </div>
    );
  }

  if (sessionData.isGeneratingQuestion || !currentQ) {
    return (
      <div class="max-w-7xl mx-auto px-4 py-20 flex flex-col items-center justify-center gap-6 text-center">
        <div class="relative">
          <div class="w-20 h-20 rounded-full border-4 border-indigo-100 border-t-indigo-600 animate-spin"></div>
          <span class="absolute inset-0 flex items-center justify-center material-symbols-outlined text-indigo-600 text-2xl">psychology</span>
        </div>
        <div>
          <h2 class="text-xl font-bold text-slate-800 mb-2">AI 面試官正在準備題目中...</h2>
          <p class="text-sm text-slate-500 font-mono">Gemma-4-31B 正在根據您的備審資料和志願學校產生專屬問題...</p>
          <p class="text-xs text-slate-400 font-mono mt-1">{sessionData.targetSchool} · {sessionData.targetMajor}</p>
        </div>
        <div class="flex gap-1.5 mt-2">
          {[0, 1, 2].map(i => (
            <div key={i} class="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }}></div>
          ))}
        </div>
      </div>
    );
  }

  const simulateSpeechRecognition = () => {
    const sampleAnswer = currentIdx === 0
      ? '教授您好，在邊緣裝置推論優化專案中，我使用了 TensorRT 模型量化與 ONNX Runtime，成功將整體邊緣影像識別延遲從 120ms 顯著降至 45ms，並進行全流程 Profiling 驗證。'
      : '在 FP32 轉 INT8 過程中，推論速度提升約 3.8 倍，但精準度下降了約 1.5%。為了權衡，我採用 TensorRT 的 Entropy Calibrator 最小化資訊損失，並在邊緣端設計滑動窗口濾波演算法對控制訊號進行平滑化處理。';
    
    let i = 0;
    const interval = setInterval(() => {
      i += 3;
      if (i <= sampleAnswer.length) {
        setCandidateAnswer(sampleAnswer.slice(0, i));
      } else {
        setCandidateAnswer(sampleAnswer);
        clearInterval(interval);
      }
    }, 80);
  };

  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true);
      const started = sttEngineRef.current?.start();
      if (!started) {
        simulateSpeechRecognition();
      }
    } else {
      setIsRecording(false);
      sttEngineRef.current?.stop();
    }
  };

  const handleSubmit = async () => {
    if (!candidateAnswer.trim()) return;
    setIsSubmitting(true);
    setIsStreaming(true);

    try {
      let streamedQuestion = '';
      const res = await respondInterviewStreamApi(
        sessionData.sessionId,
        currentIdx,
        candidateAnswer,
        (chunkText, currentFullText) => {
          streamedQuestion = currentFullText;
        }
      );

      const finalQuestionText = res.nextQuestion || streamedQuestion;
      const nextTurnNumber = currentIdx + 2;
      let nextPhase = "專案細節深挖與架構設計";
      if (currentIdx + 1 === 1) {
        nextPhase = "專案經歷與架構設計";
      } else if (currentIdx + 1 === 2) {
        nextPhase = "核心技術與情境問答";
      } else if (currentIdx + 1 >= 3) {
        nextPhase = "總結反思與學習潛能";
      }

      setSessionData((prev) => {
        const updatedHistory = [
          ...prev.dialogueHistory,
          {
            turn: currentIdx + 1,
            phase: currentQ.phase,
            question: currentQ.text,
            answer: candidateAnswer
          }
        ];

        const updatedQuestions = [...prev.questions];
        const nextQText = finalQuestionText || `請針對您在 ${sessionData.targetMajor || '該科系'} 相關經驗中，最核心的專業技術能力與實作成果進行詳細說明？`;
        if (!res.isFinished) {
          updatedQuestions.push({
            index: nextTurnNumber,
            phase: nextPhase,
            text: nextQText,
            hint: "著重底層原理、問題分析與具體優化成效！"
          });
        }

        return {
          ...prev,
          dialogueHistory: updatedHistory,
          questions: updatedQuestions
        };
      });

      setCandidateAnswer('');
      setIsStreaming(false);
      setIsSubmitting(false);

      if (res.isFinished || (currentIdx + 1 >= (sessionData.questionCount || 3))) {
        try {
          const reportRes = await getReportApi(sessionData.sessionId);
          setSessionData((prev) => ({
            ...prev,
            evaluationReport: reportRes
          }));
        } catch (err) {
          console.warn("Report generation error:", err);
        }
        onFinishInterview();
      } else {
        setCurrentIdx((prev) => prev + 1);
      }
    } catch (err) {
      console.error("Submit error:", err);
      setIsStreaming(false);
      setIsSubmitting(false);
    }
  };

  const handleEarlyFinish = async () => {
    ttsEngine.stop();
    setIsSpeaking(false);
    setIsGeneratingReport(true);
    setIsSubmitting(true);
    try {
      const reportRes = await getReportApi(sessionData.sessionId);
      setSessionData((prev) => ({
        ...prev,
        evaluationReport: reportRes
      }));
    } catch (err) {
      console.warn("Report generation error:", err);
    }
    onFinishInterview();
  };

  const formatTimer = (secs) => {
    const m = String(Math.floor(secs / 60)).padStart(2, '0');
    const s = String(secs % 60).padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6 flex flex-col gap-6 pb-12">
      {/* Top Bar */}
      <div class="flex flex-wrap justify-between items-center bg-white border border-slate-200 rounded-xl px-6 py-3 shadow-xs gap-3">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-indigo-600">radio_button_checked</span>
          <span class="font-mono text-xs font-bold text-slate-800">
            {sessionData.targetSchool} · {sessionData.targetGroup} · {sessionData.targetMajor}
          </span>
          <span class={`text-xs px-2.5 py-0.5 rounded-full font-bold font-mono ${
            tierInfo.isTopTier ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-slate-100 text-slate-700'
          }`}>
            {tierInfo.tierLabel}
          </span>
        </div>

        <div class="flex items-center gap-3">
          <span class="font-mono text-xs font-bold text-slate-500 uppercase tracking-wider hidden sm:inline">
            {currentQ.phase} ({currentIdx + 1} / {sessionData.questions.length})
          </span>
          <div class="flex items-center gap-1.5 font-mono font-bold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-lg text-sm">
            <span class="material-symbols-outlined text-base">timer</span>
            {formatTimer(timerSeconds)}
          </div>
          <button
            onClick={handleEarlyFinish}
            disabled={isSubmitting}
            class="px-3.5 py-1.5 rounded-lg border border-rose-200 text-rose-700 bg-rose-50 hover:bg-rose-100 font-bold text-xs flex items-center gap-1.5 transition-colors shadow-2xs cursor-pointer"
            title="提早結束面試並立即進入戰略評分報告"
          >
            <span class="material-symbols-outlined text-base text-rose-600">stop_circle</span>
            直接結束 (產出報告)
          </button>
        </div>
      </div>

      {/* Cockpit Main Grid */}
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 5 cols: AI Professor & Question Card */}
        <div class="lg:col-span-5 flex flex-col gap-6">
          {/* Avatar Station */}
          <div class="bg-white border border-slate-200 rounded-xl p-5 flex flex-col items-center justify-center text-center relative shadow-xs">
            <div class="relative mb-3">
              <div class={`absolute -inset-1.5 rounded-full transition-all duration-300 ${isSpeaking ? 'bg-indigo-200 animate-pulse opacity-100' : 'bg-indigo-50 opacity-40'}`}></div>
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCqC2pswO3FPBlDhCffhVeyAiggy-MwnKLaeCaR2Bi1xt40tuF6z3-2IBQpaRCcwDI8Q9k3biVci6SnumJRP8JgxSxaFE8jQ_O7q9oVD4LUP9qms6ZkLp-0KZ1xvOt77vJf1Zr6tASz6IUy5FRQeqlOSxaePbpJ8Pa8b1673yRkz5H5TzAfMZiqAkQ2uT0OFWDZUId7AsL-C0psn1DVHIq1in5MyBhp2p0Qum4mf7xIXoLvyA7yhkhD"
                alt="AI Professor"
                class="w-20 h-20 rounded-full object-cover border-3 border-white shadow-md relative z-10"
              />
            </div>
            <WaveformBar isSpeaking={isSpeaking} />
            <span class={`text-xs font-mono font-bold tracking-widest uppercase mt-2 transition-colors duration-300 ${isSpeaking ? 'text-indigo-600' : 'text-slate-400'}`}>
              {isSpeaking ? 'Gemma-4-31B 面試官發話中' : '等待作答中'}
            </span>
            {isSpeaking && (
              <button
                onClick={() => { ttsEngine.stop(); setIsSpeaking(false); }}
                class="mt-2 text-xs text-slate-400 hover:text-slate-600 font-mono underline cursor-pointer"
              >
                停止語音朗讀
              </button>
            )}
          </div>

          {/* Core Question Card */}
          <div class="bg-white border-l-4 border-l-indigo-600 border border-slate-200 rounded-xl p-6 flex flex-col justify-between shadow-xs min-h-[220px]">
            <div>
              <div class="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center justify-between">
                <span class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-indigo-600 text-sm">psychology</span>
                  核心發問 (Question {currentIdx + 1})
                </span>
                <div class="flex items-center gap-2">
                  {isStreaming && (
                    <span class="text-[10px] bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded font-bold font-mono animate-pulse flex items-center gap-1">
                      <span class="w-1.5 h-1.5 rounded-full bg-indigo-600 animate-ping"></span>
                      SSE 實時串流中
                    </span>
                  )}
                  {tierInfo.isTopTier && (
                    <span class="text-[10px] bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded font-bold font-mono">
                      高難度專業技術 / 申論題 Mode
                    </span>
                  )}
                </div>
              </div>
              <p class="text-base sm:text-lg font-bold text-slate-900 leading-relaxed">
                {displayedQuestion}
              </p>
            </div>
            <p class="text-xs text-slate-400 font-mono mt-4 pt-3 border-t border-slate-100">
              請具體說明您採用的技術架構、問題拆解邏輯與量化成果指標。
            </p>
          </div>
        </div>

        {/* Right 7 cols: STT Transcription & Cockpit Controls */}
        <div class="lg:col-span-7 flex flex-col gap-6">
          {/* Previous Dialogue History if any */}
          {sessionData.dialogueHistory && sessionData.dialogueHistory.length > 0 && (
            <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 shadow-xs">
              <div class="text-xs font-mono font-bold text-slate-600 uppercase flex items-center gap-2 mb-2">
                <span class="material-symbols-outlined text-indigo-600 text-sm">history</span>
                過往對話歷程 (第 {sessionData.dialogueHistory.length} 輪作答摘要)
              </div>
              <div class="space-y-2 text-xs">
                {sessionData.dialogueHistory.slice(-1).map((item, idx) => (
                  <div key={idx} class="bg-white border border-slate-200 rounded-lg p-3">
                    <p class="font-bold text-indigo-900 mb-1">Q{item.turn}: {item.question}</p>
                    <p class="text-slate-700 text-xs leading-relaxed"><span class="font-bold text-slate-900">考生作答：</span>{item.answer}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Real-time STT Card */}
          <div class="bg-white border border-slate-200 rounded-xl p-6 flex flex-col relative shadow-xs">
            <div class="flex justify-between items-center mb-4 border-b border-slate-100 pb-3">
              <span class="text-xs font-mono font-bold text-slate-600 uppercase flex items-center gap-2">
                <span class="material-symbols-outlined text-sm">closed_caption</span>
                即時語音轉文字 (STT) 應答區 (第 {currentIdx + 1} 題作答)
              </span>
              <span class={`text-xs font-mono flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-bold transition-all ${
                isRecording
                  ? 'bg-rose-100 text-rose-700 border border-rose-300 animate-pulse'
                  : 'text-slate-500 bg-slate-100'
              }`}>
                <span class={`w-2 h-2 rounded-full ${isRecording ? 'bg-rose-600 animate-ping' : 'bg-slate-400'}`}></span>
                {isRecording ? '語音收音中 (STT REC)' : '待命開口'}
              </span>
            </div>

            <textarea
              rows="6"
              value={candidateAnswer}
              onChange={(e) => setCandidateAnswer(e.target.value)}
              placeholder="請點擊下方麥克風按鈕開口說話，或直接輸入回答..."
              class="w-full bg-slate-50 border border-slate-200 rounded-lg p-4 text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm sm:text-base leading-relaxed resize-none"
            />
          </div>

          {/* Controls Dock */}
          <div class="bg-white border border-slate-200 rounded-xl p-5 flex items-center justify-between shadow-xs">
            <button
              onClick={() => setShowHintModal(true)}
              class="px-4 py-2.5 rounded-lg border border-slate-300 text-slate-700 font-medium text-sm hover:bg-slate-50 transition-colors flex items-center gap-2"
            >
              <span class="material-symbols-outlined text-amber-500 text-lg">lightbulb</span>
              請求引導提示
            </button>

            {/* Pulsing Mic Control */}
            <div class="flex flex-col items-center justify-center">
              <button
                onClick={toggleRecording}
                class={`w-14 h-14 rounded-full flex items-center justify-center text-white shadow-lg transition-all ${
                  isRecording
                    ? 'bg-red-600 animate-mvPulse'
                    : 'bg-indigo-600 hover:bg-indigo-700'
                }`}
              >
                <span class="material-symbols-outlined text-2xl">mic</span>
              </button>
            </div>

            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              class="px-6 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm transition-all flex items-center gap-2 shadow-sm active:scale-95"
            >
              <span class="material-symbols-outlined text-base">send</span>
              {isSubmitting ? '送出中...' : '確認送出回答'}
            </button>
          </div>
        </div>
      </div>

      {/* Hint Modal */}
      {showHintModal && (
        <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div class="bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <div class="flex items-center gap-2 text-amber-600 font-bold text-lg mb-3">
              <span class="material-symbols-outlined text-2xl">lightbulb</span>
              Socratic 引導提示
            </div>
            <p class="text-slate-700 text-sm leading-relaxed mb-6">
              {currentQ.hint}
            </p>
            <div class="flex justify-end">
              <button
                onClick={() => setShowHintModal(false)}
                class="px-5 py-2 rounded-lg bg-indigo-600 text-white font-bold text-sm hover:bg-indigo-700 transition-colors"
              >
                理解，繼續答題
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
