const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const outDir = 'C:/Users/marti/Desktop/iThome---2026/days/images/day25';

if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: CHROME_PATH,
    args: ['--no-sandbox', '--disable-gpu'],
    defaultViewport: { width: 1280, height: 900 }
  });
  const page = await browser.newPage();

  await page.goto('http://localhost:5173', { waitUntil: 'networkidle2', timeout: 20000 });
  await new Promise(r => setTimeout(r, 1500));

  // Inject session state directly to report page
  await page.evaluate(() => {
    const allEls = document.querySelectorAll('[class]');
    let appFiber = null;
    for (const el of allEls) {
      const key = Object.keys(el).find(k => k.startsWith('__reactFiber'));
      if (!key) continue;
      let current = el[key];
      while (current) {
        if (current.elementType && typeof current.elementType === 'function' && current.elementType.name === 'App') {
          appFiber = current; break;
        }
        current = current.return;
      }
      if (appFiber) break;
    }
    if (!appFiber) return;
    const tabHook = appFiber.memoizedState;
    const sessionHook = tabHook.next;
    sessionHook.queue.dispatch({
      ...sessionHook.memoizedState,
      sessionId: 'sess_day25_report',
      targetSchool: '國立臺灣大學',
      targetMajor: '資訊工程學系',
      targetGroup: '資訊電機學群',
      questionCount: 3,
      evaluationReport: {
        scores: {
          logic_structure: 8.5,
          major_relevance: 9.0,
          communication_clarity: 8.0,
          adaptability: 7.5
        },
        overall_feedback: "面試整體表現相當出色！考生在回答中展現了紮實的邊緣裝置模型量化 (TensorRT/ONNX) 與軟硬體整合知識。在回答結構上能有效落實 STAR 原則，並對演算法權衡 (Trade-off) 有深刻理解。",
        strengths: [
          "STAR 結構極為完整，敘事脈絡清晰",
          "專業術語（FP32/INT8, Entropy Calibrator）精準且運用得當",
          "具備良好的跨領域邏輯與邊緣端實作經驗"
        ],
        improvements: [
          "面對延伸追問時，可進一步補充量化對推論精準度的具體影響指標",
          "建議可連結台大資工系當前的前沿研究實驗室（如高效能計算與 AI 晶片）"
        ],
        question_diagnoses: [
          {
            turn_index: 1,
            question: "你在邊緣裝置推論優化中使用了 TensorRT 和 ONNX Runtime，請詳細說明從 FP32 轉 INT8 量化時遇到的精準度下降問題，以及你如何解決？",
            original_answer: "在 FP32 轉 INT8 過程中，推論速度提升約 3.8 倍，但精準度下降了約 1.5%。為了權衡，我採用 TensorRT 的 Entropy Calibrator 最小化資訊損失。",
            weakness_analysis: "原始回答已涵蓋核心數據與技術方案，但缺乏面對極端邊界數據 (Edge Cases) 時的具體驗證過程，建議增加 Profiling 工具的使用說明。",
            improved_sample: "【Situation】在邊緣邊檢視訊識別專案中，受限於板端算力，FP32 模型的 120ms 延遲無法達到即時性需求。【Action】我採用 TensorRT 將模型進行 INT8 量化，並選擇 KL 散度導向的 Entropy Calibrator 進行校準。【Result】成功將模型延遲從 120ms 降低至 45ms (提升 2.67 倍)，精準度損失僅 1.2%，符合邊緣端部署要求。"
          },
          {
            turn_index: 2,
            question: "當面對生成式 AI 普及，你認為資工系學生最重要的核心競爭力是什麼？",
            original_answer: "我認為是系統底層架構的理解力，以及將 AI 工具與跨領域問題結合的能力。",
            weakness_analysis: "觀點明確，但缺乏具體案例佐證。",
            improved_sample: "【Situation】AI 工具能快速生成程式碼，但無法取代底層系統設計與架構優化能力。【Action】我著重於深入研讀作業系統與編譯器原理，並將 AI 模型應用於生醫影像分析專案。【Result】培養了不可被 AI 輕易取代的跨領域問題拆解與軟硬體協同設計能力。"
          }
        ]
      }
    });
    tabHook.queue.dispatch('report');
  });

  await new Promise(r => setTimeout(r, 2000));
  await page.screenshot({ path: path.join(outDir, '01_evaluation_report_top.png') });
  console.log('01 evaluation report top saved');

  // Scroll to middle for radar chart & strengths
  await page.evaluate(() => window.scrollTo(0, 300));
  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({ path: path.join(outDir, '02_radar_chart_and_insights.png') });
  console.log('02 radar chart and insights saved');

  // Open first accordion item and scroll down
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const accordionBtn = btns.find(b => b.textContent.includes('Q1'));
    if (accordionBtn) accordionBtn.click();
    window.scrollTo(0, 700);
  });
  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({ path: path.join(outDir, '03_turn_by_turn_accordion.png') });
  console.log('03 turn by turn accordion saved');

  await browser.close();
})();
