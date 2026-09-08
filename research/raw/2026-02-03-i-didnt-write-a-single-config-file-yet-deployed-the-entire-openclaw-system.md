---
title: "I Didn’t Write a Single Config File, Yet Deployed the Entire OpenClaw System"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/i-didnt-write-a-single-config-file-yet-deployed-the-entire-openclaw-system-b2b941bba3db"
published: "2026-02-03"
fetched: "2026-09-08"
reading_time_min: 17.8
tags: ["openclaw", "claude-code"]
member_only: true
body_source: "medium-session"
---

# I Didn’t Write a Single Config File, Yet Deployed the Entire OpenClaw System

### Thanks to Claude Skills, these experiences compound over time, accumulating like rolling interest.

![](https://miro.medium.com/v2/0*IxAwv5_QFs-SuM6r.jpg)

Late at night, right before bed, I was burrowed under the covers with my phone, and sent a Telegram bot an arxiv paper link with a message: “Turn this paper into an explainer video.” Then I turned off the lights and went to sleep.

The next morning, I saw Telegram’s overnight replies (thank goodness I had Do Not Disturb on) — the video was ready, complete with TTS-cloned audio of my own voice, animated charts, and subtitles, all automatically saved to the VPS download directory.

After watching it, I forwarded it to the paper’s author: “So? What do you think?”

They replied: “Stunning — better than my own paper 👍”

I cracked up.

This system — from sending a Telegram message, to [OpenClaw](https://openclaw.ai/) orchestrating on the VPS, to Claude Code executing the task, to the results being sent back to my phone — involves systemd service management, environment variable propagation chains, LLM messaging mechanisms, SOUL.md behavioral rules, multi-model routing, and a dual-bot architecture. Roughly a dozen config files in total.

How many did I write myself?

I counted: turns out it was **zero**.

Every config file, every systemd service, every sync script — Claude Code wrote them all. The only two things I did throughout the entire process were: tell it what I wanted, and make the calls at key decision points.

But if you think this is some fairy tale where you press a button and get results, let me pour some cold water on that — this thing took me six days of on-and-off work.

Claude Code helped me look up docs, write configs, install software, and troubleshoot issues, but it also took wrong turns, guessed incorrectly, and sometimes spent ages fixing the wrong thing.

Six days, from zero to functional and polished. The journey was far more interesting than the destination.

![](https://miro.medium.com/v2/0*ZgKtiuXrBBOlWfQH.png)

Today’s article was written at the request of a friend from my community, “Longzhongdui.” I’m sharing the highlights and the pitfalls of the process with you.

## The Spark

It all started on the evening of January 26th.

I stumbled upon a project called Clawdbot and found it pretty intriguing. It runs on a local machine or a VPS and lets you assign tasks through common messaging apps like Telegram, so you can remote-control an AI on your server right from your phone.

My reasoning was straightforward — I wanted to dispatch tasks to Claude Code anytime from my phone, whether I was out and about or lying in bed, without having to sit at a computer and open a terminal.

But here was the problem. Claude Code’s subscription doesn’t extend to third-party tools. You can’t take your subscription quota and hook it into some API gateway or self-hosted relay. Anthropic has locked that down tight — their subscription only works with their own CLI. **If you manage to break through, you risk getting your account banned, so I strongly advise against trying.** So the approach became: keep Claude Code running on the server, and find a way to “remote-control” it from outside.

Think of it like having a sewing machine at home that doesn’t support Bluetooth or Wi-Fi, but you can put a helpful assistant next to it. You call the assistant, tell them what to sew, they operate the machine, and when it’s done, they snap a photo and send it back so you can check if it meets your requirements. You never touch the sewing machine, and you don’t even have to be home. Clawdbot is that assistant.

I told Claude Code one sentence: “I want to install this project on a VPS, set it up with a GLM model, assign tasks through Telegram, and have Claude Code do the actual execution. Research it for me.”

That was it.

Then I watched it get to work. It invoked the [deep-research skill](https://github.com/wshuyi/deep-research) I’ve shared with you before. Eight steps, tearing through Clawdbot’s documentation top to bottom. A few minutes later, it presented a complete architecture plan: Telegram receives messages, Clawdbot uses GLM (a large model from Zhipu AI) for intent understanding — figuring out what exactly I want Claude Code to do — then calls the `claude` CLI via shell to execute the task, and sends the results back through Telegram.

I made one decision: use GLM as the entry point instead of directly exposing Claude’s subscription. Using GLM as an isolation layer is both secure and doesn’t violate the subscription terms. That decision was mine; the architecture plan was Claude Code’s.

![](https://miro.medium.com/v2/0*DLUCUR5qSxa0vCCW.png)

That was the entirety of my involvement in “architecture design” — listen to its proposal, then say “Sounds good, let’s go with that.”

## Building

From that point on, I was basically sitting back watching Claude Code put the pieces together.

It ran `npm install`, ran `onboard` for initialization, generated config files, wrote systemd services, set up heartbeat monitoring, and configured exec timeout parameters. Along the way, it even suggested I not reuse the old bot token I had lying around, saying that token had been tied to a previous project and it'd be safer to create a new one for proper separation of concerns.

Made sense to me, so I went to Telegram’s BotFather and created a new bot called Claide, then handed the token over. It plugged it into the config file, started the service, and told me to try sending a message.

I sent a message on Telegram, waited a few seconds, and the bot replied.

The feeling at that moment — how do I put it — was a bit like hiring a contractor, telling them “I want an open-concept kitchen,” then going out for coffee. When you come back, the wall’s been knocked down, the plumbing’s been rerouted, and the stove’s installed. You didn’t lift a finger the entire time. You’re not even entirely sure what specific work they did, but the result is right there — you turn on the faucet and water comes out.

Magical, right?

Don’t celebrate too soon.

A freshly renovated house always has a few quirks. Some you can’t spot at first — you only notice them after you move in.

## Cracks

The next morning, I couldn’t wait to take the newly built system for a spin. I sent my first real task through Telegram — a deep research run. This was heavy lifting: Claude Code had to search the web, sift through materials, and compile the output. I figured it’d take about ten minutes.

The task itself executed without issues. I checked the VPS and confirmed that Claude Code had indeed run and generated results.

Then — radio silence on Telegram.

I stared at my phone for ten minutes. Nothing. No results, no status update, not even a “working on it” indicator. Dead quiet, as if I’d never sent the message at all. Finally, I couldn’t take it anymore and sent: “Are the results ready?” The bot replied instantly: “Completed. Here are the results…” followed by a flood of research output.

Picture this — you ask a coworker to look up some data, they finish and quietly leave it on their own desk without telling you. Half a day later you ask, and they go, “Oh, that? Done ages ago.” Wouldn’t you be internally screaming?

I described the symptom to Claude Code: “Why do I have to manually follow up every time?”

It dug into the logs and found the critical timeline — Claude Code finished execution at 07:31, the system injected an “Exec completed” notification, then there was a full ten-minute gap of nothing until 07:42 when I manually asked, and only then did GLM start processing the results.

The issue was the message type. The completion notification was injected as a system message. When GLM received a system message, it just filed it away as background info and didn’t feel the need to say anything — it was waiting for me to speak first.

Claude Code’s fix was straightforward: modify SOUL.md. SOUL.md is OpenClaw’s behavioral rulebook for the LLM, essentially a “persona manual.” It added a rule marked as highest priority — upon receiving any system notification, especially task completion notices, immediately organize and send the results to the user without waiting to be asked. After the change, it worked.

But there’s a deeper lesson here. The first time Claude Code modified SOUL.md, I tested it and found it hadn’t taken effect. I said “still not working,” and it was puzzled. After more investigation, it discovered that the old conversation session had cached the previous version of the config, so the new rules simply hadn’t been loaded. It had to archive the old session and restart the gateway for the new rules to take effect.

The key point is that Claude Code itself didn’t realize this the first time. It edited the file and assumed it was done, overlooking the “loading” layer in between. This kind of mistake is extremely common — a human ops engineer edits a config and forgets to restart the service; Claude Code edits SOUL.md and forgets about config caching. It’s the same blind spot.

This was the first time I clearly realized: while Claude Code can tirelessly do your bidding, it has cognitive blind spots just like the rest of us.

## The Deep Pit

Starting on day three, things got dense and chaotic.

I sent a video task through Telegram — convert a paper into an explainer video. The video was generated, but when I played it — the voice was Edge TTS’s robotic tone, not the high-quality MiniMax voice I had configured, which was cloned from my own voice. So the difference was glaringly obvious.

I asked Claude Code: “Why did the TTS downgrade?”

Just that one sentence. Then I watched it investigate.

First, it guessed the config file path was wrong — opened `secrets.zsh`, checked it over, paths were fine, MINIMAX_API_KEY was there. Then it guessed it was a file permissions issue — ran `chmod` all over the place, everything that should be 600 was 600, not a permissions problem. Then it guessed that a Claude Code version update had changed how environment variables are read — checked the changelog, nothing had changed.

Three wrong turns, each one a dead end.

I just sat there watching the whole time, not intervening, because I didn’t know where the problem was either. But I could feel Claude Code starting to get “antsy” — its troubleshooting shifted from methodical to scattershot, poking around in unlikely places.

Then it seemed to realize it was flailing, gradually calmed down, and instead of guessing which layer had broken, started tracing the call chain from top to bottom. This chain had five layers: systemd starts the OpenClaw process, OpenClaw calls the exec module, exec invokes the `claude` CLI via shell, Claude Code runs a Python script, and in the Python script `os.environ.get('MINIMAX_API_KEY')` returns None. It added debug output at every layer and finally discovered — the environment variable was already missing at the first layer. The systemd layer simply didn't have MINIMAX_API_KEY at all.

The reason might sound absurd: when systemd starts a process, it doesn’t source your `.zshrc` or `secrets.zsh` at all. The world you see in your terminal and the world Clawdbot sees through systemd are two parallel universes. No matter how perfectly you've configured things in your terminal, as far as systemd is concerned, none of it exists.

After finding the root cause, things still weren’t over. Claude Code tried using systemd’s `EnvironmentFile` to load environment variables, only to run into another snag — `EnvironmentFile` requires the format `KEY=value`, with no quotes and no `export` prefix, but `secrets.zsh` uses `export MINIMAX_API_KEY="sk-xxx"`. Incompatible formats, and systemd doesn't throw an error or warning when it encounters improperly formatted lines — it just silently skips them. This "silent failure" is the worst kind of trap.

Ultimately, Claude Code devised a dual-file auto-sync solution: maintain a conversion function that, whenever `secrets.zsh` is updated, automatically converts its contents into a systemd-compatible format and writes them to a separate `.env` file. The systemd service config points to this `.env` file. Only then was the five-layer propagation chain finally connected end to end.

![](https://miro.medium.com/v2/0*I3pABzythSqDdXs5.jpg)

What impressed me about this process wasn’t the technical details, but the real state of Claude Code’s troubleshooting — it didn’t find the answer right away. It guessed wrong, took wrong turns, and wasted time on dead-end paths. Pretty much like a junior engineer who lacks experience but tries really hard. The difference is that it doesn’t get tired, doesn’t get frustrated, and after guessing wrong three times, it can still calm down and switch strategies. It doesn’t need you to comfort it, and it won’t complain that the problem is too hard.

That same day, something even worse happened. I sent a PDF to the bot, wanting it to extract key content and make a summary. The bot straight-up froze — spun its wheels for a long time, then replied with something completely irrelevant.

Claude Code checked the logs and was startled by a number. That message had 137,213 tokens. Normally, when I send a message, it’s about 500 characters. This time? 200,516 characters. Four hundred times the usual.

The PDF had been inlined into the message body as plain text — two hundred thousand characters of raw PDF content, dumped wholesale into GLM. GLM’s job was supposed to be understanding “what you want to do,” but instead it was forced to first “read” an entire multi-page paper. The context window was maxed out, and the actually useful part — “make me a summary” — was drowned in an ocean of two hundred thousand characters.

Once again, Claude Code modified SOUL.md, adding PDF defense rules — when excessively long content is detected, extract only the user’s instructions and pass the file path to Claude Code for processing. You handle the intent, it handles the content — each sticking to their own lane.

You’d think things would be smooth sailing from here?

By day four, multiple problems erupted simultaneously. The Chinese text in a paper-to-video conversion displayed as `\uXXXX` escape codes — over eleven hundred garbled characters. The paper's author information had been replaced by AI hallucinations with completely fabricated English names — the original authors were Fan Zhenjia, Zhang Yunong, and Yang Lijuan, but the video showed Pengyi Zhang, Dan Wu, and Shuyi Wang. Even the journal name was changed from the *Journal of Library Science in China* to "Journal of Documentation" — all AI fabrications. Background images were missing, charts were missing, and scene rendering used the wrong component — carefully designed visual elements had gone completely unused, replaced by a stripped-down shell.

Staring at the screen, I gave my feedback and added: “I’m frustrated.”

That wasn’t a platitude — I was genuinely frustrated. You spend days having Claude Code build this system, and every day brings new bugs. Fix one and two more pop up. It felt like robbing Peter to pay Paul. You start wondering if you chose the wrong path — maybe this stuff just shouldn’t be configured by AI.

## The Turning Point

When I said “I’m frustrated,” Claude Code’s response caught me off guard. It didn’t offer empty comfort, no “I understand how you feel” platitudes. Instead, it immediately listed every unresolved issue and started working through them one by one.

Unicode garbled text — it ran a regex scan across all TSX files and replaced over eleven hundred `\uXXXX` escape sequences back to UTF-8 Chinese characters. Author information hallucinations — it wrote protective rules into the Skill config, requiring future video generation to extract metadata accurately from the source PDF, with no AI fabrication allowed. Missing background images — it traced back to a routing error in the rendering component, found the carefully designed scene file that had been sitting idle, and connected the route.

Every bug was investigated, fixed, and documented. More importantly, it turned every pitfall into a rule and stored it in the Skill config — so if the same type of issue occurs again, there’s a documented reference instead of starting from scratch. These lessons transformed from “something I remember” into “system configuration” — transmittable organizational memory.

And Claude Code could also keep an eye on Clawdbot’s operations, analyzing various activities.

![](https://miro.medium.com/v2/0*enqurRVco62CP-yW.png)

At this point, feeding it a paper produced videos that were genuinely satisfying.

![](https://miro.medium.com/v2/0*mMv-z2J_E7kMre3e.png)

But just as I was starting to smile, trouble showed up again.

This time, though, it wasn’t Claude Code’s fault.

On day five, something both funny and headache-inducing happened — the Clawdbot project changed its name three times in a single week.

Originally called Clawdbot — because Clawd is a play on Claude, riffing on the lobster claw pun. Picture a lobster reaching out its big claw to operate your computer — pretty vivid imagery. The project’s [GitHub](https://github.com/openclaw/openclaw) stars were climbing fast, and then [Anthropic sent a trademark protection request](https://www.trendingtopics.eu/clawdbot-moltbot-anthropic/). Understandable — Clawd and Claude sound nearly identical, and Anthropic’s legal team was bound to take notice.

So Clawdbot became Moltbot. Molting — as in a lobster shedding its shell — kept the crustacean theme alive. Clever name, but the `moltbot` package name on npm was squatted by a third party. If you ran `npm install -g moltbot@latest`, you'd end up with someone else's placeholder package, not the official one. The team had to tell everyone to keep using `clawdbot@latest` for installation until the `moltbot` package name could be reclaimed. This kind of npm name squatting isn't uncommon in the JavaScript community, but for anyone unaware, it's a well-hidden trap.

I wrote about this story in detail in [One Person, One Week, Three Names — What Actually Happened with OpenClaw?](https://mp.weixin.qq.com/s/DaBC0bBy4V9uv6GPQSfYiw). You can [click the link to read more](https://mp.weixin.qq.com/s/DaBC0bBy4V9uv6GPQSfYiw).

Soon after, Moltbot was renamed again. The final name landed on [OpenClaw](https://openclaw.ai/), meaning “open claw,” and the [stable version on npm](https://www.npmjs.com/package/openclaw) was finally free from squatters. DigitalOcean, Cloudflare, and other cloud providers have already rolled out [one-click deployment options](https://www.digitalocean.com/blog/moltbot-on-digitalocean), so in the future you may not need to set up a VPS from scratch. But the self-hosted route still has value — you maintain full control over your data.

I had originally planned to handle the migration during the Moltbot era. But the list of issues Claude Code laid out talked me out of rushing in.

After this final rename, I just told Claude Code: “They changed the name again. Handle the migration.”

![](https://miro.medium.com/v2/0*Q9yfTgMiZrImJVBs.png)

It handled every detail. Backed up existing configs (each file timestamped), installed the new version, created new systemd services, updated environment variable files, disabled old services and enabled new ones, and even wrote a rollback script just in case. I didn’t even need to know which files the migration involved — it covered everything. The only thing I had to do was when it said “there’s a task that’s been running for five hours, and the migration requires restarting services which will terminate it,” I said, “Fine, kill it.”

That was the full extent of my participation in the “migration decision.”

On day six, a new idea struck me. Up to this point, every task went through the same pipeline — whether it was making a video or checking the weather, it required spinning up Claude Code, the heavy artillery. It’s like calling a moving company to pick up a package — using a sledgehammer to crack a nut.

I told Claude Code one sentence: “I want two bots. One uses GLM for heavy lifting, calling Claude Code for complex tasks. The other uses Kimi K2.5 (a large model from Moonshot AI), handling lightweight tasks directly with Skills on its own, without needing to fire up Claude Code every time.”

Claude Code checked the [official documentation](https://docs.openclaw.ai/start/getting-started) and confirmed that OpenClaw natively supports multi-agent isolation and multiple Telegram Bot configurations. Then it designed a complete dual-bot architecture: Bot A, bound to GLM, serves as the “heavy-duty task executor” — when it receives complex tasks, it delegates to Claude Code for running scripts, editing code, doing data analysis, and other demanding work. Bot B, bound to Kimi K2.5, serves as the “lightweight assistant” — it handles tasks directly using all the Skills in `~/.claude/skills/`, things like answering questions, looking stuff up, and doing text conversions. The two bots each have independent workspaces, model configurations, and session spaces, completely isolated from each other.

![](https://miro.medium.com/v2/0*hHTorRTEiwJIfhCK.png)

I went to BotFather and created a second bot, gave the token to Claude Code, and it took care of the rest.

![](https://miro.medium.com/v2/0*7WUtGk453axXkKLD.png)

From solution design to configuration to functional testing, all I provided was a token and a one-sentence description of what I wanted.

Of course, if you really think Kimi K2.5 can only check the weather, think again.

Because it’s natively multimodal, it’s excellent at interpreting images.

As a Chinese-built model, it can even compose poetry.

![](https://miro.medium.com/v2/0*NUnYvwPAMXaAfVGk.png)

Kimi + OpenClaw can even perform deep research tasks using your existing Claude Skills, following your instructions.

This also shows us that in the future, many tasks don’t necessarily have to be tied to Claude Code. It gives us more options and more control.

From a single bot with one model on day one, to two bots with two models and a light/heavy split by the end — the architecture evolved continuously. And throughout it all, I was only ever “describing what I wanted.”

## Retrospective

After six days, what I want to share with you from this experience isn’t “how amazing Claude Code is,” but a more practical takeaway.

What did Claude Code do for me? Research, installation, configuration, debugging, migration, architecture design. From the first day’s one-sentence request to the sixth day’s dual-bot architecture, every concrete task was done by Claude Code. I never wrote a single config file, never manually edited a systemd service, never read a single page of OpenClaw documentation myself.

But what can’t Claude Code do? It can’t guarantee getting it right the first time. The environment variable issue — it guessed wrong three times before finding the root cause. The SOUL.md edit that didn’t take effect — it didn’t realize the session caching problem on its own. The PDF bomb, Unicode garbled text, author hallucinations — none of these were foreseen. They only got fixed after they blew up. And by day four, when multiple bugs hit simultaneously, it couldn’t untangle the whole picture at once — it had to work through them one by one.

There’s also a very real limitation — the context window. Claude Code’s context is finite, and in a complex session that goes on long enough, it starts forgetting what was discussed earlier. You might assume it remembers a previous troubleshooting conclusion, but it may have already lost it. At that point, you need to feed key information back to it, or just start a fresh session from scratch. This “forgetting” isn’t a rare edge case — it’s a structural limitation that you have to factor into your expectations.

So what do you need to do? Two things.

First, describe your requirements clearly. You don’t need to know what systemd is, don’t need to understand how environment variables propagate, but you have to be able to articulate “what I want” and “what’s currently wrong.” “The TTS downgraded” — those few words are enough, clear and complete. Claude Code will figure out why on its own. But if you say “something seems off with the system,” it’ll struggle to help — because it doesn’t know what’s off either. The more specific your symptom description, the faster it can troubleshoot.

Second, make the calls at key decision points yourself. Use GLM or directly expose the Claude subscription? Terminate a running task during migration or not? What model for the new bot, and what role should it play? These aren’t technical questions — they’re about your needs and preferences, and Claude Code can’t decide for you. It can give you options and analysis, but the final call is yours. You’re the commander; it’s the advisor and the construction crew.

## Takeaway

This real experience of human-AI collaboration isn’t a sci-fi tale of “AI does everything with one click,” nor a cynical rant about “AI is useless.” It’s more like working with a very hardworking but inexperienced partner — you set the direction, they do the work; they make mistakes, you point them out, they fix them; and after fixing, they write down the lesson so they don’t make the same mistake again. You stumble through the pitfalls together, and you climb out together.

With Claude Code, someone like me — a lazy person who’d rather not read docs and write configs — can actually build things I couldn’t have built before. But the price is patience. You need patience to let it take wrong turns, patience to re-describe the problem when it guesses wrong, patience to take a deep breath on day four when bugs are exploding everywhere, and then say, “Keep going. One at a time.”

Fortunately, thanks to Claude Skills, these experiences compound over time, accumulating like rolling interest.

I think it’s a price worth paying.

Want to give it a try and let Claude Code help you set up OpenClaw?

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- • [The Transparency Revolution in AI Writing: How 7 Agents Used “Inner Monologue” to Collaboratively Produce a Tech Blog in 80 Minutes](https://mp.weixin.qq.com/s/IhqpOhE0sAtcyJaRhFmiWw)
- • [Claude Skill Snapshots: Adding an “Undo Button” to Your AI Skill Iterations](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
- • [Getting Started with Claude Skills: One Article to Understand How AI Upgrades from “Mouthpiece” to “Worker”](https://mp.weixin.qq.com/s/GS3aFsSKajo_Uk3LAkC_Yw)
- • [In the AI Era, Stop “Doing Homework” — Go Create Your Own “Works”](https://wshuyi.medium.com/in-the-age-of-ai-stop-doing-homework-start-creating-your-masterpiece-009cf4f37388)
- • [From Vibe Coding to End-to-End Content Creation: My Hard-Won Lessons from AI Collaboration](https://wshuyi.medium.com/from-ambient-programming-to-end-to-end-content-creation-the-pitfalls-and-insights-ive-gained-from-58c4108f2a95)
