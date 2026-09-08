---
title: "Reading the Same Paper: Where Does an AI Agent Beat the Chat Box?"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/reading-the-same-paper-where-does-an-ai-agent-beat-the-chat-box-c3cc68f5440d"
published: "2026-06-30"
fetched: "2026-09-08"
reading_time_min: 22.4
tags: ["ai", "academic-research", "data-analysis", "floatboat"]
member_only: true
body_source: "medium-session"
---

# Reading the Same Paper: Where Does an AI Agent Beat the Chat Box?

### What an AI Agent is really good at isn’t “understanding,” but “doing” — it can take over the kind of work that used to be “I can’t do it, so it has nothing to do with me.” That’s a door it opens for ordinary people; don’t miss it.

![](https://miro.medium.com/v2/0*1CCTBwocjXHSG8__.png)

## Hands-On

Using AI to read papers is old news by now. Ever since ChatGPT first blew up, [I’ve talked about the most basic use case over and over — in class and in my articles: drop a paper into the chat box and ask it what the paper is about and where the core mechanism lies](https://wshuyi.medium.com/with-ai-can-tackling-research-papers-turn-from-a-chore-into-an-adventure-a979ec4f5494).

![](https://miro.medium.com/v2/0*upZwZje3DoN26RsH.png)

*Caption: The familiar baseline — asking an ordinary chat box to summarize what a paper is about.*

If reading English is a slog for you, it can quickly lay it all out in Chinese.

![](https://miro.medium.com/v2/0*IX7SLtUmvheh5OvE.png)

*Caption: The chat box rendering the English paper into Chinese for easier reading.*

You can also ask it to draw a diagram to make the paper’s machinery more intuitive. By now we’re all plenty comfortable with these moves.

![](https://miro.medium.com/v2/0*9NsNqfgrJEvTBlxb.png)

*Caption: Asking the chat box to draw a diagram that makes the paper’s mechanism more intuitive.*

But today, what I want to talk about has a new lead. Not the chat box anymore, but an AI Agent (think of it as an AI assistant that can actually roll up its sleeves and do the work, not just keep you company chatting).

So here’s the question: when it comes to interpreting that same paper, what exactly separates an AI Agent from the old chat box?

The difference comes down to one thing — it can **roll up its sleeves**.

That sounds like a small thing, but it carries real weight. A chat box can read, explain, and sketch a diagram, but at the end of the day it’s just “talking.” An AI Agent is different — it can actually “do.” It can pull back a whole batch of related literature for you and weave it into a literature network; it can turn around and dig through your own knowledge base, cross-checking what you’ve squirreled away over the years against this paper; and when it runs into a data-driven paper, as long as the raw data is available, it can independently run a secondary analysis from scratch, reproduce the results from the original paper, and see whether they line up.

![](https://miro.medium.com/v2/0*INopIQYZGZJ_39c2.png)

And here’s the best part: precisely because it actually ran that whole data analysis from start to finish, it develops a deeper feel for the process, the results, and the methods the paper describes — so when it turns around to explain it to you, it explains it far more clearly.

That’s the difference “being able to do” makes — not a difference of degree, but of kind. As for what those words really mean, we’ll have to watch it do the real thing.

## A Worked Example

Let me give you a real example and walk through it from the top.

This example originally came from the Dedao platform — a paper introduced in the latest installment of Zhuo Ke’s column. It’s a thirty-year chimpanzee study, published in April 2026 in [Science](https://www.science.org/doi/10.1126/science.adz4944), and it carries real heft.

![](https://miro.medium.com/v2/0*18fDNkJ_0TQoOFZ5.png)

*Caption: The paper at the center of this walkthrough — a thirty-year chimpanzee study published in Science (April 2026).*

Leading it are Aaron Sandel of UT Austin (the University of Texas at Austin) and John Mitani of the University of Michigan; and the Ngogo long-term project that underpins the study traces all the way back to 1995, when Mitani and David Watts of Yale set it up together. The subjects are a group of chimpanzees in Kibale National Park in Uganda — this population, called Ngogo, is the largest known chimpanzee community in the world today.

Honestly, what this paper studies is about as far from my own field as you can get — they study animal societies, they study chimpanzees, and I’m a complete outsider. But the story itself is plenty stunning. The researchers followed this group of chimpanzees for thirty years and managed to witness and record, firsthand, a community going from rupture to splitting apart, all the way through to [the whole arc of “war” and even lethal violence](https://news.utexas.edu/2026/04/09/first-clearly-documented-split-in-worlds-largest-known-chimpanzee-community-leads-to-deadly-violence/), with not even the infants spared. Bear in mind, this kind of permanent split is exceedingly rare — genetic evidence suggests it happens only about once every 500 years. The study breaks the population into two branches and analyzes them with extraordinary precision: there’s the long-term record of these chimpanzees across time, and there’s coordinate point after coordinate point across space.

![](https://miro.medium.com/v2/0*Hhzj0P_ScysFNBeD.png)

(Image from the paper)

There’s actually a very specific reason I got interested in it. Zhuo Ke dropped a line in his introduction: the later data cleaning for this paper made use of Claude. That one line got my curiosity going. How exactly does AI work its way into a serious piece of scientific data analysis?

![](https://miro.medium.com/v2/0*evOmAWLl87VIdsD6.png)

*Caption: What sparked the author’s curiosity: a note (from Zhuo Ke’s column) that the paper’s data cleaning used Claude.*

And as it happens, I had just the right tool on hand. The AI Agent I’m using is called [Floatboat](https://floatboat.ai/?invite=7EXPCEYUNX), developed by my friend Shaoqing’s team. He recommended it to me, and I’ve been giving it a try lately.

![](https://miro.medium.com/v2/0*WvaJ6JgP6Cd9nags.png)

*Caption: Floatboat, the AI Agent used throughout this walkthrough.*

Today we’re not going to burrow into the paper’s internals and pick apart its conclusions. We’re only going to look at one thing: how to use an AI Agent to better grasp a paper’s main thread and its research methods, and how to put its publicly released data to work for you. For one, it helps me read the paper more thoroughly; for another, it’s a heads-up to you: next time you get your hands on someone’s public data, here’s how you might mine it for patterns.

## Q&A

What I opened is the Floatboat interface.

![](https://miro.medium.com/v2/0*F27Gn86ertzEpDfl.png)

*Caption: The Floatboat interface.*

Two things to get straight up front. First, I’ve already run this entire workflow end to end on my side — everything I’m about to show you is the real output. Second, just to mention it in passing, the model I picked is Opus 4.8. As for why I chose it of all the options, I’ll get into that at the crucial moment.

The first step is dead simple. I dragged that paper in and just asked: “What’s this paper about?”

![](https://miro.medium.com/v2/0*Z0r29yNSNuGwHcrl.png)

*Caption: The author’s opening prompt — “What does this paper say?” — with the paper PDF attached.*

After it read through, it told me this is an April 2026 anthropology and primatology paper published in Science, and then laid it all out point by point: core content, a one-line conclusion, the research background, the central debate, the key data and methods, the three phases of the event, and the main conclusions and significance. Drop a paper in and it quickly pulls out this skeleton for you.

![](https://miro.medium.com/v2/0*DRvOAmmgXCjV3I8Y.png)

*Caption: Floatboat’s structured breakdown: core content, a one-line conclusion, background, the central debate, key data and methods, the event’s three phases, and significance.*

At this point you might curl your lip: what’s so special about that? My Doubao, my DeepSeek can do that too.

True enough. But the upside of an AI Agent is tucked away in what comes next. Notice what it says right after: I can help you organize this into a one-page visual interpretation report, or distill it into a streamlined Chinese note, or even turn it into a slide deck.

![](https://miro.medium.com/v2/0*Qsg7wfcpzQPYQq7K.png)

*Caption: Unprompted, Floatboat offers next steps — a one-page visual report, a concise Chinese note, or a slide deck.*

Hanging beneath it is a whole string of features (it calls them “skills”) — making slides, web pages, and so on — each of which it can keep working on. Before I’d even said a word, it had already laid out “the things you might want to do next” right in front of me. This little move keeps popping up later, again and again.

So I went on to ask my second question: what methods did this study use? I’m not in anthropology, not in animal sociology, and I’m not familiar with any of this stuff — but I’m genuinely interested in its research methods.

![](https://miro.medium.com/v2/0*hLGjDCeuwM2dRIgf.png)

*Caption: The author’s second prompt — “What methods did this study use?”*

First it thought it over for a while — it’ll spread its thinking process out for you to see — then it laid out what it actually did, and gave me a pretty solid list.

![](https://miro.medium.com/v2/0*qWx3aV1v6N89FTR_.png)

*Caption: Floatboat’s rundown of the study’s methods.*

On the data collection side: thirty years of long-term field tracking (that one item alone is remarkable — no wonder it could land in Science), behavioral focal observation, demographic statistics, GPS home-range data, plus genetics.

On the data analysis side: social network and statistical analysis (put plainly, it’s drawing who’s close to whom and who pairs up with whom into a relationship network and running the numbers): multilayer network fusion, Leiden community detection (an algorithm for carving out the clustered subgroups within a network), modularity (a metric for how cleanly a network is partitioned into blocks), and longitudinal network change-point detection (finding the point on a timeline where the relationship structure abruptly shifts).

On the supporting-tools side: spatial analysis, data wrangling, plotting in R — and here is where Claude got used.

![](https://miro.medium.com/v2/0*B_vrxrfe8jMnI5VA.png)

*Caption: The supporting-tools section — spatial analysis, data wrangling, and R plotting — where Claude was used.*

It added one more note: the complete methodological details, supplementary materials, and the relevant datasets and code are all publicly open-sourced.

It specifically pointed out the most elegant thing about this study’s methodology: long-term behavioral observation, plus genetics, plus GPS spatial data — these three mutually independent lines of evidence all ended up pointing to the very same turning point, 2015. Three independent verifications, converging by different roads, which makes the conclusion all the more reliable.

![](https://miro.medium.com/v2/0*gGBShBm9EvPja-C8.png)

*Caption: Floatboat highlights the study’s elegance: three independent lines of evidence (behavior, genetics, GPS) all converge on the 2015 turning point.*

Having finished, it again volunteered a suggestion: would you like me to organize these methods into a methodology flowchart, or make a “methods and data sources” comparison table? See — it’s planning out my next step for me again.

But what I really had my heart set on was those words, “used Claude.” I was dying to know exactly how it was used. So I latched onto that thread and pushed further: in this paper, where exactly was AI used?

![](https://miro.medium.com/v2/0*tcsk3Q9a86B25a_x.png)

*Caption: The author presses further — “Where exactly was AI used in this paper?”*

It broke it down into three places.

![](https://miro.medium.com/v2/0*mTTiOIgLol1_1fdN.png)

*Caption: Floatboat splits the answer into three places.*

The first is the core methods — things like learned temporal network fusion, longitudinal network change-point detection, and the degree-corrected stochastic block model (a network clustering model that also factors in the differences in how many connections each node has). These are actually algorithms from statistics and network science, not the same thing as the “AI” I’m talking about (that is, large language models).

The second place is what I was really after: generative AI as a supporting tool, namely Claude — used for two things: organizing and analyzing the spatial data, and drawing and laying out the final figures in R.

![](https://miro.medium.com/v2/0*ISw9M0DXHSicQ7EW.png)

*Caption: The place the author was after — generative AI (Claude) as a supporting tool, used to organize and analyze the spatial data and to draw and lay out the final R figures.*

The third place is information like the authors and their institutions. It also mentioned in passing that it could give me a deeper rundown of that “learned fusion network.”

![](https://miro.medium.com/v2/0*y5pfc4KjnBmJ2e21.png)

*Caption: The third place — author and institution information.*

I thought that sounded good, but let’s set it aside for now and keep our eyes on the Claude thread.

## Getting Started

Up to this point, it’s all still been “asking.” What really made my eyes light up was the leap from “asking” to “doing.”

I copied that line from the acknowledgments word for word — the one where the paper says in black and white that Claude was used — pasted it in, and then made a slightly harder request: could you explain this part in a more pedagogical way, as if you were facing a freshman in a data science department?

![](https://miro.medium.com/v2/0*cE1l5EgwpO0E8ykz.png)

*Caption: The author pastes in the acknowledgment line and asks Floatboat to explain it as if teaching data-science freshmen.*

It said: sure, there’s actually a very important data science lesson hidden in here.

![](https://miro.medium.com/v2/0*T4j2xvWXm-_ZxPa5.png)

*Caption: Floatboat agrees, noting there’s an important data-science lesson hidden here.*

It first walked me through what this data pipeline looks like, then zeroed in on exactly how Claude was helping.

One: organizing and analyzing the spatial data — normally a mountain of repetitive, fiddly, error-prone grunt work.

Two: data cleaning and wrangling — how to fill in missing values, how to handle outliers, then merging, grouping, aggregating. It took care of all of it.

Three: drawing the figures in R and laying them out — tuning a single figure until it’s good enough to make it into Science.

![](https://miro.medium.com/v2/0*nCD0ZkQ6m4nNRY_U.png)

*Caption: Floatboat’s three points on what Claude did: organize the spatial data, clean and wrangle it, and draw/lay out the R figures to a Science-worthy standard.*

It explained it really well. I also noticed that when it finished, it handed me two options: either turn this whole pipeline into a teaching diagram, or just use the real data, pair it with some beginner-level sample code, and run it for me right then and there.

![](https://miro.medium.com/v2/0*a1wB2GvxeiVLwwxo.png)

*Caption: Two offered options — turn the pipeline into a teaching diagram, or run real data live with beginner-level sample code.*

I thought the latter sounded interesting, so I said: alright, let’s write some R using the real data.

I have to admit, I hadn’t opened up an R environment in ages — I work in Python all the time these days. But it was quick about it, said it’d run the actual code in R, and then really did produce a result for me.

![](https://miro.medium.com/v2/0*XqodBJqxMjEtQVhe.png)

*Caption: Floatboat runs actual R code and produces a result.*

Let’s take a look together at what came out:

![](https://miro.medium.com/v2/0*mQ1TKgiH1jZBSp34.png)

*Caption: The figure Floatboat produced (with a Chinese title) — the central group’s population after the split, falling from 107 to 80 over 2018–2024 (data: Sandel et al., Science 2026, Fig. 5C).*

This is the change in population numbers for the central group after the split, from 2018 to 2024 — you can clearly see the total trending downward. Honestly, the figure itself isn’t what I care about, but what it did next was something I found really useful. It gave me the entire R script in full, and when I opened it up, the comments were airtight — every step accounted for, one step at a time. That part I genuinely love.

![](https://miro.medium.com/v2/0*SXFsjdztePZZcKsL.png)

*Caption: The complete R script Floatboat returned, with step-by-step comments.*

It even broke it down piece by piece: what the core idea of this figure is, and how that plot command builds it up layer by layer.

![](https://miro.medium.com/v2/0*2EGu3LpAOcVqXhjM.png)

*Caption: Floatboat walking through how the plot command builds the figure up layer by layer.*

It even owned up to that first failure where the Chinese title wouldn’t display, and how it later solved it — so even the pitfalls it stumbled into, you can pick up along with everything else.

![](https://miro.medium.com/v2/0*eqrciXW5V175pHnR.png)

*Caption: Floatboat owning up to an early failure — the Chinese title wouldn’t display — and how it fixed it.*

When it was done, it added its usual line: I can help you change it if you need.

![](https://miro.medium.com/v2/0*EXgrFYT6vZ8VZWCu.png)

*Caption: Floatboat’s customary closing offer: “I can modify it for you if you need.”*

The paper does in fact have a population-change figure like this.

![](https://miro.medium.com/v2/0*ZUFVleWjAjoWgyG6.png)

*Caption: The paper’s own population-change figure, for comparison.*

But look — by this point, what I wanted was long past just “can it understand the paper.”

## Crossing the Line

What really got me excited was that batch of spatial data.

Staring at those coordinate points, I thought it over and made a request that was honestly a bit much. I told it: could you take its spatial data and make me a figure that’s beautiful, effective — even better than the one in the paper?

![](https://miro.medium.com/v2/0*OzgxH1XOKB7su0q2.png)

*Caption: The author’s bold prompt — make a figure from the spatial data that’s even better than the paper’s.*

That request has a certain nerve to it. Their figure ran in Science, and here you are, casually demanding one even better.

But Floatboat actually went and did it. It laid the whole process out for me to see: first it got hold of the complete data — the data itself is open source, with the corresponding CSV files here (that is, comma-separated tabular data), plus the region labels and so on — it said it had found everything, and then started processing it step by step.

![](https://miro.medium.com/v2/0*yz8rLFrOs89G5jjv.png)

*Caption: Floatboat reporting that it has gathered the complete open-source data (CSV files, region labels, and so on) and begun processing it step by step.*

After fussing with it for a bit, it handed me a curt five-word verdict: the results are excellent.

![](https://miro.medium.com/v2/0*a251ZAlfi0q8jfjv.png)

*Caption: Floatboat’s terse verdict: the results are excellent.*

How “really well,” exactly? Look: one figure is the pre-split distribution, 2011 to 2014; one is the post-split distribution, 2018 to 2023; plus a third figure, “the collapse of spatial overlap between the two groups” — the home ranges of the two populations, which originally overlapped on the map, with the overlapping portion steadily caving in until they finally stayed strictly out of each other’s territory. Put the three figures side by side and the story suddenly stands up on its own.

![](https://miro.medium.com/v2/0*3vMVybQpxLw4P-XV.png)

*Caption: The three maps Floatboat generated — the pre-split distribution (2011–2014), the post-split distribution (2018–2023), and the collapse of spatial overlap between the two groups.*

It also gave me a separate, streamlined two-panel version (two figures side by side, left and right) — click in and it’s a clean, crisp before-and-after comparison.

![](https://miro.medium.com/v2/0*rxzbwnmg6BIWDN5l.png)

*Caption: A separate, clean two-panel version — a crisp before-and-after comparison.*

The plotting script is attached right alongside it, so if you want to draw it yourself, or want to specifically tweak one part of it, you can just build on this as your base.

![](https://miro.medium.com/v2/0*fwy_4f67hw7PBkGn.png)

*Caption: The plotting script, attached so readers can redraw or tweak it.*

It made a point of emphasizing that this uses real data, a huge amount of it — a full 165,000 spatial points.

![](https://miro.medium.com/v2/0*37pG3Q4EuymXH97U.png)

*Caption: Floatboat stressing this uses real data — a full 165,000 spatial points.*

The figure at the bottom uses the yearly overlap data.

![](https://miro.medium.com/v2/0*vl1F81OkfsmRh5fJ.png)

*Caption: The lower figure, built from the yearly spatial-overlap data.*

It even went out of its way to double-check whether this was really its data, citing the [DOI](https://doi.org/10.1126/science.adz4944) (a Digital Object Identifier — a string of characters you can follow all the way back to the original data), with even the storage location marked out crystal clear.

![](https://miro.medium.com/v2/0*iAgJUzMdYJ3SLCzB.png)

*Caption: Floatboat double-checking the data’s provenance, citing the DOI and even the storage location.*

Finally, it laid out the full story this figure tells.

![](https://miro.medium.com/v2/0*pSB6X7VpdGp0VyhI.png)

*Caption: Floatboat narrating, in full, the story the figure tells.*

And it turned the tables on me: “Didn’t you ask for something better than the original?” Then it gave its reasoning: it had gone from a plain display up to a well-grounded argument, with a more complete narrative that reads more smoothly.

![](https://miro.medium.com/v2/0*_b102Cu_UT9YYj7M.png)

*Caption: Floatboat turning the tables — “Didn’t you ask for something better?” — arguing it upgraded a plain display into a grounded argument.*

At this point I was already pretty satisfied. But it added another line of its own: I can also make you a year-by-year animated version. I said go ahead then.

![](https://miro.medium.com/v2/0*1q1FrGEbkoq7Jikf.png)

*Caption: Floatboat volunteering to build a year-by-year animated version.*

Then it delivered the year-by-year animated version: one MP4 video, one GIF. In the MP4, as the years tick forward one by one, you can watch with your own eyes how that split unfolds across the whole figure, playing from the early 2010s all the way to 2023; the GIF loops, and you can see the changes from figure to figure just as clearly.

![](https://miro.medium.com/v2/0*FUhooKDUzhdEl31q.gif)

*Caption: The year-by-year animation Floatboat produced (a looping GIF), showing the split unfold across the map.*

It was also pretty considerate — it stacked up all 13 single-frame PNG images one by one, so if you want to look at just the 2017 one, you can pull it up in a snap.

![](https://miro.medium.com/v2/0*6nlu4AQtTkKHoZSW.png)

*Caption: All 13 single-frame PNGs, stacked so any single year (e.g. 2017) can be pulled up on its own.*

The rendering script, as usual, is fully public — transparent and detailed.

![](https://miro.medium.com/v2/0*00lmgYHGnKHDinee.png)

*Caption: The rendering script, again made fully public.*

There was a little side story in the process: the system’s default FFmpeg (a commonly used video-processing tool) was missing an encoder. How it spotted that, and how it worked around it — it laid all of it out plainly.

![](https://miro.medium.com/v2/0*_bxQ2iwyUKAq_BrI.png)

*Caption: Floatboat explaining a hiccup — the default FFmpeg lacked an encoder — and how it spotted and worked around it.*

I think this is exactly a kind of interpretability: what I ended up holding is a GIF file — you can see the result — and the entire path leading to that result — the frame-by-frame images, the segment-by-segment scripts, the pitfall it hit along the way — it hid none of it, and you can see that too. With a setup like this, going on to understand the data, to make use of it, even to find an angle of your own inside it, all becomes a lot easier.

## Making the Choice

But after all this excitement, there’s something I have to tell you in all seriousness.

You’ve probably noticed by now that the model I used from start to finish was Opus 4.8. Which model you pick is by no means a trivial detail.

Floatboat has a whole row of models to choose from.

![](https://miro.medium.com/v2/0*MwtWX6MysZp3G_ng.png)

*Caption: Floatboat’s model picker, with a row of selectable models.*

Opus 4.8, GPT-5.5 and the like are all marked “double” — plainly put, expensive. Is there a cheap one? Yes, like DeepSeek V4 Flash, which only burns 0.1. You can even switch on Auto Mode and let the framework pick the model for you.

![](https://miro.medium.com/v2/0*wcTep9UMqREzvw8F.png)

*Caption: Auto Mode, which lets the framework pick the model for you.*

But I have to give you a heads-up: leaving it to auto-select, the results sometimes can’t quite be trusted.

I happen to still have an earlier conversation saved: same prompt, same paper, the only difference being that that time I used Auto Mode.

![](https://miro.medium.com/v2/0*QhkejF0HuZKhkhgw.gif)

*Caption: An earlier run with the same prompt and the same paper, this time on Auto Mode (animated).*

And look at the result — the core conclusion it gave went off the rails right at the start: are we talking about chimpanzees, or about bonobos?

![](https://miro.medium.com/v2/0*UgvZmA_ceH0z9j8m.png)

*Caption: The Auto-Mode error the author flags — the output calls the animals “wild bonobos” (野生倭黑猩猩, red-boxed) when the study is about chimpanzees (黑猩猩).*

These two are not the same thing — a chimpanzee is Pan troglodytes, a bonobo is another species, with different habits and different social structures; they’re worlds apart. Yet in that passage, it conflated the two. And not just that one spot — the writeup it gave that time was also clearly far more cursory than the one I’m walking you through in detail here.

That’s exactly why, on tasks that are genuinely important and genuinely serious, when you use an AI Agent, having a good saddle isn’t enough — you’ve got to fit it with a good horse too. What’s a good horse? A better model.

![](https://miro.medium.com/v2/0*J6EPvrznOfe08GbN.png)

This choice-of-model question is best not handed straight to the framework’s auto mode to decide for you. The framework can help you do the work beautifully, but the judgment of “is this matter serious enough, is it worth a top model, can the result be trusted” — that’s a human’s job, and it’s the part you shouldn’t surrender.

Especially with things like paper interpretation, method extension, and data analysis — you pick a suitable, better model yourself, and only then does the result let you rest easy. A mistake like calling a chimpanzee a bonobo, if it lands in an analysis you’re handing in for the record, the bit of money you saved is nowhere near enough to fill the hole you’ll be patching later. At the end of the day, this isn’t about being stingy or not — it’s about whether the result can be trusted.

## Wrapping Up

Using Floatboat, this AI Agent, I ran a real, hands-on reproduction and verification of the geographic-location and population-interaction information in this chimpanzee paper. My takeaway after running it: the figures it produced may be more convincing than the original one in the paper, because they’re clearer and more detailed. More importantly, throughout the whole analysis it clearly didn’t just “understand” — it genuinely “understood more deeply”: compare its description of that split, of the before-and-after changes, between before the analysis and after, and the latter is plainly more detailed and more on point.

![](https://miro.medium.com/v2/0*LqmD-4NLVCcPidIP.png)

*Caption: Floatboat explaining how the animation tells the story, phase by phase — spatial overlap sliding from a high of 0.68–0.87 down to 0.26 by the 2018–2023 post-split period.*

This is what “being able to do,” mentioned at the start, looks like when it actually lands. A chat box can only tell you what a paper says; an AI Agent can roll up its sleeves, run the data for real, and turn around to digest the paper more thoroughly.

These days plenty of disciplines talk about being data-driven, but data analysis is exactly the kind of skill that, for far too many people, leaves them completely in the dark. In the old days, the raw data others painstakingly made public would sit right in front of you and might as well not exist — you weren’t going to touch it anyway, so it just sat there gathering dust. But now it’s different: as long as your goal is clear in your mind, the whole stretch from data to conclusion can be handed off to it to run automatically. This threshold has been genuinely lowered — don’t let a single “I don’t get data analysis” or “I can’t program in Python/R” shut you out before you’ve even started.

An AI Agent — you might as well simply think of it as a combination of **a model plus a framework**.

![](https://miro.medium.com/v2/0*KzF3wwUrkvR40NFA.png)

As for the model half, I still feel we should be free to choose it ourselves, because different models each have their own temperament and their own situations they’re good at. And the framework half, the more user-friendly the better. Take the example we just walked through: at the end of nearly every step, it handed me a few options I could click — the next steps it had figured out for me.

![](https://miro.medium.com/v2/0*JC5gHa_du1hDHkHb.png)

*Caption: The clickable next-step options Floatboat offers at the end of nearly every step.*

I especially love this feeling: it lays out my follow-up analysis goals for me ahead of time, so I don’t have to rack my brain — it gives a few solid options, and I just click one and I’m off.

Back to [Floatboat](https://floatboat.ai/?invite=7EXPCEYUNX), the framework itself. It really does have a lot of features, and it’s a bit different from your run-of-the-mill AI Agent — it pulls file browsing and web operations all into one tool, and there’s even a “calendar-driven” way of playing with it.

![](https://miro.medium.com/v2/0*ZaVOjtgwOUYWIuOM.png)

*Caption: Floatboat’s broader feature set — file browsing, web operations, even a “calendar-driven” mode — all bundled into one tool.*

But for me, it’s “a heavy instrument used lightly” — I’m basically just using [Floatboat](https://floatboat.ai/?invite=7EXPCEYUNX) as a general-purpose AI Agent framework. You can of course use Codex, or Claude Code, except that when you use those, you’ll find the models you can pick are often limited; whereas with [Floatboat](https://floatboat.ai/?invite=7EXPCEYUNX), these cutting-edge models are all on the table, with fewer restrictions. [If you’re interested too, you might as well give it a try yourself](https://floatboat.ai/?invite=7EXPCEYUNX).

What an AI Agent is really good at isn’t “understanding,” but “doing” — it can take over the kind of work that used to be “I can’t do it, so it has nothing to do with me.” That’s a door it opens for ordinary people; don’t miss it.

Here’s to happy AI-assisted research.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- [Can you hand a literature review off to AI with peace of mind? On building a research workflow that doesn’t fall apart](https://mp.weixin.qq.com/s/-wchS6BmYj8z71BZJYnY8A)
- [AI has made writing papers more efficient — but are you really using it right?](https://mp.weixin.qq.com/s/miqd66_e1kA_NRaxMPdI9g)
- [Getting started with Claude Skills: one article to understand how AI goes from “mouthpiece” to “worker”](https://mp.weixin.qq.com/s/GS3aFsSKajo_Uk3LAkC_Yw)
- [Still agonizing over whether someone’s work is “purely human” or has AI mixed in? You may need to get used to hybrid intelligence](https://wshuyi.medium.com/hybrid-intelligence-what-youre-really-buying-ee4ae5000188)
- [Claude Skill snapshots: an “undo button” for iterating on your AI skills](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
