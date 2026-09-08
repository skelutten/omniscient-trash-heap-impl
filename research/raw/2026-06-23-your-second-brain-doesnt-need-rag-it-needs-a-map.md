---
title: "Your Second Brain Doesn’t Need RAG. It Needs a Map"
author: "Fabio Yáñez Romero"
author_url: "https://medium.com/@fabioyanezromero"
source: "https://pub.towardsai.net/your-second-brain-doesnt-need-rag-it-needs-a-map-5feaca01b923"
published: "2026-06-23"
fetched: "2026-09-08"
reading_time_min: 10.7
tags: ["knowledge-management", "artificial-intelligence", "ai-agent", "agentic-rag", "llm"]
member_only: true
body_source: "medium-session"
---

# Your Second Brain Doesn’t Need RAG. It Needs a Map

### Karpathy’s markdown system for retrieving information with agents appears to be the best way to avoid losing context compared with RAG and other retrieval systems, but it becomes quite expensive as the knowledge base grows. Here’s how you can deal with that without a RAG system.

![Karpathy’s approach doesn’t require Obsidian, but Obsidian has become its natural home — it works directly with Markdown and builds a graph from the wikilinks between files. Also, the addition of the Obsidian CLI works really well for interaction with agents. Image by the author.](https://miro.medium.com/v2/1*ktU8QwU9wnZK8001-oDeFg.png)

A few years ago, keeping your knowledge base as a folder of plain markdown files looked like a temporary fix — something to use until a proper tool with a database and embeddings came along.

The opposite happened. As the models improved, the flat-text vault became more useful, not less. With long enough context windows, the model could read your notes in order, the way you wrote them — no retrieved fragments to stitch back together. The compromise had become the better option.

That is why the idea of a second brain — keeping all your knowledge in plain text, Markdown being the favourite since models are already trained on it — has become so popular lately, for several reasons:

- **Agents can effectively synthesise information in the vault and perform a range of tasks **— surfacing insights, writing summaries, and correlating notes with new ideas.
- **Chunked retrieval brings its own problems** — lost context, fragments that don’t line up — which agentic reading sidesteps entirely.
- **It avoids dedicated databases and backend infrastructure**, which keeps knowledge management accessible to a non-technical audience.

> The enhancement of language models capabilities over the last year has made agentic search a good alternative for retrieving information on its own, without requiring a complex system to handle the entire retrieval process.

Karpathy’s proposal uses a very flat directory structure, with little nesting, so the agent has a clear picture of where to look, reducing the possibilities of getting lost.

> This simple yet effective approach provides context for the agent, but it falls apart as knowledge grows.

I’ll show how I solved this with the second brain I set up for myself — useful if you’d rather not migrate your whole markdown vault to something more RAG-like, with all the involved workarounds.

Karpathy’s Markdown vault does not age well, at least not in its naïve version, for the reasons discussed below.

## Where the flat vault breaks

When you point an agent at a pile of documents, it has no built-in sense of how to read them without burning through tokens.

By default, it reads the whole document you hand it — or, if you point it at a folder, every document inside. That breaks down in two cases: when you have many documents, and when you have one very large one:

- **With many documents**, you exhaust the context window fast, which makes the agent more expensive after just a couple of questions.
- **With one large document**, it’s worse: the same exhaustion, plus you’re now loading sections the task doesn’t need — noise the model has to read past.

The flat structure I described is fine for a handful of documents, but it turns into a headache once you’ve got a thousand in one directory.

> It becomes a problem not just for the agent. It’s a problem for you, the maintainer, too

Think of it like setting up a codebase: you don’t just dump every source file into one directory. You build a folder hierarchy with sensible relative paths, so your scripts can navigate it, and humans can still read it.

A markdown vault wants the same balance — not so flat that the agent has to sift one folder of thousands of files, and not so deeply nested that it walks through directory after directory to gather what it needs.

And by the time the vault has grown a lot, **you still haven’t actually needed RAG **— there are several reasons not to reach for it, and a few changes to the vault itself usually do the job instead.

## **Why RAG is usually overkill here**

Following the usual best practices for scaling a document vault, we might be tempted to use a RAG system, but it might be over-engineering in our specific case — and for a non-technical audience (and for those who don’t want to spend weeks fixing the system instead of actually using it), that is a resounding no.

The main reason not to go into the RAG style is twofold: first, we have to add many new components, which makes the system much more complex for our task and costs us a lot of time to make it work; and second, the agent has many different capabilities we haven’t explored yet that could handle this properly.

Among the different components we shall add to make it work properly at scale, we have:

- **Semantic embedding design**: which language model shall we use to generate the embeddings, based on the domain of the data, and all the hyperparameters around them, such as the chunk overlap that keeps consecutive chunks continuous, so we don’t get messy fragments glued together.
- **A vector database** that lets us index and perform the type of search we want, since we might need a hybrid search — filtering by metadata first, adding other retrieval techniques like BM25…
- **A reranker for the chunks returned** for each specific task, which at least involves a new language model specialised just for that.
- **Query rephrasing** to adapt the user’s task to the vector database before proceeding, which is a kind of translation between the user’s query and the vault’s jargon.

Those are all new components we need to add just to make the RAG work properly in our case — not for a mockup — and we still haven’t covered the evaluation of the whole RAG system, which can be a real nightmare.

And as we mentioned, the agent we’re going to use in our own vault has some capabilities we haven’t explored yet — I’m talking about the **tools** and proper **skill design**.

## **Improving the agent, not the system**

As mentioned before, recent language models have become capable enough that agentic search is a clear option; now let’s improve it with the right tools, skills, and context, rather than changing the entire system.

Language models can dramatically improve their performance using tools, which are usually represented as Python functions that the model invokes to perform different tasks; for example, a model calling a calculator function instead of doing the arithmetic in natural language, which would waste many tokens.

Among these tools are the CLI commands we use to explore the directory structure on our machines, offering many search capabilities such as “grep”, “read”, and glob expressions. The agent already uses those commands to pull the contents of the files it uses as context.

> The agent works in a loop: it issues a tool call — listing a directory, globbing a path, grepping a pattern, reading a file — looks at the result, and decides the next move

So we can take advantage of a simple, well-designed **directory structure** (the first dimension of my approach) to continue using agentic search rather than moving to a RAG system.

The model shall receive the general folder structure in its main **AGENTS.md** file, which is loaded as context by default when it is in the agent’s root folder. Alternatively, we can create a specific skill that teaches the agent how to navigate the folder structure efficiently — something the agent can build on its own with little trouble and indicate the skill in AGENTS.md.

But this approach, by itself, is missing something when dealing with larger documents, because running CLI operations directly on them loads the entire document into the context window — the same problem we set out to solve.

To solve this, **a proper card for every document** is the way to retrieve just the content we want, letting the agent know what’s inside a document without reading all of it, and how it relates to other documents in the vault (the second dimension considered in my approach).

Let’s look more closely at the two dimensions we’ve considered so far.

### **Dimension 1 — Where a document lives: folders and paths**

A folder tree with a bit of thought behind it is a free, pre-built index — because the path itself carries meaning. This synergises directly with the tools the agent has available, as we can see in the next real example:

```plaintext
vault/
  library/
    2026/
      2026–06/
        a-long-technical-report/
          card.md # the map
          full.md # the territory
```

The model never has to search for “things from June 2026.” It just walks`library/2026/2026-06/`, and this structure can be referenced directly in AGENTS.md, as mentioned before.

> A path is a coordinate, and coordinates are something file tools already know how to walk — no embedding required.

This is the one dimension that sits outside the card entirely: it’s about *where*, not *what*. Before a single document is read, the candidate set has already shrunk from “everything” to “the right neighbourhood,” based solely on folder names.

Launch your agent inside a specific folder, and it’s scoped to that folder (like Claude Code) — handy when you want it working on one project at a time instead of roaming the whole vault.

### Dimension 2 — The Map For The Entire Document: the Card

The card can be designed in many different ways, based on the nature of the documents you’re using: a paper, a report, a skill for a specific agent, a repository, etc. But there are some common areas we shall consider to make retrieval and understanding of our vault more efficient for the agent:

- **A YAML frontmatter** is a key-value configuration file that can be embedded in the document and lets the model access important metadata, such as the title, tags, date, source, or a short summary.

```yaml
---
title: "A Long Technical Report"
created: 2026-06-09
tags: [reinforcement-learning, reasoning, efficiency]
summary: "One-paragraph statement of what the document argues and shows."
key_claims:
  - "The first load-bearing claim, in one line."
  - "The second."
has_tables: true
has_figures: true
token_estimate: 14200
full_document: "library/2026/2026-06/a-long-technical-report/full.md"
---
```

- **A section map:** this component gives the document’s structure to the card. In many cases it’s just another map that tells you the different sections present in the document, as well as the length of those sections in general, so the agent can be careful about loading all the content for the task it’s performing.

```markdown
| Section | Lines | ~Tokens |
|------------------------------|---------|---------|
| Abstract                     | 25-28   | ~395    |
| Introduction                 | 29-79   | ~2143   |
| Annotation and Datasets      | 80-92   | ~907    |
| Method                       | 93-226  | ~3538   |
| Experiment                   | 227-319 | ~3120   |
| Discussions and Future Works | 360-367 | ~812    |
| Related Work                 | 368-385 | ~1489   |
| Conclusion                   | 386-391 | ~333    |
| References                   | 392-531 | ~4040   |
```

- **Wikilinks:** the links that naturally connect the original documents with other documents. Ideally, these wikilinks are inside the cards, as those consume far fewer tokens, and since any card already points to its original content, having the cards connected gives you the real connections between all the documents without loading them all at once.

```yaml
### Cited Vault Papers

- [[self-distillation-zero-self-revision-turns-binary-rewards-in]] - (builds-on)
- [[rethinking-on-policy-distillation-of-large-language-models-p]] - (builds-on)
```

This way, the card becomes a map of the entire document, fully navigable at no extra cost. If we save the documents in markdown format, their sections can be easily filtered by headers to retrieve the precise information we want using only agentic search.

> The card is the map of a territory you never have to fully enter to understand it

> You can take advantage of the first dimension considered here, as the relative paths might already indicate where the card and the real document are located. But wikilinks are difficult to replace, as they can be useful for linking documents from other projects, where relative paths become less viable.

The document card comes with certain drawbacks: we shall not only design the tag and metadata system up front, but also use an agent to create the summary and the section mapping once, to enrich the document card. I recommend creating a dedicated skill for this in AGENTS.md, so you don’t have to do it manually all the time.

![](https://miro.medium.com/v2/1*7W9_QtChyUO5g2QIbSh3fg.png)

> There is no free lunch: you either think carefully about your document vault, or take on the complex engineering of the RAG components.

## The two dimensions in action: “what moved in RL last month?”

With both dimensions in place, an expensive open-ended question becomes a short walk. Suppose you want to know what changed in reinforcement learning over the past month.

First, **filter by date**. Two nearly-free signals point the same way: the `created` field in each card’s YAML, and the `2026/2026-06/` folder the documents already live in. A path glob plus a frontmatter check — no query, no embedding — and the candidate set drops from the whole vault to a single month.

Then **filter by tag**. Intersect that month with the reinforcement-learning tag cluster: `reinforcement-learning`, and neighbours like `reasoning`. Because the tags were designed around the questions you ask, this is precise routing rather than a fuzzy similarity guess. Now you have this month’s RL documents, and you still haven’t opened a single one.

Next, **read the cards, not the documents**. For each candidate, read only its card: metadata, summary, key claims, and section map. Dozens of long documents collapse into a few hundred tokens of maps, and the model finally knows what it has.

Now **connect across the cards**. Compare one card’s claims and tags against the others, and cluster the advances — three threads moved this month, and here is how they relate — using nothing but the frontmatter. This is the synthesis step.

Finally, the **one deliberate read**. For the two or three documents that matter most, follow the card’s wikilink into the full document and use the section map to open only the section you need. The expensive read happens once, at the very end, after the cheap structure has already done all the narrowing.

There are many similarities here with database querying best practices: filter and be as specific as possible before performing the big retrieval.

> Run the same question through a retrieval stack instead, and you’re chunking the whole vault, tuning top-k, and hoping the reranker surfaced the right fragments — with no notion of “last month” at all, unless you engineered one in.

## What it comes down to

When you strip it back, it all comes down to a change in how the model spends its tokens. Without structure, it spends them opening files blindly, just to find out what they contain. With structure, it has them read the one section that matters, deliberately opened, after the cheap maps have narrowed.

There is no index to install, nothing to evaluate, and no tuning bill that comes due every time the content changes. You already own the folders, the frontmatter, and the file tools. This is the real advantage of structure over a retrieval stack: it is a one-time design cost that carries over to the next corpus, rather than a recurring one that does not.

This is the same long-context tax I wrote about in diminishing returns, seen from the other side:

[[**Diminishing Returns: Reducing Long-Context Failure in Agentic Settings**
*Why do language models fail when concatenating simple tasks but nail it on every individual task?*pub.towardsai.net](https://pub.towardsai.net/diminishing-returns-reducing-long-context-failure-in-agentic-settings-7368dfc86063)](https://pub.towardsai.net/diminishing-returns-reducing-long-context-failure-in-agentic-settings-7368dfc86063)

There, a context stuffed with earlier steps quietly degraded the model’s reasoning; here, it quietly drains your token budget. The fix is the same in both cases: don’t make the model hold more than it needs.

> The flat-text second brain never needed RAG. It just needed a map

> **Understanding should not be a luxury reserved for specialists.
**My goal is to make frontier AI and machine learning research accessible through clear, tutorial-style explanations.

> If this piece helped you think more clearly about the topic, showing support with **claps** or a **subscription** genuinely helps keep this work going.

> You’re always welcome to connect with me on [LinkedIn](https://www.linkedin.com/in/fabio-yanez/), where I share more writing and ideas in the same spirit.
