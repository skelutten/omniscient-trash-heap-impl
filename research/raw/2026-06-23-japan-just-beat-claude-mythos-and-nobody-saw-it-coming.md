---
title: "Japan Just Beat Claude Mythos And Nobody Saw It Coming"
author: "Pranit naik"
author_url: "https://medium.com/@pranithnaikpranit"
source: "https://medium.com/no-time/japan-just-beat-claude-mythos-and-nobody-saw-it-coming-cc55238ec536"
published: "2026-06-23"
fetched: "2026-09-08"
reading_time_min: 8.8
tags: ["ai", "technology", "llm", "sakana-fugu", "generative-ai-tools"]
member_only: true
body_source: "medium-session"
---

# Japan Just Beat Claude Mythos And Nobody Saw It Coming

### Artificial Intelligence | Sakana AI | Sakana Fugu Review | AI Models 2026

## Japan Just Beat Claude Mythos And Nobody Saw It Coming

### Sakana Fugu: Here Is Everything You Need To Know About This AI

![Sakana Fugu (Image Edited by Author)](https://miro.medium.com/v2/1*5QHLkQtdfqfCNO_nftnzag.png)

Read here for [FREE](https://medium.com/@pranithnaikpranit/cc55238ec536?source=friends_link&sk=294ebb00278385d125a91d4a98911d63)

Sakana Fugu starts at $20 a month, but a single hard query to its top tier, *Fugu Ultra*, can reportedly cost around $10. That gap exists because behind one simple API call, the system might quietly bring in three or four different AI models to answer your question, then merge their work into a single response. It is an unusual way to build an AI product, and it is exactly why Sakana AI’s new release has become one of the most talked about launches of the week.

## What Sakana Fugu Actually Is

![Image from Sakana Fugu](https://miro.medium.com/v2/1*IouEgn5YsX1s7bfUlovHTA.png)

Sakana Fugu is **not a foundation model** in the way GPT 5.5, Gemini 3.1 Pro, or Claude’s models are. Sakana, a Tokyo based AI lab, did not train one giant new model from scratch, and it is not claiming to have done so.

Instead, Fugu is a small “**conductor**” model that sits in front of a pool of other AI systems. You send it a prompt through one OpenAI compatible API, the same setup you would use with any other model.

*From there, Fugu decides what to do internally-*

Sometimes it just answers directly.

Other times it splits the task apart, sends different pieces to different models, checks the results, and stitches everything into one final answer. None of that complexity ever touches your code.

## **Two versions, two jobs.**

*Fugu ships as two variants behind the same endpoint:*

- **Fugu** is the everyday option. Lower latency, tuned for coding, code review, and general chat.
- **Fugu Ultra** is the heavier version, meant for long, multi step work like AI research, scientific paper reproduction, Kaggle style competitions, cybersecurity assessment, and patent or literature searches.

During the closed beta, which ran with close to 500 early users, base Fugu was actually called “Fugu Mini.”

### **The worker pool.**

Sakana’s technical report names a pool that includes GPT 5.5, Claude Opus 4.8, and Gemini 3.1 Pro, alongside open-source models. The pool is swappable. Companies can add, remove, or exclude specific models in base Fugu for compliance reasons, without any retraining required on their end. Notably, Anthropic’s export restricted Fable 5 and Mythos models are not in the pool at all, because they are not publicly reachable for anyone to call.

### **It can call itself.**

One of the stranger design choices here is that Fugu can list itself as a worker. That creates recursive loops where the system reviews its own team’s prior output, spots a failure, and spins up a corrective workflow on the fly, without retraining.

**What you cannot see.** Fugu is closed source and hosted only. You cannot run it locally, and Sakana does not disclose which models get picked for any given query. The underlying research is public. The shipped product is not.

## Benchmarks: What The Numbers Show, And What They Don’t

![Sakana fugu benchmarks](https://miro.medium.com/v2/1*Wj200Fpaty4AIQHFHKpMOQ.png)

![Image Edited by Author (Sakana fugu benchmarks)](https://miro.medium.com/v2/1*XzkD1FoPOCMZIVuT42OvfQ.png)

A few things matter beyond the raw scores.

- Every number here is **vendor reported**. The baselines come from each company’s own published results, not a neutral party running everything side by side under the same conditions.
- In an interesting twist, the cheaper base Fugu actually outperforms the more expensive Fugu Ultra on a couple of benchmarks. That suggests more orchestration is not automatically better, something Sakana itself refers to as “over orchestration.”
- Sakana’s own report also names specific patterns the system tends to fall into, like having one model debate and aggregate answers from others, having one model build something while another debugs it, or pulling in a specialist for a narrow part of a problem, such as one model handling cryptography while another rebuilds the math from scratch.
- Even basic specs are a little fuzzy. Pricing pages list a 272K token context window, while other product material mentions up to 1M, so this is one detail to verify directly if it matters for your use case.

The bigger reason this launch is getting attention has less to do with the scores and more to do with timing. The US restricted public access to Fable 5 and Mythos on June 12, 2026. Fugu launched ten days later, built almost entirely around that moment.

## Pricing

### The Part That Actually Matters For Choosing Fugu

This is probably the single biggest reason anyone outside a research lab would consider Fugu, so it is worth laying out plainly.

- Subscriptions run ***$20 (Standard)**, **$100 (Pro)**, and **$200 (Max)*** per month, and every tier includes both Fugu and Fugu Ultra.
- Pay as you go pricing for Fugu Ultra is **$5 per million input tokens** and **$30 per million output tokens**, with cached input at $0.50. Those rates roughly double once a request goes past 272K tokens of context.

Sakana avoids stacking fees across the multiple models it calls behind one query. Even if a request touches three different models, you are billed a single blended rate based on the highest tier model involved, not the sum of all of them.

- *There is a launch promotion offering a free second month for anyone who subscribes before the end of July 2026.*
- **Fugu is not available in the EU or EEA at launch**, while Sakana works toward GDPR compliance. That is a notable gap given that the whole pitch is aimed at companies and even governments worried about vendor dependence.

### Testing with Claude Opus -

One side by side test had developers build the same small game, a simple Crossy Road style clone, using both tools.

Fugu Ultra finished in about 22 minutes and roughly 89,000 tokens, costing about $7.32.

Claude Opus 4.8 took about 79 minutes and roughly 940,000 tokens, costing about $37.85.

The verdict from that comparison was straightforward: **Opus produced the better quality result, Fugu was cheaper and faster, not better.**

## How Fugu Actually Works

This is the part most coverage skips, but it explains why Fugu behaves the way it does.

### **The router in base Fugu is decision only, not generative.**

Rather than writing out a chain of reasoning and then picking a model, base Fugu uses a lightweight selection head that runs alongside the model’s normal output layer. It reads an early hidden state from the orchestrator and outputs one score per model in the pool. The highest scoring model gets the job, and Fugu skips the expensive step of generating full text to make that decision. That is the main reason its response time can feel close to a direct call to a single frontier model, rather than something noticeably slower.

### **Fugu Ultra runs on something called the Conductor.**

Instead of picking one model, the Conductor writes out an entire workflow in plain language: a sequence of steps, each naming a subtask, the specific worker assigned to it, and which earlier outputs that worker is allowed to see. That last piece, called an access list, is what defines the communication structure between agents. It is flexible enough to support simple chains, best of several attempts, or branching tree shaped workflows. Ultra typically designs workflows of up to five steps, averaging around three.

**Persistent memory is the newer addition.**

*Two mechanisms here are worth knowing:*

- **Agent isolation.** One worker only sees another worker’s output if it is explicitly on its access list. This stops the first model to respond from quietly biasing everyone after it.
- **Shared memory across turns.** In a longer conversation, later workflows can see tool calls made in earlier ones, so the system does not waste time repeating the same lookup or calculation.

### **How it was actually trained.**

Sakana describes a four part pipeline:

1. Supervised fine tuning on tasks with a clear right answer, where each worker model is tested repeatedly and the router learns from the resulting spread of scores, not just a single best label.
2. Evolutionary optimization, using a method called CMA ES, on real multi turn coding sessions. Sakana says it tried standard reinforcement learning first and it failed here, because the reward signal was too thin and noisy. The evolutionary approach worked better.
3. Reinforcement learning for the Conductor’s workflow design, trained on randomized pools of models so it generalizes to whatever mix of open and closed models it is later given.
4. The persistent memory system described above.

Sakana also reports a token efficiency figure worth flagging with some skepticism: its Conductor paper claims roughly 1,820 tokens per query, compared to about 11,203 for a conventional multi agent setup. That is a research paper metric, not an independently verified spec of the shipped product.

### The Demos Sakana Showed Off

Alongside the benchmark numbers, Sakana ran a handful of hands on demonstrations:

- An autonomous research run where the system improved a small model’s training setup across more than 100 experiments in under a day on a single GPU, beating three comparison baselines.
- A Rubik’s Cube solver, written from a single prompt, that solved all of its held out test cubes near the optimal number of moves while two of three comparison models failed completely.
- A reading task on a centuries old piece of classical Japanese handwriting, where Fugu Ultra scored far higher than the closest comparison model.
- Four games of blindfold chess, where it beat three frontier models and a strong chess engine.
- A simulated trading run over one historical market window, which posted stronger average returns than the comparison models, with the standard disclaimer that past performance does not guarantee future results.

These make for a good launch video, and they are genuinely creative test cases. They are also still company run demos, judged against company chosen comparisons.

## Fugu vs OpenRouter Fusion

The comparison everyone keeps making is to OpenRouter’s Fusion, which moved from an experimental feature into full API availability just days before Fugu launched. They sound similar on the surface. They are not built the same way.

### **Fusion fans out, then merges.**

It sends your prompt to several models at once, in parallel, has a judge model compare the answers for agreement, disagreement, and gaps, and then has a synthesizer write a final response that blends the strongest parts of each one. It is built for cases where multiple perspectives genuinely help, like research questions or expert critique, and OpenRouter has published results showing fused panels beating individual frontier models on a deep research benchmark.

### **Fugu decides first, then acts.**

Its conductor figures out up front which models to call, in what order, and what each one is allowed to see, before any of those calls happen. Instead of asking everyone the same question and blending the answers, it might have one model build something, hand it to a second model to check for security issues, and only bring in a third if the first two disagree. The common shorthand circulating online captures it well: Fusion behaves more like a voting booth, Fugu behaves more like a conductor.

**The cost models are different too.**

- Fusion bills you for every model it calls in the panel, plus the judge. With a typical three model panel, that can run roughly four to five times the cost of one regular completion.
- Fugu charges a single blended rate no matter how many models get pulled in behind the scenes.

Some commercial breakdowns put Fugu’s effective cost at around a quarter of an equivalent Fusion run, though that depends heavily on the workload and how often each system actually decides to call in extra help.

Neither system has been tested independently at real scale yet, and both are only days to weeks old.

## Reception & Skepticism

Reaction to Fugu is mixed. Supporters see it as a hedge against relying on a single AI provider, while critics argue it is still a closed-source system built on closed-source models, so it does not provide true AI sovereignty.

Skepticism is also fueled by Sakana’s track record. Earlier projects, including AI CUDA Engineer and AI Scientist, faced criticism over evaluation issues and unreliable results, leading some researchers to view Fugu’s benchmarks cautiously.

## Notable Facts

- Sakana was founded in 2023 by David Ha, Llion Jones, and Ren Ito.
- It reached a $2.65B valuation after a $135M Series B in 2025.
- An open-source replica, **OpenFugu**, appeared shortly after launch.
- Sakana’s earlier **ALE-Agent** achieved strong results in major coding competitions.

## Who Fugu Is For

- Best for complex, multi-step tasks like coding, research, and verification.
- Less compelling for simple prompts, where a frontier model may be cheaper and faster.
- Useful as a vendor-diversification strategy, but not true sovereignty.
- Not currently available in the EU/EEA.

## Bottom Line

Fugu is an interesting orchestration system with promising ideas, but most performance claims come from Sakana itself. Independent validation is limited, and early users report mixed experiences, so it is best viewed as a promising experiment rather than a proven replacement for leading models.
