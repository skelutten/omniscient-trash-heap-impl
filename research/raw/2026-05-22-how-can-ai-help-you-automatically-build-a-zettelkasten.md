---
title: "How Can AI Help You Automatically Build a Zettelkasten?"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/how-can-ai-help-you-automatically-build-a-zettelkasten-78eca636fc73"
published: "2026-05-22"
fetched: "2026-09-08"
reading_time_min: 15.0
tags: []
member_only: true
body_source: "medium-session"
---

# How Can AI Help You Automatically Build a Zettelkasten?

### What we need to do is not hand our thinking over to AI. It is to lower, as much as possible, the mechanical barriers that stop us from starting to think.

![](https://miro.medium.com/v2/0*5F_cCjELJbnR7Sym.jpg)

## Where This Started

Recently, I built a small tool that uses AI to help me automatically build a Zettelkasten — a box of linked note cards.

It can automatically extract cards from articles I’ve written in the past and from my Get notes, build bidirectional links among them, and then turn that network back into topic ideas and article outlines.

That may sound a little mystical. So let’s start with a role model.

His name was Niklas Luhmann, a German sociologist.

![](https://miro.medium.com/v2/0*tv3Lq561-jLW8A49.jpg)

From the time he entered academia in the 1960s until he completed *The Society of Society* in the 1990s, Luhmann kept writing for more than 30 years. Over his lifetime, he published more than 70 books and nearly 400 academic papers, many of which were later translated into other languages.

Think about that for a second. That kind of output would be intimidating in any era. It wasn’t the occasional flash of inspiration. It was long-term, steady, high-density production.

Naturally, many people ask: what was his secret?

Luhmann’s own answer was that he had a card-based writing system.

In the documentary *Niklas Luhmann — Beobachter im Krähennest*, he showed his paper card system. Those cards weren’t simple excerpts. Through numbering, cross-linking, and constant additions, they grew into a knowledge network he could repeatedly enter and keep expanding.

Of course, Luhmann’s output can’t be explained by tools alone. But his card box at least shows one thing: long-term writing requires a material system you can keep calling on and keep connecting.

![](https://miro.medium.com/v2/0*aawkaqI9zH6Oyemr.jpg)

Later, the German writer Sönke Ahrens wrote a book called *How to Take Smart Notes*.

![](https://miro.medium.com/v2/0*ekc4CjxsqsKnW5t7.jpg)

When the Chinese edition first launched, I even participated in a livestream translation session and wrote a blurb for it.

![](https://miro.medium.com/v2/0*pIXSnY7mjjjkpVLq.jpeg)

*Caption: This is a promotional screenshot for the Chinese edition of Sönke Ahrens’s book, showing my recommendation text for it.*

By that logic, I should be a faithful practitioner of this method, right?

Here’s the problem — as you know, I’m a rather lazy person.

If you ask me to truly practice the Zettelkasten method, I can usually get started and stay enthusiastic for two or three days. After that, the materials are scattered everywhere again. To put it politely, it becomes “pearls strewn all over the floor.”

## The Pain Point

My materials are mainly scattered across two places.

One category is articles I’ve already published.

These articles have been written from beginning to end. On the surface, the content has already been captured. But the problem is that articles are linear. They are like paved roads: good for readers walking from the beginning to the end, but they do not automatically break themselves down into reusable long-term notes.

The most important part of Luhmann’s method is not that he “wrote a lot of cards.” It is that those cards **can form a network**. An idea can be reused later in different articles and different questions, and new connections can emerge among the cards.

I didn’t do this very well in the past.

The other category is in Get notes.

My notes used to be even more fragmented. Only in the last two years have I increasingly used Get notes for daily capture, which finally pulled things together. Whenever I see something interesting, read useful material, hear an idea, or receive various pieces of information synced from my Knowledge Planet community, they all get saved there.

That is, of course, a good thing. At least the materials are not lost.

But “not lost” does not mean “actually used.” Every time I want to write a new article, I still have to rack my brain for a topic. In theory, a card network should help topics emerge “from the bottom up.” In reality, the network never grew, and I still had to squeeze topics out of my own head. As someone who has promised Knowledge Planet subscribers three articles every month, I constantly feel the pressure of coming up with topics.

## The Method

Then I thought: these days, can’t AI help with a lot of things we don’t feel like doing ourselves?

If you don’t want to make slides, AI can help you make them. If you don’t want to write a report, AI can help you build the structure. If you don’t want to write data-analysis code from scratch, AI can write it for you. Even in programming, AI assistance has already become common.

If coding itself is changing, why can’t AI help with extracting, organizing, filtering, and linking card notes?

But card notes are not just about tidying up a format. They involve sources, attribution of ideas, and long-term reuse. So I can’t simply hand everything over to AI and let it generate cards in one click. I have to add several gates.

My approach is actually quite simple.

First, I treat my existing articles and Get notes as factual sources. AI is not allowed to invent cards out of thin air. Each card must come from something I have already written, recorded, read, or collected. Otherwise, the output may look rich, but in reality it may just be duckweed drifting in from the model’s training data.

Once the sources are in place, AI extracts candidate cards from them. By “extract,” I don’t mean mechanically copying a paragraph and calling it done. I mean pulling out concepts, judgments, experiences, and cases that can be reused over the long term, then turning them into atomic notes.

After extraction, there must also be filtering. If a similar card already exists on the same topic, there is no need to create a duplicate. Otherwise, redundant content keeps piling up, and what you end up with is not a knowledge network but a landfill.

Finally, the cards have to align with my values.

That may sound a little abstract, but it is crucial. Get notes may contain a lot of external content — some from books, some from articles, some from other people’s views. Once they enter my note system, they do not automatically become “my views.”

I need AI to make a candidate judgment based on the values reflected in my past articles: Do I support this claim? Is it consistent with the things I have long emphasized? Later, I read the judgments AI gives me. It feels a bit like drawing cards in a game — always fresh, always a little exciting. If it gets it right, I sign off. If it goes off track, I revise it. If it cannot make the point clearly, I delete it.

Manually reviewing AI’s automatic comments based on your values is **extremely important and cannot be skipped**. If AI does not make its first-pass comments according to your values, isn’t that basically letting someone else ride wild horses through your mind? And if AI gives you comments and you use them without even looking, then the owner of the note base is no longer you. It is AI.

With these gates in place, AI is not thinking for me. It is doing the mechanical, repetitive, but necessary grunt work that has to be done.

## The Technology

Technically, I’m using “Lobster,” which is OpenClaw, together with a Codex subscription.

If you don’t care about the technical details, you can think of it this way: I wrote a set of rules, and AI follows those rules to organize materials for me.

In the Claude / OpenClaw context, this set of rules is called a Skill. You can think of it as an instruction manual for AI. An Agent is the AI worker that actually does the job. It follows the manual to read my materials, extract cards, build links, and generate candidate topics and article outlines.

Of course, this does come with a cost.

During my experiment, the Codex usage screen showed that in roughly one day, this task consumed about 50% of my quota for that week. That number is honestly a little terrifying.

![](https://miro.medium.com/v2/0*RpWkUZumLKuIk0w7.png)

*Caption: The Codex usage screen shows that this automated card-building task consumed roughly half of my weekly usage quota in about a day.*

On the other hand, the results it produced were also enough to make me inhale sharply.

## The Process

This is what it looked like while working last night.

![](https://miro.medium.com/v2/0*-RzHngK8Jbl0cqUM.gif)

*Caption: The screen recording shows OpenClaw and Codex running through the workflow overnight: scanning old articles, extracting candidate cards, and writing source links.*

That night, it was mainly scanning old articles, extracting candidate cards, and writing source links. From the screen recording, you can see it kept running for a long time. By the time I checked the next day, the task was already complete.

After watching it, I truly felt this was the modern version of an AI worker. It does not complain about being tired. It does not get distracted. It just steadily finishes a long, important task. This was also the first time OpenClaw helped me complete a task like this. I was very satisfied.

If I had to do this work myself, it’s not that I would necessarily be exhausted beyond recognition. It’s that I would never start in the first place. Don’t forget: Teacher Wang is lazy.

## The Results

So how did the final result look?

I mainly checked three things: whether the cards had sources, whether there were links among the cards, and whether those links could in turn generate topic ideas.

I opened the result directory in Obsidian.

On the left is a list of notes it extracted. Every card has its own source; none was generated out of nowhere. On the right, you can see a series of related cards. These cards have already been linked to one another. They are no longer lonely excerpts sitting by themselves.

![](https://miro.medium.com/v2/0*8KS2ksJFnyjrnfwv.png)

*Caption: In Obsidian, the extracted card list appears on the left, while related cards are shown on the right, demonstrating that the notes have source-backed links rather than standing alone as isolated excerpts.*

One card came from Get notes. It was a note I left in January 2021 while reading related material.

The original note was very short, but below it appeared a section called “My Judgment.”

Notice that “My Judgment” was not something I wrote by hand. It was AI’s result after measuring that original note against values extracted from my previous articles.

![](https://miro.medium.com/v2/0*ijymHg47WOyW2cI-.png)

*Caption: This card shows an AI-generated “My Judgment” section under a brief original note, evaluating the source material against values inferred from my past writing.*

I think this one summarized it very well. I can just sign off on it. If another one is inaccurate, I will revise it just the same.

Another example is a set of thoughts from September 29, 2025, about building Agent systems. The card includes not only “My Judgment” but also a link to the original text.

![](https://miro.medium.com/v2/0*DYD0DIKh8YQh3kSq.png)

*Caption: This card includes both an AI-generated “My Judgment” section and a link back to the original source note about building Agent systems.*

Clicking through takes me directly back to the original record. That record itself is an audio note, which discusses topics such as reinforcement learning and multi-agent collaboration.

![](https://miro.medium.com/v2/0*_dClYxqh64rNEMtd.png)

*Caption: The original source record is an audio note in Get notes, showing how the generated card can be traced back to richer source material.*

The newly generated card and the original material are connected through bidirectional links. You are not only seeing an “AI summary card”; you can return to the source at any time, check where it came from, and find richer original information.

Over the course of that one night, OpenClaw + Codex used my Skill to generate more than a thousand cards, along with the citation relationships between those cards and the original materials.

![](https://miro.medium.com/v2/0*gxelZUb4iwND5L5h.png)

*Caption: The network graph visualizes the large number of generated cards and the links among them, though it is more useful as an overview than as a detailed map of every structure.*

Of course, this kind of big network graph is mostly there to look impressive. It shows that there are many items and that links have been established, but you cannot expect to understand the entire structure from one network diagram.

The truly useful next step is this: **how to use these cards to help you generate topics and article outlines**.

To make candidate topics easier to browse, I asked it to periodically generate a simple HTML page showing the top three candidate topics.

I tried this out and found that, in terms of vividness and readability, it is indeed more intuitive than static Markdown.

![](https://miro.medium.com/v2/0*AmcSDeEBKBH0YvtS.png)

*Caption: The generated HTML page presents the top three candidate topics, making the automatically surfaced ideas easier to browse than a static Markdown list.*

It listed three candidates for me, all of them automatically surfaced through cluster analysis of card links. Let’s focus on the first one: a teaching-slide pipeline.

The system tells me how many cards support this topic, how tightly they are connected, and why the topic is worth writing about.

Then it gives me an initial outline.

![](https://miro.medium.com/v2/0*2VvB5j0CeoBXk3VV.png)

*Caption: The outline page connects each proposed module to supporting cards and their sources, so the article structure grows from the existing note network rather than from an invented outline.*

This outline is not pulled out of thin air. It places different modules alongside the corresponding cards. Under each module, I can keep clicking through to see which cards support it and which original sources those cards came from.

That is much more reliable than first writing an outline, then forcing AI to find materials for it — or worse, letting AI invent the materials.

The benefits mainly come in two parts. Under every module, I can trace back to the original cards. I’m not asking AI to improvise supporting material on the spot; I’m looking for structure inside an existing material network. When writing the article, I’m not pouring fresh concrete at the last minute. I’m assembling something from structural components that already exist.

![](https://miro.medium.com/v2/0*FzWvKIOOyBo1HyoO.png)

*Caption: This topic page shows the supporting cards behind a proposed article idea, reinforcing that the outline is assembled from existing materials rather than fabricated on demand.*

Even more interestingly, it also tells me what gaps this topic currently has.

![](https://miro.medium.com/v2/0*3fMPNysY6EcXNsLf.png)

*Caption: The gap analysis flags weaknesses in the candidate topic, such as missing opposing viewpoints, insufficient adversarial scrutiny, and a lack of cases or empirical evidence.*

For example, in this case it says the topic lacks an opposing perspective, lacks adversarial scrutiny, and lacks cases and empirical evidence.

That is valuable.

Because when we write articles, one of the easiest traps is to keep following our own argument in a straight line. The more smoothly we write, the more complete it looks — but in fact, it may never have been stress-tested by opposing views.

Now the system reminds you: the evidence is not enough here; this part needs patching.

Of course, in order to carry my laziness all the way through, I also wrote into the Skill that if it discovers gaps that need to be filled, it can automatically call a deep-research skill — in other words, ask AI to look for additional evidence, materials, and cases.

There is still a gate here: materials found through supplementary research are not inserted directly into the article. They first enter a pending source library. Only after I confirm that the sources are reliable and truly relevant to the current question will they be turned into new cards and linked with the existing cards.

That creates a very interesting loop.

Your card network generates topics; the topics expose gaps; the gaps trigger supplementary research; the supplementary research becomes new cards and returns to the network.

Doesn’t that feel a bit like “growth”?

## Timeliness

When I showed this system to my students, their eyes went wide.

But one student asked a very good question:

If we bring in all the old materials, it does look rich. But won’t there be timeliness problems? For example, old tools, old models, expired announcements, and so on — will the system still turn those into cards?

I said: good question.

Look at this image.

![](https://miro.medium.com/v2/0*LTjec8F2QWrisaW-.png)

*Caption: This processing log shows that the system was not blindly turning every source into a new card; it was skipping some old, time-sensitive materials.*

This was a record from the processing run at around 6:09 that morning. At the time, it did not blindly turn every source into a new card.

Why?

Because it skips some content that is strongly time-sensitive and already fairly old.

For example: limited-time free offers, invitation codes, and version news about models or tools. Those things may have been valuable at the time, but once the window has passed, letting them enter a long-term card system would instead pollute the network.

So what enters the card box should not be all information. It should be information suitable for long-term reuse.

This is crucial.

A Zettelkasten is not a trash can. It is not a “come one, come all” warehouse for materials. It should be more like a sieve: filtering out short-term noise and keeping what can be reused across time.

## Sharing

After seeing it, my student was excited and asked me: Teacher, how can we get this?

I said I would share it with everyone.

He said, great. Teacher, if you don’t make it public, I was going to run over to your GitHub and grab it.

I thought to myself: is this a student, or a highway robber? 😂

Fortunately, I had already planned to share this Skill publicly. The GitHub address is here:

[https://github.com/wshuyi/zettel-builder](https://github.com/wshuyi/zettel-builder)

![](https://miro.medium.com/v2/0*WibP5W-WzE2RzbPh.png)

*Caption: The GitHub repository for the zettel-builder Skill is available at the link above, with installation and usage details.*

Oh, right — if you find it useful, feel free to give it a star while you’re there.

This Skill is still evolving quickly. By the time you read this article, the GitHub version is very likely newer and better than the version I recorded in the video.

## Closing Thoughts

Finally, let’s return to the opening question: can AI actually help you build a Zettelkasten?

My answer is: yes — but you have to understand where it can help, and you also have to know what it cannot do for you.

It can help with mechanical tasks.

For example: extracting candidate cards from large amounts of material, finding original sources, building bidirectional links, generating lists of related cards, regularly scanning for candidate topics, and spotting evidence gaps.

Are these things important? Yes.

Are these things annoying? Extremely.

If I had to do all of them entirely by myself, would I keep going? Probably not.

So it makes sense to let AI do this grunt work.

You can think of it as a prep cook in the kitchen. It washes the vegetables, cuts them, sorts them, lays them out, and may even remind you: this dish needs a little more acidity, and that one is missing a side ingredient.

But the chef is still you.

What the final dish tastes like, which ingredients go into the pan, which judgments stay, which views get deleted, and which conclusions you take responsibility for — those decisions are still yours.

I know some serious practitioners of the Zettelkasten method may worry at this point: if you don’t digest the cards by hand yourself, will they become empty shells without real understanding?

I understand that concern.

If your field does not change quickly, the boundaries of your questions are stable, and you can steadily and slowly polish cards by hand, that is a kind of happiness.

But not every field has that luxury.

When the external environment changes quickly, tools keep iterating, and information density keeps rising, fully manual organization may lose out on efficiency. At least for me, if I still relied entirely on manual organization, many topics might never have time to grow.

What we need to do is not hand our thinking over to AI. It is to lower, as much as possible, the mechanical barriers that stop us from starting to think.

AI helps you chop the vegetables.

The chef is still you.

Happy AI-assisted Zettelkasten writing.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- • [Can You Safely Hand a Literature Review Over to AI? A Look at How to Build a Research Workflow That Doesn’t Go Off the Rails](https://mp.weixin.qq.com/s/-wchS6BmYj8z71BZJYnY8A)
- • [Claude Skill Snapshot: Add an “Undo Button” to Your AI Skill Iteration](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
- • [Too Many Card Notes to Remember? Let AI Help You Automatically Find the Connections](https://mp.weixin.qq.com/s/DYxMcuhDCeXSsufywfOwQQ)
- • [In the AI Era, Stop “Doing Homework” and Start Creating Your Own “Work”](https://wshuyi.medium.com/in-the-age-of-ai-stop-doing-homework-start-creating-your-masterpiece-009cf4f37388)
- • [Getting Started with Claude Skills: How AI Upgrades from “Mouthpiece” to “Worker” in One Article](https://mp.weixin.qq.com/s/GS3aFsSKajo_Uk3LAkC_Yw)
