# Art of README

> Source: [hackergrrl/art-of-readme](https://github.com/hackergrrl/art-of-readme)
> License: [Creative Commons Attribution](https://creativecommons.org/licenses/by/2.0/)

Distilled principles from the original article. Read the full source for history, examples, and community context.

---

## Core Idea

A README is a module consumer's first -- and maybe only -- look into your creation. Your job is to:

1. Tell them what it is (with context)
2. Show them what it looks like in action
3. Show them how they use it
4. Tell them any other relevant details

## Brevity

The ideal README is as short as it can be without being any shorter. Detailed documentation is good -- make separate pages for it -- but keep your README succinct.

## Key Elements (in order)

Readers scan READMEs top to bottom, short-circuiting when they find what they need or a red flag. Order matters:

1. **Name** -- Self-explanatory names are best. If the name is technical, define terms.
2. **One-liner** -- One sentence describing what the module does. Helps readers decide quickly.
3. **Usage** -- Show the module in action before diving into API docs. Copy-paste examples are best.
4. **API** -- Detail objects, functions, signatures, return types, callbacks, and events. Cover caveats.
5. **Installation** -- Even if it is just `npm install`, spell it out. New users need the guidance.
6. **License** -- Incompatible licenses are a quick disqualifier. Put non-permissive licenses near the top.

## Cognitive Funneling

Structure information from broad to specific:

- Widest end: name, description, high-level purpose
- Middle: usage examples, common scenarios
- Narrow end: API details, edge cases, background

> "The level of detail in Perl module documentation generally goes from less detailed to more detailed. Your SYNOPSIS section should contain a minimal example of use; the DESCRIPTION should describe your module in broad terms, generally in just a few paragraphs; more detail should be given in subsequent sections." -- perlmodstyle

## Practical Tips

1. Include a **Background** section if your project depends on non-obvious concepts.
2. Link aggressively. Few modules exist in a vacuum.
3. Document argument types and return values where not obvious from convention.
4. Include example code as a runnable file in the repo.
5. Use badges sparingly. Ask: "What real value does this badge provide to the typical reader?"
6. Keep APIs small and well-defined. Small APIs need less documentation.
7. For CLIs, show command invocations and their output.

## README Checklist

- [ ] One-liner explaining the module's purpose
- [ ] Necessary background context and links
- [ ] Unfamiliar terms link to informative sources
- [ ] Clear, runnable usage example
- [ ] Installation instructions
- [ ] API documentation
- [ ] Cognitive funneling (broad to specific)
- [ ] Caveats and limitations mentioned up-front
- [ ] Does not rely on images for critical information
- [ ] License
