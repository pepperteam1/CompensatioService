import numpy as np
import serial
import time
import requests
import os
import csv
import pandas as pd

from pywinauto import application
from pywinauto.win32functions import ShowWindow
from pynput.keyboard import Key, Controller
import time
from datetime import datetime
from serial import Serial
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
print("running")

PATIENT_NAME = "Moshe"
LAST_TRAIL_COMPENSATION = []
VISUAL = True

keyboard = None
comp_dic = {
    0: 'trunk-flex',
    1: 'scapular-e',
    2: 'scapular-r',
    3: 'shoulder-flex',
    4: 'elbow-flex',
    5: 'distal-dys-syn',
    6: 'success'

}
feedback_hist = []
comp_hist = {'trunk-flex': 0,
             'scapular-e': 0,
             'scapular-r': 0,
             'shoulder-flex': 0,
             'elbow-flex': 0,
             'distal-dys-syn': 0}
predefined_compensations = []
compensation_hierarchy = []


@app.route("/")
def welcome():
    return " i am here"


@app.route("/new_patient", methods=['POST'])
def reboot():
    feedback_hist.clear()
    comp_hist = {'trunk-flex': 0,
                 'scapular-e': 0,
                 'scapular-r': 0,
                 'shoulder-flex': 0,
                 'elbow-flex': 0,
                 'distal-dys-syn': 0}
    print(request.json)
    predefined_compensations.clear()
    predefined_compensations.extend(request.json['pre_comp'])
    compensation_hierarchy.clear()
    compensation_hierarchy.extend(request.json['comp_hier'])
    return "rebooted", 200


