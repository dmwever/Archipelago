include "./AP.xs";

void InitScenarioLocations() {
    return;
}

void GiveScenarioItems() {
    return;
}

void SetScenarioAge() {
    SetVanillaAge(IMPERIAL_AGE);
}

void SetPavilionLayout() {
    return;
}

const int AP53_VERSION = 1;
const int AP53_RECORDS = 512;
const int AP53_FIELDS = 8;

const int REC_BOOT = 1;
const int REC_MAKE = 2;
const int REC_SCAN = 3;
const int REC_RESULT = 4;
const int REC_OPEN = 5;
const int REC_DONE = 6;

const int RAM_LEGACY_TYPE = 35;
const int RAM_DE_TYPE = 1258;
const int CAPPED_RAM_TYPE = 422;
const int SIEGE_RAM_TYPE = 548;
const int SIEGE_WORKSHOP_TYPE = 49;

const int CASE_COUNT = 3;
const int CASE_SPAWN_LEGACY = 0;
const int CASE_SPAWN_DE = 1;
const int CASE_TRAIN = 2;

const int SPAWN_WATCH_SECONDS = 8;
const int TRAIN_WATCH_SECONDS = 180;

const int SEEN_CAPACITY = 64;

int ap53Log = -1;
int ap53Count = 0;
int ap53Tick = 0;
int ap53Closed = 0;
int ap53Scan = -1;
int ap53Seen = -1;
int ap53SeenCount = 0;

int caseIndex = 0;
int caseStarted = 0;
int phaseStartSecond = 0;
int caseUnit = -1;
int shopUnit = -1;

int spotX = 0;
int spotZ = 0;

void ap53Write(int recType = 0, int v1 = 0, int v2 = 0, int v3 = 0, int v4 = 0, int v5 = 0) {
    if (ap53Count >= AP53_RECORDS) {
        return;
    }
    int base = ap53Count * AP53_FIELDS;
    xsArraySetInt(ap53Log, base + 0, recType);
    xsArraySetInt(ap53Log, base + 1, ap53Tick);
    xsArraySetInt(ap53Log, base + 2, xsGetGameTime());
    xsArraySetInt(ap53Log, base + 3, v1);
    xsArraySetInt(ap53Log, base + 4, v2);
    xsArraySetInt(ap53Log, base + 5, v3);
    xsArraySetInt(ap53Log, base + 6, v4);
    xsArraySetInt(ap53Log, base + 7, v5);
    ap53Count = ap53Count + 1;
}

bool isRamType(int typeId = -1) {
    if (typeId == RAM_LEGACY_TYPE) {
        return (true);
    }
    if (typeId == RAM_DE_TYPE) {
        return (true);
    }
    if (typeId == CAPPED_RAM_TYPE) {
        return (true);
    }
    if (typeId == SIEGE_RAM_TYPE) {
        return (true);
    }
    return (false);
}

int ap53CopyId(int unitId = -1) {
    if (unitId < 0 || xsDoesUnitExist(unitId) == false) {
        return (-1);
    }
    return (xsGetUnitCopyId(unitId));
}

int ap53ObjectId(int unitId = -1) {
    if (unitId < 0 || xsDoesUnitExist(unitId) == false) {
        return (-1);
    }
    return (xsGetUnitObjectId(unitId));
}

bool isRamUnit(int unitId = -1) {
    if (isRamType(ap53CopyId(unitId))) {
        return (true);
    }
    return (isRamType(ap53ObjectId(unitId)));
}

bool alreadySeen(int unitId = -1) {
    for (i = 0; < SEEN_CAPACITY) {
        if (xsArrayGetInt(ap53Seen, i) == unitId) {
            return (true);
        }
    }
    return (false);
}

void markSeen(int unitId = -1) {
    if (ap53SeenCount >= SEEN_CAPACITY) {
        return;
    }
    xsArraySetInt(ap53Seen, ap53SeenCount, unitId);
    ap53SeenCount = ap53SeenCount + 1;
}

void clearSeen() {
    for (i = 0; < SEEN_CAPACITY) {
        xsArraySetInt(ap53Seen, i, -1);
    }
    ap53SeenCount = 0;
}

void ap53ScanRams(int index = 0) {
    int units = xsGetPlayerUnitIds(1, -1, ap53Scan);
    if (units >= 0) {
        ap53Scan = units;
    }
    int elapsed = xsGetGameTime() - phaseStartSecond;
    for (i = 0; < xsArrayGetSize(ap53Scan)) {
        int unitId = xsArrayGetInt(ap53Scan, i);
        if (unitId < 0 || xsDoesUnitExist(unitId) == false) {
            continue;
        }
        if (isRamUnit(unitId) == false) {
            continue;
        }
        if (alreadySeen(unitId)) {
            continue;
        }
        markSeen(unitId);
        ap53Write(REC_SCAN, index, elapsed, unitId, ap53CopyId(unitId),
                  ap53ObjectId(unitId));
    }
}

