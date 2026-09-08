---
title: "From Text to Knowledge Graph in One Command: Building a Modular LLM-Backed Framework"
author: "Fabio Yáñez Romero"
author_url: "https://medium.com/@fabioyanezromero"
source: "https://pub.towardsai.net/from-text-to-knowledge-graph-in-one-command-building-a-modular-llm-backed-framework-ec98abd3d565"
published: "2026-03-30"
fetched: "2026-09-08"
reading_time_min: 12.3
tags: ["knowledge-graphs", "python", "nlp", "data-engineering", "machine-learning"]
member_only: true
body_source: "medium-session"
---

# From Text to Knowledge Graph in One Command: Building a Modular LLM-Backed Framework

### How abstraction, registries, and a clean CLI turn chaotic text into structured, queryable knowledge — without locking you into a single model or pipeline

![](https://miro.medium.com/v2/1*QK0tqsaa4JGaecPWw4h5Gg.png)

LLMs can summarise a legal contract, answer questions about a medical record, and extract entities from a research paper. But ask them to produce a *structured, trustworthy knowledge graph* from any of those documents, and you’ll spend more time cleaning up hallucinated relations and disconnected nodes than you would have spent reading the text yourself.

So you build tooling around it. And if you’ve ever done that, you know how it ends: a tangle of provider-specific scripts, hard-coded prompts, and a `run_pipeline_v3_FINAL_fixed.py` that only you understand — and only on a good day.

> ***This is Part 2 of a series on building and augmenting knowledge graphs from unstructured text.** [In Part 1](#), we covered Information Extraction fundamentals, the difference between asserted and augmented knowledge graphs, and why end-to-end systems beat the ones that involve several steps. This post focuses on the architectural design and practical use of the framework we built on top of those ideas: ***Knowledge Graph Builder.**

[[**GitHub - FabioYanezRomero/Knowledge-Graph-Builder: Repository for building knowledge graphs from…**
*Repository for building knowledge graphs from specific datasets using generative language model through ollama …*github.com](https://github.com/FabioYanezRomero/Knowledge-Graph-Builder)](https://github.com/FabioYanezRomero/Knowledge-Graph-Builder)

A general-purpose knowledge graph extractor will underperform a domain-specific one almost every time — that’s well established. The real problem starts when you try to make your tool domain-specific: suddenly, you’re maintaining separate scripts for each domain, duplicating logic across providers, and watching a clean prototype collapse into a tangled mess of hard-coded paths and copy-pasted prompts.

The *Knowledge Graph Builder* is built around a specific bet — that you can have full domain specialisation without any of that boilerplate. Every component in the framework is independently replaceable, yet the whole thing still runs from a single command.

In this post, we’ll walk through its architecture: how each module works, how they compose into a complete extraction-augmentation-visualisation pipeline, and why swapping a provider, a domain, or an output format is a matter of changing one flag — not rewriting your pipeline.

## 📌 What You’ll Learn

- How five independent modules — clients, builders, domains, **I/O (readers and writers)**, and visualisation — connect through registries into a single pipeline.
- Why BaseLLMClient separates *grounded extraction* from *unconstrained augmentation *— and why that distinction matters for graph quality.
- How custom provider subclasses make local models work alongside cloud APIs without any changes to the core pipeline.
- How the Domain module packages prompts, few-shot examples, and schemas so that switching from `--domain legal` to `--domain medical` changes the entire extraction vocabulary.
- How the YAML-configured pipeline and CLI turn a four-step workflow into a single, reproducible command, promoting reusability and storage without boilerplate code.

## The Core Idea: Abstraction as the Brain, CLI as the Heart

*Knowledge Graph Builder* is a modular Python framework that extracts knowledge graphs from unstructured text, using Google’s [langextract](https://github.com/google/langextract) library to obtain *grounded* triples — extractions anchored to specific character positions in the source text. From there, it can augment those graphs with inferred relationships, convert them to standard formats, and visualise the results.

![Knowledge Graph Builder architecture overview: the Builder orchestrates Domains and Clients for knowledge graph construction, while the Pipeline wraps the full workflow — from input parsing to visualisation — under a single CLI. Image by the author.](https://miro.medium.com/v2/1*o7PCWh3mxEvay1PQJPL0XQ.png)

The framework’s architecture centres on one principle:

> **Every component prone to change shall be easy to swap, maintaining the usability of the entire framework for creating knowledge graphs.**

- The LLM provider changes? Swap the client.
- Need a new generation strategy? Add a builder.
- New domain? Just add a folder.
- New dataset input format? Add a Reader.
- New graph output format? Add a writer.

The framework doesn’t force you to modify its core to extend it.

There are five primary modules:

- **Clients** — abstract wrappers for LLM providers (Gemini, Ollama, LM Studio, and others).
- **Builders** — the core logic that indicates the different tasks an LLM will perform for getting and improving the knowledge graph.
- **Domains** — packaged prompt templates, few-shot examples, and entity/relation schemas.
- **I/O (Readers & Writers)** — input format detection and graph format conversion.
- **Visualisation** — interactive graph rendering with provenance colour-coding, focusing on distinguishing the graph elements based on the methods used to obtain them.

Each module has a registry that maps string keys to implementations, making them CLI-accessible without any conditional imports or verbose configuration. Also, you can wrap a complete process in a pipeline, which is a quality-of-life improvement that lets you store your favourite configurations.

Let’s go through them.

## The Builder: Where the Actual Work Happens

Before touching any client or provider, it’s worth understanding the Builder — because it’s where the actual work happens. The clients don’t implement their own extraction logic; they delegate to the Builder.

> The builder defines the blueprint for the actions the framework can take to obtain the knowledge graph.

### Extraction Builder

The **Extraction Builder** handles prompt construction, few-shot example injection, and triple normalisation. All of this is unified into a single function that integrates the other modules using langextract.

Right now, extraction is always grounded via langextract, which means every triple it returns comes with character-level source spans — you always know exactly where in the document a claim came from.

> With LangExtract every triple comes anchored to the exact characters in the source text — so you can always trace a claim back to the sentence that produced it.

### Augmentation Builder

The **Augmentation Builder** is more open. It uses a **strategy registry** — a protocol-based pattern in which each augmentation strategy is a class that uses a decorator to store the strategy inside the registry.

The protocol specifies the minimum required signature (client, domain prompt, examples, and the ground-truth triples), but each strategy implements its own logic.

This way, we can cleanly define the minimum required parameters, and you can focus on the specific logic for your use case scenario.

The only strategy currently implemented is connectivity, which reduces disconnected components in the graph by inferring bridging triples.

> Adding a new strategy means writing one class and applying a decorator.

### The distinction between Extraction and Augmentation

Mix extraction with augmentation, and you lose the one thing that makes your graph trustworthy: knowing which triples came from the text and which the model inferred on its own.

Keeping them separate means you always know which triples are asserted and which are inferred — a distinction that matters enormously for any downstream task that depends on trust or verifiability.

## One Interface, Every Provider

The client layer is where provider diversity is tamed. Every provider — whether it’s a cloud API or a locally-hosted model — must implement ***BaseLLMClient***, an abstract class that enforces two methods:

```python
class BaseLLMClient(ABC):

    @abstractmethod
    def extract(self, text, prompt_description, examples=None,
                format_type=None, temperature=None, max_tokens=None, **kwargs):
        """Grounded extraction — returns triples with source character positions."""
        pass

    @abstractmethod
    def augment(self, text, prompt_description, format_type,
                temperature=None, max_tokens=None, **kwargs):
        """Ungrounded augmentation — inferred triples, no source spans required."""
        pass
```

The separation between extract() and augment() is intentional as it matches the Builder logic:

- Grounded extraction asks: *what is explicitly stated in this text?*
- Augmentation asks: *given what we know and also the augmentation strategy, which nodes and relations can we infer to populate the graph?*

But also, each provider subclass implements ***from_config()***, which translates a flat ClientConfig object into a call to its own constructor.

This is what makes the CLI ergonomic: rather than specifying —api-key, —base-url, —timeout, and —model as separate flags that mean different things across providers, you pass a single config object and let each client handle its own defaults.

```python
# These three calls behave identically from the CLI's perspective:
ClientFactory.from_config(client_type="gemini",  model_id="gemini-2.0-flash", api_key="...")
ClientFactory.from_config(client_type="ollama",  model_id="gemma3:27b",       base_url="http://localhost:11434")
ClientFactory.from_config(client_type="lmstudio",model_id="gemma-3-27b-it",   base_url="http://localhost:1234")
```

The ClientFactory maintains a registry of provider classes, populated at import time by a @client decorator on each provider file.

The CLI doesn’t need to know anything about how each provider is constructed — it just calls ClientFactory.create(config) and gets back a fully initialised instance.

## Domains: Switch the Domain, Change Everything

Getting good outputs from a language model — especially for a structured task like knowledge graph extraction — requires more than a clever prompt.

You need domain-appropriate vocabulary, carefully chosen few-shot examples, and a schema that constrains the output. The Domain module packages all of this together, as each domain is a folder with a predictable structure. This is one example for the legal domain:

```
legal/
├── extraction/
│   ├── prompt.md
│   └── examples.json
├── augmentation/
│   └── connectivity/
│       ├── prompt.md
│       └── examples.json
└── schema.json
```

The KnowledgeDomain abstract class loads these resources from disk, providing all the building blocks needed to assemble the prompt.

Augmentation strategies have their own subdirectories, so each strategy gets its own prompt and examples without any naming conflicts. There might be many augmentation strategies based on your use case.

The practical implication is significant:

> **swapping domains changes the entire extraction vocabulary without touching the pipeline code**

A domain registry (using the same decorator pattern as the client registry) makes domains CLI-accessible by name. This is the framework’s consistent pattern: convention-based string registration everywhere, so the CLI stays thin.

## I/O: Getting Data In and Out Without Friction

With structured extraction, getting data in and out cleanly matters as much as the extraction itself.

The **Readers** submodule automatically handles format detection and loading from JSON, JSONL, and CSV files based on their extensions. The load_records() function accepts optional field-name overrides and a limit parameter, making it straightforward to run experiments on subsets of a corpus.

The **Writers** submodule currently outputs [**GraphML](https://networkx.org/documentation/stable/reference/readwrite/graphml.html)** via a normalisation pipeline that cleans and deduplicates the LLM-generated triples before serialising them. GraphML is the right default: it’s compatible with [NetworkX](https://networkx.org/), [Gephi](https://gephi.org/), and most graph analysis tooling.

> The design makes it easy to add new writers — turtle for ontology workflows, Cypher for [Neo4j](https://neo4j.com/)…

The Triple data model that connects the two is worth noting. Each triple carries an inference field that marks it as explicit (directly stated) or contextual (inferred by the augmentation step), along with an optional justification for contextual triples. This provenance is preserved all the way through to the GraphML output.

## Visualisation: Making the Graph Legible

Even if the output JSON format for the obtained knowledge graphs is suitable for storing all the information, it is not visually pleasing.

To easily assess the quality of the generated knowledge graph, a visualisation module is essential, as it makes the structure legible to a domain expert curating or validating the output.

In this sense, *Knowledge Graph Builder* keeps langextract’s original visualisation for ground-truth inspection — it highlights extracted entities and relations directly in the source text, marked by character offsets.

![Ground-truth inspection via langextract: extracted entities are highlighted directly in the source text, colour-coded by role (head or tail), with character-level offsets that let you trace every triple back to the exact sentence that produced it. The playback controls step through entities one by one, making it easy to audit extraction quality on a per-record basis. Image by the author.](https://miro.medium.com/v2/1*kX3LMom2Fi18iwYy5rnaqw.png)

For the graph itself, an interactive network visualisation renders the full knowledge graph in the browser. The graph differentiates several properties at a glance:

- Ground-truth and augmented triples are clearly distinguished through colour and edge styling, so you can immediately see how much the connectivity strategy changed the graph structure.
- The size of each node scales with degree centrality, making the most connected entities obvious.
- Nodes are draggable, and a search bar filters entities in real time.
- A built-in path finder highlights the shortest route between any two nodes — useful for tracing how entities connect across the graph.
- You can switch layouts, toggle between dark and light themes, and export the current view as PNG, SVG, or JSON.

We kept the HTML interactive visualisation for all those reasons!

![Interactive network visualisation of the extracted knowledge graph: node size reflects degree centrality, edge colour distinguishes ground-truth triples from augmented ones, and labels remain readable through a force-directed layout. The large central node marks the most-connected entity in the graph — a pattern that is immediately visible at a glance but would be buried in raw JSON output. To keep the layout clean, only the most connected nodes display their labels directly; the rest reveal their names on hover, so the graph stays legible even as it grows. Image by the author.](https://miro.medium.com/v2/1*QGrBo2lbECBwuaYsGHn-tg.png)

But for larger graphs, this visualisation becomes less practical — which is a known limitation and a likely target for future work.

## The Builder as the Knowledge Graph Orchestrator

At this point, it’s worth stepping back to see how the Builder relates to the modules we’ve just covered. The Builder is the only component that touches both Domains and Clients at the same time — it pulls prompts and examples from the Domain, routes them through the Client, and validates the results. That makes it the natural orchestration layer for everything that involves the language model: extraction, augmentation, prompt assembly, and output validation all live here.

But the Builder only cares about the LLM side. It doesn’t handle input formats, graph conversion, or visualisation. For a complete data-engineering workflow, we need something that wraps the Builder’s orchestration into a broader pipeline — which is exactly what the next module provides.

![Inside the Builder: input records flow through prompt assembly and LLM execution (via Client), then through validation (constrained by the Domain’s schema) before leaving as output graphs. The Domain provides resources, the Client handles model calls, and the Builder orchestrates both. Image by the author.](https://miro.medium.com/v2/1*Wi2ogAnDpZrzjFn27kcNKw.png)

## The Pipeline: Where Everything Clicks Together

The builder effectively abstracts all language-model usage in building the knowledge graph, but that is not enough for the entire data-engineering pipeline.

> All five modules above are useful individually, but the real value comes from composing them.

To solve this problem, the Pipeline module provides the outer orchestration layer — a way to declare a full extraction workflow as a reusable, version-controlled configuration.

The module has three components:

- **PipelineContext** is the data carrier: it holds the record ID, source text, accumulated triples, metadata, and errors for a single document as it flows through the pipeline, maintaining traceability.
- **PipelineRunner** executes an ordered list of steps against a batch of contexts, using a ThreadPoolExecutor for parallel processing.
- **YAML configuration files** declare the entire pipeline — client, domain, input, and step parameters — into a single portable document.

Currently, six steps are registered in the pipeline:

![](https://miro.medium.com/v2/1*IhXxpNZfDL40k64_CaNyuw.png)

And here is an example of a pipeline YAML file, integrating all the previous operations for your experiment:

```yaml
client:
  type: gemini
  model: gemini-2.0-flash

domain:
  name: legal
  extraction_mode: open

input:
  path: data/legal/legal_background.jsonl
  text_field: text

output_dir: outputs/kg_extraction

steps:
  - extract
  - augment:
      max_disconnected: 1
      max_iterations: 5
  - convert
  - visualize-network
```

This config is reproducible, shareable, and overridable: any value can be replaced at invocation time via CLI flags, so you can use the same base recipe with different input files or model configurations.

But we cannot finish talking about the framework without introducing the cherry on the cake: the CLI, our last quality-of-life feature for easily executing all the different configurations we already stored.

## The CLI: One Command to Run It All

Everything described above is accessible from a single *kgb* console script. Each command does one thing and produces output that the next command can consume:

We can run each granular step with the CLI to build the pipeline (extract, augment, convert, visualize…).

```bash
# Step 1 — Grounded extraction: triples with character-level source anchors
kgb extract --input data/legal/legal_background.jsonl \
            --domain legal --client gemini --model gemini-2.0-flash

# Step 2 — Augmentation: inferred bridging triples to reduce disconnected components
kgb augment connectivity --input data/legal/legal_background.jsonl \
            --domain legal --client gemini --max-disconnected 1 --max-iterations 5

# Step 3 — Conversion to GraphML
kgb convert --input outputs/kg_extraction/extracted_json

# Step 4 — Visualisation
kgb visualize network --input outputs/kg_extraction/graphml --dark-mode
kgb visualize extraction --input data/legal/legal_background.jsonl \
            --triples outputs/kg_extraction/extracted_json
```

Or directly execute the stored pipeline in the defined YAML with the command run-pipeline.

```bash
# Flag-based: toggle individual stages
kgb run-pipeline --input data/legal/legal_background.jsonl \
                 --domain legal --client gemini \
                 --extract --augment --convert --visualize

# Config-based: load a reusable YAML recipe
kgb run-pipeline --config kgb/pipeline/configs/legal_gemini.yaml
```

Also, running just “***kgb”*** with no arguments launches an interactive terminal with readline history and tab completion, useful when testing your configurations. This tool has been built with [Typer CLI](https://typer.tiangolo.com/).

## What This Architecture Actually Buys You

It’s worth stepping back to articulate what the modular design achieves — not just what it contains.

**Provider independence.** Running the same extraction against Gemini, a local Ollama instance, and LM Studio requires no changes to the pipeline. This matters both for cost management (local models for iteration, cloud APIs for production) and for the kind of comparative evaluation we’ll explore in the next post.

**Domain portability.** The same pipeline code can process legal documents, medical records, or scientific literature by switching a single flag. The extraction vocabulary, examples, and constraints all travel with the domain folder, not the code.

**Reproducibility.** YAML pipeline configs are version-controllable and shareable. Anyone with access to the same model and domain can reproduce your graph exactly.

**Incremental adoption.** You can drop into any stage of the pipeline with pre-existing data. If you already have extracted triples in JSON, you don’t need to re-run extraction to test a new visualisation.

## What Comes Next

The framework architecture is the foundation. But a framework only proves its worth when you put it to work.

In the next post, we’ll run a systematic evaluation across **13 model configurations **— covering Gemini 2.0 Flash, Gemini 2.5 Flash, several Gemini 3 variants, and multiple Gemma models via both Ollama and LM Studio — against a legal corpus. We’ll compare extraction quality, augmentation behaviour, and the practical differences between running these models through a cloud API versus local inference.

The results surface some genuinely surprising patterns — about which providers actually deliver on extraction quality, how much model size really matters, and where local inference holds its own against cloud APIs. Not always the outcomes you’d expect.

## From `run_pipeline_v3_FINAL` to `kgb run-pipeline`

That tangle of provider-specific scripts and copy-pasted prompts from the opening? *Knowledge Graph Builder* replaces it with five swappable modules, a registry pattern that keeps the CLI thin, and a YAML config you can version-control and share. One command, full provenance, any provider.

The *Knowledge Graph Builder* repository is available on [GitHub](https://github.com/FabioYanezRomero/Knowledge-Graph-Builder). It ships with shell scripts for each backend, the legal domain configuration used in our upcoming evaluation, and YAML pipeline templates for getting started. If you’re working on information extraction in a specific domain and want to discuss extending the framework, feel free to reach out.

> **Understanding should not be a luxury reserved for specialists.**
My goal is to make frontier AI and machine learning research accessible through clear, tutorial-style explanations.

> If this piece helped you think more clearly about the topic, showing support with **claps** or a **subscription** genuinely helps keep this work going.

> You’re always welcome to connect with me on [**LinkedIn](https://www.linkedin.com/in/fabio-yanez/)**, where I share more writing and ideas in the same spirit.
