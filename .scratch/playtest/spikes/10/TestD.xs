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

const int T_MILITIA = 74;
const int T_VILLAGER = 83;

const int CHURN_CAPACITY = 64;
const int CHURN_PER_TICK = 2;
const int LOAD_READS = 200;
const int WINDOW = 15;

int ap10Log = -1;
int ap10Count = 0;
int ap10Tick = 0;
int ap10Scan = -1;
int ap10Second = -1;
int ap10Closed = 0;

int meterTicks = 0;
int churnMode = 0;
int loadMode = 0;
int ruleEnabled = 1;
int phaseId = 0;
int loadSink = 0;

int churnIds = -1;
int churnHead = 0;

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
        }
    }
}

void ap10Load() {
    for (n = 0; < LOAD_READS) {
        loadSink = loadSink + structGetInt(getUnit(n % unitTableCount), "owned");
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

void ap10SetPhase(int id = 0, int enabled = 0, int churn = 0, int load = 0) {
    phaseId = id;
    ruleEnabled = enabled;
    churnMode = churn;
    loadMode = load;
    if (enabled == 1) {
        xsEnableRule("UnitsanityChecks");
    } else {
        xsDisableRule("UnitsanityChecks");
    }
    ap10Write(REC_PHASE, id, enabled, churn, xsArrayGetSize(ap10Scan), load);
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
    xsWriteString("AP10D");
    xsWriteInt(AP10_VERSION);
    xsWriteInt(AP10_RECORDS);
    for (i = 0; < AP10_RECORDS * AP10_FIELDS) {
        xsWriteInt(xsArrayGetInt(ap10Log, i));
    }
    xsWriteString("END");
    xsWriteInt(ap10Count);
    xsCloseFile();
    xsChatData("<GREEN>AP10 run D done, file closed. " + ap10Count
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
        ap10SetPhase(1, 0, 1, 0);
    }
    if (index == 1) {
        ap10SetPhase(2, 1, 1, 0);
    }
    if (index == 2) {
        ap10SetPhase(3, 0, 1, 0);
    }
    if (index == 3) {
        ap10SetPhase(4, 1, 1, 0);
    }
    if (index == 4) {
        ap10SetPhase(5, 0, 1, 0);
    }
    if (index == 5) {
        ap10SetPhase(6, 1, 1, 0);
    }
    if (index == 6) {
        ap10SetPhase(7, 0, 0, 0);
    }
    if (index == 7) {
        ap10SetPhase(8, 1, 0, 0);
    }
    if (index == 8) {
        ap10SetPhase(9, 0, 0, 0);
    }
    if (index == 9) {
        ap10SetPhase(10, 1, 0, 0);
    }
    if (index == 10) {
        ap10SetPhase(11, 0, 0, 0);
    }
    if (index == 11) {
        ap10SetPhase(12, 0, 0, 1);
    }
    if (index == 12) {
        ap10SetPhase(13, 0, 0, 0);
    }
    if (index == 13) {
        ap10SetPhase(14, 0, 0, 1);
    }
}

void ap10Boot() {
    ap10Log = xsArrayCreateInt(AP10_RECORDS * AP10_FIELDS, 0, "ap10-log");
    churnIds = xsArrayCreateInt(CHURN_CAPACITY, -1, "ap10-churn");
    ap10Scan = xsArrayCreateInt(1, -1, "ap10-scan");

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

    xsChatData("<YELLOW>AP10 run D: unitsanity=" + unitsanityReady
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
    if (churnMode == 1) {
        ap10Churn();
    }
    if (loadMode == 1) {
        ap10Load();
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
              ruleEnabled, churnMode, loadMode);
    meterTicks = 0;
    ap10Second = second;
    ap10Write(REC_STAGE, second, ap10Count, phaseId, 0, 0);

    if (second >= 3 && second <= 10) {
        ap10Bulk(17);
    }
    if (second == 11) {
        InitCaveman();
        ap10Write(REC_EVENT, EV_CAVEMAN_ON, 0, 0, 0, 0);
    }
    if (second == 12) {
        churnMode = 1;
    }

    ap10Schedule(second);

    if (second >= 228) {
        ap10Flush();
        xsDisableRule("AP10Meter");
        xsDisableRule("AP10Driver");
    }
}
