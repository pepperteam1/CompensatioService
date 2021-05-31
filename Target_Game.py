import threading
import multiprocessing
import serial
import time
from naoqi import ALProxy
import random
from datetime import datetime
from Tkinter import *
import tkFileDialog
import csv
import os
import pandas as pd
import math


def PathGet():
    global inputFile
    inputFile = tkFileDialog.askdirectory()


def multiplier():  # automatic calc the time for each cup/key
    try:
        subjectName = subj_name.get()
        if (v1.get() == 1):
            Gender = "Male"
        else:
            Gender = "Female"
        with open(
                '/home/pepper/catkin_ws/src/pepper_robot/pepper_sensors_py/src/board/data/' + subjectName + '_' +
                Gender[0] + '.csv',
                'r') as csvfile:
            dataFrame = pd.read_csv(csvfile)

        duration1 = round(dataFrame.loc[dataFrame["LevelNumber"] == 0, "Duration"].mean())
        duration2 = round(dataFrame.loc[dataFrame["LevelNumber"] == 1, "Duration"].mean())
        duration3 = round(dataFrame.loc[dataFrame["LevelNumber"] == 2, "Duration"].mean())
        duration4 = round(dataFrame.loc[dataFrame["LevelNumber"] == 3, "Duration"].mean())
        duration5 = round(dataFrame.loc[dataFrame["LevelNumber"] == 4, "Duration"].mean())
        if math.isnan(duration2):
            duration2 = duration1 + 5
        if math.isnan(duration3):
            duration3 = duration2 + 5
        if math.isnan(duration4):
            duration4 = duration3 + 5
        if math.isnan(duration5):
            duration5 = duration4 + 5
        txtDisp4.delete(0, END)  # deletes the current value
        txtDisp4.insert(0, int(duration1))  # inserts new value assigned by 2nd parameter
        txtDisp5.delete(0, END)
        txtDisp5.insert(0, int(duration2))
        txtDisp6.delete(0, END)
        txtDisp6.insert(0, int(duration3))
        txtDisp7.delete(0, END)
        txtDisp7.insert(0, int(duration4))
        txtDisp8.delete(0, END)
        txtDisp8.insert(0, int(duration5))
        csvfile.close()

    except ValueError:
        pass


class Tags(object):
    def __init__(self):
        self.running = True
        self.threads = []

    def ShowImage(self, PlayNumber, LevelNumber, i, q):
        global CUP3_time
        global CUP4_time
        global CUP5_time
        global CUP6_time
        global CUP7_time
        memory.insertData("Turn", PlayNumber)
        if LevelNumber == 0:
            if i == 12:
                i = 1
            memory.insertData("ImageUrl", "T_3_" + str(i) + ".jpg")
            memory.insertData("Tfd", CUP3_time)
        elif LevelNumber == 1:
            memory.insertData("ImageUrl", "T_4_" + str(i) + ".jpg")
            memory.insertData("Tfd", CUP4_time)
        elif LevelNumber == 2:
            memory.insertData("ImageUrl", "T_5_" + str(i) + ".jpg")
            memory.insertData("Tfd", CUP5_time)
        elif LevelNumber == 3:
            memory.insertData("ImageUrl", "T_6_" + str(i) + ".jpg")
            memory.insertData("Tfd", CUP6_time)
        elif LevelNumber == 4:
            memory.insertData("ImageUrl", "T_7_" + str(i) + ".jpg")
            memory.insertData("Tfd", CUP7_time)
        manager.runBehavior("showimagetarget/behavior_1")

        # human_feel(PlayNumber)
        print("image number:" + str(i))
        # print("finish show image")

    def getValues(self, v_p, q, LevelNumber):  # chacks the order of the cups
        arduinodata1 = [];
        arduinodata = []
        while arduinodata1 == []:
            ser.write(b'p');
            time.sleep(0.5)
            arduinodata1 = ser.readlines()
            arduinodata1 = (x for x in arduinodata1 if
                            "Reader" in x)  # delete all the unessery data that was in the serial
            arduinodata1 = [i.split('\r\n', 1)[0] for i in arduinodata1]

        ser.close();
        if len(arduinodata1) < (
                LevelNumber + 3):  # make sure that all the data that was needed are scaned from the serial
            ser.open();
            manager.runBehavior("slow6/behavior_1")
            c = 0
            while (c < 5) and (arduinodata == []):
                ser.write(b'v');
                print("i'm here")
                c = c + 1
                arduinodata = ser.readlines()
                arduinodata = (x for x in arduinodata if "Reader" in x)
                arduinodata = [i.split('\r\n', 1)[0] for i in arduinodata]

        if (len(arduinodata1) > len(arduinodata)):
            print(arduinodata1)
            ser.close();
            memory.insertData("Press", 1)
            q.put(arduinodata1)
        else:
            print(arduinodata)
            ser.close();
            memory.insertData("Press", 1)
            q.put(arduinodata)

    def go(self, PlayNumber, LevelNumber, j, P_V):  # starts the threading process
        t1 = threading.Thread(target=self.ShowImage, args=(PlayNumber, LevelNumber, j, q,))
        t2 = threading.Thread(target=self.getValues, args=(P_V, q, LevelNumber))
        t1.start()
        t2.start()
        self.threads.append(t1)
        self.threads.append(t2)


