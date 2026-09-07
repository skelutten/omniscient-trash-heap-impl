# The Omniscient Trash Heap — Reference Implementation

> *All the sources. All the wisdom. Some of the trash.*

**The Omniscient Trash Heap** (`trashheap`) är den officiella och fullt verifierade Python-referensimplementationen av kunskapsarkitekturen LLM Wiki (v3.8.10). Systemet tillhandahåller deterministisk kunskapskompilering, flerskiktad validering (Lager 1–5), strikt epistemisk proveniens, hybrid återhämtning (RRF över BM25, kunskapsgraf och tät vektorrepresentation), strukturell kodanalys (AST) samt tvåvägs interoperabilitet med Google Open Knowledge Foundation (OKF v0.2).

### Specifikationer & Planer
Detta repository fokuserar strikt på den körbara implementationen och testerna. Normativa specifikationer, arkitekturkrav och den fullständiga implementationshistoriken hanteras i specifikationsrepot:
👉 **[skelutten/omniscient-trash-heap-spec](https://github.com/skelutten/omniscient-trash-heap-spec)**
- [Normativa specifikationer (`specs/`)](https://github.com/skelutten/omniscient-trash-heap-spec/tree/master/specs)
- [Implementationsplaner (`plans/`)](https://github.com/skelutten/omniscient-trash-heap-spec/tree/master/plans)
- [Beslutslogg (`plans/DECISION_LOG.md`)](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/plans/DECISION_LOG.md)

---

## Snabbstart med `uv`

Projektet körs smidigast med [`uv`](https://github.com/astral-sh/uv). Ingen manuell aktivering av virtuella miljöer krävs:

```bash
# Synkronisera projektets beroenden (inklusive opt-in Parquet/DuckDB)
uv sync --extra parquet

# Verifiera att alla 10 YAML-register laddar och validerar korrekt
uv run trashheap check-registries

# Kör hela test- och valideringsgrinden (130 tester, 37/37 arkitekturfamiljer)
bash tools/check.sh
```

Om du vill installera `trashheap` som ett globalt CLI-verktyg i din användarprofil:
```bash
uv tool install .
```

---

## Installera Agent Skill (`.agents/skills/trashheap`)

Projektet följer den öppna standarden **Agent Skills** (`agentskills.io` / `dot-agents.com`). AI-agenter (t.ex. Antigravity, Claude Code, Cursor) använder denna skill för att känna till systemets slash-kommandon (`/lint`, `/validate`, `/query`, `/show`, `/stage-lint`, `/ingest`, `/rebuild`).

### 1. Projektnivå (Automatisk)
Skillen genereras automatiskt i repot under:
```text
.agents/skills/trashheap/SKILL.md
```
Agenter som öppnar detta repository upptäcker och laddar den automatiskt. För att synkronisera filen med senaste scheman och källkod:
```bash
uv run trashheap generate-skills
```

### 2. Global användarnivå (Tillgänglig i alla projekt och mappar)
Om du vill att dina agenter ska ha tillgång till `trashheap`-kommandona även när du arbetar i andra projekt och kataloger kan du installera skillen globalt i din användarprofil:

```bash
# Automatisk global installation till ~/.agents/skills/trashheap/SKILL.md
uv run trashheap generate-skills --global

# Alternativt skapa en symbolisk länk:
mkdir -p ~/.agents/skills
ln -sfn $(pwd)/.agents/skills/trashheap ~/.agents/skills/trashheap
```

---

## Var lagras allt? (Datalayout)

Systemet separerar strikt mellan kod/motor, kanoniska referensfixturer och externa wikikorpusar:

1. **Projektkällkod och motor:**
   - Plats: `/home/daniel6651/omniscient-trash-heap-impl` (detta repository)
   - CLI-paket: `trashheap/`
   - Formella specifikationer: `specs/`
   - Scheman och register: `schemas/registry/`
2. **Kanonisk referenskorpus (Testfixturer):**
   - Plats: `fixtures/canonical/`
   - Innehåller 20 certifierade Knowledge Objects som används för automatiska tester, linter-verifiering och specifikationskonformans.
   - Detta är standardmålet (`--corpus-root`) för CLI-kommandon om inget annat anges.
3. **Den konverterade wikin:**
   - Plats: `/home/daniel6651/wiki`
   - Innehåller **572 konverterade artiklar** organiserade i taxonomiska underkataloger under `personal/` (t.ex. `02_formella_vetenskaper_matematik/`, `04_psykologi_kognition/`, etc.).
   - Varje artikel har fullständig frontmatter och länk till ursprunglig källfil (`source_refs`).
4. **Den orörda råa gamla wikin:**
   - Plats: `/home/daniel6651/wiki-old/wiki`
   - Bevarad som historisk oföränderlig råkälla (read-only snapshot).

---

## Sökning och Återhämtning (`query`)

Kommandot `query` kör hybrid RRF-sökning (Reciprocal Rank Fusion) och returnerar ett strukturerat **Evidence Bundle** i JSON-format.

### Söka i den konverterade wikin

Eftersom standardkatalogen är `fixtures/canonical/` behöver du peka ut din wiki med `--corpus-root`:

```bash
uv run trashheap query "poker" --corpus-root /home/daniel6651/wiki --include-drafts
```

### Varför behövs `--include-drafts` för gamla wikin?

Enligt migreringsspecifikationen ([Plan 60](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/plans/60-OLD-WIKI-MIGRATION.md) / Kontraktsregel 10) importeras legacy-artiklar med säkerhetsstatus `status: draft`. Detta förhindrar att omodererat material automatiskt markeras som formellt fastställd sanning (`status: established`).

Sökmotorn filtrerar som standard bort `draft`-objekt i kanoniskt läge. Med flaggan `--include-drafts` inkluderas alla migrerade artiklar i sökresultaten.

### Avancerade sökflaggor

```bash
# Aktivera opt-in semantisk vektoråterhämtning
uv run trashheap query "game theory decision making" --corpus-root /home/daniel6651/wiki --include-drafts --vector

# Filtrera på scope
uv run trashheap query "arkitektur" --scope engineering

# Returnera hela brödtexten för varje träff i JSON-svaret
uv run trashheap query "poker" --corpus-root /home/daniel6651/wiki --include-drafts --include-body
```

---

## Läsa hela artiklar (`show` och filsystemet)

I Evidence Bundle är fältet `body_excerpt` avsiktligt begränsat till ett kort utdrag ($\le 250$ tecken) för att snabbt ge en överblick och spara LLM-tokenbudget vid sökning. **All text, tabeller och kapitelanalyser finns fullständigt bevarade på disk.**

### Alternativ 1: Använd kommandot `trashheap show` (rekommenderat)

Skicka artikelns `node_id` eller relativa filnamn direkt till `trashheap show`:

```bash
uv run trashheap show PERS-DOC-MIG_DOYLE_BRUNSON_SUPER_SYSTEM_1_2CC294-0001 --corpus-root /home/daniel6651/wiki
```
Detta skriver ut hela den fullständiga Markdown-artikeln direkt i terminalen.

### Alternativ 2: Öppna direkt via `"path"` i filsystemet

Varje träff i sökresultatet innehåller fältet `"path"`. Eftersom artiklarna är vanliga Markdown-filer kan de öppnas direkt i valfri editor (`less`, `cat`, VS Code, Obsidian):

```bash
cat /home/daniel6651/wiki/personal/02_formella_vetenskaper_matematik/PERS-DOC-MIG_DOYLE_BRUNSON_SUPER_SYSTEM_1_2CC294-0001.md
```

### Alternativ 3: Begär full text vid sökning

Lägg till `--include-body` vid anrop till `trashheap query` för att få hela brödtexten under nyckeln `"body"` i JSON-strukturen.

---

## Smidigt Shell-Alias

För att slippa skriva `--corpus-root /home/daniel6651/wiki --include-drafts` varje gång kan du lägga till ett alias i din `~/.bashrc`:

```bash
alias mywiki='uv run --directory /home/daniel6651/omniscient-trash-heap-impl trashheap query --corpus-root /home/daniel6651/wiki --include-drafts'
alias mywikishow='uv run --directory /home/daniel6651/omniscient-trash-heap-impl trashheap show --corpus-root /home/daniel6651/wiki'
```

Sedan kan du enkelt köra:
```bash
mywiki "poker"
mywikishow PERS-DOC-MIG_DOYLE_BRUNSON_SUPER_SYSTEM_1_2CC294-0001
```

---

## Översikt över CLI-kommandon

| Kommando | Beskrivning | Exempel |
|---|---|---|
| `query` | Hybrid RRF-sökning (BM25 + graf + vektor) | `uv run trashheap query "architecture"` |
| `show` | Visa hela innehållet för ett Knowledge Object | `uv run trashheap show <node-id> --corpus-root /home/daniel6651/wiki` |
| `lint` | Flerskiktad validering av Markdown-filer (Lager 1–5) | `uv run trashheap lint fixtures/canonical` |
| `validate` | Validera en specifik fil inom korpuskontext | `uv run trashheap validate <path/to/file.md>` |
| `check-registries` | Validera alla 10 YAML-scheman och register | `uv run trashheap check-registries` |
| `staging` | Parquet/DuckDB analytisk staging och ekvivalens | `uv run trashheap staging status` |
| `structural` | AST-kodgraf, indexering och konsekvensanalys | `uv run trashheap structural impact --symbol HybridRetriever` |
| `graph` | Grafintelligens, klusteranalys och topologiska gap | `uv run trashheap graph analyze` |
| `discover` | Upptäcka dubbletter, ontologiska och topologiska gap | `uv run trashheap discover scan` |
| `ingest` | Säker inläsning av råkällor med path-sandboxing | `uv run trashheap ingest <source-path> --profile document` |
| `stage-lint` | Inspektera och validera staging-området | `uv run trashheap stage-lint` |
| `review` | Granska kandidatförslag inför promotering | `uv run trashheap review list` |
| `promote` | Atomär och transaktionssäker promotion via DPCP | `uv run trashheap promote <proposal-id> --actor user@example.com` |
| `bundle` | Exportera och importera Knowledge Bundles / OKF v0.2 | `uv run trashheap bundle export --scope engineering --format okf` |
| `migrate` | Migrera äldre wikikorpusar enligt regler 1–11 | `uv run trashheap migrate plan --source-dir ... --target-dir ...` |
| `rename` | Atomär omdöpning med propagering av länkar och graf | `uv run trashheap rename --old-id ... --new-id ...` |
| `rebuild` | Återskapa index och cacher direkt från Markdown | `uv run trashheap rebuild` |
| `status` | Visa systemstatus, hållbarhet och kunskapsskuld | `uv run trashheap status` |
| `reap` | Rensa utgångna förslag enligt TTL-regler | `uv run trashheap reap` |
| `conformance` | Generera konformansmatris (37/37 familjer) | `uv run trashheap conformance` |

---

## Verifiering och Testning

Hela systemets integritet garanteras genom automatiserade tester och grindar:

```bash
# Kör hela verifieringsgrinden
bash tools/check.sh

# Kör enbart enhetstester och integrationstester
uv run pytest -v

# Kör Ruff-linter
uv run ruff check
```
