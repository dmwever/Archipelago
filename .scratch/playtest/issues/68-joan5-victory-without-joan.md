# 68: Joan 5 declares victory on the refugees alone, without Joan reaching Compiegne

**Reported:** 2026-11-02, playtesting

**Status:** done (pending in-game test)

## Report

Joan of Arc 5 does not require Joan to be in Compiegne to declare victory, just the 6 villagers.

## The counter double-counts

`AP Victory` (t79) fires on **variable 2 equal to 2**:

| | |
| --- | --- |
| condition | `variable_value` variable **2**, comparison Equal, quantity **2** |
| effects | `script_call Victory();`, deactivate t8, deactivate t12 |

Exactly two triggers write variable 2, and the intent is plainly one point each:

| trigger | looping | condition | effect |
| --- | --- | --- | --- |
| **t54 `Refugees in Area 6`** | **yes** | 6 of P1's object_type 3 inside `(174,128)-(180,134)` | var2 **+1** |
| t56 `Joan in Area` | no | object **14871** brought into the same area | var2 **+1** |

Object 14871 is unit 629 owned by P1 - Joan.

t54 is **looping and never deactivates itself**. It turns off the other refugee counters
(t49-t53 and t55) but not t54, so while six refugees stand in the Compiegne box the trigger
re-fires every tick and adds 1 each time. Variable 2 goes 1, 2, 3, ... and `AP Victory` catches
it at 2 on the second tick. Joan never has to arrive.

## This is an inherited vanilla counter being read as a tally

The looping is vanilla. In the stock `2_Joan_5`:

| vanilla trigger | looping | writes var2 |
| --- | --- | --- |
| `Refugees in Area 0` through `Area 5` | yes | no |
| `Refugees in Area 6` | **yes** | **yes** |
| `Joan in Area` | no | **yes** |

So vanilla carries the same latent double-count. What vanilla does **not** do is treat var2 as a
victory condition. The only vanilla trigger that reads `var2 == 2` is `[D10] Reach Compiegne`,
which is **disabled** and whose effects are a message and a trigger activation.

`AP Victory` is an AP-era trigger that keyed the scenario's ending on a counter that was never a
reliable tally of "both halves done".

## The fix

Two shapes, and the second is safer:

1. **Clear t54's looping flag.** One field. But the loop is vanilla and the other refugee
   counters all loop too, so something else may rely on the re-evaluation; this needs checking
   before it is taken.
2. **Give `AP Victory` the two real conditions** instead of the derived counter - 6 of P1's
   object_type 3 in `(174,128)-(180,134)` **and** object 14871 in the same area. That is exactly
   what t61 `AP Escort Joan` and t63 `AP Escort Refugees` already test separately, so the
   conditions are known good and can be copied. It leaves vanilla's counter alone.

## Logic is already correct

`rules/joan_rules/joan_5.py` requires all ten refugee items **and** `keeps_its_siege` for
`JOAN5_VICTORY`, `JOAN5_ESCORT_JOAN` and `JOAN5_ESCORT_REFUGEES` alike. Logic expects the escort
to be done; only the scenario is lenient. So this is a scenario-side fix with no rule change.

## Comments

### Fixed (2026-11-03), pending in-game test

`AP Victory` no longer reads the doubling counter. It now carries two conditions:

| | |
| --- | --- |
| `variable 2 == 1` | Joan reached Compiegne |
| `variable 0 == 6` | six refugees reached Compiegne |

The looping `Refugees in Area 6` trigger can no longer supply both halves on its own.
