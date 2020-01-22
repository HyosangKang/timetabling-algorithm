
    
def TooManyCourses(Loc, J, CrsInfo, TimeSlot, numstd): # Check density of timeslot
    tl = list(TimeSlot)
    for l in tl:
        tmpLst = [n for n in range(Loc) if CrsInfo[J[n]]['Level'] == CrsInfo[J[Loc]]['Level'] \
                    and CrsInfo[J[n]]['ClassType'] == '공통필수' and l in list(CrsInfo[J[n]]['Timetable'])]
        if len(tmpLst) > 0:
            s = CrsInfo[J[Loc]]['ClassSize']
            for ll in tmpLst:
                s += CrsInfo[J[ll]]['ClassSize']
            if s > numstd:
                return True
    return False
            

def MergeClass(Loc, J, crsDic, timeSlot, lst): # Allocate classes in the same slot
    tmpList = [J[l] for l in list(range(Loc)) if J[l] in lst]
    if tmpList and crsDic[tmpList[0]]['Timetable'] != timeSlot:
        return False
    return True


def SeperateClass(Loc, J, CrsInfo, TimeSlot, lst): # Separate two classes in different DAYS
    day1 = []
    day2 = []
    tmp1 = list(TimeSlot)
    for l in tmp1:
        day1.append(int(l / 27))
    day1 = set(day1)
    tmpList = [J[l] for l in list(range(Loc)) if J[l] in lst]
    if len(tmpList) > 0:
        tmp2 = list(CrsInfo[tmpList[0]]['Timetable'])
        for l in tmp2:
            day2.append(int(l / 27))
        day2 = set(day2)
        if len(day1.intersection(day2)) > 0:
            return False
    return True


def SpecialRequestSuccess(Loc, J, CrsInfo, TimeSlot):   # Process special requests (merge or separate)
    mList = [[16, 17, 18]]
    for lst in mList:
        if J[Loc] in lst:
            return MergeClass(Loc, J, CrsInfo, TimeSlot, lst)

    sList = [[18, 31]]
    for lst in sList:
        if J[Loc] in lst:
            return SeperateClass(Loc, J, CrsInfo, TimeSlot, lst)
    return True
