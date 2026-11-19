# 10: The Ratha's status line sits above queue-button text

**What to build:** Nothing yet — this needs a ruling first. `extended_tooltip_id` in
`GameStrings.py` adds a flat `+21000` to the baked name string id, so a row whose name string is
itself in the 21xxx campaign band derives a tooltip in the 42xxx scoreboard band. 05 looked at this
and ruled it harmless because none of the affected objects has a train button, so the game never
renders their extended tooltip. `Age2UnitData.RATHA` and `ELITE_RATHA` break that argument: they are
the Bengali unique unit and its elite upgrade, they are trainable, and they do have a train button.

Confirmed, not inferred — `python -m worlds.age2de.tools.recapture_string_ids --verify` reports:

```
RATHA         21104 -> 42104  'Click to remove this unit from the queue.'
ELITE_RATHA   21105 -> 42105  'Click to stop creating this unit.'
```

Those ids reach the game through `UnitData.xs` and `addUnit(..., row.tooltip_id)`, and
`writeUnitStatusLine` writes them verbatim, so in a Bengali seed with Unitsanity on, hovering the
Ratha reads a status line above "Click to remove this unit from the queue." instead of above the
Ratha's own description. The empty-string guard in `Unitsanity.xs` cannot catch it: the string
resolves to real text.

The ruling needed is which way to fix it: the `+21000` offset is wrong for rows already in that
band and needs a band-aware derivation, or those rows carry no tooltip id and fall into the
no-extended-tooltip case 05 already defined. 03's ruling that the ids are baked and never computed
in game stands either way.

**Status:** needs-triage

- [ ] A Bengali seed's Ratha and Elite Ratha either carry their own description beneath the status
      line or carry no status line at all
- [ ] `recapture_string_ids --verify` reports no mismatch that a trainable object can render
- [ ] The remaining mismatches are still covered by a recorded reason, not by silence

## Rulings

- 2026-11-13: Out of scope for 06, which only re-applies whatever the other tickets decided to write.

## Comments

- 2026-11-13: Found by the review on 06 and verified against the game's own
  `key-value-strings-utf8.txt`. 05's count of the damage — "jobs resolve 4/24, heroes 9/16, escorts
  0/2" — is right about the five enums behind `UnitLocation`, and the two mismatches it missed are in
  `UNIT_NAME_STRINGS` itself, which it recorded as 230 ok / 30 absent without looking at the 2
  mismatched. Those 2 are the Ratha pair.
- 2026-11-13: `WARSHIPS` 7034 and `HEAVY_WARSHIPS` 7035 also mismatch but are not this bug: they land
  on 28034 / 28035, which are the "Upgrade to <b>War Galley…" strings — the right kind of text for an
  upgrade tech. `HERDER_MALE` / `HERDER_FEMALE` 5897 -> 26897 is the case 05 already recorded. The
  remaining 13 are the jobs, Joan heroes and `OYSTER_GATHERER` in the 21xxx band, which have no train
  button and so never render.
