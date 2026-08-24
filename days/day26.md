# 【Day 26】報告本地匯出：一鍵下載 Markdown / PDF 診斷書

學生需要將練習成果儲存留存。今天我們要實作 **一鍵匯出 Markdown / PDF 診斷書** 功能。

---

## 1. Markdown 報告匯出腳本 (`frontend/export.js`)

```javascript
function downloadMarkdownReport(reportData, candidateProfile) {
  const content = `# UniMock AI 模擬面試診斷報告

- **目標申請學系：** ${candidateProfile.target_major}
- **評分結果：**
  - STAR 邏輯條理性: ${reportData.scores.logic_structure} / 10
  - 科系專業契合度: ${reportData.scores.major_relevance} / 10
  - 表達清晰度: ${reportData.scores.communication_clarity} / 10
  - 臨場應變力: ${reportData.scores.adaptability} / 10

## 綜合點評
${reportData.overall_feedback}

## 優勢亮點
${reportData.strengths.map(s => `- ${s}`).join('\n')}

## 建議改進方向
${reportData.improvements.map(i => `- ${i}`).join('\n')}
`;

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `UniMock_Report_${candidateProfile.target_major}.md`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
```

---

## 結語與明天預告

今天我們打通了報告本地匯出下載功能。

明天 **【Day 27】**，我們將強化邊界異常處理，實作網路中斷、麥克風異常與模型降級機制！
