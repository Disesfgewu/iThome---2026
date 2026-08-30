import React, { useState, useRef } from 'react';
import { uploadResumeApi, startInterviewApi } from '../api/realApi';
import { departmentGroups as mockDepartmentGroups, checkSchoolTier } from '../api/realApi';

export default function SetupPage({ sessionData, setSessionData, onStartInterview }) {
  const [targetSchool, setTargetSchool] = useState(sessionData.targetSchool || '國立臺灣大學');
  const [targetGroup, setTargetGroup] = useState(sessionData.targetGroup || '資訊電機學群');
  const [targetMajor, setTargetMajor] = useState(sessionData.targetMajor || '資訊工程學系');
  const [persona, setPersona] = useState(sessionData.interviewerPersona || 'strict');
  const [qCount, setQCount] = useState(sessionData.questionCount || 3);
  const [isScanning, setIsScanning] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const hasStartedRef = useRef(false);

  const tierInfo = checkSchoolTier(targetSchool);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsScanning(true);
    try {
      const profile = await uploadResumeApi(file, targetSchool, targetGroup, targetMajor);
      setUploadedFileName(profile.fileName);
      setSessionData((prev) => ({
        ...prev,
        extractedProfile: profile
      }));
    } catch (err) {
      console.error('File upload failed:', err);
      alert('檔案解析失敗或格式損壞（請確認上傳有效的 PDF 備審資料）。系統已自動為您切換為純文字簡歷模式！');
    } finally {
      setIsScanning(false);
    }
  };

  const handleStart = async () => {
    // 防止重複點擊：若已在啟動中，直接忽略
    if (hasStartedRef.current || isStarting) return;
    hasStartedRef.current = true;
    setIsStarting(true);

    // ✅ Step 1：立即跳轉至面試艙（帶 loading 狀態），不等 API
    setSessionData((prev) => ({
      ...prev,
      targetSchool,
      targetGroup,
      targetMajor,
      interviewerPersona: persona,
      questionCount: qCount,
      isGeneratingQuestion: true,    // ← 面試艙用此旗標顯示載入中
      questions: []
    }));
    onStartInterview();

    // ✅ Step 2：在背景非同步呼叫 API，回傳後更新 sessionData
    try {
      const startRes = await startInterviewApi(
        sessionData.sessionId,
        targetSchool,
        targetGroup,
        targetMajor,
        persona,
        qCount,
        sessionData.extractedProfile
      );

      setSessionData((prev) => {
        const firstQ = startRes.firstQuestion;
        if (firstQ) {
          return {
            ...prev,
            sessionId: startRes.sessionId || prev.sessionId,
            isGeneratingQuestion: false,
            questions: [
              { index: 1, phase: '破冰自述與專業動機', text: firstQ, hint: '著重底層原理與專案動機！' }
            ]
          };
        } else {
          // API 回傳但 firstQuestion 為空 → 用 fallback 問題避免卡在 loading
          console.warn('startInterviewApi returned empty firstQuestion, using fallback');
          return {
            ...prev,
            sessionId: startRes.sessionId || prev.sessionId,
            isGeneratingQuestion: false,
            questions: [
              {
                index: 1,
                phase: '破冰自述與專業動機',
                text: `歡迎來到 ${targetSchool} ${targetMajor} 的面試模擬現場。請您先進行約 1 到 2 分鐘的自我介紹，說明您的報考動機，以及您最具代表性的個人優勢與專長？`,
                hint: '著重表達條理、動機與個人特色！'
              }
            ]
          };
        }
      });
    } catch (err) {
      console.error('startInterviewApi error:', err);
      setSessionData((prev) => ({ ...prev, isGeneratingQuestion: false }));
    }
  };

  return (
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <div class="mb-8">
        <h2 class="text-3xl font-bold text-slate-900 tracking-tight mb-2">面試參數與志願設定</h2>
        <p class="text-slate-600 text-base max-w-3xl">
          請設定您的目標學校、學群與學系。系統將根據學校難度階層動態調整 AI 面試官的出題深度與申論題型。
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left 60%: Configuration Options */}
        <div class="lg:col-span-7 flex flex-col gap-6">
          {/* School, Department Group & Major Grid */}
          <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-5">
            {/* Target School Text Input */}
            <div>
              <label class="block text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center justify-between">
                <span class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-indigo-600 text-lg">domain</span>
                  目標學校 (文字輸入)
                </span>
                <span class={`text-xs px-2.5 py-0.5 rounded-full font-bold font-mono ${
                  tierInfo.isTopTier ? 'bg-amber-100 text-amber-800 border border-amber-300' : 'bg-slate-100 text-slate-600'
                }`}>
                  {tierInfo.tierLabel}
                </span>
              </label>
              <input
                type="text"
                value={targetSchool}
                onChange={(e) => setTargetSchool(e.target.value)}
                placeholder="請輸入目標學校，例如：國立臺灣大學、國立成功大學..."
                class="w-full bg-slate-50 border border-slate-300 text-slate-900 rounded-lg py-3 px-4 focus:ring-2 focus:ring-indigo-500 focus:outline-none font-bold"
              />
              {/* Dynamic Difficulty Hint Banner */}
              <div class={`mt-2.5 p-3 rounded-lg text-xs leading-relaxed font-medium transition-all ${
                tierInfo.isTopTier
                  ? 'bg-amber-50 border border-amber-200 text-amber-900'
                  : 'bg-slate-50 border border-slate-200 text-slate-600'
              }`}>
                {tierInfo.difficultyDesc}
              </div>
            </div>

            {/* Department Group Dropdown */}
            <div>
              <label class="block text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                <span class="material-symbols-outlined text-indigo-600 text-lg">category</span>
                目標學群 (下拉選擇)
              </label>
              <select
                value={targetGroup}
                onChange={(e) => setTargetGroup(e.target.value)}
                class="w-full bg-slate-50 border border-slate-300 text-slate-900 rounded-lg py-3 px-4 focus:ring-2 focus:ring-indigo-500 focus:outline-none font-medium cursor-pointer"
              >
                {mockDepartmentGroups.map((group) => (
                  <option key={group} value={group}>
                    {group}
                  </option>
                ))}
              </select>
            </div>

            {/* Target Major Text Input */}
            <div>
              <label class="block text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                <span class="material-symbols-outlined text-indigo-600 text-lg">school</span>
                目標系所 / 專業 (文字輸入)
              </label>
              <input
                type="text"
                value={targetMajor}
                onChange={(e) => setTargetMajor(e.target.value)}
                placeholder="請輸入目標系所，例如：資訊工程學系、會計學研究所..."
                class="w-full bg-slate-50 border border-slate-300 text-slate-900 rounded-lg py-3 px-4 focus:ring-2 focus:ring-indigo-500 focus:outline-none font-bold"
              />
              <div class="flex gap-2 mt-2">
                <span class="text-xs text-slate-400 font-mono">熱門快速填入：</span>
                {['資訊工程學系', '電機工程學系', '會計學研究所', '企業管理研究所'].map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setTargetMajor(m)}
                    class="text-xs text-indigo-600 hover:underline font-medium"
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* AI Persona Radio Cards */}
          <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <label class="block text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <span class="material-symbols-outlined text-indigo-600 text-lg">psychology</span>
              AI 面試官性格模型
            </label>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Strict Persona Card */}
              <div
                onClick={() => setPersona('strict')}
                class={`relative flex flex-col p-5 rounded-xl border-2 cursor-pointer transition-all ${
                  persona === 'strict'
                    ? 'border-indigo-600 bg-indigo-50/40 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}
              >
                <div class="flex items-start justify-between w-full mb-3">
                  <div class="w-10 h-10 rounded-full bg-rose-100 text-rose-700 flex items-center justify-center font-bold">
                    <span class="material-symbols-outlined">gavel</span>
                  </div>
                  <div class={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    persona === 'strict' ? 'border-indigo-600' : 'border-slate-300'
                  }`}>
                    {persona === 'strict' && <div class="w-2.5 h-2.5 rounded-full bg-indigo-600" />}
                  </div>
                </div>
                <span class="font-bold text-lg text-slate-900">嚴格審查型</span>
                <span class="text-xs font-mono text-slate-500 mt-2">高壓追問 / 壓力測試 / 邏輯漏洞探測</span>
              </div>

              {/* Socratic Persona Card */}
              <div
                onClick={() => setPersona('socratic')}
                class={`relative flex flex-col p-5 rounded-xl border-2 cursor-pointer transition-all ${
                  persona === 'socratic'
                    ? 'border-indigo-600 bg-indigo-50/40 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}
              >
                <div class="flex items-start justify-between w-full mb-3">
                  <div class="w-10 h-10 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                    <span class="material-symbols-outlined">lightbulb</span>
                  </div>
                  <div class={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    persona === 'socratic' ? 'border-indigo-600' : 'border-slate-300'
                  }`}>
                    {persona === 'socratic' && <div class="w-2.5 h-2.5 rounded-full bg-indigo-600" />}
                  </div>
                </div>
                <span class="font-bold text-lg text-slate-900">啟發引導型</span>
                <span class="text-xs font-mono text-slate-500 mt-2">循循善誘 / 深度挖掘 / 潛力評估</span>
              </div>
            </div>
          </div>

          {/* Question Count Selector */}
          <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <label class="block text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <span class="material-symbols-outlined text-indigo-600 text-lg">list_alt</span>
              擬真題數設定
            </label>
            <div class="flex gap-4">
              {[3, 5, 8].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setQCount(num)}
                  class={`w-20 h-12 rounded-lg font-mono font-bold text-base transition-colors ${
                    qCount === num
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  0{num} 題
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right 40%: File Upload & Extracted Profile */}
        <div class="lg:col-span-5 flex flex-col gap-6">
          {/* Drag and Drop Area */}
          <label class={`relative border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center text-center transition-colors relative overflow-hidden min-h-[200px] ${
            isScanning
              ? 'bg-slate-50 border-slate-300 cursor-not-allowed'
              : 'bg-indigo-50/50 border-indigo-300 cursor-pointer hover:bg-indigo-50'
          }`}>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={isScanning}
              class="hidden"
            />
            {isScanning ? (
              <>
                <div class="w-14 h-14 rounded-full border-4 border-indigo-100 border-t-indigo-600 animate-spin mb-3" />
                <h3 class="font-bold text-slate-700 text-base mb-1">AI 正在解析備審資料...</h3>
                <p class="text-xs text-slate-500 font-mono">Gemma-4-31B 多模態分析中，請稍候</p>
                <div class="flex gap-1.5 mt-3">
                  {[0,1,2].map(i => (
                    <div key={i} class="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                  ))}
                </div>
              </>
            ) : (
              <>
                <div class="w-14 h-14 bg-indigo-600 text-white rounded-full flex items-center justify-center mb-3 shadow-md">
                  <span class="material-symbols-outlined text-3xl">cloud_upload</span>
                </div>
                <h3 class="font-bold text-slate-900 text-base mb-1">上傳備審資料 (PDF)</h3>
                <p class="text-xs text-slate-500">點擊上傳或拖曳 PDF 檔案至此</p>
                {uploadedFileName && (
                  <div class="mt-4 inline-flex items-center gap-2 bg-white border border-emerald-200 px-3 py-1.5 rounded-full shadow-xs text-xs font-mono text-slate-700">
                    <span class="material-symbols-outlined text-emerald-600 text-sm">check_circle</span>
                    {uploadedFileName}
                  </div>
                )}
              </>
            )}
          </label>

          {/* AI Extracted Profile Box */}
          <div class="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm flex-1 flex flex-col">
            <div class="bg-slate-100 px-5 py-3 border-b border-slate-200 flex items-center justify-between">
              <span class="text-xs font-mono font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                <span class="material-symbols-outlined text-indigo-600 text-sm">memory</span>
                AI 即時解析摘要
              </span>
              <span class="text-xs font-mono text-emerald-600 flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">bolt</span>
                {uploadedFileName ? '解析完成' : '待上傳'}
              </span>
            </div>

            <div class="p-5 flex flex-col gap-4 text-sm">
              <div class="bg-indigo-50 border border-indigo-100 rounded-lg p-3 text-xs font-mono">
                <p class="text-slate-500">志願：<strong class="text-indigo-900">{targetSchool} · {targetGroup} · {targetMajor}</strong></p>
              </div>

              {/* Highlights */}
              <div>
                <h4 class="text-xs font-mono font-bold text-emerald-700 flex items-center gap-1 mb-2">
                  <span class="material-symbols-outlined text-sm">add_circle</span>
                  技術與亮點 (Highlights)
                </h4>
                {sessionData.extractedProfile.highlights && sessionData.extractedProfile.highlights.length > 0 ? (
                  <ul class="space-y-1.5">
                    {sessionData.extractedProfile.highlights.map((h, i) => (
                      <li key={i} class="border-l-2 border-emerald-400 pl-2.5 text-slate-700 font-mono text-xs">
                        <strong>[{h.category}] {h.title}</strong>: {h.description}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p class="text-xs text-slate-400 font-mono">（尚未上傳 PDF 備審資料）</p>
                )}
              </div>

              {/* Blindspots */}
              <div>
                <h4 class="text-xs font-mono font-bold text-rose-700 flex items-center gap-1 mb-2">
                  <span class="material-symbols-outlined text-sm">warning</span>
                  潛在盲區 (Blindspots)
                </h4>
                {sessionData.extractedProfile.detectedBlindspots && sessionData.extractedProfile.detectedBlindspots.length > 0 ? (
                  <ul class="space-y-1.5">
                    {sessionData.extractedProfile.detectedBlindspots.map((b, i) => (
                      <li key={i} class="border-l-2 border-rose-400 pl-2.5 text-slate-700 font-mono text-xs">
                        {b}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p class="text-xs text-slate-400 font-mono">（尚未檢測到盲區）</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Start Button */}
      <div class="mt-8 pt-6 border-t border-slate-200 flex justify-end">
        <button
          onClick={handleStart}
          disabled={isStarting || isScanning}
          class={`font-bold text-lg px-8 py-3.5 rounded-xl shadow-lg transition-all flex items-center gap-3 active:scale-95 ${
            isStarting || isScanning
              ? 'bg-slate-400 text-slate-200 cursor-not-allowed opacity-70'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer'
          }`}
        >
          {isStarting ? (
            <>
              <span class="material-symbols-outlined animate-spin text-xl">progress_activity</span>
              正在連線 AI 面試官...
            </>
          ) : (
            <>
              🚀 啟動模擬面試艙
              <span class="material-symbols-outlined">arrow_forward</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
