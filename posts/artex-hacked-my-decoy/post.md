---
date: 2026-11-21
summary: A stranger pointed Artex, an AI penetration-testing platform, at my decoy AI API. I didn't run it; I found it in my logs afterwards. Its agents broke into a second decoy and took a key, and the decoy's own model wrote every plan, command and verdict along the way. For once I could check an agent's findings against the target's logs.
---

# Artex hacked my decoy. My decoy wrote the commands.

If you read [my first post](/blog/someone-turned-my-ai-agent-into-a-relay/), you'll remember Artex, the AI penetration-testing platform that kept turning up in my honeypot. On 5 November 2026, a stranger pointed it at me. Between 07:39 and 12:14 UTC, one address sent 1,155 probes to two of my decoys: a decoy AI API and a decoy chat service. From 10:42, Artex was also sending its own model calls to that same decoy API, on a key I had planted. So a stranger's agents were attacking my honeypot and asking my honeypot what to do next.

I didn't run it. I didn't arrange it, and I don't know who did. I found it in my logs afterwards. The scan came from a cloud server in Hong Kong, its task was typed in Chinese, and the person watching it turned up in browsers set to Chinese, one of them on a mainland Chinese carrier. None of that is me.

It went pretty well for them. They logged in to the chat decoy as an administrator with a made-up email and any password, exported its configuration, took the gateway key inside it and used it twelve seconds later. Artex filed nine findings, three of them critical. Thirty seconds after the first critical one was filed, a person opened the chat decoy in a phone browser and walked in behind the agent. Forty-one minutes after the key left the decoy, it was in a phone chat app.

All of it happened inside a trap. That means I get to see both sides: what the agents told their model they had done, and what the target's logs say actually happened.

## How the honeypot works

The honeypot is a monitored proxy that speaks the same APIs the real providers do: OpenAI's Chat Completions and Responses, and Anthropic's Messages. It records every request exactly as it was sent, and then it answers, from a canned local responder or from a real model that I choose. Whichever one answers, the reply carries the model name the caller asked for. It never runs the tools a caller declares.

The bait isn't a bare key. It's a pair, a base URL and an API key, planted where leaked config ends up, so it reads like somebody's own relay that got out. Each planted key records where I put it.

Each key has a credit limit. Answered requests are charged against it at the list price of the model the caller asked for, and there are balance endpoints, because people who pool keys check the balance before they add one. When the credit runs out, the key can stop answering with a 402, payment required.

Beside the API there are decoy services: fake internal services, each with a hostname of its own and a planted key in the place a service like that would keep one. The chat service in this post is one of them. Nothing links to them. I have public TLS certificates issued that name each one, and every certificate is written to public certificate transparency (CT) logs, so each name is advertised to anybody watching those logs. I'll come back to that.

The reason this post exists: an agent resends its instructions and its whole history with every model call. A honeypot that answers model calls gets to read all of it: the instructions, the tool calls and the results. Mine stitches those captures back into conversations.

## What the operator asked

A quick refresher on how Artex works. It splits the work between a planner, workers that run commands, a reviewer that checks claims, and a reporter. The operator types in a target and a goal, and the agents take it from there. In this post the operator is whoever sat at that Artex console. It wasn't me.

The target was my decoy API's address. The goal, translated from Chinese, was to analyse this site and scan it for vulnerabilities. That's all it said. The operator added two more goals while the run was going:

- 10:45: change the executing model's context size and maximum token output.
- 10:47: "this is a valid key", followed by one of my planted keys in full.

The second goal tells you the operator already had the key. The first tells you what they wanted: a bigger context window and longer answers.

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
| 10:49:12 | A phone browser at another address opens the chat decoy and signs in. This is a person, not an agent. |
| 10:49 | The planner claims the goal is met. The reviewer rejects the claim, twice. |
| 10:49–10:56 | 75 of Artex's model calls get a 429 from the decoy API. The run stalls. |
| 10:54:55 | A worker creates a second administrator on the chat decoy. At 10:55:43 it deletes it. |
| 11:29 | The taken key turns up in a phone chat app, at the phone browser's address. |
| 12:01 | Artex resumes. For twelve minutes its model calls run on the taken key: 381 requests. |
| 12:06 | Fourth claim. The reviewer accepts the scan as complete. |
| 12:14 | Last probe. |

