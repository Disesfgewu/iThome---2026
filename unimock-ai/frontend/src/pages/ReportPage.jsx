import React, { useState } from 'react';
import RadarCanvas from '../components/RadarCanvas';

export default function ReportPage({ sessionData, onReset }) {
  const [openAccordion, setOpenAccordion] = useState(0);

  const report = sessionData.evaluationReport;
  const scores = report.scores;

  const handleDownloadMarkdown = () => {
    const content = `# UniMock AI 模擬面試診斷報告

- **目標學校：** ${sessionData.targetSchool}
- **目標學群：** ${sessionData.targetGroup}
- **目標學系：** ${sessionData.targetMajor}
- **評分結果：** 84 / 100 (A- 具備良好基礎)
  - STAR 邏輯條理性: ${scores.logic_structure} / 10
  - 科系專業契合度: ${scores.major_relevance} / 10
  - 表達清晰度: ${scores.communication_clarity} / 10
  - 臨場應變力: ${scores.adaptability} / 10

## 綜合點評
${report.overall_feedback}

## 關鍵優勢 (Strengths)
${report.strengths.map((s) => `- ${s}`).join('\n')}

## 建議改進方向 (Improvements)
${report.improvements.map((i) => `- ${i}`).join('\n')}
`;

    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `UniMock_Report_${sessionData.targetSchool}_${sessionData.targetMajor}.md`;
    link.click();
  };

  return (
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      {/* Header */}
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <p class="font-mono text-xs text-slate-500 mb-1">SESSION ID: {sessionData.sessionId}</p>
          <h2 class="text-3xl font-bold text-slate-900 tracking-tight">評測診斷報告</h2>
        </div>
        <div class="flex gap-3">
          <button
            onClick={handleDownloadMarkdown}
            class="px-4 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-700 font-medium text-sm hover:bg-slate-50 transition-colors flex items-center gap-2 shadow-xs"
          >
            <span class="material-symbols-outlined text-lg">download</span>
            下載 Markdown / PDF 診斷書
          </button>
        </div>
      </div>

      {/* Top Grid: Score & Executive Summary */}
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
        {/* Score Badge */}
        <div class="lg:col-span-4 bg-white border border-slate-200 rounded-2xl p-8 flex flex-col justify-center items-center text-center shadow-xs relative overflow-hidden">
          <span class="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 font-mono font-bold text-xs uppercase tracking-widest mb-4">
            Overall Grade
          </span>
          <div class="flex items-baseline justify-center gap-2 mb-2">
            <span class="text-6xl font-extrabold text-indigo-600 tracking-tight">84</span>
            <span class="text-2xl text-slate-400 font-bold">/ 100</span>
          </div>
          <div class="flex items-center gap-2 mt-2">
            <span class="px-3 py-1 rounded-md bg-indigo-600 text-white font-bold text-sm">A-</span>
            <span class="text-sm font-medium text-slate-700">表現優異，具備錄取潛力</span>
          </div>
        </div>

        {/* Executive Summary */}
        <div class="lg:col-span-8 bg-white border border-slate-200 rounded-2xl p-8 flex flex-col justify-center shadow-xs">
          <h3 class="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2 border-l-4 border-indigo-600 pl-3">
            <span class="material-symbols-outlined text-indigo-600">summarize</span>
            執行摘要
          </h3>
          <p class="text-slate-600 text-base leading-relaxed mb-6">
            {report.overall_feedback}
          </p>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-slate-100 pt-4 text-xs font-mono">
            <div>
              <p class="text-slate-400 mb-1">目標志願</p>
              <p class="font-bold text-slate-800">{sessionData.targetSchool} {sessionData.targetMajor}</p>
            </div>
            <div>
              <p class="text-slate-400 mb-1">總題數</p>
              <p class="font-bold text-slate-800">{sessionData.questionCount} 題</p>
            </div>
            <div>
              <p class="text-slate-400 mb-1">語速 (WPM)</p>
              <p class="font-bold text-slate-800">142 (適中)</p>
            </div>
            <div>
              <p class="text-slate-400 mb-1">眼神接觸</p>
              <p class="font-bold text-emerald-600">88% (優)</p>
            </div>
          </div>
        </div>
      </div>

      {/* Middle Grid: Radar & Insights */}
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
        {/* Radar Chart Card */}
        <div class="lg:col-span-5 bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col items-center">
          <h3 class="text-base font-bold text-slate-900 mb-4 self-start">核心維度分析</h3>
          <RadarCanvas scores={scores} />
          <div class="flex justify-center gap-6 mt-4 text-xs font-mono">
            <span class="flex items-center gap-1.5 text-indigo-600 font-bold">
              <span class="w-3 h-3 rounded-xs bg-indigo-600"></span> 本次表現
            </span>
            <span class="flex items-center gap-1.5 text-slate-500">
              <span class="w-3 h-3 rounded-xs bg-slate-300"></span> 錄取基準線 (7.5)
            </span>
          </div>
        </div>

        {/* Strengths & Improvements */}
        <div class="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-6">
          {/* Strengths Card */}
          <div class="bg-white border-l-4 border-l-emerald-500 border border-slate-200 rounded-2xl p-6 shadow-xs">
            <h3 class="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
              <span class="material-symbols-outlined text-emerald-600">verified</span>
              關鍵優勢 (Strengths)
            </h3>
            <ul class="space-y-3">
              {report.strengths.map((st, i) => (
                <li key={i} class="flex items-start gap-2 text-sm text-slate-700">
                  <span class="material-symbols-outlined text-emerald-600 text-base mt-0.5">check_circle</span>
                  {st}
                </li>
              ))}
            </ul>
          </div>

          {/* Target Improvements Card */}
          <div class="bg-white border-l-4 border-l-amber-500 border border-slate-200 rounded-2xl p-6 shadow-xs">
            <h3 class="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
              <span class="material-symbols-outlined text-amber-500 fill">lightbulb</span>
              待加強項目 (Targets)
            </h3>
            <ul class="space-y-3">
              {report.improvements.map((im, i) => (
                <li key={i} class="flex items-start gap-2 text-sm text-slate-700">
                  <span class="material-symbols-outlined text-amber-500 text-base mt-0.5">target</span>
                  {im}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Turn-by-Turn Accordions */}
      <div class="mt-8">
        <h3 class="text-xl font-bold text-slate-900 mb-6">對答覆盤與 STAR 重構建議 (Turn-by-Turn)</h3>

        {report.question_diagnoses.map((diag, idx) => (
          <div key={idx} class="bg-white border border-slate-200 rounded-xl mb-4 overflow-hidden shadow-xs">
            <button
              onClick={() => setOpenAccordion(openAccordion === idx ? -1 : idx)}
              class="w-full text-left p-5 flex items-center justify-between hover:bg-slate-50 transition-colors"
            >
              <div class="flex items-center gap-3">
                <span class="font-mono text-xs font-bold bg-slate-100 text-slate-600 px-2.5 py-1 rounded-md">
                  Q{diag.turn_index}
                </span>
                <span class="font-bold text-slate-900 text-base">{diag.question}</span>
              </div>
              <span class={`material-symbols-outlined text-slate-400 transition-transform ${
                openAccordion === idx ? 'rotate-180' : ''
              }`}>
                expand_more
              </span>
            </button>

            {openAccordion === idx && (
              <div class="p-6 border-t border-slate-100 bg-slate-50/50 grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left: Original & Weakness */}
                <div class="space-y-4">
                  <div>
                    <h4 class="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <span class="material-symbols-outlined text-sm">record_voice_over</span>
                      學生原始回答 (Original Transcript)
                    </h4>
                    <p class="p-4 rounded-lg bg-white border border-slate-200 text-sm text-slate-800 leading-relaxed">
                      「{diag.original_answer}」
                    </p>
                  </div>

                  <div>
                    <h4 class="text-xs font-mono font-bold text-rose-600 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <span class="material-symbols-outlined text-sm">troubleshoot</span>
                      AI 弱點分析
                    </h4>
                    <p class="text-sm text-slate-700 leading-relaxed bg-rose-50 border border-rose-200 rounded-lg p-3">
                      {diag.weakness_analysis}
                    </p>
                  </div>
                </div>

                {/* Right: STAR Enhanced Sample */}
                <div class="bg-white border-l-4 border-l-indigo-600 border border-slate-200 rounded-lg p-5 shadow-xs">
                  <h4 class="text-sm font-bold text-indigo-900 mb-3 flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-indigo-600 fill">auto_awesome</span>
                    高分示範 (STAR 結構重構)
                  </h4>
                  <p class="text-sm text-slate-700 leading-relaxed">
                    {diag.improved_sample}
                  </p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Reset CTA */}
      <div class="mt-8 pt-6 border-t border-slate-200 flex justify-end">
        <button
          onClick={onReset}
          class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-6 py-2.5 rounded-xl shadow-md transition-colors"
        >
          重新開始另一輪練習
        </button>
      </div>
    </div>
  );
}
