# 【Day 25】報告視覺化：前端動態雷達圖與評分報告渲染

當面試結束後，前端頁面需呈現視覺化的面試報告。今天我們要使用 **Chart.js** 繪製多維度雷達圖，並渲染結構化診斷卡片。

---

## 1. 雷達圖 Chart.js 渲染模組 (`frontend/radar_chart.js`)

```javascript
function renderRadarChart(canvasId, scores) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['STAR 邏輯條理性', '科系專業契合度', '表達清晰度', '臨場應變力'],
      datasets: [{
        label: '模擬面試評分 (1-10)',
        data: [
          scores.logic_structure,
          scores.major_relevance,
          scores.communication_clarity,
          scores.adaptability
        ],
        backgroundColor: 'rgba(34, 211, 238, 0.2)',
        borderColor: '#22d3ee',
        pointBackgroundColor: '#22d3ee'
      }]
    },
    options: {
      scales: {
        r: {
          min: 0,
          max: 10,
          ticks: { stepSize: 2 }
        }
      }
    }
  });
}
```

---

## 結語與明天預告

今天我們實現了雷達圖與診斷報告的前端視覺化。

明天 **【Day 26】**，我們將實作一鍵將面試診斷報告本地匯出為 Markdown / PDF 檔案的功能！