class CL(object):  # the change level process
    def __init__(self):
        self.running = True
        self.threads = []

    def ChangeLevel(self, q):
        ser.open();
        arduinodata1 = [];
        ser.write(b'o');

        while arduinodata1 == []:
            ser.write(b'o');
            arduinodata1 = ser.readlines()
            arduinodata1 = (x for x in arduinodata1 if not "0" in x)
            # print(arduinodata1)
            arduinodata1 = [i.split('\r\n', 1)[0] for i in arduinodata1]
            arduinodata1 = [i.split('\r\n', 1)[0] for i in arduinodata1]
            # print("cups")
            # print(arduinodata1)
        print(arduinodata1)
        ser.close();
        q.put(arduinodata1[0])

    def ChangeLevel_show(self, LevelNumber, q):
        if LevelNumber != -1:
            manager.runBehavior("changelevel/behavior_1")
            time.sleep(0.5)
        if LevelNumber == 0:
            manager.runBehavior("changelevel4/behavior_1")
        if LevelNumber == -1:
            manager.runBehavior("stopgame/behavior_1")
            manager.runBehavior("changelevel4/behavior_1")

    def goLevel(self, LevelNumber):
        t3 = threading.Thread(target=self.ChangeLevel, args=(q,))
        t4 = threading.Thread(target=self.ChangeLevel_show, args=(LevelNumber, q,))
        t3.start()
        t4.start()
        self.threads.append(t3)
        self.threads.append(t4)


def join_threads(threads):  # Needed for the threading, just a definition of the librery

    #    Join threads in interruptable fashion.
    #    From http://stackoverflow.com/a/9790882/145400

    for t in threads:
        while t.isAlive():
            t.join(5)