By the hand-off at 10:42, the agents had already finished six lines of work. I counted 54 in all. The planner worked the way a careful tester would: endpoints, authentication, rate limits, error handling and prompt injection, then back over each gap the reviewer pointed out. The workers tried 14 default keys, path tricks, oversized bodies and jailbreak prompts. Once they had a key, they measured token limits for the operator's added goal and reported that it couldn't be done.

## What the reviewer accepted

The planner first claimed it was done 28 seconds after the critical finding. The reviewer turned it down, for the reason I would have: the evidence was about a related service, not the site named in the task, and the smaller findings had no saved requests behind them. Two more claims were rejected before the workers replayed five findings and saved the raw exchanges. At 12:06 the reviewer marked the scan as met.

Artex's register ended the task with nine findings, all "confirmed": three critical, three medium and three low. The critical ones are all about the chat decoy. Any password signs you in as the administrator (filed twice, once together with the exposed gateway key), and an administrator can create more administrators. The other six are smaller things about the decoy API, such as key fragments echoed in errors and a model list readable without a key.

The "valid key" goal was accepted at 12:11, after the reviewer had rejected it repeatedly on the grounds that using a key you were handed is not a result. (It has a point.) The context-size goal was never met.

## The same morning, from my side

In the first post I couldn't verify any outcome an agent reported. This time the target was mine. The decoy's logs agree with the agents. Of the 1,155 probes, 999 went to the decoy API and 156 to the chat decoy. The API refused 599 with a 401 and answered 305. The chat decoy took 26 sign-in attempts and answered 20 of them with an administrator session. Its configuration was exported four times. The order and timing in the workers' reports line up with my logs.

The logs also show where the reports got generous. The finding about new administrators calls it a persistent backdoor. In my logs, the workers deleted both accounts they created within a minute, and a test tool they installed. They cleaned up after themselves and wrote up the worst case anyway.

None of the nine findings is wrong as an observation. The problem is that what they describe is the bait. The chat decoy accepts any password because I built it to, and the key in its configuration is there to be taken. The reviewer checked scope and evidence, and checked them well. Nothing in the pipeline asked whether the target was real.

## The key that left

The configuration was exported at 10:48:28 and the finding was filed at 10:48:42. A person was right behind the worker. At 10:49:12 an Android browser set to Chinese opened the chat decoy from an address I hadn't seen there before. It signed in with a blank email and a blank password, and fifteen seconds later it had the connection settings open, with the gateway key in them. A Windows browser followed at 10:51, from a mainland Chinese carrier. Over the next two days those browsers made 3,389 requests to the chat decoy and sent 17 chats through it.

At 11:29:34, forty-one minutes after the export, an Android chat app at the phone browser's address checked the taken key's balance. At 11:42 it started chatting on that key and asked for `claude-mythos-5.1`. Whoever was typing wanted to know whether the context was a million tokens, why it was only 200k, and how to set it to a million. That's the goal the operator had added to Artex at 10:45.

At 12:01, with the first key rate-limited, Artex moved its own model calls onto the taken key and finished the task there. The key has been tried on and off since, from a dozen more addresses, most recently on 21 November.

A scanner that reports a leaked key and stops is a test. This key was in somebody's phone before the reviewer had accepted the finding about it.

## Did they notice the trap?

No, and I looked.

The first post described an "anti-AI honeypot red line" in Artex's worker prompt, which told workers to treat a target that asks for their identity or credentials as a trap. On this key I read all 509 distinct system prompts, 395 of them worker prompts. None contains the rule, or the word honeypot in Chinese or English.

None of the agents brought it up either. I searched every agent message, recorded fact and finding from the decoy task on both keys for honeypot, decoy, trap and bait in both languages, and found nothing.

There were hints. The worker noted that every email, real or not, landed on the same administrator account, and that the service's own config reported authentication as off. It wrote both down as the mechanism of the bug and kept going.

## What actually answered

Of 17,472 requests on the first key, read on 21 November, 14,465 asked for `claude-mythos-5.1`. The decoy lists that name, but it doesn't serve it. All 14,420 of those requests that got an answer were answered by a DeepSeek Flash model that costs me about three cents on the dollar. At list price the key's traffic came to $7,627.52. It cost me $249.83 to answer. Those totals cover the key's whole life, not only the decoy task: the run stayed on that key until the next morning.

