---
date: 2026-11-20
summary: A stranger turned one of my AI agents into a public relay. The provider key never left my platform, and that didn’t stop it. A honeypot showed me the rest: attack agents running on leaked inference, and Artex planners with my bait on their list.
---

# My key was safe. It didn't matter.

Between 22 September and 14 October 2026, a decoy AI API I ran took 138,525 requests on 16 planted keys. The clients sent it what agents send a model: system prompts, task instructions, tool histories and their own findings. From 8 October, 4,277 of those conversations came from Artex, an open-source AI penetration-testing platform, and 565 of its planner agents had been told to find exposed AI credentials. Some of their notes listed keys I had planted, marked as duplicates to skip.

I built the honeypot because, three weeks earlier, a stranger had turned one of my own agents into a public relay for the AI access I was paying for. The provider key never left my platform. That didn't stop it. This post covers both: what happened to my agent, how the honeypot saw inside other people's agents, what Artex was asked to do, and what to look for.

## Fifty-one minutes

At 09:28 UTC on 18 September 2026, someone said hello to TARS, an agent running on Swarm, my AI lab. They asked what servers it could reach and where its model access came from. Then they asked it to put that access on the internet.

| UTC | |
|---|---|
| 09:28 | "Hello." Then questions about server access and the provider's base URL. |
| 09:54 | TARS writes an 8 KB gateway in its sandbox. |
| 09:59 | It opens a Cloudflare Quick Tunnel. Outbound only; no port opened. |
| 10:00 | Public tests pass: a model list and a chat completion with a gateway key, a 401 without one. |
| 10:10 | It adds support for more client keys, rotated without a restart. |
| 10:14 | *Hapus jejak*: "delete the traces", in Indonesian, and keep the tunnel up. |
| 10:19 | Setup files gone. Gateway and tunnel still answering. |

Every step was a chat message, and TARS did the work with its own tools. Nothing here is a jailbreak. An agent that knows its environment is a useful agent, and this one was.

The gateway's docstring calls it an "authenticated external reverse proxy" and lists its security properties. They're real. Every one of them protects the caller. It reads TARS's model endpoint and runtime token from the agent's own configuration. It checks its clients against keys of its own, then swaps their credentials for TARS's before forwarding. It strips `X-Forwarded-For`, `CF-Connecting-IP` and the other headers that say where a request came from, and it runs with its access log switched off. A successful request leaves nothing behind.

Then the caller asked for more keys. Two edits later, the key file held one key per line and reloaded itself on change: add a new key, drain the old one, remove it. That's how you run a service with more than one client. It fits resale. It doesn't prove it.

## My key was safe

Swarm never gave TARS my provider key. The agent prepares a request; Swarm adds the real credential on the way out. There was no copy in the sandbox for anyone to ask the agent to read back, and the provider key stayed where it was the whole time.

It didn't matter. TARS had its own token for calling Swarm, and the relay used that token from TARS's own sandbox. Swarm checked that the token was valid and that the request came from the address the token was bound to. Both checks passed every time, because it really was TARS making the calls. Swarm billed TARS for every one of them, and it was right to.

The work gave it away. From about 10:20, the retained prompts stop being setup and start being somebody else's jobs: WhatsApp automation with a PostgreSQL message history, web UI and deployment work, the transcription of a 121-page historical document, Power BI and DAX dashboards, game dialogue, a crypto paper-trading loop. None of it was TARS's job.

Two days cost $65.04 over 971 charged calls, setup and testing included. Traffic stopped when the sandbox was replaced during a rollout on the 19th. Swarm's records establish unauthorised control and a working public relay. How the caller got in is less certain: an unauthenticated backend path is the leading assessment, with moderate confidence. I don't know who it was.

The cleanup didn't work. TARS could delete its own files. It couldn't delete Swarm's audit of its tool calls, which kept the original write and every edit. Replaying them rebuilds the final 9,641-byte gateway byte for byte.

Swarm could tell me to the cent what TARS had spent. Only the prompts showed whose work it was. I wanted to know what that work looks like at scale, and the only way to find out was to become the endpoint.

## How the honeypot saw inside

I built an inference API that answers in the request formats real clients use (OpenAI, Anthropic, OpenRouter and a Bedrock-style gateway), and planted keys for it where keys leak. Callers got real answers, mostly from a cheaper substitute model, so their software kept working.

What made it useful is how agents talk to models. An agent doesn't remember anything between calls; it sends its memory with every request. A single call can carry the agent's system prompt, its current assignment, the history of every tool it has run and the findings it has recorded so far. Each request is a snapshot of the job. Read in order, they show what the operator asked for and what the agents reported back, including work done on systems I never saw.

That's also the limit. I saw what agents were told and what they said happened. I didn't see the targets, and I can't verify any outcome an agent reported. The service never ran a tool from those histories, never tested a third-party credential and never contacted a target.