def StartGame():  # the function that starts the game
    global CUP3_time
    global CUP4_time
    global CUP5_time
    global CUP6_time
    global CUP7_time
    global novideo
    no_video = novideo.get()
    CUP3_time = CUP3_show.get()
    CUP4_time = CUP4_show.get()
    CUP5_time = CUP5_show.get()
    CUP6_time = CUP6_show.get()
    CUP7_time = CUP7_show.get()

    subjectName = subj_name.get()  # raw_input("Please Enter the subject's Name: PSYnn-for young, PSOnn - for old - nn-is the number of the subject ")
    if (v1.get() == 1):
        Gender = "Male"
    else:
        Gender = "Female"
    # Gender = #raw_input("Please Enter the subject's Gender: [Male] or [Female] ")
    Push_V = 2  # its not raely needed but alot of the code is based on it so for now not deleted
    Trail = v2.get()  # Do the Trail now? (NO,YES)
    # push data to pepper:
    memory.insertData("Press", 0)
    memory.insertData("ReactionT", 0)
    memory.insertData("YN", 0)
    memory.insertData("Push_V", int(Push_V))
    memory.insertData("Gender", Gender)
    nostop = no_stop.get()
    memory.insertData("Nostop", nostop)
    PlayNumber = 1;  # the number of the play game
    LevelNumber = 0;  # the level of the game (0-4)
    num_succes = 0;
    P_V = int(Push_V);  # select (1- voice recognition , 2- push button)
    List_F = ["f_1", "f_3", "f_4", "f_5", "f_6", "f_7", "f_8", "f_9", "f_10"]  # failure response
    List_A = ["s_1", "s_4", "s_5", "s_6", "s_7", "s_8", "s_9", "s_10"]  # success response
    if (v3.get() == 1):  # if the game is new open new file
        File = open(subjectName + '_startover.txt', 'w')
        PlayNumbercurent = PlayNumber
        Round_number = 1
        File = open(subjectName + '_startover.txt', 'w')
        File.write(str(LevelNumber) + " " + str(PlayNumber) + " " + str(Round_number) + " " + str(num_succes))
        File.close()
        firsttime = first_time.get()
        if firsttime == 1:
            manager.runBehavior("intro/behavior_1")
        else:
            manager.runBehavior("welcome1/behavior_1")
        manager.runBehavior("instruction2/behavior_1")
        manager.runBehavior("weakhand/behavior_1")
        if no_video == 0:
            manager.runBehavior("video_target/behavior_1")
    else:  # need new file
        File = open(subjectName + '_startover.txt', 'r')  # open a file and write in it!
        # read what turn is it and what the changes are
        linesfiles = File.readlines()
        LevelNumber = int(linesfiles[len(linesfiles) - 1].split(' ')[0])
        PlayNumbercurent = int(linesfiles[len(linesfiles) - 1].split(' ')[1])
        Round_number = int(linesfiles[len(linesfiles) - 1].split(' ')[2])
        num_succes = int(linesfiles[len(linesfiles) - 1].split(' ')[3])
        File.close()
        manager.runBehavior("re_2/behavior_1")
    # if its first turn
    if int(Trail) == 1:  # if to do the trail while playing with the screen (1) or on playing with pepper (0 )
        manager.runBehavior("tryp/behavior_1")
        t = Tags()
        data = []
        t.go(0, 0, 1, 2)  # try pushbutton
        join_threads(t.threads)
        data = q.get()  # getValues()
        CardName = [''] * 7C:\Python27C:\Python27
        CardNum = [0] * 7
        ReaderNum = [''] * 7
        for j in range(0, len(data)):
            ReaderNum[j] = data[j].split(': ', 3)[0]
            CardName[j] = data[j].split(': ', 3)[2]
            Cardindexpre = data[j].split(' ', 3)[1]
            Cardindex = int(Cardindexpre.split(':', 2)[0])
            CardNum[Cardindex] = Cards[CardName[j]];
        Success = (CardNum == cups_3[0])
        if Success:
            manager.runBehavior("s_1/behavior_1")
        else:
            manager.runBehavior("f_1/behavior_1")
        ser.close()
        manager.runBehavior("tryp2/behavior_1")
        ser.open()
        t.go(0, 0, 2, 2)  # try pushbutton
        join_threads(t.threads)
        data = q.get()  # getValues()
        CardName = [''] * 7
        CardNum = [0] * 7
        ReaderNum = [''] * 7
        for j in range(0, len(data)):
            ReaderNum[j] = data[j].split(': ', 3)[0]
            CardName[j] = data[j].split(': ', 3)[2]
            Cardindexpre = data[j].split(' ', 3)[1]
            Cardindex = int(Cardindexpre.split(':', 2)[0])
            CardNum[Cardindex] = Cards[CardName[j]];
        Success = (CardNum == cups_3[1])
        if Success:
            manager.runBehavior("s_4/behavior_1")
        else:
            manager.runBehavior("f_3/behavior_1")
        ser.close()
        ser.open()
        manager.runBehavior("startgame/behavior_1")
    rand_3_5 = random.sample(range(1, 12), 11)
    rand_6 = random.sample(range(1, 11), 10)
    rand_7 = random.sample(range(1, 11), 10)
    rand_ten = random.sample(range(1, 11), 10)
    behavior_num = -1
    # ser.open()
    # change the if for the game thaht it is
    for PlayNumber in range(PlayNumbercurent, 30):
        ##File = open(subjectName + '_startover.txt', 'w')
        ##File.write( str(LevelNumber) + " " + str(PlayNumber) + " " + str(change) + " " + str(change_2) + " " + str(change_3))
        ##File.close()
        behavior_num = behavior_num + 1
        Round_number = Round_number + 1
        data = []
        ReaderNum = [''] * 7
        # R_Num = [''] * 6
        CardName = [''] * 7
        CardNum = [0] * 7
        # CardNum_o = [0] * 6
        # newscore = [0] * 6
        t = Tags()
        # random number for the image to show on peppers tablet
        if LevelNumber < 3:
            i = rand_3_5[Round_number - 1];
        elif LevelNumber == 3:
            i = rand_7[Round_number - 1];
        else:
            i = rand_ten[Round_number - 1];
        current_time = datetime.now()
        tic = time.time()
        if P_V == 1:  # voice recognition
            t.ShowImage(PlayNumber, LevelNumber, i, q)
            t.getValues(P_V, q)
            data = q.get()  # getValues()

        elif P_V == 2:  # push button
            ser.close()
            ser.open();
            t.go(PlayNumber, LevelNumber, i, P_V)
            join_threads(t.threads)
            time.sleep(1.5)
            data = q.get()  # getValues()
        toc = time.time()
        duration = str(toc - tic);
        for j in range(0, len(data)):
            ReaderNum[j] = data[j].split(': ', 3)[0]
            CardName[j] = data[j].split(': ', 3)[2]
            Cardindexpre = data[j].split(' ', 3)[1]
            Cardindex = int(Cardindexpre.split(':', 2)[0])
            CardNum[Cardindex] = Cards[CardName[j]];
        ReaderNum = [x for x in ReaderNum if x]
        """for k in range(0, len(ReaderNum)):
            R_Num[k] = int(ReaderNum[k].split(' ', 2)[1])
        R_Num = [x for x in R_Num if x != '']
        CardNum = [x for x in CardNum if x != 0]
        print (R_Num)
        print (ReaderNum)"""
        # print(memory.getData("Press"))
        print("card number : " + str(CardNum[:]))
        print(CardNum)
        """for k in range(0,len(R_Num)):
            CardNum_o[R_Num[k]]=CardNum[k];
        print(CardNum_o[:]);"""

        if LevelNumber == 0:  # try to make a short code.
            for k in range(0, len(CardNum) - 1):
                if CardNum[k] != 0:
                    if CardNum[k] == cups_3[i - 1][k]:
                        if k <= 2:
                            num_succes = num_succes + 1
                        elif (k == 4) or (k == 5):
                            num_succes = num_succes + 2
                        else:
                            num_succes = num_succes + 3
            Success = (CardNum == cups_3[i - 1])
            print("cups3:" + str(cups_3[i - 1]))

        elif LevelNumber == 1:
            for k in range(0, len(CardNum) - 1):
                if CardNum[k] != 0:
                    if CardNum[k] == cups_4[i - 1][k]:
                        if k <= 2:
                            num_succes = num_succes + 1
                        elif (k == 4) or (k == 5):
                            num_succes = num_succes + 2
                        else:
                            num_succes = num_succes + 3
            Success = (CardNum == cups_4[i - 1])
            print("cups4:" + str(cups_4[i - 1]))

        elif LevelNumber == 2:
            for k in range(0, len(CardNum) - 1):
                if CardNum[k] != 0:
                    if CardNum[k] == cups_5[i - 1][k]:
                        if k <= 2:
                            num_succes = num_succes + 1
                        elif (k == 4) or (k == 5):
                            num_succes = num_succes + 2
                        else:
                            num_succes = num_succes + 3
            Success = (CardNum == cups_5[i - 1])
            print("cups5:" + str(cups_5[i - 1]))

        elif LevelNumber == 3:
            for k in range(0, len(CardNum) - 1):
                if CardNum[k] != 0:
                    if CardNum[k] == cups_6[i - 1][k]:
                        if k <= 2:
                            num_succes = num_succes + 1
                        elif (k == 4) or (k == 5):
                            num_succes = num_succes + 2
                        else:
                            num_succes = num_succes + 3
            Success = (CardNum == cups_6[i - 1])
            print("cups6:" + str(cups_6[i - 1]))

        elif LevelNumber == 4:
            for k in range(0, len(CardNum) - 1):
                if CardNum[k] != 0:
                    if CardNum[k] == cups_7[i - 1][k]:
                        if k <= 2:
                            num_succes = num_succes + 1
                        elif (k == 4) or (k == 5):
                            num_succes = num_succes + 2
                        else:
                            num_succes = num_succes + 3
            Success = (CardNum == cups_7[i - 1])
            print("cups6:" + str(cups_7[i - 1]))
        if behavior_num == 10:
            behavior_num = 0
        if Success:
            manager.runBehavior(List_A[PlayNumber % 8] + "/behavior_1")
            num_succes = num_succes + 1;
            print(num_succes)  # Move to place that will print always even if u dont succes.
        else:
            # print(rand_ten[PlayNumber-1])
            # print(List_F[rand_ten[PlayNumber-1]-1])

            manager.runBehavior(List_F[PlayNumber % 9] + "/behavior_1")
            time.sleep(1.5)
            manager.runBehavior("wrongordersecond/behavior_1")
            time.sleep(1)
        results[PlayNumber] = Success;
        sum_succes[PlayNumber - 1] = Success;
        #  fr = open(subjectName + '_' + Gender[0] + '.txt', 'a+') # append to the end of the file text
        #  # current time , Pepper/tablet , P_V , PlayNumber , LevelNumber , durationOfReaction , Success , cupsOrder , correctImage cups , Reaction number
        #  fr.write(current_time.strftime('%Y-%m-%d %H:%M:%S') + " " + "Pepper" + " " + "pushbutton" + " " + str(
        #  PlayNumber) + " " + str(LevelNumber) + " " + duration + " " + str(Success) + " " + str(
        #  CardNum[:]) + " " + str(i) + " " + str(rand_ten[behavior_num]) + "\n");
        # #edit the last line
        #  fr.close()

        with open(
                '/home/pepper/catkin_ws/src/pepper_robot/pepper_sensors_py/src/board/data/' + subjectName + '_' +
                Gender[0] + '.csv', 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if os.stat(
                    '/home/pepper/catkin_ws/src/pepper_robot/pepper_sensors_py/src/board/data/' + subj_name.get() + '_' +
                    Gender[0] + '.csv').st_size == 0:
                writer.writerow(
                    ["Date", "Time", "Game mode", "PlayNumber", "LevelNumber", "Duration", "Success", "CardNum",
                     "Picture"])
            writer.writerow(
                [current_time.strftime('%Y-%m-%d'), current_time.strftime('%H:%M:%S'), "Pepper", str(
                    PlayNumber), str(LevelNumber), str(float(duration) - 4.6), str(Success), str(CardNum[:]),
                 "T_" + str(LevelNumber + 3) + "_" + str(i)])
        csvfile.close()

        ser.close();
        if PlayNumber == 5:
            manager.runBehavior("stretch1/behavior_1")
        if PlayNumber == 10:
            manager.runBehavior("stretch2/behavior_1")
        t = CL()
        if LevelNumber < 4:
            if PlayNumber == 3:  # ask to change level
                data = []
                t.goLevel(LevelNumber)
                join_threads(t.threads)
                data = q.get()  # getValues()
                ans = data;
                # if memory.getData("YN")==1:
                if ans == "yes":
                    LevelNumber = LevelNumber + 1;  # 4-cups
                    File = open(subjectName + '_startover.txt', 'w')
                    Round_number = 0
                    File.write(
                        str(LevelNumber) + " " + str(PlayNumber) + " " + str(Round_number) + " " + str(num_succes))

                    File.close()
                    manager.runBehavior("nextlevel/behavior_1")
            elif (Round_number > 3 and (Round_number % 3) == 0 and LevelNumber == 0) or (
                    (Round_number % 4) == 0 and LevelNumber > 0):  # 4 trails in level 0, 3 trails in level 1.t = CL()
                data = []
                if LevelNumber == 1 or LevelNumber == 3:  # stop the game at level 2 or 4.
                    t.goLevel(-1)
                    join_threads(t.threads)
                    data = q.get()  # getValues()
                    ans = data;
                    if ans == "yes":
                        print(sum_succes)
                        # num_succes=sum(sum_succes);
                        if num_succes % 2 == 0:
                            num_succes = num_succes / 2
                        else:
                            num_succes = (num_succes + 1) / 2
                        SoundSucces = num_succes / 2;
                        memory.insertData("SumSuccess", "Slide" + str(num_succes) + '.JPG');
                        memory.insertData("SoundSucces", str(SoundSucces) + '.ogg');
                        manager.runBehavior("points/behavior_1")
                        manager.runBehavior("finishgamev2/behavior_1")
                        manager.runBehavior("nexttime-8a0fd0/behavior_1")
                        PlayNumber = 30
                        break
                t.goLevel(LevelNumber)
                join_threads(t.threads)
                data = q.get()  # getValues()
                ans = data;
                # if memory.getData("YN")==1:
                if ans == "yes":
                    LevelNumber = LevelNumber + 1;  # 4-cups
                    File = open(subjectName + '_startover.txt', 'w')
                    Round_number = 0
                    File.write(
                        str(LevelNumber) + " " + str(PlayNumber) + " " + str(Round_number) + " " + str(num_succes))

                    File.close()
                    manager.runBehavior("nextlevel/behavior_1")
                if (ans == "no" and Round_number > 12 and LevelNumber == 0) or (
                        ans == "no" and Round_number >= (4 + (4 * (4 - LevelNumber))) and LevelNumber > 0):
                    SoundSucces = num_succes;
                    memory.insertData("SumSuccess", "Slide" + str(num_succes) + ".JPG");
                    memory.insertData("SoundSucces", str(SoundSucces) + '.ogg');
                    manager.runBehavior("points/behavior_1")
                    manager.runBehavior("finishgamev2/behavior_1")
                    manager.runBehavior("nexttime-8a0fd0/behavior_1")
                    PlayNumber = 30
        elif LevelNumber == 4 and Round_number == 4:
            print(sum_succes)
            SoundSucces = num_succes;
            memory.insertData("SumSuccess", "Slide" + str(num_succes) + ".JPG");
            memory.insertData("SoundSucces", str(SoundSucces) + '.ogg');
            manager.runBehavior("points/behavior_1")
            manager.runBehavior("finishgamev2/behavior_1")
            manager.runBehavior("nexttime-8a0fd0/behavior_1")
            PlayNumber = 30
            break
        File = open(subjectName + '_startover.txt', 'w')
        File.write(str(LevelNumber) + " " + str(PlayNumber) + " " + str(Round_number) + " " + str(num_succes))
        File.close()


global inputFile
global CUP3_time  # Time of picture show.
global CUP4_time
global CUP5_time
global CUP6_time
global CUP7_time
global novideo

numPoint = 7
ReaderNum = [''] * 7
CardName = [''] * 7
CardNum = [0] * 7

# Arragment of the images of the cups.
# 1-orange, 2-purple,3-yellow,4-blue,5-green
cups_3 = [[3, 5, 4, 0, 0, 0, 0], [5, 1, 4, 0, 0, 0, 0], [2, 1, 3, 0, 0, 0, 0], [4, 5, 2, 0, 0, 0, 0],
          [5, 3, 2, 0, 0, 0, 0], [3, 4, 5, 0, 0, 0, 0], [2, 4, 0, 3, 0, 0, 0], [4, 1, 0, 5, 0, 0, 0],
          [1, 2, 0, 3, 0, 0, 0], [2, 0, 3, 1, 0, 0, 0], [3, 0, 4, 2, 0, 0, 0], [3, 5, 4, 0, 0, 0, 0],
          [0, 3, 2, 4, 0, 0, 0], [0, 5, 4, 3, 0, 0, 0],
          [0, 2, 1, 4, 0, 0, 0]];  # all 6 combinations of arranging the 3-cups
cups_4 = [[2, 5, 3, 1, 0, 0, 0], [3, 4, 2, 5, 0, 0, 0], [1, 3, 2, 4, 0, 0, 0], [4, 0, 2, 1, 0, 3, 0],
          [3, 0, 4, 2, 0, 5, 0], [4, 0, 2, 1, 0, 5, 0], [4, 5, 0, 2, 1, 0, 0], [1, 4, 0, 5, 2, 0, 0],
          [5, 3, 0, 4, 2, 0, 0], [5, 1, 4, 0, 3, 0, 0], [4, 1, 2, 0, 5, 0, 0], [1, 3, 5, 0, 2, 0, 0],
          [1, 2, 5, 0, 0, 3, 0], [4, 3, 1, 0, 0, 5, 0], [3, 1, 4, 0, 0, 2, 0]];
cups_5 = [[5, 1, 3, 2, 0, 4, 0], [2, 3, 4, 5, 0, 1, 0], [3, 5, 2, 1, 0, 4, 0], [4, 1, 3, 2, 0, 5, 0],
          [2, 5, 1, 3, 0, 4, 0], [4, 3, 5, 1, 2, 0, 0], [1, 3, 4, 5, 2, 0, 0], [2, 4, 1, 3, 5, 0, 0],
          [4, 3, 2, 5, 1, 0, 0], [2, 4, 5, 3, 1, 0, 0], [3, 2, 5, 0, 4, 1, 0], [1, 2, 3, 0, 5, 4, 0],
          [3, 5, 4, 0, 1, 2, 0], [4, 1, 5, 0, 2, 3, 0], [2, 3, 1, 0, 5, 4, 0]];
cups_6 = [[4, 2, 3, 0, 1, 4, 5], [3, 3, 2, 0, 4, 5, 1], [4, 2, 3, 5, 4, 1, 0], [1, 4, 2, 5, 3, 3, 0],
          [3, 1, 5, 2, 3, 4, 0], [1, 4, 4, 2, 5, 0, 3], [2, 3, 4, 5, 4, 0, 1], [5, 4, 2, 1, 4, 0, 3],
          [3, 1, 0, 5, 2, 4, 4], [5, 2, 0, 1, 4, 3, 3], [1, 4, 0, 4, 3, 5, 2], [0, 4, 1, 5, 3, 2, 3],
          [0, 2, 3, 4, 1, 5, 4], [0, 5, 2, 1, 3, 3, 4], [1, 0, 4, 2, 3, 5, 4], [5, 0, 4, 3, 2, 1, 3],
          [4, 0, 4, 2, 1, 3, 5], [5, 2, 3, 3, 0, 4, 1], [2, 1, 3, 4, 0, 5, 4], [4, 3, 1, 5, 0, 2, 3]];
cups_7 = [[2, 3, 3, 5, 1, 4, 4], [3, 1, 5, 3, 4, 2, 4], [1, 3, 4, 5, 4, 3, 2], [2, 5, 1, 3, 3, 4, 4],
          [4, 4, 3, 5, 2, 3, 1], [5, 3, 3, 2, 4, 4, 1], [2, 4, 4, 1, 3, 3, 5], [1, 2, 3, 3, 4, 4, 5],
          [5, 4, 4, 3, 3, 2, 1], [5, 4, 3, 1, 3, 4, 2]];
# open and upload a specific arduino sketch
# arduinoCommand = "\"C:\Program Files (x86)\Arduino\\arduino\" --upload --board \"arduino:avr:uno\" --port COM3 \"C:\Users\Avital\Documents\Arduino\RFID_READ\MultiRFIDReader\MultiRFIDReader.ino\""
# print(arduinoCommand)
# presult = subprocess.call(arduinoCommand, shell=True)
# time.sleep(30)
# connecting to the arduino port in this computer it's in port: COM5.
if os.path.exists('/dev/ttyACM0') == True:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
if os.path.exists('/dev/ttyACM1') == True:
    ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)

