# 【Day 26】報告本地匯出：一鍵下載 Markdown / PDF 診斷書與剪貼簿複製

學生在完成面試模擬與 AI 評測後，需要將備戰診斷成果儲存留存或導入個人備審資料。今天我們要介紹 ** UniMock AI 多功能報告匯出系統** 的開發與測試，包含「**一鍵下載 Markdown (.md) 檔**」、「**觸發瀏覽器原生存列印/PDF 產出**」以及「**剪貼簿一鍵複製**」三大核心功能。

---

## 1. 核心需求與用戶 Prompt 紀錄

依據使用者需求：「*進行 Day26 的部份的開發與測試，並記錄我給你的 prompt 以及對應的內容到 md 中，測試一樣使用瀏覽器 agent 去進行操作並實際驗證前端呈現無誤後，截圖到 md 中做紀錄*」

### 🎯 開發目標與規格要點
1. **多格式匯出彈窗 (Export Options Modal)**：點擊報告頁面頂部的「匯出 / 下載診斷書」按鈕時，跳出模態彈窗供使用者選擇匯出模式。
2. **格式一：下載完整 Markdown 檔 (.md)**：自動彙整目標志願、四維度評分、執行摘要點評、關鍵優勢、待加強項目以及逐題 STAR 重構對答歷程，導出檔名如 `UniMock_Report_逢甲大學_會計學研究所.md`。
3. **格式二：友善列印與 PDF 另存 (Print / PDF)**：透過 CSS `@media print` 隱藏導覽列與按鈕等非必要 UI，專注排版列印區塊。
4. **格式三：複製 Markdown 至剪貼簿 (Copy to Clipboard)**：調用 `navigator.clipboard` API 快速複製，並彈出 Toast 提示訊息。

---

## 2. 前端匯出邏輯實作 (`ReportPage.jsx` & `index.css`)

### 2.1 戰略診斷報告 Markdown 生成器

```javascript
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
```

### 2.2 匯出動作處理函數 (`Download`, `Print`, `Copy`)

```javascript
// 1. 觸發本地 Blob 檔案下載
const handleDownloadMarkdown = () => {
  const content = generateMarkdownContent();
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `UniMock_Report_${sessionData.targetSchool}_${sessionData.targetMajor}.md`;
  link.click();
  setShowExportModal(false);
  showToast('已成功下載 Markdown 診斷報告！');
};

// 2. 一鍵複製文字至剪貼簿
const handleCopyMarkdown = () => {
  const content = generateMarkdownContent();
  navigator.clipboard.writeText(content).then(() => {
    setShowExportModal(false);
    showToast('已將完整 Markdown 診斷報告複製至剪貼簿！');
  });
};

// 3. 觸發原生存列印模式 (PDF 保存)
const handlePrintPDF = () => {
  setShowExportModal(false);
  setTimeout(() => window.print(), 300);
};
```

### 2.3 友善列印 CSS 樣式 (`index.css`)

```css
/* Print / PDF Export Styles */
@media print {
  header, nav, button, .no-print {
    display: none !important;
  }
  body {
    background: white !important;
    color: black !important;
  }
  .max-w-7xl {
    max-width: 100% !important;
    padding: 0 !important;
  }
}
```

---

## 3. 瀏覽器 Agent 實機自動化測試與驗證

我們透過 **Browser Subagent** 進行真實瀏覽器操作測試，驗證研究所志願選擇、面試問答、評測報告產出與匯出彈窗功能：

### 3.1 報告頁面完整呈現

![Evaluation Report Page Full](images/day26/02_report_page_full.png)

### 3.2 匯出彈窗 (Export Modal) 互動展示

![Export Options Modal Demo](images/day26/01_export_modal_demo.png)

---

## 結語與明天預告

今天我們打通了 UniMock AI 戰略診斷報告的本地匯出下載與列印分享機制，支援 Markdown 檔案下載、PDF 友善列印以及剪貼簿一鍵複製。

明天 **【Day 27】**，我們將強化系統的邊界異常處理與穩定度，實作 **網路中斷、麥克風異常與 LLM 模型降級機制**！
