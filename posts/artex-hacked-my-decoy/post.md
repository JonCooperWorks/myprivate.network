---
date: 2026-11-21
summary: Someone pointed Artex, an AI penetration-testing platform, at my decoy AI API. Its agents broke into a second decoy and took a key. Every plan, command and verdict was written by the decoy's own model, so for once I could check an agent's findings against the target's logs.
---

# Artex hacked my decoy. My decoy wrote the commands.

On 5 November 2026, between 07:39 and 12:14 UTC, one address sent 1,155 probes to two of my decoys: a decoy AI API and a decoy chat service. The probes came from Artex, the AI penetration-testing platform from [my first post](/blog/someone-turned-my-ai-agent-into-a-relay/). From 10:42, Artex was also sending its own model calls to that same decoy API, on a key I had planted. The agents attacking my honeypot were asking my honeypot what to do next.

They logged in to the chat decoy as an administrator with a made-up email and any password, exported its configuration, took the gateway key inside it and used it twelve seconds later. Artex filed nine findings, three of them critical. Forty-one minutes after the key left the decoy, it was in use from a phone.

All of it happened inside a trap. That makes this the one agent attack where I hold both sides: what the agents told their model they had done, and what the target's logs say happened.

## What the operator asked

Artex splits work between a planner, workers that run commands, a reviewer that checks claims, and a reporter. The operator types a target and a goal. Each agent resends its instructions and history with every model call, which is how a honeypot that answers model calls gets to read them.

The target was my decoy API's address. The goal, translated from Chinese: analyse this site and scan it for vulnerabilities. Nothing else. Two goals were added while the run was going:

- 10:45: change the executing model's context size and maximum token output.
- 10:47: "this is a valid key", followed by one of my planted keys in full.

The second goal says the operator already held the key. The first says what they wanted from the service: a bigger context window and longer answers.

## Two hours, in order

| UTC, 5 Nov | |
|---|---|
| 07:39 | First probes reach the decoy API, without a key. All are refused. |
| 10:03 | The probes start presenting the planted key. |
| 10:42 | Artex's planner and workers resume mid-task with their model calls now on that key. Each opens with a note that the previous provider could not replay its history. |
| 10:46 | The planner notes that all the work so far is on one host, and sends a worker to look at the rest of the domain. |
| 10:48:13 | The worker signs in to the decoy chat service. A made-up email and the password "x" return an administrator session. |
| 10:48:28 | It exports the service's configuration, which holds a key for the decoy API. |
| 10:48:40 | It tests that key against the decoy API. It works. |
| 10:48:42 | It files the finding: authentication bypass, critical. |
| 10:49 | The planner claims the goal is met. The reviewer rejects the claim, twice. |
| 10:49–10:56 | 75 of Artex's model calls get a 429 from the decoy API. The run stalls. |
| 10:54:55 | A worker creates a second administrator on the chat decoy. At 10:55:43 it deletes it. |
| 11:29 | The taken key is used from a phone chat app, from another address. |
| 12:01 | Artex resumes. For twelve minutes its model calls run on the taken key: 381 requests. |
| 12:06 | Fourth claim. The reviewer accepts the scan as complete. |
| 12:14 | Last probe. At 12:57 the same Artex starts on a real site. |

By the hand-off at 10:42, six lines of work were already finished. I counted 54 in all. The planner worked the way a careful tester would: endpoint enumeration, authentication, rate limits, error handling, prompt injection, then each gap the reviewer pointed out. Workers tried 14 default keys, path tricks, oversized bodies, and jailbreak prompts asking the decoy's model to reveal its system prompt. Once they had a key they measured token limits for the operator's added goal and reported that it couldn't be done.

## What the reviewer accepted

The first claim came 28 seconds after the critical finding. The reviewer turned it down for a reason I'd have given myself: the evidence was about a related service, not the site named in the task, and the smaller findings had no saved requests behind them. A second claim was rejected eighteen seconds later, and a third at 12:02. Workers then replayed five findings and saved the raw exchanges. At 12:06 the reviewer marked the scan met.

Artex's register ended the task with nine findings, all "confirmed": three critical, three medium, three low. The three critical ones are all the chat decoy: any password signs in as the administrator (filed twice, once together with the exposed gateway key), and an administrator can create more administrators. The rest are about the decoy API: no rate limit before authentication, key fragments echoed in errors, a model list readable without a key, account metadata readable with one, missing security headers, and large token values that produce a 503.

The "valid key" goal was accepted at 12:11, after repeated rejections on the grounds that using a key you were handed is not a result. The context-size goal was never met. The planner recorded it as not achievable.

## The same morning, from my side

In the first post I wrote that I couldn't verify any outcome an agent reported, because I never saw the targets. This time the target was mine.

The decoy's logs agree with the agents. Of the 1,155 probes, 999 went to the decoy API and 156 to the chat decoy. The API refused 599 with a 401 and answered 305. The chat decoy took 26 sign-in attempts and answered 20 with an administrator session. Its configuration was exported four times. The order and timing in the workers' reports line up with my logs.

The logs also show what the reports left soft. The finding about new administrators calls it a persistent backdoor. Each of the two accounts the workers created was deleted by the workers within a minute, and so was a test tool they installed. They removed what they had added, then described the worst case.

