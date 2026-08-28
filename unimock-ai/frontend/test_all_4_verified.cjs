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

  // 1. Setup Page -> Start Interview
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle2', timeout: 20000 });
  await new Promise(r => setTimeout(r, 1500));

  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const startBtn = btns.find(b => b.textContent.includes('啟動模擬面試艙'));
    if (startBtn) startBtn.click();
  });

  // Wait 12 seconds for Q1 loading to finish
  console.log('Waiting 12s for Q1 loading...');
  await new Promise(r => setTimeout(r, 12000));
  await page.screenshot({ path: path.join(outDir, '01_self_intro_q1_clean.png') });
  console.log('Q1 Self Intro Screenshot saved');

  // 2. Direct Finish -> Report Page to verify Radar Canvas Chart
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const finishBtn = btns.find(b => b.textContent.includes('直接結束'));
    if (finishBtn) finishBtn.click();
  });

  // Wait 12 seconds for report page loading to finish
  console.log('Waiting 12s for report generation...');
  await new Promise(r => setTimeout(r, 12000));
  await page.evaluate(() => window.scrollTo(0, 250));
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: path.join(outDir, '02_radar_chart_perfect.png') });
  console.log('Radar Chart Screenshot saved');

  await browser.close();
})();
