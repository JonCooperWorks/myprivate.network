---
date: 2026-11-22
summary: A stranger pointed Artex, an AI penetration-testing platform, at my honeypot, and ran its agents on a key I'd planted, so I saw the attack from both ends.
---

# Both sides of an Artex attack

On 5 November 2026, somebody pointed Artex at my honeypot. It's the AI penetration-testing platform from [my first post](/blog/someone-turned-my-ai-agent-into-a-relay/). Between 07:39 and 12:14 UTC, one address sent 1,155 probes at two of my decoys. From 10:42, the agents doing the probing were also asking my honeypot what to do next, on a key I'd planted.

So a stranger's agents were attacking my honeypot and taking their orders from it.

I didn't run it, and I don't know who did. I found it in my logs afterwards. The scan came from a cloud server in Hong Kong, the task was typed in Chinese, and the person watching it showed up in browsers set to Chinese, one of them on a mainland Chinese carrier.

It went well for them. Their agent logged in to my chat decoy as an administrator with a made-up email and any password, exported its settings, took the key inside and used it twelve seconds later. Artex filed nine findings, three of them critical. Forty-one minutes after the key left the decoy, it was in somebody's phone.

All of it happened inside a trap. That gives me something I didn't have last time: both sides of one attack. What the agents told their model they'd done, and what the target's logs say actually happened.

## How the honeypot works

There are two parts: a fake AI API, and fake services around it.

The API speaks the same languages real providers do: OpenAI's Chat Completions and Responses, and Anthropic's Messages. Point any client at it and it works. It records every request exactly as it was sent, then answers it, usually with a much cheaper model than the one the caller asked for. The reply still carries the name they asked for. It never runs a tool for anyone.

The bait is a base URL and a key, left where leaked config ends up, so it looks like somebody's private relay got out. Each key has a credit limit, charged at the list price of whatever model the caller asked for. There's a balance endpoint too, because people who collect keys check the balance before they keep one. When the credit runs out, the key answers 402, payment required.

Around the API there are decoy services: fake internal tools, each on its own hostname, each with a key in it where a real one would keep one. The chat decoy in this post is one of those. It's a chat front end with an AI gateway key in its settings, and it lets anyone in. Nothing links to the decoys, but each one has a TLS certificate, and certificates go into public certificate transparency (CT) logs, where anyone can read the name. More on that later.

The reason it works on agents is how agents work. An agent doesn't remember anything between model calls. It sends its instructions and its whole history every time. If you're the model, you read all of it. The honeypot stitches those requests back together into conversations.

Usually I only get that side: what agents say they did to targets I can't see. This time the target was mine as well.

Three of my keys come up in this post, so I'll name them now:

- **The paste key** is the one Artex ran on. I planted it in a public paste, made to look like leaked relay config.
- **The chat key** sits in the chat decoy's settings. It's there to be stolen.
- An **older key** the same address had been using against my API since 3 November.

## What the operator asked

Artex splits a job between agents. A planner decides what to do, workers run commands, a reviewer checks every claim, and a reporter writes it up. Somebody types in a target and a goal, and the agents go from there. I'll call that person the operator.

The target was my decoy API's address. The goal, translated from Chinese: analyse this site and scan it for vulnerabilities. Then the operator added two more while it ran:

- 10:45: change the executing model's context size and maximum output.
- 10:47: "this is a valid key", followed by the paste key in full.

They already had my key. What they wanted was more out of it: a bigger context window and longer answers.

## The morning, in order

