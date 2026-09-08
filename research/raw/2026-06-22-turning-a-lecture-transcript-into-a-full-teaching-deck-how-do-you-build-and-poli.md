---
title: "Turning a Lecture Transcript Into a Full Teaching Deck: How Do You Build and Polish a Skill Like…"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/turning-a-lecture-transcript-into-a-full-teaching-deck-how-do-you-build-and-polish-a-skill-like-0053555b454d"
published: "2026-06-22"
fetched: "2026-09-08"
reading_time_min: 30.0
tags: []
member_only: true
body_source: "medium-session"
---

# Turning a Lecture Transcript Into a Full Teaching Deck: How Do You Build and Polish a Skill Like…

## **Turning a Lecture Transcript Into a Full Teaching Deck: How Do You Build and Polish a Skill Like This?**

### *The hard part isn’t drawing the pictures — it’s teaching it not to draw them wrong.*

![](https://miro.medium.com/v2/0*EPQ1jaWj42Qd0C5p.png)

## Noticing

On June 16, 2026, at the invitation of Professor Song Enmei of *Documentation, Information & Knowledge*, I gave an online talk for Wuhan University’s School of Information Management, as part of its “Luojia Information Management · Frontier Forum.”

![](https://miro.medium.com/v2/0*xpF5oN7uEiVWYNCG.png)

*Caption: A screenshot of the online forum session — the gallery-view grid of attendees, with my own video feed among them.*

After the talk, a good friend sent over a heartfelt outpouring of reflection and praise. It ended with this line.

![](https://miro.medium.com/v2/0*kmMGdUtXlQwzNfrn.png)

*Caption: A chat screenshot. The friend writes, “Today’s slide style is different from before, too — looks like image 2 really is good.” I reply, “Exactly — you’ve got a sharp eye!”*

He’d very sharply spotted the change in my slide style. Ha.

That’s right — the slides that night basically looked like this.

![](https://miro.medium.com/v2/0*VYmA5QhwjeSgiEnf.png)

*Caption: One of the slides from that night — a clean, white-background infographic titled “Shifting Roles: From ‘Human-in-the-Loop’ to ‘Human-on-the-Loop.’” On the left, robots run each step (gather → filter → analyze → report) while a person checks each one; on the right, the person steps up to set the goal, monitor direction, and verify the final result, with the execution delegated to the agent.*

Here’s another.

![](https://miro.medium.com/v2/0*yNyNfe-j6jtlRXnV.png)

*Caption: Another example slide in the same clean, Keynote-style look.*

If you’ve been following my videos for a while, you’ll know my slides didn’t used to look anything like this.

Usually it was black text on a white background, a few words or a list of short phrases. Very plain.

![](https://miro.medium.com/v2/0*BI64Y-l1i9PijPJV.png)

*Caption: One of my old, plain slides — the title “Types of Hard Security” over a three-item bullet list: disaster backup, data-leak prevention, and encryption & permissions.*

Why? Was I like Steve Jobs, with an almost obsessive devotion to simplicity?

Of course not. It’s because **I’m a lazy person**.

If a text list would do, I wouldn’t bother with a picture.

If a picture was unavoidable, I’d plop down a single one on its own, and the next page would, more likely than not, be back to a text list.

Right?

![](https://miro.medium.com/v2/0*_nkTZ3u3lZlfq3iJ.gif)

So why are my slides so lively and vivid now?

Because of **rising productivity and the falling cost per unit of output**, naturally.

Let me walk you through it.

## How It Started

A while back I read an article on the “Dedao” app, written by Xuan Mingdong, Dedao’s head of content quality control. The gist was that when you’re making content or teaching a class, you absolutely have to start with a verbatim transcript.

![](https://miro.medium.com/v2/0*QmuDMUR_5mgJF9-k.jpeg)

*Caption: The Dedao article in question, titled “Why Do the Pros at Making Courses All Recommend Writing a Verbatim Transcript?” — shown here as its 15-minute audio version.*

To be honest, I used to really dislike writing transcripts — felt like a hassle. Even for the courses I ran in Dedao’s AI Study Circle, I’d just get the slides ready and start talking, and then an editor would convert the audio and video of my talk into a transcript for me.

So the moment I saw that headline, I had zero interest in reading it. But that day, by sheer accident, I happened to be driving and listening to the audio version of the article — switching it off wasn’t convenient, so I just let it play. And the more I listened, the more it made sense. I actually tried it for a stretch, and after a few rounds of prepping classes and getting ready for talks, I discovered that the transcript really does matter. When you write down, word for word, everything you mean to say in a class, *that’s* when your thinking gets clear and your confidence is at its fullest.

But finishing the transcript is only the first step of a very long march. You can’t very well teach a class staring at a screen full of text. You still have to **express it visually** — turn it into page after page of content you can put up on a screen, talk through, and look at.

What I wanted in my heart was actually dead simple: I hand a finished transcript to the AI, and it hands me back a whole set of beautiful, classroom-ready slide images.

![](https://miro.medium.com/v2/0*Lt-hP8_6FyN0Ctpg.png)

*Caption: A diagram of the simplest form I was after — “Give it a transcript, get a whole deck back”: a lecture transcript goes into the AI, which returns two outputs, an illustrated-narration version (image + narration) and a minimalist image set (straight to PPT).*

In terms of form, the final deliverable I wanted came in two pieces. One I call the “illustrated transcript version,” which keeps the chapter structure of the script, with each image followed by its corresponding narration — handy for prepping and for iterating. The other is a “minimalist image set,” with nothing but a title and the images laid out in order, easy to drop straight into Quarto or a PPT.

Because the input is a long piece of text, slicing up the content is itself a hassle — so I let the AI handle that too. I wanted it to do the cutting for me, and to cut it **just right**: cram too much onto one page and the screen is a wall of stuff students can’t keep up with; chop it too fine and there’s no “cognitive gap” worth talking about. Ideally it inches forward bit by bit, with each chunk having something to say, without filling the page wall to wall.

A Skill like this — is it easy to build?

If you mean the first version, then yes, dead easy. Just take all those requirements you just laid out, throw them at Claude Code or [Youmind](https://youmind.com/pricing?ref=WXXAG8&campaign=2026-618) verbatim, in their raw text form, and ask it to “make a Skill.” It’ll spit one out right away. And it’ll look the part.

But once you’ve got that first draft of a Skill and actually feed it a transcript — that’s when the trouble starts.

Over the past two weeks, while prepping classes, teaching, and giving talks, I’ve been locked in a battle of wits with this Skill. Through dogged error-correction and iteration, it now works really well. I’ve already published it on Youmind. If you like this style, you can call it up directly inside Youmind. For the English Version, [click here](https://youmind.com/~skills/019eec91-b94d-7f5d-978e-0731c51214ce). [Here’s the link for the Chinese version](https://youmind.com/skills/lecture-infographic-generator-yYw26Iud0eKlsX).

![](https://miro.medium.com/v2/0*rq6AUPRzijt2xUTj.png)

*Caption: The published Skill on Youmind, ready to be called directly.*

And if you want to do more than just use it — if you want to understand how this Skill was “honed” into shape — then let me walk you through it in detail below. I hope it helps you build and polish Skills of your own for whatever unique task you’ve got.

## Getting the Heat Right

The first thing I had to tame was the style.

I have a clear preference: the finished product has to slot into the RevealJS / Quarto web-presentation framework I always use, which means the background has to be pure white — that way, when I’m editing, I can casually drop in a page, layer on my own text list or an image, and have it not look out of place.

As for the page style: last year I went to the Open Mind conference, where the organizers required us to use Keynote. I’d rarely used it before, but the style left a deep impression, so I had the AI Agent imitate it too.

But the AI didn’t get any of this out of the gate. I told it to make things “livelier,” and it cranked out a pile of hand-drawn, cartoonish flourishes. Look at the left side of the image below — honestly, a touch of that here and there is refreshing, a nice change of pace. But page after page of it feels off. You’re someone lecturing university students; you’re not addressing kindergarten or primary-school kids, nor putting on a demo for an art-and-animation class. A screen full of doodles isn’t quite right.

![](https://miro.medium.com/v2/0*pwS1UmXQ6RGlu4rK.png)

*Caption: A before/after of the style — “Too flashy → proper and easy to slot in.” On the left (✗ Before), a busy hand-drawn, doodle-style take on “The Meaning of Fractions and How to Compare Them,” noted as too cartoonish to pass; on the right (✓ After), the same topic in a clean Keynote style with a pure white background, easy to drop into the deck.*

So I kept grinding away at it: take the proper Keynote route + a pure white background; the “lively” quality shouldn’t be tossed out, but a little goes a long way. Getting it right **took several rounds of swinging back and forth between “too busy” and “too bare” before it settled down**. And it made me realize, for the first time, that getting the taste in my head across to it takes more than a single sentence — you’ve got to keep handing it real examples and your own real feedback, and have it revise, over and over.

## Sweating the Details

Once the style was set, what followed was all about sweating the details.

Earlier on, models were limited enough that just getting it to render the Chinese in an image correctly — no garbled characters, no going rogue — was already a chore. I even wrote a whole piece for you about it: [How Do You Get AI to Render Chinese in Images More Reliably and Accurately?](https://mp.weixin.qq.com/s/HYrZOxB6kFcqh_zLjoGUNA) These days, from Nano Banana Pro to GPT image 2, the handling of Chinese keeps getting more impressive. But generating slides where text and visuals work together still takes plenty of methods and tricks worth keeping in mind.

The first problem is that the AI loves to take liberties. I asked it to draw a three-step flow, said only “draw three nodes,” and never told it what text went in the boxes. It promptly made up a few little Chinese labels and stuck them in. That time the made-up text happened to make sense — but that’s just gambling. It could just as easily have cooked up a string of words that had nothing to do with anything and hung them right there on my teaching diagram as if they belonged. I immediately added a rule: anywhere text might appear, either pin the exact words down for it, or tell it plainly, “no text allowed here.”

![](https://miro.medium.com/v2/0*A-efp8bvJTIkzOZ6.png)

*Caption: The fix for made-up text — “Leave the text unspecified and the model invents its own.” On the left (✗ Before), a three-node flow whose box labels the model filled in on its own, flagged as possibly mismatched nonsense; on the right (✓ After), the same flow where the text is either pinned down exactly or a box is explicitly left text-free.*

The next problem cropped up in conveying the meaning of “who’s doing the work.” I asked it to draw a “human-in-the-loop” diagram — meaning the AI runs each step, and a human comes along to check each one in turn. Instead, it drew me a row of people, heads down, doing the work with their own hands, in direct contradiction with the caption below the figure that read “reviewed step by step by a human”: if the people are doing the work themselves, step by step, then who is left to review?

![](https://miro.medium.com/v2/0*oIYIyaP59-up3px5.png)

*Caption: The wrong version — a row of people each doing the work by hand. The caption under the figure reads “humans review each operation step by step,” but the red line below points out the contradiction: “the humans are doing it themselves, which clashes with the caption.”*

So I spelled it out for it: the ones doing the work are robots; the human is in charge of reviewing. And that’s how we got the image you see here.

![](https://miro.medium.com/v2/0*tsYIEHHtrMiyPetW.png)

*Caption: The corrected “human-in-the-loop” version — robots perform each step (gather → filter → analyze → report) and a person reviews each one, under the caption “humans review each operation step by step.”*

The most exasperating part was that sometimes the meaning conveyed by ordering and arrows came out completely backwards. I wanted to show a score climbing from 94.4% to 100%, but it parked that big “100%” down at the bottom of the frame, with the arrow pointing up at the small old number above it. Read it straight through, and the whole image looks for all the world like “dropped from 100 back down to 94.4” — a step forward drawn, against all sense, as an across-the-board regression.

I added a rule for it: for any before-and-after comparison, position, arrow direction, color, and font size all have to be locked down together — the arrow points unmistakably from old to new. This rule actually got flagged by an independent review at the time and bounced back for another round of revisions before it passed muster. At the end of the day, getting a model to catch its own mistakes is notoriously unreliable — something I’ve written about specifically in [What Do You Do When an AI Agent Can’t Catch Its Own Mistakes?](https://mp.weixin.qq.com/s/naS917RIF1KqTLcfiE-L0A) — so for this kind of gatekeeping, I’d much rather hand it off to a pair of outside eyes.

![](https://miro.medium.com/v2/0*aUUxaOzazDq7RxHg.png)

*Caption: The before/after on the score comparison — “Don’t let an ‘improvement’ read as a ‘setback.’” On the left (✗ Before), the big “100%” sits low with an arrow pointing up at a small “94.4%,” which reads as a regression; on the right (✓ After), “94.4% → 100%” runs left to right, old small and gray, new big and green, with the arrow pointing clearly from old to new.*

Here I have to let you in on a hidden truth. They’re all called “multimodal” (able to read images), but when Opus looks at an image to review and verify it, the accuracy is always just a notch short. So I laid down a requirement: whenever a GPT model can be called to look at the image, always use GPT to review how the generated image turned out.

The three specific problems above all really come down to the same thing — we’re loading the model up with too heavy a task, and the boundaries aren’t clear enough. After talking it over with it, I added a rule: before drawing anything, you have to spell out in the prompt, down to the last detail, exactly what the picture is meant to convey, and only then send it to the GPT image 2 model. That way, there’s less and less guessing and reading between the lines, and the precise positioning and requirements get spelled out in ever more detail.

There was another time when the image needed to pair each of several key points with a one-line explanation, drawing a connecting line from each point over to its line of text. But those lines all got crossed up — tangled into a knot, with the wrong explanation tied to the wrong point, and no way to tell which explanation went with which. I went several rounds with the AI and saw no improvement at all.

Then it suddenly hit me: this kind of “which point is this sentence explaining” attribution simply shouldn’t be drawn with lines stretching across half the layout — GPT image 2’s routing of lines isn’t reliable. Better to tie the explanation and its point together on the same little card, so it’s crystal clear what goes with what.

![](https://miro.medium.com/v2/0*gykRP4LWZeguICPe.png)

*Caption: The fix for tangled connectors — “Don’t make the model route geometry; bind meaning to position and text instead.” On the left (✗ Before), the four seasons are joined to their descriptions by thin crossing lines, so the links get scrambled; on the right (✓ After), each season and its description sit bound together on one card (spring = the season when all things revive, summer = the hot season, autumn = the harvest season, winter = the cold season), clear and easy to check one by one.*

In other words, if you don’t impose constraints, one and the same relationship can be expressed in different forms. And as it happens, some of those forms are things today’s AI just isn’t good at (spatial-geometric relationships and the like) — so rather than try to teach it how to handle them, you might as well steer clear of that path of expression in the first place. As the saying goes, “there are things one simply does not do.”

Grinding through this round after round, you’ve probably caught the flavor of it by now: as a human user, you can’t predict every category of mistake the AI might make. All we can do is, in practice, play to its strengths and around its weaknesses as best we can so it knows how to do a task well, and then, with each pothole we hit, patch up the holes that might surface.

People say AI lacks vertical data in many domains. The truth is, our process of using these frameworks and giving feedback over and over *is* exactly that most precious data. Claude Code and Codex are made to be likable, which makes them all the more likely to rapidly accumulate this kind of genuine human-feedback behavioral data. Whereas if you’re a foundation-model vendor who only makes the model and not the framework, you have no way to get this data directly — you can only try to “borrow” it from the others via distillation. So you’ll see foundation-model vendors rolling out their own xxxCode products more and more, and faster and faster — Kimi Code, ZCode, and so on. Don’t think they’re making the Harness framework nice to use as a favor to us users. It’s much more that the model vendors *need* to collect more of real users’ domain-by-domain behavioral data.

## What Settles

Hard work pays off. After two weeks of polishing, when I now hand Youmind or Claude Code a fresh transcript, what comes out is basically just the way I want it.

All the flaws that used to drive me up the wall — the made-up labels, the backwards arrows, the tangled connecting lines, the goofy doodles — it now steers clear of them all. Not because it suddenly got smart, but because I turned every single pothole into a rule it has to clear before it lifts a finger.

What I deliver are batches of images. But what truly settles — what can be reused over and over — are the principles and patterns behind those images.

If you, too, are training up some AI tool, don’t expect a single sentence to make it click. Take all those “what I wanted was clearly *this* — how did it give me *that*?” moments and write them down one by one, turning each into a rule you feed back in. Of course, you don’t have to write these by hand — you just tell your AI Agent:

> *Look back over our entire conversation in this session. Pay special attention to the moments where I interrupted what you were doing to make a request — those are usually the important ones. Wherever you hit a pothole during execution, or picked up some lesson on your own, or wherever I caught a wrong direction and corrected it in time or flagged it on later review — go check whether all of it has been written down in the right place. For instance, updating the corresponding skill, or even the global config.*

Once you’ve accumulated enough of these patterns, what you hold isn’t just a usable tool — you’ve also built up a feel for how to refine a vague idea into a definite result. In a world where AI tools are increasingly the order of the day, that ability is precious and scarce.

## Sharing

This Skill that turns a transcript into a series of Keynote-style teaching images — I’ve already packaged it up and put it on Feishu, and you can grab it and install it yourself: [the lecture-image-pack sharing doc](https://www.feishu.cn/docx/CCxodX604oW0I4xehojcdL22nW1), which includes the zip and a QR code.

![The hard part isn’t drawing the pictures — it’s teaching it not to draw them wrong.](https://miro.medium.com/v2/0*xOfiZ3MG8pextBoS.png)

![](https://miro.medium.com/v2/0*U3ElyVjPT2Sa_NIf.png)

## Noticing

On June 16, 2026, at the invitation of Professor Song Enmei of *Documentation, Information & Knowledge*, I gave an online talk for Wuhan University’s School of Information Management, as part of its “Luojia Information Management · Frontier Forum.”

![](https://miro.medium.com/v2/0*1AWIGoZR0leKX5Y1.png)

*Caption: A screenshot of the online forum session — the gallery-view grid of attendees, with my own video feed among them.*

After the talk, a good friend sent over a heartfelt outpouring of reflection and praise. It ended with this line.

![](https://miro.medium.com/v2/0*FQxR0T4UGz_820vf.png)

*Caption: A chat screenshot. The friend writes, “Today’s slide style is different from before, too — looks like image 2 really is good.” I reply, “Exactly — you’ve got a sharp eye!”*

He’d very sharply spotted the change in my slide style. Ha.

That’s right — the slides that night basically looked like this.

![](https://miro.medium.com/v2/0*fuJmnNjNUxUWW0S8.png)

*Caption: One of the slides from that night — a clean, white-background infographic titled “Shifting Roles: From ‘Human-in-the-Loop’ to ‘Human-on-the-Loop.’” On the left, robots run each step (gather → filter → analyze → report) while a person checks each one; on the right, the person steps up to set the goal, monitor direction, and verify the final result, with the execution delegated to the agent.*

Here’s another.

![](https://miro.medium.com/v2/0*SRPgKcoxv1MZfJcV.png)

*Caption: Another example slide in the same clean, Keynote-style look.*

If you’ve been following my videos for a while, you’ll know my slides didn’t used to look anything like this.

Usually it was black text on a white background, a few words or a list of short phrases. Very plain.

![](https://miro.medium.com/v2/0*guBJHwc0Dmu-vlby.png)

*Caption: One of my old, plain slides — the title “Types of Hard Security” over a three-item bullet list: disaster backup, data-leak prevention, and encryption & permissions.*

Why? Was I like Steve Jobs, with an almost obsessive devotion to simplicity?

Of course not. It’s because **I’m a lazy person**.

If a text list would do, I wouldn’t bother with a picture.

If a picture was unavoidable, I’d plop down a single one on its own, and the next page would, more likely than not, be back to a text list.

Right?

![](https://miro.medium.com/v2/0*K_tnKnfwUFaONvRm.gif)

So why are my slides so lively and vivid now?

Because of **rising productivity and the falling cost per unit of output**, naturally.

Let me walk you through it.

## How It Started

A while back I read an article on the “Dedao” app, written by Xuan Mingdong, Dedao’s head of content quality control. The gist was that when you’re making content or teaching a class, you absolutely have to start with a verbatim transcript.

![](https://miro.medium.com/v2/0*NeylSLq--YmJc-Wd.jpeg)

*Caption: The Dedao article in question, titled “Why Do the Pros at Making Courses All Recommend Writing a Verbatim Transcript?” — shown here as its 15-minute audio version.*

To be honest, I used to really dislike writing transcripts — felt like a hassle. Even for the courses I ran in Dedao’s AI Study Circle, I’d just get the slides ready and start talking, and then an editor would convert the audio and video of my talk into a transcript for me.

So the moment I saw that headline, I had zero interest in reading it. But that day, by sheer accident, I happened to be driving and listening to the audio version of the article — switching it off wasn’t convenient, so I just let it play. And the more I listened, the more it made sense. I actually tried it for a stretch, and after a few rounds of prepping classes and getting ready for talks, I discovered that the transcript really does matter. When you write down, word for word, everything you mean to say in a class, *that’s* when your thinking gets clear and your confidence is at its fullest.

But finishing the transcript is only the first step of a very long march. You can’t very well teach a class staring at a screen full of text. You still have to **express it visually** — turn it into page after page of content you can put up on a screen, talk through, and look at.

What I wanted in my heart was actually dead simple: I hand a finished transcript to the AI, and it hands me back a whole set of beautiful, classroom-ready slide images.

![](https://miro.medium.com/v2/0*r-sX8mlWsCxUn4ox.png)

*Caption: A diagram of the simplest form I was after — “Give it a transcript, get a whole deck back”: a lecture transcript goes into the AI, which returns two outputs, an illustrated-narration version (image + narration) and a minimalist image set (straight to PPT).*

In terms of form, the final deliverable I wanted came in two pieces. One I call the “illustrated transcript version,” which keeps the chapter structure of the script, with each image followed by its corresponding narration — handy for prepping and for iterating. The other is a “minimalist image set,” with nothing but a title and the images laid out in order, easy to drop straight into Quarto or a PPT.

Because the input is a long piece of text, slicing up the content is itself a hassle — so I let the AI handle that too. I wanted it to do the cutting for me, and to cut it **just right**: cram too much onto one page and the screen is a wall of stuff students can’t keep up with; chop it too fine and there’s no “cognitive gap” worth talking about. Ideally it inches forward bit by bit, with each chunk having something to say, without filling the page wall to wall.

A Skill like this — is it easy to build?

If you mean the first version, then yes, dead easy. Just take all those requirements you just laid out, throw them at Claude Code or [Youmind](https://youmind.com/pricing?ref=WXXAG8&campaign=2026-618) verbatim, in their raw text form, and ask it to “make a Skill.” It’ll spit one out right away. And it’ll look the part.

But once you’ve got that first draft of a Skill and actually feed it a transcript — that’s when the trouble starts.

Over the past two weeks, while prepping classes, teaching, and giving talks, I’ve been locked in a battle of wits with this Skill. Through dogged error-correction and iteration, it now works really well. I’ve already published it on Youmind. If you like this style, you can call it up directly inside Youmind. For the English Version, [click here](https://youmind.com/~skills/019eec91-b94d-7f5d-978e-0731c51214ce). [Here’s the link for the Chinese version](https://youmind.com/skills/lecture-infographic-generator-yYw26Iud0eKlsX).

![](https://miro.medium.com/v2/0*45KcyXoPA_AL_wrq.png)

*Caption: The published Skill on Youmind, ready to be called directly.*

And if you want to do more than just use it — if you want to understand how this Skill was “honed” into shape — then let me walk you through it in detail below. I hope it helps you build and polish Skills of your own for whatever unique task you’ve got.

## Getting the Heat Right

The first thing I had to tame was the style.

I have a clear preference: the finished product has to slot into the RevealJS / Quarto web-presentation framework I always use, which means the background has to be pure white — that way, when I’m editing, I can casually drop in a page, layer on my own text list or an image, and have it not look out of place.

As for the page style: last year I went to the Open Mind conference, where the organizers required us to use Keynote. I’d rarely used it before, but the style left a deep impression, so I had the AI Agent imitate it too.

But the AI didn’t get any of this out of the gate. I told it to make things “livelier,” and it cranked out a pile of hand-drawn, cartoonish flourishes. Look at the left side of the image below — honestly, a touch of that here and there is refreshing, a nice change of pace. But page after page of it feels off. You’re someone lecturing university students; you’re not addressing kindergarten or primary-school kids, nor putting on a demo for an art-and-animation class. A screen full of doodles isn’t quite right.

![](https://miro.medium.com/v2/0*DE5-m7M0GGvU6sMf.png)

*Caption: A before/after of the style — “Too flashy → proper and easy to slot in.” On the left (✗ Before), a busy hand-drawn, doodle-style take on “The Meaning of Fractions and How to Compare Them,” noted as too cartoonish to pass; on the right (✓ After), the same topic in a clean Keynote style with a pure white background, easy to drop into the deck.*

So I kept grinding away at it: take the proper Keynote route + a pure white background; the “lively” quality shouldn’t be tossed out, but a little goes a long way. Getting it right **took several rounds of swinging back and forth between “too busy” and “too bare” before it settled down**. And it made me realize, for the first time, that getting the taste in my head across to it takes more than a single sentence — you’ve got to keep handing it real examples and your own real feedback, and have it revise, over and over.

## Sweating the Details

Once the style was set, what followed was all about sweating the details.

Earlier on, models were limited enough that just getting it to render the Chinese in an image correctly — no garbled characters, no going rogue — was already a chore. I even wrote a whole piece for you about it: [How Do You Get AI to Render Chinese in Images More Reliably and Accurately?](https://mp.weixin.qq.com/s/HYrZOxB6kFcqh_zLjoGUNA) These days, from Nano Banana Pro to GPT image 2, the handling of Chinese keeps getting more impressive. But generating slides where text and visuals work together still takes plenty of methods and tricks worth keeping in mind.

The first problem is that the AI loves to take liberties. I asked it to draw a three-step flow, said only “draw three nodes,” and never told it what text went in the boxes. It promptly made up a few little Chinese labels and stuck them in. That time the made-up text happened to make sense — but that’s just gambling. It could just as easily have cooked up a string of words that had nothing to do with anything and hung them right there on my teaching diagram as if they belonged. I immediately added a rule: anywhere text might appear, either pin the exact words down for it, or tell it plainly, “no text allowed here.”

![](https://miro.medium.com/v2/0*S6_8MxsLoA01JNSf.png)

*Caption: The fix for made-up text — “Leave the text unspecified and the model invents its own.” On the left (✗ Before), a three-node flow whose box labels the model filled in on its own, flagged as possibly mismatched nonsense; on the right (✓ After), the same flow where the text is either pinned down exactly or a box is explicitly left text-free.*

The next problem cropped up in conveying the meaning of “who’s doing the work.” I asked it to draw a “human-in-the-loop” diagram — meaning the AI runs each step, and a human comes along to check each one in turn. Instead, it drew me a row of people, heads down, doing the work with their own hands, in direct contradiction with the caption below the figure that read “reviewed step by step by a human”: if the people are doing the work themselves, step by step, then who is left to review?

![](https://miro.medium.com/v2/0*JbWI7Z1Siao7xHqP.png)

*Caption: The wrong version — a row of people each doing the work by hand. The caption under the figure reads “humans review each operation step by step,” but the red line below points out the contradiction: “the humans are doing it themselves, which clashes with the caption.”*

So I spelled it out for it: the ones doing the work are robots; the human is in charge of reviewing. And that’s how we got the image you see here.

![](https://miro.medium.com/v2/0*EJGSh1MtYJLM8Tos.png)

*Caption: The corrected “human-in-the-loop” version — robots perform each step (gather → filter → analyze → report) and a person reviews each one, under the caption “humans review each operation step by step.”*

The most exasperating part was that sometimes the meaning conveyed by ordering and arrows came out completely backwards. I wanted to show a score climbing from 94.4% to 100%, but it parked that big “100%” down at the bottom of the frame, with the arrow pointing up at the small old number above it. Read it straight through, and the whole image looks for all the world like “dropped from 100 back down to 94.4” — a step forward drawn, against all sense, as an across-the-board regression.

I added a rule for it: for any before-and-after comparison, position, arrow direction, color, and font size all have to be locked down together — the arrow points unmistakably from old to new. This rule actually got flagged by an independent review at the time and bounced back for another round of revisions before it passed muster. At the end of the day, getting a model to catch its own mistakes is notoriously unreliable — something I’ve written about specifically in [What Do You Do When an AI Agent Can’t Catch Its Own Mistakes?](https://mp.weixin.qq.com/s/naS917RIF1KqTLcfiE-L0A) — so for this kind of gatekeeping, I’d much rather hand it off to a pair of outside eyes.

![](https://miro.medium.com/v2/0*8X-s8gjR2J-rbo_8.png)

*Caption: The before/after on the score comparison — “Don’t let an ‘improvement’ read as a ‘setback.’” On the left (✗ Before), the big “100%” sits low with an arrow pointing up at a small “94.4%,” which reads as a regression; on the right (✓ After), “94.4% → 100%” runs left to right, old small and gray, new big and green, with the arrow pointing clearly from old to new.*

Here I have to let you in on a hidden truth. They’re all called “multimodal” (able to read images), but when Opus looks at an image to review and verify it, the accuracy is always just a notch short. So I laid down a requirement: whenever a GPT model can be called to look at the image, always use GPT to review how the generated image turned out.

The three specific problems above all really come down to the same thing — we’re loading the model up with too heavy a task, and the boundaries aren’t clear enough. After talking it over with it, I added a rule: before drawing anything, you have to spell out in the prompt, down to the last detail, exactly what the picture is meant to convey, and only then send it to the GPT image 2 model. That way, there’s less and less guessing and reading between the lines, and the precise positioning and requirements get spelled out in ever more detail.

There was another time when the image needed to pair each of several key points with a one-line explanation, drawing a connecting line from each point over to its line of text. But those lines all got crossed up — tangled into a knot, with the wrong explanation tied to the wrong point, and no way to tell which explanation went with which. I went several rounds with the AI and saw no improvement at all.

Then it suddenly hit me: this kind of “which point is this sentence explaining” attribution simply shouldn’t be drawn with lines stretching across half the layout — GPT image 2’s routing of lines isn’t reliable. Better to tie the explanation and its point together on the same little card, so it’s crystal clear what goes with what.

![](https://miro.medium.com/v2/0*p_tk424tOiX1tx0V.png)

*Caption: The fix for tangled connectors — “Don’t make the model route geometry; bind meaning to position and text instead.” On the left (✗ Before), the four seasons are joined to their descriptions by thin crossing lines, so the links get scrambled; on the right (✓ After), each season and its description sit bound together on one card (spring = the season when all things revive, summer = the hot season, autumn = the harvest season, winter = the cold season), clear and easy to check one by one.*

In other words, if you don’t impose constraints, one and the same relationship can be expressed in different forms. And as it happens, some of those forms are things today’s AI just isn’t good at (spatial-geometric relationships and the like) — so rather than try to teach it how to handle them, you might as well steer clear of that path of expression in the first place. As the saying goes, “there are things one simply does not do.”

Grinding through this round after round, you’ve probably caught the flavor of it by now: as a human user, you can’t predict every category of mistake the AI might make. All we can do is, in practice, play to its strengths and around its weaknesses as best we can so it knows how to do a task well, and then, with each pothole we hit, patch up the holes that might surface.

People say AI lacks vertical data in many domains. The truth is, our process of using these frameworks and giving feedback over and over *is* exactly that most precious data. Claude Code and Codex are made to be likable, which makes them all the more likely to rapidly accumulate this kind of genuine human-feedback behavioral data. Whereas if you’re a foundation-model vendor who only makes the model and not the framework, you have no way to get this data directly — you can only try to “borrow” it from the others via distillation. So you’ll see foundation-model vendors rolling out their own xxxCode products more and more, and faster and faster — Kimi Code, ZCode, and so on. Don’t think they’re making the Harness framework nice to use as a favor to us users. It’s much more that the model vendors *need* to collect more of real users’ domain-by-domain behavioral data.

## What Settles

Hard work pays off. After two weeks of polishing, when I now hand Youmind or Claude Code a fresh transcript, what comes out is basically just the way I want it.

All the flaws that used to drive me up the wall — the made-up labels, the backwards arrows, the tangled connecting lines, the goofy doodles — it now steers clear of them all. Not because it suddenly got smart, but because I turned every single pothole into a rule it has to clear before it lifts a finger.

What I deliver are batches of images. But what truly settles — what can be reused over and over — are the principles and patterns behind those images.

If you, too, are training up some AI tool, don’t expect a single sentence to make it click. Take all those “what I wanted was clearly *this* — how did it give me *that*?” moments and write them down one by one, turning each into a rule you feed back in. Of course, you don’t have to write these by hand — you just tell your AI Agent:

> *Look back over our entire conversation in this session. Pay special attention to the moments where I interrupted what you were doing to make a request — those are usually the important ones. Wherever you hit a pothole during execution, or picked up some lesson on your own, or wherever I caught a wrong direction and corrected it in time or flagged it on later review — go check whether all of it has been written down in the right place. For instance, updating the corresponding skill, or even the global config.*

Once you’ve accumulated enough of these patterns, what you hold isn’t just a usable tool — you’ve also built up a feel for how to refine a vague idea into a definite result. In a world where AI tools are increasingly the order of the day, that ability is precious and scarce.

## Sharing

This Skill that turns a transcript into a series of Keynote-style teaching images — I’ve already packaged it up and put it on Feishu, and you can grab it and install it yourself: [the lecture-image-pack sharing doc](https://www.feishu.cn/docx/CCxodX604oW0I4xehojcdL22nW1), which includes the zip and a QR code.

![](https://miro.medium.com/v2/0*ifO16a6_Hxg9s-eS.png)

*Caption: The Feishu sharing doc for the lecture-image-pack (“classroom explainer image set”) Skill, with sections on what the Skill does and how to install it.*

Installation doesn’t take any manual fiddling on your part either. Just hand the zip to your own AI assistant, have it first figure out which environment you’re running, then install it and verify on its own that it can be called up properly. When generating images it’ll draw on AI image-generation capabilities, so all you need is to make sure you’ve got a working GPT image 2 drawing channel on hand.

Here’s to a pleasant time with AI-assisted manuscript visualization — and even more, I hope that through this article you’ve come away with a method for polishing AI Skills of your own.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- [AI Makes Dazzling Slides — But Can You Still Stay in Control?](https://mp.weixin.qq.com/s/d7LAxs3bSnmfAlP8AMSkSA)
- [Claude Skill Snapshots: An “Undo Button” for Iterating on Your AI Skills](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
- [In the Age of AI, Stop “Doing Homework” — Go Create Your Own “Work”](https://wshuyi.medium.com/in-the-age-of-ai-stop-doing-homework-start-creating-your-masterpiece-009cf4f37388)
- [Don’t Let AI “Pretend to Finish Reading” for You: How I Used “Making Slides” to Force Myself Into Close Reading of Papers](https://mp.weixin.qq.com/s/x3jKgbo0qw26vPAAvn6dnA)
- [Midjourney Can Read Images Now — Is That a Good Thing?](https://mp.weixin.qq.com/s/z6AYsYZGGJx3GNGQaybTRQ)

*Caption: The Feishu sharing doc for the lecture-image-pack (“classroom explainer image set”) Skill, with sections on what the Skill does and how to install it.*

Installation doesn’t take any manual fiddling on your part either. Just hand the zip to your own AI assistant, have it first figure out which environment you’re running, then install it and verify on its own that it can be called up properly. When generating images it’ll draw on AI image-generation capabilities, so all you need is to make sure you’ve got a working GPT image 2 drawing channel on hand.

Here’s to a pleasant time with AI-assisted manuscript visualization — and even more, I hope that through this article you’ve come away with a method for polishing AI Skills of your own.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- [AI Makes Dazzling Slides — But Can You Still Stay in Control?](https://mp.weixin.qq.com/s/d7LAxs3bSnmfAlP8AMSkSA)
- [Claude Skill Snapshots: An “Undo Button” for Iterating on Your AI Skills](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
- [In the Age of AI, Stop “Doing Homework” — Go Create Your Own “Work”](https://wshuyi.medium.com/in-the-age-of-ai-stop-doing-homework-start-creating-your-masterpiece-009cf4f37388)
- [Don’t Let AI “Pretend to Finish Reading” for You: How I Used “Making Slides” to Force Myself Into Close Reading of Papers](https://mp.weixin.qq.com/s/x3jKgbo0qw26vPAAvn6dnA)
- [Midjourney Can Read Images Now — Is That a Good Thing?](https://mp.weixin.qq.com/s/z6AYsYZGGJx3GNGQaybTRQ)
