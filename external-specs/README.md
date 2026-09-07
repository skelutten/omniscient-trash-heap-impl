# External Specifications (vendored, read-only)

> **Status**: Non-normative container. The vendored documents are normative **for
> their own authors**, not for this project; this project's obligations toward them
> are stated in `specs/`.

---

## 1. What belongs here

Third-party specifications that this project **implements against or interoperates
with**, vendored verbatim so the dependency is explicit, diffable and available
offline.

| Directory | Upstream | Version | Consumed by |
|---|---|---|---|
| `okf/` | [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog) | 0.2 | `specs/OKF-INTEROP.md` |

## 2. What does NOT belong here

This distinction keeps the folder from becoming a dumping ground:

| Material | Correct home | Why |
|---|---|---|
| An OpenAPI spec, RFC or technical manual that is **wiki content** | a Knowledge Object with `object_type: Specification` and `source_type: api_spec` / `rfc` / `vendor_doc` | It is knowledge *in* the wiki, not a contract the wiki is built against |
| Design discussions, articles, blog posts, transcripts | `research/` | Non-normative source material, not a specification |
| This project's own specifications | `specs/` | Normative, authored here |
| Registry data | `schemas/registry/` | Machine-read source of truth |

The test: **do we write code or invariants that must conform to this document?**
If yes, it belongs here. If it is something the wiki merely *describes*, it does not.

## 3. Rules

- **READ-ONLY.** A vendored document MUST NOT be edited, reformatted, translated or
  partially copied. Any local commentary goes in `specs/`, never in the vendored file.
- **PINNED.** Every vendored directory MUST contain a `PIN.yaml` recording upstream
  URL, branch, commit (where obtainable), retrieval time, retriever, `sha256`, size
  and the SPDX licence.
- **LICENSED.** The upstream licence MUST be vendored alongside the document, with
  attribution recorded in `PIN.yaml`. `okf/` is Apache-2.0; the copy is verbatim
  and unmodified.
- **TRACEABLE.** `PIN.yaml` MUST list the `specs/` documents that consume it, so an
  upgrade can find its blast radius.
- **UPGRADED DELIBERATELY.** Upgrading is: re-fetch → `diff` against the vendored
  copy → update `PIN.yaml` → update the affected invariants in the consuming
  `specs/` document **in the same change**. A pin bump without a spec review is how
  an interoperability claim silently becomes false.

## 4. Verifying a pin

```bash
sha256sum -c <<< "$(python3 -c "
import yaml;print(yaml.safe_load(open('external-specs/okf/PIN.yaml'))['retrieved']['sha256'])
")  external-specs/okf/SPEC.md"
```

## 5. Why vendor at all

The alternative — a URL in a comment — was rejected because:

1. `OKF-010` requires deterministic export. Determinism against a moving upstream
   is not verifiable.
2. An upgrade must be reviewable. Only a vendored copy can be diffed.
3. `OKF-009` requires round-trip preservation of unknown fields, which requires
   knowing exactly which fields the pinned version defines.
4. Offline and air-gapped environments must be able to build and validate.