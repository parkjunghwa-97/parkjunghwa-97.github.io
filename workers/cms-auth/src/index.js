// Gift Clean CMS 인증 Worker (PR-A)
//
// 이 Worker는 CMS 로그인 PIN 검증과 짧은 수명의 세션 토큰 발급만 담당합니다.
// data/*.json 저장이나 GitHub 커밋 기능은 이 Worker에 포함되어 있지 않습니다.
//
// 필요한 Secret (코드에는 절대 값을 넣지 않고 아래 명령으로 등록):
//   wrangler secret put ADMIN_PIN
//   wrangler secret put SESSION_SECRET
//
// 선택적 환경 변수 (wrangler.toml [vars]):
//   ALLOWED_ORIGIN - CMS가 실제로 서비스되는 origin (예: https://대한청소만세.kr)

const SESSION_TTL_SECONDS = 60 * 60 * 2; // 세션 토큰 유효 시간: 2시간

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const corsHeaders = buildCorsHeaders(env);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (url.pathname === '/login' && request.method === 'POST') {
      return handleLogin(request, env, corsHeaders);
    }

    return jsonResponse({ error: 'not_found' }, 404, corsHeaders);
  },
};

async function handleLogin(request, env, corsHeaders) {
  if (!env.ADMIN_PIN || !env.SESSION_SECRET) {
    return jsonResponse({ error: 'server_not_configured' }, 500, corsHeaders);
  }

  let body;
  try {
    body = await request.json();
  } catch (err) {
    return jsonResponse({ error: 'invalid_request' }, 400, corsHeaders);
  }

  const pin = typeof body.pin === 'string' ? body.pin : '';
  if (!pin || !timingSafeEqual(pin, env.ADMIN_PIN)) {
    return jsonResponse({ error: 'invalid_pin' }, 401, corsHeaders);
  }

  const session = await createSessionToken(env.SESSION_SECRET);
  return jsonResponse({ token: session.token, expiresAt: session.expiresAt }, 200, corsHeaders);
}

async function createSessionToken(secret) {
  const issuedAt = Math.floor(Date.now() / 1000);
  const expiresAt = issuedAt + SESSION_TTL_SECONDS;
  const payload = { role: 'admin', iat: issuedAt, exp: expiresAt };
  const payloadSegment = base64UrlEncodeString(JSON.stringify(payload));
  const signature = await signHmac(payloadSegment, secret);
  return { token: payloadSegment + '.' + signature, expiresAt };
}

async function signHmac(data, secret) {
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const signatureBuffer = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(data));
  return base64UrlEncodeBuffer(signatureBuffer);
}

function timingSafeEqual(a, b) {
  if (a.length !== b.length) {
    return false;
  }
  let result = 0;
  for (let i = 0; i < a.length; i += 1) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}

function base64UrlEncodeString(str) {
  return base64UrlEncodeBuffer(new TextEncoder().encode(str));
}

function base64UrlEncodeBuffer(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function buildCorsHeaders(env) {
  return {
    'Access-Control-Allow-Origin': env.ALLOWED_ORIGIN || '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

function jsonResponse(data, status, corsHeaders) {
  return new Response(JSON.stringify(data), {
    status,
    headers: Object.assign({ 'Content-Type': 'application/json' }, corsHeaders),
  });
}
