# Install injection and slot-data field

Type: grilling
Status: open
Blocked by: 03, 05

## Question

How does the tier reach the scenario at install? The option-to-slot-data wiring, where the AI and
trigger steps plug into `InstallHandler.steps_for`, how built scripts are attached
(`set_custom_ai` per player), and what `/install` (incremental vs `full`) does with an already
built campaign.

Also from [Does the scenario difficulty touch logic or locations?](06-difficulty-logic-impact.md): install disables the
AP triggers of difficulty-dependent locations absent at the seed's difficulty, alongside
`branching_triggers`, so the client needs the difficulty (or the resolved location list) in slot
data.
