# NOTICE

This tool is a derivative work based on:

- **Project**: naver-blog-automation
- **Author**: choigpt_ai (Instagram [@choigpt_ai](https://instagram.com/choigpt_ai))
- **Source**: https://github.com/choigpt-ai/naver-blog-automation
- **License**: MIT (see `LICENSE` in this folder — copied verbatim from upstream)

Per the MIT License, the original copyright notice and permission notice are
preserved in `LICENSE`. This folder contains modified and additional code
("GiftClean customization") built on top of the original structure. Files
carried over with little or no change keep their original author's logic;
files that were substantially rewritten for GiftClean are noted in
`CHANGELOG_FROM_UPSTREAM.md`.

## What changed, in one line

The original tool is a general-purpose "Threads post → Naver blog" writer.
This fork narrows it to a **GiftClean-only cleaning-service blog writer**
with a GiftClean-specific input form, a rewritten content-generation prompt
that enforces GiftClean's tone/structure/forbidden-phrase rules, stronger
publish-safety gates (`ALLOW_PUBLISH`, `DRY_RUN`), upload validation, PII
warnings, EXIF stripping, and a mandatory human-approval step before any
Naver interaction and again before the temp-save click.

No code in this folder ever clicks a "발행"(publish)/예약발행/공개 설정
control on Naver — see `automation/editor.py` and `config/safety.py`.
