include "./AP.xs";

void CavemanExemption() {
    return;
}

void InitScenarioLocations() {
    return;
}

void GiveScenarioItems() {
    return;
}

void SetScenarioAge() {
    SetVanillaAge(DARK_AGE);
    SetMaxAge(IMPERIAL_AGE);
}

void SetPavilionLayout() {
    return;
}

const int AP10_VERSION = 1;
const int AP10_RECORDS = 1000;
const int AP10_FIELDS = 8;
const int AP10_WATCHES = 4;

const int REC_STAGE = 1;
const int REC_WATCH = 2;
const int REC_ROW = 3;
const int REC_RATE = 4;
const int REC_EVENT = 5;
const int REC_GATE = 6;
const int REC_COUNTS = 7;

const int EV_CREATE = 1;
const int EV_CONVERT = 2;
const int EV_REMOVE = 3;
const int EV_ITEM = 4;
const int EV_TECH = 8;

const int T_MILITIA = 74;
const int T_MAN_AT_ARMS = 75;
const int T_LONG_SWORDSMAN = 77;
const int T_SHEPHERD = 592;
const int T_VILLAGER = 83;

const int ITEM_MILITIA_LINE = 315;
const int ITEM_SHEPHERD = 710;
const int ITEM_MAN_AT_ARMS = 3673;
const int ITEM_LONG_SWORDSMAN = 3663;

const int AP10_CAVEMAN_REMOVED = 0;

int ap10Log = -1;
int ap10Count = 0;
int ap10Tick = 0;
int ap10Scan = -1;
int ap10Second = -1;
int ap10TicksThisSecond = 0;
int ap10Closed = 0;

int watchUnitIds = -1;
int watchLastObject = -1;
int watchLastOriginal = -1;
int watchLastState = -1;

int rowTypes = -1;
int rowLastOwned = -1;
int rowLastSent = -1;
int rowCount = 0;

int lastGate = -1;
int lastMilitia = -1;
int lastManAtArms = -1;
int lastLongSwordsman = -1;
int lastShepherds = -1;
int lastVillagers = -1;

int anchorIds = -1;
int anchorCount = 0;
int churnId = -1;

int mapCentreX = 0;
int mapCentreZ = 0;

void ap10Write(int recType = 0, int v1 = 0, int v2 = 0, int v3 = 0, int v4 = 0, int v5 = 0) {
    if (ap10Count >= AP10_RECORDS) {
        return;
    }
    int base = ap10Count * AP10_FIELDS;
    xsArraySetInt(ap10Log, base + 0, recType);
    xsArraySetInt(ap10Log, base + 1, ap10Tick);
    xsArraySetInt(ap10Log, base + 2, xsGetGameTime());
    xsArraySetInt(ap10Log, base + 3, v1);
    xsArraySetInt(ap10Log, base + 4, v2);
    xsArraySetInt(ap10Log, base + 5, v3);
    xsArraySetInt(ap10Log, base + 6, v4);
    xsArraySetInt(ap10Log, base + 7, v5);
    ap10Count = ap10Count + 1;
}

vector ap10Spot(int column = 0, int row = 0) {
    float x = 1.0 * (mapCentreX + column);
    float z = 1.0 * (mapCentreZ + row);
    return (xsVectorSet(x, 0.0, z));
}

int ap10Create(int typeId = -1, int playerId = 1, int column = 0, int row = 0) {
    int created = xsCreateUnit(typeId, playerId, ap10Spot(column, row), false, false, false);
    int owner = playerId;
    if (created < 0 && playerId != 1) {
        owner = 1;
        created = xsCreateUnit(typeId, 1, ap10Spot(column, row), false, false, false);
    }
    ap10Write(REC_EVENT, EV_CREATE, typeId, owner, created, 0);
    return (created);
}

void ap10AddAnchor(int column = 0, int row = 0) {
    if (anchorCount >= 128) {
        return;
    }
    int created = xsCreateUnit(T_VILLAGER, 1, ap10Spot(column, row), false, false, false);
    if (created < 0) {
        return;
    }
    xsArraySetInt(anchorIds, anchorCount, created);
    anchorCount = anchorCount + 1;
}

void ap10SetWatch(int slot = -1, int unitId = -1) {
    if (slot < 0 || slot >= AP10_WATCHES) {
        return;
    }
    xsArraySetInt(watchUnitIds, slot, unitId);
    xsArraySetInt(watchLastObject, slot, -2);
    xsArraySetInt(watchLastOriginal, slot, -2);
    xsArraySetInt(watchLastState, slot, -2);
}

void ap10AddRow(int typeId = -1) {
    if (rowCount >= 16) {
        return;
    }
    xsArraySetInt(rowTypes, rowCount, typeId);
    xsArraySetInt(rowLastOwned, rowCount, -1);
    xsArraySetInt(rowLastSent, rowCount, -1);
    rowCount = rowCount + 1;
}

