# Setup

review-skill runs on its own, but its automated checks come from create-skill's scripts. Install both skills together so the validator is found next to this skill.

## Install both skills

```bash
npx skills add costa-marcello/skillkit -s create-skill -s review-skill
```

## Where the validator is looked up

SKILL.md step 2 takes the first of these folders that contains `quick_validate.py`:

1. `../create-skill/scripts/` relative to review-skill's folder (`${CLAUDE_SKILL_DIR}/../create-skill/scripts/` in Claude Code)
2. `.claude/skills/create-skill/scripts/` in the project
3. `.agents/skills/create-skill/scripts/` in the project
4. `~/.claude/skills/create-skill/scripts/`
5. `~/.agents/skills/create-skill/scripts/`

Check an install with:

```bash
ls ~/.claude/skills/create-skill/scripts/
```

It should list `quick_validate.py` and `security_scan.py`.

## Python and PyYAML

The scripts need Python 3 and PyYAML. Use `python`, or `python3` where `python` is not on the path (on Windows, `python3` may be the Microsoft Store stub):

```bash
python -m pip install pyyaml
```

quick_validate exits 3 when PyYAML is missing.

## gitleaks (secret scan)

security_scan uses gitleaks for the secret scan and exits 3 when it is missing. Install it for your OS:

| OS | Command |
|----|---------|
| macOS | `brew install gitleaks` |
| Windows | `winget install gitleaks`, or `scoop install gitleaks` |
| Linux | Download the `linux_x64` (or `linux_arm64`) tarball from https://github.com/gitleaks/gitleaks/releases, extract it, and put `gitleaks` on the path |

For Linux, after downloading the tarball from the releases page:

```bash
tar -xzf 'gitleaks_<version>_linux_x64.tar.gz' gitleaks && sudo mv gitleaks /usr/local/bin/
gitleaks version
```

## Commands

With `<dir>` set to the folder found above, and each placeholder kept inside its single quotes (on Windows, run these with the Bash tool, which is Git Bash):

```bash
python '<dir>/quick_validate.py' '<target-skill>' [--portable]
python '<dir>/security_scan.py' '<target-skill>' --verbose --no-marker
```

`--no-marker` keeps security_scan from writing its pass marker into the target, which review-skill relies on in every mode. security_scan ends with `RESULT secrets=<n> leads=<n>`; exit 1 or 2 means secrets only when that line shows `secrets` above 0.

## Manual fallback

When create-skill is not installed, or a script exits 3, review-skill applies `rules.md` by hand: it walks every rule, quotes the evidence for each finding, and reads the bundled files for secrets. The report then says "automated checks: not run" with the reason, so the reader knows the definitive checks were done by reading rather than by the validator.
