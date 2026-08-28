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
    defaultViewport: { width: 1280, height: 900 }
  });
  const page = await browser.newPage();
  const errs = [];
  page.on('console', msg => { if (msg.type() === 'error') errs.push(msg.text()); });
  page.on('pageerror', e => errs.push('PAGE ERR: ' + e.message));

  // 1. Setup Page -> Start Interview
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle2', timeout: 20000 });
  await new Promise(r => setTimeout(r, 1500));

  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const startBtn = btns.find(b => b.textContent.includes('啟動模擬面試艙'));
    if (startBtn) startBtn.click();
  });

  // Wait for 1st question (wait until loading screen clears)
  let q1Text = '';
  for (let i = 0; i < 20; i++) {
    await new Promise(r => setTimeout(r, 1000));
    q1Text = await page.evaluate(() => document.body.innerText);
    if (!q1Text.includes('正在準備題目') && (q1Text.includes('自我介紹') || q1Text.includes('歡迎來到'))) {
      break;
    }
  }

  const hasSelfIntro = q1Text.includes('自我介紹') || q1Text.includes('歡迎來到');
  console.log('Q1 loaded. Contains self intro:', hasSelfIntro);
  const qBoxText = await page.evaluate(() => {
    const el = document.querySelector('.lg\\:col-span-5');
    return el ? el.innerText.slice(0, 200) : '';
  });
  console.log('Question Card Text:', qBoxText);
  await page.screenshot({ path: path.join(outDir, '01_self_intro_q1.png') });

  // 2. Direct Finish -> Wait for Report Page to verify Radar Canvas
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const finishBtn = btns.find(b => b.textContent.includes('直接結束'));
    if (finishBtn) finishBtn.click();
  });

  // Wait for Report Page (after report generation loading screen)
  for (let i = 0; i < 25; i++) {
    await new Promise(r => setTimeout(r, 1000));
    const text = await page.evaluate(() => document.body.innerText);
    if (text.includes('評測診斷報告') && text.includes('核心維度分析')) break;
  }

  await page.evaluate(() => window.scrollTo(0, 250));
  await new Promise(r => setTimeout(r, 1000));

  const canvasState = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return { found: false };
    const ctx = canvas.getContext('2d');
    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    let nonZeroPixels = 0;
    for (let i = 3; i < imgData.data.length; i += 4) {
      if (imgData.data[i] > 0) nonZeroPixels++;
    }
    return {
      found: true,
      width: canvas.width,
      height: canvas.height,
      styleWidth: canvas.style.width,
      styleHeight: canvas.style.height,
      nonZeroPixels
    };
  });
  console.log('Radar Canvas State:', JSON.stringify(canvasState, null, 2));
  await page.screenshot({ path: path.join(outDir, '02_radar_canvas_verified.png') });

  console.log('Errors:', errs);
  await browser.close();
})();