void ap53DropRams() {
    int units = xsGetPlayerUnitIds(1, -1, ap53Scan);
    if (units >= 0) {
        ap53Scan = units;
    }
    for (i = 0; < xsArrayGetSize(ap53Scan)) {
        int unitId = xsArrayGetInt(ap53Scan, i);
        if (unitId < 0 || xsDoesUnitExist(unitId) == false) {
            continue;
        }
        if (isRamUnit(unitId)) {
            xsRemoveUnit(unitId);
        }
    }
    clearSeen();
}

void ap53Flush() {
    if (ap53Closed == 1) {
        return;
    }
    ap53Closed = 1;
    bool created = xsCreateFile(false);
    if (created == false) {
        xsChatData("<RED>AP53: could not create the .xsdat file");
        return;
    }
    xsWriteString("AP53");
    xsWriteInt(AP53_VERSION);
    xsWriteInt(AP53_RECORDS);
    for (i = 0; < AP53_RECORDS * AP53_FIELDS) {
        xsWriteInt(xsArrayGetInt(ap53Log, i));
    }
    xsWriteString("END");
    xsWriteInt(ap53Count);
    xsWriteInt(424242);
    xsCloseFile();
    xsChatData("<GREEN>AP53 done, file closed. " + ap53Count
               + " records. Quit the scenario.");
}

void main() {
    ap53Log = xsArrayCreateInt(AP53_RECORDS * AP53_FIELDS, 0, "ap53-log");
    ap53Scan = xsArrayCreateInt(1, -1, "ap53-scan");
    ap53Seen = xsArrayCreateInt(SEEN_CAPACITY, -1, "ap53-seen");

    spotX = xsGetMapWidth() / 2;
    spotZ = xsGetMapHeight() / 2;

    initializeStructsScript();
    InitLocations();
    SetScenarioAge();

    ap53Write(REC_BOOT, apVanillaAge, AP_US_CAVEMAN, AP_TS_MODE, spotX, spotZ);
    xsChatData("<YELLOW>AP53 v1: which genie id is a Battering Ram? vanillaAge="
               + apVanillaAge + " caveman=" + AP_US_CAVEMAN);
    xsEnableRule("AP53Harness");
}

rule AP53Harness
    inactive
    minInterval 1
    maxInterval 1
    group AP53
{
    ap53Tick = ap53Tick + 1;

    if (caseIndex >= CASE_COUNT) {
        ap53Write(REC_DONE, CASE_COUNT, ap53Count, 0, 0, 0);
        ap53Flush();
        xsDisableRule("AP53Harness");
        return;
    }

    if (caseStarted == 0) {
        clearSeen();
        if (caseIndex == CASE_TRAIN) {
            xsEffectAmount(cModResource, cAttributeWood, cAttributeAdd, 5000.0, 1);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, 5000.0, 1);
            shopUnit = xsCreateUnit(SIEGE_WORKSHOP_TYPE, 1,
                                    xsVectorSet(1.0 * spotX, 1.0 * spotZ, 0.0),
                                    false, false, true);
            ap53Write(REC_OPEN, caseIndex, SIEGE_WORKSHOP_TYPE, shopUnit,
                      ap53CopyId(shopUnit), ap53ObjectId(shopUnit));
            xsChatData("<YELLOW>AP53: Siege Workshop placed at the centre. Train rams now - "
                       + TRAIN_WATCH_SECONDS + " seconds.");
        } else {
            int typeId = RAM_LEGACY_TYPE;
            if (caseIndex == CASE_SPAWN_DE) {
                typeId = RAM_DE_TYPE;
            }
            caseUnit = xsCreateUnit(typeId, 1,
                                    xsVectorSet(1.0 * spotX, 1.0 * spotZ, 0.0),
                                    false, false, true);
            ap53Write(REC_MAKE, caseIndex, typeId, caseUnit, ap53CopyId(caseUnit),
                      ap53ObjectId(caseUnit));
            xsChatData("<YELLOW>AP53: spawned type " + typeId + " -> unit " + caseUnit
                       + " copyId " + ap53CopyId(caseUnit)
                       + " objectId " + ap53ObjectId(caseUnit));
        }
        phaseStartSecond = xsGetGameTime();
        caseStarted = 1;
        return;
    }

    ap53ScanRams(caseIndex);

    int window = SPAWN_WATCH_SECONDS;
    if (caseIndex == CASE_TRAIN) {
        window = TRAIN_WATCH_SECONDS;
    }
    int waited = xsGetGameTime() - phaseStartSecond;
    if (waited < window) {
        return;
    }

    ap53Write(REC_RESULT, caseIndex, caseUnit, ap53CopyId(caseUnit),
              ap53ObjectId(caseUnit), ap53SeenCount);
    ap53DropRams();
    if (caseIndex == CASE_TRAIN && shopUnit >= 0 && xsDoesUnitExist(shopUnit)) {
        xsRemoveUnit(shopUnit);
    }
    caseUnit = -1;
    caseStarted = 0;
    caseIndex = caseIndex + 1;
}
