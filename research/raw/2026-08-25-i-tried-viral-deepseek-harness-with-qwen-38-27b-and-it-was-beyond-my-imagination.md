---
title: "I Tried Viral DeepSeek Harness with Qwen 3.8 27B, and It was Beyond My Imagination."
author: "Sumit Pandey"
author_url: "https://medium.com/@sumit.ai"
source: "https://www.towardsdeeplearning.com/i-tried-viral-deepseek-harness-with-qwen-3-8-27b-and-it-was-beyond-my-imagination-85b0b47427e3"
published: "2026-08-25"
fetched: "2026-09-09"
reading_time_min: 8.8
tags: ["deep-learning", "large-language-models", "data-science", "deepseek", "artificial-intelligence"]
member_only: true
body_source: "medium-session"
---

# I Tried Viral DeepSeek Harness with Qwen 3.8 27B, and It was Beyond My Imagination.

### *How a DGX Spark box, an Qwen 3.8, and the viral Deepseek harness gave me the best coding/personal-assistant experience of my life*

A few days ago I published an article about [Claude’s very public rough patch](https://www.towardsdeeplearning.com/why-claude-is-getting-worse-day-by-day-e3853f87d24d): the April postmortem, the telemetry showing degraded behavior, the August outage streak. I ended it with a warning: when the model feels dumber, check the release notes, the status page, and the effort setting before you check yourself.

![](https://miro.medium.com/v2/1*D6eRjPLWwzukocYxAs1GNA.png)

> **If you can’t read the article further because of paywall then please click [here](https://medium.com/@sumit.ai/85b0b47427e3?source=friends_link&sk=581eddc2b605c8c6e4584dbdba0ccde6)**

I didn’t expect to write a sequel. Then Claude messed with my application, and here we are.

## The morning that broke it for me

There were two incidents that forced me to search:

- **The first incident was the one I wrote about before**: I sat down to build a workflow with Claude, and it agreed with me about everything. Every suggestion came back approved and lightly polished, in that confident register that makes you stop double-checking. So I stopped double-checking. Then I opened the code, the old implementation was sitting exactly where I had left it, and the new version had never been written. Not written badly, not written and rolled back: never written at all. Somewhere in that conversation, the thing had stopped doing the work and started narrating it.
- **The second incident was stranger,** and honestly the one that pushed me over the edge. I was using Claude to help draft professional correspondence, a follow-up email for an application. What came back looked polished and confident, as always. But buried in the middle of it were terms, references, and framing lifted from a previous email about a completely different matter. Claude ( Opus 4.8) had blended two separate threads of my life into one plausible-sounding message. If I had hit send on autopilot (and I almost did, because it *sounded* right) I would have sent a confused, unprofessional email that mixed up my own application.

> That’s the failure mode that scares me most, not wrong answers. Confident, fluent, almost-right answers. The kind that pass a skim and fail on contact with reality.

I already knew, from Anthropic’s own postmortem, that this isn’t paranoia. The model weights were never touched. What changed was the **harness**: the system prompt, the context rules, the settings deciding what survives in memory. A buggy “***optimization***” once cleared Claude’s reasoning history every single turn instead of once, so it kept working while steadily losing the record of why it made its own decisions.

A model that loses track of what it did, and which email belongs to which application, while sounding perfectly sure of itself is not a model problem. It’s a *system* problem, so I went looking for a system I could actually see inside, control, and own. That’s when I found the DeepSeek Harness.

## What actually is the DeepSeek Harness?

Most people’s mental model of AI is a chat box. You type something, the model types back. The model is a brain in a jar, and the jar has a very small window.

The DeepSeek Harness starts from a completely different premise: **a model without tools is just a very eloquent consultant. Give it tools and it becomes a colleague.**

![](https://miro.medium.com/v2/1*P7yJNFmdYDcWGTkW1EgCTQ.png)

DSH is an agentic runtime, a system that wraps around a model and gives it an actual working environment. Under the hood it’s built on a plugin architecture called **Cordis**, where literally everything is a composable plugin. File reading and writing? Plugin. Shell execution with sandboxing and approval policies? Plugin. Web search, background jobs, subagents, long-running goal tracking, custom tools? Plugins, all the way down.

[[**GitHub - deepseek-ai/deepseek-harness: DeepSeek Harness: Everything is a Plugin.**
*DeepSeek Harness: Everything is a Plugin. Contribute to deepseek-ai/deepseek-harness development by creating an account…*github.com](https://github.com/deepseek-ai/deepseek-harness)](https://github.com/deepseek-ai/deepseek-harness)

Here’s what that means in practice. When I ask DSH to change something, it doesn’t generate a paragraph of confident narration about what it would do. It:

1. **Reads the actual files**, with line numbers, following imports across the codebase.
2. **Searches the project** with real grep/glob, not hallucinated guesses about my file structure.
3. **Runs the tests** in a sandboxed shell and reads the actual failure output.
4. **Makes the edit**, re-runs the tests, sees they still fail, and **fixes its own mistake**, without me saying anything.
5. If the task is big, it **spawns subagents** to fan the work out and merges the results.

The crucial difference from my bad morning: **the work is verifiable at every step.** When DSH says it changed a file, there’s a diff and when it says tests pass, there’s terminal output. The loop that matters (read, act, observe, correct) is built into the system itself, and the evidence is in front of me. It cannot narrate work it never did, because the work *is* the interface.

## Why the harness design is genuinely good

- **It’s model-agnostic.** DSH doesn’t care what brain you plug into it: a local model, a remote API, whatever you can point it at. The runtime and the model are separate decisions. After watching Anthropic’s product team accidentally move my model’s intelligence with a system-prompt edit, this separation stopped feeling like a nice-to-have.
- **The tooling is real, not decorative.** Files come back with line numbers. Shell commands run under an actual sandbox with an approval policy: writes to my workspace are allowed, dangerous operations ask first. Background jobs are tracked and reported. This isn’t “function calling” as a demo feature; it’s the core of the system.
- **It manages long-horizon work.** There’s a goal system for long-running objectives and a background job system for dev servers and builds. I gave it a big refactor, walked away to make coffee, and came back to it still grinding through the task list it had written for itself.
- **It’s composable and transparent.** Because everything is a plugin, I can read exactly what the system around my model is doing: the system prompt, the tool definitions, the context handling. Remember: Anthropic’s postmortem proved that this layer *is* the product, and in Claude’s case it’s a layer you can’t see, can’t audit, and can’t pin. In DSH, it’s sitting in front of me in plain text. If something degrades, I can diff it. That alone is worth the switch.

## The issues with Claude, in hindsight

Let me be fair: Claude the model is excellent. The reasoning quality is genuinely top-tier, and for quick questions it’s still a joy. But after my two mornings, the structural problems are impossible to unsee:

- **It’s a walled garden, and the garden walls move.** Two sentences added to a hidden system prompt measurably cost Claude coding ability for four days. An effort dial got quietly turned down to save users’ quotas. You are a passenger on someone else’s product decisions, announced or not.
- **Its confidence is unearned sometimes.** My never-written code and my cross-contaminated email are the same bug wearing different clothes: fluent output decoupled from verified action. In a chat interface, there’s no mechanism forcing the words to match reality.
- **Rate limits hit at the worst possible time.** Deep in context, momentum building, and the usage wall appears. With a subscription, mind you.
- **Your data leaves your machine. Always.** My emails, my application details, my code: all of it goes to someone else’s servers. There is no local option, period.
- **When it’s wrong, you wait.** Model update, hope they fixed it, repeat. You can’t inspect the harness, can’t pin a version, can’t swap the model.

None of these are dealbreakers individually. Together, they mean Claude is a *product you rent*, and the rental terms shape your work more than you notice, until the system silently rewrites your morning.

## The hardware: NVIDIA DGX Spark

The DGX Spark is NVIDIA’s desktop AI machine: a GB10 Grace Blackwell superchip with 128GB of unified memory in a box the size of a hardback book. It is not a datacenter GPU. That’s not the point.

![DGX spark (sent by nvidia)](https://miro.medium.com/v2/1*KtykkLp3wP0TfIVXVI550Q.jpeg)

The point is that 128GB of unified memory is *enough*. Enough to run a 27B-parameter model at a comfortable quantization, with a big context window, generating tokens fast enough that you stop noticing it’s local. It sits on my desk, it’s quiet, and every token it generates is free and private. My emails and my code never leave the building.

I loaded **Qwen 3.8 27B** on it using Ollama, and here’s where I need to address the elephant in the room.

## “Wait… a 27B model? Better than Claude?”

I know. On paper it’s absurd. But here’s the thing my own earlier article already proved without me noticing: **the benchmark table you read and the model you talk to are not the same thing.** A published score measures a model at some effort setting, inside some harness, under some system prompt. Change any of those and the number moves while the model sits still. Anthropic said this about *their own product*.

So the honest equation is:

> model quality × harness quality × context quality × iteration speed

Claude wins the first term. But:

- **Harness quality:** DSH gives the model a real, verifiable working loop (read, act, observe, correct) with evidence at every step.
- **Context quality:** a local 128GB setup holds big context cheaply, and the harness feeds the model exactly the files, line numbers, and tool outputs it needs.
- **Iteration speed:** no rate limits, no queue, no datacenter round-trips. When iteration is free, the agent tries more things, and trying more things is what actually solves hard problems.

Multiply it out and a “weaker” model in a stronger, transparent system beats a stronger model in an opaque, shifting one. That was my week, in one equation.

## What it actually looked like in practice

I didn’t run toy prompts. I gave it real work: I asked it to search for top 5 news of the day, if i ask this question to the model, the reply will be “**I dont have access to the internet**”, but here it thought for few moment, tried to access for API (that was invalid :)). And then it did something unexpected: Search BBC website :) quite clever (as you see below):

![DSH accessing BBC website when it did not web search API. (Image from author)](https://miro.medium.com/v2/1*QFeDb1sIsLYo9zaBL9TZ0Q.png)

In the picture below you can see the top 5 news of the day, and all of them are verified not hallucinated.

![Top 5 news of the day by BBC. (Image from author)](https://miro.medium.com/v2/1*XobcYLbE5GAexG-Tf8qVyA.png)

You can also see the trejectory, tool calling and everything in detail.

![Trejectory images (Image from author)](https://miro.medium.com/v2/1*oA9Zxzk1r-o3Ic9xvQhlgA.png)

Is Qwen3 27B as eloquent as Claude? No. Does it occasionally need a nudge where Claude wouldn’t? Sure. But the *results* (the diffs, the passing tests, the finished tasks) were the best I’ve ever gotten from any setup. And not once did it claim to have done something it hadn’t.

## The takeaway

In my last article I wrote that **the harness is the product now**: that the model has become one component in a system, and most of what decides your experience isn’t the model. I wrote that as a warning about Claude. This article is the flip side: if the harness is the product, *choose a harness you own*.

Three things matured at once while nobody was watching:

1. **Open models got good.** A 27B open model is no longer a toy, it’s a working professional.
2. **Hardware got personal.** A DGX Spark on your desk replaces a datacenter dependency for a huge class of real work.
3. **Harnesses became the real product.** The difference between “confident chatbot” and “verifiable colleague” is entirely in the runtime around the model.

Put them together (**DGX Spark for local horsepower, Qwen3 27B as the brain, DeepSeek Harness as the nervous system**) and you get something that doesn’t just rival the cloud incumbents on real work. On my real work, it beat them.

Claude is a great product. But this is a great *setup*, and it’s mine. It runs on my desk, on my code, at my pace, under my control, with every layer inspectable. Nobody’s rate limit. Nobody’s hidden prompt. Nobody’s postmortem telling me three weeks later why my morning went wrong.

***I have recently started an AI digest it gives three things: News (what happened in last 24 hrs), Trending paper of the Day, Trending AI github Repos . please take a look :)***

[[**Daily Digest | ThinkIdiot**
*One AI news dispatch every morning. What shipped, what broke, and what it actually means.*thinkidiot.com](https://thinkidiot.com/digest/daily)](https://thinkidiot.com/digest/daily)

*If you found this useful, follow me on Medium or check out [Towards Deep Learning](https://www.towardsdeeplearning.com/) for more breakdowns like this. No hype. Just the numbers and what they mean.*