@app.route("/getFeedback")
def pepper_reaction_logics():
    # preparations
    slow_movement = False
    # if request.args.get('speed') > 500:
    #     slow_movement = True
    compensations_analysis = {}
    comp_list = request.json['comps']
    num_of_compensation = 0
    current_session_compensations = []
    history_compensation_executed = 0
    for idx, val in enumerate(comp_list):
        compensations_analysis[comp_dic.get(idx)] = val

    feedback_in_last_three_sessions = False
    if len(feedback_hist) > 2:
        if feedback_hist[0] or feedback_hist[1] or feedback_hist[2]:
            feedback_in_last_three_sessions = True
    else:
        if True in feedback_hist:
            feedback_in_last_three_sessions = True

    if compensations_analysis['trunk-flex'] == 1:
        num_of_compensation += 1
        comp_hist['trunk-flex'] = comp_hist['trunk-flex'] + 1
        current_session_compensations.insert(0, "trunk-flex")
    if compensations_analysis['scapular-e'] == 1:
        num_of_compensation += 1
        comp_hist['scapular-e'] = comp_hist['scapular-e'] + 1
        current_session_compensations.insert(0, "scapular-e")
    if compensations_analysis['scapular-r'] == 1:
        num_of_compensation += 1
        comp_hist['scapular-r'] = comp_hist['scapular-r'] + 1
        current_session_compensations.insert(0, "scapular-r")
    if compensations_analysis['shoulder-flex'] == 1:
        num_of_compensation += 1
        comp_hist['shoulder-flex'] = comp_hist['shoulder-flex'] + 1
        current_session_compensations.insert(0, "shoulder-flex")
    if compensations_analysis['elbow-flex'] == 1:
        num_of_compensation += 1
        comp_hist['elbow-flex'] = comp_hist['elbow-flex'] + 1
        current_session_compensations.insert(0, "elbow-flex")
    if compensations_analysis['distal-dys-syn'] == 1:
        num_of_compensation += 1
        comp_hist['distal-dys-syn'] = comp_hist['distal-dys-syn'] + 1
        current_session_compensations.insert(0, "distal-dys-syn")
    for history_compensation_record in comp_hist:
        history_compensation_executed = history_compensation_executed + comp_hist[
            history_compensation_record]

    # Logics based on Feedback flowchart
    if compensations_analysis['success'] == 0:
        # A1
        print("A1")
        LAST_TRAIL_COMPENSATION = current_session_compensations
        return {"feedback": False, "route": "A1", "type": "null"}
    else:
        # A2
        print("A2")
        if not num_of_compensation > 0:
            feedback_hist.append(False)
            if len('fds') <= 0:
                print("50% visual + 50% verbal and visual")
                if VISUAL:
                    return {"feedback": True, "route": "**", "type": "good_movement_visual"}
                else:
                    return {"feedback": True, "route": "**", "type": "good_movement_verbal"}
            else:
                print("visual only + feedback on good movement")
                return {"feedback": True, "route": "**", "type": "good_movement_visual"}
        # # B1
        # print("B1")
        # if not slow_movement:
        #     # C1
        #     print("C1")
        #     return {"feedback": False, "route": "C1", "compensation": "null"}
        # else:
        #     # C2
        #     print("C2")
        #     if speed_feedback == 0:
        #         # D1
        #         print("D1")
        #         return {"feedback": False, "route": "D1", "compensation": "null"}
        #     else:
        #         # D2
        #         print("D2")
        #         return {"feedback": True, "route": "D2", "compensation": "null"}
        else:
            # B2
            feedback_hist.append(True)
            print("B2")
            num_of_predefined_compensation_executed = 0
            current_predefined_comp = []
            for compensation in current_session_compensations:
                if predefined_compensations[compensation]:
                    current_predefined_comp.insert(0, compensation)
            if len(current_predefined_comp) == 0:
                # E1
                print("E1")
                print("feedback on mission success - 50% visual + 50% verbal")
                # global LAST_TRAIL_COMPENSATION
                LAST_TRAIL_COMPENSATION = current_session_compensations
                if VISUAL:
                    return {"feedback": True, "route": "**", "type": "mission_success_visual"}
                else:
                    return {"feedback": True, "route": "**", "type": "mission_success_verbal"}
            else:
                # E2
                print("E2")
                if len(current_predefined_comp) == 1:
                    # F1
                    print("F1")
                    if comp_hist[current_session_compensations[0]] > 2:
                        # G2
                        print("G2")
                        if feedback_in_last_three_sessions:
                            # H2
                            print("H2")
                            # global LAST_TRAIL_COMPENSATION
                            LAST_TRAIL_COMPENSATION = current_session_compensations
                            return {"feedback": False, "route": "H2", "type": "null"}
                        else:
                            # H1
                            print("H1")
                            # global LAST_TRAIL_COMPENSATION
                            LAST_TRAIL_COMPENSATION = current_session_compensations
                            return {"feedback": True, "route": "H1", "type": current_session_compensations[0]}
                    else:
                        # G1
                        print("G1")
                        print("feedback on mission success - 50% visual + 50% verbal")
                        # global LAST_TRAIL_COMPENSATION
                        LAST_TRAIL_COMPENSATION = current_session_compensations
                        if VISUAL:
                            return {"feedback": False, "route": "G1", "type": "mission_success_visual"}
                        else:
                            return {"feedback": False, "route": "G1", "type": "mission_success_verbal"}
                else:
                    # F2
                    print("F2")
                    for key, value in compensation_hierarchy.items():
                        if compensation_hierarchy[key][key] in current_predefined_comp:
                            print(compensation_hierarchy[key][key])
                            if comp_hist[compensation_hierarchy[key][key]] > 1:
                                # I2
                                print("I2")
                                if feedback_in_last_three_sessions:
                                    # H2
                                    print("J2")
                                    # global LAST_TRAIL_COMPENSATION
                                    LAST_TRAIL_COMPENSATION = current_session_compensations
                                    return {"feedback": False, "route": "J2", "type": "null"}
                                else:
                                    # H1
                                    print("J1")
                                    # global LAST_TRAIL_COMPENSATION
                                    LAST_TRAIL_COMPENSATION = current_session_compensations
                                    print("feedback on mission success - 50% visual + 50% verbal")
                                    return {"feedback": True, "route": "J1",
                                            "compensation": compensation_hierarchy[key][key]}
                            else:
                                # I1
                                print("feedback on mission success - 50% visual + 50% verbal")
                                print("I1")
                                if VISUAL:
                                    return {"feedback": False, "route": "I1", "type": "mission_success_visual"}
                                else:
                                    return {"feedback": False, "route": "I1", "type": "mission_success_verbal"}

        # global LAST_TRAIL_COMPENSATION
        LAST_TRAIL_COMPENSATION = current_session_compensations
    return False


