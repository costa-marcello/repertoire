# Feedback Loops (M4)

How to check a skill's workflows for M4: a workflow that deletes, overwrites, publishes, or migrates, or that has 5 or more steps, needs a check before the irreversible step and a final verification.

## When M4 applies

| Workflow | Needs a check |
|----------|---------------|
| Fewer than 5 steps that only read | No |
| 5 or more steps | Yes: at least one check, and a final verification |
| Deletes, overwrites, or moves files | Yes: before the step |
| Publishes, pushes, releases, or sends | Yes: before the step |
| Migrates data or schemas | Yes: a dry run or validation first |

## What counts as a check

A concrete command or observation with a pass condition:

- a validator run with its exit code ("`python scripts/validate.py out.docx` exits 0");
- a diff or listing reviewed before applying (`git diff --stat`, a dry run);
- a test run;
- a re-read of the output against stated criteria;
- for actions that affect other people, showing the user what will happen and waiting for a yes.

"Make sure it looks right" is not a check; it is also an M7 lead.

## Patterns that pass

Validate, fix, repeat before the irreversible step:

```markdown
1. Edit `word/document.xml`.
2. Run `python scripts/validate.py unpacked/`.
3. If it fails, read the error, fix it, and run step 2 again.
4. Pack only when step 2 exits 0: `python scripts/pack.py unpacked/ out.docx`.
```

Plan, validate, execute for batch or destructive work:

```markdown
1. Write the planned changes to `plan.json`.
2. Run `python scripts/check_plan.py plan.json`; it rejects unknown fields and duplicate targets.
3. Apply the plan only after step 2 passes, then run `python scripts/verify.py` on the result.
```

A progress checklist for long workflows, which Claude copies and ticks off:

```text
Task progress:
- [ ] Step 1: Analyze input
- [ ] Step 2: Create plan
- [ ] Step 3: Validate plan (check)
- [ ] Step 4: Apply changes
- [ ] Step 5: Verify output (check)
```

## Patterns that fail

- "Edit the XML, then pack." No validation before packing.
- "Make all changes, then verify at the end" on a destructive step: the check comes after the damage.
- A plan that is executed without being validated.
- Multi-file changes with no intermediate check.
- A loop with no exit condition: "fix and re-run" needs a limit or a pass condition.

## Fix

Add a validate-fix-repeat loop before the irreversible step, a final verification, and an explicit limit or pass condition for any loop.
