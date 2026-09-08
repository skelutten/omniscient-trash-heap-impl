---
title: "Is RAG Outdated?"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/is-rag-outdated-da70b4e7bf20"
published: "2026-03-13"
fetched: "2026-09-08"
reading_time_min: 6.8
tags: []
member_only: true
body_source: "medium-session"
---

# Is RAG Outdated?

### *Today’s RAG Is Not Yesterday’s RAG*

![](https://miro.medium.com/v2/0*QVlOdJgxKCzbYqHY.jpg)

## The Question

In my Knowledge Planet community, a member named momo asked a question.

He’s been using Codex and Claude Code to build a local knowledge graph powered by RAG. While working on it, he went back and reread some of my earlier articles on RAG, only to realize they were written several years ago. His question was: **Has RAG already been replaced by newer approaches? Or is it still worth pursuing — just with newer tools to build a personal local system?**

That’s a great question. I suspect many of you have a similar uncertainty — RAG hasn’t been in the spotlight much lately. But “not talked about as much” and “no longer useful” are two very different things.

## Is RAG Obsolete?

Let me give you a straight answer: **No, it’s not obsolete — but today’s RAG is not yesterday’s RAG.**

If you remember the RAG tutorials from 2023, they all looked pretty much the same: chunk your documents, convert them into vectors with an embedding model, store them in a vector database, and when a user asks a question, retrieve the most relevant chunks and feed them into the prompt for the LLM. This pipeline was simple and straightforward. The downsides were just as obvious — retrieval quality was poor, context often fell apart, and the answers frequently missed the mark entirely.

![](https://miro.medium.com/v2/0*RS-OOWZYJzG94twJ.png)

**This “beginner version” of RAG is indeed outdated.**

But the core idea behind RAG hasn’t left the stage. There are two reasons it feels like RAG isn’t talked about as much anymore.

**First, long-context models have absorbed some of the scenarios that used to belong to RAG.** Today’s models routinely support context windows of hundreds of thousands of tokens. If your knowledge base isn’t that large — say, a few hundred pages of lecture notes, or a mid-sized document collection — just feeding everything into the prompt might be the easiest solution, no retrieval needed at all. For these use cases, there’s genuinely no need to bother with RAG.

We recently published a paper titled *An Empirical Study on Long-Document Processing Capabilities of Large Language Models*, which compares different models on exactly this front. You can [click this link to download it](https://kns.cnki.net/kcms2/article/abstract?v=esvOG1ozB-jUtoy908sYstYP_Mo4ZRCaoJv8EbO80M5CYXQEkCd55XD_hPs9lVAdZixt6o2ap7FhMcfwPOUob9DNl7CDvAX8NBSjTHjKz2A7DETrMO8e2nNTFygPn__hV6gvvn-QMvXkYFLVoJ42i3d-s-F2SDQD&uniplatform=NZKPT) (available in Chinese).

![](https://miro.medium.com/v2/0*t_OQhJjO_2QRbaUC.png)

That said, there’s a challenge worth mentioning: models advance too fast. When the paper was written, the models used in the experiments were still state-of-the-art. By the time it was officially published, most of them had already been updated by their respective companies.

**The second reason is more important: RAG hasn’t disappeared — it’s been absorbed into a larger system.** The industry term now is “context engineering.” RAG is just one component, working alongside reranking, query rewriting, memory systems, and tool calling. You don’t have a separate conversation about whether a car’s tires are good — but every car needs tires. That’s the role RAG plays now — it’s no longer in the spotlight, but no serious knowledge QA system can do without it.

![](https://miro.medium.com/v2/0*49wpSyuwZa2dS_Zz.png)

Looking at the product level makes this even clearer. OpenAI’s API still has a built-in [file search](https://platform.openai.com/docs/guides/tools-file-search) feature that does hybrid retrieval combining semantic search and keyword matching. Anthropic launched [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) in 2024, which specifically adds contextual information and reranking on top of RAG. Their official report shows that hybrid retrieval reduced retrieval failures by nearly 50%, and adding reranking on top of that cut the remaining failures by another two-thirds. These companies aren’t abandoning RAG — **they’re turning RAG from a vector database demo into an industrial-grade retrieval engineering system.**

So here’s my take: **RAG is still worth doing, but what’s worth doing today is no longer the 2023 “chunk-embed-top-k” beginner version. It’s the evolved version — hybrid retrieval, intelligent reranking, and the ability to decide on its own when to fetch information.**

## Are Knowledge Graphs Worth Building?

You mentioned my earlier article [*GraphRAG + GPT-4o mini: Building an AI Knowledge Graph at Low Cost](https://wshuyi.medium.com/graphrag-gpt-4o-mini-building-an-ai-knowledge-graph-at-low-cost-a4282440d92e)*. For readers who haven’t seen it, here’s a quick recap: GraphRAG is a project from Microsoft that layers a knowledge graph on top of standard RAG, using graph structures to represent entities and relationships across documents.

![](https://miro.medium.com/v2/0*7aXEfJOwhIhmAc_3.jpg)

The project is still actively maintained, with [new versions continuously being released on GitHub](https://github.com/microsoft/graphrag).

![](https://miro.medium.com/v2/0*tWIVaCt8z89NYWUv.png)

**Is knowledge-graph-enhanced RAG worth doing? Yes — but my advice is: don’t make it your starting point.**

GraphRAG solves a specific class of problems. When your questions go beyond what keyword matching can handle — things like “what themes have been recurring in my notes over the past two weeks,” “how has a certain concept evolved across different papers,” or “help me trace a chain of relationships across multiple documents” — these broad, cross-document questions that require connecting the dots across sources are where plain vector search falls short and graph structures can play a unique role.

But equally important: **GraphRAG is not an automatic upgrade over standard RAG.** Benchmarks have specifically compared the two, and the conclusion is that each has its strengths. On many everyday QA tasks, GraphRAG actually performs worse than standard RAG, along with higher latency. Think of the graph as a “second-layer index” — it helps you do relational reasoning, but it’s not the foundation.

**Here’s my practical recommendation: get basic hybrid retrieval right first.** Semantic search plus keyword retrieval, plus a reranking model — this combination handles the vast majority of scenarios. “Where is a certain definition in this paper?” “How does this concept get explained in these lecture notes?” “Find me the source and give me the citation.” — hybrid retrieval covers these needs.

When you’ve been using it for a while and find your needs evolving — you start caring about relationships between documents, wanting cross-document timelines and concept networks — that’s when you layer on the graph. No rush.

## How Do You Ensure Data Privacy?

You mentioned wanting to build a local system while maintaining good confidentiality. That’s entirely doable, but there’s an important distinction to think through.

**“Local execution” and “local inference” are not the same thing.**

Codex CLI can read files, modify code, and run scripts in your local directories — those operations genuinely happen on your own machine. It even supports connecting to local model providers like Ollama. So using Codex as the engineering backbone for your knowledge system works just fine.

But if the underlying inference still uses a cloud model (like GPT or Claude), what you actually end up with is **local indexing and local tooling, but cloud-based inference**. Your retrieval results, your assembled prompt — they still get sent to the cloud. That’s not true end-to-end local deployment.

![](https://miro.medium.com/v2/0*vHaYIc9KIK-tMvjr.jpg)

So how do you draw that privacy boundary? **The key is to keep sensitive data behind the retrieval layer.** Your raw documents, chunks, embeddings, full-text indexes — all of that stays local. The cloud model only sees the minimal, relevant fragments returned by retrieval. This way, even if the model is in the cloud, it only touches the few fragments relevant to the current question, not your entire knowledge base.

![](https://miro.medium.com/v2/0*KHP4ic6pOwes0_qd.jpg)

If you want to go further — keeping everything local, from indexing to inference — then switch the model provider to a local one too. Both Codex and Claude Code now support connecting to local models. The trade-off is that local models generally can’t match the cloud heavyweights in raw capability, but for knowledge-base QA tasks, they’re often good enough.

## Wrapping Up

We’ve covered three questions. RAG isn’t obsolete — only the bare-bones 2023 approach is. Today’s RAG has evolved alongside long-context models, reranking, and intelligent retrieval into a larger system. Knowledge graphs are also worth building, but don’t rush — get hybrid retrieval solid first, then add graphs when your needs call for it. As for data privacy, building a local system with Codex or Claude Code is definitely feasible — the key is to draw your privacy boundary at the data and retrieval layer. And keep in mind: locally deployed models still lag behind their cloud counterparts.

You’re already building. That already puts you ahead of most people who are still at the “thinking about it” stage. Keep going.

If you find this article useful, please click the `Clap` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Feel free to [subscribe to my Patreon](https://patreon.com/wshuyi) to access exclusive articles for paid users.

For video content, check out [my YouTube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- • [Perplexity or the Big Three? My AI Subscription List and Selection Logic](https://mp.weixin.qq.com/s/QEAcGKlA6h3kQnY3B8lz3Q)
- • [In the AI Era, Should You Ditch Your Knowledge Management Tools?](https://wshuyi.medium.com/in-the-ai-era-should-you-ditch-your-knowledge-management-tools-322843da2e4d)
- • [AI Applications Are Booming — Is Your Moat Wide Enough?](https://mp.weixin.qq.com/s/-H-Q70wBTDaN7APYnRhI6g)
- • [GraphRAG + GPT-4o mini: Building an AI Knowledge Graph at Low Cost](https://wshuyi.medium.com/graphrag-gpt-4o-mini-building-an-ai-knowledge-graph-at-low-cost-a4282440d92e)
- • [In the ChatGPT Era, My New Book *Symbiotic Intelligence* Is Out](https://mp.weixin.qq.com/s/WZuTCe2cPcOmmQuHb52Xvw)
