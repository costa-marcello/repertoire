# Execution Checklists

## Contents

1. [Audit Mode](#audit-mode)
2. [Review Mode](#review-mode)
3. [Improve Mode](#improve-mode)
4. [Refactor Mode](#refactor-mode)
5. [Update Mode](#update-mode)
6. [Generate Mode](#generate-mode)

<!-- v1.1.0 | 2026-10-14 -->

Mode-specific checklists for tracking progress during CLAUDE.md operations. Phase numbers match SKILL.md.

---

## Audit Mode

```
- [ ] Phase 1: Discovery - Files found: ___
- [ ] Phase 2: Quality assessment - Scores calculated
- [ ] Phase 3: Report generated

Summary:
- [ ] Total files: ___
- [ ] Average score: ___/100
- [ ] Files needing update: ___
```

---

## Review Mode

```
- [ ] Phase 1: Discovery - Files found: ___
- [ ] Phase 2: Rubric score ___/100 | Rule quality ___/13 | Rating: [Excellent/Good/Fair/Poor]
- [ ] Phase 4: Issues found - Missing reasoning: ___ | Vague: ___ | Negative: ___ | Conflicts: ___ | Wrong imports: ___
- [ ] Phase 3: Report output, with the Phase 4 issues
- [ ] No file changed, no project command run

Rule quality dimensions:
- [ ] Reasoning score: ___/3
- [ ] Specificity score: ___/3
- [ ] Positive framing score: ___/3
- [ ] Examples score: ___/2
- [ ] Structure score: ___/2
- [ ] Conflicts: ___ (-1 each, down to -3)
```

---

## Improve Mode

```
- [ ] Phase 1: Discovery complete
- [ ] Phase 2: Quality assessment complete
- [ ] Phase 4: Issues detected (reasoning, vague, negative-only, conflicts, wrong imports)
- [ ] Phase 3: Report presented to user, with the Phase 4 issues
- [ ] Phase 5: Targeted updates proposed with diffs, user approved
- [ ] Phase 7: Updates applied and each file re-read

Changes made:
- [ ] Commands added/updated
- [ ] Gotchas documented
- [ ] Reasoning added to rules
- [ ] Vague rules made specific
- [ ] Negative rules reframed positively
```

---

## Refactor Mode

```
- [ ] Phase 6: Triage score ___ | Decision: [Skip/Light/Standard/Deep]
- [ ] Phase 6: Contradictions - Found: ___ | Resolved: ___
- [ ] Phase 6: Keep vs Extract determined
- [ ] Phase 6: Rule files planned, with a paths: glob for each topic-specific rule
- [ ] Phase 6: Preview shown: each new or changed file, each rule to be removed
- [ ] Phase 7: User approved, files written and re-read
- [ ] Phase 7: Validation checklist from the Refactoring Complete template passed

Quality improvements applied:
- [ ] Missing reasoning added
- [ ] Vague rules made specific
- [ ] Negative rules reframed positively
- [ ] Examples added where needed
- [ ] Hybrid format validated
- [ ] Critical rules at BOTH start AND end
- [ ] No @ import of a .claude/rules/ file
```

---

## Update Mode

```
- [ ] Phase U1: Codebase scan complete
  - [ ] Package manager detected: ___
  - [ ] Commands extracted: ___
  - [ ] Directory structure mapped
  - [ ] Frameworks detected: ___
  - [ ] Config/env files found: ___
  - [ ] AGENTS.md present: [yes/no]
- [ ] Phase U2: Existing CLAUDE.md read (or none found)
- [ ] Phase U3: Drift detection complete
  - [ ] Stale commands: ___
  - [ ] Missing commands: ___
  - [ ] Structure changes: ___
  - [ ] Tech stack changes: ___
- [ ] Phase U4: Change preview presented
- [ ] Phase U5: User approved changes
- [ ] Phase U6: Updates applied and each file re-read

Preservation check:
- [ ] Hard Rules untouched
- [ ] Core Principles untouched
- [ ] User-authored reasoning preserved
- [ ] Gotchas preserved (unless referencing deleted files)
```

---

## Generate Mode

```
- [ ] Phase G1: Discovery - Directories scanned: ___
- [ ] Phase G2: Scoring - Candidates (score >= 4): ___
- [ ] Phase G3: Content extraction complete
- [ ] Phase G4: Preview generated
- [ ] Phase G5: User approved files: ___
- [ ] Phase G6: Files created and each one re-read

Directory scores:
- [ ] {path} - Score: ___ [Create/Skip]
- [ ] {path} - Score: ___ [Create/Skip]
- [ ] {path} - Score: ___ [Create/Skip]

Quality gate (per file):
- [ ] No @ import of a parent CLAUDE.md (it loads already)
- [ ] Under 500 tokens hard cap (about 100 minimal, 150-300 full)
- [ ] One-sentence Context (not verbose)
- [ ] Key Files lists 2-5 files only (not exhaustive)
- [ ] Patterns include reasoning ("pattern — why")
- [ ] No duplicate content from root CLAUDE.md
- [ ] No generic advice ("write clean code")
- [ ] Directory-specific content only
```
