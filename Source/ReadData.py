import csv, random


def ConvertReq(slotstr):
    slotlist = []
    for val in slotstr:
        if "~" not in val:
            if "월" in val:
                day = 0
            elif "화" in val:
                day = 1
            elif "수" in val:
                day = 2
            elif "목" in val:
                day = 3
            else:
                day = 4
            slotlist += [27*day + i for i in range(27)]
        elif "요일" not in val:
            vals = val.split("~")
            tmpl = []
            for v in vals:
                tt = v.split(":")
                if tt[1] == "00":
                    tmpl.append((int(tt[0]) - 9) * 2)
                else:
                    tmpl.append((int(tt[0]) - 9) * 2 + 1)
            for d in range(5):
                slotlist += [27*d + i for i in range(tmpl[0], tmpl[1])]
        else:
            if "월" in val:
                day = 0
            elif "화" in val:
                day = 1
            elif "수" in val:
                day = 2
            elif "목" in val:
                day = 3
            else:
                day = 4
            valss = val.split("요일")
            vals = valss[1].split("~")
            tmpl = []
            for v in vals:
                tt = v.split(":")
                if tt[1] == "00":
                    tmpl.append((int(tt[0]) - 9) * 2)
                else:
                    tmpl.append((int(tt[0]) - 9) * 2 + 1)
            slotlist += [27*day + i for i in range(tmpl[0], tmpl[1])]
    return slotlist


def CourseInfo(yrsem, crsDic, global_unavails):
    if crsDic:  isNew = False
    else:       isNew = True

    with open("Data/" + yrsem + "/" + yrsem + "CourseList.csv", 'r') as course_info_file:
        Dic = list(csv.DictReader(course_info_file))
    keyTypes = Dic[-1].copy()
    del Dic[-1]
    if isNew:   crsDic = list(Dic)

    for c, crs in enumerate(Dic):
        for key in crs.keys():
            if keyTypes[key] == 'int':
                crsDic[c][key] = int(crs[key])
            elif keyTypes[key] == 'lint':
                crsDic[c][key] = [int(v) for v in crs[key].split()]
            elif keyTypes[key] == 'lstr':
                crsDic[c][key] = crs[key].split()
    for crs in crsDic:
        crs['Level'] = int(crs['ClassCode'][2])
        crs['AvailableSlots'] = ConvertReq(crs['Request'])
        crs['UnavailableSlots'] = ConvertReq(crs['Reject'])
        if len(crs['AvailableSlots']) == sum(crs['Credit']):
            crs['Fixed'] = True
            crs['SoftFixed'] = True
        elif crs['AvailableSlots']:
            crs['Fixed'] = False
            crs['SoftFixed'] = True
            crs['AvailableSlots'] = [i for i in crs['AvailableSlots'] if i not in global_unavails and i not in crs['UnavailableSlots']]
        else:
            crs['Fixed'] = False
            crs['SoftFixed'] = False
            for d in range(5):
                crs['AvailableSlots'] += [i for i in range(27*d, 27*d + 18) if i not in global_unavails and i not in crs['UnavailableSlots']]
    return crsDic


def StudentInfo(crsDic, yrsem):
    stdDic = []
    with open("Data/" + yrsem + "/" + yrsem + "StudentSurvey.csv", 'r') as file:
        data = file.readlines()
        num = 0
        for line in data[1:]:
            items = line.split(",")
            tmpdict = {
                'Id': 'Sur' + str(num).zfill(3),
                'SchoolYear' : int(items[1]),
                'SurveyCode' : []
            }
            for i in range(2, 6):
                tmpdict['SurveyCode'] += [(i-1)*100 + int(v) for v in items[i].split()]
            stdDic.append(tmpdict)
            num += 1

    for std in stdDic:
        std['Enrolled'] = []
        for code in std['SurveyCode']:
            tmplst = [c for c, crs in enumerate(crsDic) if crs['SurveyCode'] == code]
            if tmplst:
               std['Enrolled'].append(random.choice(tmplst))
        std['Enrolled'].sort()
    stdDic = [std for std in stdDic if sum([sum(crsDic[i]['Credit']) for i in std['Enrolled']]) / 2 < 40]

    for crs in crsDic:  # Rewrite the roster for courses
        crs['Roster'] = []
    for s, std in enumerate(stdDic):
        for c in std['Enrolled']:
            crsDic[c]['Roster'].append(s)
    for crs in crsDic:
        crs['Roster'].sort()
    return stdDic
