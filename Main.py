from Source import ReadData, CheckData, WriteData, Assign, Addon
import json
import sys
from random import shuffle
from time import time, sleep, strftime
from termcolor import colored

NUM_MIN = True              # 0 if no time straints
SHORT_PRINT = True
SHORT_MIN = 5
NUM_DEL = 10                # number of deleting pair for each step
THRESHOLD = 100             # Threshold for removal

unavails = []
for day in range(5):
    unavails.append((day + 1) * 27 - 1)  # The end of the day
    unavails += list(range(day * 27 + 6, day * 27 + 8))  # Lunch time
    unavails += list(range(day * 27 + 18, day * 27 + 20))  # Dinner time
unavails += list(range(4 * 27 + 16, 5 * 27))  # No Friday afternoon

"""
STAGE 1: DATA PREPARATION
"""
yrsem = "20Spring"
crsDic = ReadData.CourseInfo(yrsem, [], unavails)
stdDic = ReadData.StudentInfo(crsDic, yrsem)
stdDic, crsDic = Assign.OptimizeEnroll(stdDic, crsDic, yrsem)

"""
STAGE 2: OPTIMIZATION
"""

CheckData.InitTT(crsDic)
confPairInst = CheckData.InstPair(crsDic)
confPairStd  = CheckData.StdPair(stdDic, crsDic)
confPair     = CheckData.RemoveDuplicates(confPairInst, confPairStd)
print("Final conflicting pairs...(" + str(len(confPairInst)) + "," + str(len(confPairStd)) + ")")

"""
STAGE 3: INTEGER PROGRAMMING
"""

J = list(range(len(crsDic)))
shuffle(J)

Loc     = 0
mloc    = Loc
ell_sec = True
numConfInst = [0 for _ in range(len(confPairInst))]
numConfStd  = [0 for _ in range(len(confPairStd))]
Dep         = [[0 for _ in range(len(crsDic))] for _ in range(len(crsDic))]

t0     = time()
InitT0 = time()

print("Starting from " + colored(str(Loc), 'red') + "/%d. (%d%% completed)" % (len(crsDic), int(Loc / len(crsDic) * 100)), end=" ")
sys.stdout.flush()

remCount = 0

while Loc < len(J):
    ellapsed = time() - t0
    if SHORT_PRINT:
        if int(ellapsed) % 4 == 0 and ell_sec:
            print(".", end="")
            sys.stdout.flush()
            ell_sec = False
        if int(ellapsed) % 2 == 1:
            ell_sec = True
    else:
        progressbar = str()
        for i in range(int(Loc / 2)):
            progressbar += '-'
        progressbar += str(Loc)
        progressbar = progressbar.ljust(int(mloc / 2))
        progressbar += '*' + str(mloc)
        progressbar = progressbar.ljust(int(len(J) / 2) + 1)
        print("|%s |I[loc]=%d(%d)" % (progressbar, J[Loc], len(confPair)))

    timer = max(SHORT_MIN - remCount, 1)
    if NUM_MIN and ellapsed > 60 * timer:
        print("\nInitializing...", end=" ")
        sleep(1)
        CheckData.RemoveMaxConflictPair(NUM_DEL, THRESHOLD, numConfStd, confPairStd)
        confPair = confPairStd + confPairInst
        numConfStd = [0 for _ in range(len(confPairStd))]
        print("(%d pairs left)" % len(confPair))
        print("Re-starting at " + colored(str(mloc), 'blue') + "/%d. (%d%% completed)" % (len(crsDic), int(Loc / len(J) * 100)), end=" ")
        remCount += 1
        sys.stdout.flush()
        sleep(1)
        t0 = time()
        continue

    Inserted = False
    shuffle(crsDic[J[Loc]]['PossibleTimes'])
    checktimeslot = True
    for timeSlot in crsDic[J[Loc]]['PossibleTimes']:
        if not CheckData.TimeConflict(timeSlot, Loc, crsDic, J, confPair, confPairStd, numConfStd, Dep):
            if not Addon.SpecialRequestSuccess(Loc, J, crsDic, timeSlot):
                continue
            if not crsDic[J[Loc]]['PossibleClassrooms']:
                Inserted = True
            else:
                for room in crsDic[J[Loc]]['PossibleClassrooms']:
                    if not CheckData.RoomConflict(timeSlot, Loc, room, crsDic, J):
                        crsDic[J[Loc]]['Classroom'] = room
                        Inserted = True
                        break
            if Inserted:
                break

    if Inserted:
        crsDic[J[Loc]]['Timetable'] = timeSlot
        Loc += 1

    else:
        if Loc > mloc:
            remCount = 0
            print("\nInserted up to " + colored(str(Loc), 'red') + "/%d. (%d%% completed) %d(sec)" % (len(crsDic), int(Loc / len(crsDic) * 100), int(time() - InitT0)), end=" ")
            sys.stdout.flush()
            mloc = Loc
            numConfStd = [0 for _ in range(len(confPairStd))]
            numConfInst = [0 for _ in range(len(confPairInst))]
            t0 = time()

            with open("Data/" + yrsem + "/Results/" + yrsem + "TimetableTemp.json", "w") as file:
                file.write(json.dumps(crsDic))
            WriteData.ToCSV("Data/" + yrsem + "/Results/" + yrsem + "TimetableTemp.csv", crsDic, yrsem)

        Dep[J[Loc]][Loc] += 1
        bb = Dep[J[Loc]][Loc]
        if bb > Loc:
            Dep[J[Loc]][Loc] = 0
            bb = Loc
        for i in range(Loc - bb, Loc):
            crsDic[J[i]]['Timetable'] = []
            crsDic[J[i]]['Classroom'] = -1
        tempI = J[Loc - bb: Loc]
        J[Loc - bb] = J[Loc]
        J[Loc - bb + 1: Loc + 1] = tempI
        Loc -= bb

DateTime = strftime("%Y%m%d_%H%M")
with open("Data/" + yrsem + "/Results/data_" + yrsem + "_" + DateTime + ".json", "w") as file:
    file.write(json.dumps(crsDic))


print("...The dictionary of timetable is written to " + colored("data_" + yrsem + "_" + DateTime + ".json", 'blue') + "'\n")
WriteData.ToCSV("Data/" + yrsem + "/Results/data_" + yrsem + "_" + DateTime + "_timetable.csv", crsDic, yrsem)
# WriteData.ByCourse("Data/" + yrsem + "/Results/data_" + yrsem + "_" + DateTime + "_course.csv", crsDic, yrsem)
# WriteData.ByInstructors("Data/" + yrsem + "/Results/data_" + yrsem + "_" + DateTime + "_instructors.txt", crsDic)





