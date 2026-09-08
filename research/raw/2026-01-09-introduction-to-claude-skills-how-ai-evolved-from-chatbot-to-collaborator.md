---
title: "Introduction to Claude Skills: How AI Evolved from Chatbot to Collaborator"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/introduction-to-claude-skills-how-ai-evolved-from-chatbot-to-collaborator-92e1711e778b"
published: "2026-01-09"
fetched: "2026-09-08"
reading_time_min: 10.8
tags: ["claude-skills", "claude-code", "ai"]
member_only: true
body_source: "medium-session"
---

# Introduction to Claude Skills: How AI Evolved from Chatbot to Collaborator

### People are no longer just competing on whose model is smarter, but who can use AI better.

![](https://miro.medium.com/v2/0*kxhcs_i7tkWz5Zpg.png)

Have you ever felt like new AI terminology changes faster than smartphone release cycles?

You just figured out what “Function Calling” was yesterday, and today “Skills” pops up. Someone mentioned “MCP” the day before yesterday, and before you’ve even processed it, someone else is talking about “Agent” tomorrow. Every time you see these words, your first thought is: Am I falling behind again?

Don’t panic. Today we’re going to break down “Claude Skills” and make it crystal clear.

More importantly, I’ll explain how it relates to concepts you already know — functions and function calling. You’ll discover these aren’t three isolated new terms, but rather steps building on top of each other. Once you understand these three layers, you’ll be able to judge where any new term fits.

## Starting Point

Let’s begin with something familiar: “functions” in programming.

Think of a function as a “little helper.” You tell it what to do (give it an input), and after completing the task, it tells you the result (gives you an output). Like a waiter in a restaurant: you order, they serve, following the same process every time.

For example, a programmer writes a function called `calculate_tax(income)`. You throw in an income number, and it calculates how much tax you owe and returns it. Need to calculate again? Just call it once more. No need to rewrite the tax calculation logic every time.

The value of functions comes down to three principles: **encapsulation, reuse, standardization**.

Package up how something is done, and anyone can use it later, always the same way. This has been programmers’ most fundamental productivity tool for decades.

![](https://miro.medium.com/v2/0*JaC-ftV4H-PIoB8O.png)

But functions have a limitation — they only exist in the code world.

When a programmer writes `getWeather()` in code, that function will 100% execute. But regular people don't write code, and AI doesn't directly "run" this code. So how do we let AI use these "little helpers"?

## Building Bridges

In 2023, a concept called “Function Calling” became popular.

Think of it as giving the AI that could only chat a phone and a contact list.

Before this, when you asked AI “What’s the weather like in Beijing today?” it would either make up an answer from training data or honestly say “I don’t know.” Because it couldn’t actually do anything — it had no way to take action in the real world.

With function calling, things changed.

Developers tell AI in advance: “Here’s a contact list with a function called `get_weather`. When you want to check the weather, call this number." When AI receives the question "What's the weather like in Beijing today?" it decides: "Oh, I need to call `get_weather` to answer this."

Then it generates a standardized “note” (called JSON) that says:

```json
{
  "function": "get_weather",
  "arguments": {
    "city": "Beijing"
  }
}
```

This note gets received, parsed, and executed by an external program. The one actually calling the weather bureau is the external program, not AI itself. After execution, the result returns to AI, and AI tells you in plain language: “Beijing is sunny today, 15 degrees.”

**Here’s a key twist that beginners often miss.**

Traditional functions are “deterministic” — when a programmer writes `getWeather()` in code, it 100% executes.

But LLM function calling is “probabilistic” — when AI sees “What’s the weather like today?” it has to **decide for itself** whether to call the weather function. This judgment is based on understanding, not rules. There’s a small chance it might judge incorrectly, like interpreting “weather” as someone’s name.

So the essence of function calling is: **Let AI “make calls,” but whether to call and whom to call, it decides for itself.**

![](https://miro.medium.com/v2/0*rytgiqbmSPOYX3n3.png)

This is a huge leap — AI is no longer just a “knowledge base,” it’s becoming an “actor.”

But function calling has a problem: it’s scattered and one-off.

You give AI a dozen functions, but it can only pick one to call each time. If a task requires calling five or six functions in sequence, with logic decisions in between and reference documents needed, function calling isn’t enough.

## The Leap

On October 16, 2025, Anthropic released a new feature: [**Claude Skills](https://support.anthropic.com/en/articles/12512176-what-are-skills)**.

Think of Skills as a combination of an employee handbook and a toolbox.

The employee handbook tells AI: “When you encounter a certain type of task, here’s what to do, how many steps, and what tools to use for each step.” The toolbox contains the scripts and reference materials it needs.

Specifically, a Skill is a folder containing three things:

**First, a SKILL.md file**. This is the “instructions,” written in natural language. It tells AI: what this Skill does, when to use it, how to use it, and what to watch out for.

**Second, scripts**. These can be code written in Python, JavaScript, or other languages. When AI needs to “take action,” it executes these scripts.

**Third, resource files**. Such as reference documents, templates, and configuration files. AI can consult these materials while executing tasks.

You might ask: What’s the essential difference from function calling?

The difference is: **Function calling is a “single tool,” while Skills is a “complete solution.”**

Here’s an analogy. Function calling is like handing you a hammer, a screwdriver, and a wrench — you have to know when to use which. Skills is like giving you a “How to Assemble an IKEA Bookshelf” manual, which not only tells you the steps but also includes all the necessary tools and parts.

There’s another important mechanism called “progressive disclosure.”

AI’s “working memory” is limited (technically called the “context window”). If you dump all Skills content in at once, AI gets overwhelmed.

Skills’ approach is: normally just tell AI “there’s this manual available,” and AI only opens it when actually needed. Like you don’t need to memorize an entire encyclopedia — just look up the relevant page when you have a question.

![](https://miro.medium.com/v2/0*EjEouiPty8tEA9pJ.png)

Now let’s look at all three layers together:

![](https://miro.medium.com/v2/0*2W_XjXkXeMe3886u.png)

Looking from bottom to top, abstraction levels increase. Functions are code-level, function calling is interface-level, Skills is workflow-level.

**Skills can include function calls, but function calls are just part of Skills.**

Like a recipe isn’t just a list of actions like “chop vegetables,” “stir-fry,” and “plate” — it also includes knowledge about “why do it this way,” “how to control the heat,” and “what to do if it burns.”

## In Practice

After all this theory, what can Skills actually do? Let’s look at some real cases.

**First, one of my own projects: [x-article-publisher-skill](https://github.com/wshuyi/x-article-publisher-skill).**

![](https://miro.medium.com/v2/0*I2Sr4zxSPEHYlcgw.png)

If you write articles in Markdown and want to publish them to X (Twitter) Articles, you’ll encounter a maddening problem: copy-paste and all formatting is lost.

Headings become plain text, bold becomes plain text, links become plain text. You have to manually add everything back. Just fixing formatting for one article takes 15–20 minutes.

Even worse are images. You have to manually upload each one, then drag it to the correct position. With a dozen images, it’s easy to mess up the order.

How does this Skill solve it?

It first parses your Markdown file, extracts the title and cover image, and calculates a “block_index” for each content image — that’s which paragraph the image should appear after.

Then it converts Markdown to rich-text HTML and pastes it into the X editor via clipboard. Formatting perfectly preserved.

Finally, it uses browser automation (Playwright) to precisely insert each image at the correct position.

What used to take 20–30 minutes of manual work now completes **fully automatically** in minutes. Beyond the time savings, **for lazy people, not having to lift a finger is what really matters.**

You might say: Isn’t this just an automation script?

Yes and no.

With a plain automation script, you have to remember when to use it, how to use it, and how to fill in parameters. But a Skill puts “when to use” and “how to use” into the instructions. You just tell AI “publish this article to X,” and it knows to invoke this Skill and how to operate.

**This is the value of “knowledge encoding” — turning “I know how to do it” into “AI also knows how to do it.”**

Let’s look at some enterprise scenarios.

**Meeting management**: A Skill can automatically extract summaries, decisions, and action items from meeting notes, then draft follow-up emails. No more spending half an hour organizing notes after meetings.

**Data analysis**: Throw it a CSV file, and it automatically identifies key metrics, finds anomalies, and generates illustrated reports. Non-technical people can quickly extract insights from data.

**Customer support**: It retrieves accurate answers from the company knowledge base, then organizes them into humanized replies. Both accurate and warm.

These scenarios share a common thread: **They’re all highly repetitive tasks with fixed steps but requiring some judgment.** Before, you either muscled through it manually or spent big money developing specialized software. Now, a Skill handles it.

**Finally, developer tools.**

There’s a Skill called `skill-creator` that's particularly interesting—it's a Skill for creating Skills.

![](https://miro.medium.com/v2/0*bhv_H62D5ebJFWmn.png)

You chat with it, describe what workflow you want to implement, and it generates a complete Skill project framework for you. This is what’s called a “meta-skill.”

There’s also `webapp-testing`, which can automatically operate a browser based on test cases, perform functional testing on web applications, then generate test reports. Part of the frontend testing process is automated.

## Getting Started

After all this, how do you start using Skills?

**If you want to use existing Skills**, the simplest way is through Claude Code’s plugin marketplace.

The default auto-install only includes Claude’s official plugin marketplace.

![](https://miro.medium.com/v2/0*FymQmR_k0UD_43c7.png)

You can also add other marketplaces based on your needs. Here’s an example:

- ounter(line
- ounter(line
- ounter(line

```bash
/plugin marketplace add anthropics/claude-code
```

![](https://miro.medium.com/v2/0*MhDohJ7Dk8jNlPWG.png)

After installation, you’ll have two plugin marketplaces.

![](https://miro.medium.com/v2/0*4FtnD5wcYLB8kCDe.png)

As you can see, the `/plugin` command lets you add and manage plugins.

Here are some plugins I’ve already installed.

![](https://miro.medium.com/v2/0*qxTc3hSkP4QMRWI3.png)

After installation, you can ask Claude to complete tasks using a certain Skill. For example: “Use the PDF Skill to extract table data from this document.”

**If you want to create your own Skills**, you can use the `skill-creator` meta-skill. Chat with it, describe your workflow, and it will generate a framework for you.

You can write Claude Skills to help you analyze materials, conduct automated research, and draw corresponding structure diagrams.

For example, here’s a Dream of the Red Chamber character relationship map.

![](https://miro.medium.com/v2/0*kH9W7zpHq2sCFnkr.png)

Below are the interactions among the Seven Warring States.

![](https://miro.medium.com/v2/0*psMsurNzMl8OG9EJ.png)

For usage, [**refer to this article of mine](https://mp.weixin.qq.com/s/edyLjMcarzIrjRi3vsuCPQ)**.

A more advanced approach is using Claude Skills to connect excellent external tools, such as NotebookLM as a knowledge base. This way you can organically combine NotebookLM’s powerful search and knowledge verification capabilities with your own creativity and other model tools’ features.

![](https://miro.medium.com/v2/0*cZpG8Kl4MbO-jMbI.png)

I have [**a detailed introduction in this article.](https://mp.weixin.qq.com/s/lrAeILr8qAJjrMXmnK339g)**

Want to see what Skills others have made? Search GitHub for [**awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)**, where the community has curated excellent Skills.

![](https://miro.medium.com/v2/0*PB4f1Pnf62BUv-Im.png)

I personally recommend the [**plugin marketplace 42plugin](https://42plugin.com/)** created by Huoshui Intelligence (Yang Zhiping’s team).

![](https://miro.medium.com/v2/0*URhGRDUEILitR5hD.png)

Not only does it organize many plugins, but it also has corresponding ratings and scores, which helps avoid pitfalls.

![](https://miro.medium.com/v2/0*Cnf2leFr4z4Mxmdn.png)

The most important point: **Creating Skills doesn’t necessarily require coding ability.**

Instructions in SKILL.md are written in natural language. If your workflow doesn’t involve complex scripts, natural language instructions alone can accomplish a lot.

As Claire Vo said in [**Lenny’s Newsletter](https://www.lennysnewsletter.com/p/claude-skills-explained)**: Even non-programmers can create powerful, reusable AI workflows by clearly defining their workflows.

![](https://miro.medium.com/v2/0*CnJYWVV8jf61Ownf.png)

## Summary

Now let’s look back at these three steps:

- **Programming functions** are the foundation. They provide the most basic and reliable logic execution units.
- **LLM function calling** is the bridge. It transforms AI from just a “knowledge base” into an actor that can “make calls” to drive the external world.
- **Claude Skills** is the blueprint. It integrates scattered tools and instructions into complete workflows, enabling AI to accomplish complex tasks more reliably and professionally. These three layers are converging. Developers continue writing efficient functions as underlying tools; expose tools to AI through function calling; then use Skills to guide AI in using these tools intelligently.

**The real power is: it lets “domain experts” also “teach” AI.**

You don’t need to be a programmer. You just need to understand your workflow clearly, and you can package that knowledge into a Skill. Your expertise no longer exists only in your head — it becomes a capability AI can invoke.

By the way, just as I was writing this article (January 8, 2026), Claude Code released another major update. Skills now support isolated context, hot reloading, specified models, use in sub-agents… [**Plugin Marketplace](https://code.claude.com/docs/en/discover-plugins)** has also officially launched.

![](https://miro.medium.com/v2/0*btWwyTVRX7H7qr07.png)

Anthropic also released Agent Skills specification as an [**open standard](https://aibusiness.com/foundation-models/anthropic-launches-skills-open-standard-claude)** — the same approach they took with MCP (Model Context Protocol), following the open ecosystem route.

Gartner analysts say this marks the AI market’s focus shifting from “model updates” to “use case implementation.”

In plain language: people are no longer just competing on whose model is smarter, but who can use AI better.

Skills is the core carrier of this transformation. It turns AI from a “responder” into a “collaborator.”

Next time someone throws a new Agent-related term at you, ask yourself: Which layer is it on? Is it a code-level tool, an interface-level bridge, or a workflow-level blueprint?

Once you figure that out, new terms won’t be scary anymore.

Have you tried Claude Skills? Have you created Claude Skills that fit your own workflow?

Feel free to share in the comments — let’s discuss together.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [**follow my column](https://wshuyi.medium.com/)** to receive timely updates.

Welcome to [**subscribe to my Patreon column](https://patreon.com/wshuyi)** to access exclusive articles for paid users.

To watch video content, please subscribe to [**my Youtube channel](https://www.youtube.com/@wshuyi)**.

My Twitter: [**@wshuyi](https://twitter.com/wshuyi)**

## Further Reading

- [**Taste or Skills? The Capability Revolution Sparked by ChatGPT](https://mp.weixin.qq.com/s/cSysHNhu24H8dUpKk9XxQg)**
- [**The True Scarce Skill in the AI Era: From Technical Know-How to Insight](https://wshuyi.medium.com/the-most-valuable-skill-in-the-ai-era-414beddba2d6)**
- [**How to Use Claude Skills for Deep Research and Auto-Generated Diagrams](https://mp.weixin.qq.com/s/edyLjMcarzIrjRi3vsuCPQ)**
- [**From Dry Theory to Hands-On Practice: How AI Agents Explain Complex Concepts Through Interactive Tutorials](https://wshuyi.medium.com/from-dry-theory-to-vivid-practice-how-ai-agents-explain-complex-concepts-with-interactive-9f68d82b9ec8)**
- [**New Semester, Set Yourself Up with a Great AI Assistant — One That Thinks, Searches the Web, and Has a Knowledge Base](https://wshuyi.medium.com/new-semester-equip-yourself-with-a-powerful-ai-assistant-capable-of-thinking-connecting-to-the-446e9291e8d7)**