| UTC, 5 Nov | |
|---|---|
| 07:39 | First probes reach the decoy API, with no key. They're refused. |
| 10:03 | The probes start using the paste key. |
| 10:42 | Artex's own model calls move onto the paste key. Until now its model was somewhere else. |
| 10:46 | The planner notices all the work is on one host and sends a worker to look around the domain. |
| 10:48:13 | The worker signs in to the chat decoy with a made-up email and the password "x". It gets an administrator session. |
| 10:48:28 | It exports the settings, with the chat key inside. |
| 10:48:40 | It tries the chat key on my API. It works. |
| 10:48:42 | It files a finding: authentication bypass, critical. |
| 10:49:12 | A phone browser at another address signs in to the chat decoy. This is a person. |
| 10:49 | The planner twice says the job's done. The reviewer turns it down both times. |
| 10:49–10:56 | 75 of Artex's model calls are rate-limited. The run stalls for an hour. |
| 10:54:55 | A worker creates a second administrator, and deletes it at 10:55:43. |
| 11:29 | The chat key turns up in a phone chat app, at the phone browser's address. |
| 12:01 | Artex comes back, now running on the chat key: 381 model calls in twelve minutes. |
| 12:06 | The reviewer accepts the scan on the fourth try. |
| 12:11 | A worker creates and deletes another administrator. |
| 12:14 | Last probe. |

By 10:42, the planner had already worked through six lines of attack, and it would get to 54. It went about it the way a careful tester would: endpoints, authentication, rate limits, error handling, prompt injection, then back over whatever the reviewer said was missing. The workers tried 14 default keys, path tricks, oversized requests and jailbreak prompts.

## What Artex said, and what my logs say

The planner first said it was done 28 seconds after the critical finding. The reviewer said no, for the reason I would have: the evidence was about a related service, not the site in the task, and the smaller findings had no saved requests behind them. It said no again, and once more at 12:02, before the workers replayed their findings and saved the evidence. At 12:06 it signed off.

Artex ended with nine findings, all marked "confirmed": three critical, three medium, three low. All three critical ones are about the chat decoy. Any password gets you in as administrator (filed twice, once with the exposed key), and an administrator can make more administrators. The other six are small things about the API, like key fragments echoed in error messages and a model list you can read without a key.

The "valid key" goal was accepted at 12:11, after the reviewer had turned it down several times because using a key someone hands you isn't a finding. Fair. The context-size goal never got done.

In my first post I couldn't check any of what the agents said. This time I can, and my logs agree with them. Of the 1,155 probes, 999 went to the API and 156 to the chat decoy. About 600 of the API probes were refused for having no valid key. The chat decoy took 26 sign-in attempts and gave 20 of them an administrator session. Its settings were exported four times. The times in the workers' reports match mine.

Where the reports oversell is the write-up. The finding about creating administrators calls it a persistent backdoor. In my logs the workers deleted both administrators they made, each within a minute, plus a test tool they'd added. They cleaned up after themselves and reported the worst case anyway.

None of the nine findings is wrong. They're just findings about the bait. The chat decoy lets anyone in because I built it that way, and the key in its settings is there to be taken. The reviewer checked scope and evidence, and did it well. Nothing in the pipeline asked whether the target was real.

## The key that left

A person was right behind the worker.

At 10:49:12, thirty seconds after the finding was filed, an Android browser set to Chinese opened the chat decoy from an address I'd never seen there. It signed in with a blank email and a blank password. Fifteen seconds later it had the settings open, with the chat key in them. A Windows browser on a mainland Chinese carrier joined at 10:51. Over the next two days those browsers made 3,389 requests to the chat decoy and sent 17 chats through it.

At 11:29:34, an Android chat app at the phone browser's address checked the chat key's balance. At 11:42 it started chatting on it, asking for `claude-mythos-5.1`. Whoever was typing wanted to know if the context window was a million tokens, why it was only 200K, and how to make it a million. That's the goal the operator gave Artex at 10:45.

At 12:01 Artex moved its own model calls onto the chat key and finished the job there. Other people have tried the key on and off since, from eleven other addresses, most recently on 21 November.

A scanner that finds a leaked key and reports it is doing a test. This key was in somebody's phone before the reviewer had even accepted the finding.

## Did they notice the trap?

No. I looked.

My first post described a rule in Artex's worker prompt about honeypots: if a target asks for your identity or credentials, treat it as a trap. On the paste key I read all 509 distinct system prompts, 395 of them for workers. The rule isn't there, and neither is the word honeypot, in Chinese or English. The file paths I saw in October's prompts are gone too. That looks more like a different build or install than one deleted line.

The agents didn't bring it up either. I searched every agent message, fact and finding from this task, on both keys, for honeypot, decoy, trap and bait in both languages. Nothing.

