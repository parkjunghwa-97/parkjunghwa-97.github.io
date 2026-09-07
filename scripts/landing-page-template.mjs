// PR-L3: SEO 랜딩페이지 정적 HTML 렌더링. build-landing-pages.mjs에서만 사용합니다.
// 이 파일은 순수 함수만 담아 오프라인 테스트가 쉽도록 build-landing-pages.mjs(오케스트레이션)와
// 분리했습니다.

export function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function escapeAttr(value) {
  return escapeHtml(value);
}

// XML(사이트맵) 전용 이스케이프. HTML 이스케이프와 동일한 5글자만 다루면 충분합니다
// (이 프로젝트의 sitemap.xml에는 URL 문자열만 들어가므로).
export function escapeXml(value) {
  return escapeHtml(value);
}

function paragraphsFromPlainText(text) {
  const cleaned = String(text || '').replace(/\r\n/g, '\n').trim();
  if (!cleaned) {
    return '';
  }
  return cleaned
    .split(/\n{2,}/)
    .map(function (block) {
      const withBreaks = escapeHtml(block).replace(/\n/g, '<br>');
      return '<p>' + withBreaks + '</p>';
    })
    .join('\n');
}

// PR-L2 nav 마크업(onclick="showPage('service')" 등)은 SPA 전용이라, 정적 랜딩페이지에서는
// 실제 이동 가능한 href로 바꿉니다. 추출된 문자열만 변환하고 index.html 원본은 건드리지 않습니다.
export function transformNavForStaticPage(navHtml) {
  let result = navHtml;
  result = result.replace(
    /<div class="nav-brand" onclick="showPage\('home'\)">([\s\S]*?)<\/div>/,
    '<a class="nav-brand" href="/index.html">$1</a>'
  );
  result = result.replace(
    /<button class="([^"]*)" onclick="showPage\('([a-z]+)'\)">([^<]*)<\/button>/g,
    function (match, className, target, label) {
      return '<a class="' + className + '" href="/index.html#' + target + '">' + label + '</a>';
    }
  );
  return result;
}

// index.html의 footer는 상대경로 href="privacy.html"을 쓰는데, 이는 index.html과
// 같은 위치(루트)에서만 유효합니다. 랜딩페이지는 /<slug>/index.html(한 단계 깊은 경로)에
// 있으므로 그대로 두면 /<slug>/privacy.html로 깨집니다. 추출된 footer 문자열만 바꾸고
// index.html 원본은 건드리지 않습니다.
export function transformFooterForStaticPage(footerHtml) {
  return footerHtml.replace(/href="privacy\.html"/g, 'href="/privacy.html"');
}

// settings.json의 contact.telLink만 유효한 "tel:" 링크로 인정합니다(예: "tel:010-4122-9207").
export function isValidTelLink(value) {
  return typeof value === 'string' && /^tel:\+?[0-9-]+$/.test(value.trim());
}

function resolveImagePath(relativePath) {
  const cleaned = String(relativePath || '').trim();
  if (!cleaned) {
    return '';
  }
  return '/' + cleaned.replace(/^\/+/, '');
}

function resolveAbsoluteUrl(domain, relativePath) {
  const cleaned = String(relativePath || '').trim();
  if (!cleaned) {
    return '';
  }
  return domain + '/' + cleaned.replace(/^\/+/, '');
}

function buildImageBlock(className, src, alt, domain) {
  if (!src) {
    return '';
  }
  return '<figure class="' + className + '"><img src="' + escapeAttr(resolveImagePath(src)) + '" alt="' + escapeAttr(alt || '') + '" loading="lazy"></figure>';
}

function buildBeforeAfterBlock(item, domain) {
  if (!item.beforeImage && !item.afterImage) {
    return '';
  }
  const before = item.beforeImage
    ? '<figure><img src="' + escapeAttr(resolveImagePath(item.beforeImage)) + '" alt="' + escapeAttr(item.beforeImageAlt || '') + '" loading="lazy"><figcaption>작업 전</figcaption></figure>'
    : '';
  const after = item.afterImage
    ? '<figure><img src="' + escapeAttr(resolveImagePath(item.afterImage)) + '" alt="' + escapeAttr(item.afterImageAlt || '') + '" loading="lazy"><figcaption>작업 후</figcaption></figure>'
    : '';
  return '<div class="landing-before-after">' + before + after + '</div>';
}

