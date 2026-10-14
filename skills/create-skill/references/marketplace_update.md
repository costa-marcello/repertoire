# Marketplace Update

This step applies only when the repository has `.claude-plugin/marketplace.json` at its root. Without that file there is no marketplace to update, so skip it. Schema source: https://code.claude.com/docs/en/plugins/marketplace-reference

## Contents

1. [Schema](#schema)
2. [Adding a skill](#adding-a-skill)
3. [Updating a skill](#updating-a-skill)
4. [Validating](#validating)

## Schema

**Top level** (all three fields required):

| Field | Meaning |
|-------|---------|
| `name` | Marketplace name, in kebab-case |
| `owner` | Object with a required `name` and optional `email` and `url` |
| `plugins` | Array of plugin entries |

Other top-level fields, such as `description`, are optional.

**Each `plugins[]` entry:**

| Field | Required | Meaning |
|-------|----------|---------|
| `name` | Yes | Plugin name, in kebab-case. Names starting with `claude-`, `anthropic-`, `anthropics-`, or `cc-plugin-` are an error. |
| `source` | Yes | A relative path string starting with `./`, or a source object of type `github`, `url`, `git-subdir`, `npm`, `archive`, or `command` |
| `strict` | No | Default `true`: the plugin's own `plugin.json` is the authority, and the entry adds to it. With `false`, the entry is the whole definition: no `plugin.json` is needed, and the entry lists the components itself, for example `"skills": ["./skills/csv-report"]`. |
| `version` | No | A free-form string. When it is present, use semver (below). |
| `description`, `author`, `category`, `keywords`, `homepage` | No | Listing metadata |

Claude Code ignores unknown fields at load time, and `claude plugin validate` warns about them.

Minimal file with one plugin that bundles several skills:

```json
{
  "name": "team-skills",
  "owner": { "name": "Platform Team" },
  "plugins": [
    {
      "name": "team-skills",
      "source": "./",
      "description": "Skills for profiling CSV files and applying brand guidelines.",
      "version": "1.0.0",
      "strict": false,
      "skills": ["./skills/csv-report", "./skills/brand-guidelines"]
    }
  ]
}
```

## Adding a skill

1. Read the existing file and follow its structure: one plugin per skill, one plugin that lists several skills, or one plugin that finds its skills in `skills/`.
2. **One plugin per skill:** add an entry whose `name` is the skill name.
   - `source`: the plugin's directory.
   - `description`: shortened from the SKILL.md description.
   - `version`: `"1.0.0"`, if the other entries carry versions.
3. **One plugin for several skills:** add the skill's path to that plugin's `skills` array, and bump its minor version if it has one.
4. **One plugin that finds its skills in `skills/`** (no `skills` array, as in Repertoire): a new `skills/<skill-name>/` needs no manifest change. Run the validation below anyway.

## Updating a skill

Bump `version` on the plugin that contains the skill:

| Change | Bump | Examples |
|--------|------|----------|
| Patch (1.0.x) | Bug fixes, wording, typo corrections | Fixed a broken path reference |
| Minor (1.x.0) | New features, new reference files, new workflow steps | Added a validation step |
| Major (x.0.0) | Breaking changes | Renamed the skill, changed its arguments, restructured the workflow |

If the existing entries have no `version` field, do not add one just for this change. Without a version, a plugin update installs the latest pushed commit.

## Validating

1. From the repository root, run `claude plugin validate .`.
2. Fix every error. Read every warning: an unknown field is usually a typo.
3. Run `git diff .claude-plugin/marketplace.json` and check that only the intended entries changed.
