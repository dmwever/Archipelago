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
    return;
}

void SetPavilionLayout() {
    return;
}

const int AP10_VERSION = 1;
const int AP10_RECORDS = 1000;
const int AP10_FIELDS = 8;
const int AP10_WATCHES = 5;

const int REC_STAGE = 1;
const int REC_WATCH = 2;
const int REC_ROW = 3;
const int REC_RATE = 4;
const int REC_EVENT = 5;

const int EV_CREATE = 1;
const int EV_CONVERT = 2;
const int EV_REMOVE = 3;
const int EV_ITEM = 4;
const int EV_RESEARCH = 5;
const int EV_IMMUNE = 6;
const int EV_CLEAR_ROW = 7;

const int T_KNIGHT = 38;
const int T_SPEARMAN = 93;
const int T_SCOUT = 448;
const int T_SKIRMISHER = 7;
const int T_MANGONEL = 280;
const int T_MILITIA = 74;
const int T_ARCHER = 4;
const int T_VILLAGER = 83;

const int ITEM_ARCHER = 300;
const int TECH_LOOM = 22;

const int AP10_CAVEMAN_REMOVED = 0;

int ap10Log = -1;
int ap10Count = 0;
int ap10Tick = 0;
int ap10Stage = 0;
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

int anchorIds = -1;
int anchorCount = 0;

int mapCentreX = 0;
int mapCentreZ = 0;

int pendingItemTick = -1;

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

void ap10DropAnchor() {
    if (anchorCount < 1) {
        return;
    }
    anchorCount = anchorCount - 1;
    int unitId = xsArrayGetInt(anchorIds, anchorCount);
    xsRemoveUnit(unitId);
    ap10Write(REC_EVENT, EV_REMOVE, unitId, 0, 0, 0);
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
        int sent = 0;
        if (IsScenarioLocationComplete(locationId)) {
            sent = 1;
        }
        if (owned == xsArrayGetInt(rowLastOwned, i) && sent == xsArrayGetInt(rowLastSent, i)) {
            continue;
        }
        xsArraySetInt(rowLastOwned, i, owned);
        xsArraySetInt(rowLastSent, i, sent);
        ap10Write(REC_ROW, typeId, owned, sent, locationId, 0);
    }
}

void ap10ClearRow(int typeId = -1) {
    int index = findUnit(typeId);
    if (index < 0) {
        return;
    }
    structSetInt(getUnit(index), "owned", 0);
    ap10Write(REC_EVENT, EV_CLEAR_ROW, typeId, 0, 0, 0);
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
    xsWriteString("AP10A");
    xsWriteInt(AP10_VERSION);
    xsWriteInt(AP10_RECORDS);
    for (i = 0; < AP10_RECORDS * AP10_FIELDS) {
        xsWriteInt(xsArrayGetInt(ap10Log, i));
    }
    xsWriteString("END");
    xsWriteInt(ap10Count);
    xsCloseFile();
    xsChatData("<GREEN>AP10 run A done, file closed. " + ap10Count
               + " records. Quit the scenario.");
}

void ap10Stage1(int second = 0) {
    if (second == 5) {
        int created = ap10Create(T_KNIGHT, 2, -6, -6);
        ap10SetWatch(0, created);
    }
    if (second == 6) {
        int knight = xsArrayGetInt(watchUnitIds, 0);
        if (knight < 0) {
            return;
        }
        xsSetUnitOwner(knight, 1, false);
        ap10Write(REC_EVENT, EV_CONVERT, knight, T_KNIGHT, 1, 0);
    }
}

void ap10Stage2(int second = 0) {
    if (second == 11) {
        int created = ap10Create(T_SPEARMAN, 2, -8, -6);
        ap10SetWatch(1, created);
    }
    if (second == 12) {
        int spear = xsArrayGetInt(watchUnitIds, 1);
        xsSetUnitOwner(spear, 1, false);
        ap10Write(REC_EVENT, EV_CONVERT, spear, T_SPEARMAN, 1, 0);
        ap10Stage = 2;
    }
}

