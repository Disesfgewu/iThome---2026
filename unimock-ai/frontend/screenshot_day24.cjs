const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const outDir = 'C:/Users/marti/Desktop/iThome---2026/days/images/day24';

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: CHROME_PATH,
    args: ['--no-sandbox', '--disable-gpu'],
    defaultViewport: { width: 1280, height: 800 }
  });
  const page = await browser.newPage();
  const errs = [];
  page.on('console', msg => { if (msg.type() === 'error') errs.push(msg.text()); });
  page.on('pageerror', e => errs.push('PAGE ERR: ' + e.message));

  await page.goto('http://localhost:5173', { waitUntil: 'networkidle2', timeout: 20000 });
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: path.join(outDir, '01_setup_page.png') });
  console.log('01 setup page done');

  // Inject interview state
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
    if (!appFiber) { console.error('App not found'); return; }
    const tabHook = appFiber.memoizedState;
    const sessionHook = tabHook.next;
    sessionHook.queue.dispatch({
      ...sessionHook.memoizedState,
      sessionId: 'sess_day24_demo',
      targetSchool: '國立臺灣大學',
      targetMajor: '資訊工程學系',
      targetGroup: '資訊電機學群',
      isGeneratingQuestion: false,
      questions: [{
        index: 1,
        phase: '破冰自我介紹',
        text: '隨著大型語言模型如 GPT 的普及，許多程式碼編寫工作可以由 AI 完成，你認為在這樣的時代下，學習資訊工程的核心價值是什麼？如何培養不可被 AI 取代的競爭力？',
        hint: '著重思辨與自我反思！'
      }],
      dialogueHistory: []
    });
    tabHook.queue.dispatch('interview');
  });

  await new Promise(r => setTimeout(r, 2500));
  await page.screenshot({ path: path.join(outDir, '02_interview_waveform_standby.png') });
  console.log('02 standby waveform done');

  // Simulate isSpeaking=true via React state injection
  await page.evaluate(() => {
    const allEls = document.querySelectorAll('[class]');
    for (const el of allEls) {
      const key = Object.keys(el).find(k => k.startsWith('__reactFiber'));
      if (!key) continue;
      let current = el[key];
      while (current) {
        if (current.elementType && typeof current.elementType === 'function' && current.elementType.name === 'InterviewPage') {
          // find isSpeaking hook (4th hook: currentIdx, candidateAnswer, isRecording, isSpeaking)
          let h = current.memoizedState; // currentIdx
          h = h.next; // candidateAnswer
          h = h.next; // isRecording
          h = h.next; // isSpeaking
          if (h && h.queue) {
            h.queue.dispatch(true);
            return 'dispatched isSpeaking=true';
          }
        }
        current = current.return;
      }
    }
    return 'not found';
  });

  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({ path: path.join(outDir, '03_interview_waveform_speaking.png') });
  console.log('03 speaking waveform done');

  console.log('Build errors:', errs.length === 0 ? 'none' : errs.join('\n'));
  await browser.close();
})();
