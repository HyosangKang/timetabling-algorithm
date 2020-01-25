import json

def find_time(slot):
    if int(slot / 27) < 1:
        tmp = "Mon-"
    elif int(slot / 27) < 2:
        tmp = "Tue-"
    elif int(slot / 27) < 3:
        tmp = "Wed-"
    elif int(slot / 27) < 4:
        tmp = "Thr-"
    else:
        tmp = "Fri-"
    tmp += str(9 + int((slot % 27) / 2)) + ":"
    if (slot % 27) % 2:
        tmp += "30"
    else:
        tmp += "00"
    return tmp


def ToCSV(WRITE_FILE_NAME, TTdic, yrsem):
    ClsRm = []
    with open("Data/" + yrsem + "/ClassRoom.csv", 'r') as classroom_file:
        lines = classroom_file.readlines()
        for line in lines[1:]:
            v = line.split(",")
            ClsRm.append(v[1].replace("\n", ""))

    TT = []
    for dic in TTdic:
        tmp = [0 for _ in range(len(TTdic))]
        for j in dic['Timetable']:
            tmp[j] = 1
        TT.append(tmp)
    NUM_CRS = len(TTdic)
    with open(WRITE_FILE_NAME, "w") as file:
        for year in range(1, 5):
            file.write("Timetable for grade " + str(year) + "\n")
            tmpTT = TT[:]
            for i in range(NUM_CRS):
                if TTdic[i]['Level'] != year:
                    tmpTT[i] = [0 for _ in range(5 * 27)]
            prevList = [-1 for _ in range(NUM_CRS)]
            currList = [-1 for _ in range(NUM_CRS)]
            for j in range(5 * 27):
                prevList = currList
                currList = [-1 for _ in range(NUM_CRS)]
                tmp = str()
                tmplist = []
                for i in range(NUM_CRS):
                    if tmpTT[i][j] == 1:
                        tmplist.append(i)
                for i in tmplist:
                    if i in prevList:
                        currList[prevList.index(i)] = i
                for i in tmplist:
                    if i not in prevList:
                        currList[currList.index(-1)] = i
                mloc = 0
                for i in range(NUM_CRS):
                    if currList[i] != -1:
                        mloc = i + 1
                tmp = find_time(j)
                tmp += "~" + str(9 + int((j % 27) / 2)) + ":"
                if (j % 27) % 2:
                    tmp += "00"
                else:
                    tmp += "30"
                for i1 in range(mloc):
                    if currList[i1] == -1:
                        tmp += ","
                    else:
                        tmp += "," + TTdic[currList[i1]]['CourseName'] + "(" + TTdic[currList[i1]]['ClassCode'] + ") " \
                               + "Sect " + str(TTdic[currList[i1]]['Section']) + " " + ClsRm[TTdic[currList[i1]]['Classroom']]
                        for name in TTdic[currList[i1]]['Instructors']:
                            if name[0] not in "0123456789":
                                tmp += " " + name
                file.write(tmp + "\n")


def Slot2Str(slotlst):
    lst = str()
    st = slotlst[0]
    for i in range(len(slotlst)):
        slot = slotlst[i]
        if slot+1 not in slotlst:
            end = find_time(slot+1)
            end = end.split("-")
            lst += find_time(st) + "~" + end[1] + " "
            if i < len(slotlst) - 1:
                st = slotlst[i+1]
    return lst


def FindDayTime(strlst):
    retstr = []
    daystr = "CMN44."
    tt = strlst.split("요일")
    d = tt[0]
    if d == "월":
        retstr.append(daystr + "1")
    elif d == "화":
        retstr.append(daystr + "2")
    elif d == "수":
        retstr.append(daystr + "3")
    elif d == "목":
        retstr.append(daystr + "4")
    else:
        retstr.append(daystr + "5")
    tt1 = tt[1].split("~")
    for i in range(2):
        k = tt1[i]
        kt = k.split(":")
        h = int(kt[0])
        if kt[1] == "00":
            slot = 2*(h-9)
        else:
            slot = 2*(h-9) + 1
        if i == 0:
            retstr.append("UCS05." + str(slot + 2).zfill(2))
        else:
            retstr.append("UCS05." + str(slot + 1).zfill(2))

    return retstr


