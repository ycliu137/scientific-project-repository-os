# language.md — Project language is English

Default: **English** for everything agents and collaborators share — skills, objects, code, comments, `docs/`, Change Reports, pipelines, `env/`, tests, and the paper manuscript.

## Allowed Chinese

| Where | What |
|-------|------|
| `tex_docs/` | Durable **meeting notes** (and other human TeX) in Chinese; compile to PDF (`skills/tex-docs.md`) |
| `meeting_record/` | Private raw transcripts / recall in Chinese (`skills/meeting-record.md`) |

No other tree (including `docs/`, `objects/`, `src/`, `pipelines/`, paper `tex/`) should be written in Chinese.

## Promote into English

Facts that leave the meeting folder become English: `H_*` / `CL_*` / `EXP_*`, `workspace/current/NEXT_ACTION.yaml`, Change Reports, pipeline READMEs. Do not copy a Chinese paragraph into an object YAML.

Quoted original titles in a `source` object may keep the original script **in one field**; the `title` / body the OS reasons over stay English.

## Do not

- Mix Chinese into skills, constitution, or code comments “for the local team”
- Use Chinese in artefact path tokens
- Treat a Chinese `tex_docs/` note as a result object
