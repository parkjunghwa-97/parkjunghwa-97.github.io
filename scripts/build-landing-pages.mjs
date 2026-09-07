#!/usr/bin/env node
// PR-L3: data/landing-pages.json의 publish:true 항목만 실제 정적 페이지(<slug>/index.html)로
// 생성하고, sitemap.xml의 landing 전용 마커 구간을 그 목록으로 교체합니다.
//
// 이 스크립트는 GitHub Actions에서 "Checkout" 직후, "Upload artifact" 이전에 실행됩니다
// (.github/workflows/pages.yml 참고). 실패하면 process.exit(1)로 종료해 이후 스텝
// (Upload/Deploy)이 실행되지 않게 합니다 - 깨진 상태가 배포되는 일이 구조적으로
// 불가능하도록 설계했습니다.
//
// 안전 원칙(반드시 지킬 것, PR-L3 설계 승인 조건):
//   1) 이 스크립트는 삭제 연산(fs.rm/fs.unlink/fs.rmdir 등)을 절대 포함하지 않습니다.
//      "이번에 필요한 것만 새로 만든다"만 수행하며, 이전 실행의 산출물을 정리하는 책임은
//      지지 않습니다(실제 운영에서는 GitHub Actions가 매번 fresh checkout이고 GitHub
//      Pages 배포가 이전 아티팩트를 이번 것으로 완전히 교체하는 방식이라 이것으로
//      충분합니다 - 로컬에서 반복 실행하며 테스트할 때는 매번 새 임시 디렉터리를
//      사용해야 합니다).
//   2) slug는 예약어/형식/중복 검증을 통과한 것만 디렉터리로 만듭니다.
//   3) index.html/sitemap.xml의 마커는 정확히 1쌍씩만 존재해야 하며, 그렇지 않으면
//      전체 빌드를 실패시킵니다(부분 생성 금지).
import fs from 'node:fs';
import path from 'node:path';
import {
  renderLandingPage,
  buildSitemapEntry,
  escapeXml
} from './landing-page-template.mjs';

const ROOT = process.cwd();

const LANDING_SLUG_ALLOWED_PATTERN = /^[a-z0-9-]+$/;
// Worker(workers/cms-auth/src/index.js)의 RESERVED_LANDING_SLUGS와 반드시 동일하게
// 유지해야 합니다. 저장소 최상위 구조가 바뀌면 두 곳 모두 함께 검토할 것.
const RESERVED_LANDING_SLUGS = [
  'cms', 'data', 'uploads', 'css', 'js', 'images', 'workers', 'cases',
  'index', 'privacy', 'partner', 'sitemap', 'robots', 'llms', 'logo', 'hero',
  'cname', 'nojekyll', 'readme', 'refresh', 'refresh2', 'refresh3', 'refresh4',
  'refresh5', 'site-refresh', 'naver3b5de69a2e79f1adcbb8e102e40851b2'
];

const NAV_START = '<!-- LANDING_TEMPLATE_NAV_START -->';
const NAV_END = '<!-- LANDING_TEMPLATE_NAV_END -->';
const FOOTER_START = '<!-- LANDING_TEMPLATE_FOOTER_START -->';
const FOOTER_END = '<!-- LANDING_TEMPLATE_FOOTER_END -->';
const CONTACTBAR_START = '<!-- LANDING_TEMPLATE_CONTACTBAR_START -->';
const CONTACTBAR_END = '<!-- LANDING_TEMPLATE_CONTACTBAR_END -->';
const SITEMAP_START = '<!-- LANDING_SITEMAP_START -->';
const SITEMAP_END = '<!-- LANDING_SITEMAP_END -->';

class BuildError extends Error {}

function fail(message) {
  throw new BuildError(message);
}

function countOccurrences(text, needle) {
  if (!needle) {
    return 0;
  }
  let count = 0;
  let index = 0;
  for (;;) {
    const found = text.indexOf(needle, index);
    if (found === -1) {
      break;
    }
    count += 1;
    index = found + needle.length;
  }
  return count;
}

