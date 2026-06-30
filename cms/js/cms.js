(function(){
  const DEFAULT_PIN = '231204';
  const SESSION_KEY = 'daehanCmsSession';
  const LOCK_KEY = 'daehanCmsLock';
  const DATA_KEY = 'daehanCmsDraftData';
  const MAX_ATTEMPTS = 5;
  const LOCK_MINUTES = 10;

  const fallbackData = {
    cases: [
      {
        id: 'case-001',
        title: '강서구 원룸 특수청소',
        service: '특수청소',
        region: '서울 강서구',
        description: '생활 폐기물 정리와 바닥 살균을 함께 진행한 작업사례입니다.',
        photos: ['../images/reviews/review-02.jpg']
      },
      {
        id: 'case-002',
        title: '남양주 누수복구 현장',
        service: '누수복구',
        region: '경기 남양주',
        description: '누수 이후 오염 구역 정리와 건조 상담을 진행한 샘플입니다.',
        photos: []
      }
    ],
    reviews: [
      {
        id: 'review-001',
        service: '유품정리',
        rating: 5,
        content: '상담부터 정리까지 차분하게 안내해주셔서 큰 도움이 됐습니다.'
      },
      {
        id: 'review-002',
        service: '쓰레기집청소',
        rating: 5,
        content: '사진으로 진행 상황을 공유해주셔서 믿고 맡길 수 있었습니다.'
      }
    ],
    journal: [
      {
        id: 'journal-001',
        title: '인천 부평구 주거 청소 기록',
        region: '인천 부평구',
        content: '입구 동선 확보 후 폐기물 분류, 반출, 살균 순서로 작업했습니다.'
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
        image: '../hero.jpg'
      }
    ],
    settings: {
      cmsVersion: '1.5',
      initialPin: '231204',
      dataMode: 'json-ready',
      customerSite: 'https://xn--vk1by2k4ygtjy88bcjm.kr/',
      adminPath: '/cms/'
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

  let cmsData = {};

  document.addEventListener('DOMContentLoaded', function(){
    bindLogin();
    bindNavigation();
    bindForms();
    bindPreview();

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

  function bindForms(){
    document.querySelectorAll('form[data-form]').forEach(function(form){
      form.addEventListener('submit', function(event){
        event.preventDefault();
        const type = form.dataset.form;
        const entry = formToEntry(form, type);
        const targetKey = type === 'banner' ? 'banner' : type;

        if(!Array.isArray(cmsData[targetKey])){
          cmsData[targetKey] = [];
        }
        cmsData[targetKey].unshift(entry);
        localStorage.setItem(DATA_KEY, JSON.stringify(cmsData));
        form.reset();
        renderAll();
        setStatus('임시 저장됨');
      });
    });
  }

  function formToEntry(form, type){
    const values = Object.fromEntries(new FormData(form).entries());
    values.id = type + '-' + Date.now();
    if(type === 'cases'){
      const fileInput = form.querySelector('input[type="file"]');
      values.photos = fileInput ? Array.from(fileInput.files).map(function(file){ return file.name; }) : [];
    }
    if(type === 'reviews'){
      values.rating = Number(values.rating || 5);
    }
    if(type === 'notices'){
      values.published = form.elements.published.checked;
    }
    return values;
  }

  function showApp(){
    document.getElementById('loginView').classList.add('is-hidden');
    document.getElementById('appView').classList.remove('is-hidden');
    loadData().then(function(){
      renderAll();
      showScreen('cases');
      setStatus('샘플 데이터 로드 완료');
    });
  }

  function showScreen(screen){
    document.getElementById('previewPane').classList.add('is-hidden');
    document.querySelectorAll('.menu-btn').forEach(function(button){
      button.classList.toggle('active', button.dataset.screen === screen);
    });
    document.querySelectorAll('.screen').forEach(function(section){
      section.classList.toggle('active', section.id === 'screen-' + screen);
    });
    document.getElementById('screenTitle').textContent = titles[screen] || '관리 화면';
  }

  async function loadData(){
    const saved = localStorage.getItem(DATA_KEY);
    if(saved){
      try {
        cmsData = JSON.parse(saved);
        return;
      } catch(error) {
        localStorage.removeItem(DATA_KEY);
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
        return [key, fallbackData[key]];
      }
    }));
    cmsData = Object.fromEntries(entries);
  }

  function renderAll(){
    renderList('casesList', cmsData.cases || [], function(item){
      return card(item.title, item.description, [item.service, item.region]);
    });
    renderList('reviewsList', cmsData.reviews || [], function(item){
      return card(item.service + ' 후기', item.content, [String(item.rating || 5) + '점']);
    });
    renderList('journalList', cmsData.journal || [], function(item){
      return card(item.title, item.content, [item.region]);
    });
    renderList('pricesList', cmsData.prices || [], function(item){
      return card(item.service, item.description, [item.priceText]);
    });
    renderList('faqsList', cmsData.faqs || [], function(item){
      return card(item.question, item.answer, []);
    });
    renderList('noticesList', cmsData.notices || [], function(item){
      return card(item.title, item.content, [item.startDate, item.endDate, item.published ? '게시' : '미게시']);
    });
    renderList('bannerList', cmsData.banner || [], function(item){
      return card(item.title, item.message, [item.image]);
    });
    renderSettings();
  }

  function renderList(id, items, renderer){
    const container = document.getElementById(id);
    if(!container){
      return;
    }
    container.innerHTML = '';
    if(!items.length){
      container.appendChild(card('데이터 없음', '샘플 또는 임시 저장 데이터가 없습니다.', []));
      return;
    }
    items.forEach(function(item){
      container.appendChild(renderer(item));
    });
  }

  function renderSettings(){
    const list = document.getElementById('settingsList');
    const settings = cmsData.settings || fallbackData.settings;
    list.innerHTML = '';
    Object.keys(settings).forEach(function(key){
      list.appendChild(card(key, String(settings[key]), []));
    });
  }

  function card(title, body, meta){
    const item = document.createElement('article');
    item.className = 'data-item';

    const strong = document.createElement('strong');
    strong.textContent = title || '제목 없음';
    item.appendChild(strong);

    const paragraph = document.createElement('p');
    paragraph.textContent = body || '내용 없음';
    item.appendChild(paragraph);

    if(meta && meta.filter(Boolean).length){
      const metaWrap = document.createElement('div');
      metaWrap.className = 'data-meta';
      meta.filter(Boolean).forEach(function(value){
        const span = document.createElement('span');
        span.textContent = value;
        metaWrap.appendChild(span);
      });
      item.appendChild(metaWrap);
    }
    return item;
  }

  function setStatus(text){
    document.getElementById('loadStatus').textContent = text;
  }
})();
