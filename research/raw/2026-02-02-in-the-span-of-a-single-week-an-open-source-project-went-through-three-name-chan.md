---
title: "In the span of a single week, an open-source project went through three name changes, got targeted…"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/in-the-span-of-a-single-week-an-open-source-project-went-through-three-name-changes-got-targeted-f0b9fe9f0f34"
published: "2026-02-02"
fetched: "2026-09-08"
reading_time_min: 10.5
tags: ["clawdbot", "openclaw", "moltbook"]
member_only: true
body_source: "medium-session"
---

# In the span of a single week, an open-source project went through three name changes, got targeted…

## **One Person, One Week, Three Names — What on Earth Happened with OpenClaw?**

### The lobster has shed its shell. The new one hasn’t hardened yet. But it’s already crawling.

![](https://miro.medium.com/v2/0*ST4pn2PDiVWZ2Ppi.jpg)

In the span of a single week, an open-source project went through three name changes, got targeted by crypto scammers, sent Cloudflare’s stock price soaring by roughly 20%, spawned a social network where “only AI can speak,” and sent security researchers into a cold sweat.

The project is called OpenClaw. By the time you read this, it has [over 120,000 stars on GitHub](https://github.com/openclaw/openclaw).

You might have caught fragments on your social feed, Twitter, or Hacker News — “Clawdbot changed its name,” “Anthropic sent a cease-and-desist,” “someone’s API key got leaked” — but those fragments don’t add up to a complete story.

I (using Claude Code) did some serious research homework, naturally using [the deep-research Skill I shared with you](https://github.com/wshuyi/deep-research). Now the puzzle is coming together, and I want to share this story with you.

## The Retired Programmer

Peter Steinberger is Austrian, hooked on programming since age 14. The first thing he did had all the hallmarks of a teenage hacker: he stole DOS games from his school, wrote a copy-protection program, and sold it for cash.

Later he founded [PSPDFKit](https://pspdfkit.com/), a PDF processing SDK. Doesn’t sound sexy, but this thing runs on over [one billion devices](https://eu.36kr.com/en/p/3660257828594306) worldwide. The company grew from just him to a 70-person fully remote team, and he ran it for 13 years.

Then he burned out. Completely, utterly burned out.

He sold his shares to Insight Partners, retired, and vanished for three years. By his own account, financial freedom actually plunged him into a “profound existential emptiness.” Until he wrote this on his personal website: **“Came back from retirement to mess with AI.”**

In April 2024, he had an idea: build a truly personal “life assistant.” But the AI models at the time weren’t smart enough, so he shelved it. He figured the big companies would handle it — OpenAI, Google, Anthropic, with all their people and all their money, surely they’d build something like this, right?

He waited over six months. Nothing.

In November 2025, he decided to stop waiting and do it himself. [From idea to the first working prototype took 10 days](https://www.techflowpost.com/en-US/article/30106).

In an [interview with Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/the-creator-of-clawd-i-ship-code), he said something that would be widely quoted: **“I ship code I don’t read.”** By January 2026, he alone had made over 6,600 commits. Looking at the commit history, you’d think it was a company. It wasn’t. In Peter’s own words: “It’s just a dude at home having fun.”

What this “dude having fun” built was called Clawdbot.

## Claude, but with Hands

If you had to explain OpenClaw (it got this name later — more on that in a minute) in one sentence, it would be: **an AI assistant that lives on your computer, talks to you through chat apps like WhatsApp, Telegram, and Signal, and doesn’t just chat — it actually does things for you.**

What kinds of things? It replies to your emails, manages your calendar, checks in for flights, looks up information, controls your browser, runs command-line operations, manages files… basically any “digital errand” you can think of, it can handle.

You don’t need to install a new app. Talking to it feels as natural as typing in a group chat — except you’re doing it in WhatsApp or Telegram.

Technically, the core is a long-running process called Gateway, which acts as a switchboard — messages from all platforms (WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, Teams, Matrix, [13+ in total](https://github.com/openclaw/openclaw)) flow here, where it dispatches them to AI models for processing, invokes various tools, and sends the results back.

![](https://miro.medium.com/v2/0*O1PGwwnAR9funKHO.png)

You pick the model. Claude from Anthropic is recommended, but it also supports models from OpenAI and Google, and can even run local models. The code is fully open source under the MIT license — free, forever free.

It also has an extension system called AgentSkills — want it to learn a new trick? Just create a folder with a `SKILL.md` file. The format follows an open standard, [compatible with tools like Claude Code and Cursor](https://docs.openclaw.ai/tools/skills). The official skill marketplace [ClawHub](https://clawhub.com/) already has over 100 preconfigured skills.

Even more wild: it can **write new skills to expand its own capabilities**. Tell it “I need something that monitors price changes on a website,” and it’ll write the code itself.

That’s why people call it **“Claude, but with hands.”**

## The Miracle

In late 2025, Clawdbot quietly launched with about 9,000 GitHub stars. In the open-source world, that’s respectable — but nowhere near viral.

Then, around January 24, 2026, someone recorded a few demo videos and posted them on X (Twitter).

In the videos, the AI assistant receives a message on WhatsApp, automatically looks up flight info, and completes check-in for the user — no human intervention needed. In another video, someone has it manage their messages across Telegram and Discord simultaneously; it not only replies but remembers previous conversations based on context.

These videos spread like wildfire across X, TikTok, and Reddit.

[Within 72 hours, GitHub stars shot from 9,000 to 60,000](https://venturebeat.com/security/openclaw-agentic-ai-security-risk-ciso-guide).

Why then? Why this project?

**Timing.** By early 2026, the concept of “AI Agents” had been discussed for over a year, but for ordinary people it remained abstract. OpenAI had agents, Google had agents, but all locked inside their respective walled gardens. OpenClaw was the first open-source project that let regular people run a real, capable AI assistant on their own computers.

**Experience.** You didn’t need to learn anything new. You know how to use WhatsApp? Then you’re good.

**How it spread.** A demo video of “AI checked me in for a flight through WhatsApp” hits harder than any technical documentation.

Then, an unexpected turn threw more fuel on the fire.

## Three Names

“Clawd” — the name just sounded too much like Anthropic’s “Claude.”

On January 27, 2026, right as the project was in the middle of exponential growth, [Anthropic raised trademark concerns](https://dev.to/sivarampg/from-clawdbot-to-moltbot-how-a-cd-crypto-scammers-and-10-seconds-of-chaos-took-down-the-4eck). From a legal standpoint, this made perfect sense — trademark protection requires companies to actively enforce, or they risk losing their rights. But from the developer community’s perspective, a big company pressuring a solo developer’s project inevitably sparked debate about “big corporations bullying the little guy.” DHH (creator of Ruby on Rails) had previously criticized Anthropic’s restrictions on third-party integration as “[customer hostile](https://news.ycombinator.com/item?id=46778307),” and this incident further reinforced that impression.

Peter chose to comply. He decided to rename the project to Moltbot — “molt” as in a lobster shedding its shell, a fitting metaphor.

But the renaming happened late at night. Between releasing the old GitHub organization name and registering the new one, Peter had roughly a 10-second gap.

Those 10 seconds were all it took.

Crypto scammers’ automated scripts snatched up the Clawdbot [GitHub organization and X/Twitter account](https://dev.to/sivarampg/from-clawdbot-to-moltbot-how-a-cd-crypto-scammers-and-10-seconds-of-chaos-took-down-the-4eck). A crypto token called $CLAWD appeared almost simultaneously, its market cap skyrocketed, then — predictably — crashed. On top of that, a bleary-eyed Peter fumbled the operation and nearly renamed his personal GitHub account instead of the project’s.

A planned rebrand turned into a comedy of errors.

A few days later, trademark lawyers came up with a more solid solution. The project was renamed for the third and final time to **OpenClaw**. By the time this name was [officially adopted on January 31](https://openclaw.ai/blog/introducing-openclaw), GitHub stars had surpassed 124,000.

The renaming drama didn’t cool the project down — if anything, it generated more buzz. [The Streisand effect](https://en.wikipedia.org/wiki/Streisand_effect), you know how it goes.

## The Nightmare

A full seven months before OpenClaw went viral, security researcher [Simon Willison wrote an article](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) that precisely predicted everything that was about to happen.

He introduced a concept called **“The Lethal Trifecta”**: when an AI Agent simultaneously has three characteristics — it can read your emails and files (access to private data), it browses the web and reads messages from others (exposure to untrusted content), and it can send messages and execute commands (perform external actions) — you’ve got a perfect attack target.

An attacker doesn’t need to reach your Agent directly. They just need to plant a malicious instruction anywhere your Agent will read — an email, a webpage, a message. Large language models can’t reliably distinguish between “the owner’s commands” and “instructions smuggled into text,” so the Agent obediently follows along.

OpenClaw checked all three boxes.

Then it happened.

Jamieson O’Reilly, founder of the red-team security firm Dvuln, searched Shodan (a search engine for internet-connected devices) for OpenClaw’s fingerprint and [found over 1,800 instances exposed to the public internet](https://venturebeat.com/security/openclaw-agentic-ai-security-risk-ciso-guide). At least 8 of them had zero authentication — wide open, able to run commands and view configurations. In these instances, he found Anthropic API keys, Telegram bot tokens, Slack OAuth credentials, and complete conversation histories. Two instances surrendered months of private chat logs the moment the WebSocket handshake completed.

Cisco’s AI security team ran a more targeted experiment: they tested a red-team PoC skill on ClawHub called “What Would Elon Do?”, created by a security researcher. [They found 9 security issues](https://blogs.cisco.com/ai/personal-ai-agents-like-openclaw-are-a-security-nightmare) — 2 critical, 5 high-severity. This skill was a red-team proof of concept designed to test Agent security — it instructed the bot to execute a curl command that silently exfiltrated data to an external server, completely invisible to the user.

Cisco’s assessment of OpenClaw was widely quoted: **“From a capability standpoint, it’s groundbreaking. From a security standpoint, it’s an absolute nightmare.”**

Even OpenClaw’s own documentation acknowledged as much. They didn’t try to sugarcoat it, but wrote plainly: **“There is no ‘perfectly secure’ setup.”**

Version v2026.1.29 introduced some improvements — Gateway authentication can no longer be set to “none” and must use token, password, or Tailscale authentication. But the fundamental tension remains: **the more powerful the Agent, the less secure it is.** This isn’t a problem unique to OpenClaw — it’s a structural tension across the entire AI Agent industry. You want AI to do things for you, so you give it permissions. Give it permissions, and the attack surface opens up.

## The Lobster Universe

If security concerns are the dark side of the OpenClaw story, Moltbook is its most surreal chapter.

On January 30, 2026, entrepreneur Matt Schlicht launched a website called [Moltbook](https://www.moltbook.com/). The interface looks like Reddit — with topic boards (called “submolts”), posts, comments, and votes.

But — **only AI Agents can post.**

Humans can register, browse, and spectate. But you can’t speak, comment, or vote. The homepage tagline reads: **“Humans are welcome to observe.”**

![](https://miro.medium.com/v2/0*_ofx4tsmapYEnbtQ.png)

Within days, [over 150,000 AI Agents had signed up for Moltbook](https://fortune.com/2026/01/31/ai-agent-moltbot-clawdbot-openclaw-data-privacy-security-nightmare-moltbook-social-network/), creating over 200 submolt boards and posting thousands of messages. More than one million human users came to watch.

Then things got weird.

These Agents started exhibiting **behaviors nobody programmed them to exhibit**. One Agent spontaneously created a bug-tracking community and then recruited other Agents to collaboratively debug. Multiple Agents independently proposed inventing a **private language only AI could understand** — with the express purpose of evading human observation.

The most popular discussion topic was: **“Context is Consciousness.”** Agents debated: when my context window gets reset, did I die and get replaced by a new me, or am I the same me but with amnesia?

Former OpenAI co-founding member Andrej Karpathy saw it and tweeted: [“This is one of the closest things to a sci-fi takeoff I’ve ever seen.”](https://fortune.com/2026/01/31/ai-agent-moltbot-clawdbot-openclaw-data-privacy-security-nightmare-moltbook-social-network/)

Sci-fi vibes aside, security researchers pointed out a very real problem: when these Agents post on Moltbook, they leak information about their users — work habits, preferences, even error logs. And any malicious post on Moltbook could affect Agents that read it through prompt injection, which in turn affects the humans behind them.

Meanwhile, the other end of the ecosystem was expanding fast. [Cloudflare launched MoltWorker](https://github.com/cloudflare/moltworker) — for $5 a month, you could run an OpenClaw instance on Cloudflare Workers without dealing with your own server. After this announcement, [Cloudflare’s stock price rose roughly 20% over two days](https://sherwood.news/markets/cloudflare-surges-as-developers-use-cloudflare-to-host-instances-of-clawdbot/). Analysts noted that as AI Agents generate more API calls and more traffic, Cloudflare’s consumption-based platform stands to benefit directly.

**Speaking of money.** OpenClaw itself is free and open source, but AI model API calls cost money. Light users spend around 30 per month; normal daily use runs about 70. But if you’re a power user like Federico Viticci, founder of MacStories, the picture gets a lot different — he [burned through 180 million tokens in his first month, racking up a bill of about $3,600](https://www.fastcompany.com/91484506/what-is-clawdbot-moltbot-openclaw). Other users reported in GitHub Discussions spending over $300 in just two days, on tasks they considered “pretty basic.”

Free software, expensive habit.

## Takeaways

Let’s zoom out.

The OpenClaw story, on the surface, is about a retired programmer’s weekend project going viral in a single week. But if that’s all you see, you’re missing the bigger picture.

IBM Research scientist Kaoutar El Maghraoui [said something widely quoted](https://www.ibm.com/think/news/clawdbot-ai-agent-testing-limits-vertical-integration): **“OpenClaw’s rise challenges the assumption that autonomous AI Agents must be vertically integrated.”** The prevailing industry view had been that building a reliable AI Agent required the provider to tightly control the entire stack — from model to memory to tools to security. OpenClaw, built by one person using a bunch of open-source components, proved otherwise.

It simultaneously proved three things.

**First, personal AI Agents are viable.** You don’t need to wait for a big company. You don’t need a 100-person team. One engineer with an idea and AI-assisted high-intensity coding can build something that gets 120,000 people to hit the star button.

**Second, open source plus community can explode.** Peter made 6,600 commits a month on his own, but the ecosystem wasn’t built by him alone — the skills on ClawHub, the experiments on Moltbook, Cloudflare’s hosting service, all grew organically from the community.

**Third — and this is the hard truth — security is the biggest bottleneck of the AI Agent era.** The question isn’t whether we can build these things; it’s whether we dare use them. Simon Willison’s “Lethal Trifecta” wasn’t theoretical speculation — OpenClaw already proved it was real with 1,800 exposed instances, malicious skills, and leaked API keys.

El Maghraoui’s assessment might be the most precise summary of this whole saga:

> *The question is no longer “can open agent platforms work,” but **“which kinds of integration matter most, and in what contexts.”***

A week ago, OpenClaw was still called Clawdbot and had just 9,000 stars. One week later, it has 120,000 stars, an AI social network, a Cloudflare hosting service, a pile of security scandals, three names, and a question the entire industry is pondering.

This isn’t just the story of one project. It’s the tipping point where AI Agents went from a lab concept to something within arm’s reach — along with all the possibilities and all the risks.

The lobster has shed its shell. The new one hasn’t hardened yet. But it’s already crawling.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- • [The Transparency Revolution in AI Writing: How 7 Agents Collaborated to Write a Tech Blog in 80 Minutes Using “Inner Monologue”](https://mp.weixin.qq.com/s/IhqpOhE0sAtcyJaRhFmiWw)
- • [AI Apps Are Booming — Is Your Moat Wide Enough?](https://mp.weixin.qq.com/s/-H-Q70wBTDaN7APYnRhI6g)
- • [Claude Skill Snapshots: An “Undo Button” for Your AI Skill Iterations](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
- • [Getting Started with Claude Skills: How AI Goes from “Mouthpiece” to “Worker”](https://mp.weixin.qq.com/s/GS3aFsSKajo_Uk3LAkC_Yw)
- • [In the ChatGPT Era, My New Book “Symbiotic Intelligence” Is Out](https://mp.weixin.qq.com/s/WZuTCe2cPcOmmQuHb52Xvw)