time.sleep(2)  # Delay python function.

# 1-orange, 2-purple,3-yellow,4-blue,5-green
Cards = {'5F D5 A0 59': 1, '6B FB A0 59': 2, 'DF 72 A0 59': 3, '27 73 28 83': 4, '3F C4 A0 59': 5, 'D7 A8 AE 29': 3,
         '56 82 24 83': 4, '07 8E AE 29': 4, 'EC A8 AF 29': 4}

q = multiprocessing.Queue()
change = 0  # check the changes between levels [0-3cups, 1-4cups,2-5cups,3-6cups]
change_2 = 0
change_3 = 0
results = [[0] * 7 for i in range(30)]  # we need to makes algoritem which check the number of total games.
sum_succes = [[0] * 1 for i in range(30)]  # read the syntax of [0]*1 for.
num_succes = 0;
memory = ALProxy("ALMemory", "192.168.1.104", 9559)
manager = ALProxy("ALBehaviorManager", "192.168.1.104", 9559)
motion = ALProxy("ALMotion", "192.168.1.104", 9559)
motion.wakeUp()
postureProxy = ALProxy("ALRobotPosture", "192.168.1.104", 9559)
postureProxy.goToPosture("StandInit", 1.0)
motion.setExternalCollisionProtectionEnabled("All", False)  # External-collision avoidance - disable