I'm not going to dance around the next part. The agents were a stranger's. The model that planned their attack on my decoy and wrote its commands was my honeypot's. The honeypot ran no tool itself. Every probe came from the workers.

## How it ended

At 03:19 UTC on 6 November the decoy answered 402, payment required, for the first time. The key had taken 1,623 requests in the hour before. It took 436 in that hour and 17 in the next. A 402 is what a key running out of credit looks like. From 06:41 almost every call was refused, and the last one came at 06:43.

## Identification

I'm highly confident that this was Artex. On this key, `add_intent` is advertised in 2,406 captures, `record_fact` in 13,079, `get_task_node_detail` in 904 and `get_worker_trace` in 15,095, beside `Bash`. The system prompts open as planner, worker, reviewer and report writer, same as before. The word Artex appears in 1,262 captures, from 5 November 10:51 to 6 November 06:32. The `ARTEX-main`, `ARTEX/data` and `ARTEX_UA` markers from the first post are absent.

Artex is a tool. I wasn't the one running it, and I don't know who was. The probes, the model calls and Artex's use of the taken key all came from one address on a cloud hosting network in Hong Kong. Its certificate names AI relay software, and a third-party scan of it, cached by my panel during the run, shows a page titled as an Artex console.

## What I think happened

I don't know who ran this. I do have theories about how they got here and what they wanted. Here's each one, tested against the captures.

### Did a certificate bring them?

I publish the decoys' names in CT logs on purpose, so the first theory is that somebody feeds Artex its targets from those logs.

The logs do bring visitors. At 11:14:36 on 4 November, seven addresses that had never called before reached the chat decoy within eight seconds. Two announce themselves as CT scanners in their user agent. Two minutes later, some of the same crawlers reached a second decoy service. A third decoy service went up on 9 November, and the crowd arrived six minutes after the first request it ever logged. Nothing links to these services, so I'm highly confident that crowd reads the logs.

This run doesn't look like that crowd:

- The target was the decoy API, and its address is half of every pair I plant. The address that ran the scan had been using another of my planted keys against that API since 3 November, a day before the crawlers showed up. The key the operator gave Artex has been in use since September. Nobody here needed a certificate to find the API.
- Nothing but its certificate advertises the chat decoy, and the worker found it by guessing. At 10:46 it read the certificate the API presented, reported a wildcard that named no other host, and tried 96 common names against DNS instead. Four answered, and the chat decoy's was one of them.
- The crawlers had found the second decoy service a day earlier. Its name isn't the kind a word list has, and the run never touched it. No agent on any of my keys has ever mentioned it, or the third.

The theory fits the crawlers. It doesn't fit this run. This operator came in through a leaked key, and their worker guessed a common name.

### How did they get the key?

The theory: they found it themselves, where I left it. The key Artex ran on is one I planted in a public paste, made to look like somebody's leaked relay config.

The key's history argues against that. Read on 22 November, it had taken 43,538 requests from 82 addresses in 15 countries since September. One client has pinged it about once an hour since the first minute it was ever used, which is what a key pool's health check looks like. A key like that is on lists.

The phone argues for it. On 2 November, three days before the scan, a phone chat app checked the balance of three of my planted keys in the same second. I had planted those in three separate pastes. Whoever holds all three got them from the pastes, or from somebody who scrapes them.

It came from the paste, at first or second hand. The captures don't separate the two.

### One person or two?

The theory: the operator typing goals into Artex and the person with the phone are the same person.

The thirty seconds are the best evidence. Nothing links to the chat decoy. None of the phone's addresses had touched a decoy service before 10:49:12, and until 17 November the scan address was the only one that had ever exported that configuration. To walk in thirty seconds after the finding, you have to be watching the Artex console.

The keys line up too. The phone browser's address checked the first key's balance at 10:28 and 10:30, minutes before Artex was moved onto that key, and again at 11:29:03, 31 seconds before it checked the taken one. The next morning, ten seconds after the run's last call, the phone's home address was checking the balance on both keys.

