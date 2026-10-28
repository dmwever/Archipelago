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

const int REC_STAGE = 1;
const int REC_ROW = 3;
const int REC_RATE = 4;
const int REC_EVENT = 5;
const int REC_PHASE = 8;

const int EV_CREATE = 1;
const int EV_REMOVE = 3;
const int EV_CAVEMAN_ON = 9;
const int EV_BULK = 10;

const int T_MILITIA = 74;
const int T_VILLAGER = 83;

const int PROBE_COUNT = 8;
const int CHURN_CAPACITY = 64;
const int CHURN_PER_TICK = 2;

int ap10Log = -1;
int ap10Count = 0;
int ap10Tick = 0;
int ap10Scan = -1;
int ap10Second = -1;
int ap10Closed = 0;

int meterTicks = 0;
int watchMode = 1;
int churnMode = 0;
int ruleEnabled = 1;

int probeTypes = -1;
int rowTypes = -1;
int rowLastOwned = -1;
int rowCount = 0;

int churnIds = -1;
int churnHead = 0;
int churnFilled = 0;

int bulkCount = 0;
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

void ap10AddRow(int typeId = -1) {
    if (rowCount >= 16) {
        return;
    }
    xsArraySetInt(rowTypes, rowCount, typeId);
    xsArraySetInt(rowLastOwned, rowCount, -1);
    rowCount = rowCount + 1;
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
        if (owned == xsArrayGetInt(rowLastOwned, i)) {
            continue;
        }
        xsArraySetInt(rowLastOwned, i, owned);
        ap10Write(REC_ROW, typeId, owned, structGetInt(unit, "locationId"), meterTicks, 0);
    }
}

void ap10Churn() {
    for (n = 0; < CHURN_PER_TICK) {
        int oldId = xsArrayGetInt(churnIds, churnHead);
        if (oldId >= 0) {
            xsRemoveUnit(oldId);
        }
        int created = xsCreateUnit(T_MILITIA, 1, ap10Spot(-18 + churnHead % 8, 14), false,
                                   false, false);
        xsArraySetInt(churnIds, churnHead, created);
        churnHead = churnHead + 1;
        if (churnHead >= CHURN_CAPACITY) {
            churnHead = 0;
            churnFilled = 1;
        }
    }
}

void ap10Bulk(int count = 0) {
    for (n = 0; < count) {
        int created = xsCreateUnit(T_VILLAGER, 1,
                                   ap10Spot(bulkCount % 20, 20 + bulkCount / 20),
                                   false, false, false);
        if (created >= 0) {
            bulkCount = bulkCount + 1;
        }
    }
    ap10Write(REC_EVENT, EV_BULK, count, bulkCount, 0, 0);
}

void ap10Probe(int second = 0) {
    int index = (second - 6) / 2;
    if (index < 0 || index >= PROBE_COUNT) {
        return;
    }
    int typeId = xsArrayGetInt(probeTypes, index);
    int created = xsCreateUnit(typeId, 1, ap10Spot(-16, -6 - index), false, false, false);
    ap10Write(REC_EVENT, EV_CREATE, typeId, created, meterTicks, index);
}

void ap10SetPhase(int phaseId = 0, int enabled = 0, int churn = 0) {
    ruleEnabled = enabled;
    churnMode = churn;
    if (enabled == 1) {
        xsEnableRule("UnitsanityChecks");
    } else {
        xsDisableRule("UnitsanityChecks");
    }
    ap10Write(REC_PHASE, phaseId, enabled, churn, xsArrayGetSize(ap10Scan), 0);
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
    xsWriteString("AP10C");
    xsWriteInt(AP10_VERSION);
    xsWriteInt(AP10_RECORDS);
    for (i = 0; < AP10_RECORDS * AP10_FIELDS) {
        xsWriteInt(xsArrayGetInt(ap10Log, i));
    }
    xsWriteString("END");
    xsWriteInt(ap10Count);
    xsCloseFile();
    xsChatData("<GREEN>AP10 run C done, file closed. " + ap10Count
               + " records. Quit the scenario.");
}

void ap10Boot() {
    ap10Log = xsArrayCreateInt(AP10_RECORDS * AP10_FIELDS, 0, "ap10-log");
    rowTypes = xsArrayCreateInt(16, -1, "ap10-row-type");
    rowLastOwned = xsArrayCreateInt(16, -1, "ap10-row-owned");
    churnIds = xsArrayCreateInt(CHURN_CAPACITY, -1, "ap10-churn");
    probeTypes = xsArrayCreateInt(PROBE_COUNT, -1, "ap10-probe");
    ap10Scan = xsArrayCreateInt(1, -1, "ap10-scan");

    xsArraySetInt(probeTypes, 0, 38);
    xsArraySetInt(probeTypes, 1, 93);
    xsArraySetInt(probeTypes, 2, 448);
    xsArraySetInt(probeTypes, 3, 7);
    xsArraySetInt(probeTypes, 4, 280);
    xsArraySetInt(probeTypes, 5, 128);
    xsArraySetInt(probeTypes, 6, 279);
    xsArraySetInt(probeTypes, 7, 281);

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

    for (i = 0; < PROBE_COUNT) {
        ap10AddRow(xsArrayGetInt(probeTypes, i));
    }

    xsChatData("<YELLOW>AP10 run C: unitsanity=" + unitsanityReady
               + " caveman=" + cavemanReady + " professions=" + professionsReady
               + " rows=" + unitTableCount);
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
    if (churnMode == 1) {
        ap10Churn();
    }
    if (watchMode == 1) {
        ap10SampleRows();
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
              ruleEnabled, churnMode, watchMode);
    meterTicks = 0;
    ap10Second = second;
    ap10Write(REC_STAGE, second, ap10Count, 0, 0, 0);

    if (second >= 5 && second <= 20) {
        ap10Bulk(3);
        ap10Probe(second);
    }

    if (second >= 22 && second <= 28) {
        ap10Bulk(26);
    }

    if (second == 30) {
        InitCaveman();
        ap10Write(REC_EVENT, EV_CAVEMAN_ON, 0, 0, 0, 0);
    }
    if (second == 32) {
        watchMode = 0;
    }

    if (second == 34) {
        ap10SetPhase(1, 0, 0);
    }
    if (second == 44) {
        ap10SetPhase(2, 1, 0);
    }
    if (second == 54) {
        ap10SetPhase(3, 0, 1);
    }
    if (second == 64) {
        ap10SetPhase(4, 1, 1);
    }
    if (second == 74) {
        ap10SetPhase(5, 0, 0);
    }
    if (second == 84) {
        ap10SetPhase(6, 1, 0);
    }

    if (second >= 94) {
        ap10Flush();
        xsDisableRule("AP10Meter");
        xsDisableRule("AP10Driver");
    }
}
