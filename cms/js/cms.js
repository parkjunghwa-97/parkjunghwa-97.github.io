(function(){
  const DEFAULT_PIN = '231204';
  const SESSION_KEY = 'daehanCmsSession';
  const LOCK_KEY = 'daehanCmsLock';
  const DATA_KEY = 'daehanCmsDraftData';
  const MAX_ATTEMPTS = 5;
  const LOCK_MINUTES = 10;

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

  document.addEventListener('DOMContentLoaded', function(){
    bindLogin();
    bindNavigation();
    bindPreview();
    bindCrudActions();
    bindSettingsActions();

    if(sessionStorage.getItem(SESSION_KEY) === 'active'){
      showApp();
    }
  });

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
      if(!button){
        return;
      }

      const type = button.dataset.type;
      const action = button.dataset.action;
      const id = button.dataset.id;

      if(action === 'new'){
        openEditor(type);
      }
      if(action === 'edit'){
        openEditor(type, id);
      }
      if(action === 'delete'){
        deleteItem(type, id);
      }
      if(action === 'cancel'){
        closeEditor(type);
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
      closeAllEditors();
      loadData({ forceSample: true }).then(function(){
        renderAll();
        showScreen('settings');
        setStatus('샘플 데이터로 초기화됨');
      });
    });

    document.getElementById('exportDataButton').addEventListener('click', exportJson);
  }

  function showApp(){
    document.getElementById('loginView').classList.add('is-hidden');
    document.getElementById('appView').classList.remove('is-hidden');
    loadData().then(function(){
      renderAll();
      showScreen('cases');
      setStatus('데이터 로드 완료');
    });
  }

  function showScreen(screen){
    document.getElementById('previewPane').classList.add('is-hidden');
    closeAllEditors();
    document.querySelectorAll('.menu-btn').forEach(function(button){
      button.classList.toggle('active', button.dataset.screen === screen);
    });
    document.querySelectorAll('.screen').forEach(function(section){
      section.classList.toggle('active', section.id === 'screen-' + screen);
    });
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
    input.value = value || '';
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
    closeEditor(type);
    renderAll();
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
    cmsData[type] = (cmsData[type] || []).filter(function(item){
      return item.id !== id;
    });
    persistData();
    closeEditor(type);
    renderAll();
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

  function renderAll(){
    renderList('cases', function(item){
      return createCard('cases', item, item.title, item.description, [item.service, item.region, photoCount(item.photos)]);
    });
    renderList('reviews', function(item){
      return createCard('reviews', item, item.service + ' 후기', item.content, [String(item.rating || 5) + '점']);
    });
    renderList('journal', function(item){
      return createCard('journal', item, item.title, item.content, [item.region]);
    });
    renderList('prices', function(item){
      return createCard('prices', item, item.service, item.description, [item.priceText]);
    });
    renderList('faqs', function(item){
      return createCard('faqs', item, item.question, item.answer, []);
    });
    renderList('notices', function(item){
      return createCard('notices', item, item.title, item.content, [item.startDate, item.endDate, item.published ? '게시' : '미게시']);
    });
    renderList('banner', function(item){
      return createCard('banner', item, item.title, item.message, [item.image, item.published ? '게시' : '미게시']);
    });
    renderSettings();
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
    items.forEach(function(item){
      container.appendChild(renderer(item));
    });
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