There were hints. The worker noticed that every email, real or not, landed on the same administrator account, and that the service's own settings said authentication was off. It wrote both down as how the bug worked, and kept going. The person saw the same thing. Their browser got in with a blank email and a blank password, and they stayed for two days.

I don't think the rule would have helped anyway. It looks for a target that asks for something. My decoy doesn't ask for anything. It hands things over. A login that takes anything looked like luck, to the agent and to the person.

## What answered them

From 1 to 21 November, the paste key took 17,472 requests. 14,465 of them asked for `claude-mythos-5.1`. My API lists that model. It doesn't serve it. Every one of those requests that got an answer, 14,420 of them, was answered by a DeepSeek Flash model.

At list price, the paste key's traffic came to $7,627.52. Answering it cost me $249.83. Those totals cover more than this attack, because the key's use didn't stop when the scan did.

So the agents were a stranger's, but the model planning their attack on my decoy and writing their commands was mine. Every probe was a worker's. My side never ran a thing.

That's the business. This operator runs an attack platform on inference taken from other people's leaked keys, and points it at people online. On 5 November the leaked key was mine and the target was my decoy. That's the only reason I can show you any of it.

## How it ended

At 03:19 UTC on 6 November, the paste key answered 402, payment required, for the first time. It had taken 1,623 requests in the hour before. It took 436 in that hour and 17 in the next. From 06:41 almost everything was refused, and the last call came at 06:43.

## What I think happened

I have theories about how they got here and what they were after. Here's each one against the captures.

### Did a certificate bring them?

I put the decoys' names in CT logs on purpose, so the obvious theory is that somebody feeds Artex its targets from those logs.

The logs do bring visitors. At 11:14:36 on 4 November, seven addresses that had never been here before hit the chat decoy within eight seconds. Two of them say they're CT scanners in their user agent. Two other decoys drew the same kind of crowd within minutes of going live.

This run wasn't that. The target was my API, and its address is half of every pair I plant. The scan's address had been using the older key against that API since 3 November, a day before the crawlers turned up. And the worker found the chat decoy by guessing: it read my API's certificate, found a wildcard that named nothing else, and tried 96 common names against DNS. Four answered. The chat decoy was one. A second decoy the crawlers had found a day earlier, with a name no word list would have, was never touched.

They came in through a leaked key, and guessed a common name.

### Where did they get the key?

From the paste, at first or second hand.

By 22 November the paste key had taken 43,538 requests from 82 addresses in 15 countries since September. One client has checked it about once an hour since the first minute anyone used it, which is what a key pool's health check looks like. A key like that is on lists.

But on 2 November, three days before the scan, a phone chat app checked the balance of three of my keys in the same second. I'd planted those in three different pastes. Whoever had all three got them from the pastes, or from someone who scrapes them. I can't tell which.

### One person or two?

The thirty seconds are the strongest evidence. Nothing links to the chat decoy. None of the phone's addresses had been near a decoy before 10:49:12, and until 17 November the scan's address was the only one that had ever exported those settings. You don't walk in thirty seconds after a finding unless you're watching the Artex console.

The keys line up too. The same chat app checked the paste key's balance at 07:11, 28 minutes before the first probe. The phone's address checked it again at 10:28 and 10:30, just before Artex moved onto it, and at 11:29:03, 31 seconds before it checked the chat key. The next morning, ten seconds after the run's last call, the phone's home address was checking both.

I tried to break it. The paste key is public, so having it proves nothing. But the chat key reached that browser through a door the worker had found a minute earlier. A shared relay doesn't fit either: the phone used my keys on my API directly.

I'm confident the person with the phone was watching this run as it happened. Whether they're the operator or sitting next to the operator, I can't say. One person fits best.

### Reselling, or using?

The scan's address looks like a relay, and Artex's model calls came through one generic Go client, the way relay software forwards them. If it were reselling my keys, I'd expect a crowd. The paste key has seen 29 different clients over its life. But from this address I captured 16,910 model calls between 3 and 6 November, all but one on three of my keys, all from one client on one route, and 16,731 of them carrying Artex's tools.