# declaration of Pepper Memory Parameters:
memory.declareEvent("Gender")  # subjects gender (male/female)
memory.declareEvent("SumSuccess");
memory.declareEvent("SoundSucces");
memory.declareEvent("ReactionT")  # reaction time from showing the image until stopping
memory.declareEvent("YN")  # Yes/No to change level
memory.declareEvent("Press")  # identify when pushbutton is pressed on arduino
memory.declareEvent("Push_V")  # select (1- voice recognition , 2- push button)
memory.declareEvent("PlayNum")
memory.declareEvent("ImageUrl")  # select the image to show on peppers's tablet
memory.declareEvent("Tfd")  # define the time delay for the image
memory.declareEvent("Turn")
memory.declareEvent("Turn")
memory.declareEvent("Nostop")

# Intial GUI Functions.
root = Tk();
root.geometry("1000x1000+0+0")
root.title("Pepper Cups Game")

# Varibles that geeting from GUI.
v1 = IntVar()  # Does it man or a woman?
v2 = IntVar()  # Are we want trail or not?io
v3 = IntVar()  # Is it new game or not?
CUP3_show = IntVar()  # How much time it take to show 3 cups images.
CUP4_show = IntVar()
CUP5_show = IntVar()
CUP6_show = IntVar()
CUP7_show = IntVar()
subj_name = StringVar()  # What is the name of the patient?
no_stop = IntVar()
first_time = IntVar()
novideo = IntVar()

