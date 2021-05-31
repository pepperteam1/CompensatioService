import numpy as np
import serial
import time
import requests
import os
import csv
import pandas as pd
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

from pywinauto import application
from pywinauto.win32functions import ShowWindow
from pynput.keyboard import Key, Controller
from tkinter import *
from tkinter import ttk
import tkinter
from tkinter import filedialog
import json
from datetime import datetime
import tkinter.font as font
from PIL import ImageTk, Image
from Functionalities import pepper_reaction_logics, record_movement
import xlwt
from xlwt import Workbook
import matplotlib.pyplot as plt

# ser = serial.Serial('COM3', 9600, timeout=1)
PATIENT_NAME = ""
COMPENSATION_HIERARCHY = {}
PREDEFINED_COMPENSATIONS = {"trunk-flex": True, "scapular-e": True, "scapular-r": True, "shoulder-flex": True,
                            "elbow-flex": True,
                            "distal-dys-syn": True}
window = Tk()
SPEED_FEEDBACK = False
PREDEFINED_COMPENSATIONS_CHECKBOX = False
REPORT_FOLDER_PATH = ""
COMPENSATIONS_HISTORY = {"trunk-flex": 0, "scapular-e": 0, "scapular-r": 0, "shoulder-flex": 0, "elbow-flex": 0,
                         "distal-dys-syn": 0}

FEEDBACK_BY_COMPENSATION_HISTORY = {"trunk-flex": 0, "scapular-e": 0, "scapular-r": 0, "shoulder-flex": 0,
                                    "elbow-flex": 0,
                                    "distal-dys-syn": 0}
FEEDBACK_HISTORY = []
PATIENT_GENDER = ""


def run_another_trail():
    os.system("python -m pepper_handler trail_beginning")
    data = record_movement()

    flowchart_results = pepper_reaction_logics(data, COMPENSATIONS_HISTORY, SPEED_FEEDBACK,
                                               PREDEFINED_COMPENSATIONS,
                                               FEEDBACK_HISTORY, COMPENSATION_HIERARCHY)
    if flowchart_results["feedback"]:
        # feedback_request = requests.get("http://127.0.0.1:8001/react/", flowchart_results)
        print()


