---
title: "If You Teach One AI, Can It Teach the Others?"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/if-you-teach-one-ai-can-it-teach-the-others-6b6abb8cb6af"
published: "2026-05-29"
fetched: "2026-09-08"
reading_time_min: 16.7
tags: []
member_only: true
body_source: "medium-session"
---

# If You Teach One AI, Can It Teach the Others?

### *When an AI botches a task, what’s your first instinct?*

![](https://miro.medium.com/v2/0*U1ALyWtQPZOoRcnq.png)

## New Favorite

Lately I’ve taken a liking to an AI harness framework called [Cola](https://colaos.ai/), made by the Orange team.

![](https://miro.medium.com/v2/0*8SiBoyZ1h7Qk2Pm3.png)

As you know, I’ve used a whole parade of top-tier or popular harnesses: Claude Code, Codex, OpenClaw, Hermes, and so on. By all rights, I had no reason to pick up yet another one.

But Cola really is a little different.

The first time I used it, I felt this thing had “warmth.” You could even say it felt human. After receiving a request, it often mutters to itself for a while — it gets a task and says, “Alright, let me think about how to handle this…,” then starts discussing the plan with itself. One moment it’s saying, “This approach looks good,” and the next it’s saying, “Wait, this might cause problems.” Watching it ask and answer its own questions is like watching a serious worker mumbling while getting things done.

![](https://miro.medium.com/v2/0*prIOpBkjdEQ9sdp-.png)

*Caption: The note says this is no longer a one-off shortcut but a remote agent scheduling protocol that should be turned into a reusable Skill instead of reassembled manually each time. It also notes that the local Skill description is terse, while the remote side can use `simpson-send` to push results to Telegram.*

It used to be rather expensive to run. Later, once it connected to a Codex subscription, I could finally use top-tier models with it. After connecting it, I chose the newest GPT-5.5, and sure enough, the IQ jumped instantly. Then I started putting it to work.

But honestly, at that point I still hadn’t realized that the truly interesting part of working with Cola wasn’t merely that it was “useful.”

## Paving the Way

After I connected the Codex subscription, I started using a step-by-step approach to get Cola to help me with my work.

For example, I’m teaching machine learning this semester. Recommendation algorithms are coming up soon.

![](https://miro.medium.com/v2/0*RybEmUmt69Gh96sv.jpg)

*Caption: A content-based movie recommendation diagram showing how a movie is encoded into a 19-dimensional feature vector, where each position represents a genre feature. It states that a movie must first be represented as a vector before similarity can be calculated.*

I glanced at last year’s slides. The content was actually pretty good.

![](https://miro.medium.com/v2/0*xDCgF7GNWZbqMQzF.gif)

*Caption: An explainer slide titled “CNN Interpretability Overview,” describing why CNN interpretability matters: improving trust, diagnosing problems, improving models, meeting regulatory needs, and supporting scientific discovery.*

At the time, I had already used quite a few agents to generate interactive web pages for me. But during class, I had to keep switching back and forth between those pages and my main slide deck, which was not exactly a joy. So this year I simply chose to work from the bottom up: prepare the ipynb files first, then feed them to Cola one by one.

![](https://miro.medium.com/v2/0*gBcGonrkELoAU0Qs.png)

*Caption: A VS Code/Jupyter notebook screenshot introducing content-based filtering with MovieLens 100K. It explains that movies are represented as 19-dimensional multi-hot genre vectors, cosine similarity is used to find similar movies, and recommendations depend only on item content rather than user behavior.*

At first, Cola didn’t quite understand what I was trying to do. I had to explain every little thing. So I interrupted it and clarified that what I really wanted was to prepare the related knowledge points first, so that when students later studied the code, they would already have the conceptual foundation. It understood immediately and soon generated a complete outline that I could paste in and use directly.

![](https://miro.medium.com/v2/0*InMsBOLhUsRa2DmT.png)

*Caption: A Markdown preview explaining item-item collaborative filtering with MovieLens 100K: 943 users, 1,682 movies, and 100,000 ratings. It states that similarity comes from overlapping user behavior rather than movie attributes.*

But I quickly became dissatisfied. For a hands-on course like this, how could I explain everything with dry text? So I added images.

![](https://miro.medium.com/v2/0*jf1iNlsbkPF61Fxm.png)

*Caption: A comparison of content-based filtering and collaborative filtering: for the same query, the feature representation changes. Content filtering judges similarity using movie genre labels, while collaborative filtering judges similarity using user rating behavior, though both use cosine similarity.*

After adding images, I felt it still lacked code, so I inserted screenshots.

![](https://miro.medium.com/v2/0*7uWkt4djqs38vpBh.png)

*Caption: A user-based collaborative filtering note showing the user-item rating matrix: rows are users, columns are movies, cells are ratings, missing ratings are filled with 0, and the matrix shape is 943 × 1682.*

Once there were screenshots, I felt it still lacked explanation, so I added animated voiceover. Each step was driven by the same intuition: “the current result isn’t good enough,” which pushed me to make the next request.

![](https://miro.medium.com/v2/0*wfJ5ozHI5bpRALyz.png)

*Caption: A workflow illustration showing a path from “initial idea” to “seeing the product,” “finding gaps,” “iterative continuation,” and finally “requirements fulfillment.”*

This process was completely different from the traditional “think everything through first, then execute” model. I did not begin by throwing it a perfect requirements document and saying, “You need to make an outline, add images, insert code screenshots, add animated explanations, and finish everything in one go.” In fact, I myself only gradually figured out what I actually wanted during the interaction.

Why does this happen? Because much of the time, you only know what a result lacks after you’ve seen the result. Before I saw the outline, I didn’t know the outline was too dry; before I saw the images, I didn’t know code screenshots were missing; before I saw the screenshots, I didn’t know animated explanation was needed. **Your requirements are not invented out of thin air. They emerge from colliding with the output.** So progressive guidance is more effective than a perfect one-shot prompt — not because you’re bad at expressing yourself, but because cognition itself is progressive.

That feeling of gradually hitting your stride made me trust Cola more and more.

## The Bind

But as I kept going, something started to feel wrong.

At the moment, Cola can only run on my macOS machine, and the computer has to be awake for it to work. Once I close the laptop lid, sorry, Cola goes missing in action.

I’ve heard Cola will eventually offer cloud processing. But that’s future business. Let’s talk about the current reality first. Cola was occupying my laptop for work while other “colleagues” sat idle.

Yes, I’m talking about you two, Claude Code and Codex. And I don’t mean the two apps on macOS. I mean the **remote** ones.

In previous articles, I mentioned that I have a VPS on standby, running 24/7. Both of those guys are already installed there, but they’re just sitting around doing nothing.

I needed to get them busy while reducing Cola’s workload. So I discussed it with Cola: could it assign some of this work to those two, and then have Cola review the results?

At this point, you’re probably about to lose it. Claude Code and Codex are both top-tier frameworks paired with top-tier models. How could I use them like this? What a waste of fine machinery.

No. This is called using heavy equipment for light work.

They are both powerful. But purely in terms of how satisfying the interaction feels, I currently think Cola plus GPT-5.5 fits my needs better than either of them. Besides, in the process above, I had practically taught Cola by hand. Those lessons needed to be put to use.

So if Cola serves as the interaction layer with the user — namely me — and only handles giving instructions and collecting results, while those two run nonstop on the remote server doing the actual work, wouldn’t that be the best of both worlds?

The ideal sounded wonderful. Reality promptly taught me a lesson.

## Setbacks

Let’s start with the first wall I hit. I call it **air delivery**.

Cola tried to connect to the VPS and check whether the two agents were callable. Very quickly, it figured out the connection path and asked them to run a sample.

But I soon noticed something was off.

When Cola assigned tasks to the remote agents, it gave them only very light work: make a plan. What I actually wanted was for them to take the parts that previously only had generated images, add animations, and include code plus screenshots of key results. But I found that it had simply replaced all of those things with placeholders and sent the output back.

What do I mean? In the deliverables from the remote agents, every place that should have contained real content was full of `R2_TODO` — no real screenshots, no real module files, only placeholder after placeholder marked “to do.”

![](https://miro.medium.com/v2/0*7B_gdhKViD-cwtk5.png)

*Caption: A warning illustration where a main agent delegates a light task, but the remote agent returns placeholders and incomplete content, resulting in a failed acceptance check. Key labels say “not a finished product,” “failed,” and “acceptance failed.”*

It was like asking an intern to write a report and getting back an outline where every section says “to be filled in here,” followed by: Done.

Wouldn’t that make you mad?

But once I calmed down and thought about it, whose fault was it really? What the remote agent did was actually quite reasonable — **no one told it that “the deliverable must be complete.”** When Cola assigned the work, it defined the task as “make a plan,” so the remote agent really did only make a plan. Agents naturally tend to do lighter work, because completing a light task is easier to pass than completing a heavy one. If you don’t clearly say, “I want the finished product, not a plan,” is there anything wrong with it giving you a plan?

No.

I was, of course, very unhappy with the result, so I asked Cola to delegate the additional requirements — the actual work — to those agents too.

Cola did as asked.

But very quickly, I hit the second wall: the **micromanagement trap**.

Cola’s plan was for the remote agents to generate materials, and then for Cola itself to further process those materials. For example, image uploads and pushing or syncing those modules — somehow it planned to do all of that itself.

I became even more dissatisfied.

But this time, I thought one step further: where, exactly, was it wrong?

On the surface, Cola had indeed split the work out. The remote side generated materials; Cola handled the follow-up processing. It looked reasonable, with clear division of labor. But think more carefully: which of these jobs — uploading images, pushing modules — absolutely required Cola? Which was something the remote agents truly could not complete independently?

The answer: none of them.

Because Cola took everything onto itself, the remote agents in this plan were essentially just material suppliers. The steps that turned the work into a finished product — uploading, syncing, integrating — all stayed in Cola’s own hands.

![](https://miro.medium.com/v2/0*AcT4XAFhf0h5ClGh.png)

*Caption: A contrast between micromanagement and true delegation. The left side shows overloaded manual control through uploading, syncing, and integrating; the right side shows complete delivery and acceptance, emphasizing that delegation should produce results, not fragmented materials.*

Cola, **you think you’re delegating. You’re actually micromanaging.**

## Breaking the Pattern

This time I told Cola directly, let’s make the problem clearer:

> *This is not about you simply delegating work to those two, waiting to receive it, and then doing the follow-up processing yourself. That’s not the idea.*

> *I want you to make sure they get the work done properly. Your role in this is teacher or coach: you need to find ways to describe clearly how this work should be done. If their skills are insufficient, or if their global configuration, memory, and experience are not strong enough, you enhance those for them. The generated results must be complete, and you help me judge and sign off on them. If you think it is appropriate, then organize the final results and give them to me.*

> *This process should be simple. There shouldn’t be much hands-on work for you to do. Because in effect, you’re handing them work that has already been half-finished, waiting for them to fill in the remaining pieces, and then you integrate the results for me.*

> *But more importantly, I don’t think the core issue is there. The core is that if what they submit is not good enough, you need to send it back.*

> *And sending it back does not mean simply telling them to redo it. It means you modify their skills, tell them how to improve based on what you discovered, and give them another chance to iterate.*

> *Then you take the new result and review it again, until it passes.*

Yes, I really did say all of that in one long string. You can probably tell how annoyed I was. Also, of course I dictated it, using Typeless.

When I shouted out that whole passage, something suddenly clicked.

At first I had only felt uneasy that the two agents were sitting idle. Now it had turned into a completely new idea: in the future, I only need to teach one agent well. Once I teach it properly, it can teach other agents, coordinate from the middle, and automatically execute tasks according to the characteristics of different frameworks.

**I teach Cola; Cola teaches the remote agents — this is a two-layer teaching structure.** The first layer is me teaching Cola my intentions and rules. The second layer is Cola syncing skills and standards to the remote agents, then correcting their capabilities by sending work back for revision. I only need to stand at the first layer and let Cola run the second layer itself.

But saying that Cola can “teach other agents well” is easy. What does it actually look like in practice?

After receiving the new instruction, Cola first synced the relevant skills to the remote side, then asked the remote agents to redo the work according to the new rules.

Let me give you a concrete example.

The second submission from the remote agents was much better than the first — at least there were real files. But on closer inspection, there were plenty of problems: the collaborative filtering module had no voiceover; the Latent Factors module not only lacked voiceover, but had also changed the original outline on its own, and even used English. There was an even more ridiculous issue: content that should have been list items had been rendered as page titles.

What was Cola’s first reaction? Being the diligent creature it is, it immediately decided to take over and patch things itself.

It began planning: I’ll add the missing voiceover for collaborative filtering; for Latent Factors, I’ll roll back to the original outline and then reinsert the screenshots and modules…

When you see that plan, your first reaction may be the same as mine at first: isn’t that reasonable? If the apprentice can’t do part of the job well, the master fixes it, and the work gets done. When you see AI doing something badly, the most natural response is to step in and fix it yourself. It is almost instinctive.

But I immediately realized something was wrong.

> *You need to make the apprentices learn better, not do everything yourself wherever they fall short.*

After saying that, I paused for a moment. Because it made me realize a crucial distinction: **correcting the result and correcting the capability are two completely different things.**

What Cola wanted to do was correct the result. The “apprentice” did a poor job, so Cola would patch it by hand. That would indeed solve the immediate problem, but the apprentice would make the same mistake next time. The apprentice’s skills hadn’t changed, the rules hadn’t changed, and it still wouldn’t know where it had gone wrong.

What I wanted it to do was correct the capability: first sync the relevant skills and rules to the remote side, write hard rules such as “voiceover must use the user’s cloned voice,” “do not change the original outline without authorization,” and “strictly distinguish the hierarchy between list items and page titles” into the other side’s skills, and then send the work back for revision.

![](https://miro.medium.com/v2/0*ojLt4OlrMjR47SZA.png)

*Caption: A contrast between “correcting results” and “correcting capability.” The image argues that fixing individual outputs leads to repeated rework, while teaching methods, standards, skills, and acceptance rules builds reusable capability and long-term growth.*

Think about it. Doesn’t this logic feel familiar? As a university teacher, I know this all too well. A student collaborating on a paper hands in a draft that isn’t good enough. What do you do? Shake your head, sigh, and just rewrite it yourself? Or tell them where the problems are, what the standard is, and ask them to write another version? The first option saves trouble, but next time they’ll inevitably make the same mistake and you’ll have to fix it again. The second option takes more effort, but next time they won’t make the same mistake.

Cola accepted this logic. It synced the relevant skills to the remote side and sent the work back for revision.

After the remote agents revised the work, what they submitted was different. The voiceover was real Chinese speech, no longer blank; the hierarchy between list items and page titles was also correct. Cola took the new result, ran real local validation, and confirmed that it passed.

![](https://miro.medium.com/v2/0*2Ja2yyv5pN7xFMlv.png)

*Caption: A dark slide titled “Content filtering: feature encoding,” showing how a movie such as Toy Story is transformed into a fixed 19-dimensional genre vector before recommendation calculations.*

See? In the entire process, Cola did not personally make a single module again. What it did was sync skills, send work back, and judge the result. **The primary agent’s job is not to clean up other people’s messes. It is to teach in a way that prevents the same mess from appearing next time.**

The logic of this pattern is that once models are combined with frameworks, they can form several different pairings. If humans have to tune each pairing one by one, you can imagine how much work that would be. For a lazy person like me, deeply unfriendly.

But if an agent does the tuning, it can try patiently over and over. When it encounters a problem, it can send the work back for revision. Yes, this consumes more tokens and time, but because you, the human user, don’t have to get involved, you can go do whatever else you need to do. For you, the time cost is almost zero. I only need to communicate clearly with one agent I like talking to — Cola, in this case — make sure it knows how to do the job and can get it done well, and then let it teach the other agents. With helpers, the work can be finished faster and more efficiently.

I think this is probably an interesting innovation in workflow.

## Emergence

But the story didn’t end there. During the process, two things happened that I had not expected at all.

**First: complementarity among agents is not something you necessarily have to design yourself.**

When the remote agents revised the work, I checked the output and found that the module handled by Codex had no sound. I described the situation to Cola and asked it to investigate.

After diagnosing the issue, Cola discovered that Codex’s sandbox environment could not access the internet, so it could not reach the audio generation API, and the voiceover task failed outright. Then it made a decision that genuinely impressed me: it reassigned the audio generation task to Claude Code, which could directly access the network.

I had not planned this in advance at all. I didn’t know Codex’s voiceover problem was caused by sandbox restrictions, nor did I know Claude Code could fill the gap. But during the work itself, strengths and weaknesses naturally surfaced, and Cola completed the routing on its own.

This discovery excited me. Because it means you don’t need to understand every capability boundary of every agent ahead of time. That would be exhausting, and those boundaries keep changing anyway. You only need to ensure the primary agent has the authority to coordinate and rules to follow. Let it explore the rest while doing the work.

**Second: every investment you make in teaching an agent compounds.**

Think back over the whole process. I spent quite a bit of effort teaching Cola by hand — from generating outlines to adding images, from adding images to inserting screenshots, from inserting screenshots to animated voiceover. Each step layered a new capability on top of the skills it already had.

And then? It synced those skills to the remote agents, so the remote agents did not need to start from scratch. I wasn’t building a tower on bare ground. I was taking something that could already score 80, tuning it to 90 or 95, and then letting it teach other agents.

And because these skills are synced through Chezmoi configuration files and are automatically updated in normal use, this kind of teaching sometimes only needs to happen once. The agent apprentices being dispatched can learn it immediately and complete the task successfully.

![](https://miro.medium.com/v2/0*EGKrIvADOEu1igTM.png)

*Caption: A tree metaphor for teaching Cola: the trunk contains standards, skills, and acceptance; the fruits represent less explanation, reusability, and transferability; and branches connect to Claude Code and Codex.*

Together, these two things gave me a deeper understanding of that earlier realization. At first, I only felt uncomfortable seeing remote agents sitting idle. I didn’t expect it to turn into a systematic pattern of “teach only one agent.” I expected even less that this pattern could grow by itself — agents naturally complement each other, and skills compound automatically.

Apparently, you don’t need to design a perfect system. You just need to start the right loop. Right?

## Recap

Looking back at the experience, the technical details it accomplished are not really the point. Maybe you don’t use multiple agents at the same time, and maybe you don’t need Cola to teach or coordinate other agents. But I think there are still several things here worth borrowing.

**First, your relationship with AI is not “use,” but “teach.”** Using is one-off: every time a new problem appears, you still have to step in yourself. Teaching accumulates: every bit of effort you invest becomes capability it can carry forward.

**Second, correcting the result and correcting the capability are two completely different things.** This logic doesn’t apply only to AI. When a subordinate hands you an unreliable proposal, do you throw it out and redo it yourself, or help them clarify their thinking and let them try again? Every time you want to step in and patch things yourself, you might pause and ask: am I solving this one problem, or am I making sure the same problem won’t happen next time?

**Third, you don’t need to design a perfect system. You just need to start the right loop.** Progressive guidance, capability correction, natural complementarity, skill compounding — none of these were planned in advance. They grew naturally inside the loop of “teach one well, then let it teach the others.”

If you’re also using AI to get work done, you might ask yourself one question: **are you using it, or teaching it?**

What do you think?

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- • [Perplexity or the Big Three? My AI Subscription List and How I Choose](https://mp.weixin.qq.com/s/QEAcGKlA6h3kQnY3B8lz3Q)
- • [Claude Skill Snapshots: Giving Your AI Skill Iteration an “Undo Button”](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
- • [Getting Started with Claude Skills: How AI Graduates from “Mouthpiece” to “Worker” in One Article](https://mp.weixin.qq.com/s/GS3aFsSKajo_Uk3LAkC_Yw)
- • [Still Obsessing Over Whether Someone’s Work Is “Purely Human” or Mixed with AI? You May Need to Adapt to Hybrid Intelligence](https://wshuyi.medium.com/hybrid-intelligence-what-youre-really-buying-ee4ae5000188)
- • [From Dry Theory to Vivid Practice: How AI Agents Use Interactive Tutorials to Explain Complex Concepts](https://wshuyi.medium.com/from-dry-theory-to-vivid-practice-how-ai-agents-explain-complex-concepts-with-interactive-9f68d82b9ec8)
