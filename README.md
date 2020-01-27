# timetabling-algorithm

* &copy;2020 Hyosang Kang All Rights Reserved.
* Jan 26, 2020 Update: Initial commit. All data were converted to English (from Korean). Currently  data for 2020 Spring semester is available only. More data (since 19 Spring) will be updated.

## Introduction

* This is an automated timetabling algorithm developed by [Hyosang Kang](https://klein.dgist.ac.kr). The source code is written by Python3. 
* The data is used for Daegu-Gyeongbuk Institute of Science and Technology(DGIST) undergraduate study. 


## How to execute the code

* The ```Main.py``` is the executable python code for running the algorithm. If you cloned entire repository, you can run the code directly.
* ```yrsem```(string) is the name of the folder in ```./Data```. 
* You must have the following data files in ```./Data/[yrsem]/``` folder.
    * ```20SpringCourseList.csv``` contains the course information. The first row indicates the key of each column data. The last row indicate the type of data of each column. Both the first and the last rows should be removed.
        * ```int, str``` represent integer, string data
        * ```lint, lstr``` represent the list of integers, list of strings
    * ```20SpringStudentSurvey.csv``` contains the survey data of students. Each row represent a student's choice of course which she/he plans to register in the next semester. A survey code is given to each course by ```[course grade]*100 + [survey number]```. For example, number 1 class in in the ```Fsh``` column has survey code as 101. This survey code is recorded in the last column of  ```20SpringCourseList.csv```. 
    * ```ClassRoom.csv``` contains the classroom information. The ```PossibleClassrooms``` column in ```20SpringCourseList.csv``` is recorded with respect to the data in this file.
* You will see some global variable in the top lines of ```Main.py``` file.
    * ```yrsem```(string) is the name of the folder in ```./Data``` where the data for the corresponding semester in the corresponding year lie in. For example, ```yrsem = "20Spring"``` uses data in ```./Data/20Spring/```.
    * ```NUM_MIN```(boolean) is the variable for eliminating the most-conflicting pairs during the timetabling. If ```NUM_MIN``` is True, then the algorithm chooses a pair of courses which conflicted the most during the certain period of time while the algorithm is running, and remove from the list of conflict pairs.
    * ```SHORT_PRINT``` determines the output format which indicates the progress of algorithm. IF ```SHORT_PRINT``` is False, then it prints a line which indicates which course has been tried to be timetabled at which location. If ```SHORT_PRINT``` is True, then it prints a number of courses whose timetabling has been succeed only when such number reached at the new maximum.
    * ```SHORT_MIN, NUM_DEL, THRESHOLD``` are variables used for removing most-conflicted pairs. For example, if ```SHORT_MIN``` is 5, and the algorithm fails to update a new maximal number of courses timetabled successfully for 5 minutes, then it removes top ```NUM_DEL``` pairs which conflicted the most during the timetabling. Each conflict pair should be conflicted at least ```THRESHOLD``` times If there were no pairs which conflicted ```THRESHOD``` times, then the threshold is reduced by 9/10 until it finds any pair satisfying the condition. If threshold is less than 10, then the algorithm resumes without any removal of pairs.   

## Output

* The result of timetabling is stored at ```./Data/[yrsem]/Results/```. 
* The file ```data_[yrsem]_[Data_Time].json``` contains the dictionary of course data.
* The file ```data_[yrsem]_[Data_Time]_timetable.csv``` is the actual result of timetabling written in a csv format. 