# Clarifying Questions

<!-- The ask-before-search step of the research skill: which questions to ask, how, the search period, the research brief, and the start gate -->

## Contents

1. [Why ask first](#why-ask-first)
2. [Which questions to ask](#which-questions-to-ask)
3. [How to ask](#how-to-ask)
4. [The search period](#the-search-period)
5. [The research brief](#the-research-brief)
6. [When no one can answer](#when-no-one-can-answer)
7. [Example](#example)

## Why ask first

One run dispatches 6 to 10 agents, so a run aimed at the wrong angle spends all of them on results the user did not want. Settle the angle before any search. Ask only the questions whose answers would change where or how the agents search, and let the user's own words decide which those are: a vague request needs more questions, a precise one may need only the period.

## Which questions to ask

Choose from this list, in this order of impact (a word that splits the topic into different products or fields comes first, whatever its row), and skip any the request already answers:

| Dimension | Ask when | Example options |
|-----------|----------|-----------------|
| Ambiguous terms | A word means different products or fields here | Which Copilot: Microsoft 365 / GitHub / the consumer app; "agents" as AI agents / as human staff |
| Purpose | The request does not say what the answer is for. Skip it when the wording implies one: "what's new" means keeping up, and "X vs Y for a team" means choosing between them | Choosing a tool to buy / Comparing vendors for a pitch / Keeping up with the market |
| Angle | The request is only a name or a broad noun phrase, so the agents cannot tell which side of it to search | Which part of selling; what it offers / how customers rate it / how it compares / what is new |
| Scope | The answer differs by market, region, company size, industry or role | UK / Europe / Global; SMB / mid-market / enterprise |
| Current setup | The advice depends on what the user already runs | The tools the topic suggests, plus "None yet" |
| Named products | The topic has competing products, vendors or methods | Include these / Compare two of them / Leave some out |
| Period | Always (see [The search period](#the-search-period)) | Last 30 days / Last 12 months / Any date |
| Source emphasis | Practitioners and official sources may disagree | Practitioners' experience / Official and analyst data / Both, side by side (tilts the agents' queries, not the agent count) |
| Must-have content | The answer must contain something specific | Prices / Named-company case studies / Risks and compliance |
| Already known | The user may have researched this before, or their profile says they know the field | Skip the basics (Recommended when the profile says so) / Leave out what they have ruled out |
| Depth | `DEPTH` was not given and the topic looks broad or narrow | Quick (6 agents) / Default (8) / Deep (10) |

Never ask about the output format (the report ends with that offer), the search backend, the models, or anything the request already says. Ask a high-impact question even when its default is unclear: put the likeliest answer first and say in its description that it is a guess. When no option is clearly the likeliest (a priority, an angle or a focus), put a broad option such as "All of these, evenly" or "A rounded picture" first, so the default brief does not narrow the run on a guess.

## How to ask

- **Click, not type:** ask with AskUserQuestion, up to 4 questions per call. Ask the highest-impact questions first, and let their answers decide whether later ones are still needed: put a question in the next call when its options or its recommended answer depend on an earlier answer (a period after a buy-or-news purpose, a feature list after a product version). Ask at most 10 questions in total, over at most 3 calls, plus the start question in [The research brief](#the-research-brief).
- **One decision per question:** one axis only (not stage and size, or helpdesk and CRM), with options that do not overlap and name one thing each (not "Construction and transport"). Use plain words, a question of one short line (put examples in the option descriptions, not the question), a header of at most 12 characters ("Purpose", "Market", "Period"), and 2 to 4 options built from the user's topic.
- **Recommended first:** put the option you would pick first, given the request, the conversation and what the user's profile says about them (their own team and tools, their region, what they already know), and end its label with "(Recommended)". Skip a question the profile already answers, and say so in the brief.
- **Say what each option changes:** give each option a one-line description that starts with what it changes in the search ("Searches…", "Adds…", "Leaves out…"), not with what the option is. Explain any term the user may not know, and never invent figures, such as a size band in staff numbers. The tool adds "Other" for a typed answer.
- **No AskUserQuestion tool:** send the same questions as one numbered message with lettered options, the recommended one marked, say the user can reply like "1a 2c", and wait for the reply.
- **Nothing runs first:** no ToolSearch, script run or agent until the user picks Start. Two exceptions: loading AskUserQuestion, and a memory or notes lookup that the user's own instructions say to make before asking, since an earlier note can answer a question.

## The search period

How far back to search is always settled with the user: too short a period drops useful older material, and too long a one buries what is new. When the request names a period ("in the last 30 days", "since August", "this year"), use it and skip the question; the brief still shows it. Otherwise ask, with the options that fit the topic:

| Option | `PERIOD_DAYS` | Fits |
|--------|---------------|------|
| Last 30 days | 30 | Launches, incidents, breaking news |
| Last 60 days | 60 | News, what's new, current sentiment |
| Last 12 months | 365 | Tool choices, pricing, adoption |
| Any date | 3650 | Evergreen topics, methods, laws and standing rules, history |

A topic tied to one cycle or event (a run of rate rises, a law coming into force) can offer a window that starts there, such as "Since the first rate rise (Recommended)". Turn it, like a typed answer, into the number of days from that date to today. `DATE_FROM` is today minus `PERIOD_DAYS`, and the script gets `--days {PERIOD_DAYS}`. Sources that stay in force whatever their date, such as a law or an official standard, are kept even when published before the period: say so in the brief's Include line.

## The research brief

After the answers, refine `TOPIC` with the user's own terms. Add a scope term (such as "UK mid-market") to `TOPIC` only when most sources on the topic are specific to it; when the evidence is mostly global (buyer reviews, vendor news), keep the region and size in the Scope line. Check `QUERY_TYPE` against the purpose too: choosing what to buy or use is RECOMMENDATIONS, and keeping up with changes is NEWS. Then write the brief in the chat and store it as `BRIEF`:

```
Research brief
- Topic: {TOPIC}
- Purpose: {what the answer is for}
- Scope: {market, region, segment or role, or "no limit"}
- Include: {named products, sites or angles, or "nothing specific"}
- Exclude: {what to leave out, or "nothing"}
- Period: {label}, {DATE_FROM} to today
- Sources: {emphasis}
- Depth: {quick, default or deep}, {n} agents ({C} community + {O} official), {agent model and effort from model-routing.md}
- Assumed: {each answer you chose yourself, each answer taken from the profile, and each Include or Exclude item that no answer or request word supports, or "none"}
```

An Exclude line rules things out of the whole run, so put a guess there only when the user picked it; otherwise rank it lower under Include. Then ask one more AskUserQuestion: the question "Start the research with this brief?", header "Start", with the options "Start the research (Recommended)" and "Change something" (description: "Say what to change, and I'll update the brief"). After "Change something" or a typed answer, update the brief, show it again, and ask again. Search nothing until the user picks Start.

## When no one can answer

In a `claude -p` run, a subagent, or a scheduled task, nobody can click. Do not ask. Pick the recommended answer to each question you would have asked, and list each of those questions with its answer under "Assumed" in the brief. Take the period the request implies (NEWS wording such as "what's new" or "lately": last 60 days), else the period you would recommend for the topic (any date for methods, laws and history, a window from the start of the cycle for a topic tied to one, otherwise the last 12 months), and keep `DEPTH` at default when the request set no flag. Show the brief and continue without the start question. This applies even when AskUserQuestion is missing.

## Example

`/research AI tools for sales teams` names no purpose, angle, size or period. The user's profile says they sell in the UK and their CRM is Dynamics 365, so the market is not asked. The first AskUserQuestion call:

1. Purpose: Choosing tools to buy (Recommended) / Comparing vendors for a pitch / Keeping up with the market
2. Use case: The whole sales cycle (Recommended) / Prospecting and outreach / Calls and coaching / CRM and forecasting
3. Company size: Mid-market (Recommended) / SMB / Enterprise

The period and the CRM depend on the purpose, so they go in a second call: "Period: Last 12 months (Recommended) / Last 60 days / Any date" and "CRM: Dynamics 365 (Recommended) / Salesforce / HubSpot / No CRM requirement". The brief then reads "Topic: AI tools for sales teams", "Scope: UK, mid-market", "Purpose: choosing tools to buy", "Period: last 12 months", with "market: UK, from your profile" under Assumed, and the start question follows. A request such as `/research Pipedrive pricing changes in the last 30 days --quick` already names the product, the period and the depth, so it may need no question before the brief.
