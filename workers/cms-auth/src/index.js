// Gift Clean CMS 인증/저장 Worker (PR-A: 로그인, PR-B1: 조회+dryRun, PR-B2: 실제 commit, PR-B2.1: 저장 방어 로직, PR-B4: 저장 허용 타입 확장, PR-C2a: services 저장 준비, PR-D1a: sections 저장 허용)
//
// PR-A: CMS 로그인 PIN 검증과 짧은 수명의 세션 토큰 발급
// PR-B1: 세션 토큰으로 보호되는 data/*.json 조회(/content)와 저장 사전검증(/save, dryRun-only)
// PR-B2: /save에서 dryRun:false일 때 GitHub Contents API PUT으로 실제 commit 수행
//        (대상은 banners.json 하나로 제한, CMS 프론트엔드는 아직 연결하지 않음)
// PR-B2.1: /save에 두 가지 방어 로직 추가
//   - 인코딩 손상 검사: payload에 U+FFFD(�)가 있으면 dryRun 여부와 무관하게 400 invalid_encoding
//   - 무변경 감지: 현재 GitHub 파일과 payload가 동일하면 dryRun:false에서도 commit을 만들지 않고
//     unchanged:true로 응답 (dryRun:true 응답에도 unchanged 여부를 함께 반환)
// PR-B4: SAVE_WHITELIST/TYPE_VALIDATION_RULES를 banners 외 5개 타입(cases/reviews/prices/faq/notices)으로 확장
//        (CMS 프론트엔드는 아직 연결하지 않음, 나머지 저장 로직은 변경 없음)
// PR-C2a: SAVE_WHITELIST/TYPE_VALIDATION_RULES에 services(data/services.json) 추가.
//         서비스 상세 CMS 화면(PR-C2b)을 붙이기 위한 서버 준비 단계로, CMS 프론트엔드는
//         아직 연결하지 않고 /content, /save(dryRun 포함)만 services type을 허용합니다.
// PR-D1a: SAVE_WHITELIST/TYPE_VALIDATION_RULES에 sections(data/sections.json) 추가.
//         id는 홈페이지 섹션/nav 버튼 매칭 키라 name과 함께 필수 필드로 검증합니다.
//
// 필요한 Secret (코드에는 절대 값을 넣지 않고 아래 명령으로 등록):
//   wrangler secret put ADMIN_PIN
//   wrangler secret put SESSION_SECRET
//   wrangler secret put GITHUB_SAVE_TOKEN
// GITHUB_SAVE_TOKEN이 없으면 dryRun:false 요청은 503 save_not_configured로 거부됩니다.
// /content, /save(dryRun:true)는 공개 저장소 읽기이므로 이 토큰 없이도 동작합니다.
//
// 환경 변수 (wrangler.toml [vars], 비밀값 아님):
//   ALLOWED_ORIGINS  - 콤마로 구분된 다중 origin 목록
//   GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_BRANCH - 조회/commit 대상 저장소/브랜치

const SESSION_TTL_SECONDS = 60 * 60 * 2; // 세션 토큰 유효 시간: 2시간

// 저장 가능한 데이터 타입 whitelist. PR-D1a 기준 8개 타입 전체를 허용합니다.
const SAVE_WHITELIST = {
  banners: 'data/banners.json',
  cases: 'data/cases.json',
  reviews: 'data/reviews.json',
  prices: 'data/prices.json',
  faq: 'data/faq.json',
  notices: 'data/notices.json',
  services: 'data/services.json',
  sections: 'data/sections.json',
};

