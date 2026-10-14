# Execution Checklists

## Contents

1. [Audit Mode](#audit-mode)
2. [Review Mode](#review-mode)
3. [Improve Mode](#improve-mode)
4. [Refactor Mode](#refactor-mode)
5. [Update Mode](#update-mode)
6. [Generate Mode](#generate-mode)

<!-- v1.0.0 | 2026-01-30 -->

Mode-specific checklists for tracking progress during CLAUDE.md operations.

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
- [ ] Phase 0: Quality score ___/13 | Rating: [Excellent/Good/Fair/Poor]
- [ ] Phase 1: Issues found - Missing reasoning: ___ | Vague: ___ | Negative: ___ | Conflicts: ___
- [ ] Phase 2: All rules analyzed
- [ ] Phase 3: Report generated

Quality dimensions:
- [ ] Reasoning score: ___/3
- [ ] Specificity score: ___/3
- [ ] Positive framing score: ___/3
- [ ] Examples score: ___/2
- [ ] Structure score: ___/2
- [ ] Conflicts: ___
```

---

## Improve Mode

```
- [ ] Phase 1: Discovery complete
- [ ] Phase 2: Quality assessment complete
- [ ] Phase 3: Report presented to user
- [ ] Phase 4: User approved changes
- [ ] Phase 5: Updates applied

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
- [ ] Phase 0: Triage score ___ | Decision: [Skip/Light/Standard/Deep]
- [ ] Phase 1: Contradictions - Found: ___ | Resolved: ___
- [ ] Phase 2: Keep vs Extract determined
- [ ] Phase 3: Categories created
- [ ] Phase 4: Structure built
- [ ] Phase 5: Validation passed

Quality improvements applied:
- [ ] Missing reasoning added
- [ ] Vague rules made specific
- [ ] Negative rules reframed positively
- [ ] Examples added where needed
- [ ] Hybrid format validated
- [ ] Critical rules at BOTH start AND end
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
- [ ] Phase U2: Existing CLAUDE.md read (or none found)
- [ ] Phase U3: Drift detection complete
  - [ ] Stale commands: ___
  - [ ] Missing commands: ___
  - [ ] Structure changes: ___
  - [ ] Tech stack changes: ___
- [ ] Phase U4: Change preview presented
- [ ] Phase U5: User approved changes
- [ ] Phase U6: Updates applied

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
- [ ] Phase G6: Files created

Directory scores:
- [ ] {path} - Score: ___ [Create/Skip]
- [ ] {path} - Score: ___ [Create/Skip]
- [ ] {path} - Score: ___ [Create/Skip]

Quality gate (per file):
- [ ] Starts with @../CLAUDE.md (parent reference)
- [ ] Under 500 tokens hard limit (target 150-300)
- [ ] One-sentence Context (not verbose)
- [ ] Key Files lists 2-5 files only (not exhaustive)
- [ ] Patterns include reasoning ("pattern — why")
- [ ] No duplicate content from root CLAUDE.md
- [ ] No generic advice ("write clean code")
- [ ] Directory-specific content only
```
