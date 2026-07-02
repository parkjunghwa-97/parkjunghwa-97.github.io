(function(){
  const DEFAULT_PIN = '231204';
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

  const serviceOptions = ['특수청소', '쓰레기집청소', '유품정리', '화재복구', '누수복구'];
  const fallbackData = {
    cases: [
      {
        id: 'case-001',
        title: '강서구 원룸 특수청소',
        service: '특수청소',
        region: '서울 강서구',
        description: '생활 폐기물 정리와 바닥 살균을 함께 진행한 작업사례입니다.',
        photos: ['../images/reviews/review-02.jpg'],
        createdAt: '2026-07-01'
      },
      {
        id: 'case-002',
        title: '남양주 누수복구 현장',
        service: '누수복구',
        region: '경기 남양주',
        description: '누수 이후 오염 구역 정리와 건조 상담을 진행한 샘플 작업사례입니다.',
        photos: [],
        createdAt: '2026-07-01'
      }
    ],
    reviews: [
      {
        id: 'review-001',
        service: '유품정리',
        rating: 5,
        content: '상담부터 정리까지 차분하게 안내해주셔서 큰 도움이 됐습니다.',
        createdAt: '2026-07-01'
      },
      {
        id: 'review-002',
        service: '쓰레기집청소',
        rating: 5,
        content: '사진으로 진행 상황을 공유해주셔서 믿고 맡길 수 있었습니다.',
        createdAt: '2026-07-01'
      }
    ],
    journal: [
      {
        id: 'journal-001',
        title: '인천 부평구 주거 청소 기록',
        region: '인천 부평구',
        content: '입구 동선 확보 후 폐기물 분류, 반출, 살균 순서로 작업했습니다.',
        createdAt: '2026-07-01'
      }
    ],
    prices: [
      {
        id: 'price-001',
        service: '특수청소',
        priceText: '현장 확인 후 견적',
        description: '오염도, 폐기물 양, 작업 인원, 장비 투입 여부에 따라 안내합니다.'
      },
      {
        id: 'price-002',
        service: '화재복구',
        priceText: '상담 후 견적',
        description: '그을음 범위, 냄새 제거, 폐기물 처리 범위를 확인한 뒤 안내합니다.'
      }
    ],
    faqs: [
      {
        id: 'faq-001',
        question: '당일 상담이 가능한가요?',
        answer: '가능한 일정은 현장 위치와 작업 범위를 확인한 뒤 안내합니다.'
      },
      {
        id: 'faq-002',
        question: '보험 제출 서류 상담도 가능한가요?',
        answer: '화재복구, 누수복구 등 보험 접수가 필요한 현장은 상담 시 서류 발급 가능 여부를 함께 안내합니다.'
      }
    ],
    notices: [
      {
        id: 'notice-001',
        title: '여름철 긴급 복구 상담 안내',
        content: '누수와 악취 관련 상담이 늘어나는 기간에는 사진을 함께 보내주시면 빠르게 확인할 수 있습니다.',
        startDate: '2026-07-01',
        endDate: '2026-08-31',
        published: true
      }
    ],
    banner: [
      {
        id: 'banner-001',
        title: '대한청소만세',
        message: '현장 상황에 맞춘 청소와 복구 상담을 안내합니다.',
        image: '../hero.jpg',
        published: true
      }
    ],
    settings: {
      cmsVersion: '1.6',
      initialPin: '231204',
      dataMode: 'localStorage',
      customerSite: 'https://xn--vk1by2k4ygtjy88bcjm.kr/',
      adminPath: '/cms/',
      nextStep: 'V2 GitHub 자동 커밋/배포 및 고객 홈페이지 JSON 연동'
    }
  };

  const dataFiles = {
    cases: '../data/cases.json',
    reviews: '../data/reviews.json',
    journal: '../data/journal.json',
    prices: '../data/prices.json',
    faqs: '../data/faqs.json',
    notices: '../data/notices.json',
    banner: '../data/banners.json',
    settings: '../data/settings.json'
  };

  const titles = {
    cases: '작업사례 관리',
    reviews: '고객후기 관리',
    journal: '현장기록 관리',
    prices: '비용안내 관리',
    faqs: 'FAQ 관리',
    notices: '공지 관리',
    banner: '메인배너 관리',
    settings: '설정'
  };

  const editorTitles = {
    cases: '작업사례',
    reviews: '고객후기',
    journal: '현장기록',
    prices: '비용안내',
    faqs: 'FAQ',
    notices: '공지',
    banner: '메인배너'
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

  document.addEventListener('DOMContentLoaded', function(){
    installUxChrome();
    bindLogin();
    bindNavigation();
    bindPreview();
    bindCrudActions();
    bindSettingsActions();

    if(sessionStorage.getItem(SESSION_KEY) === 'active'){
      showApp();
    }
  });

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

      if(input.value === DEFAULT_PIN){
        localStorage.removeItem(LOCK_KEY);
        sessionStorage.setItem(SESSION_KEY, 'active');
        input.value = '';
        message.textContent = '';
        showApp();
        return;
      }

      const nextAttempts = lock.attempts + 1;
      const lockData = {
        attempts: nextAttempts,
        until: nextAttempts >= MAX_ATTEMPTS ? Date.now() + LOCK_MINUTES * 60 * 1000 : 0
      };
      localStorage.setItem(LOCK_KEY, JSON.stringify(lockData));
      message.textContent = nextAttempts >= MAX_ATTEMPTS ? remainingLockText(lockData.until) : 'PIN이 일치하지 않습니다. 남은 시도: ' + (MAX_ATTEMPTS - nextAttempts);
    });
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
    document.addEventListener('click', function(event){
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

    document.getElementById('exportDataButton').addEventListener('click', exportJson);
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
    const normalized = clone(fallbackData);
    Object.keys(data || {}).forEach(function(key){
      normalized[key] = data[key];
    });
    if(!Array.isArray(normalized.banner)){
      normalized.banner = normalized.banner ? [normalized.banner] : [];
    }
    ['cases', 'reviews', 'journal', 'prices', 'faqs', 'notices', 'banner'].forEach(function(key){
      if(!Array.isArray(normalized[key])){
        normalized[key] = [];
      }
    });
    normalized.settings = Object.assign({}, fallbackData.settings, normalized.settings || {}, { cmsVersion: '1.6', dataMode: 'localStorage' });
    return normalized;
  }

  function openEditor(type, id){
    const panel = document.getElementById(type + 'Editor');
    const item = id ? getItem(type, id) : null;
    activePhotoData = type === 'cases' && item && Array.isArray(item.photos) ? item.photos.slice() : [];
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
    ['cases', 'reviews', 'journal', 'prices', 'faqs', 'notices', 'banner'].forEach(closeEditor);
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
        grid.appendChild(inputField(field, item ? item[field.name] : ''));
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
    const map = {
      cases: [
        { name: 'photos', label: '사진', kind: 'photos' },
        commonService,
        { name: 'region', label: '지역 입력', kind: 'text', placeholder: '예: 서울 강서구' },
        { name: 'title', label: '제목 입력', kind: 'text', placeholder: '예: 강서구 원룸 특수청소' },
        { name: 'description', label: '설명 입력', kind: 'textarea', placeholder: '작업 전 상황과 처리 내용을 입력' }
      ],
      reviews: [
        commonService,
        { name: 'rating', label: '별점 선택', kind: 'select', options: ['5', '4', '3', '2', '1'] },
        { name: 'content', label: '후기 내용 입력', kind: 'textarea', placeholder: '고객 후기 내용을 붙여넣기' }
      ],
      journal: [
        { name: 'title', label: '현장명', kind: 'text', placeholder: '예: 인천 부평구 주거 청소 기록' },
        { name: 'region', label: '지역', kind: 'text', placeholder: '예: 인천 부평구' },
        { name: 'content', label: '기록 내용', kind: 'textarea', placeholder: '현장 상황과 작업 메모를 입력' }
      ],
      prices: [
        { name: 'service', label: '서비스명', kind: 'text', placeholder: '예: 특수청소' },
        { name: 'priceText', label: '가격 문구', kind: 'text', placeholder: '예: 현장 확인 후 견적' },
        { name: 'description', label: '안내 문구', kind: 'textarea', placeholder: '가격 산정 기준과 안내 문구를 입력' }
      ],
      faqs: [
        { name: 'question', label: '질문', kind: 'text', placeholder: '예: 당일 상담이 가능한가요?' },
        { name: 'answer', label: '답변', kind: 'textarea', placeholder: '답변 내용을 입력' }
      ],
      notices: [
        { name: 'title', label: '제목', kind: 'text', placeholder: '예: 여름철 긴급 복구 상담 안내' },
        { name: 'content', label: '내용', kind: 'textarea', placeholder: '공지 내용을 입력' },
        { name: 'startDate', label: '시작일', kind: 'date' },
        { name: 'endDate', label: '종료일', kind: 'date' },
        { name: 'published', label: '게시 여부', kind: 'checkbox' }
      ],
      banner: [
        { name: 'title', label: '배너 제목', kind: 'text', placeholder: '예: 대한청소만세' },
        { name: 'message', label: '배너 문구', kind: 'textarea', placeholder: '메인 화면에 표시할 안내 문구' },
        { name: 'image', label: '배경 이미지 경로', kind: 'text', placeholder: '예: /hero.jpg' },
        { name: 'published', label: '게시 여부', kind: 'checkbox' }
      ]
    };
    return map[type] || [];
  }

  function inputField(field, value){
    const label = document.createElement('label');
    if(field.kind === 'textarea' || field.name === 'content' || field.name === 'description' || field.name === 'answer' || field.name === 'message'){
      label.className = 'full';
    }

    if(field.kind === 'checkbox'){
      label.className = 'checkbox-row';
      const input = document.createElement('input');
      input.name = field.name;
      input.type = 'checkbox';
      input.checked = value === true || value === 'on' || value === '';
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
    }
    input.name = field.name;
    if(field.kind === 'select'){
      if(value){
        input.value = value;
      }
    }else{
      input.value = value || '';
    }
    if(field.placeholder){
      input.placeholder = field.placeholder;
    }
    if(field.name !== 'image'){
      input.required = field.kind !== 'date';
    }
    label.appendChild(input);
    return label;
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
    const values = Object.fromEntries(new FormData(form).entries());
    const existing = id ? getItem(type, id) || {} : {};
    values.id = id || type + '-' + Date.now();
    if(type === 'cases'){
      values.photos = activePhotoData.slice();
    }
    if(type === 'reviews'){
      values.rating = Number(values.rating || 5);
    }
    if(type === 'notices' || type === 'banner'){
      values.published = form.elements.published ? form.elements.published.checked : false;
    }
    values.createdAt = existing.createdAt || new Date().toISOString().slice(0, 10);
    values.updatedAt = new Date().toISOString().slice(0, 10);
    return Object.assign({}, existing, values);
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
    const renderer = getRenderer(type);
    if(renderer){
      renderList(type, renderer);
    }
  }

  function getRenderer(type){
    const renderers = {
      cases: function(item){
        return createCaseCard(item);
      },
      reviews: function(item){
        return createReviewCard(item);
      },
      journal: function(item){
        return createCard('journal', item, item.title, item.content, [item.region]);
      },
      prices: function(item){
        return createCard('prices', item, item.service, item.description, [item.priceText]);
      },
      faqs: function(item){
        return createCard('faqs', item, item.question, item.answer, []);
      },
      notices: function(item){
        return createCard('notices', item, item.title, item.content, [item.startDate, item.endDate, item.published ? '게시' : '미게시']);
      },
      banner: function(item){
        return createCard('banner', item, item.title, item.message, [item.image, item.published ? '게시' : '미게시']);
      }
    };
    return renderers[type] || null;
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

    const media = document.createElement('div');
    media.className = 'case-media';
    const photo = firstPhoto(item.photos);
    if(photo.src){
      const img = document.createElement('img');
      img.alt = photo.name || item.title || '작업사례 이미지';
      img.loading = 'lazy';
      img.src = photo.src;
      media.appendChild(img);
    }else{
      const empty = document.createElement('span');
      empty.textContent = 'No image';
      media.appendChild(empty);
    }
    article.appendChild(media);

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
    appendMeta(content, [item.service, item.region, photoCount(item.photos), item.updatedAt || item.createdAt]);
    article.appendChild(content);
    return article;
  }

  function createReviewCard(item){
    const article = document.createElement('article');
    article.className = 'data-item ux-card review-card';

    const content = document.createElement('div');
    content.className = 'ux-card-content';
    const head = document.createElement('div');
    head.className = 'data-item-head';
    const titleWrap = document.createElement('div');
    const strong = document.createElement('strong');
    strong.textContent = (item.service || '고객') + ' 후기';
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
    appendMeta(content, [item.createdAt, item.updatedAt ? '수정 ' + item.updatedAt : '']);
    article.appendChild(content);
    return article;
  }

  function firstPhoto(photos){
    const photo = Array.isArray(photos) && photos.length ? photos[0] : '';
    if(typeof photo === 'string'){
      return { src: normalizeImageSrc(photo), name: photo };
    }
    return {
      src: photo && photo.src ? normalizeImageSrc(photo.src) : '',
      name: photo && photo.name ? photo.name : ''
    };
  }

  function normalizeImageSrc(src){
    if(!src || src.indexOf('data:') === 0 || src.indexOf('/') === 0 || src.indexOf('../') === 0 || src.indexOf('http') === 0){
      return src;
    }
    return src.indexOf('images/') === 0 ? '../' + src : src;
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

    const types = ['cases', 'reviews', 'journal', 'prices', 'faqs', 'notices', 'banner'];
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
      cases: ['title', 'service', 'region', 'description'],
      reviews: ['service', 'content', 'rating'],
      journal: ['title', 'region', 'content'],
      prices: ['service', 'priceText', 'description'],
      faqs: ['question', 'answer'],
      notices: ['title', 'content', 'startDate', 'endDate'],
      banner: ['title', 'message', 'image']
    };
    const values = [titles[type] || '', editorTitles[type] || '', resultTitle(type, item)];
    return values.concat((fields[type] || []).map(function(key){
      return item && item[key] ? String(item[key]) : '';
    })).join(' ');
  }

  function resultTitle(type, item){
    if(type === 'reviews'){
      return (item.service || '고객') + ' 후기';
    }
    return item.title || item.question || item.service || '제목 없음';
  }

  function resultSummary(type, item){
    const text = item.description || item.content || item.answer || item.message || item.priceText || '';
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

  function exportJson(){
    const payload = JSON.stringify(cmsData, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'daehan-cleaning-cms-data.json';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(function(){
      URL.revokeObjectURL(url);
    }, 1000);
    setStatus('JSON 내보내기 완료');
  }

  function clone(value){
    return JSON.parse(JSON.stringify(value));
  }

  function setStatus(text){
    document.getElementById('loadStatus').textContent = text;
  }
})();
