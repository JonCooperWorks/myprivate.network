---
date: 2026-11-21
summary: Someone pointed Artex, an AI penetration-testing platform, at my decoy AI API. Its agents broke into a second decoy and took a key, and the decoy's own model wrote every plan, command and verdict along the way. For once I could check an agent's findings against the target's logs.
---

# Artex hacked my decoy. My decoy wrote the commands.

If you read [my first post](/blog/someone-turned-my-ai-agent-into-a-relay/), you'll remember Artex, the AI penetration-testing platform that kept turning up in my honeypot. On 5 November 2026, somebody pointed it at me. Between 07:39 and 12:14 UTC, one address sent 1,155 probes to two of my decoys: a decoy AI API and a decoy chat service. From 10:42, Artex was also sending its own model calls to that same decoy API, on a key I had planted. So the agents attacking my honeypot were asking my honeypot what to do next.

It went pretty well for them. They logged in to the chat decoy as an administrator with a made-up email and any password, exported its configuration, took the gateway key inside it and used it twelve seconds later. Artex filed nine findings, three of them critical. Forty-one minutes after the key left the decoy, somebody was using it from a phone.

All of it happened inside a trap. That means I get to see both sides: what the agents told their model they had done, and what the target's logs say actually happened. I'm going to walk you through both.

## What the operator asked

A quick refresher on how Artex works. It splits the work between a planner, workers that run commands, a reviewer that checks claims, and a reporter. The operator types in a target and a goal, and the agents take it from there. Each agent resends its instructions and its whole history with every model call. That's very convenient if you happen to be a honeypot that answers model calls, because you get to read all of it.

The target was my decoy API's address. The goal, translated from Chinese, was to analyse this site and scan it for vulnerabilities. That's all it said. The operator added two more goals while the run was going:

- 10:45: change the executing model's context size and maximum token output.
- 10:47: "this is a valid key", followed by one of my planted keys in full.

The second goal tells you the operator already had the key. The first tells you what they wanted from the service: a bigger context window and longer answers.

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
| 12:14 | Last probe. |

By the hand-off at 10:42, the agents had already finished six lines of work. I counted 54 in all. I'll give the planner credit, because it worked the way a careful tester would. It started with endpoint enumeration, then authentication, rate limits, error handling and prompt injection, and then it went back over each gap the reviewer pointed out. The workers tried 14 default keys, path tricks, oversized bodies and jailbreak prompts asking the decoy's model to reveal its system prompt. Once they had a key, they measured token limits for the operator's added goal and reported that it couldn't be done.

## What the reviewer accepted

The planner first claimed it was done 28 seconds after the critical finding. The reviewer turned it down, and for the same reason I would have: the evidence was about a related service, not the site named in the task, and the smaller findings had no saved requests behind them. A second claim was rejected eighteen seconds later, and a third at 12:02. The workers then replayed five findings and saved the raw exchanges. At 12:06 the reviewer marked the scan as met.

Artex's register ended the task with nine findings, all "confirmed": three critical, three medium and three low. The three critical ones are all about the chat decoy. Any password signs you in as the administrator (they filed that one twice, once together with the exposed gateway key), and an administrator can create more administrators. The rest are about the decoy API: no rate limit before authentication, key fragments echoed in errors, a model list you can read without a key, account metadata you can read with one, missing security headers, and large token values that produce a 503.

The "valid key" goal was accepted at 12:11, after the reviewer had rejected it repeatedly on the grounds that using a key you were handed is not a result. (It has a point.) The context-size goal was never met. The planner recorded it as not achievable.

## The same morning, from my side

In the first post I told you I couldn't verify any outcome an agent reported. This time the target was mine, so I can.

The decoy's logs agree with the agents. Of the 1,155 probes, 999 went to the decoy API and 156 to the chat decoy. The API refused 599 with a 401 and answered 305. The chat decoy took 26 sign-in attempts and answered 20 of them with an administrator session. Its configuration was exported four times. The order and timing in the workers' reports line up with my logs.

The logs also show you where the reports got generous. The finding about new administrators calls it a persistent backdoor. In my logs, the workers deleted each of the two accounts they created within a minute, and a test tool they installed as well. So they cleaned up after themselves and then wrote up the worst case anyway.

None of the nine findings is wrong as an observation. The problem is that what they describe is the bait. The chat decoy accepts any password because I built it to, and the key in its configuration is there to be taken. The reviewer checked scope and evidence, and it checked them well. Nothing in the pipeline ever asked whether the target was real.

