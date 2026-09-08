---
title: "Why I Tore Down the AI Meta-Skill I Spent Months Building"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/why-i-tore-down-the-ai-meta-skill-i-spent-months-building-ab96d61c5ec1"
published: "2026-09-08"
fetched: "2026-09-08"
reading_time_min: 14.4
tags: ["gpt-6", "harness-engineering"]
member_only: true
body_source: "medium-session"
---

# Why I Tore Down the AI Meta-Skill I Spent Months Building

The scaffolding that saved a weaker model can choke a stronger one.

![](https://miro.medium.com/v2/0*9kBkO6VtYJ-QKvVo.png)

## Rigidity and Flexibility

A few months ago, I [built a Skill dedicated to managing how AI does its work, and I was thrilled about it at the time](https://mp.weixin.qq.com/s/FY1DTSQ-Kpugs7NQIkDU9g).

Think of a Skill as a set of work instructions you can call up again and again. You put the requirements, the method, and the checks for a given job into it, and whenever the AI gets that kind of task, it follows along, so you don’t have to spell everything out from scratch each time.

![](https://miro.medium.com/v2/0*PVGptU8rkzF81ZSZ.png)

The Skill I built could be called a meta-skill, because what it governs is something more fundamental: keeping the model from cutting corners and shortchanging the task. Otherwise it seems to agree to everything readily enough, then hands back work with pieces missing.

Say you ask it to do a research report. It can’t just dig up a few sources and jump to conclusions. What exactly is being compared, whether the material still applies, whether there are counterexamples to the reasoning, whether the facts in the report can be traced to a source: all of that has to be accounted for.

I wanted to cover as many of the requirements I could think of at the time as possible, and put them into a reusable set of rules.

![](https://miro.medium.com/v2/0*o-FD9g6vKHX3l9yJ.png)

Writing “please do this carefully” obviously wouldn’t cut it. I named the whole arrangement “Gangrou,” Chinese for “rigid and flexible.” Looking back through the now-archived documentation, its core is a `graph.json` file: the steps, contracts, and constraints of a complex job, written out as a graph a program can read. This is called a graph IR; think of it as a map of how the steps relate, one that can both guide execution and serve as the basis for a retrospective.

It does just two things. The first is to follow that step map and carry the work out one step at a time. The graph has a class of “controlled nodes”: contract gates that check whether mandatory requirements have been met, plus steps explicitly designated as mandatory.

The executor launches subprocesses to actually run these nodes, then judges the results against rules written in advance. A simple “I’m done” from the model doesn’t count as a pass. Rework loops have a cap too; there’s no retrying forever.

Beyond that, the method layer is left to the model: how to read the material, which approach to take, how to adjust the plan. All of it can change with the task, and the process gets logged. **Hold the line on what must be delivered; leave room to choose how it gets done.**

The second thing is viz, the post-run review. It reads the graph and the run log and renders them as an HTML page, so you can see how the job unfolded. What it checks is whether the graph’s structure, representation, and rendering are correct; it doesn’t pass judgment on the quality of the task itself. The diagram below, simplified and redrawn from the archived original, shows this whole mechanism.

![](https://miro.medium.com/v2/0*T7v81gDIcqZgcpq_.png)

Take the [Deep Research workflow](https://github.com/wshuyi/deep-research) I was maintaining at the time. I wrote into the file exactly when to check and what to check: 15 stages, 24 contracts, 3 checks.

![](https://miro.medium.com/v2/0*BVj6j-JrP9ZTYeVw.png)

*Caption: The Gangrou visualization of Deep Research shows 15 stages, 24 contracts, and 3 enforced gates. The highlighted notice says this page is a workflow map and visualization only; it does not judge the quality of the work.*

It started by reassessing the question, and during the reasoning stage it lined up multiple candidate approaches to cross-check one another. Those numbers aren’t a report card, but they show how thoroughly I (working with Claude Code + Fable 5) had thought things through back then: from taking on the question to delivering the report, I wanted to account for, one by one, all the work the model might skip.

I poured a lot of myself into this Gangrou Skill. What excited me was the discovery that, through a meta-skill setup, a user’s demand that the AI “work carefully” really could be turned into something concrete, kept, and reused. From then on, putting AI to work wouldn’t just mean nagging it in the moment; I could hand it the requirements and the checks together. And the arrangement did, in fact, serve me for quite a while.

Then came the morning of September 5, 2026, when I gave Codex an order: tear down the Gangrou Skill. All of it. Even the leftover calls to it scattered through other Skills and config files were to be cleaned out.

![](https://miro.medium.com/v2/0*Hg0CEhrQ0dtlFRI0.png)

*Caption: I ask Grok Bot to assess whether Gangrou is still needed and, if not, remove it throughout the system; otherwise, reduce it to the minimum useful form. The reply proposes removing Gangrou as a default requirement for creative workflows while preserving privacy, delivery receipts, and factual verification.*

It was like a painstakingly laid sand mandala: fine colored sand arranged grain by grain into a pattern, only to be swept away in the end by the very hands that made it.

![](https://miro.medium.com/v2/0*7VMsk1_XYhLGiVsX.png)

What was wrong with me? Was I out of my mind? Why suddenly tear down something I’d spent months painstakingly building?

Because **GPT-6 had arrived**.

## The Teardown

What caught my attention most about GPT-6 Astra is its ability to see a complex task through from start to finish. According to [OpenAI’s official model usage guide](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra), it’s better at completing multistep work across code, browsers, and specialized software; when you add requirements or correct course midway, it can handle the change and keep pushing the original task forward. For me, that directly affects the work that had previously required me to keep reminding the model and filling in what it missed.

![](https://miro.medium.com/v2/0*FNIaiiuJkzXOiZOM.png)

But the most interesting part of that official guide isn’t the capability rundown. It’s a usage reminder: OpenAI strongly recommends checking the `AGENTS.md` and Skills the new model will read, to see whether they contain instructions that could affect its behavior.

![](https://miro.medium.com/v2/0*iyiCc0YGQkDm2-pP.png)

`AGENTS.md` holds the working rules for the AI, and Skills hold the instructions for specific tasks. Why does OpenAI make a point of telling us to check them? Because GPT-6 follows instructions more faithfully, which also makes it more susceptible to these files. Vague or conflicting requirements could make it stop short.

That reminder is what sent me back to reexamine the pile of Gangrou rules I had accumulated. In the past, I was always worried the model would miss a requirement, so I kept adding rules. Now that the model follows them more conscientiously, could the arrangements I added to cover for older models’ weaknesses end up getting in the way of it finishing the job?

As I investigated that question, I finally saw the distinction: some rules upheld essential standards, while others compensated for the limitations of the models available at the time. Fact-checking, privacy protection, genuine authorization, and final delivery verification still need to stay. As for things like rerunning from scratch or forcing the work into multiple candidate paths, it depends on whether the task at hand actually needs them.

Once I saw that distinction clearly, I stopped hesitating and decided to strip out that layer of extra process constraints. OpenAI’s advice was to check the rules; exactly what to remove and what to keep was a judgment I made (with help from Claude Code and Codex, of course) after going over my own workflow. That’s where the seemingly crazy demolition order came from.

![](https://miro.medium.com/v2/0*lT_wh1P-EPElkO-U.png)

Having decided surgery was needed, the next question followed naturally: who would untangle this web of rules, and who would carry out the thorough cleanup?

## Handing It Off

Who better to untie the knot than the one who tied it? I chose to hand the official guide straight to Codex + GPT-6 Astra and put it in charge of both working out the cleanup plan and carrying it out.

Also collaborating on this operation was my assistant, Grok Bot. Throughout the process it handled the crucial job of relaying messages in both directions: passing my overall intent, constraints, and mid-course adjustments along to Codex, and bringing the plan Codex worked out, its progress, and its verification reports promptly back to me.

The division of labor here was very clear:

I set the goals, drew the red lines, and corrected course whenever things drifted;

Grok Bot, as the communication hub, relayed requirements and feedback accurately;

Codex handled the actual code reading, technical judgment, file edits, and verification of results.

![](https://miro.medium.com/v2/0*eZaEOGo2_Ds9VhJK.png)

Throughout, I neither let the assistant in charge of communication overstep and draft the technical plan itself, nor tossed Codex a breezy “tidy this up for me” and walked away.

With a system of rules that had run for months and meshed together like gears, where exactly did the difficulty of cleaning it up lie? How much reasoning power did it take, and what kind of guidance and correction did it need?

## Where the Difficulty Lies

The hard part of this job lies in carefully teasing apart how the rules relate to one another. What you’re facing is a stack of rules, each written back then to address some specific pain point, and you have to determine precisely: what risk was this requirement originally guarding against? Does that risk still exist given today’s model capabilities? If you delete it rashly, will it set off a chain reaction somewhere else down the line?

Precisely because so much contextual judgment is involved, the choice of reasoning effort became key.

When I first started using the new model, I figured a reasoning level of medium was enough for everyday work. But in the course of actually doing this job, I changed my mind and told Grok Bot that Codex had to pick the level based on the specific type of task. For a system-wide cleanup like this one, where pulling one thread can unravel everything, the level had to be explicitly set to high. For other routine day-to-day tasks, the global default stayed at medium.

Cleaning up rules means examining how their logical relationships change with each edit, and I wanted to give the model more room to reason through those judgments.

![](https://miro.medium.com/v2/0*57CXhPcHIMxFLjR-.png)

For the prompt to Codex, I distilled three indispensable points:

First, state the goal clearly: spell out which old constraints on current tasks this cleanup should remove;

Second, draw the boundaries: explain which procedural gates should be deleted, and which essential requirements concerning facts, privacy, and verification must stay;

Finally, explicitly require it to produce concrete evidence that it checked the knock-on effects, and to provide results a human can review.

With the goal, boundaries, and reasoning level all spelled out, what remained was to see what would come up in actual execution.

## How It Played Out

When you tear out a meta-skill that’s deeply embedded in an entire AI agent system, smooth sailing is unlikely.

Take the Deep Research workflow mentioned earlier.

Before the changes, the workflow file listed 15 stages, 24 contracts, and 3 checks. The stages weren’t just gathering sources, extracting facts, and writing the report; they also included initializing directories, classifying the question type, assessing timeliness, re-verifying the basis of comparison, and two review passes.

![](https://miro.medium.com/v2/0*VwYYWS4qlg0D_XS_.png)

Lots of graphs and lots of stages don’t, by themselves, prove the design was flawed. Research needs authoritative sources, comparing two tools needs a consistent basis, and reasoning needs to be followed by a hunt for counterexamples; all of that is still needed today. What really needed clearing out were a few rules surrounding the core workflow.

Start with the initial steps. The old version said: “Every research run must redo Step 0 / 0.5 / 1 from scratch.” Right after that, it put the previous run’s definitions of the research subjects, comparison criteria, fact-card templates, and so on off-limits for reuse as well. They could be reused only for an explicit continuation of the same task, or when I explicitly asked to carry them over.

That requirement was originally there to prevent laziness: switching to a new topic but slapping on the previous analytical framework unchanged. But it also decided in advance whether comparison criteria could be reused. For example, say the last report compared tools by cost, deployment model, and privacy requirements, and this time it’s two different tools of the same kind. Whether those criteria still fit could have been judged item by item against the new question; the old version instead required a fresh diagnosis as a matter of principle and wouldn’t allow the previous template of comparison criteria to be carried over directly. This is what the “rigidity” I demanded back then produced.

After the change, the requirement became: first verify the research subjects, time frame, basis of comparison, and audience; trustworthy existing evidence can be reused, and whatever has changed gets verified incrementally. The question the model has to answer is whether this piece of material still applies now, rather than first proving it ran everything from scratch.

![](https://miro.medium.com/v2/0*yu2l-nrljSndPCIS.png)

Next, the reasoning stage. The old version would first probe whether subagents could be called; if they could, it automatically ran three candidate paths and then merged the three lines of reasoning. That amounts to a rule that whenever you have the means to call in three people, you must call in all three.

The new version makes ordinary research a single pass by default. Only when the question is genuinely complex or contested, or when I ask for a multi-path comparison, does it use three candidates. For a model as formidable as GPT-6, running three at once may not be a case of “two heads are better than one” so much as “too many cooks spoil the broth.”

Independent review stays. I was quite happy with this change Codex proposed.

Last comes the status of that flow graph. The old version called it the workflow’s “authoritative graph representation,” and even changing the semantics of a step, contract, or check required keeping the definitions in the graph in sync. The new version states plainly that it is just a historical workflow document, or an input when someone deliberately opts to use the old graph tooling; it no longer governs the execution of ordinary research.

![](https://miro.medium.com/v2/0*xlDJcgF5w2bsR54E.png)

The new diagram groups the work into a few easy-to-follow phases; it isn’t claiming the underlying files are down to only these steps. What it means to show is that the AI can organize the research around the question, while the evidence and reasoning check and the final delivery check still happen. The three corresponding script checks still run, respectively, before the report is completed, before final delivery, and after packaging.

For instance, if a new fact shows up in the conclusions without a matching fact card and source, it still doesn’t get through. If the material is changed after review, the new version has to be checked; the previous version’s review can’t be used to vouch for it.

To sum up: the requirements to start from scratch, automatically generate three candidate approaches, and follow the workflow graph were removed; the checks on facts and the final deliverable remained.

This also explains why I had to correct Codex partway through the cleanup. An old gate I had explicitly asked to delete couldn’t simply be softened into a gentle suggestion and left in place; a workflow already retired couldn’t be quietly pushed back in either. Because that would amount to making no change at all.

## One Concrete Improvement

There was one more change, far more concrete than “give the model more freedom”: how the research report gets packaged.

The independent verification this time found that the old delivery script, though it claimed to package by manifest, actually swept in the entire working directory recursively. A simulated private document placed there for testing went into the archive right along with everything else.

What does that tell us? That so-called rigidity doesn’t necessarily guarantee we get the result we want. Mechanical execution can even backfire.

The corrected script now collects only the final report, the web page, the image manifest, and the images actually listed in that manifest. The original prompts, internal review records, and unlisted materials all stay local. The same explicit file manifest is also used to prepare the assets for web deployment. The independent verification further checked for directory traversal and symbolic links, to keep a path that looks like it’s in the manifest from pointing outside it.

Of course, the body text and images that make the cut still need a privacy check. A file being on the manifest doesn’t mean its contents are necessarily fit for public release.

![](https://miro.medium.com/v2/0*SKRU6AVhM5_jORYH.png)

These changes also gave me a more concrete understanding of what a harness does. A [harness](https://mp.weixin.qq.com/s/YivNlDsiA5g4g6IRY5TX4w) is the working framework that lets a model access files, call tools, receive human instructions and corrections, and hand the final product back to you.

In this case, Grok Bot served as that go-between. Its role was concrete: it relayed my corrections to Codex so Codex could read the files before and after the changes, run the check scripts, and deliver the current report and images.

![](https://miro.medium.com/v2/0*KxGxvlRetY9HeVMr.png)

So removing this meta-skill and its effects across other Skills involved not only the model’s ability to carry out changes, but also my corrections, rule adjustments, and script fixes.

With these relationships sorted out, we can finally return to the dilemma we started with: if the goal all along was to get the work done well, why was building it a few months ago reasonable, and tearing it down a few months later equally reasonable?

## The Answer

Building it a few months ago and tearing it down a few months later, two seemingly contradictory acts, actually follow exactly the same criterion: how to get the work done reliably.

A few months ago, facing a model with limited capabilities, I built Gangrou to make sure the checks and steps that couldn’t be skipped actually got run, while leaving the model room to choose its methods, and then to review the process through the run graph. Building it then was a practical response to the constraints I faced.

A few months later, the shift in model capabilities led me to reexamine those arrangements, and I found some of the old requirements no longer fit. I removed them so that old habits would no longer hold back what the new model could accomplish.

## Wrapping Up

With OpenAI’s release of GPT-6, plenty of onlookers gasped that they had “witnessed the dawn of the AGI era.” That strikes me as a bit overblown, but the jump in model capability is very real. And as a user of large models, you can’t ignore the changes this brings to how you and the model interact.

If the risk a rule was originally written to guard against is long gone, if it not only fails to add certainty but is actively slowing down execution today, then don’t cling to it just because of the effort you once put in.

The technology keeps changing; what’s worth keeping is the goal of getting the work done reliably. As for the specific scaffolding and guardrails, put them up decisively when they’re needed, and when it’s time to take them down, take them down yourself, cleanly and decisively.

So before you start using the latest flagship model, I’d suggest you go through your own existing setup too, and see whether there’s anything there that needs clearing out.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- [Perplexity or the Big Three? My AI Subscription List and How I Choose](https://mp.weixin.qq.com/s/QEAcGKlA6h3kQnY3B8lz3Q)
- [Claude Skill Snapshots: An Undo Button for Iterating on Your AI Skills](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
- [In the AI Era, Stop Doing “Homework” and Start Creating Work of Your Own](https://wshuyi.medium.com/in-the-age-of-ai-stop-doing-homework-start-creating-your-masterpiece-009cf4f37388)
- [Still Fretting Over Whether Someone’s Work Is “Purely Human” or AI-Assisted? You May Need to Get Used to Hybrid Intelligence](https://wshuyi.medium.com/hybrid-intelligence-what-youre-really-buying-ee4ae5000188)
- [AI Applications Are Exploding. Is Your Moat Wide Enough?](https://mp.weixin.qq.com/s/-H-Q70wBTDaN7APYnRhI6g)
