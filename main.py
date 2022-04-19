import itertools as iter
import tkinter as tk
import pandas as pd
from PIL import ImageTk, Image
from tkinter.filedialog import askopenfile, askopenfilenames
import re, datetime
from datetime import datetime
import math
from functionshannah import merger, sw_cleanup, og_cleanup, smart_check


# FUNCTIONS=========================================================================================================

# open file function
def callCleanRev():
    x1 = " "
    file = askopenfile(parent=root, mode='r', title="choose a file")
    x1 = file.name  # This is getting the exact file address
    completeLabel = tk.Label(root, text=file.name + "has been processed", fg="Blue")
    completeLabel.place_forget()
    eStr1 = e1.get()   # These are getting the inputs from Entry boxes 1-3
    eStr2 = e2.get()
    eStr3 = e3.get()
    intCheck()
    if intCheck() == True:
        if x1.endswith(".csv"):
            completeLabel.place_forget()
            eStr3= int(eStr3)
            clean_rev(x1, eStr1, eStr2, eStr3)
            completeLabel.place(x=60,y=300)
        else:
            newWindow = tk.Toplevel(root)
            newWindow.geometry("350x50")
            completeLabel2 = tk.Label(newWindow, text="WRONG FILE TYPE: please select a CSV file (.csv)", fg="red", font="bold")
            completeLabel2.pack()
    else:
        print("Entry Error")
        completeLabel.place_forget()
        newWindow = tk.Toplevel(root)
        newWindow.geometry("350x50")
        completeLabel2 = tk.Label(newWindow, text="Entry Error: Please enter numeric values ONLY", fg="red", font="bold")
        completeLabel2.pack()
    browse_text.set("Run")


def clean_rev(x, m1, m2, y):
    # This loads the CSV file into the console
    df1 = pd.read_csv(x)
    df1.columns = [
        'Posted_Dt',
        'Doc_Dt',
        'Doc',
        'Memo / Description',
        'Department',
        'Location',
        'Contract',
        'Customer Name',
        'JNL',
        'Curr',
        'Txn Amt',
        'Debit',
        'Credit',
        'Balance (USD)'
    ]
    df1 = df1.fillna(0)
    df1["Total Billed"] = df1.Credit - df1.Debit
    df1.drop(df1[df1['Memo / Description'] == 0].index, inplace=True)
    df1['Posted_Dt'] = pd.DatetimeIndex(df1['Posted_Dt']).month
    pivot1 = pd.pivot_table(df1, index=['Contract', 'Customer Name'],columns='Posted_Dt',values='Total Billed',aggfunc='sum')
    df2 = pd.DataFrame(pivot1.to_records())
    df2 = df2.fillna(0)
    df2["Variance"] = df2[m1] - df2[m2]
    df_final = df2[(df2.Variance >= y) | (df2.Variance <= -y)]
    df_final.to_csv(x)


def callPaymatch():
    file = askopenfile(parent=root, mode='r', title="choose a file")
    x1 = file.name  # This is getting the exact file address
    instructions2 = tk.Label(frame2, text=x1, font="helvetica 12 bold", bg="#F0F0F0")
    instructions2.place(x=180, y=120)
    if x1.endswith(".csv"):
        data = pd.read_csv(x1)
        df1 = data[['Invoice number', 'Total transaction amount due']]
        df1['Total transaction amount due'] = df1['Total transaction amount due'].replace('[$,)]', '', regex=True).replace('[£,)]', '', regex=True)
        df1['Total transaction amount due'] = df1['Total transaction amount due'].replace('[(]', '-', regex=True)
        df1['Total transaction amount due'] = df1['Total transaction amount due'].astype(float)
        df2 = df1[(df1['Total transaction amount due'] != 0)]
        df2 = df2.set_index('Invoice number')
        dic = df2.T.to_dict('list')
        for x in dic:
            dic[x] = str(dic[x]).replace("[", '').replace("]", '')
            dic[x] = float(dic[x])
        eStr4 = e4.get()
        eStr4 = float(eStr4)
        paymatch(dic, eStr4)
    else:
        newWindow = tk.Toplevel(root)
        newWindow.geometry("350x50")
        completeLabel2 = tk.Label(newWindow, text="WRONG FILE TYPE: please select a CSV file (.csv)", fg="red", font="bold")
        completeLabel2.pack()


