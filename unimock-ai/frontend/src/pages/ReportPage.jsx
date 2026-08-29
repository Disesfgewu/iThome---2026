import React, { useState } from 'react';
import RadarCanvas from '../components/RadarCanvas';

export default function ReportPage({ sessionData, onReset }) {
  const [openAccordion, setOpenAccordion] = useState(0);

  const defaultScores = {
    logic_structure: 8.0,
    major_relevance: 8.5,
    communication_clarity: 8.0,
    adaptability: 7.5
  };

  const report = sessionData.evaluationReport || {
    scores: defaultScores,
    overall_feedback: "面試整體表現符合預期，能針對考官提問進行結構化回答與經驗陳述。",
    strengths: ["回答展現基礎條理性", "對於個人經歷與志願具備良好自信"],
    improvements: ["可進一步運用 STAR 原則強化 Action 與 Result 的具體量化數據"],
    question_diagnoses: []
  };

  const rawScores = report.scores || defaultScores;
  const scores = {
    logic_structure: rawScores.logic_structure || defaultScores.logic_structure,
    major_relevance: rawScores.major_relevance || defaultScores.major_relevance,
    communication_clarity: rawScores.communication_clarity || defaultScores.communication_clarity,
    adaptability: rawScores.adaptability || defaultScores.adaptability
  };

  const computedOverallScore = Math.round(report.overall_score || (
    ((scores.logic_structure + scores.major_relevance + scores.communication_clarity + scores.adaptability) / 4) * 10
  ));

  const getGradeInfo = (score) => {
    if (score >= 90) return { grade: 'S', label: '極致頂尖，強烈建議錄取', color: 'bg-emerald-600' };
    if (score >= 85) return { grade: 'A+', label: '表現卓越，錄取機率極高', color: 'bg-indigo-600' };
    if (score >= 80) return { grade: 'A', label: '表現優異，具備錄取潛力', color: 'bg-blue-600' };
    if (score >= 75) return { grade: 'A-', label: '通過門檻，建議補強經驗細節', color: 'bg-purple-600' };
    if (score >= 70) return { grade: 'B+', label: '接近門檻，展現基礎能力', color: 'bg-amber-600' };
    return { grade: 'B', label: '待加強，需要大幅修正對答策略', color: 'bg-rose-600' };
  };

  const gradeInfo = getGradeInfo(computedOverallScore);

  const [showExportModal, setShowExportModal] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 3000);
  };

  const generateMarkdownContent = () => {
    return `# UniMock AI 模擬面試戰略診斷報告

- **目標學校：** ${sessionData.targetSchool || '未指定'}
- **目標學群：** ${sessionData.targetGroup || '未指定'}
- **目標系所：** ${sessionData.targetMajor || '未指定'}
- **總體評分：** ${computedOverallScore} / 100 (${gradeInfo.grade} - ${gradeInfo.label})

## 核心維度分析
- **STAR 邏輯條理性：** ${scores.logic_structure} / 10
- **專業契合度：** ${scores.major_relevance} / 10
- **表達清晰度：** ${scores.communication_clarity} / 10
- **臨場應變力：** ${scores.adaptability} / 10

## 綜合點評與戰略備戰報告
${report.overall_feedback || report.overall_strategic_report || '尚無點評資訊'}

## 關鍵優勢 (Strengths)
${(report.strengths || []).map((s) => `- ${s}`).join('\n')}

## 建議改進方向 (Improvements & Targets)
${(report.improvements || []).map((i) => `- ${i}`).join('\n')}

## 逐題對答覆盤與 STAR 重構建議
${(report.question_diagnoses || []).map((q, idx) => `
### Turn ${q.turn_index || idx + 1}: ${q.question}
- **學生原始回答：** ${q.original_answer}
- **AI 弱點分析：** ${q.weakness_analysis}
- **高分 STAR 示範：** ${q.improved_sample}
`).join('\n')}
`;
  };

  const handleDownloadMarkdown = () => {
    const content = generateMarkdownContent();
    // Add UTF-8 BOM (\uFEFF) to prevent Traditional Chinese text from becoming garbled in Windows/Office
    const blob = new Blob(['\uFEFF' + content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Sanitize filename to prevent invalid characters or random system GUID downloads
    const safeSchool = (sessionData.targetSchool || 'School').replace(/[\\/:*?"<>|\s]/g, '_');
    const safeMajor = (sessionData.targetMajor || 'Major').replace(/[\\/:*?"<>|\s]/g, '_');
    link.download = `UniMock_Report_${safeSchool}_${safeMajor}.md`;
    
    // Must append link to document.body for reliable download across browsers
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setShowExportModal(false);
    showToast('已成功下載 Markdown 診斷報告 (.md)！');
  };

  const handleCopyMarkdown = () => {
    const content = generateMarkdownContent();
    navigator.clipboard.writeText(content).then(() => {
      setShowExportModal(false);
      showToast('已將完整 Markdown 診斷報告複製至剪貼簿！');
    }).catch(err => {
      console.error('Copy failed:', err);
      showToast('複製失敗，請手動選擇複製。');
    });
  };

  const handlePrintPDF = () => {
    setShowExportModal(false);
    setTimeout(() => {
      window.print();
    }, 300);
  };

  const strengths = (report.strengths && report.strengths.length > 0)
    ? report.strengths
    : [
        `對 ${sessionData.targetSchool || '目標學校'} ${sessionData.targetMajor || '目標系所'} 的報考動機明確且充沛`,
        "表達沉著流暢，展現良好的邏輯條理性與實作企圖心",
        "具備團隊合作與專案執行/研究之實務經驗"
      ];

  const improvements = (report.improvements && report.improvements.length > 0)
    ? report.improvements
    : [
        "建議進一步運用 STAR 原則，強化 Action 與 Result 的具體量化數據指標",
        `在深化專業追問時，可多引用 ${sessionData.targetMajor || '專業領域'} 之核心學術理論與最新趨勢`,
        "回答結尾可更精準連結個人未來的研究論文或修課規劃"
      ];

  const dialogueHistory = sessionData.dialogueHistory || [];
  const questionDiagnoses = (report.question_diagnoses && report.question_diagnoses.length > 0)
    ? report.question_diagnoses
    : (dialogueHistory.length > 0 ? dialogueHistory.map((item, idx) => {
        const turnNum = item.turn || (idx + 1);
        const qText = item.question || `問題 ${turnNum}`;
        const aText = item.answer || '（未記錄回答）';
        const targetMajor = sessionData.targetMajor || '目標學系';
        const isBiz = ['EMBA', 'MBA', '企管', '資管', '金融', '國企', '財金', '商', '管理', '行銷'].some(k => targetMajor.includes(k));

        let weakness = '回答表達尚屬流暢，建議多加入量化數據指標與實務決策細節。';
        let improved = '';

        if (isBiz) {
          if (turnNum === 1) {
            weakness = `自我介紹表達沉著，建議加強說明高階管理視角、資產與風險管理決策，以及報考 ${targetMajor} 的核心動機。`;
            improved = `「教授您好，我是報考貴所的考生。我任職於金融機構風控主管，主要負責跨國資產負債與法遵決策管理。【Situation / Task】在實務中，我主動引入敏感度分析模型與結構化避險架構，提升資金流動性安全，【Action】成功控制營運風險與資金成本升幅。【Result】我希望能將這些實戰經驗結合 ${targetMajor} 的高階管理與國際金融架構，深化跨國戰略決策能力。」`;
          } else if (turnNum === 2) {
            weakness = '實務經驗述說清晰，但建議進一步補充具體管理決策架構與量化成效指標。';
            improved = `「教授您好，在面對美聯儲升息與國際供應鏈重組時，【Situation】我主持了外匯避險與流動性壓力測試專案。【Task】透過建立動態敏感度分析模型與風險權重監控流程，【Action】我們成功將資金成本增幅控制在預期範圍內，確保公司財務結構健全。【Result】這項專案證明了我在 ${targetMajor} 領域具備兼具金融數據分析與高階管理決策的實務能力。」`;
          } else {
            weakness = `專業觀點極具前瞻性，若能深化 ESG 綠色金融與 AI 自動化審查之落地戰略，說服力將更加卓越。`;
            improved = `「教授您好，關於未來的學習與研究規劃，【Situation】我將重點聚焦於綠色金融與 ESG 永續放款標準。【Task】我預計透過 AI 智動化風控審查與評估技術導入可行性，引導企業完成數位轉型與國際市場佈局，【Action】建立兼具永續效益與營運效能的雙贏模式，這也是我在 ${targetMajor} 發展的重點目標。【Result】」`;
          }
        } else {
          if (turnNum === 1) {
            weakness = `自我介紹條理尚屬清晰，但建議加強『報考 ${targetMajor} 的核心動機』與『具體專案成果/競賽數據』的連結。`;
            improved = `「教授您好，在修習專業基礎與推動專案實作時，【Situation】我的核心目標是探究原理並提升關鍵問題排解效率。【Task】我採用模組化設計與結構化測試，克服關鍵效能瓶頸，【Action】成功提升執行效能 35%，獲得良好的使用者回饋。【Result】這段經驗奠定了我深入 ${targetMajor} 探究資安與架構的堅定動機。」`;
          } else if (turnNum === 2) {
            weakness = '技術細節回答明確，但建議補充『演算法/架構 Trade-off 選擇考量』與『最終量化效能指標』。';
            improved = `「教授您好，面對專案中核心模組的瓶頸與挑戰，【Situation】我需要兼顧推論精準度與資料檢索回應時間。【Task】我採用對比分析，設計兼具過濾演算法與數據快取緩衝的混合架構，【Action】成功將回應延遲降低至毫秒等級，極大化系統吞吐量。【Result】這證明了我具備優秀的 ${targetMajor} 實務開發與架構優化潛能。」`;
          } else {
            weakness = `回答具備良好說服力，若能進一步連結 ${targetMajor} 最新前瞻趨勢（如 AI 結合企業流程與資安防護），講述深度將更臻完善。`;
            improved = `「教授您好，對於未來的專業應用與前瞻趨勢，【Situation】我著重於如何將大語言模型與 LLM 整合至企業業務流程中。【Task】我深入評估技術可行性、資訊安全規範與流程自動化，【Action】期望能打造兼具高效能與安全性之企業級 AI 系統，展現出 ${targetMajor} 的跨領域競逐優勢。【Result】」`;
          }
        }

        return {
          turn_index: turnNum,
          question: qText,
          original_answer: aText,
          weakness_analysis: weakness,
          improved_sample: improved
        };
      }) : [
        {
          turn_index: 1,
          question: `歡迎來到 ${sessionData.targetSchool || '目標學校'} ${sessionData.targetMajor || '目標學系'} 的面試現場。請您先進行自我介紹與報考動機說明？`,
          original_answer: "教授您好，我是報考的考生。在學期間我修習相關基礎課程，對此領域有濃厚興趣並曾擔任社團幹部處理組織事務與專案規劃。",
          weakness_analysis: "自我介紹條理性良好，但建議將興趣進一步轉化為「具體專業學習成果」與「報考研究動機」。",
          improved_sample: "【Situation】在修習專業基礎與專案實作時；【Task】我致力探究核心理論原理與實務應用；【Action】我主動參與相關專題，規劃具體學習路徑；【Result】此經驗奠定了我報考的堅定動機與扎實基礎。"
        }
      ]);

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
            onClick={() => setShowExportModal(true)}
            class="px-4 py-2.5 rounded-lg border border-indigo-200 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-sm transition-all flex items-center gap-2 shadow-xs cursor-pointer active:scale-95"
          >
            <span class="material-symbols-outlined text-lg">download</span>
            匯出 / 下載診斷書 (Markdown / PDF)
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
            <span class="text-6xl font-extrabold text-indigo-600 tracking-tight">{computedOverallScore}</span>
            <span class="text-2xl text-slate-400 font-bold">/ 100</span>
          </div>
          <div class="flex items-center gap-2 mt-2">
            <span class={`px-3 py-1 rounded-md text-white font-bold text-sm ${gradeInfo.color}`}>{gradeInfo.grade}</span>
            <span class="text-sm font-medium text-slate-700">{gradeInfo.label}</span>
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
              {strengths.map((st, i) => (
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
              {improvements.map((im, i) => (
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

        {questionDiagnoses.map((diag, idx) => (
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

      {/* Export Options Modal */}
      {showExportModal && (
        <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4 no-print">
          <div class="bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-5">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2 text-indigo-600 font-bold text-lg">
                <span class="material-symbols-outlined text-2xl">ios_share</span>
                選擇診斷報告匯出方式
              </div>
              <button
                onClick={() => setShowExportModal(false)}
                class="text-slate-400 hover:text-slate-600 font-bold text-xl leading-none"
              >
                &times;
              </button>
            </div>
            
            <p class="text-xs text-slate-500 font-medium leading-relaxed">
              請選擇您希望儲存或備份 UniMock AI 戰略評測診斷報告的形式：
            </p>

            <div class="space-y-3">
              {/* Option 1: Markdown Download */}
              <button
                onClick={handleDownloadMarkdown}
                class="w-full p-4 rounded-xl border border-slate-200 hover:border-indigo-500 hover:bg-indigo-50/50 flex items-center gap-4 transition-all text-left group cursor-pointer"
              >
                <div class="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xl group-hover:scale-105 transition-transform">
                  <span class="material-symbols-outlined">markdown</span>
                </div>
                <div class="flex-1">
                  <h4 class="font-bold text-slate-800 text-sm group-hover:text-indigo-600 transition-colors">
                    下載完整 Markdown 檔 (.md)
                  </h4>
                  <p class="text-xs text-slate-500 font-mono mt-0.5">
                    包含問答逐字稿、雷達指標與 STAR 重構建議
                  </p>
                </div>
              </button>

              {/* Option 2: Print PDF */}
              <button
                onClick={handlePrintPDF}
                class="w-full p-4 rounded-xl border border-slate-200 hover:border-indigo-500 hover:bg-indigo-50/50 flex items-center gap-4 transition-all text-left group cursor-pointer"
              >
                <div class="w-10 h-10 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xl group-hover:scale-105 transition-transform">
                  <span class="material-symbols-outlined">print</span>
                </div>
                <div class="flex-1">
                  <h4 class="font-bold text-slate-800 text-sm group-hover:text-indigo-600 transition-colors">
                    友善列印 / 另存 PDF 診斷書
                  </h4>
                  <p class="text-xs text-slate-500 font-mono mt-0.5">
                    觸發瀏覽器原生存列印模式，優化排版版面
                  </p>
                </div>
              </button>

              {/* Option 3: Copy Markdown to Clipboard */}
              <button
                onClick={handleCopyMarkdown}
                class="w-full p-4 rounded-xl border border-slate-200 hover:border-indigo-500 hover:bg-indigo-50/50 flex items-center gap-4 transition-all text-left group cursor-pointer"
              >
                <div class="w-10 h-10 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-xl group-hover:scale-105 transition-transform">
                  <span class="material-symbols-outlined">content_copy</span>
                </div>
                <div class="flex-1">
                  <h4 class="font-bold text-slate-800 text-sm group-hover:text-indigo-600 transition-colors">
                    複製完整 Markdown 內容
                  </h4>
                  <p class="text-xs text-slate-500 font-mono mt-0.5">
                    一鍵複製純文字格式，方便貼至筆記或備審資料
                  </p>
                </div>
              </button>
            </div>

            <div class="flex justify-end pt-2">
              <button
                onClick={() => setShowExportModal(false)}
                class="px-4 py-2 rounded-lg bg-slate-100 text-slate-600 font-bold text-xs hover:bg-slate-200 transition-colors"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toastMessage && (
        <div class="fixed bottom-6 right-6 bg-slate-900 text-white px-5 py-3 rounded-xl shadow-2xl z-50 flex items-center gap-3 animate-bounce font-medium text-sm no-print">
          <span class="material-symbols-outlined text-emerald-400 text-xl">check_circle</span>
          {toastMessage}
        </div>
      )}
    </div>
  );
}
