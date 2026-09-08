# LLM Wiki Graph Visualization Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10  
> **Document ID**: `LLM-WIKI-VISUALIZE-001`  
> **Document family ID**: `LLM-WIKI-KG-DELTA-001`  
> **Version**: `1.0.0`  
> **Updated**: `2026-09-08`  
> **Status**: `PROPOSED`  
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status  
> **Compatibility target**: Additive, isolated, opt-in (Phase 4–5)  
> **Base specification**: `GRAPH-INTELLIGENCE.md`, `GRAPH-RETRIEVAL.md`, `DISCOVERY.md`  
> **Normative owner**: This document owns interactive graph projection, layout contracts, visual invariants, and error family `E250–E269`  
> **Related documents**: `DATA_MODEL.md`, `ONTOLOGY.md`, `RETRIEVAL.md`, `SCHEMA.md`  

---

## 1. Purpose & Core Philosophy

The Graph Visualization engine materializes interactive visual projections of the knowledge graph from canonical Markdown notes, normative registries, and derived graph analytics (`node_metrics.jsonl`, `derived_edges.jsonl`).

In conformance with the core architecture axiom (*"A Compiler, Not An Agent"* and *"All Databases are Disposable"*):
1. **Visualization is a Pure Projection:** The generated visual artifacts (standalone HTML/SVG) are 100% disposable derived projections. Markdown notes remain the single source of truth (`CANON-004`).
2. **Air-Gap & Offline Invariant:** The visualization MUST operate entirely offline without network access, third-party CDN calls, tracking beacons, or external font/script dependencies (`VIS-002`).
3. **Dual Edge Modality:** The renderer strictly differentiates between human-verified canonical ontology relations (`relation_registry.yaml`) and machine-inferred derived edges (`derived_edges.jsonl`), guaranteeing that unverified statistical connections never masquerade as canonical ontology links (`VIS-003`).

```text
Canonical Markdown Objects (personal/ & engineering/)
                      │
                      ▼
     Graph Intelligence Engine (Analysis & Delta)
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
node_metrics.jsonl          derived_edges.jsonl
        │                           │
        └─────────────┬─────────────┘
                      ▼
       trashheap graph visualize
                      │
                      ▼
      Standalone Self-Contained graph.html (Zero Network)
```

---

## 2. Normative Visual Invariants (VIS-001–VIS-015)

| Invariant | Domain | Specification Rule | Error Code |
|---|---|---|---|
| **VIS-001** | Projection | Graph visualization SHALL be a purely derived, rebuildable artifact. Regenerating it from the same corpus and derived manifest MUST be deterministic bit-for-bit. | `E250` |
| **VIS-002** | Air-Gap | The output HTML bundle MUST be self-contained, bundling all JavaScript (e.g. Vis Network / D3) and CSS inline. External `<script src="https://...">` calls are strictly forbidden. | `E251` |
| **VIS-003** | Edge Typology | Canonical edges SHALL render as solid lines styled by relation type category (structural, dependency, lineage, semantic). Inferred derived edges SHALL render as dashed lines with opacity proportional to `final_score`. | `E252` |
| **VIS-004** | Node Scaling | Node radius SHALL scale deterministically with In-Degree Centrality ($\phi_5$) or PageRank within a bounded interval $[r_{\min}, r_{\max}]$ ($10\text{px} \le r \le 40\text{px}$). | `E253` |
| **VIS-005** | Partitioning | Node color palettes SHALL be assigned deterministically based on primary taxonomy category (`TX-PERS-01..10`, `TX-ENG-01..02`) or per-scope community partition ID. | `E254` |
| **VIS-006** | Excerpt Cap | Node interaction tooltips and sidebar inspectors MUST enforce bounded excerpt length ($\le 250$ chars) to preserve context boundaries (`RETRIEVAL.md` §9.5.1). | `E255` |
| **VIS-007** | Filter Knobs | The client interface MUST provide dynamic controls for: scope selection (`personal`, `engineering`, `all`), minimum edge strength slider ($[0.15, 1.0]$), and taxonomy category toggles. | `E256` |
| **VIS-008** | Stabilization | The layout physics simulation (ForceAtlas2 / Barnes-Hut) MUST execute with a maximum iteration ceiling and auto-freeze after stabilization to prevent client CPU thrashing. | `E257` |
| **VIS-009** | Epistemic Badge | Visual inspection of any node SHALL render its epistemic badge (`evidence`, `verification`, `confidence`), flagging unverified draft nodes with distinct visual markers (e.g. hatched border). | `E258` |
| **VIS-010** | Path Isolation | Emitted file paths in visual metadata MUST be stored relative to the repository root and MUST NOT leak absolute OS host usernames (`/home/<user>`). | `E259` |