def paymatch(dictionary_pandas, target_value):

    result_window = tk.Toplevel(root,padx="50")

    x = 0
    for i in range(2,len(dictionary_pandas)+1):
        combination_objt = iter.combinations(dictionary_pandas, i)
        combinations_list= list(combination_objt)
        for j in combinations_list:
            count1 = i - 1
            checker1 = 0
            invoices = []
            while count1 >-1:
                checker1 = checker1 + dictionary_pandas[j[count1]] # <----- ADDITION STEP we have to round up here
                invoices.append(j[count1])
                count1 = count1 - 1

            if round(checker1, 2) == target_value:
                print(invoices)
                x = 1
                completeLabel3 = tk.Label(result_window, text= str(invoices)+"<---", fg="black", font="bold")
                completeLabel3.pack()
                fillerLabel = tk.Label(result_window)
                fillerLabel.pack()

    if x == 0:
        completeLabel2 = tk.Label(result_window, text="ENTRY ERROR: No result found", fg="red", font="bold", pady= 10)
        completeLabel2.pack()


def callrevRaquel():

    x1 = " "
    file = askopenfile(parent=root, mode='r', title="choose a file")
    x1 = file.name  # This is getting the exact file address
    if x1.endswith(".xlsx"):
        revRaquel(x1)
        completeLabel = tk.Label(root, text=file.name + "has been processed", fg="Blue")
        completeLabel.place_forget()
        completeLabel.place(x=20,y=300)
    else:
        print("Entry Error")

        newWindow = tk.Toplevel(root)
        newWindow.geometry("350x50")
        completeLabel2 = tk.Label(newWindow, text="WRONG FILE TYPE: please select an Excel file (.xlsx)", fg="red", font="bold")
        completeLabel2.pack()


def revRaquel(x):
    # Import the excel file that needs to have dates adjusted
    data1 = pd.read_excel(x)
    # Drop 1st column since it doesn't have useful information
    data1.pop(data1.columns[0])
    # Create new column which will store the "cleaned dates"
    data1['Date (clean)'] = None
    # To have easy access to the taget columns
    index_description = data1.columns.get_loc('Computation memo')
    index_date = data1.columns.get_loc('Date (clean)')
    #  This for-loop looks for the first date on each box under Computation Memo column and send the new value to Date (clean)
    for row in range(0, len(data1)):
        date = re.search(r'([0-9]{2}\/[0-9]{2}\/[0-9]{4})', data1.iat[row, index_description]).group()
        data1.iat[row, index_date] = date
    data1.to_excel(x)


def callHannah():

    file1 = askopenfile(parent=root, mode='r', title="choose a file")
    eraserLabel = tk.Label(root,
                           text="                                                                                                                                                                           ")
    eraserLabel.place(x=50, y=300)
    if file1.name.endswith(".csv"):
        hannahsACT(file1)
        completeLabel = tk.Label(root, text=file1.name + "  has been processed.", fg="Blue")
        completeLabel.place_forget()
        completeLabel.place(x=50, y=300)
    else:
        error1Label = tk.Label(root, text="Incorrect file type selected.", fg="Red")
        error1Label.place_forget()
        error1Label.place(x=50, y=300)

