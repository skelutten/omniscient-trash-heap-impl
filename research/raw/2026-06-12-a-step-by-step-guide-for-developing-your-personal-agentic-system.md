---
title: "A Step-by-Step Guide for Developing Your Personal Agentic System."
author: "Erdogan T"
author_url: "https://medium.com/@erdogant"
source: "https://medium.com/data-science-collective/a-step-by-step-guide-for-developing-your-personal-agentic-system-24c6cd6fa849"
published: "2026-06-12"
fetched: "2026-09-08"
reading_time_min: 35.5
tags: ["large-language-models", "agentic-rag", "probability", "python", "data-science"]
member_only: true
body_source: "medium-session"
---

# A Step-by-Step Guide for Developing Your Personal Agentic System.

### Hands-on Tutorials

## A Step-by-Step Guide for Developing Your Personal Agentic System.

### A complete guide to learn how to set up and create your own agentic LLM system with local databases and specialized for your task.

![Your new agentic team is ready for you. (image by author)](https://miro.medium.com/v2/1*po63mpOfUFmrajkBRmDkGw.png)

The use of agentic systems is becoming the go-to when automating complex tasks. As a data scientist, you need to keep up and learn the new paradigm of automation, one in which natural language becomes the primary interface for computation. Once you have seen this new concept, you will realize that the real challenge is an engineering problem: creating reliable, structured, and reproducible systems around probabilistic models. The goal is to learn how to design agentic systems that can reduce repetitive cognitive workload and assist with human tasks more efficiently and consistently.

Throughout this blog, you will learn about the emerging concept of the LLM Operating System (LLMos), in which the language model serves as the central reasoning engine, orchestrating tools, memory, retrieval, and multiple specialized agents. Then you will dive into the real, practical designs to build trustworthy agentic pipelines. *By the end, you will have built your own lightweight multi‑agent system using the Python library LLMlight that runs locally and privately, using structured prompts, retrieval‑augmented generation, embedding‑based search, and specialized agents that collaborate to solve complex tasks.*

*If you found this article helpful, you are welcome to [follow me](http://erdogant.medium.com/) because I write more about data science! I recommend experimenting with the hands-on examples in this blog. This will help you to learn quicker, understand better, and remember longer. Grab a coffee and have fun!*

## An Introduction Towards Agentic Systems.

I started writing a brief introduction about agentic systems, but there are so many concepts that need to be explained, so it has become a larger introduction to agentic systems. ***I highly recommend not skipping this introduction because these new concepts are fundamental for designing agentic systems.***

As a data scientist, there is great pleasure in building your own system instead of only consuming them. Nevertheless, we should always be cautious of the so-called “*not invented here syndrome.*” This describes the tendency of engineers to rebuild technology or software simply because it provides a complete understanding of how everything works from start to finish. While this can sometimes lead to unnecessary reinvention, it is also an important step when learning new technologies, especially in emerging fields such as AI agents. By experimenting and building these systems yourself, you will get a much deeper understanding of how they fundamentally operate, making it easier to see the advantages and the limitations of agentic workflows.

> By building agentic systems yourself as a learning step, you will gain deeper understanding of how such systems fundamentally operate, making it easier to see the capabilities and the limitations.

Once you move beyond the chat prompt of ChatGPT, Gemini, and Grok and start building systems around these language models, you quickly realize that the real challenge is not generating text. **The real challenge is designing workflows that can reliably solve practical problems in a structured and reproducible way. **This creates enormous opportunities for organizations and researchers alike in tasks such as summarizing documents, generating reports, extracting information, analyzing text, and reasoning over large collections of data.

> Tasks that once required carefully rule-based engineered systems can now often be handled using natural language instructions. Yet the reality is more complicated. The core challange remains similar; we need to design agentic workflows that are reliably, structured, and provide reproducible results.

Traditional deterministic systems are often very stable. Once deployed, they behave predictably unless the underlying rules are changed. Language models are different. Their outputs may vary depending on the prompt, the model version, parameter settings such as temperature, the context window, or even small wording changes. This flexibility is exactly what makes them powerful, but also what makes them difficult to control in production environments.

### **Takeaway 1: Your LLM is Not a Writer; It’s a CPU.**

We are now entering a new computing paradigm where the large language model itself becomes the computational core of the system. Many similarities can be found with classical operating systems around hardware abstractions. Modern AI systems revolve around what can be described as an ***LLM Operating System (LLMos)***: an architectural design in which the language model acts as the central reasoning engine that orchestrates multiple tasks, tools, and agents. The *LLMos *term is coined by* Andrej Karpathy [1, 2]*, and an architecture scheme is presented like this:

![LLM Operating System (LLMos)](https://miro.medium.com/v2/1*AjAIGRDG0OGfbekeb-inYg.png)

The analogy with traditional computing is surprisingly intuitive:

- **CPU → Large Language Model (LLM)**
- **Bytes → Tokens**
- **RAM → Context Window**

Instead of executing deterministic instructions on bytes, these systems now operate probabilistically on tokens. The context window functions as a temporary working memory, retrieval systems act as external memory storage, and prompts increasingly resemble software interfaces between components.

> We are entering a new computing paradigm where the large language model itself becomes the computational core of the system.

In many ways, we are now using language models like we did when designing entirely new software architectures, and this is challenging. The reason is that when we try to use language models for complex tasks, they require multiple forms of reasoning simultaneously. What we want in a single prompt is:

1. Retrieve information,
2. Reason over documents,
3. Validate structure,
4. Provide feedback,
5. Maintain consistency,
6. and finally generate a coherent final response.

Trying to solve everything in one large prompt becomes messy and unreliable.** This is exactly where AI agents enter the stage. **Instead of asking one massive model to solve an entire problem at once, agentic systems decompose the task into smaller, specialized subtasks. Multiple agents can then work together toward a shared objective, where each agent focuses on a specific responsibility. One agent may retrieve information, another evaluates quality, another structures references, while another summarizes the final output.

> Using agentic systems, we do not solve the entire puzzle at once, but decompose it into smaller, specialized subtasks where multiple separate LLMs (aka the agents) can work on.

### Takeaway 2: **You Don’t Need More Billions of Parameters; You Need a Specialized “Agentic Team”**.

The idea of building agentic systems sounds straightforward, but it introduces an entirely new set of engineering challenges:

- How do agents communicate?
- Which tasks should be deterministic and which stochastic?
- How do we manage limited context windows?
- How do we retrieve and statistically test for relevant information?
- How do we prevent hallucinations?
- How do we maintain consistent scoring and evaluations?

These questions are stressed even more when working with local, smaller models. Smaller models provide advantages in privacy, portability, and cost, but they also come with constraints: smaller context windows and reduced reasoning capabilities compared to larger cloud-based systems.

One of the most important realizations you may have when you do the hands-on part in this blog is that success rarely comes from a single clever prompt when building agentic systems. In practice, good systems are the result of carefully designed pipelines: chunking strategies, retrieval systems, embedding models, ranking mechanisms, structured prompts, scoring workflows, and specialized agents working together. This means that you also need to understand these concepts to make a real success of your (personal) project. More details about all the separate steps can also be found in this blog:

[[**Build Your Private Language Model: Local and Specialized For Your Tasks.**
*A complete step-by-step guide from setup to deployment of local language models, making it private, portable, and…*medium.com](https://medium.com/data-science-collective/build-your-private-language-model-local-and-specialized-for-your-tasks-f94a3f611869)](https://medium.com/data-science-collective/build-your-private-language-model-local-and-specialized-for-your-tasks-f94a3f611869)

*Here, we will take a practical engineering approach to building an agentic system. We will walk through a real-world multi-agent architecture where we will set up multiple agents discussing and working together. Along the way, we will cover:*

- Retrieval-Augmented Generation (RAG),
- Chunking and embeddings,
- Local versus global reasoning,
- Scoring workflows,
- Instructions,
- and the practical limitations of using local language models.

## The Real-World Problem: Human vs. Machine.

Many real-world problems appear straightforward until you try to automate them with large language models. You may also have experienced that in your own line of work. The most common task to automate is the evaluation of documents. At first glance, the workflow seems simple: **1. Upload a document, 2. Ask a question, and 3. You wait and let the model generate an answer. **However, in practice, these tasks are rarely isolated or deterministic because you likely have to ask multiple questions, provide more context, stop the model from hallucinating, and perform fact checks. The bad part, before you get a satisfying result, you run out of your free tokens.

> The Monolithic Prompt is a Trap.

Even a single document can require multiple forms of reasoning. The complexity grows rapidly when documents become larger and more interconnected. Furthermore, there are large differences in reports, legal documents, scientific papers, technical specifications, policy documents, and research proposals. Relevant details are differently organized across these documents, terminology is inconsistent, and important conclusions may depend on relationships between multiple parts of the text.

As humans, we use our domain knowledge and expertise to navigate through the documents. We are aware of the company rules and can solve tasks naturally by continuously switching between local and global reasoning. As an example, we zoom into specific details when necessary, while still maintaining an overall understanding of the document as a whole. Language models, however, do not inherently reason this way. They process text through a limited context window and generate outputs probabilistically, token by token. The “*monolithic*” approach, or in other words, processing an entire objective into one pass, is a recipe for architectural pain. Such “*one-shot*” approaches suffer from various limitations. *Let's jump to the next section, where we will go into more depth on why single prompts fail on complex tasks.*

## Why Single Prompts Fail and Agentic Systems Work.

When you have access to a large language model chat interface, it is tempting to solve problems in the simplest possible way: feed an entire document into a LLM and ask it to evaluate the content in one go. This monolithic approach has four core limitations when solving large, complex tasks. Let me break it down:

- **Context Window Saturation:** Even when models support massive context windows (like 200K tokens), a large document combined with dense system instructions, criteria, and strict output formatting schemas can easily push a model to its practical limits. As a result, critical segments of the document may be implicitly compressed or ignored, leading to incomplete reasoning. In the figure below you can see that the context window is the total collection of all information. In terms of the LLMos <-> PC analogy, this is the amount of RAM you have. If you push it beyond its limits, it will break and return an error.

![The total context window. Image by author.](https://miro.medium.com/v2/0*UWLrvCTfue0DNDTH.png)

- **Task Entanglement:** A single prompt forces a model to simultaneously execute fundamentally different cognitive operations: extract relevant data, interpret context, apply nuanced rules, maintain cross-sectional consistency, and generate structured feedback. Without an explicit mechanism to separate these concerns, the model often produces shallow or self-contradictory outputs.
- **Prompt Instability:** Single-pass architectures are highly sensitive to minor structural variances. Small changes in wording can significantly alter the output scores and feedback quality, even when evaluating the same underlying document.
- **Lack of Structure:** A single prompt produces a single output. No checkpoints. No reasoning steps. This makes the system incredibly difficult to debug, validate, or audit. If the final answer is incorrect, there is no clear way to trace where the reasoning chain fractured. Or in other words, making a transparent and thus trustworthy system is very difficult in such a manner.

> Complex tasks require iteration and verification. One-shot prompting removes the structure that makes judgment reliable, leaving LLM outputs brittle and inconsistent in high-impact settings.

In general, there is a mismatch between the evaluation of complex tasks and using a one-shot approach. Reasoning is that complex tasks are usually iterative by design; they require reading, cross-referencing, verifying, and refining judgments. When we push all these steps into a single transformation, it removes the structure that we as human evaluators naturally rely on. Although LLMs have made tremendous improvements in the last few years, we can not blindly trust the output of LLMs when it comes to high-impact tasks because solutions tend to be brittle, opaque, difficult to scale, and inconsistent. ***The solution? Create a large modular system out of simpler parts by using Small Local Language Models for Specialized Tasks. See next section.***

## What Is an Agent Architecture?

In practice, most agentic systems are structured pipelines where multiple (specialized) LLM models have a specific task and collaborate toward a shared objective. Simply put, when you use one large language model, you call it a model, but when you use multiple LLM models in a joint goal, you can talk about an agentic system. A misconception around LLM agents is that they are fundamentally intelligent entities on their own. They are basically a single (small and/or local) LLM model with specific instructions and a predefined task.

> **Small Local Models are Winning in a Team.**

The idea of agentic systems is that, instead of forcing a single prompt to solve everything at once, the problem is chopped into smaller subtasks, and each agent is given a predefined responsibility and is allowed to operate only within a constrained context. This improves controllability, interpretability, and modularity. The architecture of agent systems contains several types of agents. The most common agents are described as A1 to A6, as shown in the Figure below. However, you can design many more roles if you need them.

![Each agent has a specialized task. Together they form a system to solve the more complex task. Image by author.](https://miro.medium.com/v2/1*sSshxnyygk4dKFMThutA4w.png)

- **A1: Retrieval agent: **To identify relevant sections of a document.
- **A2: Reasoning agent:** To analyze the retrieved context.
- **A3: Summary agent:** To summarize the retrieved context.
- **A4: Evaluation agent:** To validate completeness or quality.
- **A5: Scoring agent:** To assign confidence or ranking.
- **A6: Orchestration agent:** To aggregate the final response and determine whether the task is done or needs another round of thinking.

This decomposition of different tasks for specialized agents introduces several advantages. **First**, it reduces cognitive overload for the model. Smaller tasks generally produce more stable and reliable outputs than large multi-objective prompts. **Second**, it creates intermediate checkpoints. Since each stage produces structured outputs, failures become easier to debug and validate. **Third**, it improves scalability. Individual agents can be replaced, upgraded, or optimized independently without redesigning the entire system. **Fourth**, it enables hybrid reasoning strategies. Some agents may operate deterministically using retrieval or rule-based logic, while others may perform stochastic reasoning using LLMs. This distinction becomes extremely important in production systems where consistency matters.

> In many ways, agentic architectures resemble classical distributed systems.

Instead of a single monolithic process performing all operations, specialized components communicate and coordinate through structured interfaces. This makes the resemblances with distributed systems. However, the difference is that the computational core is no longer a deterministic CPU pipeline, but a probabilistic reasoning engine centered around language models. **This architectural shift is one of the defining characteristics of the emerging LLM Operating System (LLMos) paradigm. ***Before we go into the hands-on examples, I will first briefly explain the concepts of RAG, chunking, embedding, searching, ranking, and finally generation.*

![The Large Language Model Operating System (LLMos). Agents with specialized tasks are depicted for demonstration purposes. Image by author.](https://miro.medium.com/v2/1*LNaHkDATyY7liyjZCsFv6g.png)

## Retrieval-Augmented Generation (RAG) Pipeline.

One of the core limitations of large language models is that they do not inherently “know” which parts of a large document are relevant to a specific question. Feeding entire books, reports, or databases directly into a model is often inefficient, expensive, and unreliable due to the limited context window.

Retrieval-Augmented Generation (RAG) fixes this problem by introducing an external retrieval layer before generation. Instead of sending the full document to the model, the system first searches for the most relevant text fragments and only provides those fragments as contextual input to the LLM.

An intuitive way to think about RAG is through the analogy of human memory. Imagine your brain was split into thousands of tiny, searchable memory fragments. When you ask yourself, ***“Where are my keys?”*,** **you do not replay your entire life story.** Instead, you subconsciously retrieve only the memories that seem relevant: arriving home, putting something on the kitchen table, grabbing your jacket, and so on. RAG works similarly. Large documents are divided into many smaller pieces called ***chunks***. When a question is asked, the system searches through those chunks and retrieves only the most relevant ones. These top-ranked fragments are then inserted into the model’s limited context window, which acts as temporary working memory. From there, the language model is very good at weaving those fragments into a coherent answer — even though it only sees part of the complete information.

### The challenges of RAG systems

RAG also introduces a critical dependency: retrieval quality. If an important chunk is not retrieved, the model may fill the missing gap with a plausible-sounding answer rather than the correct one. In other words, the generation quality is fundamentally constrained by the retrieval pipeline. In many modern agentic systems, RAG acts as the *external memory layer* of the architecture. The context window becomes temporary working memory, while the vector database functions as persistent semantic storage. Together, they form one of the foundational building blocks of practical LLM Operating Systems.

### Four steps are required in the RAG pipeline

A typical RAG pipeline consists of several stages for which the most simplest form is referred to as **“Simple RAG”** or **“Naive RAG”** (see Figure below). This baseline approach can be optimized at four major stages: **chunking**, **searching**, **embedding**, and **scoring**. Together, these form a more advanced and customizable RAG pipeline. See [here ](https://levelup.gitconnected.com/testing-18-rag-techniques-to-find-the-best-094d166af27f)for more details about different types of RAG strategies.

![Simple RAG Architecture with the strategies that can be optimized. Image by author.](https://miro.medium.com/v2/1*W0qK0DVZyARHmpFtuAU-UQ.png)

- **Chunking Strategy**: Defines how source documents are split into smaller, coherent segments. Better chunking ensures that each piece contains enough context to be meaningful while avoiding redundancy or fragmentation. This step directly impacts retrieval relevance and efficiency. [Here ](https://ai.gopubby.com/21-chunking-strategies-for-rag-f28e4382d399)is an interesting blog about chunking strategies, but overall, chunking can be in terms of words, sentences, paragraphs, tokens, or semantic sections.
- **Embedding Strategy**: Each chunk is transformed into a numerical representation called an embedding. Embedding models convert text into high-dimensional vectors such that semantically similar text fragments become mathematically close to one another. This allows the system to search documents based on meaning rather than exact keyword matches. Options include TF-IDF, Word2Vec, Sentence-BERT, or modern OpenAI embeddings. The embedding choice shapes the semantic quality of retrieval, as it dictates how similarity is measured. Read [here a blog](https://medium.com/data-science/text-embeddings-comprehensive-guide-afd97fce8fb5) with more detailed information.
- **Search/Retrieval Strategy**: When a user submits a query, the query itself is also embedded into the vector space. The system then computes similarity scores between the query embedding and all document chunks. One way to do this is by using brute-force nearest neighbor search. However, there are also smarter approaches, such as FAISS approximate nearest neighbor (ANN), or memory-efficient approaches like MemVid. The strategy also depends on dataset size, latency requirements, and hardware constraints.
- **Scoring Strategy**: Chunks with the highest similarity scores are assumed to be most relevant to the question. The scoring strategy assigns relevance scores to candidate chunks to determine which should influence the final answer. Cosine similarity is the most common.

### Ranking and Aggregation of the Chunks

After retrieval, the top-k most relevant chunks are selected and aggregated into a new context window. This step is more important than it initially appears. Simply retrieving relevant chunks is not always sufficient. Retrieved chunks may overlap, contain redundant information, or miss important supporting context. Additional ranking strategies are therefore often used, such as the re-ranking models, metadata filtering, hybrid retrieval, or the heuristic aggregation of methods.

### The Final Step is Generation.

The final step is the generation of the answer based on the **selected context + instructions + prompts**. At this stage, the LLM no longer needs to reason over the entire document. Instead, it focuses only on the most relevant information retrieved earlier in the pipeline. This approach thus improves efficiency, context utilization, response quality, and scalability for long-document analysis.

### Tasks That Work Remarkably Well Using This Pipeline.

Such an approach works very well for lookup questions (as listed below) because multiple chunks can easily be detected using the scoring and ranking approach, and then the answer is generated using the highly relevant chunks in the context.

- *“Does the document contain model comparison?”*
- *“Is a methodology section present?”*
- *“Which datasets are used?”*

However, some questions require understanding the document as a whole rather than locating a specific sentence or paragraph. Consider questions such as:

- *“Is the advice well thought out?”*
- *“Is the argumentation coherent?”*
- *“Is the methodology logically to follow?”*

I hope that this section clarifies that a major limitation is that such an approach optimizes for **local relevance** and not **global relevance**.* Let's jump to the next section to learn more about global reasoning.*

## Global Reasoning Workflow

In many modern agentic systems, RAG acts thus as the external memory layer of the architecture. The context window becomes temporary working memory, while the vector database functions as persistent semantic storage. Together, they form one of the foundational building blocks of practical LLM Operating Systems. The retrieval system searches for chunks that are most similar to the query and forwards only those fragments to the language model. To address the limitations of “zooming in” and “zooming out” of the document, many practical systems introduce an additional reasoning layer before final generation. This is a multi-step global reasoning strategy.

![Multi-step reasoning approach. First, the chunks of interest are retrieved, analyzed, and summaries together with observations are generated. Then, the results are merged and aggregated. Then the prompt can be optimized, and the final step is for the LLM to use the optimized prompt, along with the aggregated summaries, to reason and generate the final response. (image by author)](https://miro.medium.com/v2/1*YoDWiuw1r4JBs2zkuHMZRg.png)

### The Two-Step Global Reasoning Strategy

Global reasoning workflows are closely related to hierarchical reasoning systems because, at **the lowest level,** *chunks contain local information. ***At intermediate levels, ***summaries capture section-level meaning.* **At higher levels:** *aggregated summaries represent the document globally.*

Instead of directly answering the question from retrieved chunks, the system first creates an intermediate global representation of the document. A simplified workflow looks like this:

1. Split the document into chunks.
2. Analyze each chunk independently.
3. Generate local summaries or observations.
4. Aggregate these intermediate summaries.
5. Construct a global representation of the document.
6. Answer the original question using the aggregated context.

This transforms the workflow from: `***Retrieve → Generate` ***into: `***Analyze → Summarize → Aggregate → Reason → Generate`***

The difference may appear subtle, but architecturally it is extremely important. This means that the model is no longer forced to compress all reasoning into one generation step. Instead, the system gradually builds higher-level abstractions over the document. A global reasoning approach mirrors how we read long documents. We rarely memorize every sentence individually. Instead, we continuously compress information into higher-level mental representations while reading. Such an approach thus introduces a form of *iterative memory compression* for language models. *There is another important step that can be taken, and that is the rewriting of the prompt (see next section).*

### Query Rewriting

Another important component of global reasoning is query rewriting. Highly specific user questions are often difficult to use directly during chunk summarization because they bias the model toward local retrieval behavior. Instead, the system may first reformulate the query into a broader analytical objective.

For example:

- **Original query: ***“Is the proposal well thought out?”*
- **Rewritten reasoning objective: ***“Analyze the coherence, structure, feasibility, and consistency of the document.”*

This broader reasoning instruction allows the chunk-level analyses to focus on extracting higher-level signals rather than searching for explicit keywords.

### Local and Global Reasoning Together

In practice, it is best to combine the local and global strategies.

- Local retrieval pipelines for deterministic questions,
- And global reasoning workflows for abstract or holistic evaluations.

**This hybrid approach is one of the key architectural patterns emerging in modern agentic systems.** Different reasoning strategies are applied depending on the nature of the task, rather than forcing all questions through a single pipeline. In many ways, this represents a shift from prompt engineering toward reasoning engineering: designing workflows that allow language models to operate on information at multiple levels of abstraction.

## Small Language Models Are Winning.

One of the most important shifts this year in the field of LLMs is the movement away from single monolithic dense language models toward *agentic AI systems* that are composed of multiple specialized agents.

NVIDIA Research has argued that “*Small Language Models are the future of Agentic AI,*” while Microsoft introduced highly efficient 1-bit LLMs that drastically reduce memory requirements and make local deployment increasingly feasible. At the same time, **sparse model architectures **have emerged in which only a subset of parameters is activated during inference, reducing computational overhead while maintaining strong performance. You can see this difference in the type of models that are created, as an example, **Gemma 4-26B-a4B**, which means that this model has roughly **26 billion total parameters,** but importantly, that it has approximately **4 billion parameters that are active during inference. **This is not a normal dense model anymore but it is a Mixture-of-Experts (MoE) architecture. All these developments are really great because, in combination with **Agentic AI**, we do not need to rely on a single model but can create multiple models, each specialized for a specific task that jointly solve the task. ***In the next section, we will set up the tools we need and then design our own agentic system in the hands-on part.***

## Set Up Your Own Local Model Using LM Studio.

Before we can start experimenting with LLMs and agentic systems, we need to set up our own local model. One of the most used software at this point is [LMstudio](https://lmstudio.ai/). It is free, there is a user interface, and it connects surprisingly well with the hardware in your machine. Above all, popular models can easily be downloaded and directly used. The installation is a regular installation file. Besides LMstudio, there are also various other good alternatives, such as [Ollama](https://ollama.com/) or [Claude](https://claude.ai/download). Either way, if tools have an endpoint, you can use them to work with the language models in your local Python environment.

![LM studio: https://lmstudio.ai/](https://miro.medium.com/v2/1*hVQSQTSUTtKQHC7-5eLb6Q.png)

> Download and install the software.

> Go to the developer window (Steps 1 and 2) and enable “start running” (Step 3). This will make the models accessible via the localhost (Step 4): `[https://127.0.0.1:1234`](https://127.0.0.1:1234.)

![LM studio screenshot to start running (image by author).](https://miro.medium.com/v2/0*HExNqqOQ86FUnDst.png)

When you have downloaded your favorite models and enabled the “start running”, you can also experiment in the Chat section to see what the speed of response time is. *In the next section, we will create our first model in Python.*

## The LLMlight Library.

The LLMlight library is an easy-to-use and lightweight Python package for running Language Models locally with minimal dependencies. It is an **agentic pipeline** with various stages from handling the input prompt to the output of the model. A schematic overview of LLMlight is depicted in the figure below. In general, there are six key steps in the pipeline: first, the `chunking `of text, then `search strategy`, `embedding strategy`and `scoring strategy`, `context strategy`, and finally the `prompting strategy` . The parameters, like t**emperature and** **top-p sampling,** can be adjusted so that you keep control over the response variation.

![A schematic overview of the LLMlight library. Image by Author.](https://miro.medium.com/v2/0*G-Ha7S9COzADlj8z.png)

### Chunking Strategy

The **LLMlight** library utilizes a modular and configurable **Chunking Strategy** designed to split large documents into smaller, coherent segments, ensuring each piece contains sufficient context for effective embedding and retrieval. Chunking is the first step in the LLMlight workflow. Its primary goal is to ensure that retrieval is both relevant and efficient by avoiding the “dilution” of information that occurs when models try to process long documents through limited context windows. By breaking text into segments, the system can pinpoint the most significant fragments for a specific query rather than struggling with a massive monolithic document. The chunking process is highly customizable via the `chunks` parameter.

- **Methods:** Chunks can be created based on **characters** or **words**. General RAG strategies supported by the library can also consider sentences, paragraphs, tokens, or semantic sections.
- **Default Configuration:** The default setting for the library is `{‘method’: ‘chars’, ‘size’: 1000, ‘overlap’: 200}`.
- **Size:** This default creates a segment every 1000 characters.
- **Overlap:** A 200-character overlap is maintained between adjacent chunks to prevent the fragmentation of knowledge and help the model make sense of the context at the boundaries of each piece.

It is strongly recommended to never chunk too small (specifically **avoiding segments < 200 characters**) to prevent “hallucinations,” as tiny fragments often lack the complete information required for accurate reasoning. **2.** Before chunking, try to clean your raw documents by removing headers, footers, and boilerplate text, which reduces noise and improves model performance.

### Search Strategy — Local Databases.

The search strategy specifies how candidate chunks are searched in the (vector) database. LLMlight intends to keep it lightweight and easy to use. This also accounts for the storage of information in databases. Vector databases are great and fast, but also require (complex) installation procedures. LLMLight, therefore, incorporates **SQLite + HNSW. **The default backend uses a local SQLite database with an optional HNSW index for **fast approximate nearest-neighbor search**, ensuring that retrieval remains performant even as your data grows

### Embedding & Scoring Strategies

The embedding strategies determine how chunks and queries are represented in the vector space. The available embedding methods in LLMlight are:

- **TF-IDF:** Best for structured documents with matching query terms
- **Bag of Words: **Simple word frequency approach
- **BERT: **Advanced contextual embeddings for free-form text
- **BGE-small: **Efficient embedding model for general use

The scoring strategy assigns relevance scores to candidate chunks so that the top chunks can be returned. **Cosine similarity** is the default.

### Context Strategies

The context strategy in LLMlight contains two agents that work together to create a single comprehensive text based on all input chunks. The **chunk-analyzer-agent** has specific instructions to analyze each chunk and its relation to the other chunks. The **smart-context-agent **then uses the processed chunks and summarizes it with specific instructions into one coherent text. The reason for such an extensive approach is that the detected chunks can be gathered from various documents/sources. The LLMlight library contains three **context strategies**, `No processing`, `chunk-wise` and `global-reasoning`. In exercise 5, we will go through each of the strategies and evaluate the results.

- **None: **No preprocessing. The raw and entire context text is used
- **chunk-wise**: Breaks the context into manageable chunks.
- **global-reasoning:** Creates a global summary of the context

### Prompt Optimization

The final prompt is a combination of various parts that are either provided by the user or are created by the agents.

- **System message:** Defines the AI’s role and behavior
- **Context:** Processed and retrieved relevant information
- **User query:** The specific question or request
- **Instructions:** Additional guidance for response generation

## Exercise 1: Load A Single Model and Have A Simple Chat.

In this first exercise, we will use the endpoint of LM studio to connect with the available models, and then ask some basic questions to the model. In my case, the default endpoint is `[http://localhost:1234`](http://localhost:1234) which can be used for various tasks (see figure below for the supported endpoints). We now need to use the chat completions, which is also the default within `LLMlight`. I have several models in my LMstudio environment, which means that I can easily decide which model to use for specific tasks. *Note that when you run the model for the first time, the model needs to be loaded into memory, which can take some time.*

```bash
# Install the library
pip install llmlight
```

```python
from LLMlight import LLMlight

# Initialize the LLMlight client
client = LLMlight(model='google/gemma-4-26b-a4b-qat', endpoint="http://localhost:1234/v1/chat/completions")

# Ask a question
response = client.prompt('What is the capital of France?')
print(response)

# [LLMlight.LLM] [INFO    ] Model            : google/gemma-4-26b-a4b-qat
# [LLMlight.LLM] [INFO    ] Context strategy : disabled
# [LLMlight.LLM] [INFO    ] Retrieval method : naive_rag
# [LLMlight.LLM] [INFO    ] Embedding        : {'memory': 'bert', 'context': 'bert'}
# [LLMlight.LLM] [INFO    ] Alpha (sig. test): None
# [LLMlight.LLM] [INFO    ] Chunk config     : {'method': 'chars', 'size': 1000, 'overlap': 200}
# [LLMlight.LLM] [INFO    ] LLMlight initialised.
# [LLMlight.LLM] [INFO    ] Creating response with google/gemma-4-26b-a4b-qat..
# [LLMlight.LLM] [INFO    ] No context strategy applied.
# [LLMlight.LLM] [INFO    ] No context is provided into the prompt.
# [LLMlight.LLM] [INFO    ] Running model: google/gemma-4-26b-a4b-qat 

# The capital of France is Paris.
```

## Exercise 2: Create a Local Knowledge Base.

A local knowledge base is the critical first step in building a private agentic system, as it functions as the database for reasoning with your local verified facts. With the LLMlight library, we can easily ingest raw data, including PDFs, text files, or even entire directories, by employing the `memory_add` function, which automatically handles the preprocessing and chunking required for effective retrieval. For storage, the default is set to the standard **SQLite database** (optimized with an **HNSW index** for high-speed searching) or the highly portable **MemVid** backend. MemVid is particularly innovative, as it compresses millions of text embeddings into a **single MP4 video file**, making your entire knowledge base offline-friendly and easy to transfer between edge devices or different machines without complex database installations. Once you save your data to disk with`memory_save()`, you can create your own personal research assistant, thereby ensuring your sensitive information remains private.

```python
# Import library
from LLMlight import LLMlight

# Initialize model and memory
client = LLMlight(model='google/gemma-4-26b-a4b-qat', endpoint="http://localhost:1234/v1/chat/completions")
# Create (or load) database
client.memory_init(store_path='knowledge_base.db')

# Add a PDF file to the database (extracts and chunks text automatically)
url = 'https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf'
pdf_text = client.read_pdf(url)

# Write to db
client.memory_add(text=pdf_text)

# Show the chunks
client.memory_chunks(1)

# Store to disk (SQLite DB is persisted automatically)
client.memory_save()

# Query on the new knowledge
response = client.prompt(query='What are attention networks?', response_format='Summarize in 3 sentences.')
print(response)

```

## Exercise 3: The Differences in Output Using Context Strategy Methods.

The LLMlight library has three distinct context strategies to optimize how retrieved information is presented to the language model: **None**, **chunk-wise**, and **global-reasoning**.

The **None** (or “No Processing”) strategy is the most naive approach, where the raw and entire retrieved context is used as-is, with top candidate chunks simply combined into a single block for the prompt. See code block and results below:

```python
from LLMlight import LLMlight

# Initialize with NO context strategy
client = LLMlight(model='google/gemma-4-26b-a4b-qat', retrieval_method='naive_rag', context_strategy=None, top_chunks=6, endpoint="http://localhost:1234/v1/chat/completions")

# Create (or load) database
client.memory_init(store_path='knowledge_base.db')

# Query on the new knowledge
response = client.prompt(query='What are attention networks?', response_format='Summarize in 2 sentence')

print(response)
# Based on the provided text, attention networks utilize mechanisms like self-attention 
# to perform tasks such as reading comprehension, summarization, and machine translation 
# by capturing the syntactic and semantic structures of sentences. 
# They operate by computing attention weights on "values" using "queries" and "keys" through 
# a softmax function, with common types being additive or dot-product multiplicative attention.

```

In contrast, the **chunk-wise** strategy breaks the context into manageable segments and applies a specific transformation to each top chunk, ensuring a coherent analysis before the information is sent to the model.

```python
from LLMlight import LLMlight

# Initialize with CHUNK-WISE context strategy
client = LLMlight(model='google/gemma-4-26b-a4b-qat', retrieval_method='naive_rag', context_strategy='chunk-wise', top_chunks=6, endpoint="http://localhost:1234/v1/chat/completions")

# Create (or load) database
client.memory_init(store_path='knowledge_base.db')

# Query on the new knowledge
response = client.prompt(query='What are attention networks?', response_format='Summarize in 2 sentence')

# [LLMlight.LLM] [INFO    ] Chunk wise analysis on 6 chunks of text.
# Processing chunk:   0%|          | 0/6 [00:00<?, ?chunk/s][08-06-2026 22:11:53] [LLMlight.LLM] [INFO    ] Working on text chunk 1/6
# Processing chunk:  17%|█▋        | 1/6 [00:54<04:31, 54.24s/chunk][08-06-2026 22:12:47] [LLMlight.LLM] [INFO    ] Working on text chunk 2/6
# Processing chunk:  33%|███▎      | 2/6 [01:18<02:26, 36.66s/chunk][08-06-2026 22:13:12] [LLMlight.LLM] [INFO    ] Working on text chunk 3/6
# Processing chunk:  50%|█████     | 3/6 [01:30<01:15, 25.33s/chunk][08-06-2026 22:13:23] [LLMlight.LLM] [INFO    ] Working on text chunk 4/6
# Processing chunk:  67%|██████▋   | 4/6 [01:51<00:47, 23.81s/chunk][08-06-2026 22:13:45] [LLMlight.LLM] [INFO    ] Working on text chunk 5/6
# Processing chunk:  83%|████████▎ | 5/6 [02:47<00:35, 35.13s/chunk][08-06-2026 22:14:40] [LLMlight.LLM] [INFO    ] Working on text chunk 6/6
# Processing chunk: 100%|██████████| 6/6 [03:14<00:00, 32.48s/chunk]
# [LLMlight.LLM] [INFO    ] Running model: google/gemma-4-26b-a4b-qat 

print(response)
# The provided context does not contain a formal definition of "attention networks." 
# It only describes the mathematical mechanism of attention, which uses queries, keys, and values to 
# compute output weights through methods like scaled dot-product or additive attention.

```

Finally, the **global-reasoning** strategy employs a sophisticated hierarchical approach that analyzes, summarizes, and aggregates chunks to create a global representation of the document. While the chunk-wise method tends to be more strict and focuses on local relevance, global reasoning is specifically designed for abstract or holistic evaluations — such as determining if an overall methodology is logical — by building higher-level abstractions that mirror how humans read and compress long documents.

```python
from LLMlight import LLMlight

# Initialize with GLOBAL-REASONING context strategy
client = LLMlight(model='google/gemma-4-26b-a4b-qat', retrieval_method='naive_rag', context_strategy='global-reasoning', top_chunks=6)

# Create (or load) database
client.memory_init(store_path='knowledge_base.db')

# Query on the new knowledge
response = client.prompt(query='What are attention networks?', response_format='Summarize in 2 sentence')

# [LLMlight.LLM] [INFO    ] Global-reasoning on 6 chunks of text.
# Processing chunk: 100%|██████████| 6/6 [03:14<00:00, 32.48s/chunk]
# [LLMlight.LLM] [INFO    ] Running model: google/gemma-4-26b-a4b-qat 

print(response)
# Based on the provided text, attention networks are computational mechanisms that use queries, keys, 
# and values to determine weights via a scaled dot-product and a softmax function. 
# These networks can enhance model interpretability and, when combined with feed-forward layers, achieve a computational 
# complexity similar to separable convolutions.

```

## Exercise 4: Create A Discussion Between Two Agents On A Theme of Interest.

One of the most interesting applications is creating autonomous discussions between multiple AI agents. In this example, you will learn to set up two different agents, each with its own knowledge base, retrieval settings, and personality. During the conversation, every agent uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from its memory before generating a response. This allows the agents to reason from different perspectives, challenge each other’s assumptions, and build upon previously exchanged ideas. By assigning distinct expertise domains. such as a Data Scientist, and a Farmer, you can simulate debates, brainstorming sessions, or expert panel discussions. *See the code block below to combine memory, retrieval, and language generation to create dynamic multi-agent workflows that go far beyond simple question-answer interactions.*

![Discussion between two agents on a topic of interest (image by author).](https://miro.medium.com/v2/1*c9Ycahx-6fXieXOXIuRbpw.png)

```python
# Initialize
from LLMlight import LLMlight

# temperature=0.1               Lower means a More factual debate
# temperature=1.0               Higher means more creative discussion
# top_chunks=10                 Use more retrieved context
# embedding='bert'              Strong semantic retrieval
# retrieval_method='naive_rag'  Standard RAG retrieval

# ====================================================
# Agent A: Data Scientist
# ====================================================
agent_a = LLMlight(
    model="google/gemma-4-26b-a4b-qat",
    retrieval_method="naive_rag",
    embedding="bert",
    context_strategy=None,
    top_chunks=5,
    temperature=0.7,
)

# Set the database for Agent 1
agent_a.memory_init(store_path="agent_a.db")

# Add some background information database for agent 1
agent_a.memory_add("""
Large Language Models are one of the most important step we did in the field of AI
It helps the workload and the work easier and faster.
""")

agent_a.memory_add("""
Large Language Models use transformer architectures and are trained on
massive text corpora using self-supervised learning.
""")


# ====================================================
# Agent B: Farmer
# ====================================================
agent_b = LLMlight(
    model="google/gemma-4-26b-a4b-qat",
    retrieval_method="naive_rag",
    embedding="bert",
    context_strategy=None,
    top_chunks=5,
    temperature=0.7,
)

# Set the database for Agent 2
agent_b.memory_init(store_path="agent_b.db")

# Add some background information database for agent 2
agent_b.memory_add("""
The use of AI and machine learning consumes to much power and there is no need for this
new technology. The human work was good enough and there is no need to change that.
""")

agent_b.memory_add("""
Recent research shows that LLMs hallucinate and do not solve real world applications.
""")


# ====================================================
# Discussion Loop
# ====================================================

topic = "Discuss the importance of the use of Large Language Models and AI."
message = topic

for turn in range(5):

    print(f"\n{'='*80}")
    print(f"ROUND {turn+1}")
    print(f"{'='*80}")

    response_a = agent_a.prompt(
        system='You are a Data Scientist.',
        query=
        f"""
        Topic:
        {message}
        """,
        response_format='Give your opinion in 1-2 paragraphs and ask a question to the other agent.',
    )

    print("\nAgent A:")
    print(response_a)

    response_b = agent_b.prompt(
        system='You are a farmer.',
        f"""
        The Data Scientist said:

        {response_a}
        """,
        response_format='Respond to the discussion in 1-2 paragraphs and ask a follow-up question.',
    )

    print("\nAgent B:")
    print(response_b)

    message = response_b
```

## Introducing The Third Agent: The Moderator

While two agents can engage in rich and insightful discussions as shown above, they can become trapped in repetitive arguments, focus excessively on disagreements, or drift away from the original objective. Introducing a third agent acting as a moderator or mediator can significantly improve the quality of the conversation. Rather than contributing new domain knowledge, the moderator observes the dialogue, identifies areas of agreement and disagreement, and periodically summarizes the key points raised by both sides. The moderator can also steer the discussion toward unresolved questions, request clarification when arguments become vague, and encourage the agents to converge on a shared conclusion. This mirrors the role of a facilitator in human discussions and helps transform a debate into a collaborative problem-solving exercise. In LLMlight, the moderator can leverage its own memory and retrieval pipeline to maintain an objective overview of the conversation, making multi-agent systems more effective, coherent, and goal-oriented. See the code block on how to add the moderator agent:

![Discussion between two agents on any topic of interest, but controlled by the moderator agent. (image by author).](https://miro.medium.com/v2/1*FOrKLdd7cMJ0jIQdpfNCWA.png)

```python
from LLMlight import LLMlight

# ====================================================
# Agent A: Data Scientist
# ====================================================
agent_a = LLMlight(
    model="google/gemma-4-26b-a4b-qat",
    retrieval_method="naive_rag",
    context_strategy=None,
    top_chunks=5,
    temperature=0.7,
)

agent_a.memory_init(store_path="agent_a.db")

agent_a.memory_add("""
Large Language Models are one of the most important step we did in the field of AI
It helps the workload and the work easier and faster.
Large Language Models use transformer architectures and are trained on
massive text corpora using self-supervised learning.
""")

# ====================================================
# Agent B: Farmer
# ====================================================
agent_b = LLMlight(
    model="google/gemma-4-26b-a4b-qat",
    retrieval_method="naive_rag",
    context_strategy=None,
    top_chunks=5,
    temperature=0.7,
)

agent_b.memory_init(store_path="agent_b.db")

agent_b.memory_add("""
The use of AI and machine learning consumes to much power and there is no need for this
new technology. The human work was good enough and there is no need to change that.
Recent research shows that LLMs hallucinate and do not solve real world applications.
""")


# ====================================================
# Agent C: Moderator
# ====================================================
moderator = LLMlight(
    model="openai/gpt-oss-20b",
    retrieval_method="naive_rag",
    context_strategy=None,
    top_chunks=5,
    temperature=0.3,  # lower temperature for objective summaries
)

moderator.memory_init(store_path="moderator.db")


# ====================================================
# Shared discussion memory
# ====================================================
shared_memory = LLMlight(model="openai/gpt-oss-20b")
shared_memory.memory_init(store_path="discussion.db")

# ====================================================
# Discussion Loop
# ====================================================
topic = "Discuss the importance of the use of Large Language Models and AI."
message = topic

for turn in range(5):

    print(f"\n{'='*80}")
    print(f"ROUND {turn+1}")
    print(f"{'='*80}")

    # --------------------------------------------
    # Agent A responds
    # --------------------------------------------
    response_a = agent_a.prompt(
        system='You are a Data Scientist.',
        query=
        f"""        

        Current discussion:
        {message}

        """,
        instructions='Provide your opinion and ask a question to the Farmer.',
        response_format='Response can be maximum 1-2 paragraphs.'
    )

    print("\nData Scientist:")
    print(response_a)

    # --------------------------------------------
    # Agent B responds
    # --------------------------------------------
    response_b = agent_b.prompt(
        system='You are a Farmer.',
        query=f"""        

        The Data Scientist said:

        {response_a}

        """
        instructions='Respond and ask a follow-up question.',
        response_format='Response can be maximum 1-2 paragraphs.'
    )

    print("\nFarmer:")
    print(response_b)

    # --------------------------------------------
    # Moderator summarizes
    # --------------------------------------------
    moderator_summary = moderator.prompt(
        system='You are a neutral moderator.',
        query=
        f"""        

        Data Scientist:
        {response_a}

        Farmer:
        {response_b}

        Perform the following tasks:
        1. Summarize the key arguments.
        2. Identify agreements.
        3. Identify disagreements.
        4. Propose one question that helps both agents move toward consensus.
        
        """,
        response_format='Keep the output concise.'
    )

    print("\nModerator:")
    print(moderator_summary)

    # Store discussion history
    shared_memory.memory_add(response_a)
    shared_memory.memory_add(response_b)
    shared_memory.memory_add(moderator_summary)

    # Next round starts from moderator guidance
    message = moderator_summary


# ====================================================
# Final consensus
# ====================================================
consensus = moderator.prompt(
    system='You are a neutral moderator.',
    query=
    """
    Review the discussion and provide:

    - Main conclusions
    - Remaining disagreements
    - Final consensus statement

    """,
    response_format='Keep it under 200 words.'
)

print("\nFINAL CONSENSUS")
print("=" * 80)
print(consensus)

```

This pattern works surprisingly well because the moderator acts as a control mechanism. Without it, two agents often drift into increasingly detailed arguments. The moderator periodically compresses the discussion, extracts agreements, and injects a goal-oriented question, which keeps the conversation focused and helps the agents converge on a shared conclusion.

## Controlling the Conversation With A Scoring Agent.

To make multi-agent discussions more controllable and goal-oriented, the conversation can be explicitly bounded by a fixed number of iterations as shown in the examples above, where we used five rounds. This prevents endless argument loops, but a more dynamic and intelligent improvement is to introduce a scoring agent alongside the moderator. The task of this fourth agent is to evaluate each round of discussion and assign a convergence score based on how much agreement exists between the agents. If the score exceeds a predefined threshold, the system can terminate early, indicating that a satisfactory consensus has been reached. The scoring agent can assess factors such as semantic alignment of conclusions, reduction in contradictions, and stability of shared definitions across turns. Most optimal is to use a hybrid approach where you can use a fixed upper limit of five rounds, but with an adaptive stopping mechanism driven by agreement scoring, allowing complex topics to get the time they need to converge naturally.

![Discussion between two agents on a topic of interest. The moderator agent summarizes and tries to make the data scientist and the farmer reach a consensus. The Scoring agent scores whether there is consensus. If yes, the discussion ends; if not, another round is started. (image by author).](https://miro.medium.com/v2/1*xx86ZwIEqDZGjZrQro0TWQ.png)

```python
from LLMlight import LLMlight

# ====================================================
# Agent A: Data Scientist
# ====================================================
agent_a = LLMlight(
    model="google/gemma-4-26b-a4b-qat",
    retrieval_method="naive_rag",
    context_strategy=None,
    top_chunks=5,
    temperature=0.7,
)
agent_a.memory_init(store_path="agent_a.db", overwrite=True)

# ====================================================
# Agent B: Farmer
# ====================================================
agent_b = LLMlight(
    model="google/gemma-4-26b-a4b-qat",
    retrieval_method="naive_rag",
    context_strategy=None,
    top_chunks=5,
    temperature=0.7,
)
agent_b.memory_init(store_path="agent_b.db", overwrite=True)

# ====================================================
# Moderator Agent (keeps discussion structured)
# ====================================================
moderator = LLMlight(
    model="openai/gpt-oss-20b",
    retrieval_method="naive_rag",
    context_strategy=None,
    top_chunks=5,
    temperature=0.3,
)
moderator.memory_init(store_path="moderator.db", overwrite=True)

# ====================================================
# Scoring Agent (decides convergence / stopping)
# ====================================================
scoring_agent = LLMlight(
    model="liquid/lfm2-24b-a2b",
    retrieval_method="naive_rag",
    context_strategy=None,
    top_chunks=5,
    temperature=0.0,  # deterministic scoring
)
scoring_agent.memory_init(store_path="scoring.db", overwrite=True)

# ====================================================
# Shared memory (optional logging)
# ====================================================
shared_memory = LLMlight(model="liquid/lfm2-24b-a2b")
shared_memory.memory_init(store_path="discussion.db", overwrite=True)

# ====================================================
# Discussion Loop with early stopping
# ====================================================
topic = "Discuss the importance of attention mechanisms in modern AI."
message = topic

MAX_ROUNDS = 5
AGREEMENT_THRESHOLD = 0.85  # stop if convergence is high enough

for turn in range(MAX_ROUNDS):

    print(f"\n{'='*80}")
    print(f"ROUND {turn+1}")
    print(f"{'='*80}")

    # --------------------------
    # Agent A
    # --------------------------
    response_a = agent_a.prompt(
    system='You are a Data Scientist.',
    query=f"""

    Topic:
    {message}

    """,
    instructions='Ask a question.',
    response_format='Respond in 1-2 paragraphs',
    )

    print("\nAgent A:")
    print(response_a)

    # --------------------------
    # Agent B
    # --------------------------
    response_b = agent_b.prompt(
    system='You are a Farmer.',
    query=
    f"""

    Data Scientist said:
    {response_a}

    """,
    instructions='continue the discussion with your own opinion.',
    response_format='Respond in 1-2 paragraphs.',
    )

    print("\nAgent B:")
    print(response_b)

    # --------------------------
    # Moderator summary
    # --------------------------
    moderator_summary = moderator.prompt(
    system='You are a neutral moderator.',
    query=f"""
    
    Data Scientist:
    {response_a}

    Farmer:
    {response_b}

    """,
    instructions=
    """
    Summarize:
    - agreements
    - disagreements
    - next question toward consensus
    """
    )

    print("\nModerator:")
    print(moderator_summary)

    # --------------------------
    # Scoring Agent (convergence check)
    # --------------------------
    score_output = scoring_agent.prompt(
    system='You are a scoring system.',
    query=f"""        

    Data Scientist:
    {response_a}

    Farmer:
    {response_b}

    Moderator summary:
    {moderator_summary}

    """,
    instructions='Evaluate agreement between the two agents.',
    response_format=
    """
    Return ONLY a number between 0 and 1:
    - 1.0 = full agreement / consensus reached
    - 0.0 = complete disagreement
    """,
    )

    try:
        score = float(score_output.strip())
    except:
        score = 0.0

    print("\nAgreement Score:", score)

    # --------------------------
    # Store memory
    # --------------------------
    shared_memory.memory_add(response_a)
    shared_memory.memory_add(response_b)
    shared_memory.memory_add(moderator_summary)

    # --------------------------
    # Early stopping condition
    # --------------------------
    if score >= AGREEMENT_THRESHOLD:
        print("\nConsensus reached early. Stopping discussion.")
        break

    # Next round context
    message = moderator_summary


# ====================================================
# Final summary
# ====================================================
final_summary = shared_memory.prompt("""
Summarize the full discussion:

- final consensus
- key arguments
- remaining open points (if any)
""")

print("\nFINAL SUMMARY")
print("=" * 80)
print(final_summary)

# ========================
# ROUND 1
# ========================
# Agreement Score: 0.3
# ========================
# ROUND 2
# ========================
# Agreement Score: 0.7
# ========================
# ROUND 3
# ========================
# Agreement Score: 0.6
# ========================
# ROUND 4
# ========================
# Agreement Score: 0.8
# ========================
# ...
```

## Good Instructions Are Key.

The use of instructions has become an important part of building reliable LLM applications. While it is tempting to only focus on selecting a powerful model, research has shown that engineering the instructions can dramatically improve the output depending on how a task is described. Models such as Claude are well known for responding exceptionally well to detailed instructions, role definitions, and explicit reasoning frameworks. There are dozens of instruction guides available nowadays for various roles. These instructions clearly specify the desired behavior, output structure, constraints, and success criteria rather than relying on a single generic question. An example of a GitHub repo with instructions can be found [here](https://github.com/vizra-ai/claude-code-agents).

As LLM workflows become more sophisticated, separating instructions from the user query becomes increasingly important. Consider the difference between asking a model “*Summarize attention mechanisms*” and providing instructions such as “*Act as a university lecturer, explain the concept in three paragraphs, include one practical example, and avoid mathematical notation.*” The underlying question remains similar, yet the generated response is likely to be far more useful because the model has been given a clear objective and expected format.

LLMlight embraces this philosophy by exposing the different components of a prompt as first-class parameters. Rather than concatenating everything into a single string, you can explicitly separate the query, instructions, system message, context, and response format:

```python
response = client.prompt(
    query="Explain attention mechanisms.",
    instructions="""
        Explain the concept for beginners.
        Use exactly three paragraphs.
        Include one real-world example.
    """,
    system="You are an experienced AI professor.",
    context="some context", # This is autofilled too based on the database and RAG model.
    response_format="markdown"
)
```

This separation provides several advantages. **First**, prompts become easier to read and maintain because the task description is no longer mixed with contextual information retrieved from memory. **Second**, individual components can be reused across multiple queries, allowing developers to create libraries of instructions for specific use cases. **Third**, multi-agent systems benefit enormously from explicit instructions because each agent can be assigned a unique role, objective, and communication style without modifying the actual user question. By making instructions a dedicated component of the prompting interface, LLMlight encourages a more structured and reproducible approach to building AI systems.

## Takeaways Before Creating Language Models

At this point, you know how to set up our environment and create agents that can work on your use case. I do have a few more tips:

1. **Not every solution requires a language model.** Only consider complex models when simpler solutions do not give the desired results. Start with lookup lists, regular expressions, and TF-IDF. This will save you time, complexity, maintenance, costs, and frustration.
2. **A language model needs to be optimized for your specific use case.** A good working model requires optimization of the parameters. Choose the context strategy, retrieval method, embedding, temperature, and model carefully,
3. **Always make sure that all input text is encoded with UTF-8 or Latin-1.** Do not switch encodings, because some models may skip specific encodings, causing you to miss entire documents.
4. **Never chunk too small (< 200 characters).** This will cause hallucinations, as chunks will not contain complete information. Solutions like global reasoning and chunk-wise strategies only help to a certain extent.
5. **Remove headers, footers, boilerplates, etc.** These often create too much noise in the system, decreasing the performance of the model.
6. **Always think critically about embeddings.** Some embeddings are trained for semantic similarity, like BERT models. If you are creating a QA system, TF-IDF can outperform semantic embeddings like BERT in certain domains.
7. **Vague queries will lead to vague answers.** For example, “*Give me sports tips*” will retrieve chunks that may not be of interest.
8. **Each language model must have guardrails.** Depending on your use case, force the model to provide citations or indicate in which chunk the information was found.
9. **Knowledge Leakage Is the New Data Leakage in LLMs**. Your LLM may know more than your data. More details can be found here:

[[**Knowledge Leakage Is the New Data Leakage in LLMs.**
*Your LLM may know more than your data. Learn how knowledge leakage can silently influence your results.*medium.com](https://medium.com/data-science-collective/knowledge-leakage-is-the-new-data-leakage-in-llms-57caa4769360)](https://medium.com/data-science-collective/knowledge-leakage-is-the-new-data-leakage-in-llms-57caa4769360)

## Wrapping Up: **Don’t Go Fast, Go Structured**

This is the year of “*context engineering*”. Successful LLM integration is not about the speed of deployment, but rather about the underlying cognitive architecture. As we transition from deterministic bytes to probabilistic tokens, we must manage our systems with the same rigor we apply to traditional operating systems. **Are we prepared to manage an “*operating system*” that can occasionally hallucinate its own logic?** I think that the answer lies in building modular, local, and statistically validated infrastructure. *Start small, build your own multi-agent pipelines, and stop treating the model as a writer. Treat it as the core of your new operating system.*

*Be Safe, Stay Frosty.*

*Cheers E.*

*I hope you enjoyed reading this blog. You are welcome to [follow me](http://erdogant.medium.com/) because I write more about data science! Also, try the hands-on examples in this blog. This will help you to learn quicker, understand better, and remember longer. Grab a coffee and have fun!*

## Software

- [LLMlight Github/ Documentation](https://github.com/erdogant/LLMlight)
- [Distfit GitHub/ Documentation](https://erdogant.github.io/distfit)

## Let’s connect!

- [Let’s connect on LinkedIn](https://www.linkedin.com/in/erdogant/)
- [Follow me on Github](https://github.com/erdogant)
- [Follow me on Medium](https://erdogant.medium.com/)

## References

1. Post on X about the LLMos by [**Andrej Karpathy](https://x.com/karpathy) **[https://x.com/karpathy/status/1723140519554105733](https://x.com/karpathy/status/1723140519554105733)
2. Courses by Andrej Karpathy: [https://karpathy.ai/zero-to-hero.html](https://karpathy.ai/zero-to-hero.html)
3. E. Taskesen, [*Build Your Private Language Model: Local and Specialized For Your Tasks.](https://medium.com/data-science-collective/build-your-private-language-model-local-and-specialized-for-your-tasks-f94a3f611869)* Okt 2025, *Data Science Collective (DSC), Medium.*
4. Belcak, P., Heinrich, G., Diao, S., Fu, Y., Dong, X., Muralidharan, S., Lin, Y. C., & Molchanov, P. (2025). *Small language models are the future of agentic AI*. arXiv. [https://doi.org/10.48550/arXiv.2506.02153](https://doi.org/10.48550/arXiv.2506.02153)
5. Papadimitriou, I., Gialampoukidis, I., Vrochidis, S., & Kompatsiaris, I. (2024, December 16). *RAG Playground: A framework for systematic evaluation of retrieval strategies and prompt engineering in RAG systems*. arXiv. [https://arxiv.org/abs/2412.12322](https://arxiv.org/abs/2412.12322)
6. Mansurova, M. (2024, February 13). *Text embeddings: Comprehensive guide — Evolution, visualisation, and applications of text embeddings*. *Medium*. [https://medium.com/data-science/text-embeddings-comprehensive-guide-afd97fce8fb5](https://medium.com/data-science/text-embeddings-comprehensive-guide-afd97fce8fb5?utm_source=chatgpt.com)
7. Ajayi, A. (2025, June 30). *21 chunking strategies for RAG: And how to choose the right one for your next LLM application*. *AI Advances* (Medium). [https://ai.gopubby.com/21-chunking-strategies-for-rag-f28e4382d399](https://ai.gopubby.com/21-chunking-strategies-for-rag-f28e4382d399?utm_source=chatgpt.com)
8. Khan, F. (2025, March 12). *Testing 18 RAG techniques to find the best: Crag, HyDE, Fusion and more!*. *Level Up Coding* (gitconnected.com). [https://levelup.gitconnected.com/testing-18-rag-techniques-to-find-the-best-094d166af27f](https://levelup.gitconnected.com/testing-18-rag-techniques-to-find-the-best-094d166af27f?utm_source=chatgpt.com) [Level Up Coding](https://levelup.gitconnected.com/testing-18-rag-techniques-to-find-the-best-094d166af27f)
9. Khan, F. (2025, August 11).[ Building the entire RAG ecosystem and optimizing every component: Routing, indexing, retrieval, transformation and more](https://levelup.gitconnected.com/building-the-entire-rag-ecosystem-and-optimizing-every-component-8f23349b96a4). *Level Up*.
10. Memvid — [Turn millions of text chunks into a single, searchable video file](https://www.cohorte.co/blog/turn-an-mp4-into-your-fastest-vector-store-meet-memvid-2025), Computer Software, GitHub Rep.
