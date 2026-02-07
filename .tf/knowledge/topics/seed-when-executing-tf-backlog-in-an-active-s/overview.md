# seed-when-executing-tf-backlog-in-an-active-s

Improve `/tf-backlog` so that when a **planning session is active** (started via `/tf-seed`), backlog generation automatically uses the session’s **root seed** and any attached **spikes / plan** as inputs (without the user having to re-specify the topic-id/path).

## Keywords

- planning-session
- tf-backlog
- seed
- spike
- plan
- auto-linking
- knowledge-base
- workflow