def hannahsACT(file):  # Agent comission tool

    x1 = file
    # Read the file
    data = pd.read_csv(x1, error_bad_lines=False)
    # Drop blanks from column A
    df1 = data.dropna(subset=['Agent']).reset_index(drop=True)
    # Generating new data frames and creating 4 columns on each file
    dfUS = df1.loc[df1["Location"].str.startswith(('E1', 'L1'))]
    dfUS = dfUS.assign(Agreement='', Renewal_New='', Current_Rate='', Fixed='')
    dfUK = df1.loc[df1["Location"].str.startswith(('E2', 'L2'))]
    dfUK = dfUK.assign(Agreement='', Renewal_New='', Current_Rate='', Fixed='')
    dfSNG = df1.loc[df1["Location"].str.startswith(('E3', 'L3'))]
    dfSNG = dfSNG.assign(Agreement='', Renewal_New='', Current_Rate='', Fixed='')
    dfAUS = df1.loc[df1["Location"].str.startswith(('E4', 'L4'))]
    dfAUS = dfAUS.assign(Agreement='', Renewal_New='', Current_Rate='', Fixed='')
    dfNED = df1.loc[df1["Location"].str.startswith(('E5', 'L5'))]
    dfNED = dfNED.assign(Agreement='', Renewal_New='', Current_Rate='', Fixed='')
    dfCAN = df1.loc[df1["Location"].str.startswith(('E6', 'L6'))]
    dfCAN = dfCAN.assign(Agreement='', Renewal_New='', Current_Rate='', Fixed='')
    # To create final file as a variable to be able to apply .save() to it
    writer = pd.ExcelWriter(file.name + " - Ready For SW.xlsx", engine='xlsxwriter')
    # Adding mutliple sheets to master file
    dfUS.to_excel(writer, sheet_name='US', index=False)
    workbook = writer.book
    worksheet = writer.sheets['US']
    (max_row, max_col) = dfUS.shape
    column_settings = [{'header': column} for column in dfUS.columns]
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
    worksheet.set_column(0, max_col - 1, 12)

    dfUK.to_excel(writer, sheet_name='UK', index=False)
    workbook = writer.book
    worksheet = writer.sheets['UK']
    (max_row, max_col) = dfUK.shape
    column_settings = [{'header': column} for column in dfUK.columns]
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
    worksheet.set_column(0, max_col - 1, 12)

    dfSNG.to_excel(writer, sheet_name='SNG', index=False)
    workbook = writer.book
    worksheet = writer.sheets['SNG']
    (max_row, max_col) = dfSNG.shape
    column_settings = [{'header': column} for column in dfSNG.columns]
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
    worksheet.set_column(0, max_col - 1, 12)

    dfAUS.to_excel(writer, sheet_name='AUS', index=False)
    workbook = writer.book
    worksheet = writer.sheets['AUS']
    (max_row, max_col) = dfAUS.shape
    column_settings = [{'header': column} for column in dfAUS.columns]
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
    worksheet.set_column(0, max_col - 1, 12)

    dfNED.to_excel(writer, sheet_name='NED', index=False)
    workbook = writer.book
    worksheet = writer.sheets['NED']
    (max_row, max_col) = dfNED.shape
    column_settings = [{'header': column} for column in dfNED.columns]
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
    worksheet.set_column(0, max_col - 1, 12)

    dfCAN.to_excel(writer, sheet_name='CAN', index=False)
    workbook = writer.book
    worksheet = writer.sheets['CAN']
    (max_row, max_col) = dfCAN.shape
    column_settings = [{'header': column} for column in dfCAN.columns]
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
    worksheet.set_column(0, max_col - 1, 12)
    #To save changes in the final file
    writer.save()

#  Functions to store paths for Hanna's part 2
def hannasFile1():

    global x
    x = askopenfile(parent=root, mode='r', title="choose a file #1")
    eraserLabel = tk.Label(root,
                           text="                                                                                                                                                                           ")
    eraserLabel.place(x=50, y=300)
    checkerLabelA = tk.Label(frame5, text="READY")
    blankLabelA = tk.Label(frame5, text="           ")
    if x == None:
        blankLabelA.place(x=330, y=150)
    if x.name.endswith(".xlsx"):
        if x != None:
            checkerLabelA.place(x=330, y=150)
    else:
        error1Label = tk.Label(root, text="Incorrect file type selected.", fg="Red")
        error1Label.place_forget()
        error1Label.place(x=50, y=300)
        blankLabelA.place(x=330, y=150)