void ap10SampleWatches(int units = -1) {
    for (slot = 0; < AP10_WATCHES) {
        int unitId = xsArrayGetInt(watchUnitIds, slot);
        if (unitId < 0) {
            continue;
        }
        int objectId = xsGetUnitObjectId(unitId);
        int original = originalTypeOf(unitId);
        int state = 0;
        if (xsDoesUnitExist(unitId)) {
            state = state + 1;
        }
        if (isUnitListed(units, unitId)) {
            state = state + 2;
        }
        if (IsUnitUntracked(unitId)) {
            state = state + 4;
        }
        if (objectId == xsArrayGetInt(watchLastObject, slot)
                && original == xsArrayGetInt(watchLastOriginal, slot)
                && state == xsArrayGetInt(watchLastState, slot)) {
            continue;
        }
        xsArraySetInt(watchLastObject, slot, objectId);
        xsArraySetInt(watchLastOriginal, slot, original);
        xsArraySetInt(watchLastState, slot, state);
        ap10Write(REC_WATCH, slot, unitId, objectId, original, state);
    }
}

void ap10SampleRows() {
    for (i = 0; < rowCount) {
        int typeId = xsArrayGetInt(rowTypes, i);
        int index = findUnit(typeId);
        if (index < 0) {
            continue;
        }
        vector unit = getUnit(index);
        int owned = structGetInt(unit, "owned");
        int locationId = structGetInt(unit, "locationId");
        int locked = 0;
        if (structGetBool(unit, "locked")) {
            locked = 1;
        }
        int sent = 0;
        if (IsScenarioLocationComplete(locationId)) {
            sent = 1;
        }
        if (owned == xsArrayGetInt(rowLastOwned, i) && sent == xsArrayGetInt(rowLastSent, i)) {
            continue;
        }
        xsArraySetInt(rowLastOwned, i, owned);
        xsArraySetInt(rowLastSent, i, sent);
        ap10Write(REC_ROW, typeId, owned, sent, locationId, locked);
    }
}

void ap10SampleGate(int units = -1) {
    int gate = 0;
    if (anyUnitWithLockedProfession(units)) {
        gate = 1;
    }
    if (gate == lastGate) {
        return;
    }
    lastGate = gate;
    int ready = 0;
    if (professionsReady) {
        ready = 1;
    }
    ap10Write(REC_GATE, gate, ready, 0, 0, 0);
}

void ap10SampleCounts() {
    int militia = xsArrayGetSize(xsGetPlayerUnitIds(1, T_MILITIA));
    int manAtArms = xsArrayGetSize(xsGetPlayerUnitIds(1, T_MAN_AT_ARMS));
    int longSwordsman = xsArrayGetSize(xsGetPlayerUnitIds(1, T_LONG_SWORDSMAN));
    int shepherds = xsArrayGetSize(xsGetPlayerUnitIds(1, T_SHEPHERD));
    int villagers = xsArrayGetSize(xsGetPlayerUnitIds(1, T_VILLAGER));
    if (militia == lastMilitia && manAtArms == lastManAtArms
            && longSwordsman == lastLongSwordsman && shepherds == lastShepherds
            && villagers == lastVillagers) {
        return;
    }
    lastMilitia = militia;
    lastManAtArms = manAtArms;
    lastLongSwordsman = longSwordsman;
    lastShepherds = shepherds;
    lastVillagers = villagers;
    ap10Write(REC_COUNTS, militia, manAtArms, longSwordsman, shepherds, villagers);
}

void ap10Flush() {
    if (ap10Closed == 1) {
        return;
    }
    ap10Closed = 1;
    bool created = xsCreateFile(false);
    if (created == false) {
        xsChatData("<RED>AP10: could not create the .xsdat file");
        return;
    }
    xsWriteString("AP10B");
    xsWriteInt(AP10_VERSION);
    xsWriteInt(AP10_RECORDS);
    for (i = 0; < AP10_RECORDS * AP10_FIELDS) {
        xsWriteInt(xsArrayGetInt(ap10Log, i));
    }
    xsWriteString("END");
    xsWriteInt(ap10Count);
    xsCloseFile();
    xsChatData("<GREEN>AP10 run B done, file closed. " + ap10Count
               + " records. Quit the scenario.");
}

void ap10ClimbStage(int second = 0) {
    if (second == 5) {
        int created = ap10Create(T_LONG_SWORDSMAN, 1, -6, -6);
        ap10SetWatch(1, created);
    }
    if (second == 10) {
        UnlockUnitItem(ITEM_MILITIA_LINE);
        ap10Write(REC_EVENT, EV_ITEM, ITEM_MILITIA_LINE, T_MILITIA, 0, 0);
    }
    if (second == 14) {
        UnlockTech(ITEM_MAN_AT_ARMS - TECH_ITEM_OFFSET);
        ap10Write(REC_EVENT, EV_TECH, ITEM_MAN_AT_ARMS, T_MAN_AT_ARMS, 0, 0);
    }
    if (second == 18) {
        UnlockTech(ITEM_LONG_SWORDSMAN - TECH_ITEM_OFFSET);
        ap10Write(REC_EVENT, EV_TECH, ITEM_LONG_SWORDSMAN, T_LONG_SWORDSMAN, 0, 0);
    }
}

