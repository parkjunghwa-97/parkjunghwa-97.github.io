from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marquee = '''            <div class="cert-marquee" aria-hidden="true">
              <div class="cert-marquee-track">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/women-company.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-clean.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-pest.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-estate.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-clean.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-pest.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-estate.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/women-company.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-clean.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-pest.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-estate.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-clean.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-pest.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-estate.jpg" alt="">
              </div>
            </div>'''

start = s.find('            <div class="cert-marquee" aria-hidden="true">')
end_marker = '            <div class="cert-actions">'
if start != -1:
    end = s.find(end_marker, start)
    if end != -1:
        s = s[:start] + marquee + '\n' + s[end:]

p.write_text(s, encoding='utf-8')