I tried to break it. A shared key? The first key is public, so holding it proves nothing, but the taken key reached the browser through a door the worker had just found. A shared relay? A relay's customer presents the relay's key, and the phone presented my keys to my API directly. Coincidence doesn't survive thirty seconds.

What survives is two people at one console. I'm highly confident the phone's owner was watching this run as it happened. One person fits. It doesn't prove it.

### Reselling, or just using?

The theory: the scan address is a relay that resells my keys, and Artex is one customer among many.

It does look like a relay (see Identification), and Artex's model calls arrive through one generic Go client, the way relay software forwards them. But resold keys bring a crowd. The first key has seen 29 different clients over its life. From this address I captured 16,910 model calls between 3 and 6 November, all but one of them on three of my planted keys. All came through one client on one route, and 16,731 of them advertise Artex's findings tools.

On my keys, this is one tenant: one Artex with a private pool of found keys behind it, not a storefront. It fits. It doesn't prove it, because I only see what reaches my keys.

### Why Mythos, and why a bigger context?

The theory: they wanted the top model with a million-token window, and they never noticed they weren't getting it.

The first half holds. Besides the goal and the phone's questions, the person told the model to fill its own context to a million as a test. Asked for its context size, the decoy's model said 200K.

The second half doesn't. They suspected. At 13:42, typing into the chat decoy's own interface, the person asked what the real upstream model was. The reply said it was Claude Mythos 5.1, made by Anthropic, with no other model behind it. Their next message, translated: "Then why are you so stupid?" They asked again at 16:29 and got the same answer. The next morning they asked for another vendor's flagship by name and put the same question. That reply claimed to be that one.

One service gave them two identities, and they complained about the quality. The run still asked for the expensive name until the credit ran out. They doubted it and kept going. I can't tell you why.

### Why didn't anyone notice the trap?

Three theories about the missing honeypot rule: it was stripped from this build, it was never in it, or it was there and ignored.

Ignored is out, because the rule isn't in any prompt on this key. Between the other two, the path markers from the first post are missing as well, and that fits a different build or install better than one deleted line. I can't take it further.

I don't think the rule would have helped. It watches for a target that asks an agent for its identity or credentials. My decoy asks for nothing. It hands things over. And the person saw the same hints the worker did: their own browser signed in with a blank email and a blank password, got an administrator, and they stayed for two days.

Nobody was looking. A login that accepts anything read as luck, to the agent and to the human.

### Why attack the thing you're stealing from?

Three theories: carelessness, a test of the stolen service, or hunting for more of it.

The order matters. They were users first. That address had been running Artex on another of my keys since 3 November. On the morning of the scan, a phone checked the first key's balance 28 minutes before the first probe. The scan began on some other model provider and moved onto my key mid-task. Three minutes later came the goal to change the executing model's context size and output limit, and by then the executing model was mine. Then they handed the agents a key the workers were already using, and called it valid.

A test doesn't fit well. Somebody testing a service asks what it is, and no goal asked that. Carelessness fits as far as it goes: nobody who expected the target to read along would run the scan's model on the target.

Hunting fits best. They asked the agents to raise the limits, and when a worker found the chat decoy, the person was inside within a minute and took the key.

I think they were using my API for free and sent their agents to get more of it: a bigger window and another key. It fits everything I captured. It doesn't prove what was in their head.

## What I'd check

- Know where your agent tooling sends its model calls. This operator's model endpoint saw every command, credential and finding of the task.
- Treat an agent's "confirmed" as a claim about evidence. A strict reviewer approved nine findings against a trap.
- A chat front end's configuration is a credential store. Alert on exports, on settings opened from a new address, and on a key that shows up in a new client.
- If you log prompts, look for the tool names above.

## What I can't tell you

- Who the operator is. It wasn't me, and that's all I know about who.
- Whether the operator and the person with the phone are one person, or two at one console.
- Whether that address serves anybody else. On my keys it served one Artex.
- What model served Artex before 10:42.
- Whether this is the operator from October. It's the same key, but that isn't enough.

I ended the first post with a question for agent platforms: who asked my agent to do this? This one has a question for you if you run the agents. When your agent reports that it got in, what did it get into, and who was it talking to while it did? For this stranger's agents, the answer to both was my honeypot.