// 타입별 필수 필드 규칙 (cms/js/cms.js의 typeConfig.required와 동일하게 유지)
// services의 필수 필드는 js/script.js의 isUsableService() 렌더링 조건(visible && service &&
// summary && description)과 맞춰 service/summary/description으로 정합니다. seoTitle/scope/
// process/priceNote/notes/ctaText/id/sort는 선택 필드로 허용됩니다(값이 없어도 저장 가능).
// sections의 id는 홈페이지에서 섹션/nav 버튼을 매칭하는 키이므로, name과 함께 필수로
// 검증합니다(id가 빠진 payload가 저장되면 섹션 ON/OFF 매칭이 깨질 수 있음).
const TYPE_VALIDATION_RULES = {
  banners: { required: ['title', 'description'] },
  cases: { required: ['title', 'description', 'service', 'region'] },
  reviews: { required: ['title', 'content', 'service', 'region'] },
  prices: { required: ['category', 'title', 'price'] },
  faq: { required: ['question', 'answer'] },
  notices: { required: ['title', 'content'] },
  services: { required: ['service', 'summary', 'description'] },
  sections: { required: ['id', 'name'] },
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

  // 인코딩 손상 검사(PR-B2.1): dryRun 여부와 무관하게 항상 적용합니다.
  // dryRun:true로 "저장 가능"이라고 확인받은 뒤 dryRun:false에서만 거부되는
  // 모순을 막기 위해, 마지막 GitHub 쓰기 단계 이전의 모든 검증은 dryRun 값과
  // 무관하게 동일하게 수행합니다.
  const encodingIssues = findEncodingIssues(body.payload);
  if (encodingIssues.length) {
    return jsonResponse({ error: 'invalid_encoding', details: encodingIssues }, 400, corsHeaders);
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

  const unchanged = deepEqualIgnoringKeyOrder(body.payload, current.content);

  if (body.dryRun === false) {
    if (unchanged) {
      // 내용이 실제로 같으면 쓰기 권한(GITHUB_SAVE_TOKEN)이 없어도 성공으로 처리합니다.
      // 아무것도 쓰지 않으므로 토큰이 필요하지 않습니다.
      return jsonResponse({ ok: true, unchanged: true, dryRun: false, type: type, path: path, sha: current.sha }, 200, corsHeaders);
    }

    if (!env.GITHUB_SAVE_TOKEN) {
      return jsonResponse({ error: 'save_not_configured' }, 503, corsHeaders);
    }

    let commit;
    try {
      commit = await commitGithubFile(path, body.payload, current.sha, env);
    } catch (err) {
      return jsonResponse({ error: 'github_api_error', message: String((err && err.message) || err) }, 502, corsHeaders);
    }

    return jsonResponse({
      ok: true,
      unchanged: false,
      dryRun: false,
      type: type,
      path: path,
      commitSha: commit.sha,
      commitUrl: commit.htmlUrl
    }, 200, corsHeaders);
  }

  // dryRun:true이거나 dryRun이 생략된 경우, 안전하게 dry-run으로 처리하고 commit은 수행하지 않습니다.
  return jsonResponse({ ok: true, dryRun: true, unchanged: unchanged, type: type, path: path, sha: current.sha }, 200, corsHeaders);
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

// payload 안에 유니코드 replacement character(U+FFFD, "�")가 포함되어 있는지 검사합니다.
// 인코딩이 깨진 요청(예: 터미널 인코딩 문제로 한글이 깨져 전송된 경우)을 실제
// commit 이전에 걸러내기 위한 방어 로직입니다. 가능하면 어느 index/field에서
// 발견됐는지 details에 담고, 개별 필드로 특정하지 못하는 경우 payload 전체를
// 대상으로 한 번 더 확인합니다.
function findEncodingIssues(payload) {
  const issues = [];
  if (!Array.isArray(payload)) {
    return issues;
  }

  payload.forEach(function (item, index) {
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      return;
    }
    Object.keys(item).forEach(function (field) {
      const value = item[field];
      if (typeof value === 'string' && value.indexOf('�') !== -1) {
        issues.push('index ' + index + ': ' + field + ' 필드에 손상된 문자(�) 포함');
      }
    });
  });

  if (!issues.length && JSON.stringify(payload).indexOf('�') !== -1) {
    issues.push('payload 전체에서 손상된 문자(�)가 감지되었습니다.');
  }

  return issues;
}

// 두 값이 "의미상" 동일한지 비교합니다. 객체는 key 순서를 무시하고 값만
// 비교하며, 배열은 순서를 그대로 유지한 채 원소별로 비교합니다.
function deepEqualIgnoringKeyOrder(a, b) {
  if (a === b) {
    return true;
  }
  if (a === null || b === null || a === undefined || b === undefined) {
    return a === b;
  }
  if (Array.isArray(a) || Array.isArray(b)) {
    if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) {
      return false;
    }
    for (let i = 0; i < a.length; i += 1) {
      if (!deepEqualIgnoringKeyOrder(a[i], b[i])) {
        return false;
      }
    }
    return true;
  }
  if (typeof a === 'object' && typeof b === 'object') {
    const aKeys = Object.keys(a).sort();
    const bKeys = Object.keys(b).sort();
    if (aKeys.length !== bKeys.length) {
      return false;
    }
    for (let i = 0; i < aKeys.length; i += 1) {
      if (aKeys[i] !== bKeys[i]) {
        return false;
      }
    }
    return aKeys.every(function (key) {
      return deepEqualIgnoringKeyOrder(a[key], b[key]);
    });
  }
  return false;
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
  // 조회는 공개 저장소 읽기이므로 토큰 없이도 동작합니다. 토큰이 등록되어 있으면
  // (PR-B2부터) 자동으로 인증된 요청을 사용합니다.
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

async function commitGithubFile(path, payload, sha, env) {
  const owner = env.GITHUB_REPO_OWNER;
  const repo = env.GITHUB_REPO_NAME;
  const branch = env.GITHUB_BRANCH || 'main';
  if (!owner || !repo) {
    throw new Error('GITHUB_REPO_OWNER/GITHUB_REPO_NAME이 설정되지 않았습니다.');
  }

  const jsonText = JSON.stringify(payload, null, 2) + '\n';
  const contentBase64 = encodeStringToStandardBase64(jsonText);
  const fileName = path.split('/').pop();
  const message = 'chore(cms): update ' + fileName + ' data from CMS\n\nSaved via Gift Clean CMS at ' + new Date().toISOString();

  const apiUrl = 'https://api.github.com/repos/' + owner + '/' + repo + '/contents/' + path;
  const response = await fetch(apiUrl, {
    method: 'PUT',
    headers: {
      'Accept': 'application/vnd.github+json',
      'User-Agent': 'giftclean-cms-auth-worker',
      'Authorization': 'Bearer ' + env.GITHUB_SAVE_TOKEN,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      content: contentBase64,
      sha: sha,
      branch: branch,
    }),
  });

  if (!response.ok) {
    throw new Error('GitHub Contents API PUT 실패: ' + response.status);
  }

  const data = await response.json();
  const commitInfo = (data && data.commit) || {};
  return { sha: commitInfo.sha, htmlUrl: commitInfo.html_url };
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

function encodeStringToStandardBase64(str) {
  const bytes = new TextEncoder().encode(str);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
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
