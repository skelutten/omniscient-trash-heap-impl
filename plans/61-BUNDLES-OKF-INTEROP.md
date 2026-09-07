# Plan 61 — Bundles and OKF interoperability
 
> **Status:** complete, verified (D109)
> **Prerequisite:** `02-DETERMINISTIC-CORE.md` green
> **Does not block:** source ingestion plans 03–05

## Scope

- computed bundle selectors and manifests;
- deterministic derived artifacts;
- dangling-link accounting and closure rules;
- OKF field mapping and declared lossy conversions;
- bundle-relative links and export validation;
- concrete OKF error contracts only when adapter failures are implemented.

## Acceptance

Identical corpus, selector and exporter version produce byte-identical output. Derived artifacts carry corpus, algorithm and policy versions. No bundle membership is written into canonical frontmatter.

## Source material

- `../specs/OKF-INTEROP.md`