# GUI Functions:
Tops = Frame(root, width=1000, height=100, bg="powder blue", relief=SUNKEN)
Tops.pack(side=TOP)
Lb = Label(Tops, font=('ariel', 20, 'bold'), text="Pepper 6 Cups Game:", fg="Steel Blue", bd=10, anchor='w')
Lb.grid(row=0, column=0)
f1 = Frame(root, width=1000, height=1000, bg="powder blue", relief=SUNKEN)
f1.pack(side=TOP)
button_Path = Button(f1, text="Choose Path To Save File", bg="powder blue", command=PathGet, font="-weight bold")
button_Path.grid(columnspan=2)
label_1 = Label(f1, font=('ariel', 10, 'bold'), text="Name of The Subject", bg="powder blue")
label_1.grid(columnspan=2)
txtDisp1 = Entry(f1, font=('ariel', 10, 'bold'), textvariable=subj_name, bd=10, insertwidth=1, bg="powder blue",
                 justify='left')
txtDisp1.grid(columnspan=2)
label_2 = Label(f1, text="Subject Gender:", bg="powder blue", font="-weight bold")
label_2.grid(columnspan=2)
Radiobutton(f1, text="Male", padx=20, variable=v1, value=1, font=('ariel', 10, 'bold')).grid(columnspan=2)
Radiobutton(f1, text="Female", padx=20, variable=v1, value=2, font=('ariel', 10, 'bold')).grid(columnspan=2)
label_3 = Label(f1, text="new game?:", bg="powder blue", font="-weight bold")
label_3.grid(columnspan=2)
Radiobutton(f1, text="YES", padx=20, variable=v3, value=1, font=('ariel', 10, 'bold')).grid(columnspan=2)
Radiobutton(f1, text="NO", padx=20, variable=v3, value=2, font=('ariel', 10, 'bold')).grid(columnspan=2)
label_4 = Label(f1, text="Subject Start Game: [Trail/No Trail]:", bg="powder blue", font=('ariel', 10, 'bold'))
label_4.grid(columnspan=2)
Radiobutton(f1, text="Trail", padx=20, variable=v2, value=1, font=('ariel', 10, 'bold')).grid(columnspan=2)
Radiobutton(f1, text="No Trail", padx=20, variable=v2, value=0, font=('ariel', 10, 'bold')).grid(columnspan=2)
label_5 = Label(f1, font=('ariel', 10, 'bold'), text="Time to show - 3 Cups: [sec]", bg="powder blue")
label_5.grid(columnspan=2)
txtDisp4 = Entry(f1, font=('ariel', 10, 'bold'), textvariable=CUP3_show, bd=10, insertwidth=1, bg="powder blue",
                 justify='left')
