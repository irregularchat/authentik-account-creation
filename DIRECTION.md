# Direction: authentik-account-creation

The original IrregularChat account-creation and community dashboard: a tool that creates
Authentik accounts for chat community members, later expanded to Signal and Matrix
management. It has been superseded by its fork, chat-based-community-dashboard.

Status: dormant (last change 2025-12-14). That change was a merge of September 2025 work;
the last new commit was 2025-09-02.

## Where it is heading
- Nowhere new. Development moved to `irregularchat/chat-based-community-dashboard`, a
  GitHub fork of this repo. The two share 752 commits, and this README already carries the
  dashboard's title and points to that repo's branches (README.md).
- The only work here that is not in the fork is the Signal group self-join feature
  (`!join`, instant joins for authorized users), merged as PR #5 (ce4b279b9, 80706b4d7, 9c0245fb4).
  The fork has its own Phase 2 self-join commits (7fb0eef43) and an unmerged
  `feature/signal-self-join` branch at the same head as this repo's commit 7dbf49949.

## Priorities
1. Security and data hygiene review (tracked privately).
2. Decide what happens to this repo: archive it with a pointer to the dashboard, or keep it
   as the canonical upstream (open question).
3. If any of the self-join commits are still wanted, port them to the dashboard rather
   than developing here (inferred).

## Non-goals and constraints
- Don't develop new features here while the fork is the active line (inferred from history:
  no new commits since 2025-09-02, while the fork had 82).
- Same stack and rules as the fork: Next.js/TypeScript/Prisma/tRPC under `modern-stack/`,
  Streamlit archived (README.md).

## Decisions
- 2025-12-14: merged the Signal self-join feature here, not in the fork (9c0245fb4)
- 2025-09-02: Phase 2 Signal self-join: authorized users join groups without admin action (ce4b279b9)
- 2025-08-15: moved to the Next.js stack and archived Streamlit (88e346e, shared with the fork)
- 2024-12-13: the fork chat-based-community-dashboard was created and took over development
  (GitHub fork metadata)

## Open questions for the owner
1. Archive this repo (read-only, with a README pointer to the dashboard), or keep both alive?
2. Should the self-join work (PR #5) be merged into the dashboard?

## Related documents
- See chat-based-community-dashboard's DIRECTION.md for the active line.
- `README.md`, `ROADMAP.md`, `modern-stack/ROADMAP.md` (identical in lineage to the fork's).
