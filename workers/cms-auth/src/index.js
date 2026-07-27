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
// PR-F1: sections 외 7개 타입(banners/cases/reviews/prices/faq/notices/services)에
//        공통 저장 무결성 검증(validateArrayIntegrity)을 추가. 기존 id 소실/개수
//        감소/빈 배열 저장을 거부하며, services는 id set이 기존과 정확히 일치해야
//        합니다(추가/삭제 불가). "삭제 저장"은 이번 PR에서 허용하지 않습니다.
// PR-H1a: SAVE_WHITELIST/handleSave에 settings(data/settings.json) 저장을 준비합니다.
//         settings는 배열이 아니라 단일 객체(business-settings-v1 스키마)라서
//         validatePayload/validateArrayIntegrity(둘 다 배열 전제)를 그대로 쓸 수
//         없으므로, 전용 validateSettingsPayload()를 추가하고 INTEGRITY_GUARDED_TYPES/
//         FIXED_ID_SET_TYPES에는 넣지 않습니다. CMS 화면(cms/js/cms.js)은 아직
//         settings를 saveTargetTypes에 연결하지 않았으므로, 이 PR만으로는 실제 저장
//         경로가 열리지 않습니다(화면 연결은 PR-H1b에서 진행).
// PR-H5b: 작업사례(cases) 사진 업로드 전용 엔드포인트(POST /upload-image)를 추가합니다.
//         기존 세션 인증(requireSession)을 그대로 재사용하며, type은 cases만 허용하고
//         caseId는 GitHub의 현재 data/cases.json에 실제로 존재하는 id만 허용합니다.
//         이미지 파일은 uploads/cases/<caseId>-<yyyymmdd>-<8자리 랜덤 hex>.<ext> 경로에
//         별도로 commit되며, data/cases.json은 이 엔드포인트에서 전혀 읽기 외의 방식으로
//         건드리지 않습니다(존재 확인을 위해 읽기만 함). image 필드에 업로드 경로를
//         반영하는 것은 CMS에서 기존 저장 흐름(로컬 저장 → 홈페이지에 저장하기)을 그대로
//         타는 사용자의 다음 동작입니다. 허용 형식은 jpg/jpeg, png, webp만이며 MIME/
//         확장자/매직바이트 3중 검증과 1MB 용량 제한을 적용합니다. 기존 SAVE_WHITELIST/
//         TYPE_VALIDATION_RULES/무결성 검증 로직은 한 글자도 바꾸지 않았습니다.
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