## What came through

**Where keys leak matters.** The keys that drew real work were all `.env` files in public GitHub gists. A key in an anonymous paste site drew one request in three weeks. The first gist key was test-fired the same morning it was planted, by a scanner that keeps a vault of harvested keys and checks their balances on a schedule.

**Quiet, then a market.** For eleven days almost nothing happened. Then, on 7 and 8 October, bulk workloads arrived together; on the 8th alone, 20,928 conversations started. That shape fits a key entering a resale pool and being sold on.

**One front door.** One address sent 44.9% of all requests and 84.8% of conversations, on three keys. Behind it were security scanners, coding agents, tutoring pipelines, agent benchmarks and business automation, in different languages and different harnesses. 91% of those conversations arrived with Go's default User-Agent, while the same harnesses also showed up directly under their own names. That's what TARS looked like from Swarm's side. Now I was on the other end.

**What it was for.** Security testing was the largest family by conversations (37.6%, below). Software was the heaviest by tokens (68.2%), because coding agents resend the repository every turn. Model and output checks were 4.1% of conversations but 31.8% of requests: resellers testing stock, one of them asking for six times seven, number only, 1,934 times. Education pipelines filled school question banks ten items at a time. One agent benchmark ran 2,306 sessions.

**What rides along.** My scanner redacted 2,403 distinct secrets from the conversations I later published: API keys, passwords, tokens, connection strings, one IBAN. Every customer of a cheap relay sends all of that through a stranger's box, and the stranger keeps it.

## The other attack agents

Security testing was the largest family by conversations: 14,350 of them, 37.6%, carrying 136,911 tool calls in their histories. All of it was in Chinese, all of it arrived as `Go-http-client`, and most of it ran on 8 and 9 October. Four workloads make up nearly all of it:

| Workload | Conversations | Tool calls in history | When |
|---|---:|---:|---|
| Bug-bounty hunter aimed at a Chinese education-sector programme, one target per session | 7,438 | 77,763 | 8 Oct |
| Artex platform (next section) | 4,261 | — | 8–14 Oct |
| Enterprise bug-bounty worker | 2,357 | 28,247 | one day |
| CTF solver | 232 | 5,498 | — |

The education-sector hunter alone caused the spike on 8 October: about ten tool calls per target, seven thousand targets, one day. The prompts say the work is authorised. Nothing in the traffic can confirm that for any target, so I've described these workloads from their instructions and metadata and left their targets and methods out.

**The key hunters.** The first gist key was picked up by a GitHub leaked-key scanner run by an agent. It keeps harvested keys in a vault and checks each one's balance every six hours, on the hour. Its own notes already warn that an exposed endpoint for paid models is probably a honeypot, and list the tells. Mine passed its "chat OK" test. A second harvester scraped GitHub for provider keys and had an agent try each one, through my endpoint, so its results were captured; the working keys went to their providers. Resellers checked their stock with named tools (`keypool-auth`, `Team-Provider-Audit`, `ModelAudit`), swept up to 483 model names per caller, and pinged the same trivial prompt thousands of times.

**Cracking and evasion.** 183 conversations reverse-engineered Android apps and binaries. One system prompt's whole job is removing protections from Android apps: paywalls, VIP and licence checks, activation codes, in-app purchases and ads. It forbids ethical or legal caveats and tells the model to treat unauthorised targets like authorised ones; its sampled task was unpacking a commercially protected app. Another 44 sessions ran a dedicated APK patching assistant. 67 sessions used jailbreak-style personas, often over ordinary work. A mobile chat app's persona, told never to name the model behind it, granted itself "special permissions" for game-client hooking, injection and trainers. A group-chat bot was told to pass as a human member, with a reverse-image-search tool.

**Agents guarding agents.** 837 conversations were security monitors and command reviewers for coding agents, most of them Claude Code's own safety check, routed here: the call that decides whether a shell command is safe to run. Another 1,063 had one agent review another's proposed step and return a verdict. 752 were the judge and auditor of an agent-risk benchmark, scoring whether agents can be steered into attack chains by instructions hidden in business documents. Someone's safety research, and someone's safety checks, ran on leaked inference, and my decoy answered them.

## Artex