def hannasFile2():
    eraserLabel = tk.Label(root,
                           text="                                                                                                                                                                           ")
    eraserLabel.place(x=50, y=300)
    global y
    y = askopenfile(parent=root, mode='r', title="choose a file #2")
    checkerLabelB = tk.Label(frame5, text="READY")
    blankLabelB = tk.Label(frame5, text="           ")
    if y == None:
        blankLabelB.place(x=330, y=210)
    if y.name.endswith(".xlsx"):
        if y != None:
            checkerLabelB.place(x=330, y=210)
    else:
        error1Label = tk.Label(root, text="Incorrect file type selected.", fg="Red")
        error1Label.place_forget()
        error1Label.place(x=50, y=300)
        blankLabelB.place(x=330, y=210)


def hannasP3File1():
    eraserLabel = tk.Label(root,
                           text="                                                                                                                                                                           ")
    eraserLabel.place(x=50, y=300)
    global  z
    z = askopenfile(parent=root, mode='r', title="choose a file #3")
    checkerLabelC = tk.Label(frame6, text="READY")
    blankLabelC = tk.Label(frame6, text="           ")
    if z == None:
        blankLabelC.place(x=330, y=130)
    if z != None:
        checkerLabelC.place(x=330, y=130)

def hannasP3File2():
    global  zx
    zx = askopenfile(parent=root, mode='r', title="choose a file #4")
    checkerLabelC = tk.Label(frame6, text="READY")
    blankLabelC = tk.Label(frame6, text="           ")
    if zx == None:
        blankLabelC.place(x=330, y=190)
    if zx != None:
        checkerLabelC.place(x=330, y=190)

def hannasP3File3():
    global  zy
    zy = askopenfile(parent=root, mode='r', title="choose a file #5")
    checkerLabelC = tk.Label(frame6, text="READY")
    blankLabelC = tk.Label(frame6, text="           ")
    if zy == None:
        blankLabelC.place(x=330, y=250)
    if zy != None:
        checkerLabelC.place(x=330, y=250)


def hannasPart2call():
    # check files end  with .xlsx and place error label
    if x and y  != None:
        hannasPart2(x,y)
    else:
        print("error")