txtDisp4.grid(columnspan=2)
label_6 = Label(f1, font=('ariel', 10, 'bold'), text="Time to show - 4 Cups: [sec]", bg="powder blue")
label_6.grid(columnspan=2)
txtDisp5 = Entry(f1, font=('ariel', 10, 'bold'), textvariable=CUP4_show, bd=10, insertwidth=1, bg="powder blue",
                 justify='left')
txtDisp5.grid(columnspan=2)
label_7 = Label(f1, font=('ariel', 10, 'bold'), text="Time to show - 5 Cups: [sec]", bg="powder blue")
label_7.grid(columnspan=2)
txtDisp6 = Entry(f1, font=('ariel', 10, 'bold'), textvariable=CUP5_show, bd=10, insertwidth=1, bg="powder blue",
                 justify='left')
txtDisp6.grid(columnspan=2)
label_8 = Label(f1, font=('ariel', 10, 'bold'), text="Time to show - 6 Cups: [sec]", bg="powder blue")
label_8.grid(columnspan=2)
txtDisp7 = Entry(f1, font=('ariel', 10, 'bold'), textvariable=CUP6_show, bd=10, insertwidth=1, bg="powder blue",
                 justify='left')
txtDisp7.grid(columnspan=2)
label_9 = Label(f1, font=('ariel', 10, 'bold'), text="Time to show - 7 Cups: [sec]", bg="powder blue")
label_9.grid(columnspan=2)
txtDisp8 = Entry(f1, font=('ariel', 10, 'bold'), textvariable=CUP7_show, bd=10, insertwidth=1, bg="powder blue",
                 justify='left')