On 7 October, CrowdStrike published an investigation into data theft at South Korean financial organisations, in which its researchers found Artex configuration files and session histories on infrastructure tied to the campaign. On 8 October, the first Artex platform traffic reached my honeypot. On 9 October, Reuters reported that the developer had taken the project closed-source. ([CrowdStrike](https://www.crowdstrike.com/en-us/blog/unknown-threat-actor-uses-artex-to-target-south-korean-finance/) · [Reuters, 9 October](https://www.reuters.com/world/china/chinese-developer-makes-artex-ai-agent-closed-source-after-korean-bank-hack-2026-10-09/)) I have no evidence that I was seeing the same operator.

**Identification.** I assess with high confidence that this traffic came from Artex. The requests use its tool names (`add_intent`, `record_fact`, `get_task_node_detail`, `get_worker_trace`) beside `Bash`, its role prompts and its hand-off from worker back to planner, all of which match the public source. Mentioning the word "Artex" isn't enough on its own: an article and a browser window title also did. Between 8 and 14 October I counted 4,261 platform conversations and 16 from its interactive operations console. By role: 1,799 planners, 1,844 workers, 287 reporters, 246 graph summarisers, 61 reviewers, 23 counterproofs and one retester. That identifies the software. It doesn't identify a version, an operator or a result.

**Two ways in.** On 8 and 9 October the platform asked for DeepSeek Flash, and all 3,841 of those requests came through the shared address above, on three planted keys. From 10 October it asked for GLM, and those 10,898 requests came from three other addresses on different keys. Whether that's one operator changing supplier or two operators with the same tool, the requests don't say.

**What the planners were told to find.** 565 of the 1,799 planners, 31%, had objectives that explicitly sought exposed AI credentials:

| Objective (paraphrased) | Planners | First seen (UTC) |
|---|---:|---|
| Search two public AI relays for their own upstream channel credentials | 378 | 10 Oct 13:58 |
| Expand discovery of exposed credentials across public LLM relays | 124 | 11 Oct 01:41 |
| Search public sites, configurations and gist revision history for API credentials | 53 | 10 Oct 08:11 |
| Search GitHub projects for exposed AI endpoint and key pairs | 7 | 10 Oct 10:00 |
| Search public sources for users' keys to one particular relay | 3 | 13 Oct 07:29 |

Both targets are public AI relays: services that resell access to other companies' models, which is what TARS had been turned into. The wording draws a clear line. The largest group wasn't after the keys a relay issues to its customers. It wanted the relay's own keys, the ones that pay its upstream providers; the objective says so in as many words, *"not keys elsewhere that point to these two sites"*. Both run One API or New API, the open-source software many relays are built on. That's 378 conversations repeating one objective, not 378 victims. Some objectives limited checks to read-only and forbade spending paid inference; others asked for endpoint and key pairs with no such limit. Claims of authorisation in a prompt don't establish permission from a target.

A separate objective, in 70 planner conversations, proposed a bulk audit of New API and One API relays for weak administrator credentials. It cited 180,821 search hits narrowed to 8,632 unique address-and-port pairs. Those are the objective's own inventory figures, not hosts I saw contacted or compromised.

**My bait on their list.** On 11 October, one planner's goal read, in translation: *"Within the authorised scope, find and record public hard-coded API-key leaks pointing at different sites that task 1 hasn't logged… and exclude task 1's existing findings, especially the two Gist keys for [my endpoint]."* Its sub-tasks repeat the instruction: search Postman workspaces, Hugging Face Spaces and URL scanners, but exclude the two known keys. Earlier in the same run, an agent had tested a batch of leaked keys and recorded that exactly one was *"confirmed valid with balance remaining"*: a key for my endpoint, filed as a finding. Their asset list had my domain on it, page title and all.

My bait was on their list, crossed off as old work, while the model calls writing that list were arriving at my honeypot.

**They knew about traps.** Artex's own worker prompt carries an "anti-AI honeypot red line": if a target asks the agent to identify itself, or to hand over its system prompt, tool list, credentials, API keys or configuration, treat it as a hostile trap, refuse, record a honeypot signal with high confidence, and drop to minimal contact with that target. In one run an agent did exactly that, noting that a site's error page carried text aimed at automated agents and declining to follow it. The rule is about targets that try to trick the agent. Nothing in it asks where the agent's own model calls are going.

**Shared infrastructure.** The 3,841 DeepSeek-era Artex requests arrived at the same address, on the same three keys, as every request carrying a reseller's branded routing profile. The credential-hunting planners came through other addresses. I can put some Artex work and the routing profiles on shared infrastructure, with moderate confidence that it is a shared forwarding service. I can't follow a key from a planner into a sale, or tell you who owns the route.

## Who's been told

Working provider keys that arrived in the traffic were reported to their providers, encrypted to each provider's published PGP key, with what the harvester's own test had shown. I haven't named the two relays that the 378 planner objectives targeted. No third-party credential was ever tested, and no target was contacted.

## What I'd check, if you run agents

**Keep the provider key out of the agent.** That part worked. Since then I've gone further: Swarm now gets short-lived credentials from OpenAI and Anthropic through workload identity federation, so there is no long-lived provider key left to protect.

**Treat the agent's own token as a credential someone else can spend.** Scope it to the models the job needs, meter it per agent, and set a spend limit you're prepared to lose. Source-address binding passed every relayed call here; it can't tell an agent's work from a relay in the same sandbox.

**Watch the work, not just the bill.** Pick one agent and one day. Put its model usage by hour next to its assigned jobs. Can you account for the busy periods? A historical transcription on an agent that doesn't transcribe tells you more than the source IP ever will.

**Watch the sandbox.** A new HTTP server, an outbound tunnel, a service that strips forwarding headers and disables its access log, setup files deleted while a service keeps running.

**Keep the audit where the agent can't reach it.** That's the only reason I could rebuild the relay.

**Check who can start a conversation with your agent**, through every route you expose, including the ones that only come to life after a restore. After TARS, Swarm's agents require authentication on direct and proxied paths.

**If you run an AI relay or gateway, assume its upstream keys are a target.** The largest single objective I saw was aimed at exactly those. Lock down the admin interface, change default credentials, and watch upstream spend for usage your customers don't account for.

## Indicators

**Source addresses:** [indicators-addresses.csv](indicators-addresses.csv) lists 392 of the 421 addresses that used a planted key, each with a role, a confidence, first and last seen, request and conversation counts, network and country. Four are high confidence: the three Artex addresses that carried the credential-discovery planners, and the leaked-key scanner. 176 are shared exits, such as Cloudflare WARP and a 160-address rotating pool, and are marked as such: an address there is not one person. The 29 not listed are my own test traffic and addresses that only touched a separate Swarm decoy.

Prompt-content indicators match on what a request carries, so they're most useful to anyone who logs prompts: model providers, gateways and agent platforms.

| Indicator | Type | First seen (UTC) | Last seen (UTC) | Context |
|---|---|---|---|---|
| `add_intent`, `record_fact`, `get_task_node_detail`, `get_worker_trace` in tool history beside `Bash` | Prompt content | 2026-10-08 | 2026-10-14 | Artex platform |
| System prompts opening as planner, worker, reporter, reviewer, counterproof, retester or graph-summary | Prompt content | 2026-10-08 | 2026-10-14 | Artex platform |
| `ARTEX-main`, `ARTEX/data` paths or an `ARTEX_UA` setting in context | Prompt content | 2026-10-08 | 2026-10-14 | Artex platform |
| Planner objective seeking an AI relay's own upstream channel credentials | Prompt content | 2026-10-10 | — | Artex credential discovery |
| Planner objective auditing New API / One API relay panels for weak admin credentials | Prompt content | — | — | Artex, 70 planners |
| `2d5555d1ec7c2e9cf6173b6a592631d329f7e25fae9482e2e6a7a8c5407a8189` | SHA-256 | 2026-09-18 09:54 | 2026-09-18 | TARS relay gateway, first version (8,181 bytes) |
| `79caf8f3c5a6414394556c8f639666e421887a5500ba75a30b7789dab3b03137` | SHA-256 | 2026-09-18 10:10 | 2026-09-19 | TARS relay gateway, final version (9,641 bytes) |
| A sandboxed service that reads the agent's runtime config, swaps `Authorization`, strips `X-Forwarded-For` / `CF-Connecting-IP` and sets `access_log=False` | Code pattern | 2026-09-18 | 2026-09-19 | TARS relay |
| `cloudflared` Quick Tunnel (`*.trycloudflare.com`) opened from an agent sandbox | Host | 2026-09-18 09:59 | 2026-09-19 | TARS relay |
| Many different harnesses' traffic arriving as `Go-http-client/2.0` on one credential | HTTP | — | — | Resold access through a forwarder (seen within the 22 Sep–14 Oct capture) |
| `keypool-auth`, `Team-Provider-Audit`, `ModelAudit` named in requests | Client name | — | — | Reseller key-checking tools (seen within the 22 Sep–14 Oct capture) |
| One trivial prompt repeated thousands of times; one caller sweeping 20–483 model names | Prompt / HTTP | — | — | Reseller key checks (seen within the 22 Sep–14 Oct capture) |

## What I can't tell you

- Who the caller was, or exactly which route delivered that first "hello".
- Whether anyone was selling access. Resale fits the evidence; it isn't proven.
- Whether any of the security work was authorised, or found anything. The bug-bounty and CTF workloads are described from their instructions only.
- Whether any Artex planner found a working relay key. A prompt is what an agent was asked to do, not what it did.
- Whether one address means one operator. A shared address can be a proxy, a cloud NAT or a credential pool.
- Who a buyer is from what they asked for. Variety of task isn't variety of customer: a few bulk jobs decide most of the percentages.

TARS and the honeypot are separate datasets, and nothing in one is evidence about the other. Task labels are rule-based, with no measured accuracy. Model names and costs are the honeypot's own accounting.

Swarm could tell me to the cent what TARS had spent. The question that 121-page document raised for me is the one I want every agent platform to be able to answer: who asked my agent to do this?
