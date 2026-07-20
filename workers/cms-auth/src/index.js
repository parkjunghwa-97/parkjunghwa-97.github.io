// Gift Clean CMS 인증/저장 Worker (PR-A: 로그인, PR-B1: 조회 + dryRun 저장)
//
// PR-A: CMS 로그인 PIN 검증과 짧은 수명의 세션 토큰 발급
// PR-B1: 세션 토큰으로 보호되는 data/*.json 조회(/content)와 저장 사전검증(/save, dryRun-only)
//
// 이 Worker는 아직 실제 GitHub commit을 수행하지 않습니다. /save는 dryRun 모드로만
// 동작하며, 실제 GitHub PUT commit 코드는 PR-B2에서 추가될 예정입니다.
//
// 필요한 Secret (코드에는 절대 값을 넣지 않고 아래 명령으로 등록):
//   wrangler secret put ADMIN_PIN
//   wrangler secret put SESSION_SECRET
// GITHUB_SAVE_TOKEN은 이 PR(B1)에서는 필요하지 않습니다. data/*.json 조회는 공개
// 저장소 읽기 권한만으로 가능하기 때문입니다. 실제 commit이 추가되는 PR-B2에서
// 아래 명령으로 등록할 예정입니다.
//   wrangler secret put GITHUB_SAVE_TOKEN
//
// 환경 변수 (wrangler.toml [vars], 비밀값 아님):
//   ALLOWED_ORIGINS  - 콤마로 구분된 다중 origin 목록
//   GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_BRANCH - 조회 대상 저장소/브랜치

const SESSION_TTL_SECONDS = 60 * 60 * 2; // 세션 토큰 유효 시간: 2시간

// 저장 가능한 데이터 타입 whitelist. PR-B1 기준 banners만 허용합니다.
const SAVE_WHITELIST = {
  banners: 'data/banners.json',
};

