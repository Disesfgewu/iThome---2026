const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const outDir = 'C:/Users/marti/Desktop/iThome---2026/days/images/day25';

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: CHROME_PATH,
    args: ['--no-sandbox', '--disable-gpu'],
    defaultViewport: { width: 1280, height: 1000 }
  });
  const page = await browser.newPage();

  // 1. Setup Page -> Start Interview (Graduate School Test: 逢甲大學 會計學研究所)
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle2', timeout: 20000 });
  await new Promise(r => setTimeout(r, 1500));

  await page.evaluate(() => {
    const inputs = document.querySelectorAll('input');
    const select = document.querySelector('select');
    
    if (inputs[0]) {
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
      nativeSetter.call(inputs[0], '逢甲大學');
      inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
    }
    if (select) {
      const nativeSelectSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, "value").set;
      nativeSelectSetter.call(select, '財經學群');
      select.dispatchEvent(new Event('change', { bubbles: true }));
    }
    if (inputs[1]) {
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
      nativeSetter.call(inputs[1], '會計學研究所');
      inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
    }

    const btns = Array.from(document.querySelectorAll('button'));
    const startBtn = btns.find(b => b.textContent.includes('啟動模擬面試艙'));
    if (startBtn) startBtn.click();
  });

  // Wait 12 seconds for Q1
  console.log('Waiting 12s for Q1 loading...');
  await new Promise(r => setTimeout(r, 12000));
  await page.screenshot({ path: path.join(outDir, '01_feng_chia_q1.png') });
  console.log('Q1 screenshot saved');

  // Submit Answer 1
  await page.evaluate(() => {
    const textarea = document.querySelector('textarea');
    if (textarea) {
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
      nativeSetter.call(textarea, '教授您好，我是報考逢甲大學會計學研究所的考生。大學期間我專攻會計學與審計學，並發表過關於企業內部控制與財務報導品質之研究專案。我希望在研究所階段深入探討 ESG 資訊揭露與審計品質的相關課題。');
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
    const btns = Array.from(document.querySelectorAll('button'));
    const submitBtn = btns.find(b => b.textContent.includes('確認送出回答'));
    if (submitBtn) submitBtn.click();
  });

  // Wait 12 seconds for Q2
  console.log('Waiting 12s for Q2 loading...');
  await new Promise(r => setTimeout(r, 12000));
  await page.screenshot({ path: path.join(outDir, '02_feng_chia_q2.png') });
  console.log('Q2 screenshot saved');

  // Direct Finish -> Report Page
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const finishBtn = btns.find(b => b.textContent.includes('直接結束'));
    if (finishBtn) finishBtn.click();
  });

  // Wait 95 seconds for report generation loading (Gemma LLM scoring dual calls complete & page switches)
  console.log('Waiting 95s for report generation...');
  await new Promise(r => setTimeout(r, 95000));

  // Take Report Top screenshot
  await page.screenshot({ path: path.join(outDir, '03_report_top_dynamic.png') });

  // Scroll down for Middle section (Radar, Strengths, Targets)
  await page.evaluate(() => window.scrollTo(0, 450));
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: path.join(outDir, '04_report_middle_strengths_targets.png') });

  // Scroll down for Bottom section (Turn-by-Turn STAR)
  await page.evaluate(() => window.scrollTo(0, 950));
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: path.join(outDir, '05_report_bottom_star_turn_by_turn.png') });

  console.log('All full report screenshots saved!');
  await browser.close();
})();
