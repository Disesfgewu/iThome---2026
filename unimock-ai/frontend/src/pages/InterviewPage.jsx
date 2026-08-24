import React, { useState, useEffect } from 'react';
import WaveformBar from '../components/WaveformBar';
import { respondInterviewApi } from '../api/mockApi';

export default function InterviewPage({ sessionData, setSessionData, onFinishInterview }) {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [candidateAnswer, setCandidateAnswer] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [showHintModal, setShowHintModal] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(105);
  const [displayedQuestion, setDisplayedQuestion] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const currentQ = sessionData.questions[currentIdx] || sessionData.questions[0];

  // Timer countdown
  useEffect(() => {
    const timer = setInterval(() => {
      setTimerSeconds((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Streaming typewriter effect for question
  useEffect(() => {
    if (!currentQ) return;
    setDisplayedQuestion('');
    let i = 0;
    const interval = setInterval(() => {
      if (i < currentQ.text.length) {
        setDisplayedQuestion((prev) => prev + currentQ.text.charAt(i));
        i++;
      } else {
        clearInterval(interval);
      }
    }, 35);
    return () => clearInterval(interval);
  }, [currentIdx, currentQ]);

  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true);
      setCandidateAnswer('針對這個問題，我們當時主要面臨的是記憶體 VRAM 競爭與推論超時...');
    } else {
      setIsRecording(false);
    }
  };

  const handleSubmit = async () => {
    if (!candidateAnswer.trim()) return;
    setIsSubmitting(true);

    const res = await respondInterviewApi(sessionData.sessionId, currentIdx, candidateAnswer);
    
    // Save to dialogue history
    setSessionData((prev) => ({
      ...prev,
      dialogueHistory: [
        ...prev.dialogueHistory,
        {
          turn: currentIdx + 1,
          phase: currentQ.phase,
          question: currentQ.text,
          answer: candidateAnswer
        }
      ]
    }));

    setCandidateAnswer('');
    setIsSubmitting(false);

    if (res.isFinished || currentIdx + 1 >= sessionData.questions.length) {
      onFinishInterview();
    } else {
      setCurrentIdx((prev) => prev + 1);
    }
  };

  const formatTimer = (secs) => {
    const m = String(Math.floor(secs / 60)).padStart(2, '0');
    const s = String(secs % 60).padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6 h-[calc(100vh-4rem)] flex flex-col gap-6">
      {/* Top Bar */}
      <div class="flex justify-between items-center bg-white border border-slate-200 rounded-xl px-6 py-3 shadow-xs">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-indigo-600">radio_button_checked</span>
          <span class="font-mono text-xs font-bold text-slate-600 uppercase tracking-widest">
            當前階段：{currentQ.phase} ({currentIdx + 1} / {sessionData.questions.length})
          </span>
        </div>
        <div class="flex items-center gap-2 font-mono font-bold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-md text-sm">
          <span class="material-symbols-outlined text-base">timer</span>
          {formatTimer(timerSeconds)}
        </div>
      </div>

      {/* Cockpit Main Grid */}
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
        {/* Left 5 cols: AI Professor & Question Card */}
        <div class="lg:col-span-5 flex flex-col gap-6">
          {/* Avatar Station */}
          <div class="bg-white border border-slate-200 rounded-xl p-6 flex flex-col items-center justify-center text-center relative shadow-xs">
            <div class="relative mb-4">
              <div class="absolute -inset-2 rounded-full bg-indigo-100 animate-pulse opacity-75"></div>
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCqC2pswO3FPBlDhCffhVeyAiggy-MwnKLaeCaR2Bi1xt40tuF6z3-2IBQpaRCcwDI8Q9k3biVci6SnumJRP8JgxSxaFE8jQ_O7q9oVD4LUP9qms6ZkLp-0KZ1xvOt77vJf1Zr6tASz6IUy5FRQeqlOSxaePbpJ8Pa8b1673yRkz5H5TzAfMZiqAkQ2uT0OFWDZUId7AsL-C0psn1DVHIq1in5MyBhp2p0Qum4mf7xIXoLvyA7yhkhD"
                alt="AI Professor"
                class="w-28 h-28 rounded-full object-cover border-4 border-white shadow-md relative z-10"
              />
            </div>
            <WaveformBar isSpeaking={true} />
            <span class="text-xs font-mono font-bold text-indigo-600 tracking-widest uppercase mt-3">
              Gemma-4-31B 面試官發話中
            </span>
          </div>

          {/* Core Question Card */}
          <div class="bg-white border-l-4 border-l-indigo-600 border border-slate-200 rounded-xl p-6 flex-1 flex flex-col justify-between shadow-xs">
            <div>
              <div class="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                <span class="material-symbols-outlined text-indigo-600 text-sm">psychology</span>
                核心發問
              </div>
              <p class="text-lg font-bold text-slate-900 leading-relaxed min-h-[100px]">
                {displayedQuestion}
              </p>
            </div>
            <p class="text-xs text-slate-400 font-mono mt-4">
              請具體說明您採用的技術架構與衡量指標。
            </p>
          </div>
        </div>

        {/* Right 7 cols: STT Transcription & Cockpit Controls */}
        <div class="lg:col-span-7 flex flex-col gap-6">
          {/* Real-time STT Card */}
          <div class="bg-white border border-slate-200 rounded-xl p-6 flex-1 flex flex-col relative shadow-xs">
            <div class="flex justify-between items-center mb-4 border-b border-slate-100 pb-3">
              <span class="text-xs font-mono font-bold text-slate-600 uppercase flex items-center gap-2">
                <span class="material-symbols-outlined text-sm">closed_caption</span>
                即時語音轉文字 (STT) 應答區
              </span>
              <span class="text-xs font-mono text-indigo-600 flex items-center gap-1">
                <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                REC
              </span>
            </div>

            <textarea
              value={candidateAnswer}
              onChange={(e) => setCandidateAnswer(e.target.value)}
              placeholder="請點擊下方麥克風按鈕開口說話，或直接輸入回答..."
              class="w-full flex-1 bg-slate-50 border border-slate-200 rounded-lg p-4 text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-base leading-relaxed resize-none"
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
                class={`w-16 h-16 rounded-full flex items-center justify-center text-white shadow-lg transition-all ${
                  isRecording
                    ? 'bg-red-600 animate-mvPulse'
                    : 'bg-indigo-600 hover:bg-indigo-700'
                }`}
              >
                <span class="material-symbols-outlined text-3xl">mic</span>
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
