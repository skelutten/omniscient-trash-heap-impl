---
title: "Why I’m So Excited About Codex’s New Cross-Device Remote Control"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/why-im-so-excited-about-codex-s-new-cross-device-remote-control-8f6ad15848c0"
published: "2026-05-19"
fetched: "2026-09-08"
reading_time_min: 18.9
tags: ["openai-codex", "remote-control", "openclaw"]
member_only: true
body_source: "medium-session"
---

# Why I’m So Excited About Codex’s New Cross-Device Remote Control

### Did your AI get stuck halfway through, waiting for your approval? Now your phone can save the day.

![](https://miro.medium.com/v2/0*9ubbvSoRZHIUHW4c.png)

## The Frustration

Your AI agent is grinding through a long task and then, halfway in, throws a decision at you: option A or option B? You happen to be away from the computer, so it just sits there waiting. By that point you may already be asleep, fully expecting to wake up to a finished result.

Morning comes, you walk back to the computer hopeful — only to find that the job that should have wrapped up hours ago actually stalled out after five minutes. Now you have to rerun the whole two-hour job. And the question the agent stopped to ask? Nothing remotely important. Losing two hours of progress to a courtesy check-in is maddening.

Or the opposite flavor: the AI decides on its own not to bother you and just makes the call. Hours later, you find out the whole path was wrong and you have to tear it down and start over. If you’re lucky, the upstream materials haven’t been overwritten or thrown out and there’s still something to restart from.

Sound familiar?

It does to me — more than once.

So I’ve long wanted a way to check on and steer an AI agent from my phone, anytime. Not because I enjoy playing overseer — it’s just to catch and clear those nagging little snags in time. One small decision, one nudge in the right direction, and the whole task often goes much more smoothly.

If you’ve been following my writing, you already know the routes I’ve tried.

**Option one: tmux + SSH + Termius.**

That was the path I worked out for myself back in 2025. I’d run the command-line version of Claude Code or Codex (the kind you operate by typing into a black-and-white terminal window) directly on a remote machine, use tmux — a little utility that keeps a remote program alive even if your connection drops — to hold the session open, and connect from my phone with an SSH client. I wrote that one up in detail in [How to Break Free From Your Hardware and Enjoy “Vibe Coding” Anytime, Anywhere?](https://wshuyi.medium.com/how-to-break-free-from-hardware-constraints-and-enjoy-ambient-programming-anytime-anywhere-656bd5dd34ab?postPublishedType=initial).

![](https://miro.medium.com/v2/0*xHYzD6sBJovrDMRT.png)

*A phone-side view of a Claude Code session running remotely: a long article-writing pipeline (stylist → coordinator → researcher → outliner → writer → editor) each handed off to its own agent and progressing in real time.*

That setup really did solve the “don’t let the task die just because I walked away from the desk” problem. The task is running in the cloud, after all. I pick up the phone later and the conversation is still going.

But the downsides were just as obvious. What you see on your phone is essentially a shrunken-down black-and-white terminal window. There may be several sessions on it. Which one do you reconnect to? You’re on your own to remember. You scroll back through the run log by hand. Worst of all is when the AI stops mid-task to ask which option you want, and you’re squinting at a five-inch screen trying to parse a whole wall of scrolling text.

That isn’t commanding the AI from your phone — that’s using the phone as a monitor. Better than nothing, sure, but I hit my limit fast.

**Option two: OpenClaw / Hermes.**

OpenClaw — most of us call it by its affectionate nickname, the little crayfish. The whole point of its original design was the exact pain I just described. Crayfish’s author, Peter Steinberger, just had the nerve to actually go build it, and with himself plus AI he hammered the thing into existence.

In short: the earliest OpenClaw plugged an AI agent — at the time, mostly Claude Code — into everyday chat surfaces like WhatsApp, Telegram, and Signal. I wrote two pieces about this — [One Person, One Week, Three Names — What Actually Happened With OpenClaw?](https://mp.weixin.qq.com/s/DaBC0bBy4V9uv6GPQSfYiw) and [Claude Code, Codex, OpenClaw — How I Got Them to Work Together](https://mp.weixin.qq.com/s/Sa8j6v29txgXv9raezs8TQ).

The little crayfish (OpenClaw) gave ordinary people their **first** real taste of “ask the AI to do things for me, as easily as sending a text.” You don’t need to understand remote login, you don’t need to understand session persistence, you don’t need to learn the command line. You just open Telegram or Feishu, send a message to a bot — and the barrier to entry drops through the floor.

![](https://miro.medium.com/v2/0*ytsV4v6z2bQv_dxH.png)

*An OpenClaw bot conversation: the author asks for an OpenClaw “image of the soul” and the bot ships an AI-rendered cyber-crayfish illustration in reply — message-to-creative-deliverable in a single chat round.*

But OpenClaw has its own issues. A framework being general-purpose and widely shared doesn’t mean it inspires confidence for real work. These frameworks are still in their wild-frontier phase, and updates will occasionally blow up your whole workflow. Every upgrade, you’ll see people online bracing for impact. My friend Lao Fan, for example.

![](https://miro.medium.com/v2/0*1HpzkdX1dkTLsteO.jpg)

*An X post from Lao Fan (@lukfan): “Has anyone installed the latest crayfish version yet? Any landmines? Let me know — I’m hesitating for a few minutes before pulling the trigger.”*

On top of that, plenty of pros believe the genuinely hardcore work — project-level development, say — really does need a more mature AI framework like Claude Code or Codex behind it for any peace of mind.

In fact, back in March, Claude Code already supported being remote-controlled from the phone Claude app. I was excited enough to put it through a test then too.

![](https://miro.medium.com/v2/0*X3X448Dn8sRrRyGA.png)

*The author’s Weibo post from March 2026: “Claude Code now officially supports Telegram. Today’s the day — what’s the point of any earlier intent? I was banging on this for months, and even the crayfish had no rival, exactly because Peter built OpenClaw to drive Claude Code through messaging apps like Telegram.”*

The thing is, the remote-connection process kept hitting little glitches back then. Sometimes I even ran into crossed wires between sessions.

OpenClaw and Hermes have kept improving, but in my actual testing, for serious tasks — especially ones that need complex reasoning — they’re still a notch short. The only harness framework that can really go toe-to-toe with Claude Code is Codex. So when on earth was Codex going to be reachable from a phone?

As luck would have it, that’s exactly when I spotted the Codex update.

## What Just Shipped

A little after 3 p.m. on May 15, I opened a fresh Codex chat in the ChatGPT app on my phone.

![](https://miro.medium.com/v2/0*hEZXrtTg1nxpcUAe.png)

*A new Codex thread targeting `vps-medium`. The input box reads, in Chinese: "/goal — build a small game for learning the principles of recurrent neural networks."*

Notice that when Codex rolled out this new feature, the showcase example walked you through driving a Mac running macOS from your phone. As long as the Mac has Codex’s “allow remote control” toggle on and is signed into the same account as ChatGPT on your phone, the phone will auto-detect and pair with it. You’re issuing orders from the phone, but that Mac is the machine actually doing the work.

![](https://miro.medium.com/v2/0*w_-n0IcRPU0EVUHL.png)

Worth thinking about what that actually means, though. **That Mac has to stay powered on, lid open, never sleeping, never shutting down, with the Codex desktop app running the whole time.** Put another way: whether you’re stepping out, traveling for work, or heading home for the holidays, that Mac has to stay parked at home spinning its wheels twenty-four hours a day — the electricity bill, the wear on the fan, the battery health, all real costs. Worse, while you’re away, one power blip, one auto-update reboot, one app crash, and **the phone loses the connection**. You try to hand it a task from the road and find it’s gone dark — nothing to do but groan.

So for this run, I didn’t point the target at the Mac. I picked one of my own Linux cloud machines instead.

![](https://miro.medium.com/v2/0*_gU3yb0gZwsGcxYF.png)

*The author’s Weibo post from May 15: “ChatGPT iOS now supports connecting to a remote CodeX. By default it tries to reach a macOS app — but the Mac has to stay on. I just connected to my cloud server, ran `/goal` at Extra High reasoning + fast thinking, and asked it to call the right skill and write me a math game. Worked nicely."*

A “cloud machine” is really just a Linux server you rent from a cloud provider — the industry term is **VPS** (Virtual Private Server — you don’t actually buy a physical box; the data center carves out a slice for you and you pay monthly). Its **whole job is to be online 24/7** — somebody else’s fan, the data center’s electric bill, a backbone network. Mine is called `vps-medium`. With it grinding away uncomplainingly, my Mac can be shut down or closed whenever I want, with no bearing on whether the task runs. Tencent Cloud and Alibaba Cloud both rent VPSes, and they discount them heavily around the big Chinese shopping holidays.

![](https://miro.medium.com/v2/0*JlUKPZrI8r_Fkioa.jpg)

*The Alibaba Cloud ECS landing page (in Chinese), advertising “Secure and Reliable Cloud Server ECS” with starter instances from ¥99/year for individuals up to enterprise-tier c9i instances — typical Chinese-market VPS pricing the author is referring to.*

Enough setup. For this remote Codex run, I typed `/goal` into the input box (that's Codex's built-in "tackle a complex task" command — basically telling it to reach the goal no matter what), and asked it to build a small game to help students understand how recurrent neural networks work. I cranked the reasoning tier up to Extra High (the maximum) and set thinking speed to fast, which makes execution about 1.5× quicker.

Once you dispatch the task from ChatGPT on the phone, you get to watch it play out. The Codex on the cloud quickly reached for the right `interactive-html` skill, broke the job into five steps, ran them in order, and reported progress back to me in real time.

![](https://miro.medium.com/v2/0*UyyMaexN6l6GT7H7.png)

*Codex (Chinese) narrating the plan back to the author: “I’ll work within the narrow scope of `interactive-html` — not a full teaching module with voiceover, just a 2D interactive mini-game whose core visual goal is to show how hidden state carries past information but decays or gets overwritten by new input." A five-step task list follows (define structure → implement HTML/CSS/JS → add run notes → in-browser smoke test → wrap up).*

Before long, the result was in.

![](https://miro.medium.com/v2/0*Y488Gg9InFnIg3Hq.png)

*The resulting mini-game “Memory Loop Lab” (Chinese UI): level 1 of 4, “The Last Signal.” A learner injects cold/hot inputs into a tanh-gated RNN cell to see how hidden state h_t evolves under different input-weight (W), recurrent-weight (U), and bias (b) settings.*

Learning recurrent neural networks isn’t what today’s piece is about, so I won’t unpack how this game can help you study them.

After dinner, I opened a fresh conversation for something completely unrelated — topic mining.

![](https://miro.medium.com/v2/0*Dm5OyCat1-zvF79X.png)

*Codex (Chinese) running the topic-mining workflow: it confirms the source of truth as `~/.claude/skill-registry/topic-inspiration/SKILL.md`, scopes the change narrowly to extending the trigger phrases, kicks off an independent review pass, and lists a four-step task list (confirm carrier → draft trigger expansion → revise upstream skill → sync downstream and verify).*

This time it correctly picked the `topic-inspiration` skill, and I was happy enough with the result that I posted my take:

> *Codex remote control honestly feels way more dependable than the crayfish — and more capable. If we’d had this in the second half of last year, the crayfish wouldn’t have had a market.*

A reader was quick to push back on my one-sidedness, though:

![](https://miro.medium.com/v2/0*T3OCryLRSLVKQxOm.png)

*A reply from @howell9511 (in Chinese): “My guess is the crayfish’s author had a hand in this one too — it really is well-built.”*

Fair point — none of this happened until after the crayfish’s author joined OpenAI.

Let’s talk through why a phone can reach and command Codex on a VPS directly, and how you actually set it up.

## How It Works

Codex isn’t picky about which machine it “lives” on. **The model is this: one machine keeps a Codex process running at all times, and any device you’ve previously authorized — your phone, another computer — connects to it through OpenAI’s secure channel to hand it work and watch the results come back.**

That always-on machine has a proper name — the **host** (the machine actually doing the work). The host can be your Mac, of course, or it can be a Linux box in the cloud. Oh — and [Windows support is coming soon](https://openai.com/index/work-with-codex-from-anywhere/?utm_source=chatgpt.com), so stay tuned.

![](https://miro.medium.com/v2/0*iWXhUdRGyMIHBhrN.png)

*A screenshot of OpenAI’s Codex availability docs (English body) annotated by the author in Chinese: highlighted is the line “Support for connecting your phone to a Windows Codex app will roll out soon,” confirming the upcoming Windows path.*

As long as that host has Codex running, has network access, and you’ve authorized it before, OpenAI’s relay handles the rest. That relay is called the **secure relay** — you can think of it plainly as an “encrypted middle station”: your phone and the host don’t talk directly; everything goes through OpenAI in the middle, and nobody in between can see the contents.

What links up the path from phone ChatGPT to your Mac and to your VPS is a capability OpenAI just officially shipped on May 14, called **Remote SSH** (“SSH” is the standard way developers have long used to securely log into other people’s machines — think of it as “a master key for opening a remote machine’s door”). It lets the Codex apps on different devices auto-recognize the “remote addresses” you’ve already saved on your machine, and register those remote machines as available hosts.

Below, let me walk you through how to set it up.

## Setting It Up

In the macOS Codex app, the setup is dead simple. Update to the latest version and it’ll prompt you, opening up the cross-device control feature.

![](https://miro.medium.com/v2/0*DoOkNSq1is4xap-j.png)

If you have multiple Apple devices, as long as they’re all signed into the same ChatGPT account, the connection just happens.

![](https://miro.medium.com/v2/0*w1o3TLbHUTsfsCPP.png)

But if you want to drive the command-line Codex on a VPS, there’s some configuring to do.

At the top of `~/.codex/config.toml`, add these three blocks — none of them optional:

```ini
approval_policy = "never"
```

```
sandbox_mode = "danger-full-access"
```

```
[features]
```

```
remote_control = true
```

Then mark the directories you want to allow remote operations on as trusted:

```csharp
[projects."/home/you/some-workdir"]
```

```
trust_level = "trusted"
```

That’s it.

Here’s why each piece matters.

```csharp
[features]
```

```
remote_control = true
```

This is the master switch. With it off, Codex doesn’t listen on the remote-control channel and commands from outside processes get dropped on the floor.

```ini
approval_policy = "never"
```

This line is here because Codex by default pops an approval prompt at every key moment — “before running a command,” “before writing a file” — and waits for you to press y/n. Just like the situation I described at the top. This line tells Codex to make those calls itself and stop waiting on keyboard input.

```ini
sandbox_mode = "danger-full-access"
```

The reason for this one is that Codex’s default sandbox restricts file writes, network access, and command execution. Remote tasks routinely need to install packages, write across multiple directories, and call external APIs. Those operations get tagged dangerous and the sandbox blocks them — what you’ll see is the task running halfway and then silently hanging.

`danger-full-access` straight-up grants full filesystem access. **That means whatever command the remote sends, it'll run.**

But even with all three of those set, the first time Codex enters a directory it hasn’t seen before, it’ll still pop a “do you trust this project?” prompt. Remote calls will hang there too. So you need to explicitly mark every directory you plan to let the remote enter as `trusted`.

Once that’s all done, you can add the Codex on your VPS as a controllable target from macOS.

![](https://miro.medium.com/v2/0*kmXPvFJ9m81LO2j4.png)

From then on, this VPS shows up persistently in your list of controllable devices.

![](https://miro.medium.com/v2/0*UnD4Q_wV4KUKXCOX.png)

Next time you start a new task in Codex on macOS, you can pick this VPS to run it on.

![](https://miro.medium.com/v2/0*lStrmHKvX3A485sX.png)

For instance, I can ask: what exactly has Codex been up to on my VPS the last couple of days?

![](https://miro.medium.com/v2/0*SeHB1ojo2KWcNgxp.png)

*The Codex desktop app on macOS, with the author’s prompt in Chinese (“What have I been doing the last two days?”) and Codex starting its reply: “Looking at the verifiable traces on this machine, your main threads over the past two days were these…”*

And likewise, the phone can drive it just the same.

![](https://miro.medium.com/v2/0*SIvJ2ubGPJkxhvJk.PNG)

*The phone-side Codex app showing the same `vps-medium` host as the active target and the same Chinese conversation thread ("What have I been doing the last two days?") — desktop and phone driving the same remote VPS.*

But reading this far, you might be wondering — if my phone can already drive a Codex that’s running 24/7 on a VPS that never sleeps, why bother going through the trouble of driving the Codex on my own macOS machine?

Because some jobs genuinely have to happen on your macOS box.

## Use Cases

These recent Codex updates are really a full combo punch. On top of the cross-device remote control you’ve already seen, two more very important capabilities ship with it.

The first is Computer Use — Codex directly operates your computer, performing clicks, confirmations, text entry, all of it.

For instance, a couple of days back, I set up the software on my new computer entirely with Codex’s Computer Use feature.

![](https://miro.medium.com/v2/0*vwmjnRcW-RhNoDR7.gif)

See that very pronounced mouse cursor in the screen recording above?

That’s actually all Codex auto-locating and operating the pointer, and the typing inside is fully Codex too.

The second capability is the Codex browser extension.

Right now it supports Chrome — install the Codex extension in Chrome and it can drive your browser to carry out a whole sequence of operations.

That means it can leverage sites you’re already signed into and actually pull off the kinds of actions only a real user could.

A lot of those actions are off-limits for scrapers, but because Codex is acting as your personal agent and what it does is indistinguishable from what a user does, it’s hard to actually flag.

For example, here I’m using the ChatGPT app on my phone to call the Codex extension on my Mac and dig through my X timeline today for discussions worth reading.

![](https://miro.medium.com/v2/0*KE2BH66w7o_3oMAb.jpeg)

*The phone-side Codex (Chinese) reporting back: “I scanned the most recent screens of your X ‘Following’ and ‘For You’ feeds. Most-worth-reading category: 1. Claude Mythos / Google Cloud — timeline chatter that Mythos has surfaced in the Google Cloud Console; read it as ‘restricted private preview,’ not a public release. Sources: Berryxia.AI’s discussion, Anthropic’s official article, and the Google Cloud Claude page.”*

There’s more.

![](https://miro.medium.com/v2/0*yrKbIIOXaPmqTs5d.jpeg)

*Codex (Chinese) continuing the briefing: “Also worth a quick read — 4. WeChat Reading `.skills`: if real, this is the 'content library + personal highlights/notes + agent' route, same broad direction as Spark CLI. 5. WorldSeed: multi-agent deception / collusion / hidden-intent experiments — more agent-safety simulation than capability breakthrough. 6. Codex App remote-control stability feedback from Guo Yu: home-machine remote execution is shaky, servers are steadier, iOS model selection is limited."*

Computer Use and the Chrome extension can’t run in a VPS environment right now. So if you want to fully tap Codex’s powers on a personal computer, reaching macOS remotely from your phone and driving it that way is a seriously powerful setup.

## What the Hot Takes Get Wrong

There are a few **common misreadings the breathless coverage tends to push**, and I want to set them straight.

“ChatGPT can now directly control all your computers.” Sounds dramatic, but it’s not accurate. More precisely: **ChatGPT / Codex is the end that “reaches the other machine,” connecting to hosts that are already authorized, online, and running Codex**. It hasn’t magically obtained system-level control over an arbitrary number of computers.

So is it the case that “the Codex on my MacBook can read the chat history and files on my Mac mini”? That needs a caveat too: **you have to connect to the Mac mini as a host**, and what you access is the folder on the Mac mini that **you’ve designated as a Codex project**, plus that machine’s own runtime environment. It’s not that the MacBook’s local Codex automatically tunnels in and reads the Mac mini’s entire drive. The official docs are explicit — files, every login password and token, permissions, local tooling, **all stay on the machine where Codex actually runs**.

There’s also “this means their chat histories are shared.” More accurately: **the conversation state currently in flight can be synced or handed off between the devices you’ve authorized**; it’s not that every Codex project across two computers automatically merges into a shared memory pool. What syncs is **the conversation you’re currently running**, not a tangled-up merge of files and backstories from several different computers.

What OpenAI is going for isn’t “remote desktop” — it’s making Codex an engineering agent that can work inside “the environment where the code and tools actually live,” while you steer it from whatever authorized device you have on hand. **In other words, the runtime and the control surface are now decoupled.**

## Security

The better this setup gets, the more seriously we have to talk about security.

You may have already wondered: if I crank a cloud machine wide open on permissions, what if the agent goes off the rails? Fair question.

I know plenty of articles reach this point and start hedging — “please use with caution,” “mind the risks.” That kind of line is the same as saying nothing. Let me try this from a different angle.

Running Codex on a VPS, since it’s physically isolated from the personal computer you use day to day, you can hand it broader permissions — pretty much what we set up earlier.

But running Codex on a local Mac is where permissions and privacy need real attention. Codex isn’t your average chat window. It reads project files, may run commands, modifies files, watches terminal output, watches test results, looks at screenshots, looks at diffs — it can even read local config.

On a local Mac, four kinds of things deserve special caution.

**First, your personal folders.** Don’t hand the whole Home folder to Codex right out of the gate. A single project folder is plenty. When it needs more access, grant it case by case.

**Second, credentials and keys.** Remote login keys (SSH keys) under `~/.ssh`, access keys for various cloud services, API tokens for external interfaces, the little files browsers use to remember who you are (cookies), login tokens for various chat tools, passwords sitting in config files — don't casually expose any of these to AI.

**Third, system-level permissions.** LaunchAgent / systemd (the former on macOS, the latter on Linux — both are the mechanism that lets a program “auto-start at boot” or “live in the background long-term”; once altered, every subsequent boot follows the new setting), login items, network proxies, SSH config, scheduled jobs, bulk file deletion, push-to-publish — don’t casually approve any of these on your phone. On your phone you might be waiting for the subway, eating, or talking to someone — your attention isn’t really on the agent. One tap on “approve,” and a few hours later you find it deleted something important — don’t let that happen.

**Fourth, screenshots and terminal output.** It’s convenient that you can see Codex’s feedback on the phone, but it’s also a risk. Screenshots and output by default may contain paths, usernames, internal project names, sensitive snippets. Before you forward a screenshot to a support chat or a discussion group, give it a once-over for anything that needs to be redacted.

## Looking Back

Looking back over the whole road — from tmux’s black-and-white terminal sliver, to OpenClaw’s chatbot front door, to today’s phone ChatGPT talking directly to Codex on a VPS — on the surface it’s tools iterating; underneath, it’s the same fixation driving everything: **I don’t want “which computer I’m sitting in front of right now” to decide whether I can move work forward.**

Each generation cracked the most maddening problem of the previous one and exposed a new shortcoming of its own. tmux meant your task no longer died when you closed the laptop, but it left you scrolling through logs on a five-inch screen by hand. OpenClaw dropped the bar to “send a message and you’ve handed off a job,” but the truly hardcore tasks that need deep reasoning were beyond it. Claude Code’s phone-based remote control had barely surfaced when the ban wave hit, and the sandcastle-on-the-beach uneasiness never quite left.

Codex’s combo this time — Remote SSH crossing device boundaries, Computer Use taking over the desktop, the Chrome extension reaching deep into the browser — for the first time genuinely splits “runtime” from “control surface.” The VPS is your tireless 24/7 foreman, your Mac is the skilled hand who can actually work the desktop and browser, and the phone in your hand finally returns to the role it should have been playing all along: **call a direction at the key fork in the road, then go on with your life.**

Of course, this shape isn’t the end of the road either. How permissions get granted, where to draw the safety boundaries, how context truly flows seamlessly across multiple machines — these questions only have a workable answer today, nowhere near “set it and forget it.” But at the very least, when your AI asks you at two in the morning whether it’s option A or option B, you can roll over, tap twice on your phone, and go right back to sleep.

That alone earns its keep.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- • [How Do You Manage Your AI Prompts Effectively? I Found a Best Practice That Works on Desktop and Mobile](https://wshuyi.medium.com/how-can-you-effectively-manage-your-ai-prompts-0bbdcd12d4bb)
- • [AI Apps Are Booming — Is Your “Moat” Wide Enough?](https://mp.weixin.qq.com/s/-H-Q70wBTDaN7APYnRhI6g)
- • [Claude Skill Snapshots: An Undo Button for Iterating on Your AI Skills](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
- • [[Livestream Replay] Quick Notes Live Q&A and Tool Walkthrough](https://mp.weixin.qq.com/s/6QhlvhIRXSwmsX1abMHPbg)
- • [Is AI Really About to Wake Up? My Hands-On With ChatGPT](https://mp.weixin.qq.com/s/TLbgYH8vKneRrI0sl4g-Vg)