// telLink는 호출 전에 반드시 isValidTelLink()로 검증된 값이어야 합니다(renderLandingPage 참고).
// 확정 설계대로 새 상담 목적지를 만들지 않고 기존 전화 상담 경로를 그대로 재사용합니다.
function buildSupportInfoBlock(item, telLink) {
  if (item.supportInfoEnabled !== true) {
    return '';
  }
  return [
    '<section class="landing-section landing-support-info">',
    '<h3>' + escapeHtml(item.supportInfoTitle) + '</h3>',
    paragraphsFromPlainText(item.supportInfoBody),
    '<p class="landing-support-disclaimer">' + escapeHtml(item.supportInfoDisclaimer) + '</p>',
    '<a class="hero-btn" href="' + escapeAttr(telLink) + '">' + escapeHtml(item.supportInfoCtaText) + '</a>',
    '</section>'
  ].filter(Boolean).join('\n');
}

// FAQ는 화면에 보이는 목록과 JSON-LD가 항상 같은 배열에서 나오도록, 유효한 FAQ만
// 걸러내는 이 함수 하나만 양쪽에서 재사용합니다(구조화 데이터와 화면 내용의 불일치 방지).
export function usableFaqEntries(faq) {
  return (Array.isArray(faq) ? faq : []).filter(function (entry) {
    return entry && typeof entry.question === 'string' && entry.question.trim() !== ''
      && typeof entry.answer === 'string' && entry.answer.trim() !== '';
  });
}

function buildFaqBlock(faqEntries) {
  if (!faqEntries.length) {
    return '';
  }
  const cards = faqEntries.map(function (entry) {
    return '<div class="journal-card"><h3>' + escapeHtml(entry.question) + '</h3><p>' + escapeHtml(entry.answer) + '</p></div>';
  }).join('\n');
  return '<section class="landing-section"><h2>자주 묻는 질문</h2><div class="journal-grid">' + cards + '</div></section>';
}

function buildTrustBadgesBlock(trustBadges) {
  const badges = (Array.isArray(trustBadges) ? trustBadges : []).filter(function (badge) {
    return typeof badge === 'string' && badge.trim() !== '';
  });
  if (!badges.length) {
    return '';
  }
  const items = badges.map(function (badge) {
    return '<li>' + escapeHtml(badge) + '</li>';
  }).join('');
  return '<ul class="landing-trust-badges">' + items + '</ul>';
}

function findServiceById(services, id) {
  return (Array.isArray(services) ? services : []).find(function (s) { return s && s.id === id; });
}

function findCaseById(cases, id) {
  return (Array.isArray(cases) ? cases : []).find(function (c) { return c && c.id === id; });
}

function buildRelatedLinksBlock(item, services, cases) {
  const serviceLinks = (Array.isArray(item.relatedServiceIds) ? item.relatedServiceIds : [])
    .map(function (id) { return findServiceById(services, id); })
    .filter(Boolean)
    .map(function (service) {
      return '<a href="/index.html#service">' + escapeHtml(service.service) + '</a>';
    });
  const caseLinks = (Array.isArray(item.relatedCaseIds) ? item.relatedCaseIds : [])
    .map(function (id) { return findCaseById(cases, id); })
    .filter(Boolean)
    .map(function (c) {
      return '<a href="/index.html#portfolio">' + escapeHtml((c.title || '') + ' · ' + (c.region || '')) + '</a>';
    });
  const links = serviceLinks.concat(caseLinks);
  if (!links.length) {
    return '';
  }
  return '<section class="landing-section landing-related"><h2>관련 서비스 및 작업사례</h2>' + links.join(' ') + '</section>';
}

function buildBreadcrumbHtml(item, canonicalUrl) {
  return '<nav class="landing-breadcrumb" aria-label="breadcrumb"><a href="/">홈</a> <span aria-hidden="true">›</span> <span>' + escapeHtml(item.h1 || item.seoTitle) + '</span></nav>';
}

function buildBreadcrumbSchema(item, domain, canonicalUrl) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: '홈', item: domain + '/' },
      { '@type': 'ListItem', position: 2, name: item.h1 || item.seoTitle, item: canonicalUrl }
    ]
  };
}

function buildFaqSchema(faqEntries) {
  if (!faqEntries.length) {
    return null;
  }
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqEntries.map(function (entry) {
      return {
        '@type': 'Question',
        name: entry.question,
        acceptedAnswer: { '@type': 'Answer', text: entry.answer }
      };
    })
  };
}

export function buildCanonicalUrl(domain, slug) {
  return domain + '/' + slug + '/';
}