def ByCourse(FILE_NAME_COURSE, TTdic, yrsem):
    ClsRm = []
    with open("../Data/" + yrsem + "/ClassRoom.csv", 'r') as classroom_file:
        lines = classroom_file.readlines()
        for line in lines[1:]:
            v = line.split(",")
            ClsRm.append(v[1].replace("\n", ""))

    for crs in TTdic:
        if not crs['Timetable']:
            print(crs['CourseName'], end="")
            print(crs['Timetable'])
    with open(FILE_NAME_COURSE, "w") as File:
        File.write("학년도, 학기, 조직분류, 교과목명, 교과목번호, 분반, 요일, 시작교시, 종료교시, 건물, 호실, 시간, 교수자\n")
        for CrsNum in range(len(TTdic)):
            line = "2020, CMN17.10, CMN12.03, " + TTdic[CrsNum]['CourseName'] + ", " + TTdic[CrsNum]['ClassCode'] + ", " + str(TTdic[CrsNum]['Section'])
            InstLst = str()
            for Name in TTdic[CrsNum]['Instructors']:
                if Name[0] not in "0123456789":
                    InstLst += Name + " "
            TTdic[CrsNum]['Timetable'].sort()
            ttLst = Slot2Str(TTdic[CrsNum]['Timetable'])
            rm = ClsRm[TTdic[CrsNum]['Classroom']].split("-")
            ttItm = ttLst.split()
            for tt in ttItm:
                keys = FindDayTime(tt)
                File.write(line + ", " + keys[0] + ", " + keys[1] + ", " + keys[2] + "," + rm[0] + "," + rm[1] + "," + tt + ", " + InstLst + "\n")


def ByClassRoom(FILE_NAME_CLASSROOM, TTdic, ):
    with open(FILE_NAME_CLASSROOM, "w") as File:
        for ClsRm in Classrooms:
            File.write("Classroom " + ClsRm + "\n")
            for Slot in range(5 * 27):
                File.write(find_time(Slot))
                for CrsDic in TTdic:
                    if Slot in CrsDic['Timetable'] and ClsRm in CrsDic['Classroom']:
                        InstLst = str()
                        for Name in CrsDic['Instructors']:
                            if Name[0] not in "012":
                                InstLst += Name + " "
                        File.write(" " + CrsDic['CourseName'] + "(" + InstLst[:-1] + ")")
                File.write("\n")
            File.write("\n")


def ByInstructors(FILE_NAME_INST, TTdic):
    InstLst = []
    for crs in TTdic:
        tmplst = []
        for inst in crs['Instructors']:
            if inst[0] not in "0123456789":
                tmplst.append(inst)
        InstLst += tmplst
    InstLst = list(set(InstLst))
    InstLst.sort()
    with open(FILE_NAME_INST, "w") as File:
        for inst in InstLst:
            File.write(inst + "\n")
            for crs in TTdic:
                if inst in crs['Instructors']:
                    File.write("\t" + crs['CourseName'] + str(crs['Section']) + "\n")
                    File.write("\t\t" + " " + Slot2Str(crs['Timetable']) + "\n")

# yrsem = "20Spring"
# FILE_NAME = "data_20Spring_20200124_1304"
# with open("../Data/20Spring/Results/" + FILE_NAME + ".json", 'r') as file:
#     TT = json.load(file)
#     ToCSV("../Data/" + yrsem + "/Results/" + FILE_NAME + "_timetable.csv", TT, yrsem)
    # ByCourse("../Data/" + yrsem + "/Results/" + FILE_NAME + "_course.csv", TT, yrsem)
    # ByInstructors("../Data/" + yrsem + "/Results/" + FILE_NAME + "_instructors.txt", TT)