// 마커 쌍이 정확히 1개씩, 올바른 순서로 존재하는지 검증하고 위치를 반환합니다.
// 위반 시(누락/중복/순서 오류) 빌드를 실패시킵니다.
export function locateMarkerPair(text, startMarker, endMarker, label) {
  const startCount = countOccurrences(text, startMarker);
  const endCount = countOccurrences(text, endMarker);
  if (startCount !== 1) {
    fail(label + ': START 마커가 정확히 1개가 아닙니다(발견 ' + startCount + '개) - ' + startMarker);
  }
  if (endCount !== 1) {
    fail(label + ': END 마커가 정확히 1개가 아닙니다(발견 ' + endCount + '개) - ' + endMarker);
  }
  const startIdx = text.indexOf(startMarker);
  const endIdx = text.indexOf(endMarker);
  if (startIdx > endIdx) {
    fail(label + ': START 마커가 END 마커보다 뒤에 있습니다(순서 오류)');
  }
  return { startIdx: startIdx, endIdx: endIdx };
}

export function extractBetweenMarkers(text, startMarker, endMarker, label) {
  const pos = locateMarkerPair(text, startMarker, endMarker, label);
  return text.slice(pos.startIdx + startMarker.length, pos.endIdx);
}

export function replaceBetweenMarkers(text, startMarker, endMarker, newInner, label) {
  const pos = locateMarkerPair(text, startMarker, endMarker, label);
  const prefix = text.slice(0, pos.startIdx + startMarker.length);
  const suffix = text.slice(pos.endIdx);
  return prefix + newInner + suffix;
}

export function validateLandingSlug(slug, seenSlugs) {
  const errors = [];
  if (typeof slug !== 'string' || slug.trim() === '') {
    errors.push('slug_required');
    return errors;
  }
  if (!LANDING_SLUG_ALLOWED_PATTERN.test(slug)) {
    errors.push('slug_invalid_chars');
    return errors;
  }
  if (slug.charAt(0) === '-' || slug.charAt(slug.length - 1) === '-') {
    errors.push('slug_edge_hyphen');
  }
  if (slug.indexOf('--') !== -1) {
    errors.push('slug_consecutive_hyphen');
  }
  if (RESERVED_LANDING_SLUGS.indexOf(slug) !== -1) {
    errors.push('slug_reserved');
  }
  if (seenSlugs.has(slug)) {
    errors.push('slug_duplicate');
  } else {
    seenSlugs.add(slug);
  }
  return errors;
}

function readJsonFile(relPath) {
  const fullPath = path.join(ROOT, relPath);
  let raw;
  try {
    raw = fs.readFileSync(fullPath, 'utf8');
  } catch (error) {
    fail(relPath + ' 파일을 읽을 수 없습니다: ' + error.message);
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    fail(relPath + ' JSON 파싱 실패: ' + error.message);
  }
}

function findDuplicate(values) {
  const seen = new Set();
  for (const value of values) {
    if (seen.has(value)) {
      return value;
    }
    seen.add(value);
  }
  return null;
}

