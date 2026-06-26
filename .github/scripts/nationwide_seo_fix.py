from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('      </details>\n    </div>\n  </section>','    </div>\n  </section>')
p.write_text(s,encoding='utf-8')
