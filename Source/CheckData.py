import sys, itertools
from termcolor import colored


def GenerateTimeSlot(crs, availSlots): # The function generates all possible time slots for the course.
    if not availSlots:
        availSlots = crs['AvailableSlots']
    possibleTimes = []
    hour = sum(crs['Credit'])

    if crs['Fixed']: # If the course is hard fixed, only one possible time slot is returned
        possibleTimes = [availSlots]
    elif crs['SoftFixed']:
        for sPair in list(itertools.combinations(crs['AvailableSlots'], len(crs['Credit']))):
            timeSlot = []
            for i, c in enumerate(crs['Credit']):
                timeSlot += list(range(sPair[i], sPair[i] + c))
            timeSlot = list(set(timeSlot))
            timeSlot.sort()
            if len([s for s in timeSlot if s in availSlots]) == hour:
                possibleTimes.append(timeSlot)
    else:
        for slot in availSlots:
            timeSlot = []
            for i, c in enumerate(crs['Credit']):
                s = (slot + (3 * i * 27)) % (5 * 27)
                timeSlot += list(range(s, s + c))
            timeSlot = list(set(timeSlot))
            timeSlot.sort()
            if len([s for s in timeSlot if s in availSlots]) == hour:
                possibleTimes.append(timeSlot)

    return possibleTimes


def InitTT(crsDic): # Write a dictionary for the timetable
    for crs in crsDic:
        crs['PossibleTimes'] = GenerateTimeSlot(crs, [])
        crs['Classroom'] = -1
        crs['Timetable'] = []


def InstPair(crsDic):
    instList = []
    for crs in crsDic:
        instList += crs['Instructors']
    instList = list(set(instList))
    instDic = []
    for inst in instList:
        tmpdict = {
            'Name' : inst,
            'TeachingCourses' : [c for c, crs in enumerate(crsDic) if inst in crs['Instructors']]
        }
        instDic.append(tmpdict)
    # Write a list of conflict pairs of courses due to the same instructor.
    print("Finding conflict pairs by instructors...", end=" ")
    sys.stdout.flush()
    instConfPair = []
    for inst in instDic:
        instConfPair += ConfPairList(inst['TeachingCourses'])
    instConfPair = list(set(instConfPair))
    instConfPairFiltered = instConfPair.copy()
    count = 0
    for pair in instConfPair: # Checking self-contradiction
        badPair = True
        for i in range(2):
            for timeSlot in crsDic[pair[i]]['PossibleTimes']:
                availSlots = [s for s in crsDic[pair[(i + 1) % 2]]['AvailableSlots'] if s not in timeSlot]
                if GenerateTimeSlot(crsDic[pair[(i + 1) % 2]], availSlots):
                    badPair = False
                    break
        if badPair:
            count += 1
            instConfPairFiltered.remove(pair)
            print("The pair " + crsDic[pair[0]]['CourseName'] + " and " + crsDic[pair[1]]['CourseName'] + " has been removed due to self-confliction.")
            print(crsDic[pair[0]])
            print(crsDic[pair[1]])
    print("%d pairs found" % len(instConfPair))
    if count > 0:
        print(colored(str(count), 'blue') + " pairs have been removed due to self-conflict :(")
    return instConfPairFiltered


def ConfPairList(enrList):
    enrList.sort()
    return list(itertools.combinations(enrList, 2))


def StdPair(stdDic, crsDic):
    print("Finding conflict pairs by students...", end=" ")
    sys.stdout.flush()
    confPairStd = []
    for std in stdDic:
        for pair in list(itertools.combinations(std['Enrolled'], 2)):
            if crsDic[pair[0]]['Fixed'] and crsDic[pair[1]]['Fixed']:
                continue
            confPairStd.append(pair)
    confPairStd = list(set(confPairStd))
    print("%d pairs found" % len(confPairStd))
    return confPairStd


def RemoveDuplicates(confPairInst, confPairStd):
    # Remove duplicates
    print("Merge and remove duplicates... ", end=" ")
    sys.stdout.flush()
    dupPairs = [pair for pair in confPairStd if pair in confPairInst]
    for pair in dupPairs:
        confPairStd.remove(pair)
    confPair = confPairStd + confPairInst
    print("%d pairs removed, %d pairs left" % (len(dupPairs), len(confPair)))
    sys.stdout.flush()

    return confPair


def TimeConflict(timeSlot, loc, crsDic, J, confPair, confPairStd, numConfStd, dep): # checks the time conflicts
    for idx in range(loc):
        if crsDic[J[loc]]['Fixed'] and crsDic[J[idx]]['Fixed']:
            return False
        pair = [J[loc], J[idx]]
        pair.sort()
        pair = tuple(pair)
        if [s for s in crsDic[J[idx]]['Timetable'] if s in timeSlot] and pair in confPair:
            if pair in confPairStd and dep[J[loc]][loc] + 1 > loc:
                numConfStd[confPairStd.index(pair)] += 1
            return True
    return False


def RoomConflict(timeSlot, loc, room, crsDic, J): # The function checks the classroom conflict
    if room == -1:
        return False
    for i in range(loc):
        if [s for s in crsDic[J[i]]['Timetable'] if s in timeSlot] and crsDic[J[i]]['Classroom'] == room:
            return True
    return False


def RemoveMaxConflictPair(numb, threshold, numConfStd, confPairStd):
    if threshold < 2:
        print(" Threshold too low...Continue")
        return
    count = 0
    for _ in range(numb):
        maxnum = max(numConfStd)
        if maxnum > threshold:
            count += 1
            i = numConfStd.index(maxnum)
            del numConfStd[i]
            del confPairStd[i]
    print("%d conflicting pairs removed." % count, end=" ")
    if count == 0:
        print("\n...threshold reduced to %d..." % int(threshold * 9 / 10), end=" ")
        RemoveMaxConflictPair(numb, int(threshold * 9 / 10), numConfStd, confPairStd)
    return
