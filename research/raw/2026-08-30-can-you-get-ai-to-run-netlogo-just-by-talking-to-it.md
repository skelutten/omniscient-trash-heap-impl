---
title: "Can You Get AI to Run NetLogo Just by Talking to It?"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/can-you-get-ai-to-run-netlogo-just-by-talking-to-it-3cd451e5573d"
published: "2026-08-30"
fetched: "2026-09-08"
reading_time_min: 23.3
tags: ["netlogo", "openai-codex"]
member_only: true
body_source: "medium-session"
---

# Can You Get AI to Run NetLogo Just by Talking to It?

### Give Codex the right permissions and capabilities, and you can drive the whole thing in natural language and have it operate NetLogo.

![](https://miro.medium.com/v2/0*i7EPYU0z18-FB1NB.png)

## The Barrier

On the morning of August 9, 2026, still buzzing, I posted this on Knowledge Planet:

> *This morning I used AI to drive a NetLogo simulation, using the built-in virus-spread model as an example. The AI tuned parameters fully on its own, ran multiple rounds of simulation to analyze randomness and the effects of intervention strategies, and produced a series of results. I never once dealt with the NetLogo interface, menus, or code editor — the results and visualizations just took care of themselves. Teaching this part is going to be a lot easier from now on.*

![](https://miro.medium.com/v2/0*GIoQCWjqoHl_Xaf2.png)

*Caption: A Knowledge Planet post from August 9, 2026: the author used AI to drive NetLogo, tune parameters, and produce analyses without touching the NetLogo UI.*

You may have heard of [NetLogo](https://www.netlogo.org/).

In the complex-systems simulation community, it’s widely used for teaching and research: free and open source, ships with a whole model library, and you can run ready-made models the moment it’s installed.

![](https://miro.medium.com/v2/0*q5j-9qZQqWP2jxK7.png)

People teach with it from elementary classrooms to graduate seminars, and thousands of researchers write papers with it.

![](https://miro.medium.com/v2/0*mNNjTXM4R2dvdFC_.png)

*Caption: A chat screenshot. The Chinese header says NetLogo claims “10,000+ papers,” and an OpenAlex subject-area table lists Engineering, Computer Science, and Social Sciences at the top.*

But for anyone who’s never programmed, the barrier is pretty high.

Back when I was on a Ministry of Education project studying the spread of false information, I used NetLogo’s built-in computer-virus model to build a model of how misinformation spreads on microblogs; that study came out in *Information Science*. I later looked back on the episode in my 2020 piece [How to Get Up to Speed on Complex Systems Simulation](https://sspai.com/post/58775).

![](https://miro.medium.com/v2/0*ymYWAGh3vae76a3b.jpg)

*Caption: The 2014 Information Science paper “A Microblog False-Information Diffusion Model Based on Complex-System Simulation,” by Wang Shuyi and Diao Hailun.*

The network diagram in the screenshot below is exactly what it looked like after migrating from the NetLogo virus model.

![](https://miro.medium.com/v2/0*VlPgo4wuidSNdqG3.jpg)

*Caption: A PDF page of that paper, with two NetLogo network screenshots of the migrated rumor model.*

In 2021, in [How to Get Up to Speed on NetLogo as a Complex Systems Simulation Tool](https://mp.weixin.qq.com/s/xc8e5Fo1R95tCPxSjlzE_A), I wrote that NetLogo’s “barrier is low, but the ceiling is extremely high.” Getting a model running isn’t hard. The hard part is going from “watching the animation” to “rewriting the model for your own question, running experiments, and explaining the results.”

Where’s the difficulty? Syntax, first. NetLogo comes from the Lisp family; the way you organize commands is quite different from ordinary high-level languages. People who’ve studied C, Java, JavaScript, or Python are not necessarily any more at ease on first contact than complete beginners.

![](https://miro.medium.com/v2/0*xN6C_dPA6UcbXN3X.jpg)

*Caption: A Swarma Campus video at 15:41, titled “NetLogo syntax,” comparing a NetLogo `count neighbors` command with its Lisp-like equivalent.*

And detailed NetLogo tutorials were scarce for a long time. In 2015, while I was a visiting scholar in the United States, I made a point of hauling home a thick English textbook, and I recommended English videos to graduate students. The students were stuck: “Professor, it’s all in English…”

Fortunately, in 2021, *An Introduction to Multi-Agent Modeling with NetLogo*, compiled by Swarma Club and produced by Professor Zhang Jiang and the Swarma Campus team, was published, finally giving Chinese researchers an easier on-ramp.

![](https://miro.medium.com/v2/0*ODrL7_ARPBuZhi7t.jpg)

*Caption: Cover of An Introduction to Multi-Agent Modeling with NetLogo, by Swarma Club, People’s Posts and Telecommunications Press.*

Even with an excellent Chinese tutorial, learners still have to read the model language, configure BehaviorSpace, and handle random experiments, output files, statistical plots, and anomalous results. The real barrier isn’t a single point; it’s a chain of interlocking moves.

That, recently, has started to change.

## What Changed

The change comes from AI coding assistants. Some of them no longer just write code; they can operate the software on your computer: install apps, click menus, run commands. That capability has a name: computer use — letting the AI look at the screen, move the cursor, click, and type the way a person would. Add multimodality, meaning it can actually read the interface and the charts on screen, and the two together are collapsing the old barrier of “learn the tool first, then talk about ideas.”

Take this trial of letting AI drive NetLogo. Natural language is how I said what I wanted; computer use let it see and click the GUI; multimodality let it read screenshots, curves, and interface state; file and command execution let it create models, run batches, and analyze data. The wall that used to sit between code and the graphical interface is starting to thin.

So on August 9, I ran a complete trial with OpenAI’s Codex. Codex is one of the AI coding assistants I use day to day; I already introduced it in [Claude Code, Codex, OpenClaw: How I Get Them to Work Together](https://mp.weixin.qq.com/s/Sa8j6v29txgXv9raezs8TQ).

This trial went from upgrading NetLogo, reading an existing model, designing and finishing 120 experiments, to recasting that model into a new one in another domain, running 120 more, and finally catching a chart error — **I didn’t write a single line of code the whole way**, just kept issuing instructions in Chinese.

When you’re done, I think you’ll see not only how to drive NetLogo with AI, but how to take the idea into your own research, in your own setting.

## Getting Started

The first thing I said to Codex was:

“Upgrade NetLogo to the latest version, and tell me what’s different.”

![](https://miro.medium.com/v2/0*l-alkjUdSXekzJYk.png)

*Caption: Codex chat. The prompt: upgrade NetLogo and report the differences. The reply: installed 7.0.3, stale Homebrew 7.0.2, official 7.0.4, then upgrade complete 7.0.3 → 7.0.4.*

Every fall I introduce students to complex-systems simulation methods, so I installed NetLogo last year. But you know how it is — software keeps updating, and last year’s install was already no longer the latest. I couldn’t be bothered to look up the version differences myself, so I just let Codex handle it. Ha.

Once Codex took over, it first took stock: what was actually on my machine was 7.0.3; Homebrew still had a leftover, already-invalid registration for 7.0.2; and the official current release was 7.0.4. The first ordinary upgrade got stuck on that leftover registration. It didn’t force it. It cleared the dead registration, reinstalled 7.0.4, then checked the install details one by one — the main program, the app signature (the credential that the software hasn’t been tampered with), whether it could run without the GUI — and moved the old version to the Trash as a fallback. Hmm. Pretty careful, I’ll give it that.

Of course, I only learned those details later, from the log. What I saw at the time was just: “Upgrade complete: NetLogo 7.0.3 → 7.0.4.”

After the upgrade, once NetLogo was open, I manually picked Virus on a Network from the built-in models.

![](https://miro.medium.com/v2/0*t_FLAidDg8puY0Rj.png)

Once it was open, the interface looked like this:

![](https://miro.medium.com/v2/0*8_9c5936dS1BgoWl.jpg)

On the left, the parameter controls; in the middle, the network view; on the right, the state curves.

## Reading the Model

Here is the second instruction I gave Codex:

“Walk me through this NetLogo model I have open.”

![](https://miro.medium.com/v2/0*Wymu6DVuPjgdsG6k.png)

*Caption: Codex chat. The prompt: walk me through the open NetLogo model. It identifies Virus on a Network and notes the code is an SIS/SIR hybrid, not a clean SIR.*

From the interface alone, it recognized this as the official sample [Virus on a Network](https://ccl.northwestern.edu/NetLogo/models/VirusonaNetwork), a model of a computer virus spreading on a network: the dots are computers, the links are paths the virus can travel; blue is susceptible, red is infected, gray has resistance. It also reported the baseline parameters on the interface: 150 nodes, 6 links on average per node, 3 initial infection sources, a 2.5% transmission probability per contact, a virus check every 1 tick (one step in the simulation), a 5% chance of recovery after detection, and a 5% chance of gaining resistance after recovery.

Where did that information come from? It had clicked the tabs up top itself and looked at the model’s built-in Info page and Code page.

![](https://miro.medium.com/v2/0*n6PMSKHga5LFlvg9.jpg)

The Info page is the author’s manual, covering what the model is for and how to play with it. The Code page is the corresponding code:

![](https://miro.medium.com/v2/0*IxrwtjTTOE-Q-LWj.jpg)

From the code, Codex pulled a detail the manual doesn’t spell out: although the model is often summarized as a classic SIR (susceptible, infected, recovered-and-immune) three-state model, the code is actually a hybrid of SIS and SIR. After infected nodes recover, most become susceptible again; only a small fraction gain long-term resistance.

Don’t shrug that off. It means that under the same parameter set, the virus may die out by chance in a few steps, or keep circulating for a long time. Every interpretation of the experimental results that follows rests on this mechanism.

I also asked Codex to leave evidence of a real run. It called NetLogo’s built-in Preview Commands Editor and actually executed `setup repeat 75 [go]`—that is, initialize, then run 75 consecutive steps:

![](https://miro.medium.com/v2/0*kEcSlHlW3zjBQGpo.jpg)

The red, blue, and gray nodes in the figure are states the model actually produced.

## Running Simulations

After that, I told Codex:

“Adjust the parameters reasonably, run it a few times, and help me compare.”

![](https://miro.medium.com/v2/0*BnXATjHW7KLfEj9D.png)

*Caption: Codex chat. The prompt: adjust parameters reasonably, run a few times, and compare. It proposes one-factor-at-a-time scenarios and 6×20 = 120 runs.*

Codex first settled on a simulation method: take the current parameters as baseline, and change only one key factor at a time. It also explained why: this is a stochastic model, a single run doesn’t tell you much, so each condition needs to be repeated many times, comparing peak infection, duration, and the final immune fraction — not drawing conclusions from one random outcome.

In the design, that became six scenarios: baseline, high connectivity (mean degree doubled from 6 to 12), high transmission (transmission rate doubled from 2.5% to 5%), slow detection (virus-check interval stretched from 1 to 4), fast recovery (recovery rate raised from 5% to 10%), and high resistance (resistance probability raised from 5% to 50%). Each scenario ran independently 20 times, 120 runs in all, observing at most 2000 ticks (time steps in NetLogo) each.

For the batch simulations, it used NetLogo’s built-in [BehaviorSpace](https://docs.netlogo.org/behaviorspace.html). You can think of it as an “experiment pipeline”: you register the parameter combinations and the number of repeats, and it runs them over and over, recording the data at every step.

![](https://miro.medium.com/v2/0*IyAMUXucHT8taNra.jpg)

Above is the list of the six experiments Codex configured. Below is the baseline experiment’s settings window: seven parameters, 20 repeats, the metrics collected each step, the start and stop conditions — all in there:

![](https://miro.medium.com/v2/0*wlMabzFYzxlMGpdD.jpg)

Batch simulation used to be the kind of job you learned by flipping through the manual. Now Codex configures it for you.

For the fast-recovery scenario, Codex first wanted to set the recovery rate at 15%, but that value exceeded the interface slider’s 10% ceiling. After detecting this itself, it discarded that batch of data and reran at 10%. Natural language lowered the operational barrier; it didn’t waive the discipline of simulation.

Once the 120 simulations had run, the results looked like this:

![](https://miro.medium.com/v2/0*LBhrcBAGeu_WVjZz.png)

The unusual row here is slow detection. Stretching the virus-check interval from 1 to 4 sent the mean infection peak to 86.1%, and all 20 runs still had infection at tick 2000; at the endpoint, 21.3% of nodes were still infected, on average.

## Making the Charts

The simulation results were in. I made another request:

“Visualize the conclusions you’ve reached, using whatever method fits.”

But I saw at a glance that Codex was trying to call a previously defined Skill. That didn’t match what I needed, so I stopped it immediately and added:

> *Don’t call any special-purpose tools. Use whatever method you think is most appropriate.*

Then I felt I still hadn’t made myself clear, so I paused again and refined the request:

“I don’t think what you need to show can be captured in a single chart. Use different kinds of figures for different kinds of questions. If you think it’s useful, feel free to use animations — go all out.”

![](https://miro.medium.com/v2/0*J0lUWJRz99joe8aq.png)

*Caption: Codex chat. The author stops a Skill call and asks for different figure types per question, including animation if useful.*

What it delivered was a set of figures divided by question. Each figure answers only one kind of question.

The first, an overview, answers how far apart the six scenarios are overall:

![](https://miro.medium.com/v2/0*z3mVJWBbUzEA5n5w.png)

*Caption: English key added. Original Chinese labels: Baseline, High connectivity, High transmission, Slow detection, Fast recovery, High resistance.*

The second, a distribution plot, answers how much difference randomness can actually produce under the same parameter set:

![](https://miro.medium.com/v2/0*4wTGwXxDX3sVl0rQ.png)

*Caption: English title and scenario key added around the original plot. Left violins = infection peaks; right = duration, with hollow triangles still infected at the cutoff.*

Among the 20 baseline runs, the short ones died out naturally in 3 ticks; the long ones dragged to 1769 ticks. Same parameters, wildly different fates. See? If you run it once and pick a curve that “looks typical” for the report, that’s not how you do it.

The third and fourth are a pair: the early trajectories answer how the outbreak takes shape; the full trajectories answer how long infection can drag on:

![](https://miro.medium.com/v2/0*ONc1SCYwbjVOP5uZ.png)

*Caption: Early-window infection trajectories with an English title and scenario key. Original panel titles remain in Chinese.*

The two have to be separate. If you only look at the full window, the early changes in fast recovery and high resistance get squashed; if you only look at the early window, you miss the long tail of slow detection.

![](https://miro.medium.com/v2/0*W1tNU2o2GjZ7ECHT.png)

*Caption: Full-window infection trajectories with an English title and scenario key.*

The fifth, a survival curve, answers the probability that infection is still alive at a given time:

![](https://miro.medium.com/v2/0*XuX1BxOdaidGNQjm.png)

*Caption: Kaplan–Meier survival of infection, with an English title and scenario key. The risk-set table rows are still in Chinese, in the same scenario order.*

The sixth, end-state composition, answers, when it ends or hits the observation horizon, how much of each state is there:

![](https://miro.medium.com/v2/0*xncaA64w7frubMNd.png)

It also made an animation, holding the axes fixed and letting the median infection trajectories of the six scenarios evolve together:

![](https://miro.medium.com/v2/0*YunGQy7rEKPVxw3O.gif)

*Caption: Animated median infection trajectories. English title and scenario key added; the in-frame legend is still in Chinese.*

Once the figures were done, Codex didn’t hand them to me right away. It ran a blind test of its own, and actually found six specific defects: long Chinese titles bunching into a lump, the animation’s time labels colliding with the legend, scenario names hard-coded into the survival plot, and so on. After fixing all of them, it started a separate independent review, checking the six scenarios, 120 runs, the number of censored cases (samples that still hadn’t ended at the observation horizon), and the file hashes (checksums for whether a file had been altered). The verdict: “Pass. Ready to sync and deliver.”

![](https://miro.medium.com/v2/0*isTB9cWJASNKQsPD.png)

*Caption: Codex’s own QA: it found six defects, fixed them, and an independent review passed 13/13 tests on the 6×20 runs, censoring logic, hashes, and figure readability.*

Only after that came the figures you saw earlier.

I never specified how any figure should be drawn. The only standard I gave was: **different questions, different figures**.

## Recasting the Model

The off-the-shelf model path was done: upgrade, understand, experiment, chart.

Next came what I actually wanted to do. I asked Codex for something new:

“This model is mainly about computer-virus spread. If I want to turn it into rumor spread on social media, what foundational changes do I need so the setup actually matches reality?”

![](https://miro.medium.com/v2/0*u6ImVyxHdWvustJT.png)

*Caption: Codex chat. The prompt: what basic changes turn the computer-virus model into social-media rumor spread? The reply splits contact, belief, and transmission.*

Note that this is, in fact, the model-migration work I once spent a great deal of effort finishing myself.

The first sentence of Codex’s answer made the direction plain: the crucial difference is that a computer, once infected, automatically and continuously spreads the virus; a person who sees a rumor may not believe it, may believe it but not share it, or may not believe it and still share it. **So you have to pull contact, belief, and transmission apart.**

Following that direction, it listed five foundational changes: states have to be split, so whether someone has seen it, whether they believe it, and whether they have shared it are each recorded separately; transmission has to change from “automatic infection” to “concrete sharing events”; the network has to change from undirected to a directed follow graph, because follower relationships are asymmetric and influence is highly uneven; exposure and sharing probabilities have to be jointly determined by the user, the source, the content, and the platform; and “recovery and permanent resistance” have to be replaced by processes that actually exist in the information world — stopping sharing, attention decay, accepting a correction.

It also drew a mechanism comparison of the old and new models:

![](https://miro.medium.com/v2/0*Tx5Mu7qC6-zpxmtd.png)

The left is the virus model’s worldview; the right is the rumor’s. One glance and you can see how the two worldviews differ.

## Rebuilding It

The plan was in. I kept asking Codex:

“Using the analysis you just did, build a new model, run multiple rounds of simulation the way you did before, and output the analysis and visualizations. Pay special attention to comparing it with the original model — spell out the differences and your insights.”

![](https://miro.medium.com/v2/0*yIseVQcMWRG1IGwH.png)

*Caption: Codex chat. After a second pretest clears a freeze bar, it locks parameters and will not retune because official results “look good.”*

It wrote the new model from scratch. Let me walk you through the key points.

Each user carries four independent facts: whether they have ever seen this rumor; how strongly they believe it, as a continuous value from 0 to 1; whether they have shared it; whether they have received a correction. 150 users form 4 communities; who they follow is biased toward their own community, and that bias is the skeleton of the filter bubble.

Every step of transmission is treated as a separate move. When a post goes out, followers have a 70% chance of seeing it in the feed; at the same time, platform recommendations push it to a small handful of users who don’t follow the poster. People who see it update their belief, then each decide whether to share. In the same cycle, if a rumor hits you from several different sources at once, the impact is larger than from a single source — that’s social reinforcement. When nobody is mentioning it anymore, belief slowly decays over time.

Debunking is a one-shot action: it deploys after a delay of a few cycles, and covers only a fraction of the people who had already seen the rumor at deployment time. People who see the rumor later don’t automatically get the correction. That corresponds to a one-time platform-level fact-check push, not round-the-clock moderation.

There’s another key rule: each person shares this rumor at most once. So “end” gets a new definition: once the queue of posts waiting to spread is empty, the sharing cascade enters an absorbing state — a state the system will never walk out of on its own. But notice: what’s absorbing is only the sharing. Belief does not absorb. Sharing can stop while the believers remain.

It didn’t jump straight into the official simulations. It ran pretests first. The second pretest cleared its own bar for freezing the parameters: across 8 baseline runs, coverage sat between 10 and 99 people, total shares between 3 and 35, absorption time between 1 and 12 ticks, with both quick die-outs and deeper cascades, and with the debunking able to intervene inside the transmission window. Then the parameters were frozen, and it specifically noted: it would not retune later based on whether the official results “looked good.”

What does the new model look like?

First, the settings interface. Parameters on the left; in the middle, a live directed follow network (empty at the start); curves and monitors on the right:

![](https://miro.medium.com/v2/0*GCLRI1Dn5Ocx3AIh.jpg)

*Caption: The new rumor model’s NetLogo interface before setup: Chinese buttons for Restore defaults, Setup current, Step once, and Run continuously; English slider names; empty network view.*

After setup, 150 nodes are split into 4 communities; the 3 red nodes are the initial sharers:

![](https://miro.medium.com/v2/0*GhBoemSyeV2xgEJr.jpg)

*Caption: After setup: 150 nodes in four communities, three red initial sharers. Monitors show 3 active sharers, 3 exposures, 3 believers.*

By tick 4, things had shifted. A cumulative 69 people had seen the rumor, 18 had shared, 12 had crossed the belief threshold, and the transmissible posts had already hit zero. The sharing cascade had absorbed, but the debunking hadn’t reached its deployment time yet:

![](https://miro.medium.com/v2/0*9vSaqOV2kMJJP_DL.jpg)

*Caption: Tick 4: 69 people have seen the rumor, 18 have shared, 12 believe, the post queue is empty, and fact-checking has not deployed yet.*

Advance to tick 7: the debunking deploys, 27 people who had previously seen the rumor receive a correction, and believers drop from 12 to 4. Cumulative viewers are still 69, cumulative shares still 18:

![](https://miro.medium.com/v2/0*fl7O-C8r1WMXIqWx.jpg)

*Caption: Tick 7: fact-checking deploys. 27 previously exposed users receive a correction; believers fall from 12 to 4. Cumulative viewers stay 69, shares stay 18.*

The new model has its own Info page and Code page too, with the description, the mechanism, and the bounds of interpretation all written in:

![](https://miro.medium.com/v2/0*FsQVsbnfKyzLG-SS.jpg)

On the Code page, the directed links, user attributes, and every procedure can be inspected:

![](https://miro.medium.com/v2/0*sAVTcp_F7kx6vib6.jpg)

## Batch Runs

The official experiments followed the same pattern: six scenarios, 20 runs each, 120 in all. It screenshotted the BehaviorSpace configuration as well. In the experiment list you can see 1 pretest plus 6 official experiments:

![](https://miro.medium.com/v2/0*UynTSVrBak9E-Fwb.jpg)

The top half of the baseline configuration: experiment name, 20 repeats, per-step recording. The bottom half: 17 recorded metrics, start and stop conditions, a 2000-tick safety ceiling.

![](https://miro.medium.com/v2/0*DLGTH9yZIJmqKp3H.jpg)

Those 17 metrics cover five kinds of information: state sizes, behavioral outcomes, transmission channels, cascade structure, plus random seeds and network diagnostics. There’s a wrinkle in the stop condition: it requires not only that the sharing cascade has absorbed, but also that any enabled debunking has finished executing, so the baseline doesn’t clock out before the correction takes effect and the correction data is lost entirely.

Here I’ll insert an accident that actually happened.

When the first official results came out, it did its usual quality check and found a blocking problem: the six experiment data files each had 20 runs, but the results were identical item by item. That is not a reasonable scientific result; the experiment configuration had never actually written the scenario parameters into the model — `clear-all` in the model wiped the scenario parameters BehaviorSpace had injected, so all six scenarios ran on the same parameter set. That batch of results and figures was ruled invalid. The model was changed to clear only agents, patches, plots, and drawing content, keep the experiment parameters, and then rerun.

This is a reminder for us: a batch job with “no errors” does not mean the experimental setup actually took. If you only check whether the files are all there, this task would have looked finished long ago. What research fears most is exactly this: “the files are all there, the conclusions aren’t reliable.” Codex took this checkpoint seriously on its own, and that’s why I was willing to let the conclusions move forward.

The rerun results looked like this:

![](https://miro.medium.com/v2/0*Eqk1QcLiLbhyeRfQ.png)

The strong recommendation row is the scariest. Raising the recommendation rate from 0.02 to 0.08 pushed coverage near the whole network. But the mechanism is worth spelling out: recommendation didn’t add a follow relationship to anyone; it opened a path around the follow network for each post. The network itself hasn’t changed; the path structure of information spread has already changed.

The high-follower seed row is the one I think anyone who has to govern this should care about most. The only change was picking the 3 initial sharers as the accounts with the most followers instead of at random, and coverage jumped from 38.7% to 92.2%. The content didn’t change; not one other parameter moved; only the starting points of the first posts changed. A coverage gap that large from changing only where it starts means the choice of origin is not something you can ignore.

I also had Codex make visualizations, same as before.

The overview figure for the global picture:

![](https://miro.medium.com/v2/0*-eYxGEM0RAzpwj8O.png)

*Caption: English key added. Left: exposure coverage. Right: people who shared.*

The distribution plot for random fluctuation and the long tail:

![](https://miro.medium.com/v2/0*cdOpWHy56Lu1xEYC.png)

*Caption: Violin plots of cascade size, absorption time, and depth, with an English title and scenario key.*

The absorption curves show how long each scenario’s cascade can last; all 120 runs absorbed, with no censoring:

![](https://miro.medium.com/v2/0*VSQ6X5Ega1_anMKP.png)

*Caption: Sharing-cascade absorption curve with an English title and scenario key. The risk-set table rows remain in Chinese, same order.*

The channel breakdown figure splits recommended exposure, cross-community exposure, and cross-community sharing, answering whether the scale comes from platform distribution or from key nodes:

![](https://miro.medium.com/v2/0*p4GoimhCbtDV9RVr.png)

*Caption: Channel breakdown with an English title and scenario key.*

The plot of relative effects uses the baseline as the reference and shows how far each scenario moves:

![](https://miro.medium.com/v2/0*2wh9Q5GJL61GMSxr.png)

## Off the Chart

By this point in the story, it looks like time for a tidy ending.

It wasn’t. As I flipped through the rumor model’s first-version trajectory plots, they looked more and more wrong, so I tossed it a question:

“Those line charts of yours look a bit off — some of the variation even overshoots the y-axis. Take a look and tell me what’s going on.”

![](https://miro.medium.com/v2/0*mWunbYXreDJKHQDi.png)

*Caption: Codex chat. The author flags curves that overshoot the y-axis. Codex finds the ceiling used a pooled 75th percentile while the band used a per-time 75th percentile.*

First, the figure itself. Look: in several panels, the curves and the shading clearly punch through the axis boundary:

![](https://miro.medium.com/v2/0*TO3hQIr0PpexHdMg.png)

*Caption: The broken figure — the exhibit. Purple believer bands punch through a shared y-axis ceiling. English title and scenario key added.*

After checking, it came back with an explanation.

It turned out the y-axis ceilings on those figures used the overall 75th percentile computed by mixing the values from all times and all runs together. But the shaded band drawn on the figure is the 75th percentile computed separately at each time point. Those two quantities are not equivalent: the per-time-point percentiles at the peak moments of spread can easily sit above the overall percentile that mixes peaks and troughs. So the axis was set by the pooled statistic, the curves were drawn from the per-time-point statistic, and punching through the ceiling was inevitable.

The data weren’t wrong. What was wrong was that “the statistic that sets the axis” and “the statistic that draws the plot” were not the same one.

The repaired trajectory plots look like this, each of the six panels using a y-axis that fits that panel:

![](https://miro.medium.com/v2/0*Bt6kYHrghL_XDRtt.png)

*Caption: The repaired figure: each panel has its own y-axis. English title and scenario key added.*

This stretch was also the most substantial contribution I made in the whole pipeline. Codex finished 240 valid official runs, drew a dozen-plus figures, and configured two rounds of BehaviorSpace, all without me lifting a finger — and before that, 120 first-version official runs had been discarded and rerun because of the configuration error, so 360 official runs were actually executed in total. But the “this figure is off” glance was mine.

The value of driving the modeling in natural language isn’t just “click the buttons for me.” More important, it lets a person stay in conversation about the research intent: first ask for execution, then look at the evidence; **spot an anomaly, keep asking; find the cause, fix it, and verify**.

AI Agents like Codex (AI assistants that can autonomously execute a chain of tasks) have lowered the barrier to using NetLogo; they have not taken the research responsibility away. Codex can read a model, operate the interface, write code, run experiments, analyze data, and draw figures. But why the research question is defined this way, whether the variables actually stand for the phenomenon you care about, whether the scenarios are fair to compare, whether an anomalous curve is worth distrusting, whether the last sentence of the conclusion can be spoken aloud — those still need a person’s judgment.

To put it in plain language: **being able to run is not the same as being able to publish**. Before you start, pass at least four gates — **construct validity** (do the variables actually correspond to the concept you’re studying), **empirical calibration** (do the parameters and results have real-world data behind them), **sensitivity and uncertainty** (are the repeats, random seeds, and parameter ranges enough), **replicable delivery** (are the model, experiment configuration, raw data, and analysis scripts complete enough that someone else can rerun them).

## The Takeaway

NetLogo itself hasn’t changed. The docs are still those docs; the language is still that language. Give Codex the right permissions and capabilities, and you can drive the whole thing in natural language and have it operate NetLogo.

NetLogo already brought complex-systems simulation down from “build your own toolkit” to “model inside a mature framework.” Natural-language AI assistants push one step further: you can first make the research intent clear, then let Codex work back and forth among the interface, the code, the experiments, and the data.

And this approach isn’t only for NetLogo, and it isn’t confined to multi-agent simulation. Because it can read figures and operate software, any research tool a local agent can access — if the interface is readable, the operations automatable, and the results checkable — Codex can in principle hook into that interface and turn intent into operations, even looping ones.

I chose the virus-spread example because 12 years ago I recast a new model from this one and published a paper from it, so I know it well. At least along the dimensions of batch running, quality checking, and visualization, the result of one of its analyses is finer than the weeks of hand iteration I did back then. That really does show that better tools have given research work a tangible lift.

You also saw that in some parts of this trial, Codex checked more finely than I did at the time. And I no longer have to rely on NetLogo’s built-in plotting; I can start from my own needs and produce better visualizations.

That said, execution can be handed to an Agent; research judgment cannot be outsourced — if you let go of the wheel entirely, you may drift from what you meant the analysis to do, or even let a wrong visualization contaminate the research. The judgments of direction and of value still have to stay firmly in your own hands.

Happy researching — may the AI actually help.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- [Perplexity or the Big Three? My AI Subscription List and How I Choose](https://mp.weixin.qq.com/s/QEAcGKlA6h3kQnY3B8lz3Q)
- [Claude Skill Snapshots: An Undo Button for Iterating Your AI Skills](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
- [Midjourney Can Read Images Now. Is That a Good Thing?](https://mp.weixin.qq.com/s/z6AYsYZGGJx3GNGQaybTRQ)
- [Livestream Replay: Live Q&A on Scratch Notes, Plus a Tool Demo](https://mp.weixin.qq.com/s/6QhlvhIRXSwmsX1abMHPbg)
- [From Dry Theory to Living Practice: How AI Agents Teach Complex Concepts with Interactive Tutorials](https://wshuyi.medium.com/from-dry-theory-to-vivid-practice-how-ai-agents-explain-complex-concepts-with-interactive-9f68d82b9ec8)