def save_session_data():
    wb = Workbook()
    row_index = 0
    col_index = 0
    # add_sheet is used to create sheet.
    sheet1 = wb.add_sheet('Sheet 1')

    patient = ""
    with open('patients_labels.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            compensations = row[0].split(',')
            if not patient == compensations[0]:
                sheet1.write(0, col_index + 1, compensations[0])
                col_index += 1
                patient = compensations[0]
                row_index = 1
                global FEEDBACK_HISTORY
                FEEDBACK_HISTORY = []
                global COMPENSATIONS_HISTORY
                COMPENSATIONS_HISTORY.clear()
                COMPENSATIONS_HISTORY = {"trunk-flex": 0, "scapular-e": 0, "scapular-r": 0, "shoulder-flex": 0,
                                         "elbow-flex": 0,
                                         "distal-dys-syn": 0}

            data = {"trunk-flex": int(compensations[1]), "scapular-e": int(compensations[2]),
                    "scapular-r": int(compensations[3]),
                    "shoulder-flex": int(compensations[4]), "elbow-flex": int(compensations[5]),
                    "distal-dys-syn": int(compensations[6]), "speed": 120, "success": 1}
            FEEDBACK_HISTORY.insert(0, pepper_reaction_logics(data, COMPENSATIONS_HISTORY, SPEED_FEEDBACK,
                                                              PREDEFINED_COMPENSATIONS,
                                                              FEEDBACK_HISTORY, COMPENSATION_HIERARCHY))
            print("-------------------------------------")
            sheet1.write(row_index, col_index, FEEDBACK_HISTORY[0])
            row_index += 1

    wb.save('feedback_analysis.xls')


def run_trail():
    file_to_analyze_name = record_movement()

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
    return r


def end_session():
    save_session_data()
    pepper_show_emojis_reaction = {'feedback': True, 'route': "Show Emojis"}
    # feedback_request = requests.get("http://127.0.0.1:8001/react/", pepper_show_emojis_reaction)

    # TODO: collect patient reaction to emojis board


def start_game(patient_name):
    PATIENT_NAME = patient_name
    window.withdraw()

    pepper_start_game_reaction = {'feedback': True, 'route': "Trail Beginning"}
    os.system("python -m pepper_handler a ")
    # feedback_request = requests.get("http://127.0.0.1:8001/react/", pepper_start_game_reaction)

    pepper_show_emojis_reaction = {'feedback': True, 'route': "Show Emojis"}
    # feedback_request = requests.get("http://127.0.0.1:8001/react/", pepper_show_emojis_reaction)

    # TODO: collect patient reaction to emojis board

    r = run_trail()

    if r.status_code == 200:
        results = r.json()['results'][0]
        data = {"trunk-flex": int(results[0]), "scapular-e": int(results[1]),
                "scapular-r": int(results[2]),
                "shoulder-flex": int(results[3]), "elbow-flex": int(results[4]),
                "distal-dys-syn": int(results[5]), "speed": 120, "success": 1}
        os.system("python -m pepper_handler b")
        #feedback = pepper_reaction_logics(data, COMPENSATIONS_HISTORY, SPEED_FEEDBACK, PREDEFINED_COMPENSATIONS,
                                          #FEEDBACK_HISTORY, COMPENSATION_HIERARCHY)
        #if feedback["Feedback"]:
           # os.system("python -m pepper_handler " + feedback["type"])
    elif r.status_code == 400:
        os.system("python -m pepper_handler b")
        # os.system("python -m pepper_handler try_again")
        # run_trail()

    another_session = True
    # TODO: get reaction from patient about another session
    while another_session:
        # run_another_session()
        print()
        another_session = False
        # TODO: get reaction from patient about another session
    # end_session()

    window.deiconify()

    #
    # Get predictions from the algorithm
    # predictions = r.json()
    # data = {}
    # data['trunk-flex'] = 1
    # data['scapular-e'] = 0
    # data['scapular-r'] = 0
    # data['shoulder-flex'] = 1
    # data['elbow-flex'] = 1
    # data['distal-dys-syn'] = 0
    # data['speed'] = 1400

    ##############################FEEDBACK ANALYSIS######################
    # # Workbook is created
    # wb = Workbook()
    # row_index = 0
    # col_index = 0
    # # add_sheet is used to create sheet.
    # sheet1 = wb.add_sheet('Sheet 1')
    #
    # patient = ""
    # with open('patients_labels.csv', newline='') as csvfile:
    #     reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    #     for row in reader:
    #         compensations = row[0].split(',')
    #         if not patient == compensations[0]:
    #             sheet1.write(0, col_index + 1, compensations[0])
    #             col_index += 1
    #             patient = compensations[0]
    #             row_index = 1
    #             global FEEDBACK_HISTORY
    #             FEEDBACK_HISTORY = []
    #             global COMPENSATIONS_HISTORY
    #             COMPENSATIONS_HISTORY.clear()
    #             COMPENSATIONS_HISTORY = {"trunk-flex": 0, "scapular-e": 0, "scapular-r": 0, "shoulder-flex": 0,
    #                                      "elbow-flex": 0,
    #                                      "distal-dys-syn": 0}
    #
    #         data = {"trunk-flex": int(compensations[1]), "scapular-e": int(compensations[2]),
    #                 "scapular-r": int(compensations[3]),
    #                 "shoulder-flex": int(compensations[4]), "elbow-flex": int(compensations[5]),
    #                 "distal-dys-syn": int(compensations[6]), "speed": 120, "success": 1}
    #         FEEDBACK_HISTORY.insert(0, pepper_reaction_logics(data, COMPENSATIONS_HISTORY, SPEED_FEEDBACK,
    #                                                           PREDEFINED_COMPENSATIONS,
    #                                                           FEEDBACK_HISTORY, COMPENSATION_HIERARCHY))
    #         print("-------------------------------------")
    #         sheet1.write(row_index, col_index, FEEDBACK_HISTORY[0])
    #         row_index += 1
    #
    # wb.save('feedback_analysis.xls')
    #########################################################################

    # Operate Pepper according to predictions

    # flowchart_results = pepper_reaction_logics(data, COMPENSATIONS_HISTORY, SPEED_FEEDBACK,
    #                                            PREDEFINED_COMPENSATIONS,
    #                                            FEEDBACK_HISTORY, COMPENSATION_HIERARCHY)
    # if flowchart_results["feedback"]:
    #     feedback_request = requests.get("http://127.0.0.1:8001/react/", flowchart_results)
    # os.system("python -m pepper_handler trunk_flex")


# GUI initialization
myFont = font.Font(family='Bahnschrift Light', size=14, weight='bold')
lbl = Label(window, text="Please enter the patient's details:", fg='black', font=myFont)
lbl.place(x=150, y=20)
txtfld = Entry(window, text="This is Entry Widget", borderwidth=4, relief="ridge")
txtfld.place(x=140, y=150)
lbl2 = Label(window, text="Name: ", fg='black', font=myFont)
lbl2.place(x=40, y=150)

lbl3 = Label(window, text="Gender: ", fg='black', font=myFont)
lbl3.place(x=40, y=200)
gender = StringVar(window)
gender_options = OptionMenu(window, gender, "Male", "Female")
PATIENT_GENDER = gender.get()
print()
txtfld = Entry(window, text="This is Entry Widget", borderwidth=4, relief="ridge")
txtfld.place(x=140, y=100)
lbl2 = Label(window, text="ID: ", fg='black', font=myFont)
lbl2.place(x=60, y=100)

gender_options.place(x=170, y=200)


def change_compensation_predefined(compensation, var):
    if var.get == 0:
        PREDEFINED_COMPENSATIONS[compensation] = True
    else:
        PREDEFINED_COMPENSATIONS[compensation] = False


def change_predefined_status():
    if predefined_compensations_checkbox_var.get() == 1:
        PREDEFINED_COMPENSATIONS_CHECKBOX = True
        checkbox_trunk_flex_var = IntVar()
        checkbox_trunk_flex_var.set(1)
        checkbox_trunk_flex = Checkbutton(window, text='trunk-flex', onvalue=1, offvalue=0,
                                          variable=checkbox_trunk_flex_var,
                                          command=lambda: change_compensation_predefined(compensation='trunk-flex',
                                                                                         var=checkbox_trunk_flex_var))
        checkbox_trunk_flex.place(x=20 + 30, y=270)
        checkbox_scapular_e_var = IntVar()
        checkbox_scapular_e_var.set(1)
        checkbox_scapular_e = Checkbutton(window, text='scapular-e', onvalue=1, offvalue=0,
                                          variable=checkbox_scapular_e_var,
                                          command=lambda: change_compensation_predefined(compensation='scapular-e',
                                                                                         var=checkbox_scapular_e_var))
        checkbox_scapular_e.place(x=130 + 30, y=270)
        checkbox_scapular_r_var = IntVar()
        checkbox_scapular_r_var.set(1)
        checkbox_scapular_r = Checkbutton(window, text='scapular-r', onvalue=1, offvalue=0,
                                          variable=checkbox_scapular_r_var,
                                          command=lambda: change_compensation_predefined(compensation='scapular-r',
                                                                                         var=checkbox_scapular_r_var))
        checkbox_scapular_r.place(x=240 + 30, y=270)
        checkbox_shoulder_flex_var = IntVar()
        checkbox_shoulder_flex_var.set(1)
        checkbox_shoulder_flex = Checkbutton(window, text='shoulder-flex', onvalue=1, offvalue=0,
                                             variable=checkbox_shoulder_flex_var,
                                             command=lambda: change_compensation_predefined(
                                                 compensation='shoulder-flex',
                                                 var=checkbox_shoulder_flex_var))
        checkbox_shoulder_flex.place(x=350 + 30, y=270)
        checkbox_elbow_flex_var = IntVar()
        checkbox_elbow_flex_var.set(1)
        checkbox_elbow_flex = Checkbutton(window, text='elbow-flex', onvalue=1, offvalue=0,
                                          variable=checkbox_elbow_flex_var,
                                          command=lambda: change_compensation_predefined(compensation='elbow-flex',
                                                                                         var=checkbox_elbow_flex_var))
        checkbox_elbow_flex.place(x=480 + 30, y=270)
        checkbox_distal_dys_syn_var = IntVar()
        checkbox_distal_dys_syn_var.set(1)
        checkbox_distal_dys_syn = Checkbutton(window, text='distal-dys-syn', onvalue=1, offvalue=0,
                                              variable=checkbox_distal_dys_syn_var,
                                              command=lambda: change_compensation_predefined(
                                                  compensation='distal-dys-syn',
                                                  var=checkbox_distal_dys_syn_var))
        checkbox_distal_dys_syn.place(x=590 + 30, y=270)
    else:
        PREDEFINED_COMPENSATIONS_CHECKBOX = False
        checkbox_trunk_flex = Checkbutton(window, text='trunk-flex', onvalue=1, offvalue=0, state=DISABLED)
        checkbox_trunk_flex.place(x=20 + 30, y=270)
        checkbox_scapular_e = Checkbutton(window, text='scapular-e', onvalue=1, offvalue=0, state=DISABLED)
        checkbox_scapular_e.place(x=130 + 30, y=270)
        checkbox_scapular_r = Checkbutton(window, text='scapular-r', onvalue=1, offvalue=0, state=DISABLED)
        checkbox_scapular_r.place(x=240 + 30, y=270)
        checkbox_shoulder_flex = Checkbutton(window, text='shoulder-flex', onvalue=1, offvalue=0, state=DISABLED)
        checkbox_shoulder_flex.place(x=350 + 30, y=270)
        checkbox_elbow_flex = Checkbutton(window, text='elbow-flex', onvalue=1, offvalue=0, state=DISABLED)
        checkbox_elbow_flex.place(x=480 + 30, y=270)
        checkbox_distal_dys_syn = Checkbutton(window, text='distal-dys-syn', onvalue=1, offvalue=0, state=DISABLED)
        checkbox_distal_dys_syn.place(x=590 + 30, y=270)
        global PREDEFINED_COMPENSATIONS

        PREDEFINED_COMPENSATIONS = {"trunk-flex": True, "scapular-e": True, "scapular-r": True, "shoulder-flex": True,
                                    "elbow-flex": True,
                                    "distal-dys-syn": True}
        print("")


# Predefined compensation configuration
predefined_compensations_checkbox_var = IntVar()
predefined_compensations_checkbox = Checkbutton(window, text='Predefine Compensation', onvalue=1, offvalue=0,
                                                variable=predefined_compensations_checkbox_var,
                                                command=change_predefined_status)

predefined_compensations_checkbox.place(x=480, y=150)


# Movement Speed configuration
def change_speed_feedback_status():
    if (movement_speed_feedback_var.get() == 1):
        SPEED_FEEDBACK = False
    else:
        SPEED_FEEDBACK = True


movement_speed_feedback_var = IntVar()
movement_speed_feedback_checkbox = Checkbutton(window, text='Movement Speed Feedback', onvalue=1, offvalue=0,
                                               variable=movement_speed_feedback_var,
                                               command=change_speed_feedback_status)

movement_speed_feedback_checkbox.place(x=480, y=100)

lbl = Label(window, text="Compensation Hierarchy", fg='black', font=myFont)
lbl.place(x=45, y=300)
s = ttk.Style()
s.configure('Treeview', rowheight=32)

compensation_hierarchy_treeview = ttk.Treeview(window)
compensation_hierarchy_treeview['columns'] = ("Compensation")
compensation_hierarchy_treeview.column("#0", width=0, minwidth=0)
compensation_hierarchy_treeview.column("Compensation", anchor=CENTER, width=200)

compensation_hierarchy_treeview.heading("#0", text="Rank", anchor=CENTER)
compensation_hierarchy_treeview.heading("Compensation", text="Compensation", anchor=CENTER)

compensation_hierarchy_treeview.insert(parent='', index='end', iid=0, text="", values=("trunk-flex"))
compensation_hierarchy_treeview.insert(parent='', index='end', iid=1, text="", values=("scapular-e"))
compensation_hierarchy_treeview.insert(parent='', index='end', iid=2, text="", values=("scapular-r"))
compensation_hierarchy_treeview.insert(parent='', index='end', iid=3, text="", values=("shoulder-flex"))
compensation_hierarchy_treeview.insert(parent='', index='end', iid=4, text="", values=("elbow-flex"))
compensation_hierarchy_treeview.insert(parent='', index='end', iid=5, text="", values=("distal-dys-syn"))

compensation_hierarchy_treeview.place(x=100, y=350)


def update_hierarchy():
    index = 1
    listOfEntriesInTreeView = compensation_hierarchy_treeview.get_children()
    COMPENSATION_HIERARCHY.clear()
    for each in listOfEntriesInTreeView:
        compensation = str(compensation_hierarchy_treeview.item(each)['values'])
        compensation = compensation.replace('[', '')
        compensation = compensation.replace(']', '')
        compensation = compensation.replace("'", "")
        COMPENSATION_HIERARCHY[index] = {index: compensation}
        print(COMPENSATION_HIERARCHY[index])
        index = index + 1


def up():
    rows = compensation_hierarchy_treeview.selection()
    for row in rows:
        compensation_hierarchy_treeview.move(row, compensation_hierarchy_treeview.parent(row),
                                             compensation_hierarchy_treeview.index(row) - 1)
    update_hierarchy()


def down():
    rows = compensation_hierarchy_treeview.selection()
    for row in reversed(rows):
        compensation_hierarchy_treeview.move(row, compensation_hierarchy_treeview.parent(row),
                                             compensation_hierarchy_treeview.index(row) + 1)
    update_hierarchy()


up_btn = PhotoImage(file="button_img/UP.png")
down_btn = PhotoImage(file="button_img/DOWN.png")
history_btn = PhotoImage(file="button_img/History.png")
start_btn = PhotoImage(file="button_img/START.png")
pepper_photo = PhotoImage(file="button_img/Pepper_8.png")
panel = Label(window, image=pepper_photo)
panel.place(x=390, y=330)
move_compensation_up = Button(window, command=up, image=up_btn, borderwidth=0)
move_compensation_down = Button(window, command=down, image=down_btn, borderwidth=0)
move_compensation_up.place(x=350, y=425)
move_compensation_down.place(x=350, y=500)

btn = Button(window, image=start_btn, borderwidth=0, command=lambda: start_game(txtfld.get()))
btn.place(x=475, y=714)


# img = Image.open("Rank - project.png")
# test = ImageTk.PhotoImage(img)
#
# img_label = Label(window, image=test)
# img_label.image = test
#
# img_label.place(x=10, y=370)


def data_visualization():
    global data_visualization_window
    data_visualization_window = Toplevel(window)
    data_visualization_window.geometry("410x300")
    data_visualization_window.title("Data Visualization")
    patient = StringVar(data_visualization_window)
    patient.set("")
    directory = os.fsencode("History")
    all_patients = []
    graphs = StringVar(data_visualization_window)
    graphs.set("")
    graph_options = ["Compensations Overview", "Speed Overview", "Game Overview", "Patient Feedback Overview"]
    lbl3 = Label(data_visualization_window, text="Select a patient: ", fg='black', font=myFont)
    lbl3.config(font=(myFont, 10))
    lbl3.place(x=50, y=90)

    def show_graph(selected_graph):
        if selected_graph == "Compensations Overview":
            print("Compensations Overview")
            with open(f"History\{patient.get()}") as fin:
                first_row = True
                total_trunk_flex = 0
                total_scapular_e = 0
                total_scapular_r = 0
                total_elbow_flex = 0
                total_shoulder_flex = 0
                total_dystal_sys_ = 0
                for row in csv.reader(fin):
                    if first_row:
                        first_row = False
                    else:
                        total_trunk_flex += int(row[3])
                        total_scapular_e += int(row[4])
                        total_scapular_r += int(row[5])
                        total_elbow_flex += int(row[6])
                        total_shoulder_flex += int(row[7])
                        total_dystal_sys_ += int(row[8])
            first_row = True
            df = pd.DataFrame(
                {'': ['trunk flex', 'scapular e', 'scapular r', 'elbow flex', 'shoulder flex', 'dystal sys'],
                 'total': [total_trunk_flex, total_scapular_e, total_scapular_r, total_elbow_flex, total_shoulder_flex,
                           total_dystal_sys_]})
            ax = df.plot.bar(x='', y='total', rot=0, figsize=(12, 5))
            plt.xlabel('Compensations name')
            plt.ylabel('Number of times')
            plt.show()
            plt.close()


        elif selected_graph == "Speed Overview":
            with open(f"History\{patient.get()}") as fin:
                first_row = True
                session = []
                speed = []
                for row in csv.reader(fin):
                    if first_row:
                        first_row = False
                    else:
                        session.append(row[1])
                        speed.append(int(row[9]))
            first_row = True

            df = pd.DataFrame({'speed': speed, '': session})
            df.plot.bar(x='', y='speed', rot=0, figsize=(12, 5))
            plt.xlabel('Session date')
            plt.ylabel('Patient speed')
            plt.show()
            plt.close()


        elif selected_graph == "Game Overview":
            print("Game Overview")
        elif selected_graph == "Patient Feedback Overview":
            with open(f"History\{patient.get()}") as fin:
                first_row = True
                session = []
                feedback = []
                for row in csv.reader(fin):
                    if first_row:
                        first_row = False
                    else:
                        session.append(row[1])
                        feedback.append(int(row[11]))
            first_row = True

            df = pd.DataFrame({'feedback': feedback, '': session})
            df.plot.bar(x='', y='feedback', rot=0, figsize=(12, 5))
            plt.xlabel('Session date')
            plt.ylabel('Patient feedback')
            plt.show()
            plt.close()

    # def show_graph(selected_graph):
    #     fig = Figure(figsize=(9, 9),
    #                  dpi=100)
    #     plot1 = fig.add_subplot(111)
    #     canvas = FigureCanvasTkAgg(fig,
    #                                master=data_visualization_window)
    #     canvas.get_tk_widget().pack()
    #
    #     if selected_graph == "Compensations Overview":
    #         print("Compensations Overview")
    #         with open(f"History\{patient.get()}") as fin:
    #             first_row = True
    #             total_trunk_flex = 0
    #             total_scapular_e = 0
    #             total_scapular_r = 0
    #             total_elbow_flex = 0
    #             total_shoulder_flex = 0
    #             total_dystal_sys_ = 0
    #             for row in csv.reader(fin):
    #                 if first_row:
    #                     first_row = False
    #                 else:
    #                     total_trunk_flex += int(row[3])
    #                     total_scapular_e += int(row[4])
    #                     total_scapular_r += int(row[5])
    #                     total_elbow_flex += int(row[6])
    #                     total_shoulder_flex += int(row[7])
    #                     total_dystal_sys_ += int(row[8])
    #         first_row = True
    #         # the figure that will contain the plot
    #
    #         df = pd.DataFrame(
    #             {'': ['trunk flex', 'scapular_e', 'scapular_r', 'elbow_flex', 'shoulder_flex', 'dystal_sys'],
    #              'total': [total_trunk_flex, total_scapular_e, total_scapular_r, total_elbow_flex, total_shoulder_flex,
    #                        total_dystal_sys_]})
    #         df.plot.bar(x='', y='total', rot=0, ax=plot1)
    #         plot1.set_title('Year Vs. Unemployment Rate')
    #         # canvas.draw()
    #         #
    #         # # placing the canvas on the Tkinter window
    #         # canvas.get_tk_widget().pack()
    #         #
    #         # # creating the Matplotlib toolbar
    #         # toolbar = NavigationToolbar2Tk(canvas,
    #         #                                data_visualization_window)
    #         # toolbar.update()
    #         #
    #         # # placing the toolbar on the Tkinter window
    #         # canvas.get_tk_widget().pack()
    #
    #     elif selected_graph == "Speed Overview":
    #         with open(f"History\{patient.get()}") as fin:
    #             first_row = True
    #             session = []
    #             speed = []
    #             for row in csv.reader(fin):
    #                 if first_row:
    #                     first_row = False
    #                 else:
    #                     session.append(row[1])
    #                     speed.append(int(row[9]))
    #         first_row = True
    #
    #         # df = pd.DataFrame({'total': speed, '': session})
    #         # df.plot.bar(x='', y='total', rot=0, figsize=(18, 5))
    #         # plt.show()
    #         # plt.close()
    #
    #         # the figure that will contain the plot
    #         # fig = Figure(figsize=(9, 9),
    #         #              dpi=100)
    #         # plot1 = fig.add_subplot(111)
    #         # canvas = FigureCanvasTkAgg(fig,
    #         #                            master=data_visualization_window)
    #         # canvas.get_tk_widget().pack()
    #         df = pd.DataFrame({'total': speed, '': session})
    #         df.plot.bar(x='', y='total', rot=0,ax=plot1)
    #         plot1.set_title('Year Vs. Unemployment Rate')
    #
    #
    #         # canvas.draw()
    #         #
    #         # # placing the canvas on the Tkinter window
    #         # canvas.get_tk_widget().pack()
    #         #
    #         # # creating the Matplotlib toolbar
    #         # toolbar = NavigationToolbar2Tk(canvas,
    #         #                                data_visualization_window)
    #         # toolbar.update()
    #         #
    #         # # placing the toolbar on the Tkinter window
    #         # canvas.get_tk_widget().pack()
    #         # canvas.close_event()
    #
    #
    #     elif selected_graph == "Game Overview":
    #         print("Game Overview")
    #     elif selected_graph == "Patient Feedback Overview":
    #         print("Patient Feedback Overview")

    graph_options_options = OptionMenu(data_visualization_window, graphs, *graph_options, command=show_graph)

    def set_patient_name(selected_patient):
        print(selected_patient)

        # graph_options_options.grid(row=20, column=0, padx=20)
        lbl6 = Label(data_visualization_window, text="Select a graph: ", fg='black', font=myFont)
        lbl6.config(font=(myFont, 10))
        lbl6.place(x=50, y=150)
        graph_options_options.place(x=200, y=150)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        all_patients.insert(0, filename)
    patient_options = OptionMenu(data_visualization_window, patient, *(all_patients),
                                 command=set_patient_name)
    # patient_options.grid(row=19, column=0, padx=20)
    patient_options.place(x=200, y=90)


report_folder_browser_button = Button(text="History Data Center", image=history_btn, borderwidth=0
                                      , command=data_visualization)
report_folder_browser_button.place(x=0, y=710)
window.title('Pepper - social robot')
window.geometry("800x820+10+10")
window.mainloop()

# patient_name_entry = Entry(root, width=20, borderwidth=5)
# patient_name_entry.insert(0, "Please Enter Your Name:")
# patient_name_entry.pack()
# start_game_button = Button(root, text="Start Game", command=lambda: startGame(patient_name_entry.get()))
# start_game_button.pack()
# root.mainloop()

#
# class Tags(object):
#     def __init__(self):
#         self.running = True
#         self.threads = []
#
#     def getValues(self, q, LevelNumber):  # checks the order of the cups
#         arduinodata1 = [];
#         arduinodata = []
#         #        ser.open()
#         ser.write(b'o')
#         arduinodata1 = ser.readlines()
#         arduinodata1 = (x for x in arduinodata1 if
#                         "Reader" in x)
#         # delete all the unessery data that was in the serial
#         arduinodata1 = [i.split('\r\n', 1)[0] for i in arduinodata1]
#         ser.write(b'o')
#         arduinodata1 = ser.readlines()
#         print("push")
#
#         # START RECORDING
#
#         # dsock = rx.mkdatasock()
#         # version = (3, 1, 0, 0)  # NatNet version to use
#         # while True:
#         #     data = dsock.recv(rx.MAX_PACKETSIZE)
#         #     print data
#         #     print ("1")
#         #     packet = rx.unpack(data, version=version)
#         #     if type(packet) is rx.SenderData:
#         #         version = packet.natnet_version
#         #     print packet
#         ser.write(b'o')
#         arduinodata1 = ser.readlines()
#         arduinodata1 = (x for x in arduinodata1 if
#                         "Reader" in x)
#         # delete all the unessery data that was in the serial
#         arduinodata1 = [i.split('\r\n', 1)[0] for i in arduinodata1]
#         ser.write(b'o')
#         arduinodata1 = ser.readlines()
#         print("push2")
#
#         # END RECORDING AND SEND TO ALGORITHM
#
#
# q = []
# tag = Tags()
#
# tag.getValues(q, 2)