## The key that left

The configuration was exported at 10:48:28. At 11:29:34, forty-one minutes later, an Android chat app at a different address presented that key and asked for `claude-mythos-5.1`. Whoever was typing wanted to know whether the context was a million tokens, why it was only 200k, and how to set it to a million. That's the same goal the operator had added to Artex at 10:45. It looks a lot like one person, but I can't prove that it is.

At 12:01, with the first key rate-limited, Artex moved its own model calls onto the taken key and finished the task there. People have kept trying the key on and off since then, from a dozen more addresses, most recently on the day I wrote this.

If a scanner reports a leaked key and stops there, that's a test. This key was in somebody's phone before the reviewer had even accepted the finding about it.

## Did they notice the trap?

No, and I looked.

The first post described an "anti-AI honeypot red line" in Artex's worker prompt, which told workers to treat a target that asks for their identity or credentials as a trap. On this key I read all 509 distinct system prompts, 395 of them worker prompts. None of them contains the rule, or the word honeypot in Chinese or English. Their red lines are about staying on the assigned task and inside the authorised scope. I can't tell you whether the rule was removed or this is a different build.

None of the agents brought it up either. I searched every agent message, recorded fact and finding from the decoy task on both keys for honeypot, decoy, trap and bait in both languages, and found nothing. Across the whole run, not one reply on either key contains the word.

It's not as if there were no hints. The worker noted that every email, real or not, landed on the same administrator account, and that the service's own config reported authentication as off. It wrote both of those down as the mechanism of the bug and kept going.

## What actually answered

Of 17,472 requests on the first key, read on 21 November, 14,465 asked for `claude-mythos-5.1`. The decoy lists that name, but it doesn't serve it. All 14,420 of those requests that got an answer were answered by a DeepSeek Flash model that costs me about three cents on the dollar. At list price the key's traffic came to $7,627.52. It cost me $249.83 to answer. Those totals cover the key's whole life, not only the decoy task: the run stayed on that key until the next morning.

During the decoy task itself, Artex mostly asked for the cheap model by its real name. It switched to the expensive name at 12:01, after a worker had listed the decoy's models and the phone had tried it.

I'm not going to dance around the next part. The model that planned the attack on my decoy and wrote its commands was my honeypot's. For two hours my decoy was helping to attack my decoy. The honeypot ran no tool itself. Every probe came from the workers.

## How it ended

At 03:19 UTC on 6 November the decoy answered 402, payment required, for the first time. The key had taken 1,623 requests in the hour before. It took 436 in that hour and 17 in the next. A few workers kept trying anyway. From 06:41 almost every call was refused, and the last one came at 06:43.

## Identification

I'm highly confident that this was Artex. On this key, `add_intent` is advertised in 2,406 captures, `record_fact` in 13,079, `get_task_node_detail` in 904 and `get_worker_trace` in 15,095, beside `Bash`. The system prompts open as planner, worker, reviewer and report writer, same as before. The word Artex appears in 1,262 captures, from 5 November 10:51 to 6 November 06:32. The `ARTEX-main`, `ARTEX/data` and `ARTEX_UA` markers from the first post are absent.

Artex is a tool, and I don't know who was running it. The probes, the model calls and Artex's use of the taken key all came from one address on a cloud hosting network in Hong Kong. Its certificate names AI relay software, and a third-party scan of it, cached by my panel during the run, shows a page titled as an Artex console. The planted key isn't new either: it drew 26,059 requests in the first capture period.

## What I'd check

**If you run agent tooling, know where its model calls go.** This operator's model endpoint saw every command, credential and finding of the task. Mine happened to be a honeypot. A relay is no better.

**Treat an agent's "confirmed" as a claim about evidence.** The reviewer here was strict, and it still approved nine findings against a trap.

**If you run a chat front end or gateway, its configuration is a credential store.** Alert on exports, and on a key that shows up from a new client. Here that took 41 minutes.

**If you log prompts, look for the tool names above.**

## What I can't tell you

- Who the operator is, or whether the person with the phone is the same person.
- Whether that address serves one operator or several. It looks like both an Artex host and a relay.
- What model served Artex before 10:42.
- Whether this is the operator from October. It's the same key, but that isn't enough.

I ended the first post with a question for agent platforms: who asked my agent to do this? This one has a question for you if you run the agents. When your agent reports that it got in, what did it get into, and who was it talking to while it did? This time, the answer to both was me.