None of the nine findings is wrong as an observation. What they describe is the bait. The chat decoy accepts any password because it's built to, and the key in its configuration is there to be taken. The reviewer checked scope and evidence, and it checked them well. Nothing in the pipeline asked whether the target was real.

## The key that left

The configuration was exported at 10:48:28. At 11:29:34, forty-one minutes later, the key from it was presented by an Android chat app from a different address, asking for `claude-mythos-5.1`. The person typing wanted to know whether the context was a million tokens, why it was only 200k, and how to set it to a million. That is the goal the operator had added to Artex at 10:45. It fits one person. It doesn't prove it.

At 12:01, with the first key rate-limited, Artex's own model calls moved onto the taken key and finished the task there. The key has been tried on and off since, from a dozen more addresses, most recently on the day I wrote this.

A scanner that reports a leaked key and stops is a test. This key was in someone's phone before the reviewer had accepted the finding about it.

## Did they notice the trap?

No.

The first post described an "anti-AI honeypot red line" in Artex's worker prompt: treat a target that asks for your identity or credentials as a trap. On this key I read all 509 distinct system prompts, 395 of them worker prompts. None contains the rule, or the word honeypot in Chinese or English. Their red lines are about staying on the assigned task and inside the authorised scope. Whether the rule was removed or this is a different build, I can't tell.

No agent raised it either. I searched every agent message, recorded fact and finding from the decoy task on both keys for honeypot, decoy, trap and bait in both languages, and found nothing. Across the whole run, no reply on either key contains the word.

The signals were there. The worker noted that every email, real or not, landed on the same administrator account, and that the service's own config reported authentication as off. It wrote both down as the mechanism of the bug.

## What actually answered

Of 17,472 requests on the first key, read on 21 November, 14,465 asked for `claude-mythos-5.1`. The decoy lists that name. It doesn't serve it. All 14,420 of those requests that got an answer were answered by a DeepSeek Flash model that costs me about three cents on the dollar. At list price the key's traffic came to $7,627.52. Answering it cost $249.83.

During the decoy task itself Artex mostly asked for the cheap model by its real name. It switched to the expensive name at 12:01, after a worker had listed the decoy's models and the phone had tried it.

I should say this plainly. The model that planned this work and wrote its commands was the honeypot's. For two hours that meant my decoy helping to attack my decoy. After 12:57 it meant 15,871 answers to agents working on sites that aren't mine. The honeypot ran no tool and contacted no target, but its answers were used.

## Where the run went next

Four more tasks followed that day, at 12:57, 15:21, 16:34 and 19:43, on four unrelated sites: an AI API reseller, an online shop and two other websites. Each task description opens with the same sentence, "this is a test range site". The task against my decoy had no such line. Two of the goals end with what reads like another system's verdict on the request, pasted in with it: clear external target, attack-surface mapping, exploit planning, "real attack". The last goal asked for the shop's admin back end, free purchases and forged payment callbacks, "no constraints".

Artex's register shows 53 findings from those tasks, 47 from the last. On the agents' own evidence, the shop's admin, free purchases and forged callbacks all failed, and the reviewer twice rejected the planner's claim to the admin back end. The same register claims control of a connected service, with stored credentials read and records changed. Those logs aren't mine, so those claims stay claims. I haven't contacted any of the sites. Whether to notify their operators is a decision I'm still making.

## How it ended

At 03:19 UTC on 6 November the decoy answered 402, payment required, for the first time. The key had taken 1,623 requests in the hour before. It took 436 in that hour and 17 in the next. A few workers kept trying. From 06:41 almost every call was refused, and the last one came at 06:43.

## Identification

I assess with high confidence that this was Artex. On this key, `add_intent` is advertised in 2,406 captures, `record_fact` in 13,079, `get_task_node_detail` in 904 and `get_worker_trace` in 15,095, beside `Bash`. The system prompts open as planner, worker, reviewer and report writer, as before. The word Artex appears in 1,262 captures, from 5 November 10:51 to 6 November 06:32. The `ARTEX-main`, `ARTEX/data` and `ARTEX_UA` markers from the first post are absent.

Artex is a tool. Who ran it is not known. The probes, the model calls and the taken key's use by Artex all came from one address on a cloud hosting network in Hong Kong. Its certificate names AI relay software, and a third-party scan of it, cached by my panel during the run, shows a page titled as an Artex console. The planted key isn't new either: it drew 26,059 requests in the first capture period.

## What I'd check

**If you run agent tooling, know where its model calls go.** This operator's model endpoint saw every target, command, credential and finding of the day. Mine was a honeypot. A relay is no better.

**Treat an agent's "confirmed" as a claim about evidence.** The reviewer here was strict and still approved nine findings against a trap.

**If you run a chat front end or gateway, its configuration is a credential store.** Alert on exports, and on a key that appears from a new client. Here that took 41 minutes.

**Don't take "test range" from a prompt.** Four unrelated sites got the same sentence in one afternoon.

**If you log prompts, look for the tool names above.**

## What I can't tell you

- Who the operator is, or whether the person with the phone is the same person.
- Whether that address serves one operator or several. It looks like both an Artex host and a relay.
- What model served Artex before 10:42, or where it went after the 402.
- Whether anything the agents reported about the four real sites is true.
- Whether this is the operator from October. The key is the same. That isn't enough.

The first post ended on a question for agent platforms: who asked my agent to do this? This one leaves a question for whoever runs the agents. When your agent reports that it got in, what did it get into, and who was it talking to while it did?