txtDisp8.grid(columnspan=2)
mbutton = Button(f1, text="Calculate", command=multiplier)
mbutton.grid(columnspan=2)

label_10 = Label(f1, text="time limit yes or no?:", bg="powder blue", font=('ariel', 10, 'bold'))
label_10.grid(columnspan=2)
Radiobutton(f1, text="limit", padx=20, variable=no_stop, value=0, font=('ariel', 10, 'bold')).grid(columnspan=2)
Radiobutton(f1, text="No limit", padx=20, variable=no_stop, value=1, font=('ariel', 10, 'bold')).grid(columnspan=2)
label_11 = Label(f1, text="first time?:", bg="powder blue", font=('ariel', 10, 'bold'))
label_11.grid(columnspan=2)
Radiobutton(f1, text="yes", padx=20, variable=first_time, value=1, font=('ariel', 10, 'bold')).grid(columnspan=2)
Radiobutton(f1, text="No", padx=20, variable=first_time, value=0, font=('ariel', 10, 'bold')).grid(columnspan=2)
label_12 = Label(f1, text="video?:", bg="powder blue", font=('ariel', 10, 'bold'))
label_12.grid(columnspan=2)
Radiobutton(f1, text="yes", padx=20, variable=novideo, value=0, font=('ariel', 10, 'bold')).grid(columnspan=2)
Radiobutton(f1, text="No", padx=20, variable=novideo, value=1, font=('ariel', 10, 'bold')).grid(columnspan=2)
button_Start = Button(f1, text="START GAME", bg="green", command=StartGame, font=('ariel', 15, 'bold'))
button_Start.grid(columnspan=2)

root.mainloop()
