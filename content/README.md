# Editing content

Use English for all source content. The VI button opens Google Translate's Vietnamese view of the live page; no second authored copy is needed.

| What to change | File |
| --- | --- |
| Biography, links, email, research directions | `site.json` |
| Projects | `site.json` → `projects` |
| Researchers / Research Assistants | `site.json` → `people` |
| Teaching materials / resources | `site.json` → `resources` |
| Publications | `publications.bib` |
| News / highlights | A new `.md` file in `news/` |

JSON must use double quotes and have no trailing commas. Keep filenames and IDs unique.

## People

Seven member profiles supplied by the owner are included. Add further profiles using objects like:

```json
{"name":"Full name", "role":"Researcher", "bio":"Short public biography.", "url":"https://example.org", "image":"assets/person.webp", "published":true}
```

Allowed roles: `Senior Researcher`, `Researcher`, `Research Assistant`. The group lead is rendered separately. Leave `image` or `url` empty if unused. Only use public, approved biographies and photos. Do not put unpublished research details in this public repository.

## Projects

Replace each existing placeholder and change `placeholder` to `false`. `published: false` hides an entry from the generated site; the source remains in the repository. Do not store confidential information in source files. `url` may be empty. All projects are coordinated by Hoang Nguyen, so there is no project-member field.

## Publications

Export selected published items from your Scholar profile as BibTeX and replace or append `publications.bib`. Standard `@article` and `@inproceedings` exports work directly. Run the build before deployment. Use `keywords` (comma-separated) for topic filters; records without keywords appear under “Uncategorised”. Match the five research-direction names for consistency.

Only import published journal/conference/book records. Preprints and submitted work are not automatically recognisable from every Scholar export: you must review exports. The build excludes unsupported types and records explicitly marked `status={preprint}`, `status={submitted}`, `status={accepted}`, etc.; it also excludes arXiv/bioRxiv/medRxiv venues. An absent status on a supported standard entry is treated as published, assuming your reviewed export. Duplicate DOIs are deduplicated; duplicate BibTeX keys fail with a useful error.

Use `featured_publications` in `site.json` to select homepage records by BibTeX key. Replacing an export may change the keys: update that list and any news `publication` references. Missing references fail the build instead of silently publishing stale highlights. Delete/update old news references if you remove the related record.

Citation details and titles remain in English by design. The current 32 records cover all published items in the October 2026 CV (2016–2026): 26 journal articles, five conference papers and one book chapter. The JACC 2020 poster is excluded by the owner. This is not a live Scholar feed; complete matching against the latest Scholar profile has not been verified. See ../PUBLICATION_SOURCES.md.

## News

Copy an existing Markdown file. Supported front matter: `title`, `date` (YYYY, YYYY-MM or YYYY-MM-DD), `category`, `featured` (true/false), optional `publication` (BibTeX key), `published` (true/false). Dates are not inferred: the initial items show publication years because announcement dates were not supplied. News with the same date is ordered by filename. Markdown supports paragraphs, `##` / `###` headings, bullet lists, **bold**, *italics*, and `[links](https://...)`. Raw HTML is escaped. Put the publication key on publication-related news to keep the link validated.

## Resources

Add objects to `resources`:

```json
{"title":"Resource title", "type":"Teaching material", "description":"What readers will learn.", "url":"https://example.org/resource", "published":true}
```

Use a full HTTPS URL or a local path such as `assets/resources/lab-01.pdf`. Only share material you intend to make public. Optional CV: place a **public/redacted PDF** at `assets/Hoang_Nguyen_CV.pdf`, then set `cv_file` to that path. No personal CV source or private contact details are bundled.

Member biographies can contain `\n` in the JSON string to put each qualification on its own line. The People page uses the shortened form “International University, VNU HCMC, Vietnam”.

The Teaching & Resources page currently has six course placeholders. Replace each title and description in `site.json` → `resources`, then add a resource URL when ready. Leave `url` empty to show “Materials forthcoming” without a nonfunctional link.

Member ORCID: set `orcid` in each person record to an ORCID ID or full `https://orcid.org/` URL. Leave it empty to hide the icon. The People page shows the linked icon after the name.
