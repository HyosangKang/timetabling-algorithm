import numpy as np
import json, os

def Swap(lst, mat):
    mat[lst[0]][lst[2]] -= 1
    mat[lst[0]][lst[3]] += 1
    mat[lst[1]][lst[3]] -= 1
    mat[lst[1]][lst[2]] += 1


def WeightDiff(lst, enrmat):
    crsmat = np.matmul(enrmat.T, enrmat)
    l1 = list(np.where(enrmat[lst[0]] != 0)[0])
    l2 = list(np.where(enrmat[lst[1]] != 0)[0])
    comm = [i for i in l1+l2 if i in l1 and i in l2]
    l1 = [i for i in l1 if i != lst[2] and i not in comm]
    l2 = [i for i in l2 if i != lst[3] and i not in comm]
    return 2 * (len(l1) + len(l2) - np.sum(crsmat[lst[2], l1]) + np.sum(crsmat[lst[3], l1]) - np.sum(crsmat[lst[3], l2]) + np.sum(crsmat[lst[2], l2]))


def NumConf(mat):
    enrmat = np.matmul(mat.T, mat)
    size = np.size(enrmat, 0)
    sum = 0
    for i in range(size - 1):
        for j in range(i + 1, size):
            if enrmat[i][j] != 0:
                sum += 1
    return sum


def OptimizeEnroll(stdDic, crsDic, yrsem):
    if os.path.isfile("./Data/" + yrsem + "/Results/StdData.json") and os.path.isfile("./Data/" + yrsem + "/Results/CrsData.json"):
        print("Load from existing data ... ", end="")
        with open("./Data/" + yrsem + "/Results/StdData.json", 'r') as file:
            stdDic = json.load(file).copy()
        with open("./Data/" + yrsem + "/Results/CrsData.json", 'r') as file:
            crsDic = json.load(file).copy()

    sectionPairs = []
    for crs in crsDic:
        sectionPairs.append([ind for ind, dic in enumerate(crsDic) if crs['SurveyCode'] > 0 and dic['SurveyCode'] == crs['SurveyCode'] and dic != crs])
    enrmat = np.zeros((len(stdDic), len(crsDic)))
    enrmat.astype(int)
    for s, std in enumerate(stdDic):
        for c, crs in enumerate(crsDic):
            if s in crs['Roster']:
                enrmat[s][c] = 1

    loop_count = 1
    noMoreSwap = False
    while not noMoreSwap:
        noMoreSwap = True
        print("\nloop count : " + str(loop_count) + ", Number of conflicting pairs: " + str(NumConf(enrmat)), end="")
        for s1 in range(len(stdDic)):
            swapped = False
            for c1 in np.where(enrmat[s1] == 1)[0]:
                if swapped:
                    break
                for c2 in sectionPairs[c1]:
                    if swapped:
                        break
                    for s2 in np.where(enrmat.T[c2] == 1)[0]:
                        pair = [s1, s2, c1, c2]
                        d = WeightDiff(pair, enrmat)
                        if d > 0:
                            Swap(pair, enrmat)
                            swapped = True
                            break
            if swapped:
                noMoreSwap = False
        loop_count += 1
        for c, crs in enumerate(crsDic):
            crs['Roster'] = [int(i) for i in np.where(enrmat.T[c] == 1)[0]]
            crs['Roster'].sort()
        for s, std in enumerate(stdDic):
            std['Enrolled'] = [int(i) for i in np.where(enrmat[s] == 1)[0]]
            std['Enrolled'].sort()
        with open("./Data/" + yrsem + "/Results/CrsData.json", 'w') as file:
            json.dump(crsDic, file)
        with open("./Data/" + yrsem + "/Results/StdData.json", 'w') as file:
            json.dump(stdDic, file)
    print(" ... Done")

    return stdDic, crsDic