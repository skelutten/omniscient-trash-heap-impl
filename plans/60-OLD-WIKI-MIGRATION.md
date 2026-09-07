# Plan 60 — Old wiki migration

> **Status:** separate corpus track, proposed, not started
> **Prerequisite:** `02-DETERMINISTIC-CORE.md` green
> **Does not block:** plans 03–05

## Scope

- inventory the legacy corpus;
- map legacy metadata and taxonomy to current registries;
- preserve `source_refs` and provenance;
- produce dry-run migration reports;
- migrate with idempotency and no destructive overwrite;
- validate migrated objects with the deterministic core;
- require explicit review for ambiguous or lossy mappings.

## Acceptance

A repeated migration is a no-op for unchanged input. Every migrated object has
traceable source references. The migration manifest separately reports source,
eligible, emitted, excluded and quarantined files, including mapping class and
ambiguity/error counts. Ambiguous mappings are quarantined or reported, never
silently guessed. The migrated corpus passes the core lint gate only after
review-gated provisional/lossy mappings are resolved or explicitly accepted.

## Source material

- `../specs/DATA_MODEL.md`, `EPISTEMOLOGY.md`, `ARCHITECTURE.md`
- `../schemas/registry/`

## Non-goals

Migration does not implement connectors, Universal Source capture, promotion recovery or optional retrieval features.

## External implementation feedback

A real migration was executed against a preserved legacy corpus using a separate
fresh target. The observations below are external implementation feedback and
planning input, not runtime evidence that this OE repository is implemented.

### External observations

The sibling report stated the following observations, which are useful as
design input but are not OE execution evidence:

- Legacy corpus was preserved before target creation.
- The source snapshot contained 7,055 files; 572 eligible Markdown knowledge
  objects were analyzed and 572 target objects were emitted. `index.md`
  navigation files and other non-eligible files were not canonical objects.
- The sibling report stated `0 analysis errors`, but malformed metadata used
  fallback; that number is therefore insufficient without an independent
  ambiguity/quarantine count.
- Matching manifest hash produced a no-op; changed source and changed or
  unmanaged targets were rejected.
- Legacy `source_ref` values were normalized to `source_refs` while preserving
  the original relative path.
- Link analysis found deterministic matches and unresolved links; neither was
  automatically promoted to canonical relations.
- Keywords were retained as subject terms and not automatically promoted to
  facets because they were not exact registry values.

### Contract changes recommended for OE

1. Make the migration manifest a normative artifact containing source corpus hash,
   source/target counts, preserved-source location, source-mutated flag and mode.
2. Require a fresh-target-only executor with idempotent reruns and fail-closed
   behavior for an unmanaged target, changed source or analysis errors.
3. Define exact-byte hashing over sorted repository-relative POSIX paths and make
   the source-preservation/hash check independently verifiable.
4. Keep migration enrichment read-only. Emit separate link and facet proposal
   artifacts; do not turn unresolved links or subject keywords into canonical
   relations/facets automatically.
5. Treat malformed legacy metadata as an explicit ambiguity signal. The tested
   fallback may classify an object conservatively, but the plan/report MUST retain
   a machine-readable ambiguity/quarantine record rather than silently reporting
   zero errors.
6. Preserve both singular legacy `source_ref` compatibility and normalized
   `source_refs`; provenance must remain traceable to the original relative path.
7. Add conformance tests for read-only source behavior, exact hashes, idempotency,
   target safety, changed-source rejection, malformed metadata and proposal
   non-mutation.
8. Never copy legacy `tags` directly into canonical `keywords`. Legacy tags are
   untrusted metadata: preserve them in the migration plan/audit, initialize
   canonical keywords as empty (or derive them through a separately versioned,
   reviewable process), and require evidence before publication. Add a regression
   fixture where unrelated content carries a contaminated tag profile.

This rule was added after the real migration showed an exact source-to-target copy
of semantically unrelated tag sets, including `programmering`, `devops` and
`mjukvara` on a Descartes article. The migration itself was byte-faithful; the
metadata was already wrong upstream. The safe behavior is therefore to preserve
source tags for audit without promoting them to semantic keywords.
9. Distinguish verified-personal migration targets from inferred scope: a
   personal target is valid only when explicitly established for the source;
   uncertain scope remains ambiguous and never defaults silently to personal.
10. Record conservative defaults (`draft`, `unverified`, `general`, placeholder
    confidence) as processing/classification state, not as source-quality claims.
11. Support opt-in `frontmatter: required|derived` per migration map (D95): External
    documentation trees (e.g. system documentation) carry no YAML frontmatter. Provide an
    opt-in `derived` mode that extracts titles from doc macros (e.g. `%docTitle`) or the
    first `# H1`, treats the document as its own source citation, and strips author/signum
    macros (`%docResp`, `%docOwnerLineMgr`) for privacy. `required` remains the strict
    default for wiki sources to prevent relaxing validation guards by omission.

### Registry reconciliation warning

The sibling template's facet registry uses values such as `swedish`/`english`,
while this OE repository's registry uses `sv`/`en` and has a broader toolchain and
language vocabulary. These registries must not be copied across repositories
without an explicit compatibility decision. Migration code should load the active
repository's registry and produce proposals only for values legal in that registry.

The migration evidence supports treating this plan as **informed by an external
reference implementation**. It does not validate the OE implementation. OE
implementation status remains `not started` until the above behavior exists and
is tested here.
