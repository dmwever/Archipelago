# 12: Unknown item ids hold their stream position as SKIP placeholders

**What to build:** `_handle_received_items` drops any item id this apworld doesn't know. Every later
entry then sits one index lower locally than on the server. The spent bitmask and the game's
`appliedItemCount` are both keyed by local position. After an apworld update recognises the id, they
point at different items: a spent trap can be re-delivered, or a progression item sent as SKIP.

Keep a placeholder entry at that position instead. The placeholder goes to the game as
`ITEM_SKIP`, is never one-shot, and never seats a mercenary. Keep the existing warning.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] An unknown id occupies its stream index; local indices match the server's
- [ ] The placeholder is sent as `ITEM_SKIP` and never sets a spent bit
- [ ] The warning still fires, once per unknown id
- [ ] Tests: a stream with an unknown id in the middle keeps later indices aligned, and the window
      sends SKIP at that position
