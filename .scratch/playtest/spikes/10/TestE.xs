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
const int AP10_RECORDS = 1200;
const int AP10_FIELDS = 8;

const int REC_STAGE = 1;
const int REC_RATE = 4;
const int REC_EVENT = 5;
const int REC_PHASE = 8;

const int EV_CAVEMAN_ON = 9;
const int EV_BULK = 10;
const int EV_SWAP = 11;

const int MODE_NORMAL = 0;
const int MODE_FULL = 1;
const int MODE_FETCH = 2;
const int MODE_PROFSWEEP = 3;
const int MODE_FILL = 4;

const int T_KNIGHT = 38;
const int T_VILLAGER = 83;

const int BULK_CAPACITY = 256;
const int WINDOW = 15;

int ap10Log = -1;
int ap10Count = 0;
int ap10Tick = 0;
int ap10Scan = -1;
int ap10Probe = -1;
int ap10Second = -1;
int ap10Closed = 0;

int meterTicks = 0;
int mode = 0;
int ruleEnabled = 1;
int phaseId = 0;

int bulkIds = -1;
int bulkCount = 0;
int swapIndex = 0;
int knightCount = 0;

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

void ap10Bulk(int count = 0) {
    for (n = 0; < count) {
        if (bulkCount >= BULK_CAPACITY) {
            return;
        }
        int created = xsCreateUnit(T_VILLAGER, 1,
                                   ap10Spot(bulkCount % 20, 20 + bulkCount / 20),
                                   false, false, false);
        if (created >= 0) {
            xsArraySetInt(bulkIds, bulkCount, created);
            bulkCount = bulkCount + 1;
        }
    }
    ap10Write(REC_EVENT, EV_BULK, count, bulkCount, 0, 0);
}

void ap10Swap(int count = 0) {
    for (n = 0; < count) {
        if (swapIndex >= bulkCount) {
            return;
        }
        xsRemoveUnit(xsArrayGetInt(bulkIds, swapIndex));
        swapIndex = swapIndex + 1;
        int created = xsCreateUnit(T_KNIGHT, 1,
                                   ap10Spot(-20 + knightCount % 12, 30 + knightCount / 12),
                                   false, false, false);
        if (created >= 0) {
            knightCount = knightCount + 1;
        }
    }
    ap10Write(REC_EVENT, EV_SWAP, swapIndex, knightCount, 0, 0);
}

void ap10SetPhase(int id = 0, int enabled = 0, int newMode = 0) {
    phaseId = id;
    ruleEnabled = enabled;
    mode = newMode;
    if (enabled == 1) {
        xsEnableRule("UnitsanityChecks");
    } else {
        xsDisableRule("UnitsanityChecks");
    }
    ap10Write(REC_PHASE, id, enabled, newMode, xsArrayGetSize(ap10Scan), knightCount);
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
    xsWriteString("AP10E");
    xsWriteInt(AP10_VERSION);
    xsWriteInt(AP10_RECORDS);
    for (i = 0; < AP10_RECORDS * AP10_FIELDS) {
        xsWriteInt(xsArrayGetInt(ap10Log, i));
    }
    xsWriteString("END");
    xsWriteInt(ap10Count);
    xsCloseFile();
    xsChatData("<GREEN>AP10 run E done, file closed. " + ap10Count
               + " records. Quit the scenario.");
}

void ap10Schedule(int second = 0) {
    if (second < 18) {
        return;
    }
    int index = (second - 18) / WINDOW;
    if (index == phaseId - 1) {
        return;
    }
    if (index == 0) {
        ap10SetPhase(1, 1, MODE_NORMAL);
    }
    if (index == 1) {
        ap10SetPhase(2, 1, MODE_FULL);
    }
    if (index == 2) {
        ap10SetPhase(3, 1, MODE_NORMAL);
    }
    if (index == 3) {
        ap10SetPhase(4, 1, MODE_FULL);
    }
    if (index == 4) {
        ap10SetPhase(5, 1, MODE_FILL);
    }
    if (index == 5) {
        ap10SetPhase(6, 1, MODE_NORMAL);
    }
    if (index == 6) {
        ap10SetPhase(7, 1, MODE_FULL);
    }
    if (index == 7) {
        ap10SetPhase(8, 1, MODE_NORMAL);
    }
    if (index == 8) {
        ap10SetPhase(9, 1, MODE_FULL);
    }
    if (index == 9) {
        ap10SetPhase(10, 0, MODE_NORMAL);
    }
    if (index == 10) {
        ap10SetPhase(11, 0, MODE_FETCH);
    }
    if (index == 11) {
        ap10SetPhase(12, 0, MODE_NORMAL);
    }
    if (index == 12) {
        ap10SetPhase(13, 0, MODE_PROFSWEEP);
    }
    if (index == 13) {
        ap10SetPhase(14, 0, MODE_NORMAL);
    }
}

void ap10Boot() {
    ap10Log = xsArrayCreateInt(AP10_RECORDS * AP10_FIELDS, 0, "ap10-log");
    bulkIds = xsArrayCreateInt(BULK_CAPACITY, -1, "ap10-bulk");
    ap10Scan = xsArrayCreateInt(1, -1, "ap10-scan");
    ap10Probe = xsArrayCreateInt(1, -1, "ap10-probe");

    mapCentreX = xsGetMapWidth() / 2;
    mapCentreZ = xsGetMapHeight() / 2;

    initializeStructsScript();
    InitLocations();
    InitBuildsanity();
    InitAges();
    InitTechsanity();
    InitUnitsanity();
    InitProfessions();
    startupGranted = 1;

    xsChatData("<YELLOW>AP10 run E: unitsanity=" + unitsanityReady
               + " professions=" + professionsReady + " rows=" + unitTableCount);
    xsEnableRule("AP10Meter");
    xsEnableRule("AP10Driver");
}

void main() {
    ap10Boot();
}

rule AP10Meter
    inactive
    highFrequency
    group AP10
{
    meterTicks = meterTicks + 1;
    ap10Tick = ap10Tick + 1;
    if (mode == MODE_FULL) {
        unitsDirty = true;
    }
    if (mode == MODE_FETCH) {
        ap10Probe = xsGetPlayerUnitIds(1, -1, ap10Probe);
    }
    if (mode == MODE_PROFSWEEP) {
        ap10Probe = xsGetPlayerUnitIds(1, -1, ap10Probe);
        CheckProfessionLocations(ap10Probe);
    }
}

rule AP10Driver
    inactive
    minInterval 1
    maxInterval 1
    group AP10
{
    int second = xsGetGameTime();
    if (second == ap10Second) {
        return;
    }
    ap10Write(REC_RATE, meterTicks, xsArrayGetSize(xsGetPlayerUnitIds(1, -1, ap10Scan)),
              ruleEnabled, mode, knightCount);
    meterTicks = 0;
    ap10Second = second;
    ap10Write(REC_STAGE, second, ap10Count, phaseId, 0, 0);

    if (second >= 3 && second <= 10) {
        ap10Bulk(25);
    }
    if (second == 11) {
        InitCaveman();
        ap10Write(REC_EVENT, EV_CAVEMAN_ON, 0, 0, 0, 0);
    }

    ap10Schedule(second);

    if (second >= 79 && second <= 84) {
        ap10Swap(25);
    }

    if (second >= 228) {
        ap10Flush();
        xsDisableRule("AP10Meter");
        xsDisableRule("AP10Driver");
    }
}
