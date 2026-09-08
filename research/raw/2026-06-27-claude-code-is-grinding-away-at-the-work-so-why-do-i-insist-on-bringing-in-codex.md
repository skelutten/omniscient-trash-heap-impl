---
title: "Claude Code Is Grinding Away at the Work — So Why Do I Insist on Bringing In Codex to Tear It Down?"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/claude-code-is-grinding-away-at-the-work-so-why-do-i-insist-on-bringing-in-codex-to-tear-it-down-fa84c336365d"
published: "2026-06-27"
fetched: "2026-09-08"
reading_time_min: 17.5
tags: []
member_only: true
body_source: "medium-session"
---

# Claude Code Is Grinding Away at the Work — So Why Do I Insist on Bringing In Codex to Tear It Down?

### Only when the Agent inside the loop runs effectively on its own can [we truly stand “on the loop” and “direct with composure”](https://wshuyi.medium.com/human-on-the-loop-the-researchers-new-role-in-the-age-of-agents-c74040265459).

![](https://miro.medium.com/v2/0*2ZYCuPzArAbG0W-R.jpg)

## The Question

A few days ago, I posted a little musing on Knowledge Planet:

> *Claude Code has been running a Skill generation task for almost 2 hours now. Codex is on review duty, and it’s already blocked 6 rounds. Right now Claude Code is doggedly submitting its 7th revised plan, waiting for Codex to give the word. I’d like to commend both Agent frameworks for their earnest, conscientious work ethic 🤭*

![](https://miro.medium.com/v2/0*DNPlJPExDP34iE0T.png)

*Caption: The original Knowledge Planet post (in Chinese) — the English above is its translation. The embedded terminal shows Codex having blocked six rounds of Claude Code’s revisions, with Claude Code pushing round seven.*

Blow that image up and it looks like this:

![](https://miro.medium.com/v2/0*L3UgQ1gcTYNC6Enc.png)

*Caption: A close-up of that terminal. Claude Code reports its dependency-loop check was blocked, notes that Codex’s 4th review caught a real “major” issue being softened to “minor,” confirms round six’s blockers were fixed, and is now launching round seven — about 1h 55m in, ~237K tokens spent.*

That got a community member curious, and they asked me:

> *How is this set up? When it comes to the two of them working together, could you share how to get them collaborating efficiently, instead of fighting each other?*

![](https://miro.medium.com/v2/0*dLIxRrGWe6nBcs1T.png)

*Caption: The reader’s question on Knowledge Planet (translated above). Wang Shuyi replies: “Since so many members are asking about this, I’ll make it the topic of my next article.”*

So I promised to write an article explaining it — which is the very one you’re reading now.

## The Blind Spot

Let me start with why I have Claude Code and Codex run adversarial review on each other, burning all that money (tokens) and time.

You’ve probably run into this yourself. You ask an AI to write you some code, draft a proposal, lay out a plan — and what it hands back is always supremely confident, neatly organized, seemingly airtight. You test it with normal input, everything passes, and off you go, delivering it with peace of mind.

But the traps tend to hide in those corner cases — the ones “nobody normally thinks of, yet really do happen in the real world.” By the time one surfaces in an actual scenario, you realize that the “everything passed” confidence from before was a bad check that just bounced.

So can I just have the AI check its own work one more time?

No. I’ve tried that too many times. I even [wrote a whole article warning you never to do it](https://mp.weixin.qq.com/s/naS917RIF1KqTLcfiE-L0A).

It’s not that the AI is dumb — this is structural. Just like when a person writes something, their head is full of “how I want this to run,” i.e., the normal input. They simply don’t think of the adversarial input, because the adversarial input never once showed up in their mental picture. Ask one and the same brain to be both player and referee, and the only things it can catch are the ones it already anticipated.

That’s true for people, and it’s true for AI.

![](https://miro.medium.com/v2/0*aITlo0jhhTnUbh48.png)

At this point, a lot of people’s first reaction is: well then, just round up a few more AIs. Many heads beat one, right? Let them vote, majority rules.

Makes sense — but watch out for the following situation.

If you round up three **same-source AIs** (say, 3 Agents driven by Claude models) to vote, there’s a very good chance they’ll all make the same mistake. Because their **blind spots are shared**.

Same training tendencies, same failure to imagine that adversarial input. All three saying “no problem” doesn’t mean there really is no problem — it just means the trap happens to fall squarely in their common blind spot. What the vote produces is a more deceptive flavor of false consensus.

![](https://miro.medium.com/v2/0*boyXuBa52gWAMmeA.png)

What actually works isn’t “one more helper.” It’s “find one that isn’t on its side, brought in specifically to tear it down.”

My day-to-day workhorse is Claude Code. And over on OpenAI’s side there’s Codex — the same kind of framework, also a command-line AI coding assistant that can read files and write code.

There are just two layers separating Codex from Claude Code. First, lineage: it comes from OpenAI and runs GPT-family models underneath — a different vendor, a different source from Anthropic’s Claude Code. Second, the division of labor in my workflow: Claude Code is the workhorse, responsible for pushing the work forward, while I only haul out Codex at specific moments to “poke holes.” The key is this: while Claude Code is working, it can **run a single command** right inside the same terminal and hand the task off to Codex. We’ll get into how to do this in detail later.

Savor the picture for a second: two companies that are usually at each other’s throats, their models, placed by me into one and the same terminal window with a single command. One builds, one tears down.

![](https://miro.medium.com/v2/0*Ct6ZuAlUP86FHe5N.png)

But note: what gives this combo its real power isn’t the number “two AIs” — it’s the **triple independence** standing between the teardown guy and the working guy.

The first layer is models from different vendors. Behind Claude Code is Anthropic’s model (I mostly use Opus 4.8, because Fable 5 was unavailable the couple of days I was writing this); behind Codex is OpenAI’s GPT-5.5. The two are trained along different lines, so their blind spots overlap even less.

The second layer is isolated context. The reviewer can’t see how the builder talked itself into things along the way. It won’t get swept along by “look how beautifully I reasoned earlier” — all it faces is the cold, hard result itself.

The third layer, and the most crucial one, is the adversarial stance. The task I hand it isn’t “please verify that this change is correct,” but “please find a way to demolish my confidence in this change.” The former goes looking for supporting evidence; the latter actively hunts for trouble.

![](https://miro.medium.com/v2/0*MU10aZiTDgSauEys.png)

I also love to needle it with a deliberate extra line: “This plan was made by Anthropic’s Opus — come on, give it a review.” Codex absolutely relishes that.

So let’s get into how to actually make this division of labor work in practice, along with the traps I stepped in along the way.

## The Workflow

Let me first lay out the “revise the Skill by the rules to fix the current problem” workflow I actually run every day. It has five stages, and the order matters a lot.

Stage one: investigation. Claude Code first gets a clear read on the current state. Read the logs, read the config, look at the current behavior — what exactly is going on.

Stage two: research. On the basis of the facts, form a hypothesis about the cause of the problem, along with the supporting reasoning.

Stage three: lay out the plan. Write “how I intend to change it” into a crystal-clear proposal.

Stage four: independent verification by Codex. Hand that plan, untouched, to Codex for review.

Stage five — and only now — Claude Code executes.

Here there’s a piece of discipline I’ve nailed down hard for Claude Code: **before the investigation and the plan have fully passed review, not a single character of changes is allowed.**

How does this discipline land on Claude Code’s shoulders? It’s really just one sentence. Before letting it work, I remind it:

> *Don’t touch any files yet. Get me a clear read on the current state, form your root-cause judgment, then write out a “how I intend to change it” plan. Once that’s written, stop and wait for me to have another AI review the plan; only then do you start.*

The important part is that last half-sentence — it firmly wedges the “start working” action behind “passed review.” It won’t barge in and edit your files right off the bat.

![](https://miro.medium.com/v2/0*eAdXthtJ_LvyqYRM.png)

Why be such a stickler about this? Because once code goes in, the sunk cost piles up. People can’t bear to tear down what they’ve already written; they reflexively patch over for it. I’ve seen plenty of students at their pre-defense, facing the advisor’s revision notes, look back at their own thesis drafts with that same clinging-to-their-own-work instinct.

AI is the same. It’ll feel that it already produced a lot earlier, that tossing it out would be a shame, that just modifying on top of it would be more economical. So I spell out the requirement, moving review ahead of touching anything — catching the lousy plan and killing it while the AI Agent hasn’t gotten emotionally invested yet.

So how does this plan actually get passed from Claude Code over to Codex? It’s simply that, as Claude Code executes per the rule-bound workflow, it runs a command itself, feeding the plan as input to Codex’s command-line tool:

```perl
​
printf '%s' "$prompt" | codex exec -m gpt-5.5 \
​
  -c model_reasoning_effort=xhigh \
​
  --sandbox read-only --ephemeral --skip-git-repo-check -
​
```

Let me break out a few of the key settings in this command and walk you through them:

`codex exec` simply throws the job to Codex to run; `-m gpt-5.5` tells it to use the GPT-5.5 brain (the best GPT model at the time I'm writing this); `-c model_reasoning_effort=xhigh` cranks its reasoning firepower to the top notch, making it think one layer deeper; `--sandbox read-only` is the crucial gate. It's read-only — it can see clearly everything I've got, but it can't change a single character, can't touch my real files.

This command is a “one-shot deal”: throw something over, get a review back, clean and crisp — well suited to a one-off read-only re-check like reviewing a plan, and it’s also the workhorse of this adversarial-review setup of mine.

A quick aside on a “shortcut” you may run into while reading up on this: OpenAI’s Codex plugin installs a `/codex:rescue` quick path for Claude Code. Type `/codex:rescue` straight into the chat box plus whatever you want Codex to inspect or change, and it hands the job over for you — and it can even run in the background and pick up where the last round left off. But note that this handling is **not read-only**, so I lean toward the command-line approach I described above.

Who goes first, who calls whom, where the human steps in across this whole dance — one look at the figure below and you’ll get it:

![](https://miro.medium.com/v2/0*p7Pzn0omeuj3x4-K.png)

When it’s time for review, the opening I give Codex is nearly fixed — you’re welcome to copy it too. First, spell out clearly its identity and situation, so it doesn’t misjudge:

> *Your identity right now is GPT-5.5; you’re locked in a disposable sandbox where you can see my stuff clearly, but any change you make is used-and-discarded and never lands on my real files (more on this in a moment); you’re not on the same team as the one doing the work, so tear it apart — don’t hold back.*

Then tack the two adversarial directives from earlier onto the end, word for word: one is “demolish my confidence in this change, don’t endorse it”; the other is “doubt everything by default, and treat anything that only works when all goes smoothly as a genuine weak point.” Identity, situation, stance — once all three are in place, an opening is complete.

There’s one term here I need to explain for you.

“Sandbox” — just think of it as a disposable glass workshop. I put the reviewing AI inside this workshop; it can see everything outside clearly through the glass, and it can gesture and tinker inside, but the workshop gets torched after each use. Any change it makes can’t be carried out and never lands on my real files. **This is deliberate.** What I want is for it to “judge only, never lay a hand on my real stuff” — the moment it lays a hand on them, it turns right back into both player and referee.

What do I have it review? Four things, which I also write straight into the directive I give it: feasibility, completeness, consistency, data accuracy. Just have it work through these four axes one by one.

And what if Codex nods on all four axes? Then I let it start working straightaway, without it turning back to ask me “May I begin now?” Passed is passed — a settled thing doesn’t need repeated confirmation. Save the precious human judgment for where judgment is genuinely needed.

## The Backstop

A workflow alone isn’t enough; you also need an iron rule as a backstop, or the workflow will get quietly hollowed out.

The iron rule is this: **when Codex says FAIL, Claude Code can’t just wave it off and reject it.**

Codex isn’t always a master oracle. If Claude Code obeyed it on everything, this adversarial setup would become a sham too. So Claude Code may, after careful thought, reject a problem Codex points out or a plan it proposes. The trouble is that once Claude Code has this privilege, it often opts for “not careful thought,” rejecting outright instead — with this arrogant air of “I’ve been at this for ages, I’ve got the experience, what does a little kid like you know?”

So my requirement goes like this. If Codex rules Claude Code’s plan a fail, Claude Code has only three roads it can take. Either fix it obediently; or push back — but the pushback must come with hard evidence that can be rerun and verified locally, e.g., Claude Code searches the file and lays the actual results it found in front of Codex; or honestly explain to the user that, under the objective conditions, this problem or revision plan Codex points out doesn’t apply, and give sufficient reasons. Beyond these, there is no fourth road.

![](https://miro.medium.com/v2/0*6b8k7p3FGXF4tit1.png)

I’ve been burned.

The first time was on a literature-review job. The reviewing Codex did a beautiful job, accurately flagging 8 author-attribution errors, all of the most serious grade of hard fault: the source was written by A, but in the draft it got pinned on B.

And the result? The executing Claude Code side, with one line of “Codex is probably just guessing anyway,” downgraded and skipped all 8.

Those 8 errors went into the final draft, untouched, every one.

See — the reviewer, Codex, got it right. But its correct conclusion was overridden by one flippant “it’s just guessing.” The problem wasn’t with the review ability at all; it was at the “the executing Agent didn’t own up” link.

The second lesson: that time Codex returned a FAIL, but the working Claude Code side didn’t go change the files — it just threw the same thing back for re-review. Codex, naturally, returned FAIL again. Thrown back again, FAIL again.

Just like that, “passing the buck” back and forth, 8 straight FAILs, and on the 8th the process flat-out crashed mid-run. The crash itself didn’t matter; over the course of this buck-passing, around 700,000 tokens got torched.

Money and time, all down the drain, and not a single problem solved.

You’re probably thinking back to that screenshot at the top of this article and getting confused. Same repeated submitting, same repeated blocking — yet that time I went out of my way to commend it. How did this time become a money-burning joke?

The difference is just one thing: in the opening case, every round it submitted had genuinely changed, new content in the files — it was advancing step by step, gaining ground. This time, it kept throwing back a plan that hadn’t moved at all. The former is being earnest; the latter is just spinning its wheels. On the surface, these two kinds of “repetition” look far too alike.

From then on I added one more rule: before Claude Code resubmits a plan, the files must contain real, concrete new changes — or else it must plainly declare that this is a “rebuttal rerun” carrying new evidence. Repeatedly feeding the reviewer the exact same untouched thing, hoping Codex will let it slide on a whim some round, is absolutely forbidden.

## The Payoff

A few days ago I had Claude Code write a checking Skill. Its job was to verify a checklist: I supply the text material, Claude Code supplies the illustrations. It uses the checklist to verify whether every illustration that should be there got matched up, and whether the body text really corresponds to each one. After Claude Code produced its result, it went to Codex for review. Three rounds in, Codex dug out a full four “secret passages” from underneath this supposedly airtight “checkpoint.”

Number one: a stray item in a non-standard format had slipped into the checklist; the checkpoint only inspected standard-format items and turned a blind eye to this stray one, so it strolled right in.

Number two: a key field that should only count when it reads “adopted” — yet sticking a space on either side of the value fooled the check. Because the checkpoint forgot to trim the leading and trailing spaces.

Number three was even nastier: for a certain path field, if you fill in an absolute path, or use a “parent directory” style to jump outward, you can escape the project’s bounds and point at any file in the system at all. The cause was that the function the checkpoint used to join paths simply ignores the prefix when it meets an absolute path. This is a deeply buried language trap, and Claude Code hadn’t noticed it.

Number four: you could pile up a heap of “adopted” items in the checklist to make the count look impressive, while in the body text not a single illustration that should be covered actually got covered. Because that checkpoint only counted the checklist, without setting enough constraints to guarantee a reverse check against the body.

![](https://miro.medium.com/v2/0*ewbrZUvuG4DBjM9a.jpg)

Finding the holes isn’t the end of it. For every hole dug out, I’d turn back and call out to Claude Code: “Take the input that just slipped through, build one exactly like it, write it into a test, and then set a rule: from now on, whenever this kind of input shows up, it must report FAIL.” This is called a reverse (negative) control. I don’t have to handwrite the test myself — one sentence handed down, and it plants the sentinel for me. And one hole often spawns several tests — the hole itself counts as one, each of its winding variants counts as one more, plus the normal input that was supposed to run through in the first place. Stacking it all up that way, that checkpoint ended up amassing 21 test cases.

I don’t just plug the secret passage; I plant a permanent sentinel right at its mouth. If one day it edits the code and carelessly opens that door again, this sentinel will shout instantly. In the end, that checklist’s checkpoint had all 21 test cases green, every adversarial input among them firmly blocked, while the normal product still sailed through smoothly.

![](https://miro.medium.com/v2/0*FOLOJB-zTtgSHO-k.png)

This back-and-forth is where the “collaboration” I’m talking about actually happens. It’s not two AIs politely nodding at each other; it’s one furiously building, one furiously tearing down, with me watching in the middle, breaking into a cold sweat:

> *Whew, that was close.*

## The Limits

Having sung all these praises, I also have to honestly tell you about the problems this kind of Agent collaboration may have.

The biggest problem is that it’s expensive.

The best model doing the work, another top-tier model finding fault. That’s all hard cash. I really couldn’t bear running both sides on the top-spec $200 plans, so I switched to a $100 subscription for each — roughly a quarter of the quota of the absolute top tier.

Not long after I had the two of them working and posted that musing at the top, my Claude Code subscription status already looked like this.

![](https://miro.medium.com/v2/0*Bpa13uqPC3eoxOfO.png)

Codex’s side wasn’t any better off.

![](https://miro.medium.com/v2/0*Qhanz6qu195chCK6.png)

That hit me pretty hard at the time. My adversarial-review setup can only be pulled off when the two cooperate. If Codex burns through so much that it runs out of quota, what then? And sometimes you also hit Codex being temporarily unreachable, or running into other bugs (otherwise it wouldn’t keep resetting quota and the like) — so what then?

After some thought and research, I swapped the reviewer from Codex over to a model from another company — Zhipu’s GLM 5.2 — to fill the role. In practice, all I swapped out was that “teardown backend”; the spiel I give it (play the attacker, doubt by default, treat anything that only works when all goes smoothly as a weak point) didn’t need a single word changed. Note that this move holds up precisely because GLM is yet another vendor’s model, not the same source as either Claude or Codex — the cross-source independence I want still holds.

There’s a fine line I guarded very tightly when drawing up the rules: only when it’s clearly a “genuinely unusable” case — quota, connection, that kind of thing — may the reviewer be downgraded off Codex. If what it reports is an authentication error or a dead key, Claude Code is absolutely not allowed to quietly downgrade the reviewer and thereby make it easier to fudge its own way through.

Speaking of which, I want to talk about what the human user actually does in this whole mechanism’s design.

The direction is set by me. Whether to change and which way to change — the machine doesn’t decide that for me.

The call is mine to make. Codex or GLM, they only give suggestions. If they reach agreement, execute straightaway and don’t bother me; if a directional disagreement or doubt arises, I’m the one who decides.

## In Closing

When you get two AIs to cooperate, the power has never lain in the number “two.” What actually does the work is this three-piece set. An executor in charge of building, an independent reviewer that’s a different source from it, isolated, and holding an adversarial stance, plus a human willing to own up, willing to keep the books, willing to make the call. Take away any one of them and it falls apart.

![](https://miro.medium.com/v2/0*z36-BXT_NcaUJ7Xe.png)

Tools get swapped out. Today I pair Claude Code with Codex; when the quota runs low I’ll also temporarily bring in GLM. And tomorrow, or next month, it could be a completely different combination. But the rule I’ve distilled won’t change: **never let the AI Agent that writes the thing review its own work.**

If you, too, often get burned by that “supremely confident” air of AI’s, why not try one minimal thing starting today: hand this article’s approach to your go-to AI Agent and have it use it as a reference for building the mechanism. Next time you have an AI write any chunk of checking logic that’ll be run over and over, don’t rush to believe its “everything passed” — hand it to a different company’s model, and have it independently judge whether the result might have problems.

After all, only when the Agent inside the loop runs effectively on its own can [we truly stand “on the loop” and “direct with composure”](https://wshuyi.medium.com/human-on-the-loop-the-researchers-new-role-in-the-age-of-agents-c74040265459).

You might not feel like typing all the above into Claude Code yourself. No worries — I’ve made the third-party independent adversarial review into a Skill and [open-sourced it in this GitHub repo, where you can grab it and use it straight per the instructions](https://github.com/wshuyi/codex-verify).

![](https://miro.medium.com/v2/0*pV3O8qBHPm-zVHAB.png)

With it, your Claude Code is no longer just charging ahead on its own; your in-house “strategist” — or, let’s be honest, your snarky frenemy — at its side will keep reminding it:

> *Think again.*

This kind of mechanism makes Claude Code work more steadily, dodging a lot of errors caused by glaring cognitive blind spots.

Wishing you happy AI-assisted work.

If you find this article useful, please hit the `Applaud` button.

If you think this article might be helpful to your friends, please share it with them.

Feel free to [follow my column](https://wshuyi.medium.com/) to receive timely updates.

Welcome to [subscribe to my Patreon column](https://patreon.com/wshuyi) to access exclusive articles for paid users.

To watch video content, please subscribe to [my Youtube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)

## Further Reading

- [Claude Code, Codex, OpenClaw — How Do I Get Them to Work Together?](https://mp.weixin.qq.com/s/Sa8j6v29txgXv9raezs8TQ)
- [Claude Skill Snapshots: An “Undo Button” for Iterating Your AI Skills](https://wshuyi.medium.com/skill-snapshot-your-undo-button-for-claude-code-skills-19d8f44fbe20)
- [Still Agonizing Over Whether Someone’s Work Is “Pure Human” or Has AI Mixed In? You May Need to Get Used to Hybrid Intelligence](https://wshuyi.medium.com/hybrid-intelligence-what-youre-really-buying-ee4ae5000188)
- [When AI Detection Meets Careful Polishing: Is the Line Between Academic Originality and Plagiarism Still Clear?](https://wshuyi.medium.com/ai-detection-vs-language-polish-blurring-lines-in-academic-integrity-dab08be075c2)
- [You Let a Third-Party Tool Use Your AI Subscription — Anthropic, OpenAI, and Google React in Wildly Different Ways](https://mp.weixin.qq.com/s/MJsxREgAjOejOcHd-Uepfw)
