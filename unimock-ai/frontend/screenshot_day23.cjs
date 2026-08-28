const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

const outDir = path.resolve('C:/Users/marti/Desktop/iThome---2026/days/images/day23');
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: CHROME_PATH,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--lang=zh-TW'],
    defaultViewport: { width: 1280, height: 800 }
  });
  const page = await browser.newPage();

  // Screenshot 1: Setup Page
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 2000));
  await page.screenshot({ path: path.join(outDir, '01_setup_page.png'), fullPage: false });
  console.log('01 saved');

  // Inject Interview Cabin state via React fiber
  await page.evaluate(() => {
    const allEls = document.querySelectorAll('[class]');
    let appFiber = null;
    for (const el of allEls) {
      const key = Object.keys(el).find(k => k.startsWith('__reactFiber'));
      if (!key) continue;
      let current = el[key];
      while (current) {
        if (current.elementType && typeof current.elementType === 'function' && current.elementType.name === 'App') {
          appFiber = current;
          break;
        }
        current = current.return;
      }
      if (appFiber) break;
    }
    if (!appFiber) { console.error('App fiber not found'); return; }
    const tabHook = appFiber.memoizedState;
    const sessionHook = tabHook.next;
    const prevData = sessionHook.memoizedState;
    const newData = {
      ...prevData,
      sessionId: 'sess_demo_day23',
      targetSchool: '國立臺灣大學',
      targetMajor: '資訊工程學系',
      targetGroup: '資訊電機學群',
      isGeneratingQuestion: false,
      questions: [
        {
          index: 1,
          phase: '破冰自我介紹',
          text: '你在邊緣裝置推論優化中使用了 TensorRT 和 ONNX Runtime，請詳細說明從 FP32 轉 INT8 量化時遇到的精準度下降問題，以及你如何透過 Entropy Calibrator 解決此問題？',
          hint: '著重技術細節與量化成果！'
        }
      ],
      dialogueHistory: []
    };
    sessionHook.queue.dispatch(newData);
    tabHook.queue.dispatch('interview');
  });

  await new Promise(r => setTimeout(r, 2500));

  // Screenshot 2: Interview Cockpit with Question 1 ready
  await page.screenshot({ path: path.join(outDir, '02_interview_cockpit_stt_ready.png'), fullPage: false });
  console.log('02 saved');

  // Click the mic button
  try {
    await page.click('button.rounded-full');
  } catch (e) {
    console.log('mic button click failed:', e.message);
  }
  await new Promise(r => setTimeout(r, 800));

  // Screenshot 3: After clicking mic (STT active state)
  await page.screenshot({ path: path.join(outDir, '03_stt_recording_active.png'), fullPage: false });
  console.log('03 saved');

  // Inject transcription text into textarea
  await page.evaluate(() => {
    const textarea = document.querySelector('textarea');
    if (textarea) {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      setter.call(textarea, '教授您好，在邊緣裝置推論優化專案中，我使用了 TensorRT 的 INT8 量化與 ONNX Runtime，成功將整體邊緣影像識別延遲從 120ms 顯著降至 45ms。在量化過程中精準度下降了約 1.5%，我採用 Entropy Calibrator 進行校準以最小化資訊損失。');
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await new Promise(r => setTimeout(r, 600));

  // Screenshot 4: Transcription filled
  await page.screenshot({ path: path.join(outDir, '04_stt_transcription_filled.png'), fullPage: false });
  console.log('04 saved');

  await browser.close();
  console.log('All screenshots saved to', outDir);
})();