void ap10ShepherdStage(int second = 0) {
    if (second == 28) {
        int created = ap10Create(T_SHEPHERD, 2, -8, -6);
        ap10SetWatch(0, created);
    }
    if (second == 29) {
        int shepherd = xsArrayGetInt(watchUnitIds, 0);
        if (shepherd < 0) {
            return;
        }
        xsSetUnitOwner(shepherd, 1, false);
        ap10Write(REC_EVENT, EV_CONVERT, shepherd, T_SHEPHERD, 1, 0);
    }
}

void ap10GateStage(int second = 0) {
    if (second < 34 || second > 42) {
        return;
    }
    ap10AddAnchor(4 + second - 34, 6);
    ap10AddAnchor(4 + second - 34, 8);
    if (churnId >= 0) {
        xsRemoveUnit(churnId);
        ap10Write(REC_EVENT, EV_REMOVE, churnId, 0, 0, 0);
    }
    churnId = xsCreateUnit(T_MILITIA, 1, ap10Spot(-4, 10), false, false, false);
}

void ap10HeldProfessionStage(int second = 0) {
    if (second == 44) {
        UnlockUnitItem(ITEM_SHEPHERD);
        ap10Write(REC_EVENT, EV_ITEM, ITEM_SHEPHERD, T_SHEPHERD, 0, 0);
    }
    if (second == 46) {
        int created = ap10Create(T_SHEPHERD, 1, -10, -6);
        ap10SetWatch(2, created);
    }
}

void ap10Boot() {
    ap10Log = xsArrayCreateInt(AP10_RECORDS * AP10_FIELDS, 0, "ap10-log");
    watchUnitIds = xsArrayCreateInt(AP10_WATCHES, -1, "ap10-watch-id");
    watchLastObject = xsArrayCreateInt(AP10_WATCHES, -2, "ap10-watch-obj");
    watchLastOriginal = xsArrayCreateInt(AP10_WATCHES, -2, "ap10-watch-orig");
    watchLastState = xsArrayCreateInt(AP10_WATCHES, -2, "ap10-watch-state");
    rowTypes = xsArrayCreateInt(16, -1, "ap10-row-type");
    rowLastOwned = xsArrayCreateInt(16, -1, "ap10-row-owned");
    rowLastSent = xsArrayCreateInt(16, -1, "ap10-row-sent");
    anchorIds = xsArrayCreateInt(128, -1, "ap10-anchor");
    ap10Scan = xsArrayCreateInt(1, -1, "ap10-scan");

    mapCentreX = xsGetMapWidth() / 2;
    mapCentreZ = xsGetMapHeight() / 2;

    initializeStructsScript();
    InitLocations();
    InitBuildsanity();
    InitAges();
    InitTechsanity();
    InitUnitsanity();
    InitCaveman();
    InitProfessions();
    startupGranted = 1;

    ap10AddRow(T_MILITIA);
    ap10AddRow(T_MAN_AT_ARMS);
    ap10AddRow(T_LONG_SWORDSMAN);
    ap10AddRow(T_SHEPHERD);
    ap10AddRow(T_VILLAGER);

    xsChatData("<YELLOW>AP10 run B: unitsanity=" + unitsanityReady
               + " caveman=" + cavemanReady + " professions=" + professionsReady
               + " rows=" + unitTableCount);
    xsEnableRule("AP10Harness");
}

void main() {
    ap10Boot();
}

rule AP10Harness
    inactive
    highFrequency
    group AP10
{
    ap10Tick = ap10Tick + 1;
    int second = xsGetGameTime();

    int units = xsGetPlayerUnitIds(1, -1, ap10Scan);
    if (units >= 0) {
        ap10Scan = units;
        ap10SampleWatches(units);
        ap10SampleGate(units);
    }
    ap10SampleRows();
    ap10SampleCounts();

    ap10TicksThisSecond = ap10TicksThisSecond + 1;
    if (second != ap10Second) {
        if (ap10Second >= 0) {
            ap10Write(REC_RATE, ap10TicksThisSecond, xsArrayGetSize(ap10Scan),
                      anchorCount, ap10Count, 0);
        }
        ap10Second = second;
        ap10TicksThisSecond = 0;

        ap10Write(REC_STAGE, second, ap10Count, 0, 0, 0);
        if (second == 1 || second == 2) {
            ap10AddAnchor(4, 2 + second);
        }
        ap10ClimbStage(second);
        ap10ShepherdStage(second);
        ap10GateStage(second);
        ap10HeldProfessionStage(second);

        if (second >= 52) {
            ap10Flush();
            xsDisableRule("AP10Harness");
        }
    }
}