// data/landing-pages.json을 읽고, publish:true 항목만 정적 페이지로 생성합니다.
// 반환값: { published, domain } - 테스트에서 재사용할 수 있도록 순수 로직만 분리.
export function runBuild() {
  const landingItems = readJsonFile('data/landing-pages.json');
  if (!Array.isArray(landingItems)) {
    fail('data/landing-pages.json은 배열이어야 합니다');
  }
  const services = readJsonFile('data/services.json');
  const cases = readJsonFile('data/cases.json');
  const settings = readJsonFile('data/settings.json');

  // slug는 publish 여부와 무관하게 항상 검증합니다(초안 단계에서도 나중에 실제 URL이
  // 될 값이 예약 경로를 침범하거나 다른 페이지와 충돌하면 안 되므로 - PR-L1과 동일 원칙).
  const seenSlugs = new Set();
  landingItems.forEach(function (item, index) {
    const errors = validateLandingSlug(item && item.slug, seenSlugs);
    if (errors.length) {
      fail('landing[' + index + '](id=' + (item && item.id) + ') slug 검증 실패: ' + errors.join(', '));
    }
  });

  const published = landingItems.filter(function (item) {
    return item && item.publish === true;
  });

  // 형식/예약어/중복 검증을 통과했더라도, 저장소 최상위에 예약어 목록에 없는 새 파일/
  // 디렉터리가 나중에 추가되면 slug와 우연히 겹칠 수 있습니다. RESERVED_LANDING_SLUGS
  // 갱신을 놓친 경우까지 방어하기 위해, 실제 쓰기 전에 fresh checkout 안에 그 경로가
  // 이미 존재하는지(파일이든 디렉터리든) 직접 확인합니다. 존재하면 기존 것을 덮어쓰거나
  // 지우지 않고(fs.rm/unlink/rmdir 금지 원칙 유지) 빌드 전체를 실패시킵니다.
  published.forEach(function (item) {
    const targetPath = path.join(ROOT, item.slug);
    if (fs.existsSync(targetPath)) {
      fail('slug "' + item.slug + '"에 해당하는 경로가 저장소에 이미 존재합니다(파일/디렉터리 충돌): ' + targetPath);
    }
  });

  const domain = ((settings && settings.site && settings.site.customerSite) || '').replace(/\/+$/, '');
  if (!domain) {
    fail('data/settings.json의 site.customerSite 값이 비어있습니다');
  }

  let indexHtml;
  try {
    indexHtml = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  } catch (error) {
    fail('index.html을 읽을 수 없습니다: ' + error.message);
  }

  const navHtml = extractBetweenMarkers(indexHtml, NAV_START, NAV_END, 'index.html nav');
  const footerHtml = extractBetweenMarkers(indexHtml, FOOTER_START, FOOTER_END, 'index.html footer');
  const contactBarHtml = extractBetweenMarkers(indexHtml, CONTACTBAR_START, CONTACTBAR_END, 'index.html fixed-contact-bar');

  // PR-L3 리뷰 반영: "부분 생성 금지" 원칙을 sitemap 실패 시에도 지키기 위해,
  // 페이지 HTML과 새 sitemap 내용을 전부 메모리에서 계산/검증까지 마친 뒤에만
  // 실제 파일 쓰기(fs.mkdirSync/writeFileSync)를 수행합니다. 아래 계산 단계에서
  // 하나라도 실패하면 fail()이 예외를 던져 어떤 파일도 쓰이지 않은 채 종료됩니다.
  const pagesToWrite = published.map(function (item) {
    const html = renderLandingPage(item, {
      services: services,
      cases: cases,
      settings: settings,
      navHtml: navHtml,
      footerHtml: footerHtml,
      contactBarHtml: contactBarHtml,
      domain: domain
    });
    return { dir: path.join(ROOT, item.slug), html: html };
  });

  let sitemapXml;
  try {
    sitemapXml = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
  } catch (error) {
    fail('sitemap.xml을 읽을 수 없습니다: ' + error.message);
  }

  const sitemapEntries = published.map(function (item) {
    return buildSitemapEntry(item, domain);
  });
  // 마커 사이 들여쓰기를 원본 sitemap.xml(마커 앞의 "  " 2칸)과 맞춰, 항목이 없을 때도
  // 보기 좋은 형식을 유지합니다(빈 결과가 실수로 들여쓰기를 무너뜨리지 않도록).
  const newMiddle = sitemapEntries.length ? ('\n' + sitemapEntries.join('\n') + '\n  ') : '\n  ';
  const newSitemap = replaceBetweenMarkers(sitemapXml, SITEMAP_START, SITEMAP_END, newMiddle, 'sitemap.xml landing');

  const locs = Array.from(newSitemap.matchAll(/<loc>([^<]*)<\/loc>/g)).map(function (m) { return m[1]; });
  const duplicateLoc = findDuplicate(locs);
  if (duplicateLoc) {
    fail('sitemap.xml에 중복된 URL이 있습니다: ' + escapeXml(duplicateLoc));
  }

  const urlOpenCount = (newSitemap.match(/<url>/g) || []).length;
  const urlCloseCount = (newSitemap.match(/<\/url>/g) || []).length;
  if (urlOpenCount !== urlCloseCount) {
    fail('sitemap.xml의 <url>/<\/url> 태그 개수가 일치하지 않습니다(형식 오류)');
  }

  // 여기까지 도달했다면 모든 검증을 통과한 것이므로, 이제부터만 실제로 씁니다.
  // 삭제 연산은 여전히 전혀 포함하지 않습니다(설계 원칙 §G).
  pagesToWrite.forEach(function (page) {
    fs.mkdirSync(page.dir, { recursive: true });
    fs.writeFileSync(path.join(page.dir, 'index.html'), page.html, 'utf8');
  });
  fs.writeFileSync(path.join(ROOT, 'sitemap.xml'), newSitemap, 'utf8');

  return { publishedCount: published.length, published: published, domain: domain };
}

function main() {
  try {
    const result = runBuild();
    console.log('[build-landing-pages] OK: ' + result.publishedCount + '개 랜딩페이지 생성, sitemap.xml 갱신 완료');
    process.exit(0);
  } catch (error) {
    console.error('[build-landing-pages] FAIL: ' + error.message);
    process.exit(1);
  }
}

// 테스트에서 import할 때는 자동 실행되지 않고, 실제 Actions 실행(node build-landing-pages.mjs)일
// 때만 main()이 실행되도록 분기합니다.
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
