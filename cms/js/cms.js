(function(){
  // 배포된 Cloudflare Worker 주소를 입력하세요. 예: https://giftclean-cms-auth.<subdomain>.workers.dev
  const CMS_AUTH_WORKER_URL = 'https://giftclean-cms-auth.giftclean-cms.workers.dev';
  const SESSION_KEY = 'daehanCmsSession';
  const LOCK_KEY = 'daehanCmsLock';
  const DATA_KEY = 'daehanCmsDraftData';
  const FORM_DRAFT_KEY = 'daehanCmsFormDrafts';
  const MAX_ATTEMPTS = 5;
  const LOCK_MINUTES = 10;
  const UNDO_DELETE_MS = 5000;
  const INITIAL_RENDER_LIMIT = 80;
  const RENDER_CHUNK = 80;
  const SEARCH_RESULT_LIMIT = 40;
  const DRAFT_SAVE_DELAY = 500;
  const JSON_PREVIEW_LIMIT = 3600;

  const serviceOptions = ['특수청소', '쓰레기집청소', '유품정리', '화재복구', '누수복구', '비둘기퇴치', '입주청소'];
  // sections는 PR-D1a부터 Worker의 SAVE_WHITELIST에 등록되어 saveTargetTypes에도
  // 포함합니다. 다른 7개 타입과 동일하게 refreshRemoteContent 백그라운드 sha 조회,
  // JSON 관리 화면의 저장 대상 미리보기에도 자동으로 포함됩니다.
  const contentTypes = ['cases', 'reviews', 'prices', 'faq', 'notices', 'banners', 'services', 'sections'];
  const saveTargetTypes = ['reviews', 'cases', 'prices', 'faq', 'notices', 'banners', 'services', 'sections'];
  // PR-F1: sections 외 7개 타입의 저장 무결성 방어 대상. 이 목록에 있는 타입은
  // 저장 버튼 클릭 시 saveTypeToRemote() 호출 전에 원격 최신 데이터와 비교해
  // "기존 id 소실/개수 감소/빈 배열" 상태의 저장을 차단합니다(Worker에도 동일한
  // 검증이 있어 이중 방어입니다). sections는 이미 자체 검증(validateSectionsForSave)이
  // 있어 이 목록에서 제외합니다.
  const INTEGRITY_GUARDED_TYPES = ['banners', 'cases', 'reviews', 'prices', 'faq', 'notices', 'services'];
  // services는 현재 12개 고정 서비스 상세로 운영 중이라, 추가/삭제 없이 기존
  // id set과 정확히 일치해야만 저장을 허용합니다.
  const FIXED_ID_SET_TYPES = ['services'];
  const typeConfig = {
    reviews: {
      file: 'reviews.json',
      prefix: 'review',
      label: '고객후기',
      fields: ['id', 'service', 'region', 'title', 'rating', 'content', 'image', 'source', 'date', 'visible', 'sort'],
      required: ['title', 'content', 'service', 'region']
    },
    cases: {
      file: 'cases.json',
      prefix: 'case',
      label: '작업사례',
      fields: ['id', 'service', 'region', 'title', 'description', 'image', 'date', 'featured', 'visible', 'sort'],
      required: ['title', 'description', 'service', 'region']
    },
    prices: {
      file: 'prices.json',
      prefix: 'price',
      label: '비용안내',
      fields: ['id', 'category', 'title', 'price', 'description', 'visible', 'sort'],
      required: ['category', 'title', 'price']
    },
    faq: {
      file: 'faq.json',
      prefix: 'faq',
      label: 'FAQ',
      fields: ['id', 'question', 'answer', 'visible', 'sort'],
      required: ['question', 'answer']
    },
    notices: {
      file: 'notices.json',
      prefix: 'notice',
      label: '공지',
      fields: ['id', 'title', 'content', 'date', 'visible', 'sort'],
      required: ['title', 'content']
    },
    banners: {
      file: 'banners.json',
      prefix: 'banner',
      label: '메인배너',
      fields: ['id', 'title', 'description', 'button', 'link', 'visible', 'sort'],
      required: ['title', 'description']
    },
    services: {
      file: 'services.json',
      prefix: 'service',
      label: '서비스 상세',
      fields: ['id', 'service', 'seoTitle', 'summary', 'description', 'scope', 'process', 'priceNote', 'notes', 'ctaText', 'visible', 'sort'],
      required: ['service', 'summary', 'description']
    },
    sections: {
      file: 'sections.json',
      prefix: 'section',
      label: '섹션 표시',
      fields: ['id', 'name', 'visible', 'sort'],
      required: ['name']
    }
  };
  // 홈페이지 data/*.json이 실제로 사용하는 필드만 담은 저장 허용 목록입니다.
  // typeConfig[type].fields는 CMS 편집 화면 표시용(visible/sort 입력창 등
  // CMS 내부 필드 포함)이라 그대로 쓰면 안 되고, GitHub 저장 payload는 이
  // 목록으로만 구성합니다(PR-B6).
  const REMOTE_SAVE_FIELDS = {
    banners: ['id', 'title', 'description', 'button', 'link', 'visible', 'sort'],
    cases: ['id', 'service', 'region', 'title', 'description', 'image', 'date', 'featured'],
    reviews: ['id', 'service', 'region', 'title', 'rating', 'content', 'source', 'date'],
    prices: ['id', 'category', 'title', 'price', 'description', 'visible', 'sort'],
    faq: ['id', 'question', 'answer', 'visible', 'sort'],
    notices: ['id', 'title', 'content', 'date', 'visible', 'sort'],
    // services는 CMS 편집 필드와 data/services.json 저장 필드가 완전히 동일합니다(PR-C2b).
    services: ['id', 'service', 'seoTitle', 'summary', 'description', 'scope', 'process', 'priceNote', 'notes', 'ctaText', 'visible', 'sort'],
    // sections도 CMS 편집 필드와 data/sections.json 저장 필드가 동일합니다(PR-D1b).
    sections: ['id', 'name', 'visible', 'sort']
  };

  const fallbackData = {
    cases: [
      {
        id: 'case-001',
        service: '특수청소',
        region: '서울 강서구',
        title: '특수청소 작업사례',
        description: '생활 폐기물 정리와 바닥 살균을 함께 진행한 작업사례입니다.',
        image: '',
        date: '2026-07-01',
        featured: true,
        visible: true,
        sort: 1
      },
      {
        id: 'case-002',
        service: '누수복구',
        region: '경기 남양주',
        title: '누수복구 작업사례',
        description: '누수 이후 오염 구역 정리와 건조 상담을 진행한 샘플 작업사례입니다.',
        image: '',
        date: '2026-07-01',
        featured: false,
        visible: true,
        sort: 2
      }
    ],
    reviews: [
      {
        id: 'review-001',
        service: '유품정리',
        region: '인천',
        title: '유품정리 고객 후기',
        rating: 5,
        content: '상담부터 정리까지 차분하게 안내해주셔서 큰 도움이 됐습니다.',
        source: '고객 상담 후기',
        date: '2026-07-01',
        visible: true,
        sort: 1
      },
      {
        id: 'review-002',
        service: '쓰레기집청소',
        region: '경기',
        title: '쓰레기집 청소 고객 후기',
        rating: 5,
        content: '사진으로 진행 상황을 공유해주셔서 믿고 맡길 수 있었습니다.',
        source: '고객 상담 후기',
        date: '2026-07-01',
        visible: true,
        sort: 2
      }
    ],
    prices: [
      {
        id: 'price-001',
        category: '특수청소 · 유품정리',
        title: '오염 범위 · 악취 · 폐기물',
        price: '상담 후 안내',
        description: '오염도, 폐기물 양, 작업 인원, 장비 투입 여부에 따라 안내합니다.',
        visible: true,
        sort: 1
      },
      {
        id: 'price-002',
        category: '입주청소',
        title: '원룸 · 1.5룸 · 투룸',
        price: '사진 확인 후 안내',
        description: '평수와 오염도, 짐 유무에 따라 안내합니다.',
        visible: true,
        sort: 2
      }
    ],
    faq: [
      {
        id: 'faq-001',
        question: '당일 상담이 가능한가요?',
        answer: '가능한 일정은 현장 위치와 작업 범위를 확인한 뒤 안내합니다.',
        visible: true,
        sort: 1
      },
      {
        id: 'faq-002',
        question: '보험 제출 서류 상담도 가능한가요?',
        answer: '화재복구, 누수복구 등 보험 접수가 필요한 현장은 상담 시 서류 발급 가능 여부를 함께 안내합니다.',
        visible: true,
        sort: 2
      }
    ],
    notices: [
      {
        id: 'notice-001',
        title: '상담 안내',
        content: '전화 또는 카카오톡으로 바로 상담 가능합니다. 현장 사진이나 영상을 보내주시면 예상 견적 안내가 더 빠릅니다.',
        date: '2026-07-07',
        visible: true,
        sort: 1
      }
    ],
    banners: [
      {
        id: 'banner-001',
        title: '사진 없이도 먼저 상담 가능합니다.',
        description: '현장 상태를 말씀해주시면 가능한 작업 여부부터 안내드립니다.',
        button: '카카오톡 상담',
        link: '#contact',
        visible: true,
        sort: 1
      }
    ],
    // data/services.json은 same-origin 정적 파일 fetch로 항상 실제 내용을 불러오므로
    // 이 fallback은 네트워크 오류 등 예외 상황에서만 쓰이는 최소 placeholder입니다.
    services: [
      {
        id: 'service-001',
        service: '',
        seoTitle: '',
        summary: '',
        description: '',
        scope: '',
        process: '',
        priceNote: '',
        notes: '',
        ctaText: '',
        visible: true,
        sort: 1
      }
    ],
    // data/sections.json도 same-origin 정적 파일 fetch로 실제 내용을 불러오며,
    // 이 fallback은 네트워크 오류 등 예외 상황에서만 쓰이는 최소 placeholder입니다.
    sections: [
      { id: 'home', name: '홈', visible: true, sort: 1 }
    ],
    settings: {
      cmsVersion: '1.7',
      initialPin: '231204',
      dataMode: 'localStorage',
      customerSite: 'https://xn--vk1by2k4ygtjy88bcjm.kr/',
      adminPath: '/cms/',
      nextStep: 'V2 GitHub 자동 커밋/배포 연결'
    }
  };

  const dataFiles = {
    reviews: '../data/reviews.json',
    cases: '../data/cases.json',
    prices: '../data/prices.json',
    faq: '../data/faq.json',
    notices: '../data/notices.json',
    banners: '../data/banners.json',
    services: '../data/services.json',
    sections: '../data/sections.json'
  };

  const titles = {
    cases: '작업사례 관리',
    reviews: '고객후기 관리',
    prices: '비용안내 관리',
    faq: 'FAQ 관리',
    notices: '공지 관리',
    banners: '메인배너 관리',
    services: '서비스 상세 관리',
    sections: '섹션 표시 관리',
    json: 'JSON 관리',
    settings: '설정'
  };

  const editorTitles = {
    cases: '작업사례',
    reviews: '고객후기',
    prices: '비용안내',
    faq: 'FAQ',
    notices: '공지',
    banners: '메인배너',
    services: '서비스 상세',
    sections: '섹션'
  };

  let cmsData = {};
  let activePhotoData = [];
  let activeScreen = 'cases';
  let pendingDelete = null;
  let undoDelete = null;
  let undoTimer = 0;
  let draftTimer = 0;
  let searchTimer = 0;
  let activeDraftContext = null;
  let visibleCounts = {};
  let remoteShaByType = {};
  // PR-F1: 저장 전 무결성 검증(existing id 유지/개수 감소 방지)을 위해,
  // refreshRemoteContent()가 받아온 원격 배열도 함께 캐시해둡니다.
  let remoteContentByType = {};

  document.addEventListener('DOMContentLoaded', function(){
    installUxChrome();
    bindLogin();
    bindNavigation();
    bindPreview();
    bindCrudActions();
    bindSettingsActions();

    if(hasValidSession()){
      showApp();
    }
  });

  function hasValidSession(){
    try {
      const raw = sessionStorage.getItem(SESSION_KEY);
      if(!raw){
        return false;
      }
      const session = JSON.parse(raw);
      if(!session || !session.token || !session.expiresAt){
        return false;
      }
      if(Date.now() / 1000 >= session.expiresAt){
        sessionStorage.removeItem(SESSION_KEY);
        return false;
      }
      return true;
    } catch(e){
      sessionStorage.removeItem(SESSION_KEY);
      return false;
    }
  }

  function getSessionToken(){
    try {
      const raw = sessionStorage.getItem(SESSION_KEY);
      if(!raw){
        return null;
      }
      const session = JSON.parse(raw);
      return (session && session.token) || null;
    } catch(e){
      return null;
    }
  }

  function handleExpiredSession(){
    sessionStorage.removeItem(SESSION_KEY);
    document.getElementById('appView').classList.add('is-hidden');
    document.getElementById('loginView').classList.remove('is-hidden');
    const message = document.getElementById('loginMessage');
    if(message){
      message.textContent = '로그인이 만료되었습니다. 다시 로그인해주세요.';
    }
  }

  // 각 타입(banners/cases/reviews/prices/faq/notices)의 GitHub 최신 sha를
  // 백그라운드로 확보합니다. 화면에 보이는 cmsData[type]은 절대 덮어쓰지 않고,
  // remoteShaByType만 갱신합니다. CMS_AUTH_WORKER_URL이 비어있거나 세션이
  // 없거나 요청이 실패해도 화면 동작에는 영향을 주지 않습니다(다음 저장 시도
  // 때 다시 시도됩니다).
  async function refreshRemoteContent(type){
    if(!CMS_AUTH_WORKER_URL){
      return null;
    }
    const token = getSessionToken();
    if(!token){
      return null;
    }
    try {
      const response = await fetch(CMS_AUTH_WORKER_URL + '/content?type=' + encodeURIComponent(type), {
        headers: { Authorization: 'Bearer ' + token }
      });
      if(response.status === 401){
        handleExpiredSession();
        return null;
      }
      if(!response.ok){
        return null;
      }
      const data = await response.json();
      if(data && data.sha){
        remoteShaByType[type] = data.sha;
      }
      if(data && Array.isArray(data.content)){
        remoteContentByType[type] = data.content;
      }
      return data;
    } catch(e){
      return null;
    }
  }

  // GitHub로 실제 저장하기 직전에, 화면/localStorage에는 있는 CMS 내부
  // 필드(예: cases/reviews의 visible/sort)를 제거하고 홈페이지 data/*.json이
  // 실제로 쓰는 필드만 남깁니다. cmsData 자체나 localStorage는 건드리지
  // 않고, 전송용 배열을 새로 만들어 반환합니다(PR-B6).
  function normalizePayloadForRemote(type, payload){
    const allowedFields = REMOTE_SAVE_FIELDS[type];
    if(!allowedFields || !Array.isArray(payload)){
      return payload;
    }
    return payload.map(function(item){
      const normalized = {};
      allowedFields.forEach(function(field){
        normalized[field] = item && item[field] !== undefined ? item[field] : '';
      });
      // reviews.image는 홈페이지가 선택적으로 지원하지만 실제 data/reviews.json에는
      // 아직 없는 필드라, 값이 있을 때만 포함하고 없으면 키 자체를 만들지 않습니다.
      if(type === 'reviews'){
        const image = item && item.image;
        if(image !== undefined && image !== null && image !== ''){
          normalized.image = image;
        }
      }
      return normalized;
    });
  }

  async function saveTypeToRemote(type, button){
    if(!CMS_AUTH_WORKER_URL){
      showToast('Worker 주소가 설정되지 않았습니다.');
      return;
    }
    const token = getSessionToken();
    if(!token){
      handleExpiredSession();
      return;
    }

    const config = typeConfig[type];
    const fileName = config ? config.file : type + '.json';

    // 저장 직전에 sha를 다시 확보해 확인창을 띄우는 시점과 실제 저장 시점 사이의
    // 간격을 최소화합니다.
    await refreshRemoteContent(type);
    if(!remoteShaByType[type]){
      showToast('최신 데이터를 불러오지 못해 저장할 수 없습니다. 다시 시도해주세요.');
      return;
    }

    const confirmed = window.confirm(fileName + '을 실제 홈페이지에 저장하시겠습니까?\n저장 후 약 1~2분 뒤 홈페이지에 반영됩니다.');
    if(!confirmed){
      return;
    }

    if(button){
      button.disabled = true;
    }

    try {
      const response = await fetch(CMS_AUTH_WORKER_URL + '/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
        body: JSON.stringify({
          type: type,
          payload: normalizePayloadForRemote(type, cmsData[type] || []),
          expectedSha: remoteShaByType[type],
          dryRun: false
        })
      });

      const data = await response.json().catch(function(){ return {}; });

      if(response.status === 401){
        handleExpiredSession();
        return;
      }
      if(response.status === 400 && data.error === 'invalid_encoding'){
        showToast('문자 인코딩 오류로 저장이 차단되었습니다. 새로고침 후 다시 입력해주세요.');
        setStatus('문자 인코딩 오류로 저장이 차단되었습니다. 새로고침 후 다시 입력해주세요.');
        return;
      }
      if(response.status === 409 && data.error === 'sha_conflict'){
        // 화면 내용(cmsData[type])과 localStorage는 그대로 유지하고, sha만 갱신합니다.
        await refreshRemoteContent(type);
        const message = '다른 변경사항이 먼저 저장되었습니다. 현재 편집 내용은 유지했습니다. 다시 저장하면 현재 화면 내용으로 홈페이지에 저장됩니다.';
        showToast(message);
        setStatus(message);
        return;
      }
      if(response.status === 503 && data.error === 'save_not_configured'){
        showToast('저장 기능이 아직 서버에 설정되지 않았습니다.');
        setStatus('저장 기능이 아직 서버에 설정되지 않았습니다.');
        return;
      }
      if(!response.ok || !data.ok){
        showToast('저장에 실패했습니다. 잠시 후 다시 시도하세요.');
        setStatus('저장에 실패했습니다. 잠시 후 다시 시도하세요.');
        return;
      }

      const message = data.unchanged ? '변경사항이 없습니다' : '저장 완료';
      showToast(message);
      setStatus(message);

      // 저장 성공(또는 무변경) 후에도 화면 내용과 localStorage는 그대로 두고 sha만 갱신합니다.
      await refreshRemoteContent(type);
    } catch(e){
      showToast('저장 서버에 연결할 수 없습니다. 잠시 후 다시 시도하세요.');
      setStatus('저장 서버에 연결할 수 없습니다. 잠시 후 다시 시도하세요.');
    } finally {
      if(button){
        button.disabled = false;
      }
    }
  }

  function installUxChrome(){
    installSearch();
    installToastContainer();
    installConfirmModal();
    installDraftModal();
  }

  function installSearch(){
    const header = document.querySelector('.workspace-header');
    const status = document.getElementById('loadStatus');
    if(!header || !status || document.getElementById('globalSearch')){
      return;
    }

    const tools = document.createElement('div');
    tools.className = 'header-tools';

    const label = document.createElement('label');
    label.className = 'search-box';
    label.setAttribute('for', 'globalSearch');
    const labelText = document.createElement('span');
    labelText.textContent = '검색';
    const input = document.createElement('input');
    input.id = 'globalSearch';
    input.type = 'search';
    input.placeholder = '후기, 작업사례, FAQ, 가격, 공지 검색';
    label.appendChild(labelText);
    label.appendChild(input);

    const panel = document.createElement('section');
    panel.id = 'searchPanel';
    panel.className = 'search-panel is-hidden';
    panel.setAttribute('aria-live', 'polite');

    tools.appendChild(label);
    tools.appendChild(status);
    header.appendChild(tools);
    header.insertAdjacentElement('afterend', panel);

    input.addEventListener('input', function(){
      clearTimeout(searchTimer);
      searchTimer = setTimeout(function(){
        renderSearchResults(input.value);
      }, 80);
    });
  }

  function installToastContainer(){
    if(document.getElementById('toastContainer')){
      return;
    }
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    container.setAttribute('aria-live', 'polite');
    container.setAttribute('aria-atomic', 'true');
    document.body.appendChild(container);
  }

  function installConfirmModal(){
    if(document.getElementById('confirmModal')){
      return;
    }
    const modal = document.createElement('section');
    modal.id = 'confirmModal';
    modal.className = 'modal-backdrop is-hidden';
    modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML = '<div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="confirmTitle"><h2 id="confirmTitle">정말 삭제하시겠습니까?</h2><p id="confirmMessage">삭제 후 5초 동안 되돌릴 수 있습니다.</p><div class="modal-actions"><button class="secondary-btn" type="button" id="confirmCancelButton">취소</button><button class="danger-btn" type="button" id="confirmDeleteButton">삭제</button></div></div>';
    document.body.appendChild(modal);

    document.getElementById('confirmCancelButton').addEventListener('click', closeConfirmModal);
    document.getElementById('confirmDeleteButton').addEventListener('click', confirmDelete);
  }

  function installDraftModal(){
    if(document.getElementById('draftModal')){
      return;
    }
    const modal = document.createElement('section');
    modal.id = 'draftModal';
    modal.className = 'modal-backdrop is-hidden';
    modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML = '<div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="draftTitle"><h2 id="draftTitle">임시저장된 내용이 있습니다</h2><p>새로고침 전에 작성하던 내용을 복구할까요?</p><div class="modal-actions"><button class="secondary-btn" type="button" id="draftLaterButton">나중에</button><button class="danger-btn" type="button" id="draftDiscardButton">삭제</button><button type="button" id="draftRestoreButton">복구</button></div></div>';
    document.body.appendChild(modal);

    document.getElementById('draftLaterButton').addEventListener('click', closeDraftModal);
    document.getElementById('draftDiscardButton').addEventListener('click', discardActiveDraft);
    document.getElementById('draftRestoreButton').addEventListener('click', restoreActiveDraft);
  }

  function bindLogin(){
    const form = document.getElementById('loginForm');
    const input = document.getElementById('pinInput');
    const message = document.getElementById('loginMessage');

    form.addEventListener('submit', function(event){
      event.preventDefault();
      const lock = getLockState();
      if(lock.locked){
        message.textContent = remainingLockText(lock.until);
        return;
      }

      if(!CMS_AUTH_WORKER_URL){
        message.textContent = 'Worker 주소가 설정되지 않았습니다. cms.js 상단의 CMS_AUTH_WORKER_URL을 확인하세요.';
        return;
      }

      const submitButton = form.querySelector('button[type="submit"]');
      if(submitButton){
        submitButton.disabled = true;
      }
      message.textContent = '로그인 확인 중...';

      fetch(CMS_AUTH_WORKER_URL + '/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pin: input.value })
      }).then(function(response){
        return response.json().catch(function(){ return {}; }).then(function(data){
          return { ok: response.ok, data: data };
        });
      }).then(function(result){
        if(submitButton){
          submitButton.disabled = false;
        }
        if(result.ok && result.data && result.data.token && result.data.expiresAt){
          localStorage.removeItem(LOCK_KEY);
          sessionStorage.setItem(SESSION_KEY, JSON.stringify({ token: result.data.token, expiresAt: result.data.expiresAt }));
          input.value = '';
          message.textContent = '';
          showApp();
          return;
        }
        registerFailedAttempt(message);
      }).catch(function(){
        if(submitButton){
          submitButton.disabled = false;
        }
        message.textContent = '로그인 서버에 연결할 수 없습니다. 잠시 후 다시 시도하세요.';
      });
    });
  }

  function registerFailedAttempt(message){
    const lock = getLockState();
    const nextAttempts = lock.attempts + 1;
    const lockData = {
      attempts: nextAttempts,
      until: nextAttempts >= MAX_ATTEMPTS ? Date.now() + LOCK_MINUTES * 60 * 1000 : 0
    };
    localStorage.setItem(LOCK_KEY, JSON.stringify(lockData));
    message.textContent = nextAttempts >= MAX_ATTEMPTS ? remainingLockText(lockData.until) : 'PIN이 일치하지 않습니다. 남은 시도: ' + (MAX_ATTEMPTS - nextAttempts);
  }

  function getLockState(){
    try {
      const saved = JSON.parse(localStorage.getItem(LOCK_KEY) || '{}');
      if(saved.until && saved.until > Date.now()){
        return { locked: true, attempts: saved.attempts || MAX_ATTEMPTS, until: saved.until };
      }
      if(saved.until && saved.until <= Date.now()){
        localStorage.removeItem(LOCK_KEY);
        return { locked: false, attempts: 0, until: 0 };
      }
      return { locked: false, attempts: saved.attempts || 0, until: 0 };
    } catch(error) {
      localStorage.removeItem(LOCK_KEY);
      return { locked: false, attempts: 0, until: 0 };
    }
  }

  function remainingLockText(until){
    const seconds = Math.max(0, Math.ceil((until - Date.now()) / 1000));
    const minutes = Math.ceil(seconds / 60);
    return '로그인이 잠겼습니다. 약 ' + minutes + '분 후 다시 시도하세요.';
  }

  function bindNavigation(){
    document.querySelectorAll('.menu-btn').forEach(function(button){
      button.addEventListener('click', function(){
        showScreen(button.dataset.screen);
      });
    });

    document.getElementById('logoutButton').addEventListener('click', function(){
      sessionStorage.removeItem(SESSION_KEY);
      document.getElementById('appView').classList.add('is-hidden');
      document.getElementById('loginView').classList.remove('is-hidden');
    });
  }

  function bindPreview(){
    const previewPane = document.getElementById('previewPane');
    const previewButton = document.getElementById('previewButton');
    const closePreviewButton = document.getElementById('closePreviewButton');

    previewButton.addEventListener('click', function(){
      closeAllEditors();
      const frame = previewPane.querySelector('iframe');
      if(frame && !frame.getAttribute('src')){
        frame.setAttribute('src', frame.dataset.src || '../index.html');
      }
      document.querySelectorAll('.screen').forEach(function(screen){
        screen.classList.remove('active');
      });
      previewPane.classList.remove('is-hidden');
      document.getElementById('screenTitle').textContent = '홈페이지 미리보기';
    });

    closePreviewButton.addEventListener('click', function(){
      previewPane.classList.add('is-hidden');
      const activeMenu = document.querySelector('.menu-btn.active');
      showScreen(activeMenu ? activeMenu.dataset.screen : 'cases');
    });
  }

  function bindCrudActions(){
    document.addEventListener('click', async function(event){
      const button = event.target.closest('[data-action]');
      if(!button && !event.target.closest('.card-menu')){
        closeCardMenus();
      }
      if(!button){
        return;
      }

      const type = button.dataset.type;
      const action = button.dataset.action;
      const id = button.dataset.id;
      if(action !== 'card-menu'){
        closeCardMenus();
      }

      if(action === 'new'){
        openEditor(type);
      }
      if(action === 'load-more'){
        visibleCounts[type] = (visibleCounts[type] || INITIAL_RENDER_LIMIT) + RENDER_CHUNK;
        renderScreen(type);
      }
      if(action === 'edit'){
        if(type && type !== activeScreen){
          showScreen(type);
        }
        openEditor(type, id);
      }
      if(action === 'delete'){
        requestDelete(type, id);
      }
      if(action === 'cancel'){
        closeEditor(type);
      }
      if(action === 'card-menu'){
        event.stopPropagation();
        toggleCardMenu(button);
      }
      if(action === 'undo-delete'){
        restoreDeletedItem();
      }
      if(action === 'json-export'){
        exportJsonType(button.dataset.jsonType || 'backup');
      }
      if(action === 'json-import'){
        importJsonFromTextarea();
      }
      if(action === 'json-validate'){
        validateJsonImportText();
      }
      if(action === 'json-save-preview'){
        renderSaveTargetPreview();
      }
      if(action === 'json-auto-save'){
        saveJsonTargets();
      }
      if(action === 'reload-live-json'){
        reloadLiveJsonData(button);
      }
      if(action === 'save-remote'){
        const saveType = button.dataset.type;
        if(saveType === 'sections'){
          const sectionErrors = validateSectionsForSave(cmsData.sections || []);
          if(sectionErrors.length){
            const message = '섹션 데이터에 문제가 있어 저장할 수 없습니다: ' + sectionErrors.join(' / ');
            showToast(message);
            setStatus(message);
            return;
          }
        }else if(INTEGRITY_GUARDED_TYPES.indexOf(saveType) !== -1){
          // PR-F1: 원격 최신 데이터를 다시 확보해 비교합니다(saveTypeToRemote() 내부에서도
          // 저장 직전 한 번 더 갱신하지만, 여기서는 비교용 currentContent가 필요합니다).
          await refreshRemoteContent(saveType);
          const currentContent = remoteContentByType[saveType];
          const localPayload = normalizePayloadForRemote(saveType, cmsData[saveType] || []);
          const integrityErrors = validateArrayIntegrityForSave(saveType, localPayload, currentContent);
          if(integrityErrors.length){
            const message = describeIntegrityBlockReason(integrityErrors);
            showToast(message);
            setStatus(message);
            return;
          }
        }
        saveTypeToRemote(saveType, button);
      }
    });

    document.addEventListener('submit', function(event){
      const form = event.target.closest('.editor-form');
      if(!form){
        return;
      }
      event.preventDefault();
      saveEditor(form.dataset.type, form.dataset.id || '');
    });
  }

  function bindSettingsActions(){
    document.getElementById('resetDataButton').addEventListener('click', function(){
      localStorage.removeItem(DATA_KEY);
      localStorage.removeItem(FORM_DRAFT_KEY);
      closeAllEditors();
      loadData({ forceSample: true }).then(function(){
        renderScreen('settings');
        renderSearchResults(getSearchQuery());
        showScreen('settings');
        showToast('샘플 데이터로 초기화됨');
        setStatus('샘플 데이터로 초기화됨');
      });
    });

    document.getElementById('exportDataButton').addEventListener('click', function(){ exportJsonType('backup'); });
  }

  function showApp(){
    document.getElementById('loginView').classList.add('is-hidden');
    document.getElementById('appView').classList.remove('is-hidden');
    loadData().then(function(){
      visibleCounts = {};
      showScreen('cases');
      setStatus('데이터 로드 완료');
    });
  }

  function showScreen(screen){
    activeScreen = screen;
    setStatus('');
    document.getElementById('previewPane').classList.add('is-hidden');
    closeAllEditors();
    document.querySelectorAll('.menu-btn').forEach(function(button){
      button.classList.toggle('active', button.dataset.screen === screen);
    });
    document.querySelectorAll('.screen').forEach(function(section){
      section.classList.toggle('active', section.id === 'screen-' + screen);
    });
    renderScreen(screen);
    renderSearchResults(getSearchQuery());
    document.getElementById('screenTitle').textContent = titles[screen] || '관리 화면';

    if(saveTargetTypes.includes(screen)){
      // 화면에 보이는 편집 내용(cmsData[screen])은 건드리지 않고, 저장 시 충돌
      // 비교에 쓸 최신 sha만 백그라운드로 미리 확보해둡니다.
      refreshRemoteContent(screen);
    }
  }

  async function loadData(options){
    if(!options || !options.forceSample){
      const saved = localStorage.getItem(DATA_KEY);
      if(saved){
        try {
          cmsData = normalizeData(JSON.parse(saved));
          return;
        } catch(error) {
          localStorage.removeItem(DATA_KEY);
        }
      }
    }

    const entries = await Promise.all(Object.keys(dataFiles).map(async function(key){
      try {
        const response = await fetch(dataFiles[key], { cache: 'no-store' });
        if(!response.ok){
          throw new Error('Failed to load ' + dataFiles[key]);
        }
        return [key, await response.json()];
      } catch(error) {
        return [key, clone(fallbackData[key])];
      }
    }));
    cmsData = normalizeData(Object.fromEntries(entries));
    persistData();
  }

  function normalizeData(data){
    const source = Object.assign({}, data || {});
    if(!source.faq && source.faqs){
      source.faq = source.faqs;
    }
    if(!source.banners && source.banner){
      source.banners = Array.isArray(source.banner) ? source.banner : [source.banner];
    }

    const normalized = { settings: Object.assign({}, fallbackData.settings, source.settings || {}, { cmsVersion: '1.7', dataMode: 'localStorage' }) };
    contentTypes.forEach(function(type){
      const list = Array.isArray(source[type]) ? source[type] : fallbackData[type];
      normalized[type] = normalizeTypeItems(type, list);
    });
    return normalized;
  }

  function normalizeTypeItems(type, items){
    return (Array.isArray(items) ? items : []).map(function(item, index){
      return normalizeTypeItem(type, item, index);
    });
  }

  function normalizeTypeItem(type, item, index){
    const config = typeConfig[type];
    const source = item || {};
    const normalized = {};
    config.fields.forEach(function(field){
      if(field === 'id'){
        normalized.id = cleanText(source.id) || config.prefix + '-' + String((index || 0) + 1).padStart(3, '0');
      }else if(field === 'rating'){
        normalized.rating = cleanRating(source.rating);
      }else if(field === 'visible'){
        normalized.visible = cleanVisible(source.visible);
      }else if(field === 'featured'){
        normalized.featured = cleanFeatured(source.featured);
      }else if(field === 'sort'){
        normalized.sort = cleanSort(source.sort, index);
      }else if(field === 'image'){
        normalized.image = cleanText(source.image);
      }else if(type === 'prices' && field === 'category'){
        normalized.category = cleanText(source.category || source.service);
      }else if(type === 'prices' && field === 'price'){
        normalized.price = cleanText(source.price || source.priceText);
      }else if(type === 'notices' && field === 'date'){
        normalized.date = cleanText(source.date || source.startDate);
      }else if(type === 'banners' && field === 'description'){
        normalized.description = cleanText(source.description || source.message);
      }else{
        normalized[field] = cleanText(source[field]);
      }
    });
    return normalized;
  }

  function cleanText(value){
    return typeof value === 'string' ? value.trim() : value == null ? '' : String(value).trim();
  }

  function cleanVisible(value){
    return value !== false && value !== 'false' && value !== 'off';
  }

  function cleanFeatured(value){
    return value === true || value === 'true' || value === 'on';
  }

  function cleanRating(value){
    const rating = Number(value || 5);
    if(!Number.isFinite(rating)){
      return 5;
    }
    return Math.max(1, Math.min(5, Math.round(rating)));
  }

  function cleanSort(value, index){
    const sort = Number(value || 0);
    return Number.isFinite(sort) && sort > 0 ? sort : (index || 0) + 1;
  }

  function openEditor(type, id){
    const panel = document.getElementById(type + 'Editor');
    const item = id ? getItem(type, id) : null;
    activePhotoData = [];
    panel.innerHTML = '';
    panel.appendChild(buildEditor(type, item));
    bindDraftAutosave(panel.querySelector('form'), type, id || '');
    promptDraftRestore(panel.querySelector('form'), type, id || '');
    panel.classList.remove('is-hidden');
    panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function closeEditor(type){
    const panel = document.getElementById(type + 'Editor');
    if(panel){
      panel.innerHTML = '';
      panel.classList.add('is-hidden');
    }
    activePhotoData = [];
    activeDraftContext = null;
  }

  function closeAllEditors(){
    contentTypes.forEach(closeEditor);
  }

  function buildEditor(type, item){
    const wrap = document.createElement('div');
    const heading = document.createElement('h3');
    heading.textContent = (item ? '수정: ' : '추가: ') + editorTitles[type];
    wrap.appendChild(heading);

    const form = document.createElement('form');
    form.className = 'editor-form';
    form.dataset.type = type;
    if(item){
      form.dataset.id = item.id;
    }

    const grid = document.createElement('div');
    grid.className = 'editor-grid';
    getFields(type).forEach(function(field){
      if(field.kind === 'photos'){
        grid.appendChild(photoField());
      }else{
        grid.appendChild(inputField(field, item ? item[field.name] : undefined));
      }
    });
    form.appendChild(grid);

    const actions = document.createElement('div');
    actions.className = 'form-actions';
    const save = document.createElement('button');
    save.type = 'submit';
    save.textContent = item ? '수정 저장' : '저장';
    actions.appendChild(save);

    const cancel = document.createElement('button');
    cancel.type = 'button';
    cancel.className = 'secondary-btn';
    cancel.dataset.action = 'cancel';
    cancel.dataset.type = type;
    cancel.textContent = '취소';
    actions.appendChild(cancel);
    form.appendChild(actions);

    wrap.appendChild(form);
    return wrap;
  }

  function getFields(type){
    const commonService = { name: 'service', label: '서비스 선택', kind: 'select', options: serviceOptions };
    const visibleField = { name: 'visible', label: '홈페이지 표시', kind: 'checkbox', default: true, required: false };
    const sortField = { name: 'sort', label: '정렬 순서', kind: 'number', placeholder: '예: 1', required: false };
    const map = {
      cases: [
        commonService,
        { name: 'region', label: '지역', kind: 'text', placeholder: '예: 서울 강서구' },
        { name: 'title', label: '제목', kind: 'text', placeholder: '예: 특수청소 작업사례' },
        { name: 'description', label: '설명', kind: 'textarea', placeholder: '작업 상황과 처리 내용을 입력' },
        { name: 'image', label: '작업 사진 경로', kind: 'image-url', placeholder: '예: images/cases/sample.jpg', required: false },
        { name: 'date', label: '작업일', kind: 'date', required: false },
        { name: 'featured', label: '대표 사례', kind: 'checkbox', default: false, required: false },
        visibleField,
        sortField
      ],
      reviews: [
        commonService,
        { name: 'region', label: '지역', kind: 'text', placeholder: '예: 인천' },
        { name: 'title', label: '후기 제목', kind: 'text', placeholder: '예: 인천 입주청소 고객 후기' },
        { name: 'rating', label: '별점 선택', kind: 'select', options: ['5', '4', '3', '2', '1'] },
        { name: 'content', label: '후기 내용', kind: 'textarea', placeholder: '고객 후기 내용을 입력' },
        { name: 'image', label: '리뷰 이미지 경로', kind: 'image-url', placeholder: '예: images/reviews/review-01.jpg', required: false },
        { name: 'source', label: '출처', kind: 'text', placeholder: '예: 고객 상담 후기', required: false },
        { name: 'date', label: '후기일', kind: 'date', required: false },
        visibleField,
        sortField
      ],
      prices: [
        { name: 'category', label: '서비스 분류', kind: 'text', placeholder: '예: 입주청소' },
        { name: 'title', label: '가격 항목', kind: 'text', placeholder: '예: 원룸' },
        { name: 'price', label: '가격 문구', kind: 'text', placeholder: '예: 180,000~' },
        { name: 'description', label: '설명', kind: 'textarea', placeholder: '가격 산정 기준과 안내 문구를 입력', required: false },
        visibleField,
        sortField
      ],
      faq: [
        { name: 'question', label: '질문', kind: 'text', placeholder: '예: 당일 상담이 가능한가요?' },
        { name: 'answer', label: '답변', kind: 'textarea', placeholder: '답변 내용을 입력' },
        visibleField,
        sortField
      ],
      notices: [
        { name: 'title', label: '제목', kind: 'text', placeholder: '예: 예약 안내' },
        { name: 'content', label: '내용', kind: 'textarea', placeholder: '공지 내용을 입력' },
        { name: 'date', label: '게시일', kind: 'date', required: false },
        visibleField,
        sortField
      ],
      banners: [
        { name: 'title', label: '배너 제목', kind: 'text', placeholder: '예: 사진 없이도 먼저 상담 가능합니다.' },
        { name: 'description', label: '배너 설명', kind: 'textarea', placeholder: '현장 상태를 말씀해주시면 가능한 작업 여부부터 안내드립니다.' },
        { name: 'button', label: '버튼 문구', kind: 'text', placeholder: '예: 카카오톡 상담', required: false },
        { name: 'link', label: '버튼 링크', kind: 'text', placeholder: '예: #contact', required: false },
        visibleField,
        sortField
      ]
    };
    return map[type] || [];
  }

  function inputField(field, value){
    if(field.kind === 'image-url'){
      return imageUrlField(field, value);
    }

    const label = document.createElement('label');
    if(field.kind === 'textarea' || field.name === 'content' || field.name === 'description' || field.name === 'answer'){
      label.className = 'full';
    }

    if(field.kind === 'checkbox'){
      label.className = 'checkbox-row';
      const input = document.createElement('input');
      input.name = field.name;
      input.type = 'checkbox';
      input.checked = value === undefined || value === '' ? field.default === true : value === true || value === 'on' || value === 'true';
      label.appendChild(input);
      label.appendChild(document.createTextNode(field.label));
      return label;
    }

    label.appendChild(document.createTextNode(field.label));
    let input;
    if(field.kind === 'textarea'){
      input = document.createElement('textarea');
      input.rows = 5;
    }else if(field.kind === 'select'){
      input = document.createElement('select');
      field.options.forEach(function(optionValue){
        const option = document.createElement('option');
        option.value = optionValue;
        option.textContent = field.name === 'rating' ? optionValue + '점' : optionValue;
        input.appendChild(option);
      });
    }else{
      input = document.createElement('input');
      input.type = field.kind || 'text';
      if(field.kind === 'number'){
        input.min = '1';
        input.step = '1';
      }
    }
    input.name = field.name;
    if(field.kind === 'select'){
      if(value !== undefined && value !== ''){
        input.value = value;
      }
    }else{
      input.value = value == null ? '' : value;
    }
    if(field.placeholder){
      input.placeholder = field.placeholder;
    }
    if(field.required !== false && field.kind !== 'date'){
      input.required = true;
    }
    label.appendChild(input);
    return label;
  }

  function imageUrlField(field, value){
    const label = document.createElement('label');
    label.className = 'full image-url-field';
    label.appendChild(document.createTextNode(field.label));

    const input = document.createElement('input');
    input.name = field.name;
    input.type = 'text';
    input.inputMode = 'url';
    input.autocomplete = 'off';
    input.value = value == null ? '' : value;
    if(field.placeholder){
      input.placeholder = field.placeholder;
    }
    label.appendChild(input);

    const preview = document.createElement('div');
    preview.className = 'image-url-preview';
    preview.setAttribute('aria-live', 'polite');
    label.appendChild(preview);

    const warning = document.createElement('span');
    warning.className = 'image-url-warning';
    warning.setAttribute('aria-live', 'polite');
    label.appendChild(warning);

    function syncPreview(){
      const imageValue = cleanText(input.value);
      renderImageUrlPreview(preview, imageValue, field.label);
      if(imageValue && !isLikelyImageUrl(imageValue)){
        warning.textContent = '이미지 URL 형식을 확인하세요. 저장은 가능합니다.';
        label.classList.add('has-warning');
      }else{
        warning.textContent = '';
        label.classList.remove('has-warning');
      }
    }

    input.addEventListener('input', syncPreview);
    input.addEventListener('change', syncPreview);
    syncPreview();
    return label;
  }

  function renderImageUrlPreview(container, src, label){
    container.innerHTML = '';
    const value = cleanText(src);
    if(!value){
      container.className = 'image-url-preview is-empty';
      const empty = document.createElement('span');
      empty.textContent = '이미지가 없으면 텍스트 카드로 표시됩니다.';
      container.appendChild(empty);
      return;
    }
    if(!isLikelyImageUrl(value)){
      container.className = 'image-url-preview is-empty';
      const invalid = document.createElement('span');
      invalid.textContent = '미리보기 전 URL 형식을 확인하세요.';
      container.appendChild(invalid);
      return;
    }

    container.className = 'image-url-preview';
    const img = document.createElement('img');
    img.alt = (label || 'image') + ' preview';
    img.loading = 'lazy';
    img.src = normalizeImageSrc(value);
    img.onerror = function(){
      container.className = 'image-url-preview is-empty';
      container.innerHTML = '';
      const failed = document.createElement('span');
      failed.textContent = '이미지를 불러올 수 없습니다. 경로를 확인하세요.';
      container.appendChild(failed);
    };
    container.appendChild(img);
  }

  function refreshImageUrlPreviews(form){
    if(!form){
      return;
    }
    Array.from(form.querySelectorAll('.image-url-field input[name="image"]')).forEach(function(input){
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });
  }

  function photoField(){
    const wrap = document.createElement('div');
    wrap.className = 'full photo-drop';
    wrap.dataset.photoDrop = 'true';

    const label = document.createElement('label');
    label.textContent = '사진 드래그/선택 UI';
    const input = document.createElement('input');
    input.type = 'file';
    input.name = 'photos';
    input.accept = 'image/*';
    input.multiple = true;
    label.appendChild(input);
    wrap.appendChild(label);

    const help = document.createElement('span');
    help.textContent = '이미지는 브라우저 미리보기와 localStorage 임시 저장용으로만 사용됩니다.';
    wrap.appendChild(help);

    const preview = document.createElement('div');
    preview.className = 'photo-preview';
    preview.dataset.photoPreview = 'true';
    wrap.appendChild(preview);

    input.addEventListener('change', function(){
      readPhotoFiles(input.files);
    });
    wrap.addEventListener('dragover', function(event){
      event.preventDefault();
      wrap.classList.add('is-over');
    });
    wrap.addEventListener('dragleave', function(){
      wrap.classList.remove('is-over');
    });
    wrap.addEventListener('drop', function(event){
      event.preventDefault();
      wrap.classList.remove('is-over');
      readPhotoFiles(event.dataTransfer.files);
    });

    renderPhotoPreview(preview);
    return wrap;
  }

  function readPhotoFiles(files){
    const imageFiles = Array.from(files || []).filter(function(file){
      return file.type.indexOf('image/') === 0;
    });
    if(!imageFiles.length){
      return;
    }
    Promise.all(imageFiles.map(function(file){
      return new Promise(function(resolve){
        const reader = new FileReader();
        reader.onload = function(){
          resolve({ name: file.name, src: reader.result });
        };
        reader.onerror = function(){
          resolve({ name: file.name, src: '' });
        };
        reader.readAsDataURL(file);
      });
    })).then(function(results){
      activePhotoData = results.filter(function(item){ return item.src; });
      const preview = document.querySelector('[data-photo-preview]');
      if(preview){
        renderPhotoPreview(preview);
      }
      scheduleDraftSaveForActiveForm();
    });
  }

  function renderPhotoPreview(container){
    container.innerHTML = '';
    if(!activePhotoData.length){
      const empty = document.createElement('span');
      empty.textContent = '선택된 사진 없음';
      container.appendChild(empty);
      return;
    }
    activePhotoData.forEach(function(photo){
      const thumb = document.createElement('div');
      thumb.className = 'photo-thumb';
      const src = typeof photo === 'string' ? photo : photo.src;
      const name = typeof photo === 'string' ? photo : photo.name;
      if(src){
        const img = document.createElement('img');
        img.alt = name || '작업사례 이미지 미리보기';
        img.loading = 'lazy';
        img.src = src;
        thumb.appendChild(img);
      }
      const caption = document.createElement('span');
      caption.textContent = name || '미리보기 이미지';
      thumb.appendChild(caption);
      container.appendChild(thumb);
    });
  }

  function saveEditor(type, id){
    const form = document.querySelector('.editor-form[data-type="' + type + '"]');
    if(!form){
      return;
    }
    const entry = formToEntry(form, type, id);
    const list = cmsData[type] || [];
    if(id){
      const index = list.findIndex(function(item){ return item.id === id; });
      if(index !== -1){
        list[index] = entry;
      }
    }else{
      list.unshift(entry);
    }
    cmsData[type] = list;
    persistData();
    clearFormDraft(type, id || '');
    closeEditor(type);
    renderScreen(type);
    renderSearchResults(getSearchQuery());
    showToast((editorTitles[type] || '항목') + ' 저장됨');
    setStatus((editorTitles[type] || '항목') + ' 저장됨');
  }

  function formToEntry(form, type, id){
    const values = formValues(form);
    const existing = id ? getItem(type, id) || {} : {};
    values.id = id || nextItemId(type);
    const currentIndex = (cmsData[type] || []).findIndex(function(item){ return item.id === id; });
    const index = currentIndex === -1 ? (cmsData[type] || []).length : currentIndex;
    const merged = Object.assign({}, existing, values);
    return normalizeTypeItem(type, merged, index);
  }

  function nextItemId(type){
    const config = typeConfig[type] || { prefix: type };
    return config.prefix + '-' + Date.now();
  }

  function deleteItem(type, id){
    const list = cmsData[type] || [];
    const index = list.findIndex(function(item){
      return item.id === id;
    });
    if(index === -1){
      return;
    }
    const removed = list.splice(index, 1)[0];
    undoDelete = { type: type, item: removed, index: index };
    cmsData[type] = list;
    persistData();
    closeEditor(type);
    renderScreen(type);
    renderSearchResults(getSearchQuery());
    clearTimeout(undoTimer);
    undoTimer = setTimeout(function(){
      undoDelete = null;
    }, UNDO_DELETE_MS);
    showToast((editorTitles[type] || '항목') + ' 삭제됨', {
      action: 'undo-delete',
      label: '되돌리기',
      timeout: UNDO_DELETE_MS + 600
    });
    setStatus((editorTitles[type] || '항목') + ' 삭제됨');
  }

  function getItem(type, id){
    return (cmsData[type] || []).find(function(item){
      return item.id === id;
    });
  }

  function persistData(){
    localStorage.setItem(DATA_KEY, JSON.stringify(cmsData));
  }

  function renderScreen(type){
    if(type === 'settings'){
      renderSettings();
      return;
    }
    if(type === 'json'){
      renderJsonScreen();
      return;
    }
    if(type === 'services'){
      renderServicesScreen();
      return;
    }
    if(type === 'sections'){
      renderSectionsScreen();
      return;
    }
    const renderer = getRenderer(type);
    if(renderer){
      renderList(type, renderer);
    }
  }

  // services는 12개 고정 항목을 아코디언으로 펼쳐 편집하는 화면입니다(PR-C2b).
  // cases/reviews 등과 달리 항목 추가/삭제가 없고, 각 카드 안의 입력값이 바뀔
  // 때마다 cmsData.services를 직접 갱신한 뒤 localStorage에 반영합니다.
  let servicesDraftTimer = 0;

  function renderServicesScreen(){
    const container = document.getElementById('servicesAccordion');
    if(!container){
      return;
    }
    const items = (cmsData.services || []).slice().sort(function(a, b){
      return (a.sort || 0) - (b.sort || 0);
    });
    container.innerHTML = '';
    if(!items.length){
      const empty = document.createElement('article');
      empty.className = 'data-item';
      const strong = document.createElement('strong');
      strong.textContent = '데이터 없음';
      const paragraph = document.createElement('p');
      paragraph.textContent = 'data/services.json을 불러오지 못했습니다. 새로고침 후 다시 시도해주세요.';
      empty.appendChild(strong);
      empty.appendChild(paragraph);
      container.appendChild(empty);
      return;
    }
    const fragment = document.createDocumentFragment();
    items.forEach(function(item){
      fragment.appendChild(buildServiceCard(item));
    });
    container.appendChild(fragment);
  }

  function buildServiceCard(item){
    const details = document.createElement('details');
    details.className = 'service-card';
    details.dataset.id = item.id;

    const summary = document.createElement('summary');
    summary.appendChild(buildServiceSummaryLabel(item));
    details.appendChild(summary);

    const body = document.createElement('div');
    body.className = 'service-card-body';

    const idTag = document.createElement('p');
    idTag.className = 'service-id-tag';
    idTag.textContent = 'id: ' + item.id + ' (읽기 전용)';
    body.appendChild(idTag);

    const grid = document.createElement('div');
    grid.className = 'editor-grid';
    getServiceFields().forEach(function(field){
      grid.appendChild(serviceInputField(item, field, summary));
    });
    body.appendChild(grid);

    details.appendChild(body);
    return details;
  }

  function buildServiceSummaryLabel(item){
    const label = document.createElement('span');
    label.className = 'service-summary-label';
    label.dataset.role = 'summary-label';
    label.textContent = serviceSummaryText(item);
    return label;
  }

  function serviceSummaryText(item){
    return (item.sort || 0) + '. ' + (item.service || '(서비스명 없음)') + ' · ' + visibleLabel(item.visible) + ' · 정렬 ' + (item.sort || 0);
  }

  function getServiceFields(){
    return [
      { name: 'service', label: '서비스명', kind: 'text', placeholder: '예: 특수청소' },
      { name: 'seoTitle', label: 'SEO 제목', kind: 'text', placeholder: '검색결과에 노출될 제목', required: false },
      { name: 'summary', label: '요약', kind: 'textarea', placeholder: '한두 문장 요약' },
      { name: 'description', label: '상세 설명', kind: 'textarea', placeholder: '서비스 상세 설명' },
      { name: 'scope', label: '작업 범위', kind: 'textarea', placeholder: '작업 범위', required: false },
      { name: 'process', label: '진행 순서', kind: 'textarea', placeholder: '진행 순서(비워두면 홈페이지 공통 진행 절차만 표시)', required: false },
      { name: 'priceNote', label: '가격 기준', kind: 'textarea', placeholder: '가격 산정 기준', required: false },
      { name: 'notes', label: '주의사항', kind: 'textarea', placeholder: '주의사항', required: false },
      { name: 'ctaText', label: 'CTA 문구', kind: 'text', placeholder: '(현재 정책상 비워두는 것을 권장)', required: false },
      { name: 'visible', label: '홈페이지 표시', kind: 'checkbox' },
      { name: 'sort', label: '정렬 순서', kind: 'number', placeholder: '예: 1' }
    ];
  }

  function serviceInputField(item, field, summaryEl){
    const label = document.createElement('label');
    if(field.kind === 'textarea'){
      label.className = 'full';
    }

    if(field.kind === 'checkbox'){
      label.className = 'checkbox-row';
      const input = document.createElement('input');
      input.type = 'checkbox';
      input.name = field.name;
      input.checked = item.visible !== false;
      input.addEventListener('change', function(){
        updateServiceField(item.id, field.name, input.checked, summaryEl);
      });
      label.appendChild(input);
      label.appendChild(document.createTextNode(field.label));
      return label;
    }

    label.appendChild(document.createTextNode(field.label));
    let input;
    if(field.kind === 'textarea'){
      input = document.createElement('textarea');
      input.rows = field.name === 'description' || field.name === 'scope' ? 6 : 4;
      input.value = item[field.name] == null ? '' : item[field.name];
    }else{
      input = document.createElement('input');
      input.type = field.kind === 'number' ? 'number' : 'text';
      if(field.kind === 'number'){
        input.min = '1';
        input.step = '1';
      }
      input.value = item[field.name] == null ? '' : item[field.name];
    }
    input.name = field.name;
    if(field.placeholder){
      input.placeholder = field.placeholder;
    }
    if(field.required !== false){
      input.required = true;
    }
    const eventName = field.kind === 'number' ? 'change' : 'input';
    input.addEventListener(eventName, function(){
      const value = field.kind === 'number' ? Number(input.value || 0) : input.value;
      updateServiceField(item.id, field.name, value, summaryEl);
    });
    label.appendChild(input);
    return label;
  }

  function updateServiceField(id, field, value, summaryEl){
    const list = cmsData.services || [];
    const target = list.find(function(entry){ return entry.id === id; });
    if(!target){
      return;
    }
    target[field] = value;
    if((field === 'service' || field === 'visible' || field === 'sort') && summaryEl){
      const labelEl = summaryEl.querySelector('[data-role="summary-label"]');
      if(labelEl){
        labelEl.textContent = serviceSummaryText(target);
      }
    }
    clearTimeout(servicesDraftTimer);
    servicesDraftTimer = setTimeout(persistData, DRAFT_SAVE_DELAY);
  }

  // 섹션 표시 관리(PR-D1): 홈페이지 주요 섹션의 visible만 켜고 끄는 최소 화면입니다.
  // 추가/삭제/순서 변경 UI는 없고, sort는 표시만 합니다. Worker가 아직 sections
  // 저장을 지원하지 않아(SAVE_WHITELIST 미등록) 저장 버튼은 비활성화되어 있습니다.
  let sectionsDraftTimer = 0;

  function renderSectionsScreen(){
    const container = document.getElementById('sectionsList');
    if(!container){
      return;
    }
    const items = (cmsData.sections || []).slice().sort(function(a, b){
      return (a.sort || 0) - (b.sort || 0);
    });
    container.innerHTML = '';
    if(!items.length){
      container.appendChild(emptyCard('sections'));
      return;
    }
    const fragment = document.createDocumentFragment();
    items.forEach(function(item){
      fragment.appendChild(buildSectionRow(item));
    });
    container.appendChild(fragment);
  }

  function buildSectionRow(item){
    const article = document.createElement('article');
    article.className = 'data-item section-row';

    const head = document.createElement('div');
    head.className = 'data-item-head';

    const titleWrap = document.createElement('div');
    const strong = document.createElement('strong');
    strong.textContent = item.name || item.id;
    titleWrap.appendChild(strong);
    const sortTag = document.createElement('p');
    sortTag.className = 'service-id-tag';
    sortTag.textContent = '정렬 순서: ' + (item.sort || 0) + ' (읽기 전용)';
    titleWrap.appendChild(sortTag);
    head.appendChild(titleWrap);

    const label = document.createElement('label');
    label.className = 'checkbox-row';
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.name = 'visible';
    input.checked = item.visible !== false;
    input.addEventListener('change', function(){
      updateSectionVisible(item.id, input.checked);
    });
    label.appendChild(input);
    label.appendChild(document.createTextNode('홈페이지 표시'));
    head.appendChild(label);

    article.appendChild(head);
    return article;
  }

  function updateSectionVisible(id, checked){
    const list = cmsData.sections || [];
    const target = list.find(function(entry){ return entry.id === id; });
    if(!target){
      return;
    }
    target.visible = checked;
    clearTimeout(sectionsDraftTimer);
    sectionsDraftTimer = setTimeout(persistData, DRAFT_SAVE_DELAY);
  }

  // sections 저장 버튼을 누르기 전, 실제 홈페이지 저장 서버(Worker)와 동일한
  // 규칙으로 미리 검증합니다(PR-D1c). 2026-07-22에 localStorage 캐시가 손상돼
  // sections가 1개짜리로 줄어든 채 저장된 사고가 있었는데, 그 payload는 아래
  // 조건에 걸려 saveTypeToRemote() 호출 자체가 막혔을 것입니다. cmsData.sections
  // 전체(화면에 보이는 항목 수/검색·필터와 무관)를 대상으로 검증합니다.
  const REQUIRED_SECTION_IDS = ['home', 'about', 'service', 'price', 'portfolio', 'journal', 'policy', 'partner', 'contact'];

  function validateSectionsForSave(payload){
    const errors = [];
    if(!Array.isArray(payload)){
      errors.push('sections must contain exactly ' + REQUIRED_SECTION_IDS.length + ' items');
      return errors;
    }
    if(payload.length !== REQUIRED_SECTION_IDS.length){
      errors.push('sections must contain exactly ' + REQUIRED_SECTION_IDS.length + ' items');
    }

    const seenIds = new Set();
    payload.forEach(function(item, index){
      const id = item && item.id;
      const label = typeof id === 'string' && id ? id : 'index ' + index;

      if(typeof id !== 'string' || id.trim() === ''){
        errors.push('index ' + index + ': id is required');
      }else{
        if(seenIds.has(id)){
          errors.push('duplicate section id: ' + id);
        }
        seenIds.add(id);
      }

      if(typeof (item && item.name) !== 'string' || !item.name || !item.name.trim()){
        errors.push(label + ': name is required');
      }

      if(typeof (item && item.visible) !== 'boolean'){
        errors.push(label + ': visible must be boolean');
      }

      const sort = item && item.sort;
      if(typeof sort !== 'number' || !Number.isFinite(sort)){
        errors.push(label + ': sort must be number');
      }else if(sort < 1 || sort > REQUIRED_SECTION_IDS.length){
        errors.push(label + ': sort must be between 1 and ' + REQUIRED_SECTION_IDS.length);
      }
    });

    REQUIRED_SECTION_IDS.forEach(function(requiredId){
      if(!seenIds.has(requiredId)){
        errors.push('missing required section id: ' + requiredId);
      }
    });

    return errors;
  }

  // PR-F1: sections 외 7개 타입(banners/cases/reviews/prices/faq/notices/services)
  // 공통 저장 무결성 검증입니다. Worker의 validateArrayIntegrity()와 동일한 규칙을
  // 프론트에서 먼저 적용해, 명백히 잘못된 payload(빈 배열/기존 항목 소실/개수 감소)는
  // 네트워크 요청 자체를 보내지 않고 저장 버튼 클릭 단계에서 막습니다. 이번 PR에서는
  // "삭제 저장"을 허용하지 않습니다 - 항목을 숨기려면 visible:false를 사용해야 하며,
  // 개수 감소가 필요한 명시적 삭제 기능은 이후 별도 PR로 설계합니다.
  function getItemIds(items){
    return (items || [])
      .filter(function(item){ return item && typeof item === 'object' && typeof item.id === 'string' && item.id.trim() !== ''; })
      .map(function(item){ return item.id; });
  }

  function findDuplicateIds(ids){
    const seen = new Set();
    const duplicates = new Set();
    ids.forEach(function(id){
      if(seen.has(id)){
        duplicates.add(id);
      }
      seen.add(id);
    });
    return Array.from(duplicates);
  }

  function findMissingIds(baseIds, otherIds){
    const otherSet = new Set(otherIds);
    return baseIds.filter(function(id){ return !otherSet.has(id); });
  }

  function validateArrayIntegrityForSave(type, payload, currentContent){
    const errors = [];
    if(!Array.isArray(payload)){
      errors.push('not_array: payload는 배열이어야 합니다.');
      return errors;
    }
    if(payload.length === 0){
      errors.push('empty_array: ' + type + ' payload는 빈 배열일 수 없습니다. 항목을 숨기려면 visible:false를 사용하세요.');
      return errors;
    }

    const payloadIds = getItemIds(payload);
    if(payloadIds.length !== payload.length){
      errors.push('missing_id: 모든 항목에는 문자열 id가 있어야 합니다.');
    }
    findDuplicateIds(payloadIds).forEach(function(id){
      errors.push('duplicate_id: ' + id);
    });

    // 원격 데이터를 아직 확보하지 못한 경우(오프라인/최초 로드 실패 등)에는
    // 비교 기준이 없으므로 기존 id/개수 검증은 건너뛰고, 위에서 이미 확인한
    // 구조적 오류(빈 배열/중복 id)만 반영합니다. saveTypeToRemote() 쪽에서
    // remoteShaByType이 없으면 어차피 저장을 막습니다.
    if(!Array.isArray(currentContent)){
      return errors;
    }

    const currentIds = getItemIds(currentContent);

    if(FIXED_ID_SET_TYPES.indexOf(type) !== -1){
      findMissingIds(currentIds, payloadIds).forEach(function(id){
        errors.push('services_id_set_changed: missing existing id ' + id);
      });
      findMissingIds(payloadIds, currentIds).forEach(function(id){
        errors.push('services_id_set_changed: unexpected new id ' + id);
      });
      if(payload.length !== currentContent.length){
        errors.push('services_id_set_changed: item count must stay exactly ' + currentIds.length);
      }
    }else{
      findMissingIds(currentIds, payloadIds).forEach(function(id){
        errors.push('missing_existing_id: ' + id);
      });
      if(payload.length < currentContent.length){
        errors.push('count_decreased: ' + type + ' item count decreased (current: ' + currentContent.length + ', payload: ' + payload.length + ')');
      }
    }

    return errors;
  }

  // 검증 실패 원인(코드)에 따라 관리자가 바로 이해할 수 있는 안내 문구를 고릅니다.
  function describeIntegrityBlockReason(errors){
    const joined = errors.join(' / ');
    if(joined.indexOf('missing_existing_id') !== -1 || joined.indexOf('missing existing id') !== -1){
      return '저장 중단: 기존 항목이 사라진 상태입니다. 실제 JSON 다시 불러오기를 먼저 실행해주세요.';
    }
    if(joined.indexOf('count_decreased') !== -1 || joined.indexOf('empty_array') !== -1 || joined.indexOf('item count must stay exactly') !== -1){
      return '저장 중단: 항목 수가 줄어든 상태에서는 저장할 수 없습니다. 숨김 처리는 visible 옵션을 사용해주세요.';
    }
    if(joined.indexOf('duplicate_id') !== -1){
      return '저장 중단: 중복된 id가 있습니다. 항목 내용을 확인해주세요.';
    }
    if(joined.indexOf('unexpected new id') !== -1){
      return '저장 중단: 서비스 상세는 항목 추가/삭제를 지원하지 않습니다. 기존 항목만 수정해주세요.';
    }
    return '저장 중단: 데이터에 문제가 있어 저장할 수 없습니다. (' + errors.join(', ') + ')';
  }

  function getRenderer(type){
    const renderers = {
      cases: function(item){
        return createCaseCard(item);
      },
      reviews: function(item){
        return createReviewCard(item);
      },
      prices: function(item){
        return createCard('prices', item, item.category + ' · ' + item.title, item.description, [item.price, visibleLabel(item.visible), '정렬 ' + item.sort]);
      },
      faq: function(item){
        return createCard('faq', item, item.question, item.answer, [visibleLabel(item.visible), '정렬 ' + item.sort]);
      },
      notices: function(item){
        return createCard('notices', item, item.title, item.content, [item.date, visibleLabel(item.visible), '정렬 ' + item.sort]);
      },
      banners: function(item){
        return createCard('banners', item, item.title, item.description, [item.button, item.link, visibleLabel(item.visible), '정렬 ' + item.sort]);
      }
    };
    return renderers[type] || null;
  }

  function visibleLabel(value){
    return value === false ? '숨김' : '표시';
  }

  function renderAll(){
    renderScreen(activeScreen || 'cases');
    renderSearchResults(getSearchQuery());
  }

  function photoCount(photos){
    const count = Array.isArray(photos) ? photos.length : 0;
    return count ? '사진 ' + count + '장' : '사진 없음';
  }

  function renderList(type, renderer){
    const container = document.getElementById(type + 'List');
    if(!container){
      return;
    }
    const items = cmsData[type] || [];
    container.innerHTML = '';
    if(!items.length){
      container.appendChild(emptyCard(type));
      return;
    }
    const limit = Math.min(visibleCounts[type] || INITIAL_RENDER_LIMIT, items.length);
    const fragment = document.createDocumentFragment();
    items.slice(0, limit).forEach(function(item){
      fragment.appendChild(renderer(item));
    });
    container.appendChild(fragment);
    if(limit < items.length){
      container.appendChild(loadMoreButton(type, limit, items.length));
    }
  }

  function loadMoreButton(type, shown, total){
    const wrap = document.createElement('div');
    wrap.className = 'load-more-row';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'secondary-btn';
    button.dataset.action = 'load-more';
    button.dataset.type = type;
    button.textContent = '더 보기 ' + shown + ' / ' + total;
    wrap.appendChild(button);
    return wrap;
  }

  function createCaseCard(item){
    const article = document.createElement('article');
    article.className = 'data-item ux-card case-card';

    const image = normalizeImageSrc(item.image || '');
    if(image){
      article.appendChild(createImageMedia('case-media', image, item.title || '작업사례 이미지'));
    }else{
      article.classList.add('case-card--text');
    }

    const content = document.createElement('div');
    content.className = 'ux-card-content';
    const head = document.createElement('div');
    head.className = 'data-item-head';
    const titleWrap = document.createElement('div');
    const strong = document.createElement('strong');
    strong.textContent = item.title || '제목 없음';
    titleWrap.appendChild(strong);
    head.appendChild(titleWrap);
    head.appendChild(cardActions('cases', item));
    content.appendChild(head);

    const paragraph = document.createElement('p');
    paragraph.textContent = item.description || '내용 없음';
    content.appendChild(paragraph);
    appendMeta(content, [item.service, item.region, item.date, item.featured ? '대표' : '', item.image ? '이미지 있음' : '텍스트 카드', visibleLabel(item.visible), '정렬 ' + item.sort]);
    article.appendChild(content);
    return article;
  }

  function createReviewCard(item){
    const article = document.createElement('article');
    article.className = 'data-item ux-card review-card';
    const image = normalizeImageSrc(item.image || '');
    if(image){
      article.appendChild(createImageMedia('review-media', image, item.title || '고객후기 이미지'));
    }else{
      article.classList.add('review-card--text');
    }

    const content = document.createElement('div');
    content.className = 'ux-card-content';
    const head = document.createElement('div');
    head.className = 'data-item-head';
    const titleWrap = document.createElement('div');
    const strong = document.createElement('strong');
    strong.textContent = item.title || ((item.service || '고객') + ' 후기');
    titleWrap.appendChild(strong);
    head.appendChild(titleWrap);
    head.appendChild(cardActions('reviews', item));
    content.appendChild(head);

    const rating = Math.max(1, Math.min(5, Number(item.rating || 5)));
    const ratingRow = document.createElement('div');
    ratingRow.className = 'rating-row';
    const stars = document.createElement('span');
    stars.className = 'rating-stars';
    stars.setAttribute('aria-label', rating + '점');
    stars.textContent = '★★★★★'.slice(0, rating) + '☆☆☆☆☆'.slice(0, 5 - rating);
    const score = document.createElement('span');
    score.textContent = rating + '.0';
    ratingRow.appendChild(stars);
    ratingRow.appendChild(score);
    content.appendChild(ratingRow);

    const paragraph = document.createElement('p');
    paragraph.textContent = item.content || '내용 없음';
    content.appendChild(paragraph);
    appendMeta(content, [item.service, item.region, item.source, item.date, item.image ? '이미지 있음' : '텍스트 카드', visibleLabel(item.visible), '정렬 ' + item.sort]);
    article.appendChild(content);
    return article;
  }

  function createImageMedia(className, src, alt){
    const media = document.createElement('div');
    media.className = className;
    const img = document.createElement('img');
    img.alt = alt || 'image';
    img.loading = 'lazy';
    img.src = src;
    media.appendChild(img);
    return media;
  }

  function normalizeImageSrc(src){
    if(!src || src.indexOf('data:') === 0 || src.indexOf('/') === 0 || src.indexOf('../') === 0 || /^https?:\/\//i.test(src)){
      return src;
    }
    return src.indexOf('images/') === 0 ? '../' + src : src;
  }

  function isLikelyImageUrl(src){
    const value = cleanText(src);
    if(!value){
      return true;
    }
    if(/[<>"\s]/.test(value)){
      return false;
    }
    if(/^data:image\//i.test(value)){
      return true;
    }
    if(/^https?:\/\//i.test(value)){
      try {
        new URL(value);
        return true;
      } catch(error) {
        return false;
      }
    }
    if(value.indexOf('/') === 0 || value.indexOf('../') === 0 || value.indexOf('./') === 0 || value.indexOf('images/') === 0 || value.indexOf('assets/') === 0){
      return /\.(avif|gif|jpe?g|png|svg|webp)(\?.*)?$/i.test(value);
    }
    return /\.(avif|gif|jpe?g|png|svg|webp)(\?.*)?$/i.test(value);
  }

  function cardActions(type, item){
    const actions = document.createElement('div');
    actions.className = 'card-actions compact-actions';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'icon-btn';
    button.dataset.action = 'card-menu';
    button.setAttribute('aria-label', '카드 작업');
    button.textContent = '...';
    actions.appendChild(button);

    const menu = document.createElement('div');
    menu.className = 'card-menu is-hidden';
    const edit = document.createElement('button');
    edit.type = 'button';
    edit.className = 'secondary-btn';
    edit.dataset.action = 'edit';
    edit.dataset.type = type;
    edit.dataset.id = item.id;
    edit.textContent = '수정';
    menu.appendChild(edit);

    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'danger-btn';
    remove.dataset.action = 'delete';
    remove.dataset.type = type;
    remove.dataset.id = item.id;
    remove.textContent = '삭제';
    menu.appendChild(remove);
    actions.appendChild(menu);
    return actions;
  }

  function appendMeta(parent, meta){
    const values = (meta || []).filter(Boolean);
    if(!values.length){
      return;
    }
    const metaWrap = document.createElement('div');
    metaWrap.className = 'data-meta';
    values.forEach(function(value){
      const span = document.createElement('span');
      span.textContent = value;
      metaWrap.appendChild(span);
    });
    parent.appendChild(metaWrap);
  }

  function createCard(type, item, title, body, meta){
    const article = document.createElement('article');
    article.className = 'data-item';

    const head = document.createElement('div');
    head.className = 'data-item-head';
    const titleWrap = document.createElement('div');
    const strong = document.createElement('strong');
    strong.textContent = title || '제목 없음';
    titleWrap.appendChild(strong);
    head.appendChild(titleWrap);

    const actions = document.createElement('div');
    actions.className = 'card-actions';
    const edit = document.createElement('button');
    edit.type = 'button';
    edit.className = 'secondary-btn';
    edit.dataset.action = 'edit';
    edit.dataset.type = type;
    edit.dataset.id = item.id;
    edit.textContent = '수정';
    actions.appendChild(edit);

    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'danger-btn';
    remove.dataset.action = 'delete';
    remove.dataset.type = type;
    remove.dataset.id = item.id;
    remove.textContent = '삭제';
    actions.appendChild(remove);
    head.appendChild(actions);
    article.appendChild(head);

    const paragraph = document.createElement('p');
    paragraph.textContent = body || '내용 없음';
    article.appendChild(paragraph);

    if(meta && meta.filter(Boolean).length){
      const metaWrap = document.createElement('div');
      metaWrap.className = 'data-meta';
      meta.filter(Boolean).forEach(function(value){
        const span = document.createElement('span');
        span.textContent = value;
        metaWrap.appendChild(span);
      });
      article.appendChild(metaWrap);
    }
    return article;
  }

  function emptyCard(type){
    const article = document.createElement('article');
    article.className = 'data-item';
    const strong = document.createElement('strong');
    strong.textContent = '데이터 없음';
    const paragraph = document.createElement('p');
    paragraph.textContent = (editorTitles[type] || '항목') + ' 데이터를 추가해 주세요.';
    article.appendChild(strong);
    article.appendChild(paragraph);
    return article;
  }

  function renderSettings(){
    const list = document.getElementById('settingsList');
    const settings = cmsData.settings || fallbackData.settings;
    list.innerHTML = '';
    Object.keys(settings).forEach(function(key){
      const article = document.createElement('article');
      article.className = 'data-item';
      const strong = document.createElement('strong');
      strong.textContent = key;
      const paragraph = document.createElement('p');
      paragraph.textContent = typeof settings[key] === 'object' ? JSON.stringify(settings[key]) : String(settings[key]);
      article.appendChild(strong);
      article.appendChild(paragraph);
      list.appendChild(article);
    });
  }

  function requestDelete(type, id){
    const item = getItem(type, id);
    if(!item){
      return;
    }
    pendingDelete = { type: type, id: id };
    const modal = document.getElementById('confirmModal');
    const message = document.getElementById('confirmMessage');
    if(message){
      message.textContent = (item.title || item.service || item.question || '선택한 항목') + ' 삭제 후 5초 동안 되돌릴 수 있습니다.';
    }
    if(modal){
      modal.classList.remove('is-hidden');
      modal.setAttribute('aria-hidden', 'false');
    }
  }

  function closeConfirmModal(){
    pendingDelete = null;
    const modal = document.getElementById('confirmModal');
    if(modal){
      modal.classList.add('is-hidden');
      modal.setAttribute('aria-hidden', 'true');
    }
  }

  function confirmDelete(){
    if(!pendingDelete){
      return;
    }
    const target = pendingDelete;
    closeConfirmModal();
    deleteItem(target.type, target.id);
  }

  function restoreDeletedItem(){
    if(!undoDelete){
      showToast('되돌릴 삭제 항목이 없습니다');
      return;
    }
    const list = cmsData[undoDelete.type] || [];
    if(!list.some(function(item){ return item.id === undoDelete.item.id; })){
      list.splice(Math.min(undoDelete.index, list.length), 0, undoDelete.item);
    }
    cmsData[undoDelete.type] = list;
    const restoredType = undoDelete.type;
    undoDelete = null;
    clearTimeout(undoTimer);
    persistData();
    renderScreen(restoredType);
    renderSearchResults(getSearchQuery());
    showToast('삭제를 되돌렸습니다');
    setStatus('삭제를 되돌렸습니다');
  }

  function toggleCardMenu(button){
    const actions = button.closest('.card-actions');
    const menu = actions ? actions.querySelector('.card-menu') : null;
    if(!menu){
      return;
    }
    const shouldOpen = menu.classList.contains('is-hidden');
    closeCardMenus();
    menu.classList.toggle('is-hidden', !shouldOpen);
    button.setAttribute('aria-expanded', String(shouldOpen));
  }

  function closeCardMenus(){
    document.querySelectorAll('.card-menu').forEach(function(menu){
      menu.classList.add('is-hidden');
    });
    document.querySelectorAll('[data-action="card-menu"]').forEach(function(button){
      button.setAttribute('aria-expanded', 'false');
    });
  }

  function showToast(message, options){
    const container = document.getElementById('toastContainer');
    if(!container){
      return;
    }
    const settings = options || {};
    const toast = document.createElement('div');
    toast.className = 'toast';
    const text = document.createElement('span');
    text.textContent = message;
    toast.appendChild(text);
    if(settings.action){
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'secondary-btn';
      button.dataset.action = settings.action;
      button.textContent = settings.label || '실행';
      toast.appendChild(button);
    }
    container.appendChild(toast);
    setTimeout(function(){
      toast.classList.add('is-leaving');
      setTimeout(function(){
        toast.remove();
      }, 180);
    }, settings.timeout || 3200);
  }

  function getSearchQuery(){
    const input = document.getElementById('globalSearch');
    return input ? input.value.trim() : '';
  }

  function renderSearchResults(query){
    const panel = document.getElementById('searchPanel');
    if(!panel){
      return;
    }
    const value = (query || '').trim().toLowerCase();
    panel.innerHTML = '';
    if(!value){
      panel.classList.add('is-hidden');
      return;
    }

    const types = contentTypes;
    const results = [];
    types.forEach(function(type){
      (cmsData[type] || []).forEach(function(item){
        if(results.length >= SEARCH_RESULT_LIMIT){
          return;
        }
        if(searchableText(type, item).toLowerCase().indexOf(value) !== -1){
          results.push({ type: type, item: item });
        }
      });
    });

    const head = document.createElement('div');
    head.className = 'search-panel-head';
    const title = document.createElement('strong');
    title.textContent = '통합 검색';
    const count = document.createElement('span');
    count.textContent = results.length ? results.length + '개 결과' : '결과 없음';
    head.appendChild(title);
    head.appendChild(count);
    panel.appendChild(head);

    if(!results.length){
      const empty = document.createElement('p');
      empty.className = 'search-empty';
      empty.textContent = '검색 결과가 없습니다.';
      panel.appendChild(empty);
      panel.classList.remove('is-hidden');
      return;
    }

    const list = document.createElement('div');
    list.className = 'search-results';
    results.forEach(function(result){
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'search-result';
      button.dataset.action = 'edit';
      button.dataset.type = result.type;
      button.dataset.id = result.item.id;

      const label = document.createElement('span');
      label.textContent = titles[result.type] || result.type;
      const heading = document.createElement('strong');
      heading.textContent = resultTitle(result.type, result.item);
      const body = document.createElement('small');
      body.textContent = resultSummary(result.type, result.item);
      button.appendChild(label);
      button.appendChild(heading);
      button.appendChild(body);
      list.appendChild(button);
    });
    panel.appendChild(list);
    panel.classList.remove('is-hidden');
  }

  function searchableText(type, item){
    const fields = {
      cases: ['title', 'service', 'region', 'description', 'image', 'date'],
      reviews: ['title', 'service', 'region', 'content', 'image', 'source', 'rating', 'date'],
      prices: ['category', 'title', 'price', 'description'],
      faq: ['question', 'answer'],
      notices: ['title', 'content', 'date'],
      banners: ['title', 'description', 'button', 'link']
    };
    const values = [titles[type] || '', editorTitles[type] || '', resultTitle(type, item)];
    return values.concat((fields[type] || []).map(function(key){
      return item && item[key] ? String(item[key]) : '';
    })).join(' ');
  }

  function resultTitle(type, item){
    if(type === 'reviews'){
      return item.title || ((item.service || '고객') + ' 후기');
    }
    return item.title || item.question || item.category || item.service || '제목 없음';
  }

  function resultSummary(type, item){
    const text = item.description || item.content || item.answer || item.price || item.button || '';
    return String(text).slice(0, 90);
  }

  function bindDraftAutosave(form, type, id){
    if(!form){
      return;
    }
    form.addEventListener('input', function(){
      scheduleDraftSave(form, type, id);
    });
    form.addEventListener('change', function(){
      scheduleDraftSave(form, type, id);
    });
  }

  function scheduleDraftSaveForActiveForm(){
    const form = document.querySelector('.editor-form');
    if(form){
      scheduleDraftSave(form, form.dataset.type, form.dataset.id || '');
    }
  }

  function scheduleDraftSave(form, type, id){
    clearTimeout(draftTimer);
    draftTimer = setTimeout(function(){
      saveFormDraft(form, type, id);
    }, DRAFT_SAVE_DELAY);
  }

  function saveFormDraft(form, type, id){
    const values = formValues(form);
    const photos = type === 'cases' ? activePhotoData.slice() : [];
    const drafts = getFormDrafts();
    const key = draftKey(type, id);
    if(!hasDraftContent(values, photos)){
      delete drafts[key];
      setFormDrafts(drafts);
      return;
    }
    drafts[key] = {
      type: type,
      id: id,
      values: values,
      photos: photos,
      updatedAt: Date.now()
    };
    setFormDrafts(drafts);
    setStatus('임시저장됨');
  }

  function promptDraftRestore(form, type, id){
    const draft = getFormDrafts()[draftKey(type, id)];
    if(!form || !draft){
      return;
    }
    activeDraftContext = {
      form: form,
      type: type,
      id: id,
      draft: draft
    };
    const modal = document.getElementById('draftModal');
    if(modal){
      modal.classList.remove('is-hidden');
      modal.setAttribute('aria-hidden', 'false');
    }
  }

  function restoreActiveDraft(){
    if(!activeDraftContext){
      return;
    }
    applyDraftValues(activeDraftContext.form, activeDraftContext.draft.values || {});
    refreshImageUrlPreviews(activeDraftContext.form);
    if(activeDraftContext.type === 'cases'){
      activePhotoData = Array.isArray(activeDraftContext.draft.photos) ? activeDraftContext.draft.photos.slice() : [];
      const preview = activeDraftContext.form.querySelector('[data-photo-preview]');
      if(preview){
        renderPhotoPreview(preview);
      }
    }
    closeDraftModal();
    showToast('임시저장을 복구했습니다');
  }

  function discardActiveDraft(){
    if(activeDraftContext){
      clearFormDraft(activeDraftContext.type, activeDraftContext.id);
    }
    closeDraftModal();
    showToast('임시저장을 삭제했습니다');
  }

  function closeDraftModal(){
    const modal = document.getElementById('draftModal');
    if(modal){
      modal.classList.add('is-hidden');
      modal.setAttribute('aria-hidden', 'true');
    }
  }

  function clearFormDraft(type, id){
    const drafts = getFormDrafts();
    delete drafts[draftKey(type, id)];
    setFormDrafts(drafts);
  }

  function draftKey(type, id){
    return type + ':' + (id || 'new');
  }

  function getFormDrafts(){
    try {
      return JSON.parse(localStorage.getItem(FORM_DRAFT_KEY) || '{}');
    } catch(error) {
      localStorage.removeItem(FORM_DRAFT_KEY);
      return {};
    }
  }

  function setFormDrafts(drafts){
    localStorage.setItem(FORM_DRAFT_KEY, JSON.stringify(drafts));
  }

  function formValues(form){
    const values = Object.fromEntries(new FormData(form).entries());
    Array.from(form.elements).forEach(function(element){
      if(element.name && element.type === 'file'){
        delete values[element.name];
      }
      if(element.name && element.type === 'checkbox'){
        values[element.name] = element.checked;
      }
    });
    return values;
  }

  function applyDraftValues(form, values){
    Array.from(form.elements).forEach(function(element){
      if(!element.name || !(element.name in values)){
        return;
      }
      if(element.type === 'checkbox'){
        element.checked = values[element.name] === true || values[element.name] === 'on';
      }else{
        element.value = values[element.name] || '';
      }
    });
  }

  function hasDraftContent(values, photos){
    return Object.keys(values || {}).some(function(key){
      const value = values[key];
      return value === true || (typeof value === 'string' && value.trim());
    }) || (Array.isArray(photos) && photos.length > 0);
  }

  function renderJsonScreen(){
    const result = document.getElementById('jsonValidationResult');
    if(result && !result.textContent){
      writeJsonResult(result, ['타입별 내보내기 전 필수 필드와 금지 필드를 검증합니다.'], 'neutral');
    }
  }

  function buildSaveTargetPreviews(){
    return saveTargetTypes.map(function(type){
      const config = typeConfig[type];
      const payload = buildHomepagePayload(type);
      const validation = validateSaveTarget(type, payload);
      const jsonText = JSON.stringify(payload, null, 2);
      return {
        type: type,
        file: config.file,
        path: 'data/' + config.file,
        payload: payload,
        validation: validation,
        jsonText: jsonText,
        canSave: validation.errors.length === 0
      };
    });
  }

  function renderSaveTargetPreview(){
    const container = document.getElementById('jsonSavePreviewResult');
    if(!container){
      return;
    }
    const startedAt = Date.now();
    const fragment = document.createDocumentFragment();
    let totalErrors = 0;
    const targets = buildSaveTargetPreviews();

    container.innerHTML = '';
    targets.forEach(function(target){
      const config = typeConfig[target.type];
      const payload = target.payload;
      const validation = target.validation;
      const jsonText = target.jsonText;
      const hasErrors = !target.canSave;
      totalErrors += validation.errors.length;

      const card = document.createElement('article');
      card.className = 'save-preview-item';
      card.classList.toggle('is-blocked', hasErrors);

      const head = document.createElement('div');
      head.className = 'save-preview-head';
      const title = document.createElement('strong');
      title.textContent = config.file;
      const badge = document.createElement('span');
      badge.textContent = hasErrors ? '저장 불가' : '저장 가능';
      head.appendChild(title);
      head.appendChild(badge);
      card.appendChild(head);

      const path = document.createElement('code');
      path.className = 'save-preview-path';
      path.textContent = 'data/' + config.file;
      card.appendChild(path);

      const summary = document.createElement('p');
      summary.className = 'save-preview-summary';
      summary.textContent = config.file + ': ' + payload.length + '개 / 오류 ' + validation.errors.length + '개 / ' + (hasErrors ? '저장 불가' : '저장 가능');
      card.appendChild(summary);

      if(validation.errors.length){
        const errorList = document.createElement('ul');
        errorList.className = 'save-preview-errors';
        validation.errors.slice(0, 6).forEach(function(error){
          const item = document.createElement('li');
          item.textContent = error;
          errorList.appendChild(item);
        });
        if(validation.errors.length > 6){
          const more = document.createElement('li');
          more.textContent = '외 ' + (validation.errors.length - 6) + '개 오류';
          errorList.appendChild(more);
        }
        card.appendChild(errorList);
      }

      const details = document.createElement('details');
      const detailsTitle = document.createElement('summary');
      detailsTitle.textContent = 'JSON 내용 미리보기';
      const preview = document.createElement('pre');
      preview.textContent = formatJsonPreview(jsonText);
      details.appendChild(detailsTitle);
      details.appendChild(preview);
      card.appendChild(details);

      fragment.appendChild(card);
    });

    container.appendChild(fragment);
    const elapsed = Date.now() - startedAt;
    setStatus(totalErrors ? '저장 준비 오류 확인됨' : '저장 대상 미리보기 완료');
    showToast(totalErrors ? '저장 불가 항목을 확인하세요' : '저장 대상 미리보기 완료');
    container.dataset.previewMs = String(elapsed);
  }

  function saveJsonTargets(){
    const targets = buildSaveTargetPreviews();
    const totalErrors = targets.reduce(function(sum, target){
      return sum + target.validation.errors.length;
    }, 0);
    renderSaveTargetPreview();
    if(totalErrors){
      showToast('저장 전 검증 오류를 먼저 확인하세요');
      setStatus('저장 API 연결 전 검증 오류');
      return;
    }
    showToast('저장 API 연결 전입니다');
    setStatus('저장 API 연결 전입니다');
  }

  async function reloadLiveJsonData(button){
    if(button){
      button.disabled = true;
    }
    localStorage.removeItem(DATA_KEY);
    localStorage.removeItem(FORM_DRAFT_KEY);
    closeAllEditors();
    await loadData({ forceSample: true });
    visibleCounts = {};
    renderScreen(activeScreen);
    renderSearchResults(getSearchQuery());

    const message = '임시 데이터가 초기화되고 실제 배포 JSON을 다시 불러왔습니다.';
    showToast(message);
    setStatus(message);
    const result = document.getElementById('liveReloadResult');
    if(result){
      result.textContent = message;
    }
    if(button){
      button.disabled = false;
    }
  }

  function formatJsonPreview(jsonText){
    if(jsonText.length <= JSON_PREVIEW_LIMIT){
      return jsonText;
    }
    return jsonText.slice(0, JSON_PREVIEW_LIMIT) + '\n... ' + (jsonText.length - JSON_PREVIEW_LIMIT) + '자 생략';
  }

  function exportJsonType(type){
    if(type === 'backup'){
      exportJson();
      return;
    }
    if(!typeConfig[type]){
      setStatus('알 수 없는 JSON 타입입니다');
      return;
    }
    const payload = buildHomepagePayload(type);
    const validation = validateSaveTarget(type, payload);
    const result = document.getElementById('jsonValidationResult');
    showValidationResult(result, validation, typeConfig[type].file + ' 검증');
    if(validation.errors.length){
      showToast('오류가 있어 내보내기를 중단했습니다');
      setStatus(typeConfig[type].file + ' 내보내기 실패');
      return;
    }
    downloadJson(typeConfig[type].file, payload);
    showToast(typeConfig[type].file + ' 내보내기 완료');
    setStatus(typeConfig[type].file + ' 내보내기 완료');
  }

  function exportJson(){
    const payload = {};
    const combined = { errors: [], warnings: [] };
    contentTypes.forEach(function(type){
      payload[type] = buildHomepagePayload(type);
      const validation = validateSaveTarget(type, payload[type]);
      combined.errors = combined.errors.concat(validation.errors);
      combined.warnings = combined.warnings.concat(validation.warnings);
    });
    const result = document.getElementById('jsonValidationResult');
    showValidationResult(result, combined, '전체 백업 검증');
    if(combined.errors.length){
      showToast('오류가 있어 백업 내보내기를 중단했습니다');
      setStatus('전체 백업 JSON 내보내기 실패');
      return;
    }
    downloadJson('daehan-cleaning-cms-backup.json', payload);
    showToast('전체 백업 JSON 내보내기 완료');
    setStatus('전체 백업 JSON 내보내기 완료');
  }

  function buildHomepagePayload(type){
    return normalizeTypeItems(type, cmsData[type] || []).sort(function(a, b){
      return a.sort - b.sort;
    }).map(function(item){
      const clean = {};
      typeConfig[type].fields.forEach(function(field){
        clean[field] = item[field];
      });
      return clean;
    });
  }

  function validateSaveTarget(type, payload){
    const validation = validateTypeItems(type, payload);
    if(type === 'cases'){
      validation.errors = collectCaseImageFieldErrors(cmsData[type] || []).concat(validation.errors);
    }
    return validation;
  }

  function collectCaseImageFieldErrors(items){
    const errors = [];
    if(!Array.isArray(items)){
      return errors;
    }
    items.forEach(function(item, index){
      if(hasLegacyCaseImageFields(item)){
        errors.push(typeConfig.cases.file + ' #' + (index + 1) + ': beforeImage/afterImage 필드는 사용할 수 없습니다. image 필드 1개만 사용하세요.');
      }
    });
    return errors;
  }

  function hasLegacyCaseImageFields(item){
    return !!item && typeof item === 'object' && !Array.isArray(item) && ('beforeImage' in item || 'afterImage' in item);
  }

  function downloadJson(filename, payload){
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(function(){
      URL.revokeObjectURL(url);
    }, 1000);
  }

  function validateJsonImportText(){
    const parsed = readImportJson();
    const result = document.getElementById('jsonImportResult');
    if(parsed.error){
      writeJsonResult(result, [parsed.error], 'error');
      setStatus('JSON 검증 실패');
      return false;
    }
    const validation = validateParsedImport(parsed.type, parsed.data);
    showValidationResult(result, validation, '가져오기 검증');
    setStatus(validation.errors.length ? 'JSON 검증 실패' : 'JSON 검증 완료');
    return !validation.errors.length;
  }

  function importJsonFromTextarea(){
    const parsed = readImportJson();
    const result = document.getElementById('jsonImportResult');
    if(parsed.error){
      writeJsonResult(result, [parsed.error], 'error');
      setStatus('JSON 가져오기 실패');
      return;
    }
    const validation = validateParsedImport(parsed.type, parsed.data);
    if(validation.errors.length){
      showValidationResult(result, validation, '가져오기 실패');
      showToast('JSON 오류를 확인해 주세요');
      setStatus('JSON 가져오기 실패');
      return;
    }

    if(parsed.type === 'backup'){
      contentTypes.forEach(function(type){
        if(Array.isArray(parsed.data[type])){
          cmsData[type] = normalizeTypeItems(type, parsed.data[type]);
        }
      });
    }else{
      cmsData[parsed.type] = normalizeTypeItems(parsed.type, parsed.data);
    }
    persistData();
    visibleCounts = {};
    renderScreen(activeScreen);
    renderSearchResults(getSearchQuery());
    showValidationResult(result, validation, '가져오기 완료');
    showToast('JSON 가져오기 완료');
    setStatus('JSON 가져오기 완료');
  }

  function readImportJson(){
    const select = document.getElementById('jsonTypeSelect');
    const textarea = document.getElementById('jsonImportText');
    const type = select ? select.value : '';
    const text = textarea ? textarea.value.trim() : '';
    if(!type){
      return { error: '데이터 종류를 선택해 주세요.' };
    }
    if(!text){
      return { error: '가져올 JSON 내용을 붙여넣어 주세요.' };
    }
    try {
      return { type: type, data: JSON.parse(text) };
    } catch(error) {
      return { error: 'JSON 형식이 올바르지 않습니다: ' + error.message };
    }
  }

  function validateParsedImport(type, data){
    if(type === 'backup'){
      const combined = { errors: [], warnings: [] };
      if(!data || typeof data !== 'object' || Array.isArray(data)){
        combined.errors.push('전체 백업 JSON은 객체 형식이어야 합니다.');
        return combined;
      }
      contentTypes.forEach(function(itemType){
        if(Array.isArray(data[itemType])){
          const validation = validateTypeItems(itemType, data[itemType]);
          combined.errors = combined.errors.concat(validation.errors);
          combined.warnings = combined.warnings.concat(validation.warnings);
        }
      });
      if(!contentTypes.some(function(itemType){ return Array.isArray(data[itemType]); })){
        combined.errors.push('백업 JSON에 가져올 데이터 타입이 없습니다.');
      }
      return combined;
    }
    return validateTypeItems(type, data);
  }

  function validateTypeItems(type, items){
    const config = typeConfig[type];
    const result = { errors: [], warnings: [] };
    if(!config){
      result.errors.push('알 수 없는 데이터 타입입니다.');
      return result;
    }
    if(!Array.isArray(items)){
      result.errors.push(config.file + ' 데이터는 배열이어야 합니다.');
      return result;
    }
    items.forEach(function(item, index){
      const row = config.file + ' #' + (index + 1);
      if(!item || typeof item !== 'object' || Array.isArray(item)){
        result.errors.push(row + ': 객체 형식이어야 합니다.');
        return;
      }
      if(type === 'cases' && ('beforeImage' in item || 'afterImage' in item)){
        result.errors.push(row + ': beforeImage/afterImage 필드는 사용할 수 없습니다. image 필드 1개만 사용하세요.');
      }
      if((type === 'cases' || type === 'reviews') && cleanText(item.image) && !isLikelyImageUrl(item.image)){
        result.warnings.push(row + ': image URL 형식을 확인하세요. 비어 있으면 텍스트 카드로 저장됩니다.');
      }
      config.required.forEach(function(field){
        if(!cleanText(item[field])){
          result.errors.push(row + ': ' + field + ' 값이 비어 있습니다.');
        }
      });
    });
    return result;
  }

  function showValidationResult(container, validation, heading){
    if(!container){
      return;
    }
    const messages = [];
    if(heading){
      messages.push(heading);
    }
    if(validation.errors.length){
      messages.push('오류 ' + validation.errors.length + '개');
      messages.push.apply(messages, validation.errors);
    }
    if(validation.warnings.length){
      messages.push('경고 ' + validation.warnings.length + '개');
      messages.push.apply(messages, validation.warnings.slice(0, 12));
      if(validation.warnings.length > 12){
        messages.push('외 ' + (validation.warnings.length - 12) + '개 경고');
      }
    }
    if(!validation.errors.length && !validation.warnings.length){
      messages.push('검증 통과');
    }
    writeJsonResult(container, messages, validation.errors.length ? 'error' : 'ok');
  }

  function writeJsonResult(container, messages, status){
    if(!container){
      return;
    }
    container.innerHTML = '';
    container.classList.toggle('is-error', status === 'error');
    container.classList.toggle('is-ok', status === 'ok');
    const list = document.createElement('ul');
    (messages || []).forEach(function(message){
      const item = document.createElement('li');
      item.textContent = message;
      list.appendChild(item);
    });
    container.appendChild(list);
  }

  function clone(value){
    return JSON.parse(JSON.stringify(value));
  }

  function setStatus(text){
    document.getElementById('loadStatus').textContent = text;
  }
})();
