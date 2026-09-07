# Security Policy & Threat Model

> **Status:** Authoritative Security Policy  
> **Scope:** Input ingestion, prompt injection defense, path sandboxing, and provenance verification  
> **Normative Owners:** `specs/ARCHITECTURE.md`, `specs/INGEST-STAGING.md`, `specs/VALIDATION.md`, `plans/03-SOURCE-INGESTION-SAFETY.md`

---

## 1. Core Threat Model & Design Invariants

LLM Wiki is a local-first, AI-augmented knowledge system. Because the system continuously ingests untrusted third-party web articles, PDFs, research papers, and external documentation, it operates under a strict zero-trust security perimeter.

### 1.1 Ingestion Threat Surface
1. **Indirect Prompt Injection:** External documents may contain adversarial instructions designed to hijack LLM extraction routines (e.g. attempting to delete files, exfiltrate API keys, or alter canonical facts).
   - *Mitigation:* All raw source payloads are wrapped in immutable `<untrusted_source>` boundary tags. During compilation and triage, model tool-calling and system command execution capabilities are strictly disabled (`FR-12`, `NFR-6`).
2. **Path Traversal & Arbitrary Overwrite:** Ingested file paths or generated slugs could attempt relative path escapes (e.g. `../../etc/passwd` or `../../.git/`).
   - *Mitigation:* All I/O operations strictly resolve canonical paths via `os.path.realpath` / `pathlib.Path.resolve()`. Any path outside the repository workspace is rejected with an immediate `AccessDeniedError` (`FR-13`, `AC-6`).
3. **Circular Fact Seeding & Provenance Poisoning:** Fabricated or low-quality claims could cite other unverified notes, creating an ungrounded hallucination loop.
   - *Mitigation:* Every factual claim requires an unbroken SHA-256 cryptographic provenance hash linking directly back to the immutable raw capture in `staging/` (`FR-17`, `PROV-007`, `E030`).

---

## 2. Ingestion Sandboxing & Isolation

- **Staging Quarantine:** Raw intake material resides exclusively in `staging/` and is completely invisible to production `/query` retrieval until explicitly reviewed and promoted.
- **Atomic File Operations:** Canonical file materializations use atomic `.tmp` creation and `os.replace` to prevent race conditions or corrupted partial writes during system interruption.
- **Fail-Closed Validation:** Any schema or registry violation immediately halts promotion and quarantines the candidate proposal (`VALIDATION.md`).

---

## 3. Reporting a Security Vulnerability

If you discover a security issue or vulnerability in LLM Wiki (such as a sandbox escape, injection bypass, or path traversal vulnerability), please submit an issue or private security advisory on the GitHub repository:
- **Repository:** `https://github.com/skelutten/llm-wiki-oe`