// 저장 가능한 데이터 타입 whitelist. PR-H1a 기준 9개 타입을 허용합니다(settings는
// 서버 저장 준비만 된 상태이며, CMS 화면 연결은 PR-H1b에서 진행합니다).
const SAVE_WHITELIST = {
  banners: 'data/banners.json',
  cases: 'data/cases.json',
  reviews: 'data/reviews.json',
  prices: 'data/prices.json',
  faq: 'data/faq.json',
  notices: 'data/notices.json',
  services: 'data/services.json',
  sections: 'data/sections.json',
  settings: 'data/settings.json',
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

// settings(data/settings.json) 전용 필수 필드 목록(PR-H1a). TYPE_VALIDATION_RULES는
// validatePayload()가 "배열의 각 원소 객체"를 검사하는 것을 전제로 하지만, settings는
// 배열이 아니라 단일 중첩 객체(business-settings-v1)라 같은 틀에 넣을 수 없습니다.
// 그래서 점(.) 경로로 표기한 별도 목록을 두고 validateSettingsPayload()에서
// 직접 사용합니다.
const SETTINGS_REQUIRED_STRING_FIELDS = [
  'schemaVersion',
  'brand.name',
  'brand.legalName',
  'brand.representative',
  'contact.phone',
  'contact.telLink',
  'site.customerSite',
  'site.adminPath',
];
const SETTINGS_REQUIRED_OBJECT_FIELDS = ['brand', 'contact', 'address', 'assets', 'site'];

// sections는 홈페이지 nav의 고정된 9개 섹션과 1:1로 매칭되는 데이터라, 다른 타입과
// 달리 개수/전체 id 목록/타입까지 엄격하게 검증합니다(PR-D1c). 2026-07-22 CMS에서
// 저장 버튼을 눌렀을 때 로컬 캐시가 손상된 1개짜리 payload가 그대로 GitHub에
// 저장되는 사고가 있었고, 이 검증은 그런 payload가 다시는 서버를 통과하지 못하게
// 막기 위한 최후 방어선입니다.
const REQUIRED_SECTION_IDS = ['home', 'about', 'service', 'price', 'portfolio', 'journal', 'policy', 'partner', 'contact'];

// PR-F1: sections 외 7개 타입(banners/cases/reviews/prices/faq/notices/services)에
// 공통 저장 무결성 검증을 추가합니다. 2026-07-22 sections 사고(로컬 캐시 손상으로
// 축소된 payload가 그대로 저장됨)와 동일한 유형의 사고가 이 7개 타입에서도 발생할
// 수 있어, "삭제 저장"을 이번 PR에서는 허용하지 않습니다. 항목을 숨기려면
// visible:false를 쓰고, 개수 감소가 필요한 명시적 삭제 기능은 이후 별도 PR로
// 설계합니다. sections는 이미 validateSectionsPayload()로 별도 검증하므로 이
// 목록에서 제외합니다.
const INTEGRITY_GUARDED_TYPES = ['banners', 'cases', 'reviews', 'prices', 'faq', 'notices', 'services'];
// services는 현재 12개 고정 서비스 상세로 운영 중이라, 추가/삭제 없이 기존 id set과
// 정확히 일치해야만 저장을 허용합니다(내용/visible/sort 수정만 허용).
const FIXED_ID_SET_TYPES = ['services'];

// PR-H5b: 사진 업로드를 허용하는 타입과, 업로드 대상 존재 확인에 쓸 data 파일 경로,
// 실제 이미지가 저장될 폴더입니다. 지금은 cases 하나만 허용합니다(reviews/다른
// 타입은 이후 PR에서 별도로 검토).
const UPLOAD_ALLOWED_TYPES = ['cases'];
const UPLOAD_DATA_PATH_BY_TYPE = { cases: SAVE_WHITELIST.cases };
const UPLOAD_DIR_BY_TYPE = { cases: 'uploads/cases' };

// 업로드 가능한 이미지 형식(jpg/jpeg, png, webp만). svg/gif/html/xml/js 등은 전부
// 거부합니다. MIME 타입, 파일명 확장자, 매직바이트(파일 시그니처) 세 가지가 모두
// 이 목록과 일치해야 업로드를 허용합니다(하나라도 다르면 위장된 파일로 간주해 거부).
const ALLOWED_UPLOAD_MIME_TO_EXT = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
  'image/webp': 'webp',
};
const ALLOWED_UPLOAD_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp'];
// 서버에 실제로 저장하는 파일 최대 용량(1MB). 클라이언트가 이미 축소/압축해서
// 보내지만, 서버에서도 동일한 상한을 강제해 클라이언트 검증을 우회한 요청을 막습니다.
const MAX_UPLOAD_BYTES = 1024 * 1024;

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

    if (url.pathname === '/upload-image' && request.method === 'POST') {
      return handleUploadImage(request, env, corsHeaders);
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

  const validationErrors = type === 'sections'
    ? validateSectionsPayload(body.payload)
    : type === 'settings'
      ? validateSettingsPayload(body.payload)
      : validatePayload(type, body.payload);
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

  // PR-F1: sections 외 7개 타입은 방금 읽은 원격 최신 content와 비교해 "삭제 저장"
  // (기존 id 소실/개수 감소/빈 배열)을 dryRun 여부와 무관하게 거부합니다.
  if (INTEGRITY_GUARDED_TYPES.indexOf(type) !== -1) {
    const integrityErrors = validateArrayIntegrity(type, body.payload, current.content);
    if (integrityErrors.length) {
      return jsonResponse({ error: 'invalid_payload', details: integrityErrors }, 400, corsHeaders);
    }
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

// PR-H5b: 작업사례 사진 업로드. 인증(세션) 필요 → type=cases만 허용 → caseId가 현재
// data/cases.json에 실제 존재하는지 확인 → MIME/확장자/매직바이트/용량 검증 →
// uploads/cases/ 하위에 새 파일로 commit. data/cases.json은 읽기만 하고 절대
// 수정하지 않습니다(image 필드 반영은 CMS의 기존 저장 흐름이 담당).
async function handleUploadImage(request, env, corsHeaders) {
  const session = await requireSession(request, env);
  if (!session) {
    return jsonResponse({ error: 'invalid_session' }, 401, corsHeaders);
  }

  if (!env.GITHUB_SAVE_TOKEN) {
    return jsonResponse({ error: 'save_not_configured' }, 503, corsHeaders);
  }

  let form;
  try {
    form = await request.formData();
  } catch (err) {
    return jsonResponse({ error: 'invalid_request' }, 400, corsHeaders);
  }

  const type = form.get('type');
  if (typeof type !== 'string' || UPLOAD_ALLOWED_TYPES.indexOf(type) === -1) {
    return jsonResponse({ error: 'type_not_allowed' }, 403, corsHeaders);
  }

  const caseIdRaw = form.get('caseId');
  const caseId = typeof caseIdRaw === 'string' ? caseIdRaw.trim() : '';
  if (!caseId) {
    return jsonResponse({ error: 'invalid_case_id' }, 400, corsHeaders);
  }

  const file = form.get('file');
  if (!file || typeof file.arrayBuffer !== 'function') {
    return jsonResponse({ error: 'file_required' }, 400, corsHeaders);
  }

  if (typeof file.size === 'number' && file.size > MAX_UPLOAD_BYTES) {
    return jsonResponse({ error: 'file_too_large', maxBytes: MAX_UPLOAD_BYTES }, 413, corsHeaders);
  }

  let dataFile;
  try {
    dataFile = await fetchGithubFile(UPLOAD_DATA_PATH_BY_TYPE[type], env);
  } catch (err) {
    return jsonResponse({ error: 'github_api_error', message: String((err && err.message) || err) }, 502, corsHeaders);
  }

  const existingIds = getItemIds(dataFile.content);
  if (existingIds.indexOf(caseId) === -1) {
    return jsonResponse({ error: 'case_not_found' }, 404, corsHeaders);
  }

  const declaredMime = typeof file.type === 'string' ? file.type : '';
  const declaredExt = extractExtension(typeof file.name === 'string' ? file.name : '');
  if (!ALLOWED_UPLOAD_MIME_TO_EXT[declaredMime]) {
    return jsonResponse({ error: 'invalid_file_type', reason: 'mime_not_allowed' }, 400, corsHeaders);
  }
  if (ALLOWED_UPLOAD_EXTENSIONS.indexOf(declaredExt) === -1) {
    return jsonResponse({ error: 'invalid_file_type', reason: 'extension_not_allowed' }, 400, corsHeaders);
  }

  const buffer = await file.arrayBuffer();
  if (buffer.byteLength > MAX_UPLOAD_BYTES) {
    return jsonResponse({ error: 'file_too_large', maxBytes: MAX_UPLOAD_BYTES }, 413, corsHeaders);
  }
  const bytes = new Uint8Array(buffer);
  const sniffedMime = sniffImageMimeType(bytes);
  if (!sniffedMime || sniffedMime !== declaredMime) {
    return jsonResponse({ error: 'invalid_file_type', reason: 'magic_bytes_mismatch' }, 400, corsHeaders);
  }

  const ext = ALLOWED_UPLOAD_MIME_TO_EXT[sniffedMime];
  const fileName = buildUploadFileName(caseId, ext);
  const path = UPLOAD_DIR_BY_TYPE[type] + '/' + fileName;
  const message = 'chore(cms): upload case photo ' + fileName;

  let commit;
  try {
    commit = await commitGithubBinaryFile(path, bytes, message, env);
  } catch (err) {
    return jsonResponse({ error: 'github_api_error', message: String((err && err.message) || err) }, 502, corsHeaders);
  }

  return jsonResponse({ ok: true, type: type, caseId: caseId, path: path, commitSha: commit.sha }, 200, corsHeaders);
}

// 원본 파일명 확장자를 소문자로 추출합니다(예: "IMG_1234.JPG" -> "jpg"). 확장자가
// 없으면 빈 문자열을 반환합니다. 저장 경로/파일명 생성에는 절대 쓰지 않고,
// 검증(허용 확장자인지 확인)에만 사용합니다.
function extractExtension(fileName) {
  const match = /\.([a-z0-9]+)$/i.exec(fileName || '');
  return match ? match[1].toLowerCase() : '';
}

// 파일의 첫 바이트(매직바이트/시그니처)로 실제 이미지 형식을 판별합니다. 확장자나
// Content-Type 헤더는 클라이언트가 위조할 수 있으므로, 이 결과가 최종 판단 기준입니다.
function sniffImageMimeType(bytes) {
  if (bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) {
    return 'image/jpeg';
  }
  if (
    bytes.length >= 8 &&
    bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47 &&
    bytes[4] === 0x0d && bytes[5] === 0x0a && bytes[6] === 0x1a && bytes[7] === 0x0a
  ) {
    return 'image/png';
  }
  if (
    bytes.length >= 12 &&
    bytes[0] === 0x52 && bytes[1] === 0x49 && bytes[2] === 0x46 && bytes[3] === 0x46 &&
    bytes[8] === 0x57 && bytes[9] === 0x45 && bytes[10] === 0x42 && bytes[11] === 0x50
  ) {
    return 'image/webp';
  }
  return null;
}

// 저장 파일명은 항상 서버가 새로 생성합니다(원본 파일명은 절대 사용하지 않음).
// caseId-yyyymmdd-8자리랜덤hex.ext 형태라 caseId로 추적 가능하면서도 충돌 위험이
// 거의 없고, 고객 개인정보(이름/주소/전화번호 등)가 파일명에 들어갈 여지가 없습니다.
function buildUploadFileName(caseId, ext) {
  const safeId = (caseId || '').replace(/[^a-zA-Z0-9-]/g, '').slice(0, 40) || 'case';
  const datePart = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const randomPart = randomHexSuffix();
  return safeId + '-' + datePart + '-' + randomPart + '.' + ext;
}

function randomHexSuffix() {
  const bytes = new Uint8Array(4);
  crypto.getRandomValues(bytes);
  return Array.from(bytes).map(function (b) { return b.toString(16).padStart(2, '0'); }).join('');
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

// sections 전용 무결성 검증(PR-D1c). 일반 validatePayload()보다 훨씬 엄격하게,
// 정확히 9개 항목/필수 9개 id 전체 포함/중복 id 없음/visible이 boolean/sort가
// number이고 1~9 범위인지까지 확인합니다. 하나라도 어긋나면 details에 원인을
// 담아 400으로 거부합니다.
function validateSectionsPayload(payload) {
  const errors = [];
  if (!Array.isArray(payload)) {
    errors.push('payload는 배열이어야 합니다.');
    return errors;
  }
  if (payload.length !== REQUIRED_SECTION_IDS.length) {
    errors.push('sections must contain exactly ' + REQUIRED_SECTION_IDS.length + ' items');
  }

  const seenIds = new Set();
  payload.forEach(function (item, index) {
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      errors.push('index ' + index + ': 객체가 아닙니다.');
      return;
    }
    const id = item.id;
    const label = typeof id === 'string' && id ? id : 'index ' + index;

    if (typeof id !== 'string' || id.trim() === '') {
      errors.push('index ' + index + ': 필수 필드 누락 - id');
    } else {
      if (seenIds.has(id)) {
        errors.push('duplicate section id: ' + id);
      }
      seenIds.add(id);
    }

    if (typeof item.name !== 'string' || item.name.trim() === '') {
      errors.push(label + ': 필수 필드 누락 - name');
    }

    if (typeof item.visible !== 'boolean') {
      errors.push(label + ': visible must be boolean');
    }

    if (typeof item.sort !== 'number' || !Number.isFinite(item.sort)) {
      errors.push(label + ': sort must be number');
    } else if (item.sort < 1 || item.sort > REQUIRED_SECTION_IDS.length) {
      errors.push(label + ': sort must be between 1 and ' + REQUIRED_SECTION_IDS.length);
    }
  });

  REQUIRED_SECTION_IDS.forEach(function (requiredId) {
    if (!seenIds.has(requiredId)) {
      errors.push('missing required section id: ' + requiredId);
    }
  });

  return errors;
}

// settings(data/settings.json) 전용 검증(PR-H1a). payload가 배열이 아니라 단일
// 객체라는 점이 다른 8개 타입과의 근본적인 차이입니다. brand/contact/address/
// assets/site가 모두 객체로 존재하는지, 그리고 화면에서 곧바로 쓰일 수 있는 최소
// 필수 문자열 필드(SETTINGS_REQUIRED_STRING_FIELDS)가 채워져 있는지 점(.) 경로로
// 확인합니다. address/assets 내부의 세부 필드(region/street, logo/ogImage 등)까지는
// 이번 PR에서 강제하지 않습니다 - CMS 화면 설계(PR-H1b)에 맞춰 이후 조정합니다.
function validateSettingsPayload(payload) {
  const errors = [];
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    errors.push('payload는 객체여야 합니다.');
    return errors;
  }

  SETTINGS_REQUIRED_OBJECT_FIELDS.forEach(function (key) {
    const value = payload[key];
    if (!value || typeof value !== 'object' || Array.isArray(value)) {
      errors.push('필수 객체 필드 누락 또는 잘못된 타입 - ' + key);
    }
  });

  SETTINGS_REQUIRED_STRING_FIELDS.forEach(function (fieldPath) {
    const value = getNestedValue(payload, fieldPath);
    if (typeof value !== 'string' || value.trim() === '') {
      errors.push('필수 필드 누락 - ' + fieldPath);
    }
  });

  return errors;
}

function getNestedValue(obj, dotPath) {
  return dotPath.split('.').reduce(function (acc, key) {
    return (acc && typeof acc === 'object') ? acc[key] : undefined;
  }, obj);
}

function getItemIds(items) {
  return (Array.isArray(items) ? items : [])
    .filter(function (item) { return item && typeof item === 'object' && typeof item.id === 'string' && item.id.trim() !== ''; })
    .map(function (item) { return item.id; });
}

function findDuplicateIds(ids) {
  const seen = new Set();
  const duplicates = new Set();
  ids.forEach(function (id) {
    if (seen.has(id)) {
      duplicates.add(id);
    }
    seen.add(id);
  });
  return Array.from(duplicates);
}

function findMissingIds(baseIds, otherIds) {
  const otherSet = new Set(otherIds);
  return baseIds.filter(function (id) { return !otherSet.has(id); });
}

// sections 외 7개 타입 공통 저장 무결성 검증(PR-F1). 원격에 이미 존재하는 GitHub
// 파일 content(currentContent)와 이번에 저장하려는 payload를 비교해, "삭제 저장"에
// 해당하는 상태를 400 invalid_payload로 거부합니다. details의 각 항목은
// "reason_code: 설명" 형태라 원인을 바로 확인할 수 있습니다.
//   - empty_array: payload가 빈 배열
//   - missing_id: 문자열 id가 없는 항목 존재
//   - duplicate_id: payload 안에서 id 중복
//   - missing_existing_id: 원격에 있던 id가 payload에서 사라짐(일반 7개 타입)
//   - count_decreased: 원격 대비 항목 수가 줄어듦(일반 7개 타입)
//   - services_id_set_changed: services의 id set이 기존과 정확히 일치하지 않음
//     (누락/신규 추가/개수 변경 전부 이 코드로 보고)
function validateArrayIntegrity(type, payload, currentContent) {
  const errors = [];
  if (!Array.isArray(payload)) {
    errors.push('not_array: payload는 배열이어야 합니다.');
    return errors;
  }
  if (payload.length === 0) {
    errors.push('empty_array: ' + type + ' payload는 빈 배열일 수 없습니다. 항목을 숨기려면 visible:false를 사용하세요.');
    return errors;
  }

  const payloadIds = getItemIds(payload);
  if (payloadIds.length !== payload.length) {
    errors.push('missing_id: 모든 항목에는 문자열 id가 있어야 합니다.');
  }
  findDuplicateIds(payloadIds).forEach(function (id) {
    errors.push('duplicate_id: ' + id);
  });

  const currentList = Array.isArray(currentContent) ? currentContent : [];
  const currentIds = getItemIds(currentList);

  if (FIXED_ID_SET_TYPES.indexOf(type) !== -1) {
    findMissingIds(currentIds, payloadIds).forEach(function (id) {
      errors.push('services_id_set_changed: missing existing id ' + id);
    });
    findMissingIds(payloadIds, currentIds).forEach(function (id) {
      errors.push('services_id_set_changed: unexpected new id ' + id);
    });
    if (payload.length !== currentList.length) {
      errors.push('services_id_set_changed: item count must stay exactly ' + currentIds.length);
    }
  } else {
    findMissingIds(currentIds, payloadIds).forEach(function (id) {
      errors.push('missing_existing_id: ' + id);
    });
    if (payload.length < currentList.length) {
      errors.push('count_decreased: ' + type + ' item count decreased (current: ' + currentList.length + ', payload: ' + payload.length + ')');
    }
  }

  return errors;
}

// payload 안에 유니코드 replacement character(U+FFFD, "�")가 포함되어 있는지 검사합니다.
// 인코딩이 깨진 요청(예: 터미널 인코딩 문제로 한글이 깨져 전송된 경우)을 실제
// commit 이전에 걸러내기 위한 방어 로직입니다. 가능하면 어느 index/field에서
// 발견됐는지 details에 담고, 개별 필드로 특정하지 못하는 경우 payload 전체를
// 대상으로 한 번 더 확인합니다.
// PR-H1a: settings처럼 배열이 아닌 단일 중첩 객체 payload도 검사할 수 있게 객체
// 분기를 추가했습니다. 기존 배열 타입(banners~sections)의 동작/메시지 형식은
// 그대로 유지됩니다 - 배열 분기 로직은 한 글자도 바꾸지 않았습니다.
function findEncodingIssues(payload) {
  const issues = [];

  if (Array.isArray(payload)) {
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
  } else if (payload && typeof payload === 'object') {
    collectEncodingIssuesFromObject(payload, '').forEach(function (issue) {
      issues.push(issue);
    });
  }

  if (!issues.length && JSON.stringify(payload).indexOf('�') !== -1) {
    issues.push('payload 전체에서 손상된 문자(�)가 감지되었습니다.');
  }

  return issues;
}

// findEncodingIssues()의 객체 전용 보조 함수(PR-H1a). settings처럼 중첩된 객체
// 구조를 점(.) 경로로 재귀 탐색하며 문자열 필드에서 U+FFFD를 찾습니다.
function collectEncodingIssuesFromObject(obj, prefix) {
  const issues = [];
  Object.keys(obj).forEach(function (key) {
    const value = obj[key];
    const label = prefix ? prefix + '.' + key : key;
    if (typeof value === 'string') {
      if (value.indexOf('�') !== -1) {
        issues.push(label + ' 필드에 손상된 문자(�) 포함');
      }
    } else if (value && typeof value === 'object' && !Array.isArray(value)) {
      issues.push.apply(issues, collectEncodingIssuesFromObject(value, label));
    }
  });
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

// PR-H5b: JSON 텍스트 commit(commitGithubFile)과 별개로, 이미지 등 바이너리 파일을
// 새 경로에 commit합니다. 항상 신규 파일 생성이 목적이라 sha를 보내지 않습니다
// (같은 경로에 이미 파일이 있으면 GitHub Contents API가 422로 거부합니다 - 파일명에
// 포함된 랜덤 suffix 덕분에 실제로는 거의 발생하지 않습니다).
async function commitGithubBinaryFile(path, bytes, message, env) {
  const owner = env.GITHUB_REPO_OWNER;
  const repo = env.GITHUB_REPO_NAME;
  const branch = env.GITHUB_BRANCH || 'main';
  if (!owner || !repo) {
    throw new Error('GITHUB_REPO_OWNER/GITHUB_REPO_NAME이 설정되지 않았습니다.');
  }

  const contentBase64 = encodeBytesToStandardBase64(bytes);
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

function encodeBytesToStandardBase64(bytes) {
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
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
