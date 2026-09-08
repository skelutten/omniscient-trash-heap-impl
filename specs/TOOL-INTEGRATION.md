# Plan for tool integrations

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-TOOL-INTEGRATION-001`
> **Version**: `0.1.0`
> **Updated**: `2026-08-17`
> **Source**: Adapter plan; not a normative specification
> **Status**: `PLAN`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Compatibility target**: Additive, isolated integrations; canonical wiki remains source of truth
> **Normative owner**: None; this is a non-normative integration plan
> **Related documents**: `ARCHITECTURE.md`, `OKF-INTEROP.md`, `UNIVERSAL-SOURCE-EXTENSION.md`

---

## Goal

Make LLM Wiki the canonical knowledge source and offer reproducible
integrations with Obsidian, Notion, MkDocs, Hugo and Jekyll without losing
IDs, relations, provenance or epistemic metadata.

## Principles

- The Markdown objects in `personal/` and `engineering/`, together with the YAML registries,
  are the system's only source of truth.
- Integrations are adapters. They must not introduce a competing data model layer.
- All imports are idempotent and traceable via external identifier, content hash
  and `provenance`.
- All content written to the canonical wiki must pass `python3 linter.py`.
- Tool-specific fields are kept named and isolated, for example under
  `integration_metadata.obsidian` or `integration_metadata.notion` when the schema
  is extended.

## Common adapter foundation

### Phase 1 — Contract and CLI

1. Introduce a package or a module for adapters, for example `integrations/`.
2. Define common models for:
   - `ExternalReference`: system, external ID, URL, synced timestamp and hash.
   - `ExportManifest`: **superseded** — use the normative bundle manifest contract in
     `OKF-INTEROP.md` §17.3–§17.4 (**BUNDLE-004**) rather than defining a second one.
   - `SyncResult`: created, changed, skipped and erroneous objects.
3. Create CLI commands with stable interfaces:

   ```bash
   python3 -m integrations export obsidian --output dist/obsidian
   python3 -m integrations export mkdocs --output dist/mkdocs
   python3 -m integrations import notion --database-id <id> --staging raw/notion
   ```

4. Add manifest files so that exports can be verified and repeated
   deterministically.
5. Add contract tests that compare a knowledge object before and after export/import.

**Done when:** a minimal object can be exported through a common adapter API and
the manifest is deterministic.

### Phase 2 — Metadata and link rules

1. Document a central mapping from LLM Wiki frontmatter to the respective target format.
2. Always preserve `id`, `title`, `taxonomy_path`, `taxonomy_id`, `object_type`,
   `relations` and `provenance`.
3. Choose a normal form for links in exports: internal links are identified first by
   object ID and then get a target-format-adapted URL or wiki link.
4. Define a conflict policy before two-way sync is allowed:
   - the canonical wiki wins for system fields;
   - external edits are imported as candidates to `raw/`;
   - a conflict creates a report, never a silent overwrite.

**Done when:** the mapping is tested for Article, Concept, Claim and Incident as well as
relations between objects.

## Tool-specific phases

### Phase 3 — Obsidian (first)

Obsidian has direct support for Markdown and YAML frontmatter and is therefore the
lowest-risk first integration.

1. Document how the project root or an exported `vault/` directory is opened as a vault.
2. Generate optional index notes:
   - start page per scope;
   - taxonomy index;
   - object index per type;
   - relation/backlink index based on `relations`.
3. Translate relations into Obsidian-compatible `[[ID]]` or `[[path|title]]`
   links in an exported view, without changing the source objects.
4. Add Dataview-compatible, generated indexes if Dataview is used, but do not make
   the knowledge model itself dependent on the plugin.
5. Verify that an Obsidian edit cannot change system IDs or metadata without
   the linter being run on re-import.

**Done when:** an exported vault can be navigated in Obsidian with taxonomy, links and
preserved frontmatter.

### Phase 4 — MkDocs (second priority)

1. Build an MkDocs export that copies or links generated Markdown to a
   build directory, never to the source trees.
2. Generate `mkdocs.yml` and navigation from the taxonomy registry.
3. Create pages for relations, evidence bundles and object types.
4. Choose and document a theme, for example Material for MkDocs, as an optional
   presentation dependency.
5. Run the MkDocs build in CI and check for broken links.

**Done when:** a static docs site is built from the same objects as the Obsidian export and
has deterministic navigation.

### Phase 5 — Notion import (one-way first)

1. Implement a Notion client with explicit authentication via environment variable or
   credential store; secrets must never be written to the repo or manifest.
2. Map database properties to frontmatter and blocks to Markdown.
3. Store the Notion page ID and URL in `provenance.source_refs` or named
   integration metadata.
4. Write the raw export to `raw/notion/` and create a review report before synthesis into
   `personal/` or `engineering/`.
5. Only thereafter introduce export back to Notion, with a clear conflict and
   deletion policy.

**Done when:** a Notion database can be imported traceably to staging and validated without
external changes silently overwriting canonical objects.

### Phase 6 — Hugo and Jekyll

1. Create a common static-site normal form from the adapter foundation.
2. For Hugo: generate sections from taxonomy and taxonomies from facets.
3. For Jekyll: generate collections per scope and YAML frontmatter compatible with
   Liquid templates.
4. Share link, index and relation logic with MkDocs so that the semantics do not diverge.
5. Add snapshot tests for a representative site excerpt.

**Done when:** Hugo and Jekyll exports produce builds without broken internal links.

## Quality, security and operations

1. Sanitize HTML in all publishing adapters and serialize data safely in JavaScript
   contexts.
2. Run the following in CI for each adapter that exists:

   ```bash
   python3 linter.py
   python3 scripts/validate_generated_code.py
   python3 -m pytest conformance -q
   ```

3. Add adapter tests for idempotency, link mapping, empty fields, Unicode and
   conflicts.
4. Version export manifests and mapping rules so that changed exports can be
   explained and reviewed.
5. Do not publish private scopes or source references without an explicit
   access/redaction policy.

## Prioritized delivery order

1. Adapter foundation and metadata/link contract.
2. Obsidian vault/export.
3. MkDocs export and CI build.
4. Notion one-way import to `raw/`.
5. Hugo and Jekyll export.
6. Possible two-way sync with Notion after the conflict policy has been tested in practice.