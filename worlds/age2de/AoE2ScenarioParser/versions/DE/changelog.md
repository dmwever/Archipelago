# Changelog

All changes made to the scenario file will be documented in this file.

> Local additions for the Ageipelago fork. `v1.57` was copied verbatim from
> AoE2ScenarioParser 0.7.3; `v1.58` was reverse-engineered from the shipped
> AP campaign scenarios, which the upstream parser cannot open.

## Scenario v1.58

Derived from `v1.57`. Only `EffectStruct` changed; `ConditionStruct` is untouched.

### Changed

- Triggers:

    - `trigger_version` default `4.7` -> `4.9`
    - `EffectStruct.static_value_75` default `81` -> `83` (i.e. two more `s32` fields)

### Added

- Triggers, `EffectStruct`: two `s32` fields appended after `wall_y2` and before `message`.
  Semantics unknown; observed values are `-1` for the first across all 1479 effects sampled,
  and `-1`/`1` for the second.

    ```json
    "unknown_1_58_a": {
        "type": "s32",
        "default": -1
    },
    "unknown_1_58_b": {
        "type": "s32",
        "default": -1
    },
    ```

### Verification

All 12 `AP_*.aoe2scenario` files open, and a read/write/read round-trip reproduces every
trigger, effect and condition field exactly (2402 parts across the 12). Byte-level round-trip
is *not* identical, for two reasons that predate this version and affect all versions:

- the payload is recompressed at a different zlib level, so the file shrinks ~8-10%;
- the parser strips a string's trailing null on read and does not re-add it on write, so
  embedded AI scripts lose one byte and their length prefix is adjusted to match.

No `default.aoe2scenario` is shipped for `v1.58`, so `from_default()` raises rather than
silently loading a `v1.57` file. `from_file()` and `write_to_file()` are unaffected.

---

## Scenario v1.43

No changes except for default civilization changed to 38 (from 36) because of the 2 new civs (DotD)

---

## Scenario v1.42

### Added

- Map
    - Renamed:
      `block_humanity_team_change` to `lock_coop_alliances`
    - Changed order:
    ```
    script_name
    ...
    block_humanity_team_change  -->  collide_and_correct
    collide_and_correct         -->  villager_force_drop
    villager_force_drop         -->  unknown
    unknown                     -->  lock_coop_alliances 
    ...
    player_1_camera_y
    ```
    - Added (After reorder & rename):
        - Between `lock_coop_alliances` and `player_1_camera_y`
        ```json
        "ai_map_type": {
            "type": "s32",
            "default": 0
        },  
        ```

- Triggers
    - Effects
        - Between `unknown_4` and `message`
        ```json
        "color_mood": {
            "type": "s32",
            "default": -1
        },
        ```
    - Conditions
        - Between `unknown_4` and `xs_function`
        ```json
        "object_state": {
            "type": "s32",
            "default": -1
        },
        ```

---

## Scenario v1.41

### Added

- Map:
    - Between `script_name` and `collide_and_correct`
      ```json
      "block_humanity_team_change": {
          "type": "u8",
          "default": 0
      },
      ```

---

## Scenario v1.40

### Added

- DataHeader.PlayerDataOneStruct:

    - Between `civilization` and `cty_mode`
      ```json
      "architecture_set": {
        "type": "u32",
        "default": 36
      },
      ```

- Map:

    - Between `map_color_mood` and `collide_and_correct`
      ```json
      "separator_3": {
          "type": "2",
          "default": "600a"
      },
      "script_name": {
          "type": "str16",
          "default": "",
          "dependencies": {
              "on_commit": {
                  "action": "REFRESH",
                  "target": "Files:script_file_path"
              }
          }
      },
      ```
    - Between `villager_force_drop` and `player_1_camera_y`
      ```json
      "unknown": {
          "type": "128",
          "default": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
      },
      ```

- Triggers.trigger.condition:

    - After: `target_player`
      ```json
      "unit_ai_action": {
          "type": "s32",
          "default": -1
      },
      "unknown_4": {
          "type": "s32",
          "default": -1
      },
      "xs_function": {
          "type": "str32",
          "default": ""
      }
      ```

- Triggers.trigger.effect:

    - Between: `play_sound` and `message`
      ```json
      "player_color": {
          "type": "s32",
          "default": -1
      },
      "unknown_4": {
          "type": "s32",
          "default": -1
      },
      ```

- Files:

```json
      "Files": {
        "retrievers": {
            "unknown_2": {
                "type": "4",
                "default": "00000000"
            },
            "script_file_path": {
                "type": "str16",
                "default": null,
                "dependencies": {
                    "on_refresh": {
                        "action": "SET_VALUE",
                        "target": "Map:script_name",
                        "eval": "script_name + ('.xs' if len(script_name) > 0 else '')"
                    }
                }
            },
            "script_file_content": {
                "type": "str32",
                "default": ""
            },
            "ai_files_present": {
                "type": "u32",
                "default": 0,
                "dependencies": {
                    "on_refresh": {
                        "action": "SET_VALUE",
                        "target": "self:number_of_ai_files",
                        "eval": "0 if number_of_ai_files == 0 else 1"
                    }
                }
            },
            "unknown_4": {
                "type": "4",
                "default": "00000000"
            },
            "number_of_ai_files": {
                "type": "u32",
                "default": [],
                "potential_list": false,
                "dependencies": {
                    "on_construct": {
                        "action": "SET_REPEAT",
                        "target": "self:ai_files_present"
                    },
                    "on_refresh": [
                        {
                            "action": "SET_VALUE",
                            "target": "self:ai_files",
                            "eval": "len(ai_files)"
                        },
                        {
                            "action": "SET_REPEAT",
                            "target": "self:ai_files",
                            "eval": "1 if len(ai_files) > 0 else 0"
                        }
                    ],
                    "on_commit": {
                        "action": "REFRESH",
                        "target": "self:ai_files_present"
                    }
                }
            },
            "ai_files": {
                "type": "struct:AI2Struct",
                "default": [],
                "dependencies": {
                    "on_refresh": {
                        "action": "SET_REPEAT",
                        "target": "self:number_of_ai_files",
                        "eval": "number_of_ai_files if number_of_ai_files != [] else 0"
                    },
                    "on_construct": {
                        "action": "REFRESH_SELF"
                    },
                    "on_commit": {
                        "action": "REFRESH",
                        "target": "self:number_of_ai_files"
                    }
                }
            },
            "__END_OF_FILE_MARK__": {
                "type": "1",
                "comment": "Should always be last retriever",
                "default": ""
            }
        },
        "structs": {
            "AI2Struct": {
                "retrievers": {
                    "ai_file_name": {
                        "type": "str32",
                        "default": ""
                    },
                    "ai_file": {
                        "type": "str32",
                        "default": ""
                    }
                }
            }
        }
    }
```

### Removed

- FileHeader:

    - Between `scenario_instructions` and `player_count`
      ```json
      "individual_victories_used": {
        "type": "u32",
        "default": 0
      },
      ```

---

## Scenario v1.37

### Added

- Map:

    - Between `collide_and_correct` and `player_1_camera_y`
      ```json
      "villager_force_drop": {
              "type": "u8",
              "default": 0
          },
      ```

---

## Scenario v1.36

> First DE scenario file version.
