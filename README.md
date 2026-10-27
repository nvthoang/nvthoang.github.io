# Hoang Nguyen Research Group — website source

Website học thuật responsive, dùng trên GitHub Pages và domain `www.nvthoang.com`.

**Bắt đầu:** xem [HUONG_DAN.md](HUONG_DAN.md). Thư mục `dist/` chứa website đã dựng, có thể mở `dist/index.html` để xem trước. Bộ source gồm HTML template, CSS, JavaScript, Python build script, dữ liệu nội dung và workflow GitHub Actions. Không cần npm, package trả phí, server riêng hoặc Python package bên ngoài.

## Features

- Responsive desktop, tablet and mobile layouts, with keyboard-accessible mobile navigation.
- Home, About, Research, Projects, Publications, People, News, Teaching & Resources, Join Us, Contact, privacy and 404 pages.
- English authored content. VI opens Google Translate’s Vietnamese view of the current live page. This is an external translated view, **not** a local translation engine or a stored translation cache. It requires a publicly accessible URL and depends on Google’s availability.
- Published BibTeX records are rendered as static HTML; browser-side search and year/topic/type filters. Citation copying, DOI links and a published-only BibTeX download.
- JSON for profile/projects/people/resources, Markdown for news. Content updates rebuild automatically on a push to `main` after Pages is enabled.
- Contact form configured for `hoang.nguyen@weltec.ac.nz`, using FormSubmit with its spam checks. **One-time email activation is required.** No live form submission or email delivery test was performed during development.
- No analytics, remote fonts, API keys or JavaScript framework dependencies.
- Canonical links, social metadata, Person structured data, sitemap, robots.txt, print layout and reduced-motion support.

## Content included

Five main research directions, the previously approved THNV logo, 32 published records (2016–2026) from the full October 2026 CV and three short publication updates. These updates use publication years; exact announcement dates were not supplied. The library includes all 26 journal articles, five conference papers and one book chapter listed in that CV. The JACC 2020 poster is excluded at the owner’s request. Full reconciliation against the current Scholar profile remains unverified because the supplied profile could not be read in full. See PUBLICATION_SOURCES.md. Projects are explicitly marked as placeholders. Seven owner-supplied member profiles are included: one Senior Researcher, five Researchers and one Research Assistant. No collaborator directory, unpublished study details, personal telephone number, full private CV or signature is bundled.

## Build and preview

Python **3.11 or newer**, standard library only:

```bash
python scripts/build.py
python scripts/check.py
python -m unittest discover -s tests -v
python -m http.server 8000 --directory dist
```

On Windows, use `py` instead of `python` if needed. Open `http://localhost:8000`. For a quick offline look, open `dist/index.html` directly. VI is intentionally disabled for local file/localhost previews, because Google cannot fetch those pages. Clipboard copying has a selectable-text fallback.

## Files to edit

| File | Purpose |
| --- | --- |
| `content/site.json` | Profile, five directions, projects, people, resources, contact settings |
| `content/publications.bib` | Reviewed published records exported from Google Scholar |
| `content/news/*.md` | English news items and highlights |
| `content/README.md` | Content schema and examples |
| `assets/style.css` | Colours, typography, layout and responsive rules |
| `assets/site.js` | Navigation, filters, copy citation, VI link and enquiry-topic preselection |
| `templates/base.html` | Shared header, footer and metadata |
| `scripts/build.py` | Static page generator |
| `scripts/bibtex.py` | Standard Scholar BibTeX reader |
| `.github/workflows/pages.yml` | Validation, build and GitHub Pages deployment |
| `dist/` | Generated output — edit source, then rebuild |

## Hosting

Set the repository’s Pages publishing source to **GitHub Actions**. Upload this project’s contents to the repository root, including `.github/`, not just the ZIP itself or the outer folder. The bundled workflow builds and deploys `dist`. Set the custom domain in GitHub Pages settings; a CNAME file alone is insufficient for an Actions deployment. Full steps and DNS values are in [HUONG_DAN.md](HUONG_DAN.md).

The source has been prepared for GitHub. No repository, DNS record, GitHub setting or existing public website was modified on the owner's behalf.

## Notes on third-party services

Google Translate is a free external viewing option; region/browser restrictions and scientific translation errors are possible. It does not provide a guaranteed native on-domain language switch or locally editable translation. Citation titles and bibliographic text are marked to remain in their original language. If an on-domain translation and owner-editable Vietnamese copy becomes necessary, add a separate translation workflow/provider rather than putting secret keys in browser JavaScript.

FormSubmit is free at preparation time according to its documentation. It requires external connectivity, provider activation and the provider's spam check. An institution may filter its messages. Keep direct email available as a fallback. Form delivery is not guaranteed by a static website. Activate and test using the live domain before announcing the form.

No paid service or recurring task has been activated. Standard hosted-service terms can change.

## References

- [GitHub Pages: creating a site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [GitHub Pages: custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [Google Translate: translate websites](https://support.google.com/translate/answer/2534559?hl=en&co=GENIE.Platform%3DDesktop)
- [FormSubmit documentation](https://formsubmit.co/documentation)
- Publication metadata source: owner's `Hoang_Nguyen_cv_Oct_2026.tex`, read during this task. Future additions can be imported from a reviewed Scholar export. See PUBLICATION_SOURCES.md for coverage and date conventions.
