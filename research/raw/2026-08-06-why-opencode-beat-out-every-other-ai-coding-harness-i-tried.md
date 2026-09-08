---
title: "Why OpenCode Beat Out Every Other AI Coding Harness I Tried"
author: "Hamza Boulahia"
author_url: "https://medium.com/@hamzamlwh"
source: "https://pub.towardsai.net/why-opencode-beat-out-every-other-ai-coding-harness-i-tried-4f1d60922303"
published: "2026-08-06"
fetched: "2026-09-08"
reading_time_min: 12.0
tags: ["ai", "ai-agent", "vibe-coding", "claude-code", "agentic-engineering"]
member_only: true
body_source: "medium-session"
---

# Why OpenCode Beat Out Every Other AI Coding Harness I Tried

### A year of testing came down to one clear winner, and it wasn’t Claude Code.

![Created by the author using AI.](https://miro.medium.com/v2/1*fl9X_qdFSBmWHFWywqe6Tg.png)

> [*Read for free link](https://medium.com/towards-artificial-intelligence/why-opencode-beat-out-every-other-ai-coding-harness-i-tried-4f1d60922303?sk=60c4b1c99dcb32af902b3ec1ad80970d)*

We’re currently entering the age of state-of-the-art (SOTA) open-source models.

Kimi K3 landed a few weeks ago, and before that we had GLM 5.2. It’s getting more and more clear that OpenAI, Anthropic, and Google finally have real competition from open-source models.

We’ve known for a while that frontier LLMs are plateauing. Every new flagship is a smaller step up than the last one. That was always going to mean open-weight models would eventually close the gap with the closed labs. It was just a matter of when.

What’s new this summer is that “eventually” is starting to look a lot like “now.”

![Image from Artificial Analysis](https://miro.medium.com/v2/1*-8WpFKAP9TI7Zl1gVW-tlw.png)

Over the past year, I’ve tried a handful of AI coding harnesses: Gemini CLI, Claude Code, Kiro, Antigravity, and now OpenCode.

**If you’d asked me four or five months ago** what the best option was for a developer building small to medium projects, I’d have said Claude Code or Codex without much hesitation.

**My reasoning was simple:**

These companies had the strongest models for agentic coding. They were able to accomplish tasks using fewer tokens, and despite justified complaints about strict usage limits, their subscription plans provided a better cost-per-token ratio than running the same models through a raw API.
For example, running Opus through a Claude subscription is most definitely cheaper per token than accessing the same model through an API provider such as OpenRouter.
On top of that I was leaning more towards TUI/CLI Agents, instead of IDE-integrated agents, which were the most prominent options at the time. Also, my use case doesn’t need a token-hungry setup either, and the codebases I work on aren’t massive, so a standard subscription plan gave me more than enough compute.

**But, ask me today** and the answer is OpenCode.

Two months in, it’s been a better experience than I expected going in.

Here’s why, with actual numbers.

## The Open-Weight Models Are Actually Catching Up

GLM 5.2 came out of Z.ai in mid-June. It’s a roughly 750-billion-parameter mixture-of-experts model released under a plain MIT license. Its performance is comparable to Opus 4.8, but it costs $0.6 less per million input tokens and $20.6 less per million output tokens.

Then, Kimi K3 followed from Moonshot AI in mid-July, 2.8 trillion parameters, also built for long-horizon coding and agentic work. Its performance is comparable to Fable 5, but it costs $7.0 less per million input tokens and $35.0 less per million output tokens.

These are top tier models that are in the Top 10 overall models for Web Dev according the Arena.ai, as shown in the image below.

![Screenshot from Arena.ai](https://miro.medium.com/v2/1*g3_xkbcxJpO6sKCxyEEomA.png)

While the overall performance of Claude Opus 4.8 across all relevant benchmarks (Intelligence, Coding, and Agentic) is still better than GLM 5.2, as shown in the image below. The gap isn’t really a noticeable one for standard agentic and coding tasks.

The gap becomes much more noticeable when asking models to one-shot an entire application or game from scratch. These extreme tasks are where frontier models still show their advantage.

But that is not how most developers actually use coding agents.

Most real-world usage consists of smaller iterative tasks:

- Debugging, implementing features, refactoring code, writing tests, exploring unfamiliar codebases, and improving existing systems.

For these workflows, the difference between the best closed models and the best open-weight models is becoming increasingly difficult to justify purely from a capability perspective.

![GLM 5.2 vs. Opus 4.8 benchmarks on Openrouter](https://miro.medium.com/v2/1*msefvHVhESVpa82uGkF8Wg.png)

Kimi K3 doesn’t just close the gap on Claude Fable 5, it beats it outright on several benchmarks, including taking the number one spot on the community-voted Frontend Code Arena, ahead of every closed model on the board.

![Kimi K3 ranking on Frontend code arena — Arena.ai](https://miro.medium.com/v2/1*o3YHFp-QeCdvMiYAw0yy7g.png)

**That does not mean open-weight models have won.**

Neither GLM 5.2 nor Kimi K3 dominates every benchmark, and evaluating LLMs requires much more than looking at a few leaderboards or a “Trust me bro” benchmark on release.

Performance depends heavily on the specific workflow, the type of tasks, the agent harness, and the developer’s expectations.

But for me at least, “still ahead on the hardest slice of tasks” and “worth several times the price for everything else” are two different claims. And without a doubt, the second one is the one that decides what I reach for most days.

## The Harness & Model Provider Choice

To be fully rigorous, I’d have to test every available harness, and that’s a lot. Just counting the coding agents that work with OpenRouter gets you to 34, shown below.

![Image data from Openrouter](https://miro.medium.com/v2/1*2Xp1nalM8PHeq6JejbaTiQ.png)

> *However, this post is not meant to be a universal benchmark. It is based on my personal workflow and experience.*

So, unless your use case, workflow, and project size look something like mine, **take this as one data point rather than an absolute fact.**

### Harnesses That I Previously Tried

Over the past year, I tried Gemini CLI, Kiro, Claude Code, and Antigravity. None of them stuck the way OpenCode did. Here’s the quick rundown:

- **Gemini CLI** was my first “vibe coding” experience. I liked Gemini 2.5 Pro’s performance for debugging, so I figured I’d give the CLI a shot. It was okay at first, with plenty of room for improvement, but usable for POCs and less demanding coding tasks. The frustrating part was its inability to consistently follow the rules and guidelines I specified in the GEMINI.md file. It worked fine for quick scripts but never felt built for sustained work. Interestingly, Google seems to have recognized similar limitations and has since shifted focus toward newer agent-oriented tools.
- **Kiro** came next. It was the trendy, newly launched harness with a different take on coding agents. Kiro is AWS’s spec-first IDE; it automatically generates requirement and design specs from your prompt before implementation, though you can also bypass spec generation to code directly. This approach felt like a real step up from Gemini CLI. It was really good, until it wasn’t. 
It leaned too heavily on specs, to the point where it felt too spec-y for simple projects, and the models at the time weren’t reliable enough to handle all that. Besides that, I’m also a committed VS Code user, so switching IDEs for good was never really on the table (which is also why I never tried Cursor).
- **Claude Code** was next. To be honest, I mostly wanted to see what the fuss was about. People on X wouldn’t stop talking about it. But since I am not a fan of Anthropic or OpenAI, I wasn’t really committed to any of their products. That being said, I can’t deny it outperformed everything I’d tried before across the board, partly because Claude Code is a better harness overall, and partly because Anthropic’s models were simply better at agentic coding at the time.
- **Antigravity 2.0** was the last stop. I’d heard it was a big improvement over the first release, and since it’s marketed as an agent-first platform (more on what that means shortly) and launched alongside Gemini 3.5, I gave it a try. As expected, it didn’t fit well with my coding workflow and how I want to use AI for coding.

**One more thing worth noting**: I never used any of these harnesses for more than a month. That was enough testing time for me. Between trials, I fell back on the “old way” of doing things, leaning on chatbots when I needed help.

Then, I switched to **OpenCode**.

### Why OpenCode

OpenCode is an open-source tool built by the Anomaly team back in mid-2025. Since then, it went from a fairly niche terminal tool to a massive project with well over 190,000 GitHub stars and millions of monthly developers as of this writing.
I knew about it, but I was never interested enough to use it. As I said, there are new AI harnesses launching every month, and chasing every hype cycle isn’t productive. 
What actually got me looking into open-source harnesses was GLM 5.2 and the extraordinary performance-to-price ratio it offered. That’s when I decided to do a thorough research on which open-source harness to use. 
I won’t bore you with the details, but It came down to either Pi or OpenCode.

Based on my previous experiences, I had reservations about CLI/TUI-based agents, and I realized that I did not actually want my coding agent integrated directly into my IDE. So I’ve come to believe a separate GUI is the better call, for a few reasons:

- It’s easier to use.
- It feels more natural to navigate history, adjust preferences, and manage sessions.
- It has better ergonomics for reviewing an agent’s work: diffs, tool calls, reasoning.
- GUIs are generally more advanced, supporting things like remote environments, mobile control, image handling, and file browsers.

Fortunately, on top of its CLI and TUI, OpenCode also has a desktop app, that’s still in beta.

On top of all that, OpenCode is a human-first harness and it has a subscription plan that provides GLM 5.2 among other open-source models, and it’s performance as a harness is better than Cursor CLI and Caude Code according to the following Coding Agent Index.

![Image from Artificial Analysis.](https://miro.medium.com/v2/1*3LRPK0BOLEM2X0o-i4LHuw.png)

That basically sums up why I picked OpenCode over Pi.

### About Human-first vs. Agent-first Approaches

OpenCode defaults to a two-mode(agents) setup:

- **Plan mode** is read-only and asks permission before touching your shell.
- **Build mode** is where it actually writes code.

You can flip between the two with a single keystroke/click, once you’ve read what it’s proposing. In short, the AI don’t ever acts fully autonomously, and you retain total control over what actually gets executed.

That’s briefly a human-first approach.

An agent-first approach is when you’re managing a fleet of agents from a distance:

- You talk to an orchestrator, which in turn spawns sub-agents and assigns them tasks.

So instead of guiding every step, you set the high-level objective and let the AI system execute autonomously.

Now, I don’t think agent-first is the wrong idea. It just doesn’t fit my workflow. Most of what I build doesn’t need five agents managing themselves in parallel. It needs one agent I can steer and supervise directly.

### Choosing a Model Provider

With my harness sorted, I searched for the best model provider in terms of price-to-compute ratio. That was quite the challenging task, because the main issue with subscription plans is that most of them are opaque and don’t really quantify how much compute they provide in terms of Tokens. So comparing them objectively is hard, since there’s no shared standard to measure against.

The best alternative I could think of was **user reviews**.

So I read through countless reviews and discussions about OpenCode Go, Ollama Cloud, and Z.ai, the only three providers I could find offering subscription plans for GLM 5.2.

Here’s what those reviews consistently pointed to:

- **Value for money:** OpenCode Go came out slightly ahead of Ollama Cloud Pro, and well ahead of Z.ai Lite.
- **Reliability and uptime:** Both Ollama Cloud Pro and Z.ai Lite had frequent complaints about downtime, lag, and timeouts.
- **Speed:** OpenCode Go generates responses noticeably faster than either alternative.

So overall, the Go plan was the recommended option.

The main caveat, however, is that it’s intended for small projects, so using it on a large codebase will deplete your usage in less than two weeks period, given that there’s a weekly usage threshold that you can’t surpass.

Once you’re out, it either drops to the free-tier models or draws down your Zen (OpenCode’s pay-as-you-go option) balance if you keep one topped up.

**But how much compute does the Go plan actually give?**

The subscription price is $10/month, and it provides a $60 of raw API cost. So here’s what it translate to in tokens for GLM 5.2, Kimi K3, and DeepSeek V4 pro:

![Go Subscription Plan translated into maximum and realistic blended token yields](https://miro.medium.com/v2/1*i8_8B09PyvUVhzTp-WC1GQ.png)

Based on those values, my workflow became:

- GLM 5.2 for complex reasoning and difficult implementation tasks.
- Cheaper bundled models, like DeepSeek V4 pro, for routine coding.
- Free models such as DeepSeek V4 Flash for simple questions and conversations.

During the first three weeks of the subscription, I rarely felt constrained.

**Notes:**

- Kimi K3 wasn’t available during my first month, but it’s now available, and it’s a very attractive option for highly complex tasks.
- If you’re more inclined toward pay-as-you-go, my advice is to skip OpenRouter. It’s the popular choice, but there are better options out there. Neuralwatt is one I’d point you to. I first found out about it through [this Reddit thread](https://www.reddit.com/r/opencodeCLI/comments/1tcq264/neuralwatt_has_been_a_surprisingly_good_cheap/), worth a read if you want the details.

For developers who need more capacity than what the Go subscription provides, combining it with a cheaper pay-as-you-go provider can be a very cost-effective setup. I’ll write about what the best combination is once I end up testing that setup myself.

## The OpenCode Experience

With the desktop app and a Go subscription set up, I got straight to work. I had a small project idea I’d been putting off for a while, so it felt like the right time to finally try it.

First, I set up my harness the way I prefer it to be:

- Connected my model provider.
- Created custom agents and sub-agents.
- Downloaded relevant skills.
- Set up my global AGENTS.md file.

My goal with this setup was to create an environment where the agent understood my workflow, and coding preferences from the beginning.

### **Workflow**

My average daily spend was around $3 to $4 during the first month.

I used GLM 5.2 for planning and the harder coding tasks, DeepSeek V4 Pro and MiniMax M3 for standard and simple coding work, and the free DeepSeek V4 Flash for chatting and quick questions.

This combination worked surprisingly well, and I’ll always recommend it.

> *Instead of using the most expensive model for every interaction, treat models as different tools with different strengths.*

### **Performance and reliability**

Honestly, The experience was smoother than I expected.

I haven’t experienced any downtime, errors, or delays.

Generation speed was acceptable, although it naturally depended on the selected model and the complexity of the task.

The combination of the OpenCode desktop application and VS Code worked particularly well for my workflow.

Instead of embedding the AI assistant directly inside my editor, I had a dedicated space for managing conversations, reviewing changes, and controlling the agent.

That separation felt really natural.

By the second month, the project that I started working on with OpenCode had grown past 20,000 lines of code, and I started hitting my self-imposed daily limit of $4 faster. That meant being more deliberate about session management and which model or agent I used.

That’s why a hybrid approach makes more sense for medium size projects.

For example:

- OpenCode Go ($10/month) as the main subscription.
- Additional Zen credits when needed.
- A secondary pay-as-you-go provider such as Neuralwatt for overflow usage.

Compared to traditional frontier subscriptions (Typically $20), the total cost remains very competitive.

## **Final thoughts**

OpenCode is a customizable, and beginner friendly harness, that support all the feature you’d expect or need. Its desktop app is well designed, feels natural to use, and doesn’t introduce friction to your coding workflow.

When it comes to model providers, the Go subscription is definitely a great if not the best place to start. But, if you’re working on medium sized or bigger projects, that won’t be sufficient for the whole month. Since it’s only $10, though, stacking a second subscription or adding a pay-as-you-go option is what I’d recommend.

So if you’re still paying frontier prices for every single token, it might be worth checking whether you still need to.

### Update:

In this post, I suggested using Neuralwatt as a Pay-as-you-go provider for additional compute, as it was recommended to me. I ran a small test using the same settings I tested OpenCode Go on. Here’s the result of usage:

![Neuralwatt test usage](https://miro.medium.com/v2/1*W82oj3_wPKwT_ToNWR9LNw.png)

As shown in the cost card using the energy pricing saved me just $0.05 for the amount of Input/output tokens I used. That’s not a big difference, but it is indicated everywhere on their website that the real efficiency of the energy pricing approach can be seen when using “efficient architectures” which are basically MoE Models, like Kimi models and some of the Qwen models. So, if you only use dense models, like GLM 5.2, you know what to expect.

![](https://miro.medium.com/v2/1*8vKR3n85KtVgKgi2Z3Tdqw.png)

**Thanks for taking a few minutes out of your day to read this.**

**Leave a comment** and **follow** me for more insights on AI, ML, and coding.
You can also check out my work and socials: [Website](https://hmzbo.github.io/) | [YouTube](https://www.youtube.com/@MLWH/featured) | [GitHub](https://github.com/Hmzbo) | [LinkedIn](https://www.linkedin.com/in/hamza-boulahia-280581a6) | [X](https://x.com/HamzaBlha) | [Substack](https://substack.com/@hamzamlwh?utm_campaign=profile&utm_medium=profile-page)

**Looking to level-up your AI engineering skills?
**I’ve curated a collection of must-read books and top online courses covering software architecture, deep learning, system design, LLMs, and AI fundamentals.
👉 E[**xplore my AI Engineering Reading List
](https://benable.com/HmzBo/books-to-master-ai-engineering-in-2026)👉** Ex[**plore my AI Engineering Online Courses List](https://benable.com/HmzBo/my-recommended-ai-certified-courses)**