---

## 3. Data Schema for Graph Materialization

The visualization engine consumes the canonical corpus and derived artifacts, transforming them into a structured JSON payload embedded directly into the standalone HTML file:

```json
{
  "meta": {
    "corpus_hash": "sha256:dce95b0481b394a3d8539c2b05df6558ee6db2bc66f313558980a255866020aa",
    "generated_at": "2026-09-08T12:00:00Z",
    "architecture_version": "3.8.10",
    "nodes_count": 572,
    "canonical_edges_count": 120,
    "derived_edges_count": 13047
  },
  "nodes": [
    {
      "id": "PERS-CON-MIG_SWARM_INTELLIGENCE_245476-0001",
      "label": "Swarm Intelligence",
      "title": "Swarm Intelligence — Svärmintelligens",
      "scope": "personal",
      "taxonomy_id": "TX-PERS-09",
      "taxonomy_path": "09. Strategi, Management & Ledarskap",
      "object_type": "Concept",
      "status": "draft",
      "epistemology": {
        "evidence": "inferred",
        "verification": "unverified",
        "confidence": 0.5
      },
      "radius": 18.5,
      "color": "#4A90E2",
      "body_excerpt": "Sociala insekter som myror, bin och termiter uppvisar en anmärkningsvärd förmåga att lösa komplexa problem..."
    }
  ],
  "edges": [
    {
      "id": "edge_canonical_001",
      "source": "PERS-CON-MATH-0001",
      "target": "PERS-DEF-LOGIC-0001",
      "type": "canonical",
      "relation": "DEPENDS_ON",
      "style": "solid",
      "color": "#2ECC71",
      "weight": 1.0
    },
    {
      "id": "d_edge_PERS-CON-MIG_USMC_SURVIVAL_MANUAL_PERS-CON-MIG_US_ARMY_SURVIVAL_MANUAL",
      "source": "PERS-CON-MIG_USMC_SURVIVAL_MANUAL_A3BB86-0001",
      "target": "PERS-CON-MIG_US_ARMY_SURVIVAL_MANUAL_8AC16B-0001",
      "type": "derived",
      "relation": "DERIVED_SIMILARITY",
      "style": "dashed",
      "color": "#95A5A6",
      "weight": 0.1897,
      "components": {
        "similarity": 0.9484,
        "proximity": 0.0,
        "cooccurrence": 0.0
      }
    }
  ]
}
```

---

## 4. CLI Interface Specification

The CLI command is exposed as a subcommand of `trashheap graph`:

```bash
trashheap graph visualize [OPTIONS]
```

### Options:
- `--corpus-root <DIR>`: Root directory of Knowledge Objects (default: `fixtures/canonical`).
- `--derived-dir <DIR>`: Directory containing `node_metrics.jsonl` and `derived_edges.jsonl` (default: `derived/graph`).
- `--output <FILE>`: Destination HTML file (default: `derived/graph/visualization.html`).
- `--scope <personal|engineering|all>`: Filter nodes to a specific scope (default: `all`).
- `--min-strength <FLOAT>`: Minimum edge strength cutoff for derived edges (default: `0.15`).
- `--max-nodes <INT>`: Maximum node ceiling for rendering optimization (default: `2000`).
- `--offline-vendor <DIR>`: Optional custom path to vendorized JavaScript libraries.
- `--json`: Emit machine-readable status summary with export statistics.

---

## 5. Error Codes (`E250–E269`)

- `E250: VisualizationExportError` — General export materialization failure.
- `E251: MissingDerivedGraphError` — Attempted to visualize without prior `trashheap graph analyze` output.
- `E252: AirGapSecurityViolationError` — Found non-vendorized external resource links or CDNs in bundle template.
- `E253: NodeLimitExceededError` — Graph node count exceeds configured canvas rendering safety ceiling without clustering.
- `E254: InvariantViolationError` — Emitted visual bundle fails schema validation or contains unmasked absolute paths.
