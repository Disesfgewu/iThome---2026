const http = require('http');

const payload = JSON.stringify({ session_id: 'sess_demo_test' });

// 1. Setup session first
const setupData = JSON.stringify({
  target_school: '逢甲大學',
  target_major: '會計學系/研究所',
  interview_mode: '頂大嚴謹模式'
});

function postJSON(path, data) {
  return new Promise((resolve, reject) => {
    const req = http.request({
      hostname: 'localhost',
      port: 8000,
      path: path,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(body)); } catch (e) { resolve(body); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

(async () => {
  console.log('1. Setting up session...');
  const setupRes = await postJSON('/api/interview/setup', setupData);
  console.log('Session ID:', setupRes.session_id);

  console.log('2. Submitting Q1 answer...');
  await postJSON('/api/interview/answer', JSON.stringify({
    session_id: setupRes.session_id,
    user_answer: '教授您好，我是報考逢甲會計學系/研究所的考生。我曾在學期間修習商業概論與審計學，對財務報表分析非常感興趣，曾擔任社團總幹事負責預算編列與帳務管理。'
  }));

  console.log('3. Requesting evaluation report...');
  const reportRes = await postJSON('/api/reports/generate', JSON.stringify({
    session_id: setupRes.session_id
  }));

  console.log('Report Result:');
  console.log(JSON.stringify(reportRes, null, 2));
})();
