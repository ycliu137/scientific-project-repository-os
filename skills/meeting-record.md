# meeting-record.md

Meetings are **private**. `meeting_record/` is gitignored (except `README.md`). Transcripts **may be Chinese**. Durable Chinese minutes that should become a PDF go in `tex_docs/` instead (`skills/tex-docs.md`, `skills/language.md`).

## Ingest

User drops or pastes a recall/transcript:

`meeting_record/YYYYMMDD_meeting.md`  
(optional suffix: `20260724_meeting.md`)

**Same session**, the agent **must** write:

`meeting_record/YYYYMMDD_action_items.md`

containing:

1. Short discussion summary (decisions, disagreements)
2. **Next tasks** (actionable)
3. **How to complete** each (which sibling repo, which skill, done_when)
4. Items promoted into `workspace/current/NEXT_ACTION.yaml` — **in English**

Do not skip action items because the meeting was informal. If the transcript is Chinese, still write English titles/summaries for anything that leaves this folder.

## Do not

- Commit meeting contents
- Put meetings in the source or paper repo
- Treat the transcript as a result object; promote facts into `H_*` / `CL_*` only when they become project knowledge