// 타입별 필수 필드 규칙 (cms/js/cms.js의 typeConfig.required와 동일하게 유지)
const TYPE_VALIDATION_RULES = {
  banners: { required: ['title', 'description'] },
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const corsHeaders = buildCorsHeaders(request, env);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (url.pathname === '/login' && request.method === 'POST') {
      return handleLogin(request, env, corsHeaders);
    }

    if (url.pathname === '/content' && request.method === 'GET') {
      return handleContent(request, env, corsHeaders);
    }

    if (url.pathname === '/save' && request.method === 'POST') {
      return handleSave(request, env, corsHeaders);
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

async function handleContent(request, env, corsHeaders) {
  const session = await requireSession(request, env);
  if (!session) {
    return jsonResponse({ error: 'invalid_session' }, 401, corsHeaders);
  }

  const url = new URL(request.url);
  const type = url.searchParams.get('type');
  const path = SAVE_WHITELIST[type];
  if (!path) {
    return jsonResponse({ error: 'file_not_allowed' }, 403, corsHeaders);
  }

  let file;
  try {
    file = await fetchGithubFile(path, env);
  } catch (err) {
    return jsonResponse({ error: 'github_api_error', message: String((err && err.message) || err) }, 502, corsHeaders);
  }

  return jsonResponse({ type: type, path: path, sha: file.sha, content: file.content }, 200, corsHeaders);
}

async function handleSave(request, env, corsHeaders) {
  const session = await requireSession(request, env);
  if (!session) {
    return jsonResponse({ error: 'invalid_session' }, 401, corsHeaders);
  }

  let body;
  try {
    body = await request.json();
  } catch (err) {
    return jsonResponse({ error: 'invalid_request' }, 400, corsHeaders);
  }

  const type = body.type;
  const path = SAVE_WHITELIST[type];
  if (!path) {
    return jsonResponse({ error: 'file_not_allowed' }, 403, corsHeaders);
  }

  const validationErrors = validatePayload(type, body.payload);
  if (validationErrors.length) {
    return jsonResponse({ error: 'invalid_payload', details: validationErrors }, 400, corsHeaders);
  }

  let current;
  try {
    current = await fetchGithubFile(path, env);
  } catch (err) {
    return jsonResponse({ error: 'github_api_error', message: String((err && err.message) || err) }, 502, corsHeaders);
  }

  if (!body.expectedSha || body.expectedSha !== current.sha) {
    return jsonResponse({ error: 'sha_conflict', currentSha: current.sha }, 409, corsHeaders);
  }

  if (body.dryRun === false) {
    return jsonResponse({
      error: 'dry_run_only',
      message: 'PR-B1 단계에서는 실제 GitHub commit을 지원하지 않습니다. dryRun:true로만 저장을 검증할 수 있습니다.'
    }, 501, corsHeaders);
  }

  // dryRun:true이거나 dryRun이 생략된 경우, 안전하게 dry-run으로 처리하고 commit은 수행하지 않습니다.
  return jsonResponse({ ok: true, dryRun: true, type: type, path: path, sha: current.sha }, 200, corsHeaders);
}

async function requireSession(request, env) {
  const token = getBearerToken(request);
  if (!token || !env.SESSION_SECRET) {
    return null;
  }
  return verifySessionToken(token, env.SESSION_SECRET);
}

function getBearerToken(request) {
  const header = request.headers.get('Authorization') || '';
  const match = header.match(/^Bearer\s+(.+)$/i);
  return match ? match[1] : null;
}

async function verifySessionToken(token, secret) {
  const parts = token.split('.');
  if (parts.length !== 2) {
    return null;
  }
  const [payloadSegment, signature] = parts;
  const expectedSignature = await signHmac(payloadSegment, secret);
  if (!timingSafeEqual(signature, expectedSignature)) {
    return null;
  }

  let payload;
  try {
    payload = JSON.parse(base64UrlDecodeToString(payloadSegment));
  } catch (err) {
    return null;
  }

  const now = Math.floor(Date.now() / 1000);
  if (!payload || payload.role !== 'admin' || typeof payload.exp !== 'number' || payload.exp <= now) {
    return null;
  }
  return payload;
}

function validatePayload(type, payload) {
  const errors = [];
  if (!Array.isArray(payload)) {
    errors.push('payload는 배열이어야 합니다.');
    return errors;
  }

  const rules = TYPE_VALIDATION_RULES[type];
  if (!rules) {
    errors.push('알 수 없는 type입니다.');
    return errors;
  }

  payload.forEach(function (item, index) {
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      errors.push('index ' + index + ': 객체가 아닙니다.');
      return;
    }
    rules.required.forEach(function (field) {
      const value = item[field];
      if (typeof value !== 'string' || value.trim() === '') {
        errors.push('index ' + index + ': 필수 필드 누락 - ' + field);
      }
    });
  });

  return errors;
}

async function fetchGithubFile(path, env) {
  const owner = env.GITHUB_REPO_OWNER;
  const repo = env.GITHUB_REPO_NAME;
  const branch = env.GITHUB_BRANCH || 'main';
  if (!owner || !repo) {
    throw new Error('GITHUB_REPO_OWNER/GITHUB_REPO_NAME이 설정되지 않았습니다.');
  }

  const apiUrl = 'https://api.github.com/repos/' + owner + '/' + repo + '/contents/' + path + '?ref=' + encodeURIComponent(branch);
  const headers = {
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'giftclean-cms-auth-worker',
  };
  // GITHUB_SAVE_TOKEN은 PR-B1에서는 등록되어 있지 않습니다(공개 저장소 읽기는 토큰 없이 동작).
  // 이후 PR에서 토큰이 등록되면 자동으로 인증된 요청을 사용합니다.
  if (env.GITHUB_SAVE_TOKEN) {
    headers['Authorization'] = 'Bearer ' + env.GITHUB_SAVE_TOKEN;
  }

  const response = await fetch(apiUrl, { headers: headers });
  if (!response.ok) {
    throw new Error('GitHub Contents API 요청 실패: ' + response.status);
  }

  const data = await response.json();
  const decoded = decodeStandardBase64ToString(data.content || '');
  return { sha: data.sha, content: JSON.parse(decoded) };
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

function base64UrlDecodeToString(b64url) {
  const b64 = b64url.replace(/-/g, '+').replace(/_/g, '/');
  const padded = b64 + '='.repeat((4 - (b64.length % 4)) % 4);
  return decodeStandardBase64ToString(padded);
}

function decodeStandardBase64ToString(b64) {
  const clean = b64.replace(/\n/g, '');
  const binary = atob(clean);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new TextDecoder().decode(bytes);
}

function buildCorsHeaders(request, env) {
  const origin = request.headers.get('Origin') || '';
  const allowedList = (env.ALLOWED_ORIGINS || '')
    .split(',')
    .map(function (item) { return item.trim(); })
    .filter(Boolean);
  const isAllowed = allowedList.indexOf(origin) !== -1;

  return {
    'Access-Control-Allow-Origin': isAllowed ? origin : 'null',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Vary': 'Origin',
  };
}

function jsonResponse(data, status, corsHeaders) {
  return new Response(JSON.stringify(data), {
    status,
    headers: Object.assign({ 'Content-Type': 'application/json' }, corsHeaders),
  });
}