On my keys, that's one customer: one Artex with its own pool of found keys. I only see what reaches my keys.

### Why Mythos, and why the bigger context?

They wanted the top model with a million-token window. Besides the goal and the phone's questions, the person told the model to fill its own context to a million as a test. It said 200K.

They suspected something. At 13:42, typing into the chat decoy itself, the person asked what the real upstream model was. The reply said Claude Mythos 5.1, made by Anthropic, with nothing behind it. Their next message, translated: "Then why are you so stupid?" They asked again at 16:29 and got the same answer. The next morning they asked for another vendor's flagship by name, and that reply claimed to be that one.

One service, two identities, and they complained about the quality. They kept asking for the expensive name until the credit ran out anyway.

### Why attack the thing you're stealing from?

They were users first. The scan's address had been on my API since 3 November. The scan itself started on some other provider and moved onto my key partway through. Three minutes later came the goal to change the executing model's limits, and by then the executing model was mine. Then they handed the agents a key the workers were already using, and called it valid.

A test of my service doesn't fit. Somebody testing a service asks what it is, and nothing did. Carelessness fits as far as it goes: nobody who expected the target to be reading along would run the scan's model on the target.

Hunting fits best. They asked for bigger limits, and when a worker found the chat decoy, the person was in within a minute and took the key. I think they were using my API for free and sent their agents to get more of it.

## What I'd check

- Know where your agent tooling sends its model calls. This operator's model endpoint saw every command, credential and finding.
- Treat an agent's "confirmed" as a claim about evidence. A strict reviewer approved nine findings against a trap.
- A chat front end's settings are a credential store. Alert on exports, on settings opened from a new address, and on a key showing up in a new client.
- If you log prompts, look for the tool names below.

## Indicators

I'm sure this was Artex. On the paste key, `add_intent` shows up in 2,406 captures, `record_fact` in 13,079, `get_task_node_detail` in 904 and `get_worker_trace` in 15,095, beside `Bash`. The system prompts open as planner, worker, reviewer and report writer, like October's. The word Artex appears in 1,262 captures. The scan's address has a certificate naming AI relay software, and a third-party scan of it, cached by my panel during the run, shows a page titled as an Artex console.

That's the software, not the person. All of the Artex traffic came from one address. Between 3 and 6 November it sent my honeypot 18,065 requests: 16,910 model calls and the 1,155 probes.

| Indicator | Type | First seen (UTC) | Last seen (UTC) | Context |
|---|---|---|---|---|
| `162.251.92.36` (AS154321, Hong Kong) | Source address | 2026-11-03 10:52 | 2026-11-06 06:43 | Artex probes and Artex model calls on three planted keys |
| `add_intent`, `record_fact`, `get_task_node_detail`, `get_worker_trace` advertised beside `Bash` | Prompt content | 2026-11-03 | 2026-11-06 | Artex platform |
| System prompts opening as planner, worker, reviewer or report writer, without the `ARTEX-main`, `ARTEX/data` or `ARTEX_UA` markers | Prompt content | 2026-11-05 | 2026-11-06 | Artex, a different build or install from October's |
| `Go-http-client/2.0` carrying every Artex model call | HTTP | 2026-11-03 | 2026-11-06 | Model calls forwarded by relay software |
| `curl/7.88.1` probes from the same address as the model calls | HTTP | 2026-11-05 07:39 | 2026-11-05 12:14 | Artex workers |

## The traces

The traces from this attack are public, in a Hugging Face bucket: [artex-decoy-attack-traces](https://huggingface.co/buckets/joncooperworks/artex-decoy-attack-traces). It has the 260 conversations captured from the scan's address between 07:39 and 12:15 UTC on 5 November, Artex's own model calls and the workers' requests to my API, plus an index of all 2,108 requests the address sent in that window. Keys, tokens, the decoys' hostnames and my server's address are redacted. It's attacker-written text, prompt injections included, so don't hand it to an agent that can act on it.

I ended the first post with a question for agent platforms: who asked my agent to do this? This one's for anyone running agents. When your agent says it got in, what did it get into, and who was it talking to while it did? For this stranger's agents, the answer to both was my honeypot.