@app.route("/record_momvment")
def record_movement():
    print("start recording")
    # Start Recording

    app = application.Application(backend='win32').connect(path=r"C:\Program Files\OptiTrack\Motive\Motive.exe")
    # Open Motive App
    app.top_window().set_focus()
    time.sleep(0.5)
    # ShowWindow(w.wrapper_object(), 9)

    time.sleep(1)
    keyboard = Controller()

    # Change to Live Mode

    keyboard.press('3')
    time.sleep(1)

    # Press space to start recording

    keyboard.press(Key.space)
    return "Start recoreding :)", 200
    # print("waiting for button1")
    # ser.write(b'o')
    # rduinodata1 = ser.readlines()
    # ser.write(b'o')
    # arduinodata1 = ser.readlines()
    # print("button pressed")
    #
    # keyboard.press(Key.space)
    #
    # # Change to Edit mode in Motive
    # keyboard.press('4')
    #
    # # Export file to csv
    # ser.close()
    # time.sleep(0.6)
    # file_to_analyze_name = PATIENT_NAME + datetime.now().strftime("%H:%M:%S")
    # keyboard.press('5')
    # print(file_to_analyze_name)
    #
    # # Set csv file to patient name + exercise datetime
    # start = time.time()
    # print("hello")
    # time.sleep(0.8)
    # file_name = ""
    # for i in range(len(file_to_analyze_name)):
    #     keyboard.press(file_to_analyze_name[i])
    #     time.sleep(0.07)
    #     file_name = file_name + file_to_analyze_name[i]
    # time.sleep(0.6)
    # keyboard.press(Key.enter)
    # time.sleep(0.6)
    # keyboard.press(Key.enter)
    # end = time.time()
    # print(end - start)
    # return file_name


@app.route("/stop_recording")
def stop():
    app = application.Application(backend='win32').connect(path=r"C:\Program Files\OptiTrack\Motive\Motive.exe")
    # Open Motive App
    app.top_window().set_focus()
    keyboard = Controller()
    keyboard.press(Key.space)

    # Change to Edit mode in Motive
    keyboard.press('4')

    # Export file to csv

    time.sleep(0.6)
    file_to_analyze_name = PATIENT_NAME + datetime.now().strftime("%H:%M:%S")
    keyboard.press('5')
    print(file_to_analyze_name)

    # Set csv file to patient name + exercise datetime
    start = time.time()
    print("hello")
    time.sleep(0.8)
    file_name = ""
    for i in range(len(file_to_analyze_name)):
        keyboard.press(file_to_analyze_name[i])
        time.sleep(0.07)
        file_name = file_name + file_to_analyze_name[i]
    time.sleep(0.6)
    keyboard.press(Key.enter)
    time.sleep(0.6)
    keyboard.press(Key.enter)
    end = time.time()
    print(end - start)
    return file_name


@app.route("/analyze")
def analyze():
    file_to_analyze_name = request.args.get('filename')
    file_to_analyze_name = file_to_analyze_name.replace(":", "M")
    file_to_analyze_name = file_to_analyze_name.replace("\"", "\\")
    path = "C:\\Users\\ronit\\Documents\\OptiTrack\\Session 2021-03-24\\" + file_to_analyze_name + ".csv"

    # Open csv file and send to server in order to analyze

    # time.sleep(2)
    with open(path) as csv_file:
        file = csv.reader(csv_file, delimiter=',')
        marker_names = []
        marker_ids = []
        for i, row in enumerate(file):
            if i == 2:
                marker_ids = row
            if i == 3:
                # take all  marker names from xls file of the current motion (with the same order)
                marker_names = row
                break

        last_marker = ""
        selected_markers_names = ["Skeleton 006:sternum 1", "Skeleton 006:sternum 2", "Skeleton 006:shoulder",
                                  "Skeleton 006:humerus", "Skeleton 006:elbow", "Skeleton 006:forearm",
                                  "Skeleton 006:radial", "Skeleton 006:ulnar", "Skeleton 006:wrist",
                                  "Skeleton 006:thumb", "Skeleton 006:index"]
        relevant_rows = [0, 1]
        for marker_type, marker_name in zip(marker_ids, marker_names):
            if marker_name in selected_markers_names and last_marker != marker_name and marker_type == "Bone Marker":
                relevant_rows.append(int(marker_names.index(marker_name)))
                relevant_rows.append(int(marker_names.index(marker_name)) + 1)
                relevant_rows.append(int(marker_names.index(marker_name)) + 2)
            last_marker = marker_name
    data = pd.read_csv(f'{path}', usecols=relevant_rows, skiprows=[0, 1, 2], index_col=0)
    data.to_csv('data.csv')
    blank_row = pd.DataFrame([[np.nan] * len(data.columns)], columns=data.columns)
    df = blank_row.append(data)
    df.to_csv('df.csv')
    df1 = blank_row.append(df)
    df2 = blank_row.append(df1)

    # path = "\TestMovement\test.csv"  # comment this line when in lab
    df2.to_csv('analyze.csv')
    path = ".\\analyze.csv"
    files = {'data_file': open(path)}
    r = requests.get('http://127.0.0.1:5000/testdata', files=files)
    print(r.json()['results'][0])
    return {"res": r.json()['results'][0]}, 200


if __name__ == '__main__':
    app.run(host="localhost", port=8001, debug=True)
