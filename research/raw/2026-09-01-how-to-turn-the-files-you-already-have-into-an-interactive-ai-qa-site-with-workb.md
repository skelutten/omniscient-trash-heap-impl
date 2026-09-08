---
title: "How to Turn the Files You Already Have into an Interactive AI Q&A Site with WorkBuddy"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/how-to-turn-the-files-you-already-have-into-an-interactive-ai-q-a-site-with-workbuddy-652e4806172a"
published: "2026-09-01"
fetched: "2026-09-08"
reading_time_min: 18.3
tags: []
member_only: true
body_source: "medium-session"
---

# How to Turn the Files You Already Have into an Interactive AI Q&A Site with WorkBuddy

### The real barrier to building an AI-powered application has moved. It’s no longer whether you can write code.

![](https://miro.medium.com/v2/0*fAcA7jEC91Iao5T6.jpg)

## What We Were Actually Trying to Build

Last week, [at an AI workshop I ran for a university library in Guangzhou](https://mp.weixin.qq.com/s/2QadAMg_eQ_AMDZbMcXDUw), I walked a few dozen participants through one exercise: take the files you already have — a spreadsheet, say, or a stack of policy documents — and turn them into a website. Not a website that just displays the data, either. One that answers questions. Ask it anything and it works the answer out from the real data on the spot.

The day before we did this, one of the librarians in the room was learning how to pair an AI with a knowledge base. They uploaded their library’s patron guide into WorkBuddy’s file library — WorkBuddy is Tencent’s AI workspace — and started asking it questions.

They asked what to do about an overdue book. The AI laid it out clearly, and on top of the two standard options it threw in a better one: if you’re not in a hurry to borrow anything else, just wait for the next fine-waiver day and return it then. Less hassle.

They also asked how someone off campus goes about searching for papers, and the AI listed the VPN route along with contact details for several campuses.

They even role-played a patron complaining that the library was too hot. The AI first checked whether the patron was doing okay in the heat and suggested ways to cool down, right down to a small fan, and only then told them who to contact and which other spaces they could move to. Their own verdict: these answers were probably better phrased than what a staff member would come up with on the spot.

It really did work well. The catch is that for a patron to actually use this Q&A, they’d have to connect to your knowledge base first, and know their way around the same AI tool. For most patrons, that’s far too much friction.

So it occurred to us: make it a website, and then all a patron needs is the link. And we’d tried exactly that the day before: having WorkBuddy spin up a website from a set of files.

Could we merge the two, then? Build one site that both visualizes the data and lets people ask questions about the very same data the page has loaded?

Of course we could.

This post walks through exactly how.

## Getting WorkBuddy to Build the Site

Step one: have WorkBuddy generate the whole site.

> *In my document library, generate a sample HTML page and a linked CSV data file — sales records, with charts and tables. Requirement: when I edit the CSV data, the HTML charts change to match.*

![](https://miro.medium.com/v2/0*kWLU5TJgGUm5Pi0j.png)

*Caption: WorkBuddy’s chat after the generation prompt. It reports (7m52s later) that it created two linked items in the document library: a sales-records dashboard as an HTML page, and a sales data table with 50 sample rows.*

So WorkBuddy made up a set of sales records for me.

![](https://miro.medium.com/v2/0*d80YLh7KyP7ymibx.png)

*Caption: The generated `sales_records.csv` opened as a WorkBuddy database table. The columns are order date and product name; the sample rows list smart bands, wireless earbuds, smart speakers, and tablets sold in early July 2026.*

Here’s the page it produced.

![](https://miro.medium.com/v2/0*5gnurqceWEyFvleo.png)

*Caption: The header of the generated dashboard. The subtitle says the data is read live from the sales data table (edit a record, refresh, and the charts update); the KPI cards show total sales of 331,271 yuan, 49 orders, 420 units, and an average order of 6,761 yuan.*

![](https://miro.medium.com/v2/0*K3XSUVTpQ-hGYj1p.png)

*Caption: The dashboard’s chart area: a daily sales trend line, sales by product (wireless earbuds highest), a sales-by-region donut, and the top of the order-detail table.*

Nicely illustrated, as you can see — a whole set of built-in charts that make the data easy to scan.

Then one sentence is all it takes to have WorkBuddy publish the page.

![](https://miro.medium.com/v2/0*D88iji9GOOlvnn42.png)

*Caption: One sentence (“publish the HTML as a website, and tell me whether the CSV linkage still holds”) and WorkBuddy returns a public URL, confirming the published site still reads the data table live: edit the table, refresh the page, and the KPIs, charts, and details update.*

But we wanted to go further: users should be able to ask questions about the data and get answers.

> *Can you make it interactive? Users type a question into the interface, and the site answers based on the actual data?*

WorkBuddy did as asked, and you can see it laid out several preset questions — click one and you get an answer.

![](https://miro.medium.com/v2/0*3eos-XTo1GbNp-S1.png)

*Caption: The published dashboard with the new Q&A panel (“Smart Q&A: query the sales data in natural language”). A row of preset question chips sits above the input box; here “What are total sales?” gets an answer of 296,746 yuan with supporting figures.*

Then it added a caveat:

![](https://miro.medium.com/v2/0*XLOqT6QpLUi0fgod.png)

*Caption: WorkBuddy’s technical note: this Q&A is a pure front-end rule engine with no language model behind it, because embedding an API key in a public page would leak it to every visitor. For true free-form AI Q&A, it says, you need a backend service acting as a relay.*

Ask how the online channel is performing, for instance, and the answer is solid. **But these are hardcoded.** Tweak it a little — make the question more specific, add a time range like the first ten days of July — and it draws a complete blank.

![](https://miro.medium.com/v2/0*vQEcUJw2nau4w73j.png)

*Caption: The preset question “How is the online channel performing?” answered from the data: about 145,000 yuan across 20 orders, roughly 55% of total sales, with wireless earbuds and the North China region leading.*

WorkBuddy had already spelled out the fix a moment earlier.

![](https://miro.medium.com/v2/0*Khi-dNrqaWlAadmM.png)

*Caption: The same note as above, with the key sentence boxed in red: to get real free-form AI Q&A, add a backend service as a relay.*

So step two is the one that matters: wire the site up to a large language model so it answers from the data the page actually loads. And the answers need testing — you can’t rely on the model’s mental arithmetic alone for complex math.

## Wiring In Real Q&A

Adding genuine AI Q&A turns out not to be complicated.

All I said was this:

> *I need free-form AI Q&A*

And WorkBuddy got to work. A few minutes later it reported that it was basically done.

![](https://miro.medium.com/v2/0*4eKvTyOnFjhotUuy.png)

*Caption: WorkBuddy’s reply to “I need free-form AI Q&A.” It lays out the architecture (the visitor asks; the page POSTs the question plus the latest data to a relay cloud function; the function calls the model with your DeepSeek key, which stays in the cloud; the answer returns to the page), reports that the relay code is written in `ai_qa_backend/index.py`, and says the page now runs a dual engine that falls back to the rule engine if the AI service is down.*

To have a web page call a large language model, you need a key first.

Unless the AI is running locally on your own machine, calling it takes that key. The logic isn’t complicated. Take the workshop: everyone in the room was using WorkBuddy, and every WorkBuddy account carries its own credits. Use it there and you’re burning your own credits. Other AI services are no different — calls cost money, and the provider has to know whose tab to put it on.

So you need something that vouches for your identity — proof that the caller really is you. That’s the API key.

The name sounds more technical than it is: an API key is just a string of characters that confirms who’s making the call. You apply for one, store it somewhere safe, and present it when you call.

Here’s my DeepSeek API console, with a few of my own API keys in it. Redacted, obviously.

![](https://miro.medium.com/v2/0*HY68pbje-GF8uMx5.png)

*Caption: My DeepSeek API console on the API keys page, with the “Create API key” dialog open. The key itself is covered by a black bar reading “API KEY REDACTED,” and the console reminds you that the key is shown only once and must never be exposed in browser or client-side code.*

Until you have that key, that interactive dashboard is really only half-built.

And once DeepSeek is hooked up?

Same question about online channel performance — but now with a DeepSeek API key in place, and with “the first ten days of July” added. It worked out the online sales for that window on the spot, from the sample data the page had loaded.

![](https://miro.medium.com/v2/0*e9G0uJCjgF1q8QpF.png)

*Caption: With DeepSeek wired in, the refined question “How did the online channel perform in the first ten days of July?” gets a real answer: 14 online orders totaling about 98,000 yuan, with the arithmetic shown line by line, and the trend chart below re-scoped to that window.*

And notice that even the chart below shifts to match the time range in your question.

Which means the site you’ve deployed now does two things at once: it draws on the data you’ve linked to it, and it has AI Q&A on top, so anyone who visits can ask questions against your real data.

## Three Lines of Defense for Your API Key

But mishandle that key and you’re in trouble.

Security here breaks down into three lines of defense.

**First line of defense: never expose the API key in plain text.** You’re about to deploy an AI onto a website. Write the API key straight into the page’s code and you’re not far from going broke. Once it’s sitting there in the source, anyone who grabs it can use it however they like — and nothing confines them to asking questions on your site. All of it on your dime.

And the page isn’t the only exposure. If you paste the key in plain text into a chat with an AI, it enters that provider’s data pipeline. A major provider is unlikely to do anything with your key, but every extra place it passes through is one more chance it leaks to a third party, and then who knows.

That first line is about storage: keep the API key in a credentials file on your own machine. When you talk to an AI later, tell it where the file is instead of pasting the key into the chat box. This only works with a local AI assistant that can read files on your computer. A browser-only tool just sees a filename and can’t get at the key inside.

The second is about deployment: tell the AI, in one sentence, “Please connect to the DeepSeek API through a relay function.”

![](https://miro.medium.com/v2/0*6wL_jT1QLfJY80rW.png)

*Caption: A crop of WorkBuddy’s earlier reply with “the relay function code is written” boxed in red, plus the line confirming that data linkage is preserved: the AI receives the latest records the page pulls from the table.*

To be clear up front: relay function isn’t an official Tencent Cloud product name. It’s a plain-language cue the AI understands. Whether it ends up as a Tencent Cloud SCF function, a function URL, or something else entirely is not your problem.

All you need to know is what it does. Say that sentence and the AI builds you a middle layer in the cloud: the page takes a question and hands it to that layer; the layer pulls the key out of a server-side environment variable and queries the model; the answer comes back and gets passed along to the page. Round trip done, and the key never appears in the page’s code. An ordinary visitor can’t reach it. Only someone who can log into your cloud function console can see it — so guard that console account too.

![](https://miro.medium.com/v2/0*S0A97K1uBzpetipi.png)

Honestly, though, configuring that relay function is the most time-consuming part of all of this. At the workshop, some participants took a full hour before they finally got it working.

One thing in class had me laughing and wincing at the same time.

One group announced they were done. Tested it, too. Working.

That puzzled me. This process requires setting up a relay function — how did they finish so fast?

Turns out that when WorkBuddy asked them for an API key, they pasted the key straight in as plain text. The AI had the key, so of course everything worked.

Did it work? Absolutely. If you set security aside entirely and drop the key right into the code, you can have this done in minutes. But it worked precisely because the security step got skipped altogether.

There is, of course, a much easier way to get this same configuration done. More on that in the next section.

**The third line of defense covers who gets to use your site, and how much. The relay function only keeps your key from being exposed; it does nothing about anyone freeloading on your quota.**

When we deployed in class, the AI announced two things it was about to do. First, put the key into a server-side environment variable so it never lands in the front end or the code repo. Second, no authentication. I confirmed, and it finished the deployment for me. But what does no-auth actually mean? Anyone who gets the URL of your page can burn your API on their own questions. Your key isn’t exposed, true — but your quota is wide open.

So if you’re building a real service for the public, no-auth is out of the question. You need access control or a quota ceiling.

## Letting Codex Do the Clicking

Configuring the relay function has to be done inside Tencent Cloud. WorkBuddy handed me a step-by-step manual plus a ready-made script and pointed me at Tencent Cloud’s site.

![](https://miro.medium.com/v2/0*6D6lcJ310cOjIePQ.png)

*Caption: WorkBuddy’s hand-off checklist, “What you need to do (about 10 minutes, all point-and-click)”: get a DeepSeek key; create the cloud function and attach an API gateway by following the attached `DEPLOY.md` (paste `index.py`, put the key in an environment variable, raise the timeout to 60 seconds, choose no authentication); then send back the gateway URL.*

But I’m lazy. Clicking through something like that myself is exactly the kind of work I can’t be bothered with.

So that morning, while I was prepping the class, here’s what I did: I opened Codex — the AI assistant that can drive my computer for me — lifted WorkBuddy’s manual and script out verbatim, and told it: here, do this for me.

And it started working through it, one step at a time. [Codex can control my Chrome](https://wshuyi.medium.com/can-you-get-ai-to-run-netlogo-just-by-talking-to-it-3cd451e5573d), so it opened Tencent Cloud’s pages itself and did its own clicking. At the login step it needed a WeChat QR scan. That one it couldn’t do, so I scanned the code and told it “logged in.” From there it configured everything that needed configuring — I’d told it beforehand that I was using DeepSeek, and where the API key lived on my computer. It put the key into a server-side environment variable, chose no-auth, finished the deploy, handed me a URL, and ran its own test, which passed. Then I pasted that URL back into WorkBuddy (a step that was supposed to be manual), and it put the whole thing I’d asked for online.

![](https://miro.medium.com/v2/0*DE8heASz3mgHMH5l.png)

*Caption: After the deployed function URL (partly redacted) is pasted back in, WorkBuddy reports “Free-form AI Q&A is live,” shows its own smoke test (“What are total sales?” answered as 7,580 yuan on two test records), and lists sample open-ended questions the DeepSeek-powered page can now answer.*

There was exactly one point of genuine human intervention in the whole run: scanning the WeChat QR code to log in. Everything else was Codex driving Chrome.

## How Codex Adapts on the Fly

I wasn’t recording video the first time Codex drove Chrome through all this. Afterward I had Codex run through it again and grab screenshots of the key pages as it went. Those became the animation below.

![](https://miro.medium.com/v2/0*KO0wpSLsPrZ9d4T5.gif)

*Caption: Codex driving Chrome through the Tencent Cloud SCF (Serverless Cloud Function) console: the function list with its orange API Gateway retirement banner, the “create function” wizard, code and log settings, the Function URL panel, and the final CORS configuration. The real function URL is masked.*

So what’s it actually like to watch it run itself?

Two details really stuck with me.

First: every time Codex takes a step, it looks at the result on screen, parks a thumbnail off to one side, watches what changed, and adjusts. It’s like two martial artists squaring off — fight blind and you’re tracking your opponent by sound alone — you’ll pay for it; see the moves coming and you react far faster. Codex sees the result of every step, so it can respond as it goes.

![](https://miro.medium.com/v2/0*AWaKkQcOZtY8MdQX.png)

*Caption: The Codex desktop app mid-run, with the small picture-in-picture Chrome thumbnail it watches while it works. Codex has asked me to log in and reply “logged in,” notes that the DeepSeek key has not been read or transmitted yet, and then reports that the legacy API gateway was retired in 2025, so it will switch to Tencent Cloud’s Function URL route instead.*

The second is even better. Codex spotted a banner notice on the page: Tencent Cloud’s legacy API Gateway had been retired on June 30, 2025, with the console and the APIs shut down together. In fact, the product had stopped being sold back in July 2024. Which meant the tutorial WorkBuddy gave me was written against the old API Gateway and was out of date.

![](https://miro.medium.com/v2/0*BsC2sCu--aJc6usc.png)

*Caption: The Tencent Cloud SCF function list with the orange banner Codex spotted: the API Gateway product stopped service on June 30, 2025; from July 1, 2024, no new API gateway triggers could be created; basic users should switch to Function URL and advanced users to the TSE cloud-native gateway.*

Codex worked this out on its own and switched to the new flow. I turned the updated walkthrough it wrote up into a Feishu doc and sent it to the whole class for reference.

![](https://miro.medium.com/v2/0*vwUSwd1H9Hk43CDw.png)

*Caption: The Feishu document built from Codex’s corrected walkthrough, “DeepSeek Q&A Relay Function Deployment Guide (Tencent Cloud SCF Function URL edition),” updated 2026–08–20. Its first section explains why the old guide no longer works: the API gateway trigger route is retired, so use the cloud function’s built-in Function URL, which also provides a public HTTPS address with POST, CORS, and no-auth access.*

This is exactly why an AI that will do the tedious work for you matters so much. The configuration steps themselves aren’t hard, but they’re easy to get wrong: a default may be off, a tutorial may be stale, a timeout may be set too low. Do it yourself and you’re tiptoeing through every stage. Hand it to an AI that can see the screen and correct course in real time, and it’s a completely different game.

## What It Actually Cost

The first thing most people ask is: [calling an AI API has to burn money, right](https://mp.weixin.qq.com/s/Zq3QxYym46idwtvTuuYRRw)?

I pulled up DeepSeek’s usage page in class so everyone could see. From the moment I started testing that morning through the end of the morning session, with a few dozen people all firing questions at that site — how much did it cost me?

Twenty-two fen. That’s 0.22 yuan — about three US cents.

![](https://miro.medium.com/v2/0*8m_yiOEY2eSSiMQA.png)

*Caption: The DeepSeek usage page for the workshop day (08/20): total spend ¥0.22, 91 API requests, 421,191 tokens.*

During the afternoon debrief, one participant read out the spend on their own practice account: just two fen, a fraction of a US cent.

The model we used in class was `deepseek-v4-flash`. As of August 29, 2026, its output pricing comes in two tiers, off-peak and peak: 4.5 yuan and 9 yuan per million tokens respectively. Classroom demos don't generate much call volume, so a 10-yuan balance lasts a while. A real service still needs a budget and a ceiling set against actual traffic.

DeepSeek runs on prepaid credit: you top up, it draws down, and the API returns a 402 error once your balance runs out. If you’re using another model’s API and its console offers something like a credit line, don’t switch it on until you’ve thought it through — otherwise the charges keep piling up after your prepaid balance is gone.

There’s one more practical convenience for institutional use: DeepSeek issues electronic invoices on request. A company that has completed identity verification can pay by corporate transfer, and individuals can top up with Alipay or WeChat.

## Gotchas Worth Knowing About

On top of the ones we hit while generating the site, participants ran into a few more snags during deployment and use — worth knowing about in advance.

The first you’ve already seen: the tutorial an AI gives you may be out of date. When the page or the product name doesn’t match what the tutorial describes, check the current official documentation first, then decide whether to stick with the original plan or switch approaches.

The second is sneakier. If the AI’s answers come back incomplete after deployment, cutting off mid-sentence again and again, go check the request timeout on your Tencent Cloud SCF function — it defaults to 3 seconds, and you can raise it.

The third is the most interesting, and it’s the diagnostic instinct I most want to pass along. A participant noticed that the site’s answers to date-related questions were always a little bit off. On close comparison, they weren’t wrong outright — every single date was shifted by exactly one day.

Shift the dates back a day and everything lined up. Every single one, shifted by exactly the same one day.

A perfectly uniform offset like that is a very useful troubleshooting signal. Check the raw timestamps, the business time zone, the date parsing, and the context being passed to the model first. Only when all of that comes back clean should you start wondering whether the model’s reasoning went wrong.

A pattern like that doesn’t prove on its own that the bug is in the code, but it does tell you where to look first.

![](https://miro.medium.com/v2/0*kX5MokClPMofGsaE.png)

One more thing worth keeping in mind: this site is wired only to a chat endpoint. The model has no calculator or similar tool attached, so don’t expect it to handle complicated math. A cheap Flash-tier call like this isn’t good at everything.

## Where to Draw the Line on Data

A warning: **unauthorized data and anything touching personal privacy do not belong on the public internet.**

In class we used sample sales data with nothing sensitive in it. The library patron guide that participants tried is public information too. But if what you have is real patron borrowing records, student grades, or personnel files, putting that on a public website for anyone to query is not okay.

The demo site from class used only public sample data, and it comes down once the workshop is over. If real business data is going online for the long haul, you have to confirm the scope of authorization first, de-identify the data, and spell out exactly what each type of user is allowed to see.

![](https://miro.medium.com/v2/0*2l8e6wDrpaOTpCn4.png)

*Caption: The hardened demo site: unit-sales charts by region and by category over synthetic data, and an AI Q&A box now gated by a demo access token (red box). The note explains that the token travels only in the request header and is never stored in the browser, and that at most 300 filtered rows are sent to the relay function per question. The footer marks the data as synthetic, for teaching only.*

## Wrapping Up

Looking back: we had WorkBuddy generate a page from our documents, handed the data that page actually loaded to a large model, protected the API key behind a server-side relay, and then added access control and testing with real questions. AI can take a lot of the coding and configuration off your hands, but before anything goes live, the data permissions, the answer checking, and the spending ceiling still need a person to sign off.

The biggest thing I took away from the whole exercise:

> ***The real barrier to building an AI-powered application has moved. It’s no longer whether you can write code — it’s whether you understand your lines of defense, whether you can tell a program bug from a model hallucination, and whether you can hold the line on your data boundaries.***

Keep your API key safe, keep your usage quota under control, keep sensitive data locked down, and the documents and datasets sitting dormant on your drive can become interactive tools that solve real problems for your readers and users — at almost no cost.

Do you have policy manuals or business data of your own that you’d like to turn into an interactive AI Q&A page? Have you run into problems calling an API or getting one deployed? Drop your thoughts and experiences in the comments and let’s talk it through.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- [How Windsurf Cascade Puts AI to Work on Real Problems](https://mp.weixin.qq.com/s/BnEhg3vUe3FizaML0XQJxg)
- [AI Apps Are Exploding — Is Your Moat Wide Enough?](https://mp.weixin.qq.com/s/-H-Q70wBTDaN7APYnRhI6g)
- [From Dry Theory to Live Practice: How AI Agents Explain Complex Concepts with Interactive Tutorials](https://wshuyi.medium.com/from-dry-theory-to-vivid-practice-how-ai-agents-explain-complex-concepts-with-interactive-9f68d82b9ec8)
- [New Semester, New AI Assistant: One That Thinks, Searches the Web, and Comes with a Knowledge Base](https://wshuyi.medium.com/new-semester-equip-yourself-with-a-powerful-ai-assistant-capable-of-thinking-connecting-to-the-446e9291e8d7)
- [Getting Started with Claude Skills: How AI Graduates from Mouthpiece to Actual Worker](https://mp.weixin.qq.com/s/GS3aFsSKajo_Uk3LAkC_Yw)
