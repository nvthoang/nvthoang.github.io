# Verification — 27 October 2026

## Completed checks

- Generated 15 static HTML pages, 32 published bibliography records, three publication updates, sitemap and robots.txt.
- Nine tests passed for BibTeX parsing: nested/quoted values, string macros, crossrefs/cycles, malformed input, unpublished filtering, DOI deduplication, required metadata, diacritics/corporate authors and HTML/URL safety.
- Offline output check passed for local links/assets, anchor targets, duplicate IDs, language, single main heading and image alt attributes.
- Browser checked: desktop homepage, publication library, contact form and mobile/tablet views.
- Publication year + topic filtering: 2026 + Data Science returned the MEHC-Curation paper. Empty-result search and Reset behaved correctly. Searching “peptide” returned two records in the mobile view.
- Copy citation produced a confirmation in the browser.
- VI in local preview produced the expected explanation that translation requires a public URL.
- Mobile menu opened and exposed navigation.
- At 390px and 768px iframe widths, homepage document content fit the viewport. At 320px, homepage and contact content also fit; no horizontal document overflow was observed. These were real browser iframe layouts, not physical-device tests.
- JavaScript syntax checked with Node.

## Checks that require the owner’s deployed site

- No GitHub repository was created/pushed and no GitHub Actions run occurred in the owner’s account. The workflow and static files are prepared, not deployed.
- No domain or DNS configuration was changed.
- Google Translate could not be tested against this new site before public deployment. It uses Google's external website translation view; it is not an on-domain translation API or a local cache.
- Form action, input fields, required fields and native POST flow were inspected. No external contact message was submitted. Email activation, spam checks and actual inbox delivery remain to be tested after deployment.
- No claim of exhaustive accessibility certification, cross-browser/device certification, DOI revalidation or a full publication-history audit is made.

The bibliography now includes all 32 published items in the owner’s October 2026 CV (2016–2026). The JACC 2020 poster is excluded by explicit owner instruction. All records are rendered by default, with filters covering the available publication years. Current Scholar-profile completeness could not be verified; see PUBLICATION_SOURCES.md. Exact announcement dates, project details and member appointments have not been inferred. See HUONG_DAN.md for the owner’s post-deployment steps.

## People-page update

- Seven English profiles supplied by the owner were added: one Senior Researcher, five Researchers and one Research Assistant.
- Official English names of the six universities were checked; see MEMBER_SOURCES.md. Individual qualifications and study status remain owner-supplied.
- Generated HTML was checked for all seven names, correct role groups and the absence of empty member placeholders.