void ap10Stage3(int second = 0) {
    if (second == 1 || second == 2 || second == 17) {
        ap10AddAnchor(4, 2 + second);
        ap10Write(REC_EVENT, EV_CREATE, T_VILLAGER, 1, anchorCount, 0);
    }
    if (second >= 18 && second <= 26) {
        ap10AddAnchor(4 + second - 18, 6);
        ap10AddAnchor(4 + second - 18, 8);
    }
    if (second == 20) {
        int created = ap10Create(T_SCOUT, 2, -10, -6);
        ap10SetWatch(2, created);
    }
    if (second == 21) {
        int scout = xsArrayGetInt(watchUnitIds, 2);
        xsSetUnitOwner(scout, 1, false);
        ap10Write(REC_EVENT, EV_CONVERT, scout, T_SCOUT, 1, 0);
    }
}

void ap10Stage4(int second = 0) {
    if (second == 28) {
        int created = ap10Create(T_SKIRMISHER, 2, -12, -6);
        ap10SetWatch(3, created);
    }
    if (second == 29) {
        int skirmisher = xsArrayGetInt(watchUnitIds, 3);
        xsSetUnitOwner(skirmisher, 1, false);
        ap10Write(REC_EVENT, EV_CONVERT, skirmisher, T_SKIRMISHER, 1, 0);
        ap10DropAnchor();
    }
}

void ap10Stage5(int second = 0) {
    if (second == 34) {
        int created = ap10Create(T_MANGONEL, 1, -14, -6);
        MarkUnitCavemanImmune(created);
        ap10Write(REC_EVENT, EV_IMMUNE, created, T_MANGONEL, 0, 0);
        ap10SetWatch(4, created);
    }
}

void ap10Stage6(int second = 0) {
    if (second == 41) {
        ap10ClearRow(T_MILITIA);
    }
    if (second == 42) {
        bool researched = xsResearchTechnology(TECH_LOOM, true, true, 1);
        int flag = 0;
        if (researched) {
            flag = 1;
        }
        ap10Write(REC_EVENT, EV_RESEARCH, TECH_LOOM, flag, 0, 0);
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
    InitUnitsanity();
    InitCaveman();
    InitProfessions();
    startupGranted = 1;

    ap10AddRow(T_KNIGHT);
    ap10AddRow(T_SPEARMAN);
    ap10AddRow(T_SCOUT);
    ap10AddRow(T_SKIRMISHER);
    ap10AddRow(T_MANGONEL);
    ap10AddRow(T_MILITIA);
    ap10AddRow(T_ARCHER);
    ap10AddRow(T_VILLAGER);

    xsChatData("<YELLOW>AP10 run A: unitsanity=" + unitsanityReady
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
    }
    ap10SampleRows();

    if (pendingItemTick >= 0 && ap10Tick >= pendingItemTick) {
        pendingItemTick = -1;
        ap10Stage = 3;
        UnlockUnitItem(ITEM_ARCHER);
        ap10Write(REC_EVENT, EV_ITEM, ITEM_ARCHER, T_ARCHER, 0, 0);
    }
    if (ap10Stage == 2 && pendingItemTick < 0
            && originalTypeOf(xsArrayGetInt(watchUnitIds, 1)) == AP10_CAVEMAN_REMOVED) {
        pendingItemTick = ap10Tick + 1;
    }

    ap10TicksThisSecond = ap10TicksThisSecond + 1;
    if (second != ap10Second) {
        if (ap10Second >= 0) {
            int militia = xsGetPlayerUnitIds(1, T_MILITIA);
            ap10Write(REC_RATE, ap10TicksThisSecond, xsArrayGetSize(ap10Scan),
                      xsArrayGetSize(militia), anchorCount, ap10Count);
        }
        ap10Second = second;
        ap10TicksThisSecond = 0;

        ap10Write(REC_STAGE, second, ap10Count, 0, 0, 0);
        ap10Stage1(second);
        ap10Stage2(second);
        ap10Stage3(second);
        ap10Stage4(second);
        ap10Stage5(second);
        ap10Stage6(second);

        if (second >= 47) {
            ap10Flush();
            xsDisableRule("AP10Harness");
        }
    }
}
