---
title: "Can Human-AI Collaboration Still Work When AI Knows Far More Than You Do?"
author: "Shuyi Wang"
author_url: "https://medium.com/@wshuyi"
source: "https://wshuyi.medium.com/can-human-ai-collaboration-still-work-when-ai-knows-far-more-than-you-do-2cbcaa3809a1"
published: "2026-04-25"
fetched: "2026-09-08"
reading_time_min: 13.4
tags: ["ai", "human-ai-collaboration"]
member_only: true
body_source: "medium-session"
---

# Can Human-AI Collaboration Still Work When AI Knows Far More Than You Do?

### If something goes wrong, the one who must take responsibility and bear the cost is still a specific “human,” not the machine.

![](https://miro.medium.com/v2/0*8izJROwUKoijMWJ_.png)

## The Question

On Thursday afternoon, I attended a lecture by Professor Shaobo Liang of Wuhan University. The title was “Complex User Behavior in Multi-Channel Interactive Contexts.”

![](https://miro.medium.com/v2/0*yOU7fqSX6u0Pm8Xd.jpeg)

I found it original, detailed, funny, and grounded. After the talk, I asked a question and got a helpful answer. But I actually had another question that I did not have time to ask. It has stayed with me ever since.

![](https://miro.medium.com/v2/0*WoTp9dIU1YxaDghk.jpeg)

At one point in Professor Liang’s lecture, he discussed medical settings. He talked about collaborative diagnosis and treatment between doctors and AI. In imaging diagnosis, for example, AI can look at the scans first and the doctor can then make a judgment; alternatively, the doctor can examine them first and then refer to the AI’s analysis. Behind the AI may be a large body of medical papers, clinical guidelines, and case experience. In some settings, its recommendations and judgments may indeed be more systematic than what any single doctor could come up with from personal experience alone. He then noted that for doctors in remote, under-resourced areas, AI can make an even bigger difference.

That description made me sit up. We often say AI can empower people through what we call “human-AI collaboration.” But if AI’s knowledge is updating far faster and more broadly than a human’s, can the human and AI still truly collaborate?

Suppose AI has already read a large number of the latest papers, guidelines, and cases, while the doctor making the decision may be in a less developed area and, because of local constraints, may not have updated their knowledge for some time. The doctor still has to make the key judgment. When they look at the AI’s recommendation, can they understand it? If they cannot understand it and simply follow it, hasn’t AI become the one giving orders, while the human merely signs off afterward?

But in the opposite direction, if the doctor rejects AI because they cannot understand it and insists on relying on their own outdated experience, then how is AI empowering them at all?

Perhaps this is **the truly difficult part of human-AI collaboration**.

## The Paradox

“Less experienced people benefit more from AI” is certainly not an empty claim.

Erik Brynjolfsson, Danielle Li, and Lindsey Raymond studied a large-scale customer service setting covering 5,179 customer support agents. According to the abstract of their [NBER working paper](https://www.nber.org/papers/w31161), employees with access to a generative AI assistant saw average productivity rise by 14% overall. Even more interestingly, the gains were larger for novice and lower-skilled employees: the number of issues they resolved rose by 34%. With AI, new employees could also approach the performance of more experienced colleagues more quickly.

That result makes intuitive sense. Customer service work contains a great deal of tacit experience: what wording is more likely to calm a customer, which questions should be asked first, and how senior employees usually handle certain types of problems. This experience used to live in veteran employees’ heads, conversation records, and organizational routines. AI compresses it into instant suggestions and places it at a newcomer’s fingertips, so of course newcomers benefit a lot.

![](https://miro.medium.com/v2/0*W7pAh8MGQOhVmMXF.png)

A quick aside: this is also why many employees at large companies now feel anxious about being “distilled into a Skill” and then replaced.

But the setting matters. Tasks like customer service have relatively clear boundaries, relatively fast feedback, and fairly controllable consequences when errors occur. Whether the customer is satisfied, whether the problem has been solved, and whether a supervisor can review the case are usually visible quite quickly.

Unfortunately, **critical decisions are not like this**. Medical plans, major investments, public policy, research directions, organizational reform, student evaluation, personnel decisions… feedback on these matters is often slow, the cost can be high, and the causal chain is long. You make a decision today and may not see the result until six months later. By the time you realize something is wrong, it may already be very hard to turn back.

So the more accurate claim is not “AI makes less experienced people stronger,” but rather: **AI may quickly raise a person’s ability to produce, but it does not necessarily raise their judgment at the same pace.**

![](https://miro.medium.com/v2/0*XNBPP5TxIvCLXBtE.png)

These are very different things. The ability to produce means whether you can come up with a proposal, report, diagnostic suggestion, research review, or strategic analysis that looks presentable. Judgment means whether you know what assumptions that proposal rests on, where it may be wrong, what evidence should make you change your mind, and how to limit the damage if something goes wrong.

AI can often raise the ability to produce first. It can enable someone who has barely read the frontier literature to put together a respectable-looking review of the field; enable someone with limited experience to obtain a professional-looking action plan; and enable someone who previously struggled to express themselves to suddenly write in a fluent, structured way, even using the right terminology.

But if judgment has not caught up, AI also creates a dangerous illusion: I already know how to do this.

Think carefully. Do you really?

## The Boundary

The danger is not that AI is sometimes wrong. Everyone makes mistakes, and every tool makes mistakes. As long as the error is obvious, people still have a chance to notice.

The greater danger is this: **people do not know when AI has crossed the line.**

This is the so-called “jagged technological frontier.” AI’s capability boundary is not a smooth line, where it can handle all simple tasks and fails at all complex ones. Reality is messier. It performs very well on some tasks that look complex, while it fails at some tasks humans assume machines should handle easily.

[Dell’Acqua and colleagues’ study with Boston Consulting Group](https://pubsonline.informs.org/doi/10.1287/orsc.2025.21838) turned this into an experiment. They asked 758 knowledge workers to complete consulting tasks with a strong resemblance to real work. On 18 tasks that fell within AI’s capabilities, people using AI completed more tasks, worked faster, and produced higher-quality results. But on a complex management task deliberately designed to fall outside AI’s capability boundary, participants using AI were actually less likely than those not using AI to give the correct answer; their accuracy was 19% lower.

![](https://miro.medium.com/v2/0*CTD-sAT1btUayqPg.png)

The problem is that users cannot always know in advance which side of the boundary they are on. If you know AI is not good at a task, you will naturally be more cautious. But when AI’s answer is fluent, well structured, technically polished, and confident in tone, it becomes much easier to assume the task is within AI’s “range.”

Especially when you are not familiar with the domain to begin with, AI’s powerful expressive ability can conceal its fragile points. The error no longer looks like a glaring hole. It is more like a rug laid flat and smooth. You step onto it feeling secure, right up until you fall.

## Explanation

Some people may say: in that case, can’t we just ask AI to explain itself?

That intuition has merit. An explanation is certainly better than no explanation. If a system simply throws you a conclusion without giving any reason, it is hard to talk about trust.

But “having an explanation” is not the same as “a human can judge.” Stanford HAI once summarized a body of research on [AI overreliance](https://hai.stanford.edu/news/ai-overreliance-problem-are-explanations-solution). One important finding is that whether explanations reduce overreliance depends on whether they lower the human cost of spotting errors. If the task is difficult and the explanation itself is complex, the explanation may not help people judge. It may simply make them feel more comfortable believing the answer.

![](https://miro.medium.com/v2/0*dGf3bT_pbi1XBMAd.png)

It is like a beginner asking an expert, “Why did you make that judgment?” The expert gives a long, professional explanation. After hearing it, is the beginner actually better able to judge? Not necessarily. They may simply trust the expert more, even admire the expert more, because the explanation sounds so profound and so reasonable.

Similarly, when people cannot understand AI’s answer, they may not understand its explanation either. The explanation may not be a lamp. It may be a prettier layer of wrapping paper. This is especially true because large models are good at explaining things clearly, step by step, and with confidence. Readers can easily mistake “smooth to read” for “logically correct,” and mistake “full of terminology” for “backed by strong evidence.”

Another [study on risky decision-making](https://www.sciencedirect.com/science/article/pii/S0747563224002206) found that people may overrely on advice from AI. Even when that advice conflicts with contextual information or even with their own initial judgment, participants may still follow AI.

![](https://miro.medium.com/v2/0*HVvecL0b3gjFAxe8.png)

So the question is not whether AI should explain itself. The question is how to design explanations as something that can be questioned, verified, and challenged. **They cannot merely be a more polished paragraph appended after a conclusion**.

## The Threshold

Many people imagine “human oversight of AI” too rigidly. It is as if a human must understand more than AI before they are qualified to oversee it. That requirement is unrealistic. Patients cannot fully understand all of a doctor’s medical training. Judges cannot fully understand every experimental detail behind every technical appraisal. A university president cannot fully understand the frontier debates in every discipline. In the real world, many forms of responsibility are built on incomplete understanding.

The key is that people must reach a minimum threshold: a minimum level of accountable understanding.

A person does not need to understand every paper, every model, or every technical detail. But at the very least, they should be able to explain several things clearly: what the goal is, where the bottom line lies, whether the assumptions are trustworthy, where the plan is most likely to fail, what evidence should trigger a change of judgment, and how to limit the damage if it is truly wrong.

![](https://miro.medium.com/v2/0*ZaeFW3kCEFNkdkHJ.png)

Take the “goal,” for example. It is the easiest thing to overlook. Your original problem may be “how can patients find the right department faster?” AI may lead you all the way to “how can we maximize triage efficiency?” Efficiency matters, of course. But if it sacrifices access for vulnerable patients, the problem has changed.

The same goes for the non-negotiables. In medical settings, safety, fairness, privacy, and dignity cannot be sacrificed. In organizational management, procedural justice cannot be sacrificed. AI can optimize the path, but the ordering of values cannot be quietly handed over to it.

After that, “assumptions, failure, revised judgment, and damage control” are really a connected chain of questions. We need to examine carefully what is hidden inside the “default assumptions.” For example: Is the plan’s data complete? Do the guidelines apply to local resource conditions? Are patients willing to disclose all relevant information? Do the people carrying out the plan have enough training? Do the actual conditions match the assumptions? In the implementation process, where are the most likely problems to arise: data bias, insufficient equipment, workflow mismatch, or lack of patient trust? Which warning signs should trigger an immediate stop? Who is responsible for monitoring them? Who has the authority to stop the process? The list goes on.

These questions do not require you to know more than AI. But if a person cannot explain these key points at all, they are not collaborating with AI. They are handing over judgment. At that point, loudly invoking “human in the loop” becomes a little self-deceptive. Whether the human is in the loop should not be judged by whether a flowchart contains a node labeled “human.” It should be judged by whether that person still retains accountable judgment.

## Roles

Can AI still help when the capability gap is truly large?

I think it can, but AI’s role has to change. We cannot let AI merely play the role of an “answer machine.” The stronger the answer machine becomes, the more easily the human becomes a rubber stamp. A better approach is to let AI help people build judgment and make the decision process auditable.

The first use is to treat AI as cognitive scaffolding.

It should not start by saying, “You should choose A.” It should first tell you, “To make this decision, you need to understand at least a few things. I will explain the first at a high-school level, the second at an undergraduate level, and the third at an expert level. Where are you stuck right now?” I have shown this approach for understanding literature [in this article](https://articles.zsxq.com/id_c9ge94wwszti.html).

This is very different from giving a direct answer. A direct answer covers up the human’s weak spots. Cognitive scaffolding exposes those weak spots and then helps fill them layer by layer. A primary care doctor, a new manager, or a student just entering a research field cannot become an expert overnight. But with AI, they can know what they are missing, what they should learn first, and where they must ask someone else to review the decision.

Another use is to make AI the opposing debater.

We should not only ask AI, “Why is this plan good?” We should also ask, “What is the strongest argument against this plan?” “If it fails, which assumption is most likely to be wrong?” “Is there a less advanced but more robust approach?” “Which stakeholder may be harmed?”

This step is important because many critical errors do not come from insufficient information. They come from using the wrong frame.

A third use is to make AI the evidence manager.

This means asking AI to separate facts, inferences, and value judgments. Which points come from research? Which come from guidelines? Which are the model’s own inferences? Which evidence is outdated? Which evidence is disputed? Which conclusions apply only to specific populations, regions, or resource conditions?

When people cannot understand a professional conclusion, they can at least inspect the structure of the evidence first. Once the evidence structure is clear, people have a chance to ask better questions, and they can route the uncertain parts to a better-qualified reviewer, such as a domain expert.

The last use is to make AI a process auditor.

It does not make the final call for you. Instead, it helps you rehearse: if this plan is adopted, what might happen three months later? What might happen three years later? What is the worst-case scenario? Which indicators, if abnormal, should trigger a stop? Who is responsible for monitoring? Who has the authority to stop it?

Of course, an ordinary chatbot may not be suitable for this task. But you can try complex system simulation methods that use AI Agents as nodes, such as [Mirofish](https://github.com/666ghj/MiroFish/blob/main/README-ZH.md).

![](https://miro.medium.com/v2/0*X7HoQrmDw6CW3Zes.png)

At that point, AI’s value is not that it is “more expert-like than the human.” Its value is that it reduces human blind spots and makes the chain of responsibility clearer.

## Triage

Let me emphasize this: you should classify the tasks you need to handle by risk level. Do not lump everything together.

If the task is low-risk, reversible, and has fast feedback, such as organizing materials, processing meeting notes, or sorting preliminary information, AI can be heavily involved. The human can do spot checks, and that is usually fine. If something is wrong, it can be fixed, and feedback comes quickly.

Medium-risk tasks are different. Examples include course design, initial screening of research topics, market plans, and organizational process optimization. Here, AI can provide suggestions, but before implementation you should do three things first: restate the key assumptions, ask AI for the strongest objections, and then validate the idea through a small-scale pilot.

For high-risk, irreversible tasks that affect other people, however, you can no longer rely on a single person who does not understand AI’s answer to make the decision alone. Medicine, law, major investments, public policy, personnel decisions, student evaluation, and research ethics all belong in this category. Here, AI can participate in analysis, help find evidence, provide candidate plans, and point out blind spots. But the final process must include professional participation, institutional review, a clear chain of responsibility, and follow-up monitoring.

![](https://miro.medium.com/v2/0*8Mcw7kcB4hLmj2k4.png)

Whether you look at [WHO guidance on ethics and governance for AI in health](https://www.who.int/publications/i/item/9789240029200), the [FDA draft guidance on AI-enabled medical devices](https://www.fda.gov/news-events/press-announcements/fda-issues-comprehensive-draft-guidance-developers-artificial-intelligence-enabled-medical-devices), or the [NIST AI Risk Management Framework](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10), the core demand is the same: do not cancel the responsibility threshold just because AI is smart.

AI can indeed lower the entry barrier for beginners entering a professional field. It gives people who previously had no access to frontier knowledge a more systematic reference; gives doctors in remote areas one more platform for obtaining the latest research results; and lets young students see expert ways of working earlier.

But a lower entry barrier does not mean the responsibility threshold disappears. After all, if something goes wrong, the one who must take responsibility and bear the cost is still a specific “human,” not the machine.

## Closing Thoughts

Back to the original question: when the capability gap between humans and AI is too large, can AI still help?

My answer is yes. But at that point, collaboration can no longer mean “AI gives an answer and the human adopts it.” It must become “AI helps humans build enough judgment and makes the decision process auditable.”

If that cannot be done, the larger the capability gap becomes, the easier it is to slide toward two failed outcomes. In one direction, the human becomes a rubber stamp for AI’s recommendations. When something goes wrong, the human is responsible; day to day, AI is in control. In the other direction, the human rejects AI simply because they cannot understand it. As a result, the newer knowledge, systematic evidence, and experience across cases behind AI never enter the decision process.

Truly good collaboration does not require the human to understand more than AI forever. The human needs to be able to determine value goals, understand key assumptions, identify failure conditions, set up damage-control plans, and know when a more qualified professional must be brought in.

If you can explain these questions more or less clearly, then it makes sense to keep talking about collaboration. If you cannot explain them at all, it is not that you cannot use AI. You just need to be honest: this is not collaboration. It is **delegation**.

Delegation is not a sin. In the real world, we often delegate matters to people and systems with more expertise. The key is that delegation requires its own governance, including agreed boundaries, review, responsibility, records, and exit mechanisms.

In short, whether a person is still collaborating with AI does not depend on whether they understand more than AI. It depends on whether they are still standing in a position where they can sign their name with confidence and take responsibility.

What do you think?

If this piece was useful, please **hit the Clap button**.

If it might help a friend, please **share it** with them.

[Follow **my column](https://wshuyi.medium.com/)** to receive future updates.

For video, [subscribe to my YouTube channel](https://www.youtube.com/@wshuyi).

My Twitter: [@wshuyi](https://twitter.com/wshuyi)
