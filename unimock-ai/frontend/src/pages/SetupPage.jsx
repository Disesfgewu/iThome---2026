import React, { useState } from 'react';
import { uploadResumeApi } from '../api/mockApi';

export default function SetupPage({ sessionData, setSessionData, onStartInterview }) {
  const [targetMajor, setTargetMajor] = useState(sessionData.targetMajor || '資訊工程學系');
  const [persona, setPersona] = useState(sessionData.interviewerPersona || 'strict');
  const [qCount, setQCount] = useState(sessionData.questionCount || 3);
  const [isScanning, setIsScanning] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('陳小明_資工自傳與專案.pdf');

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    setIsScanning(true);
    const profile = await uploadResumeApi(file, targetMajor);
    setUploadedFileName(profile.fileName);
    setSessionData((prev) => ({
      ...prev,
      extractedProfile: profile
    }));
    setIsScanning(false);
  };

  const handleStart = () => {
    setSessionData((prev) => ({
      ...prev,
      targetMajor,
      interviewerPersona: persona,
      questionCount: qCount
    }));
    onStartInterview();
  };

  return (
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <div class="mb-8">
        <h2 class="text-3xl font-bold text-slate-900 tracking-tight mb-2">面試參數設定</h2>
        <p class="text-slate-600 text-base max-w-3xl">
          系統將根據您設定的學系與面試官性格，結合您的個人履歷與備審檔案，動態生成高擬真學術面試題庫。
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left 60%: Configuration Options */}
        <div class="lg:col-span-7 flex flex-col gap-6">
          {/* Target Major Dropdown */}
          <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <label class="block text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
              <span class="material-symbols-outlined text-indigo-600 text-lg">school</span>
              目標申請學系
            </label>
            <select
              value={targetMajor}
              onChange={(e) => setTargetMajor(e.target.value)}
              class="w-full bg-slate-50 border border-slate-300 text-slate-900 rounded-lg py-3 px-4 focus:ring-2 focus:ring-indigo-500 focus:outline-none font-medium cursor-pointer"
            >
              <option value="資訊工程學系">資訊工程學系 (Computer Science)</option>
              <option value="醫學系">醫學系 (Medicine)</option>
              <option value="電機工程學系">電機工程學系 (Electrical Engineering)</option>
              <option value="企業管理學系">企業管理學系 (Business Administration)</option>
            </select>
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
          <label class="relative bg-indigo-50/50 border-2 border-dashed border-indigo-300 rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-indigo-50 transition-colors relative overflow-hidden min-h-[200px]">
            {isScanning && <div class="mvScan" />}
            <input type="file" accept=".pdf" onChange={handleFileUpload} class="hidden" />
            <div class="w-14 h-14 bg-indigo-600 text-white rounded-full flex items-center justify-center mb-3 shadow-md">
              <span class="material-symbols-outlined text-3xl">cloud_upload</span>
            </div>
            <h3 class="font-bold text-slate-900 text-base mb-1">上傳備審資料 (PDF)</h3>
            <p class="text-xs text-slate-500">點擊上傳或拖曳 PDF 檔案至此</p>
            <div class="mt-4 inline-flex items-center gap-2 bg-white border border-slate-200 px-3 py-1.5 rounded-full shadow-xs text-xs font-mono text-slate-700">
              <span class="material-symbols-outlined text-emerald-600 text-sm">check_circle</span>
              {uploadedFileName}
            </div>
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
                解析完成
              </span>
            </div>

            <div class="p-5 flex flex-col gap-4 text-sm">
              {/* Highlights */}
              <div>
                <h4 class="text-xs font-mono font-bold text-emerald-700 flex items-center gap-1 mb-2">
                  <span class="material-symbols-outlined text-sm">add_circle</span>
                  技術與亮點 (Highlights)
                </h4>
                <ul class="space-y-1.5">
                  {sessionData.extractedProfile.highlights.map((h, i) => (
                    <li key={i} class="border-l-2 border-emerald-400 pl-2.5 text-slate-700 font-mono text-xs">
                      <strong>[{h.category}] {h.title}</strong>: {h.description}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Blindspots */}
              <div>
                <h4 class="text-xs font-mono font-bold text-rose-700 flex items-center gap-1 mb-2">
                  <span class="material-symbols-outlined text-sm">warning</span>
                  潛在盲區 (Blindspots)
                </h4>
                <ul class="space-y-1.5">
                  {sessionData.extractedProfile.detectedBlindspots.map((b, i) => (
                    <li key={i} class="border-l-2 border-rose-400 pl-2.5 text-slate-700 font-mono text-xs">
                      {b}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Start Button */}
      <div class="mt-8 pt-6 border-t border-slate-200 flex justify-end">
        <button
          onClick={handleStart}
          class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-lg px-8 py-3.5 rounded-xl shadow-lg transition-all flex items-center gap-3 active:scale-95"
        >
          🚀 啟動模擬面試艙
          <span class="material-symbols-outlined">arrow_forward</span>
        </button>
      </div>
    </div>
  );
}
