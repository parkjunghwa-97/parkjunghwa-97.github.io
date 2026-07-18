// 네이버 검색광고 API 인증 테스트: 캠페인 목록 조회
// 사용법: node test-connection.js
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const https = require('https');

function loadEnv(file) {
  const env = {};
  const text = fs.readFileSync(file, 'utf8');
  for (const line of text.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const idx = trimmed.indexOf('=');
    if (idx === -1) continue;
    env[trimmed.slice(0, idx).trim()] = trimmed.slice(idx + 1).trim();
  }
  return env;
}

const env = loadEnv(path.join(__dirname, '.env'));
const { NAVER_CUSTOMER_ID, NAVER_API_KEY, NAVER_SECRET_KEY } = env;

if (!NAVER_CUSTOMER_ID || !NAVER_API_KEY || !NAVER_SECRET_KEY) {
  console.error('NAVER_CUSTOMER_ID / NAVER_API_KEY / NAVER_SECRET_KEY 값이 .env에 없습니다.');
  process.exit(1);
}

const method = 'GET';
const uri = '/ncc/campaigns';
const timestamp = Date.now().toString();

const signatureBase = `${timestamp}.${method}.${uri}`;
const signature = crypto
  .createHmac('sha256', NAVER_SECRET_KEY)
  .update(signatureBase)
  .digest('base64');

const options = {
  hostname: 'api.naver.com',
  path: uri,
  method,
  headers: {
    'X-Timestamp': timestamp,
    'X-API-KEY': NAVER_API_KEY,
    'X-Customer': NAVER_CUSTOMER_ID,
    'X-Signature': signature,
  },
};

const req = https.request(options, (res) => {
  let body = '';
  res.on('data', (chunk) => (body += chunk));
  res.on('end', () => {
    console.log('HTTP 상태 코드:', res.statusCode);
    try {
      console.log(JSON.stringify(JSON.parse(body), null, 2));
    } catch {
      console.log(body);
    }
    if (res.statusCode === 200) {
      console.log('\n✅ 인증 성공 — API 키가 정상 작동합니다.');
    } else if (res.statusCode === 401 || res.statusCode === 403) {
      console.log('\n❌ 인증 실패 — CUSTOMER_ID / API_KEY / SECRET_KEY 값을 다시 확인하세요.');
      console.log('   (사진에서 옮겨적은 값이라 0/O, 1/l/I 같은 글자가 잘못 읽혔을 수 있습니다.');
      console.log('    네이버 관리자 화면에서 "복사" 버튼으로 다시 복사해서 .env에 넣어주세요.)');
    }
  });
});

req.on('error', (e) => console.error('요청 실패:', e.message));
req.end();