export function renderLandingPage(item, ctx) {
  const domain = ctx.domain;
  const canonicalUrl = buildCanonicalUrl(domain, item.slug);
  const faqEntries = usableFaqEntries(item.faq);
  const ogImagePath = item.heroImage
    ? resolveAbsoluteUrl(domain, item.heroImage)
    : resolveAbsoluteUrl(domain, (ctx.settings && ctx.settings.assets && ctx.settings.assets.ogImage) || 'logo.png');

  const jsonLdBlocks = [buildBreadcrumbSchema(item, domain, canonicalUrl)];
  const faqSchema = buildFaqSchema(faqEntries);
  if (faqSchema) {
    jsonLdBlocks.push(faqSchema);
  }

  // 확정 설계: 상담 CTA(지원제도 CTA + 최종 CTA)는 새 목적지를 만들지 않고 기존
  // 전화 상담 경로(settings.contact.telLink)를 그대로 재사용합니다. 이 값이 없거나
  // 형식이 잘못됐는데 CTA를 렌더링해야 하는 상황이면, 깨진/빈 href를 만드는 대신
  // 빌드 자체를 실패시킵니다(이 예외는 build-landing-pages.mjs의 main()이 그대로
  // 잡아 빌드 실패로 처리합니다).
  const telLink = ctx.settings && ctx.settings.contact && ctx.settings.contact.telLink;
  const needsTelLink = !!item.ctaText || item.supportInfoEnabled === true;
  if (needsTelLink && !isValidTelLink(telLink)) {
    throw new Error('landing "' + item.slug + '": settings.json의 contact.telLink 값이 없거나 올바른 tel: 형식이 아니어서 상담 CTA를 생성할 수 없습니다.');
  }

  const nav = transformNavForStaticPage(ctx.navHtml);
  const footer = transformFooterForStaticPage(ctx.footerHtml);

  const body = [
    '<header>' + nav + '</header>',
    buildBreadcrumbHtml(item, canonicalUrl),
    '<main>',
    '<section class="landing-hero landing-section">',
    '<h1>' + escapeHtml(item.h1 || item.seoTitle) + '</h1>',
    buildImageBlock('landing-hero-image', item.heroImage, item.heroImageAlt, domain),
    '</section>',
    '<section class="landing-section">' + paragraphsFromPlainText(item.body) + '</section>',
    buildBeforeAfterBlock(item, domain),
    item.priceBasis ? '<section class="landing-section"><h2>비용 결정 기준</h2>' + paragraphsFromPlainText(item.priceBasis) + '</section>' : '',
    item.process ? '<section class="landing-section"><h2>작업 과정</h2>' + paragraphsFromPlainText(item.process) + '</section>' : '',
    buildSupportInfoBlock(item, telLink),
    buildFaqBlock(faqEntries),
    buildTrustBadgesBlock(item.trustBadges),
    buildRelatedLinksBlock(item, ctx.services, ctx.cases),
    item.ctaText ? '<section class="landing-section landing-final-cta"><a class="hero-btn" href="' + escapeAttr(telLink) + '">' + escapeHtml(item.ctaText) + '</a></section>' : '',
    '</main>',
    footer,
    ctx.contactBarHtml
  ].filter(Boolean).join('\n');

  return [
    '<!doctype html>',
    '<html lang="ko">',
    '<head>',
    '<meta charset="UTF-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '<title>' + escapeHtml(item.seoTitle) + '</title>',
    '<meta name="description" content="' + escapeAttr(item.metaDescription) + '">',
    '<meta name="robots" content="index,follow">',
    '<link rel="canonical" href="' + escapeAttr(canonicalUrl) + '">',
    '<meta property="og:type" content="website">',
    '<meta property="og:title" content="' + escapeAttr(item.seoTitle) + '">',
    '<meta property="og:description" content="' + escapeAttr(item.metaDescription) + '">',
    '<meta property="og:url" content="' + escapeAttr(canonicalUrl) + '">',
    ogImagePath ? '<meta property="og:image" content="' + escapeAttr(ogImagePath) + '">' : '',
    '<link rel="stylesheet" href="/css/style.css">',
    '<link rel="stylesheet" href="/css/landing.css">',
    jsonLdBlocks.map(function (block) {
      return '<script type="application/ld+json">' + JSON.stringify(block) + '</script>';
    }).join('\n'),
    '</head>',
    '<body>',
    body,
    '<script src="/js/script.js"></script>',
    '</body>',
    '</html>',
    ''
  ].filter(Boolean).join('\n');
}

export function buildSitemapEntry(item, domain) {
  const loc = buildCanonicalUrl(domain, item.slug);
  return [
    '  <url>',
    '    <loc>' + escapeXml(loc) + '</loc>',
    '    <changefreq>weekly</changefreq>',
    '    <priority>0.6</priority>',
    '  </url>'
  ].join('\n');
}