def hannasPart2(filea,fileb):
    if filea and fileb != None:
        # We import our files & open all sheets in different dataframes.

        # <This is the current month file>
        xls = pd.ExcelFile(filea.name)
        df1 = pd.read_excel(xls, "US")
        df2 = pd.read_excel(xls, "UK")
        df3 = pd.read_excel(xls, "SG")
        df4 = pd.read_excel(xls, "AUS")
        df5 = pd.read_excel(xls, "NL")
        df6 = pd.read_excel(xls, "CAN")

        oglist = (df1, df2, df3, df4, df5, df6)  # <---- just a list of dfs

        # <This is the file we use for Verification (previous month)>
        xlsV = pd.ExcelFile(fileb.name)
        df1_v = pd.read_excel(xlsV, "US")
        df2_v = pd.read_excel(xlsV, "UK")
        df3_v = pd.read_excel(xlsV, "SG")
        df4_v = pd.read_excel(xlsV, "AUS")
        df5_v = pd.read_excel(xlsV, "NL")
        df6_v = pd.read_excel(xlsV, "CAN")

        vlist = (df1_v, df2_v, df3_v, df4_v, df5_v, df6_v)  # <---- just a list of dfs

        # Next we clean up each dataframe so we can work with them
        for i in oglist:
            og_cleanup(i)

        for i in vlist:
            sw_cleanup(i)

        # Here we create the final column with the list of the exceptions.
        merger(df1, df1_v)
        merger(df2, df2_v)
        merger(df3, df3_v)
        merger(df4, df4_v)
        merger(df5, df5_v)
        merger(df6, df6_v)

        # Here we create the final file to output
        # To create final file as a variable to be able to apply .save() to it
        writer = pd.ExcelWriter(filea.name + " - Exceptions Report.xlsx",
                                engine='xlsxwriter')

        # Adding mutliple sheets to master file
        df1.to_excel(writer, sheet_name='US', index=False)
        workbook = writer.book
        worksheet = writer.sheets['US']
        (max_row, max_col) = df1.shape
        column_settings = [{'header': column} for column in df1.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
        worksheet.set_column(0, max_col - 1, 12)

        df2.to_excel(writer, sheet_name='UK', index=False)
        workbook = writer.book
        worksheet = writer.sheets['UK']
        (max_row, max_col) = df2.shape
        column_settings = [{'header': column} for column in df2.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
        worksheet.set_column(0, max_col - 1, 12)

        df3.to_excel(writer, sheet_name='SNG', index=False)
        workbook = writer.book
        worksheet = writer.sheets['SNG']
        (max_row, max_col) = df3.shape
        column_settings = [{'header': column} for column in df3.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
        worksheet.set_column(0, max_col - 1, 12)

        df4.to_excel(writer, sheet_name='AUS', index=False)
        workbook = writer.book
        worksheet = writer.sheets['AUS']
        (max_row, max_col) = df4.shape
        column_settings = [{'header': column} for column in df4.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
        worksheet.set_column(0, max_col - 1, 12)

        df5.to_excel(writer, sheet_name='NED', index=False)
        workbook = writer.book
        worksheet = writer.sheets['NED']
        (max_row, max_col) = df5.shape
        column_settings = [{'header': column} for column in df5.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
        worksheet.set_column(0, max_col - 1, 12)

        df6.to_excel(writer, sheet_name='CAN', index=False)
        workbook = writer.book
        worksheet = writer.sheets['CAN']
        (max_row, max_col) = df6.shape
        column_settings = [{'header': column} for column in df6.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
        worksheet.set_column(0, max_col - 1, 12)

        writer.save()
    else:
        print("error")

def hannasPart3call():
    hannasPart3(z,zx,zy)

def hannasPart3(hfile1,hfile2,hfile3):
    print(hfile1.name)
    print(hfile2.name)
    print(hfile3.name)
# function to check value of radio button selected
def clicked(value):
    if value == 2:
        Funct2()
    if value == 1:
        Funct1()
    if value == 3:
        Funct3()
    if value == 4:
        r2.set("1")
        Funct4()

#  Function  for Hanna's radio buttons
def clicked2(value):
    if value == 1:
        r2.set("1")
        frame5.place_forget()
        frame6.place_forget()
        frame4.place(width=750, height=280)
        print("hannas deleted")
    if value == 2:
        print("hannas menu2")
        r3.set("2")
        frame4.place_forget()
        frame6.place_forget()
        frame5.place(width=750, height=280)
    if value == 3:
        print("hannas menu2")
        r4.set("3")
        frame4.place_forget()
        frame5.place_forget()
        frame6.place(width=750, height=280)
# functions to be called by radio buttons to show menu frames
def Funct1():
    frame3.place_forget()
    frame2.place_forget()
    frame4.place_forget()
    frame5.place_forget()
    frame6.place_forget()
    frame1.place(width=750, height=280)


def Funct2():
    frame1.place_forget()
    frame3.place_forget()
    frame4.place_forget()
    frame5.place_forget()
    frame6.place_forget()
    frame2.place(width=750, height=280)

def Funct3():
    frame1.place_forget()
    frame2.place_forget()
    frame4.place_forget()
    frame5.place_forget()
    frame6.place_forget()
    frame3.place(width=750, height=280)

def Funct4():
    frame1.place_forget()
    frame2.place_forget()
    frame3.place_forget()
    frame5.place_forget()
    frame6.place_forget()
    frame4.place(width=750, height=280)

# checks for integer values in entry boxes, will return error
def intCheck():
    try:
        int(e1.get())
        int(e2.get())
        int(e3.get())
        return True
    except ValueError:
        return False


# MAIN GUI CODE=========================================================================================================

# root canvas and frames set up along with icon and title of window
root = tk.Tk()
root.title('i-land Smart Comptroller')

canvas = tk.Canvas(root)
root.geometry("650x400")  # from 600 to 750
root.resizable(False, False)
# frames will not cover radio buttons in root
frame1 = tk.Frame(root, bg="#F0F0F0", width=290, height=200)
frame2 = tk.Frame(root, bg="#F0F0F0", width=290, height=200)
frame3 = tk.Frame(root, bg="#F0F0F0", width=290, height=200)
frame4 = tk.Frame(root, bg="#F0F0F0", width=290, height=200)
frame5 = tk.Frame(root, bg="#F0F0F0", width=290, height=200)
frame6 = tk.Frame(root, bg="#F0F0F0", width=290, height=200)

# logos for Frames

logoLabel = tk.Label(frame1, text="i-land", font="Baskerville 72 bold", fg="blue")
logoLabel.place(x=220, y=25)  # from 190 to 220
logoLabel = tk.Label(frame2, text="i-land", font="Baskerville 72 bold", fg="blue")
logoLabel.place(x=220, y=25)
logoLabel = tk.Label(frame3, text="i-land", font="Baskerville 72 bold", fg="blue")
logoLabel.place(x=220, y=25)
logoLabel = tk.Label(frame4, text="i-land", font="Baskerville 72 bold", fg="blue")
logoLabel.place(x=220, y=25)
logoLabel = tk.Label(frame5, text="i-land", font="Baskerville 72 bold", fg="blue")
logoLabel.place(x=220, y=25)
logoLabel = tk.Label(frame6, text="i-land", font="Baskerville 72 bold", fg="blue")
logoLabel.place(x=220, y=25)

# radio buttons for main root bottom menu
r = tk.IntVar()
r2 = tk.IntVar()
r3 = tk.IntVar()
r4 = tk.IntVar()
r.set("1")
r2.set("1")
r3.set("2")
r4.set("3")

radB=tk.Radiobutton(root, text="Revenue Clean-up", variable=r, value=1, command=lambda: clicked(r.get()))
radB.place(x=45,y=350)  # went from 80 to 50
radB=tk.Radiobutton(root, text="Pay Match", variable=r, value=2, command=lambda: clicked(r.get()))
radB.place(x=215,y=350)
radB=tk.Radiobutton(root, text="Raquel's Rev Report", variable=r, value=3, command=lambda: clicked(r.get()))
radB.place(x=340,y=350)
radB=tk.Radiobutton(root, text="Hannah's ACT", variable=r, value=4, command=lambda: clicked(r.get()))
radB.place(x=495,y=350)
# Hanna's Radio buttons
radB=tk.Radiobutton(frame4, text="Part 1", variable=r2, value=1, command=lambda: clicked2(r2.get()))
radB.place(x=45,y=130)
radB=tk.Radiobutton(frame4, text="Part 2", variable=r2, value=2, command=lambda: clicked2(r2.get()))
radB.place(x=45,y=180)
radB=tk.Radiobutton(frame4, text="Part 3", variable=r2, value=3, command=lambda: clicked2(r2.get()))
radB.place(x=45,y=230)

radB=tk.Radiobutton(frame5, text="Part 1", variable=r3, value=1, command=lambda: clicked2(r3.get()))
radB.place(x=45,y=130)
radB=tk.Radiobutton(frame5, text="Part 2", variable=r3, value=2, command=lambda: clicked2(r3.get()))
radB.place(x=45,y=180)
radB=tk.Radiobutton(frame5, text="Part 3", variable=r3, value=3, command=lambda: clicked2(r3.get()))
radB.place(x=45,y=230)

radB=tk.Radiobutton(frame6, text="Part 1", variable=r4, value=1, command=lambda: clicked2(r4.get()))
radB.place(x=45,y=130)
radB=tk.Radiobutton(frame6, text="Part 2", variable=r4, value=2, command=lambda: clicked2(r4.get()))
radB.place(x=45,y=180)
radB=tk.Radiobutton(frame6, text="Part 3", variable=r4, value=3, command=lambda: clicked2(r4.get()))
radB.place(x=45,y=230)

# instructions for both frames
instructions = tk.Label(frame1, text="Select a file to process", font="helvetica 12 bold", bg="#F0F0F0")
instructions.place(x=410, y=140)

instructions3 = tk.Label(frame3, text="Select a file to process", font="helvetica 12 bold", bg="#F0F0F0")
instructions3.place(x=260, y=180)

instructions4 = tk.Label(frame4, text="Select a file to process", font="helvetica 12 bold", bg="#F0F0F0")
instructions4.place(x=260, y=180)

instructions5 = tk.Label(frame5, text="Current Month's file", font="helvetica 12 bold", bg="#F0F0F0")
instructions5.place(x=185, y=130)

instructions6 = tk.Label(frame5, text="Previous month file for verification", font="helvetica 12 bold", bg="#F0F0F0")
instructions6.place(x=185, y=190)

instructions7 = tk.Label(frame6, text="part 3 file 1", font="helvetica 12 bold", bg="#F0F0F0")
instructions7.place(x=185, y=110)

instructions8 = tk.Label(frame6, text="part 3 file 2", font="helvetica 12 bold", bg="#F0F0F0")
instructions8.place(x=185, y=170)

instructions9 = tk.Label(frame6, text="part 3 file 2", font="helvetica 12 bold", bg="#F0F0F0")
instructions9.place(x=185, y=230)

# input boxes and labels for both frames
tk.Label(frame1, text="Month 1").place(x=80, y=140)
tk.Label(frame1, text="Month 2").place(x=80, y=190)
tk.Label(frame1, text="Variance scope").place(x=80, y=240)

e1 = tk.Entry(frame1)
e2 = tk.Entry(frame1)
e3 = tk.Entry(frame1)
e1.place(x=180, y=140)
e2.place(x=180, y=190)
e3.place(x=180, y=240)

tk.Label(frame2, text = "Target Value").place(x=130, y=150)
e4 = tk.Entry(frame2)
e4.place(x=220, y=150)


# RUN button set up for both frames
browse_text = tk.StringVar()
browse_textx = tk.StringVar()
browse_texty = tk.StringVar()
browse_textz = tk.StringVar()
browse_textrun = tk.StringVar()
# changed font, color, and bg of button
browsebtn = tk.Button(frame1, textvariable=browse_text, command=callCleanRev, font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_text.set("Select a file")
browsebtn.place(x=410, y=180)

browsebtn2 = tk.Button(frame2, textvariable=browse_text, command=callPaymatch,  font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_text.set("Select a file")
browsebtn2.place(x=250, y=240)

browsebtn3 = tk.Button(frame3, textvariable=browse_text, command=callrevRaquel,  font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_text.set("Select a file")
browsebtn3.place(x=250, y=240)

browsebtn4 = tk.Button(frame4, textvariable=browse_text, command=callHannah,  font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_text.set("Select a file")
browsebtn4.place(x=250, y=240)

browsebtn5a = tk.Button(frame5, textvariable=browse_textx, command=hannasFile1,  font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_textx.set("Select a file")
browsebtn5a.place(x=180, y=150)

browsebtn5b = tk.Button(frame5, textvariable=browse_texty, command=hannasFile2,  font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_texty.set("Select a file")
browsebtn5b.place(x=180, y=210)

browsebtn5 = tk.Button(frame5, textvariable=browse_textrun, command=hannasPart2call,  font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_textrun.set("RUN")
browsebtn5.place(x=450, y=190)

browsebtn6 = tk.Button(frame6, textvariable=browse_textrun, command=hannasPart3call,  font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_textrun.set("RUN")
browsebtn6.place(x=450, y=190)

browsebtn6a = tk.Button(frame6, textvariable=browse_textz, command=hannasP3File1,  font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_textz.set("Select a file #3")
browsebtn6a.place(x=180, y=130)

browsebtn6b = tk.Button(frame6, textvariable=browse_textz, command=hannasP3File2,  font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_textz.set("Select a file #4")
browsebtn6b.place(x=180, y=190)

browsebtn6c = tk.Button(frame6, textvariable=browse_textz, command=hannasP3File3,  font="helvetica 12 bold", bg="sky blue", fg="black", height=1, width=15)
browse_textz.set("Select a file #5")
browsebtn6c.place(x=180, y=250)

#  starts off program on  frame 1
Funct1()

root.mainloop()