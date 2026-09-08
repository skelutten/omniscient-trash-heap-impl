---
title: "How to Build a Research Radar That Watches the Literature for You Every Day Without Writing a Line…"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/how-to-build-a-research-radar-that-watches-the-literature-for-you-every-day-without-writing-a-line-5228192e9bd5"
published: "2026-09-01"
fetched: "2026-09-08"
reading_time_min: 19.0
tags: []
member_only: true
body_source: "medium-session"
---

# How to Build a Research Radar That Watches the Literature for You Every Day Without Writing a Line…

## **How to Build a Research Radar That Watches the Literature for You Every Day Without Writing a Line of Code**

### In the age of human-AI collaboration, if you **can state your needs, can sign off on the results, and are willing to make the call**, you already have everything it takes to build an intelligent system of your own.

![](https://miro.medium.com/v2/0*zpkrhhPH6il-qgUq.png)

## Where This Started

A while back, a friend who studies water-saving irrigation in smart agriculture came to me and vented.

He wanted to keep a close eye on four emerging research areas in his field: water-saving irrigation technology, irrigation decision-support models, factors affecting fertilizer use efficiency, and crop phenotyping applications, plus five core journals and three leading scholars. But those papers are scattered across databases and journal websites. By hand, a daily sweep was out of the question; even a disciplined once-a-week pass would eat most of a day and leave him bleary-eyed.

You may have been there yourself. Whether you’re preparing a research proposal, writing a literature review, or doing research support as a subject librarian, **keeping up with the literature is a basic skill nobody gets to skip, yet it usually turns into the most tedious kind of grunt work**. Every few days you type the same keywords again and sift through the results one by one, by hand.

The commercial literature-monitoring platforms out there work well enough, but their steep annual fees are out of reach for individuals and small startup teams. And when it comes to building one yourself, most people’s first reaction is: “I’m not a computer science major. I can’t even write code. How am I supposed to build something like that?”

So the idea usually gets stuck somewhere between wanting it and having it.

I built this friend a low-cost automated monitoring system. It went live in late spring this year, and by August 20 it had quietly collected 5,200+ papers, nearly five thousand of which AI had distilled, one by one, into Chinese summary cards. All of it feeds a visual dashboard with a knowledge graph and trend alerts, refreshed every morning like clockwork.

![](https://miro.medium.com/v2/0*MuNgbgnScGtNxDaN.png)

*Caption: The “Agri Paper Radar” dashboard’s statistics overview as of the August 20 crawl: 5,219 papers in the database, 4,964 summarized, with charts of monthly paper volume, the share of each of the four research directions, source journals, and the 12 most prolific authors.*

Recently I’ve been running a workshop for the librarians at Sun Yat-sen University Library. When the pre-course questionnaires came in, what people wanted most was exactly this: a paper collection that keeps growing on its own, a visual dashboard, and real data analysis. In the hands-on sessions that followed, participants not only got the prototype running but turned up plenty of practical lessons and insights none of us expected.

![](https://miro.medium.com/v2/0*KvyNXrLD4kyXcIDh.jpeg)

In this post I’ll take the whole system apart for you: how it’s built, the lessons from where it broke, how it has evolved, and **the ready-to-use tool I’ve packaged for you**.

## The Real Barrier

Many people hear “automated literature tracking” and immediately picture crawler frameworks, vector databases, distributed schedulers, and a pile of other jargon that makes their heads spin.

A few years ago, that really was a wall too high to climb. But in the era of large language models, the real barrier has long since moved: **the hard part isn’t building it; it’s spelling out what you want to watch**.

My friend and I spent far more energy mapping out the “watch list” than building the system itself. Which four sub-areas? Which five journals? Which three scholars? Those are expert judgments only someone truly immersed in the field can make. Once they’re thought through, they go into a simple configuration file and become the brain of the whole system.

As for the technical underpinnings, you might find this hard to believe: a free academic data API, a single-file database, a large language model called as if it were a function, a pile of static web pages, plus an alarm clock that fires on schedule.

No expensive rented servers, no complex distributed architecture. Five perfectly ordinary, everyday parts snapped together into a research radar that runs itself every day.

## Collecting the Papers

The first step in building the radar is solving the upstream problem: where do the papers come from, and where do they go once fetched?

For the data source, we chose [OpenAlex](https://openalex.org/) as the workhorse. It’s an open, free scholarly metadata platform with extremely broad coverage, and fields like title, abstract, authors, and citation counts are all available through an open API. Register for a free API key and you’re set; the free quota is more than enough for personal monitoring. Of the five journals my friend specified, four can be tracked directly in OpenAlex by journal ID, and the four research areas can be pulled live from the full index by search terms.

The remaining one, the Chinese journal *Smart Agriculture* (智慧农业), isn’t indexed in OpenAlex yet, so we filled the gap through [DOAJ](https://doaj.org/), the Directory of Open Access Journals.

You might be wondering: why not crawl the more authoritative commercial databases, or scrape the journal websites directly?

The answer is plain: **an automated system lives or dies on compliance and stability**. Take Clarivate, the owner and operator of Web of Science: its terms of use explicitly prohibit unauthorized programmatic harvesting. And some Chinese journal websites have strict anti-scraping mechanisms; a script that so much as visits gets a 403 error. For individuals and research teams, free, compliant, open data APIs are the only option that will keep running smoothly over the long haul.

Where does the data live? The entire system runs on nothing but a single-file **SQLite** database.

I’ve taught database courses for many years, and I keep telling my management students: for a small system at the personal or lab-group level, there’s really no need to go to the trouble of setting up a heavyweight database server. Think about it: plenty of the apps on your phone store their local data in SQLite. A single-file database needs no installation and zero configuration; copy the file and you have a full backup. It’s remarkably sturdy.

One design principle matters even more: **the ingestion stage never touches AI**. Ingestion just pulls data and writes it to the database. Keeping the front of the pipeline simple and clean means that even if the LLM service downstream occasionally times out or throws errors, papers keep landing in the database without interruption.

## Digesting the Papers

Once data flows steadily into the database, step two is getting AI to help digest it.

Until now, the way most people have read papers with AI is to open a chat window, drop in a PDF or an abstract, and go back and forth. That works for close reading of key papers, but with new literature pouring in every day, if you’re still doing it one chat at a time, neither you nor your wallet can keep up.

Our solution: **call the large language model as a deterministic processing function**.

Calling it as a function means nailing down the input and output formats completely: the input is always “paper title + abstract,” and the output must be a strict five-field JSON object, extracting a one-line summary (tldr), the key method (method), the main finding (finding), the research area it belongs to (direction), and an opportunity for further work (opportunity). When it runs, how many papers it handles per day, which database field the result is written back to: all of that is wired together by code, with no human in the loop.

The prompt template we actually use in the system is very lean. Here it is as-is, with only the domain terms swapped for placeholders like “XX” so you can drop in your own field:

```typescript
​
You are a research assistant in the field of XX. Below are the title and abstract of a paper.
​
Output strict JSON in Simplified Chinese, with the following fields:
- tldr: one sentence on what this paper did (no more than 50 characters)
- method: the key method / data / technique used (no more than 40 characters)
- finding: the most important finding or conclusion (no more than 50 characters)
- direction: choose the single best fit from ["XX technology","XX decision-support methods and models","factors affecting XX use efficiency","XX applications","Other"]
- opportunity: one sentence useful for finding a research direction: a research gap / opportunity worth extending (no more than 60 characters)
Output only the JSON object, with no extra text.
​
Title: {title}
​
Abstract: {abstract}
​
```

Every paper that passes through this pipeline comes out as a cleanly structured card.

![](https://miro.medium.com/v2/0*cdsRcVlNd9RB_lYB.png)

*Caption: One AI-generated summary card. The tag reads “water-saving irrigation technology”; below the English title and authors, the four Chinese fields give the one-line summary, the method, the key finding (properly installed and maintained micro-irrigation saves 30–50% of water and raises yields 20–40%), and a research opportunity.*

For the model backend we hooked up Zhipu AI’s GLM series (recently upgraded to 5.3, the newest version our subscription covers). But this layer isn’t picky about models at all; plug in whichever LLM API you already subscribe to.

Beyond the per-paper cards, the system also periodically aggregates recent papers within each research area and has the model write a “trend brief” of a hundred words or so: What specific sub-problems is current research focused on? How are the mainstream methods evolving? Which gaps remain unfilled? The single-paper cards help you decide whether a paper deserves a close read; the trend briefs help you see the big picture.

![](https://miro.medium.com/v2/0*FCdGnUHgBBSf3FjG.png)

*Caption: The dashboard’s “trend alert” tab: a four-point AI-written brief (nutrient management papers up 129×, potassium and phosphorus heating up fast, computer vision and organic fertilizer still small but promising), a list of keywords on the rise, and collapsible per-direction trend digests.*

## The Dashboard

With the data processed, how do you present it in a way that’s pleasant to look at?

The dashboard’s evolution is a vivid illustration of **prototype thinking** in information systems development.

When I teach information systems development, I keep stressing to students: never start by designing some huge, complex system behind closed doors, signing off on requirements with the user and then vanishing for half a year, only to hand over something at the end of the semester that leaves the user bewildered. The safer approach: **build the smallest working prototype first, MVP-style, get the data flowing, and keep iterating on something you can see and touch**.

The first version of this system was honestly crude: just a card list split into columns by research area. Only after the papers in the database passed a thousand did we gradually add four in-depth analysis modules to the dashboard: a statistical overview, a keyword co-occurrence graph with 42 nodes, a tracker for hot terms that have surged over the past six months, and an AI-written trend-alert brief.

![](https://miro.medium.com/v2/0*VpJ_xQDTgbRmWt2d.png)

*Caption: The keyword co-occurrence graph. Node labels are in Chinese (deep learning, yield, climate, remote sensing, NDVI, drones, soil moisture, drought, water use efficiency, and so on); node size reflects frequency and colors mark clusters.*

Technically, the dashboard is a **purely static web page**. Each day, once the pipeline finishes running the analysis scripts, it generates HTML files with the data embedded directly. This architecture needs no backend server sitting around listening, is extremely lightweight, and lays the groundwork for the zero-cost deployment that comes next.

## Deployment

Getting it running on your own machine is just for your own amusement. The system only creates real value when researchers can open it anytime, anywhere, on a phone or a computer.

Many tutorials like this get stuck at deployment: the overseas hosting platforms they recommend are great, but direct access from within China is often difficult. Our strategy is “build once, publish on two tracks”:

One track pushes to [Cloudflare Pages](https://pages.cloudflare.com/), taking advantage of its global CDN for stable distribution; the other goes to “Studios” on [ModelScope](https://www.modelscope.cn/) (魔搭社区), Alibaba’s open-source model community, where you can create a static space for free, upload the web files, and get a public link with fast, direct access from within China.

Add a scheduler, and the entire pipeline fires at 7:30 a.m. every day: fetch new papers, call the model, update the graph dashboard, push to both hosting platforms, and, while it’s at it, deliver the day’s brief to your phone.

Let’s do the math: the data API stays within its free quota, the database is maintenance-free, static hosting costs nothing, and the only real money spent is the LLM’s daily tokens, which on our side ride on an existing subscription, so the marginal cost is zero. What’s truly expensive isn’t money; it’s the time spent up front mapping out the watch list. But you do that once, whereas a commercial platform’s annual fee comes due every single year.

With the method I share below, you can easily deploy a literature monitoring site of your own. Here’s a sample: [click this link](https://wshuyi-agentic-assessment-workbuddy-workbuddy-glm5.ms.show/) or scan the QR code below to take a look.

![](https://miro.medium.com/v2/0*nXZc1kdTA4zAGo5_.png)

## Where It Broke

So far this sounds like smooth sailing, but over two-plus months of real operation, the system taught us three hard lessons:

**Lesson one: you have to check the limits of free data sources yourself.**

During spot checks shortly after launch, we found two bugs that were equal parts funny and exasperating. First, the source records for *Transactions of the Chinese Society of Agricultural Engineering* (农业工程学报), one of our subscribed journals, had a coverage gap in OpenAlex around 2020. The second was even wilder: when fetching papers by Kang Shaozhong, an academician of the Chinese Academy of Engineering, the database tagged this top expert in agricultural soil and water engineering as affiliated with “Huawei Technologies.” Whether the upstream metadata was wrong or the institution matching went astray, we’ll never know.

![](https://miro.medium.com/v2/0*OQSFa2hBmMRuIkp2.png)

*Caption: The OpenAlex record (W4386910800) for a 2023 paper in the Journal of the Science of Food and Agriculture: all seven authors, academician Kang Shaozhong included, are tagged “Huawei Technologies (China); China Agricultural University.” The red note at the bottom warns that open databases’ institution fields can be wrong, so key data still needs manual spot checks.*

The takeaway: **open databases have rich metadata, but they can’t reliably identify people, and they make no guarantees**. If you’re going to use this for rigorous subject analysis in research support, you still have to pull out the handful of records that matter and check them yourself.

**Lesson two: automated systems die quietly.**

In late June, the system went silent for 13 days. No error, no alarm, no exception notification. The scheduled task had simply been disabled by accident during a debugging session, and it was almost two weeks before I happened to open the dashboard and noticed the flow had stopped. We scrambled to backfill 333 papers overnight. In mid-July it stalled briefly again, this time because of an underlying gateway update and an expired authentication token.

The lesson: **automation does not mean hands-off**. Systems tend to fail when they’re at their quietest. Getting into the habit of checking the dashboard’s last-updated timestamp regularly is the most basic checkup in system maintenance. And maintenance really doesn’t take much: glance at the timestamp at the top of the dashboard once a week, two minutes; pull a dozen or so cards once a month and check the institution and journal fields, half an hour tops. That’s the “minimum monthly rent” any fully automated system has to pay.

**Lesson three: LLM rate limits quietly pile up debt.**

The LLM we call has concurrency and rate limits, so to keep the pipeline from timing out we initially capped summaries at 45 papers a day in the config file.

In practice, though, the daily searches across several research areas brought back well over a hundred new papers a day. Wide pipe in, narrow pipe out: dozens of “undigested” papers a day snowballed. It wasn’t until the August 20 tally that we realized the database held 5,200+ papers, only 2,100+ of which AI had summarized, leaving a backlog of nearly three thousand. We raised the daily cap from 45 to 150 and ran a separate catch-up pass, clearing 2,800+ that same day and essentially wiping out the backlog. The nearly five thousand cards you saw at the start came from exactly that.

![](https://miro.medium.com/v2/0*T34Ye205A9-z8yuu.png)

*Caption: The “backlog debt” curve from the system’s own database, June 10 to August 25: cumulative papers ingested (blue, 5,736) versus cumulative papers summarized (green, 5,473), with the shaded gap showing the snowballing backlog. The annotations mark the August 20 stocktake (nearly 3,000 papers behind) and the same-day catch-up run of 2,828 summaries after the daily cap was raised from 45 to 150.*

In other words, **any stage in an automated pipeline where input outruns output is a system debt waiting to surface**.

## A Pleasant Surprise

In the recent workshop, the librarians at Sun Yat-sen University Library and the trainee teaching assistants tested this tool on their own real-world use cases. They not only validated the workflow but stumbled onto something none of us saw coming.

During testing, one librarian had WorkBuddy try connecting to Sun Yat-sen University’s internal database to download papers, an impromptu side test outside the radar’s main pipeline. Because we had uploaded a Sun Yat-sen University Library user manual to WorkBuddy during the previous day’s training, the AI, before executing the bulk-download instruction, **went and consulted the manual on its own**.

In the manual it read the criteria for “excessive downloading” violations and the account-suspension clauses. So instead of carrying out the instruction straight away, it stopped first and walked the librarian through, item by item, the red lines that bulk downloading might cross and the risk of being banned.

Watching the AI **read the rules on its own and treat them sensibly as boundaries** genuinely impressed the librarians in the room. It made me more certain of one thing: **when you give AI permissions, you have to hand it the rules at the same time**. A traditional crawler can’t read a manual; every red line has to be written into the code by a human. This AI assistant read the manual itself and knew on its own when to hit the brakes.

## Bottlenecks

Of course, once people got deep into hands-on use, they were also blunt about the current prototype’s many pain points. The feedback was candid, and it captures exactly the growing pains a system must go through on the way from “toy” to “productivity tool”:

The first thing they ran into was resource access. Interestingly, the AI is proactive about following rules but passive about finding ways forward: when both open access (OA) and institutional database resources are configured, it tends to take the easiest OA route, and once it hits a permission barrier, it lacks the resilience to switch on its own between the institution’s licensed channels and OA, or to retry through multiple channels.

That’s not all. What made the subject librarians shake their heads even more was the search strategy: fishing for papers with fixed keywords is still too mechanical. It doesn’t adjust the search expression dynamically based on results the way a professional information specialist would, or fall back on synonym expansion and controlled vocabularies, so it’s prone to letting things slip through the net, or drifting further off target with each pass.

What really holds it back, though, is deep full-text processing: although some papers’ full texts were obtained, the dashboard doesn’t yet actually take them apart. The charts still stop at macro statistics like publication dates and journal distribution, while high-value findings such as experimental data and comparisons of technical approaches haven’t been properly extracted.

## The Road Ahead

In response to the bottlenecks exposed in practice, the workshop groups proposed the next round of upgrades on the spot. One caveat first: everything below is still on the drawing board and is not in the current version of the skill.

First, **rebuilding the pipeline’s evidence layer**: borrowing the paper-access and search-strategy pieces that mature Agent Skills for literature-based writing, systematic literature reviews, and deep research have already solved, and embedding them deep in the dashboard backend. The LLM would no longer just hand you a vague one-liner; it could pull facts from the body text and back every trend judgment on the dashboard with a tight chain of evidence.

Second, **human-AI collaborative search**: bringing in the deep-research mechanism so the AI helps researchers iteratively expand their search strings, boosting relevance substantially while preserving recall.

Third, **broadening the range of settings it can serve**: the current architecture, built on a single file and lightweight APIs, is best suited to a **customized research radar for an individual scholar, a lab group, or a startup team** (handling hundreds to thousands of papers). Scaling it up into something a university library runs for an entire college, a big-picture subject briefing service backed by tens of thousands of papers, would require further exploration in institutional access integration, high-concurrency distributed computing, and knowledge service systems.

## Ready to Use

By now you may be wondering how on earth you’re supposed to set all of this up (the fetching, parsing, summarizing, charting, and generating scripts) on your own computer.

So that you can use this approach with zero barrier to entry, I’ve packaged the complete workflow distilled from all the development and tuning into a standalone Agent Skill: **Instant Paper Radar (`instant-paper-radar`)**. Think of an Agent Skill as an assignment brief written for an AI: you bundle up the full set of rules, steps, and templates for a job, hand it over, and the AI follows it.

You don’t even need to write the config file by hand. Before you begin, you need just three things: an AI environment that supports Agent Skills (Codex or [WorkBuddy](https://www.workbuddy.cn/events/invite?inviteCode=cxdprramd), for example), an LLM API key (whichever provider you subscribe to, or one with a free tier), and the skill package itself. The Feishu (Lark) document below has the download and installation steps.

![](https://miro.medium.com/v2/0*He_o5_k_rWaTY45V.png)

*Caption: The Feishu document “instant-paper-radar · Instant Paper Radar Skill Share.” It describes the skill (one sentence in, an offline paper-analysis dashboard out, built from OpenAlex and DOAJ with five-field cards, trend briefs, and a keyword graph) and gives the installation steps: download the attached zip and ask your AI agent to install it.*

Once you load the skill in such an environment (Claude Code, OpenClaw, [WorkBuddy](https://www.workbuddy.cn/events/invite?inviteCode=cxdprramd), and so on), all you need is one sentence in plain language:

> *“Build me an Instant Paper Radar dashboard on ‘applications of large language models in education.’”*

The skill then kicks off the entire pipeline automatically:

First, **automatic config generation and parsing**: based on your topic, the AI first drafts two to four sub-areas and candidate lists of journals and scholars, and generates the corresponding English search terms. Note that this is only a first draft. Which areas are truly worth watching, which journals carry credibility: that still needs you, the domain insider, to look it over and nod, or cross it out.

Second, **fully automated pipeline execution**: fetch the papers, clean the data, and generate the five-field cards and per-area trend briefs through a sandboxed prompt template.

Third, **instant single-file dashboard output**: it computes the keyword co-occurrence network, pulls out emerging hot topics, inlines a lightweight charting engine, and within minutes delivers a complete, interactive HTML dashboard that opens offline with a double-click.

I’ve organized the skill package download, installation steps, and detailed usage instructions into a Feishu document for you. Just grab what you need:

👉 O**nline documentation:** I[nstant Paper Radar User Guide (Feishu document)](https://www.feishu.cn/docx/O77JddWmyop6EyxwRyicqgrsnmd)

If you’re on your phone, you can also save the QR code below and scan it anytime to read the guide and get set up:

![](https://miro.medium.com/v2/0*DsehvtK-v0y3flXx.png)

## From Snapshot to Standing Radar

With the skill packaged up, moving the research radar to a new field becomes remarkably painless: **you don’t even have to edit a single JSON config file by hand, just say a different sentence in the prompt**, and the AI handles the tedious execution steps like building search expressions and cleaning data.

Better still, this Instant Paper Radar gives you a smooth **upgrade path**:

Step one, instant validation: drive the skill with a single sentence and, within five minutes, get a retrospective snapshot of a field’s literature, so you can first check whether the search areas are on target and whether the current hot topics match your expectations.

Once you’re happy with the topics and results it produces, take step two and upgrade it into a standing radar that “pushes a daily digest at 7:30 every morning.” The `config.json` and `export.json` the skill generates locally are exactly the handoff blueprint you need. [WorkBuddy](https://www.workbuddy.cn/events/invite?inviteCode=cxdprramd) has scheduled-task capability built in. Hand those two config files back to it, tell it "deploy on the two-track plan from the Deployment section above and run once every morning at 7:30," and the next morning it can start running on its own.

![](https://miro.medium.com/v2/0*nYyT6FyPb4SK7IU2.png)

*Caption: WorkBuddy’s “Scheduled Tasks” tab, with the “Add automation” button highlighted in red above a grid of automation templates (daily AI news, weekly work report, and so on). This is where the radar’s 7:30 a.m. daily run gets set up.*

Validate the idea with a dirt-cheap instant snapshot first, then turn the proven configuration into a long-term asset. That may be the most effortless research workflow the Agent era has to offer.

## Wrapping Up

Since the day I first built this system, one conviction has only grown stronger:

> ***Don’t treat owning an automated system of your own as some far-off feat of software engineering. At its core it’s a thinking exercise: stating your professional needs to AI precisely.***

Free data APIs, a single-file database, a model API called as a function, static web pages, automated scheduling, and now a packaged Agent Skill on top: every part is within easy reach. What’s truly scarce and irreplaceable in this process is your deep insight into your own academic field: **which research areas are worth tracking, which journals are credible, and how to evaluate and sign off on the analysis AI gives you**.

In the age of human-AI collaboration, if you **can state your needs, can sign off on the results, and are willing to make the call**, you already have everything it takes to build an intelligent system of your own.

Starting today, stop letting the “I can’t code” voice in your head hold you back. Pick an AI assistant you’re comfortable with, load the Instant Paper Radar skill, spell out your research monitoring needs clearly, and start tracking the literature automatically, on your own terms.

Once you’ve tried the skill, let me know how it went in the comments. I’d love to compare notes.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- [Can You Trust AI With a Literature Review? On Building a Research Workflow That Doesn’t Go Off the Rails](https://mp.weixin.qq.com/s/-wchS6BmYj8z71BZJYnY8A)
- [Local AI + Automatic Capture: Build a Knowledge Management System of Your Own](https://wshuyi.medium.com/local-ai-automated-capture-building-your-own-knowledge-management-system-bbe583006927)
- [How to Have AI Build Your Zettelkasten Automatically](https://wshuyi.medium.com/how-can-ai-help-you-automatically-build-a-zettelkasten-78eca636fc73)
- [If AI Does the Research and Writes the Paper End to End, Can You Publish It Under Your Name?](https://mp.weixin.qq.com/s/WtHbftFwtpF4JtbFxNa8cA)
- [How to Use Custom Prompts in Readwise Reader to Have AI Process Information for You](https://wshuyi.medium.com/how-to-customize-prompts-in-readwise-reader-to-automate-information-processing-fbf71906179e)
