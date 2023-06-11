from tkinter import *
from tkinter import messagebox as mbox
from tkinter import ttk
from sqlite3 import *
from tkinter.filedialog import *
from configparser import *

contView = False
# addView = False
fViewSearch = False

cont_text = "База данных 'Знаменитые программисты России'\nпозволяет: добавлять / изменять / удалять" \
            " информацию.\nКлавиши программы:\nF1-вызов справки по программе,\nF2-добавить в базу данных," \
            "\nF3-удалить из базы данных,\nF4-изменить запись в базе данных,\nF10-Меню программы"
photoBuffer = None
querydata = []
namelist = []

cursor = connect("AmDB.db").cursor()
cursor.execute("CREATE TABLE if not exists AmDB (id INTEGER PRIMARY KEY, sur TEXT, info TEXT, photo BLOB);")


def cmQuit(event=None):
    cursor.connection.close()
    form1.quit()


def selectAll():
    global querydata, namelist
    cursor.execute("SELECT id, sur FROM AmDB")
    querydata = cursor.fetchall()
    namelist = [querydata[i][1] for i in range(len(querydata))]


def updateData(event=None):
    global querydata
    choosen = sur_list.curselection()
    if len(choosen) == 0:
        return
    exportData = querydata[choosen[0]]
    addInfoF(list(exportData))


def insertData(event=None):
    addInfoF()


def contentOp(event=None):
    global contView

    def contentCl():
        global contView
        aboutProg.destroy()
        contView = False

    if not contView:
        aboutProg = Toplevel()
        aboutProg.title("Содержание")
        aboutProg.geometry("300x200+300+100")
        aboutProg.resizable(False, False)
        Button(aboutProg, text="Закрыть", command=contentCl, height=1, width=6).place(x=225, y=150)
        description = Label(aboutProg, wraplength=300, text=cont_text, anchor=W, justify=LEFT)
        description.place(x=5, y=5)
        contView = True


def aboutProgInfo():
    mbox.showinfo("О программе", "База данных 'Знаменитые программисты России'\n(c) Kostyukhin I.M., Russia, 2023")


def search():
    global querydata, fViewSearch

    def submit(event=None):
        found = False
        lake = inplake.get()
        for i in range(0, len(namelist)):
            if namelist[i] == lake:
                found = True
                cur = sur_list.curselection()
                if len(cur) > 0:
                    sur_list.select_clear(cur)
                sur_list.select_set(i)
                listSelect()
                break
        if not found:
            mbox.showerror("Ошибка!", "Не найдено ни одной записи")
        global fViewSearch
        searchForm.destroy()
        fViewSearch = False

    def close(event=None):
        global fViewSearch
        searchForm.destroy()
        fViewSearch = False

    if not fViewSearch:
        searchForm = Toplevel()
        searchForm.focus_set()
        searchForm.geometry("300x100+300+100")
        searchForm.resizable(height=False, width=False)
        searchForm.title('Поиск')
        content = ttk.Label(searchForm, text="Введите ФИО полностью:", padding=10)
        content.pack(anchor=NW)
        inplake = StringVar()
        inp = Entry(searchForm, textvariable=inplake, width=47)
        inp.place(x=6, y=30)
        inp.focus_set()
        searchForm.protocol('WM_DELETE_WINDOW', close)
        Button(searchForm, text='Поиск', command=submit).place(x=245, y=60)
        searchForm.bind('<Return>', submit)
        fViewSearch = True


def addInfoF(data=None):
    # global addView
    global photoBuffer
    photoBuffer = None
    selected = sur_list.curselection()

    # def addInfoClose():
    #     global addView
    #     addInfo.destroy()
    #     addView = False

    # if not addView:
    def saveAdd():
        sur = entrySur.get()
        info = infoArea.get(1.0, END)
        if data:
            query = "UPDATE AmDB SET sur = ?, info = ?, photo = ? WHERE id=?;"
            par = (sur, info, photoBuffer, data[0])
            cursor.execute(query, par)
            cursor.connection.commit()
            sur_list.delete(selected)
            sur_list.insert(selected, sur)
            selectAll()
            sur_list.select_set(selected)
            listSelect()
        else:
            query = "INSERT INTO AmDB(sur, info, photo) VALUES (?,?,?)"
            par = (sur, info, photoBuffer)
            cursor.execute(query, par)
            cursor.connection.commit()
            sur_list.insert(END, sur)
            selectAll()
            sur_list.select_set(END)
            listSelect()

        addInfo.destroy()

    def uploadPhoto():
        global photoBuffer
        selectedPhoto = askopenfilename(title="Выберите фотографию личности", filetypes=[("png files", "*.png")])
        if selectedPhoto:
            try:
                with open(selectedPhoto, "rb") as F:
                    photoBuffer = F.read()
                    F.close()
            except Exception:
                mbox.showerror("Упс...", "Неподходящее имя файла")

    addInfo = Toplevel()
    addInfo.title("Добавить данные")
    addInfo.geometry("500x400+300+100")
    addInfo.resizable(False, False)
    addInfo.grab_set()
    addInfo.focus_set()
    # Button(addInfo, text="Закрыть", command=addInfoClose, height=1, width=6).place(x=430, y=360)
    surText = Label(addInfo, text="ФИО:", anchor=W, justify=LEFT)
    surText.place(x=5, y=5)
    entrySur = Entry(addInfo, width=30)
    entrySur.place(x=5, y=30)
    infoText = Label(addInfo, text="Текст статьи:", anchor=W, justify=LEFT)
    infoText.place(x=5, y=50)
    infoArea = Text(addInfo, width=60, height=10)
    infoArea.place(x=5, y=80)

    if data:
        imageBlobQuery = f"SELECT photo FROM AmDB WHERE id={data[0]}"
        cursor.execute(imageBlobQuery)
        dataImgText = cursor.fetchall()
        photoBuffer = dataImgText[0][0]
        entrySur.insert(0, data[1])
        infoArea.insert(END, selectedText.get(1.0, END))

    photoText = Label(addInfo, text='Фотография:')
    photoText.place(x=5, y=250)

    Button(addInfo, text="Выбрать", command=uploadPhoto, height=1, width=6).place(x=85, y=250)
    Button(addInfo, text="Сохранить", command=saveAdd, height=1, width=8).place(x=5, y=360)
    # addView = True


def deleteData(event=None):
    global querydata
    choosen = sur_list.curselection()
    if len(choosen) == 0:
        return
    else:
        recordId = querydata[choosen[0]][0]
        delAccept = mbox.askyesno(title="Удаление...", message="Вы уверены что хотите удалить данные?")
        if delAccept:
            cursor.execute(f"DELETE FROM AmDB WHERE id={recordId};")
            cursor.connection.commit()
            sur_list.delete(choosen)
            photo_canvas.delete("all")
            selectedText.place_forget()
            mbox.showinfo(title="Удачно", message="Запись удалена!")
            selectAll()
        else:
            sur_list.select_set(choosen)


def listSelect(event=None):
    choosenIndex = sur_list.curselection()
    if len(choosenIndex) == 0:
        return
    choosenIndex = choosenIndex[0]
    imageBlobQuery = f"SELECT photo, info FROM AmDB WHERE id={querydata[choosenIndex][0]}"
    cursor.execute(imageBlobQuery)
    dataPhotoText = cursor.fetchall()
    image = dataPhotoText[0][0]
    selectedImage = None if not image else PhotoImage(data=image, format='png').subsample(2, 2)
    photo_canvas.create_image(0, 0, image=selectedImage, anchor=NW)
    photo_canvas.image = selectedImage
    photo_canvas.place(x=200, y=10, width=380, height=400)
    selectedText.delete(1.0, END)

    selectedText.insert(END, dataPhotoText[0][1])
    selectedText.place(x=540, y=10, width=250, height=565)


def logIn():
    config = ConfigParser()
    config.read("AmDB.ini")
    login = config['main']['user']
    password = config['main']['keyuser']

    def checkPass(event=None):
        if login == inpLogin.get() and password == inpPassword.get():
            authorisationForm.destroy()
        else:
            entryLogin.delete(0, END)
            entryPassword.delete(0, END)
            mbox.showerror("Ошибка!", "Ошибка входа! Неверный логин или пароль!")

    authorisationForm = Tk()
    authorisationForm.resizable(width=False, height=False)
    authorisationForm.geometry("200x200+300+200")
    authorisationForm.title("Войти")
    inpLogin = StringVar()
    inpPassword = StringVar()
    getLogin = Label(authorisationForm, text='Введите логин:')
    getLogin.place(x=50, y=10)
    entryLogin = Entry(authorisationForm, textvariable=inpLogin)
    entryLogin.place(x=30, y=40)
    entryLogin.focus_set()

    getPass = Label(authorisationForm, text='Введите пароль:')
    getPass.place(x=50, y=70)
    entryPassword = Entry(authorisationForm, show='*', textvariable=inpPassword)
    entryPassword.place(x=30, y=100)
    Button(authorisationForm, text="Вход", width=10, command=checkPass).place(x=50, y=140)
    authorisationForm.protocol('WM_DELETE_WINDOW', exit)
    authorisationForm.bind('<Return>', checkPass)
    authorisationForm.mainloop()


logIn()

form1 = Tk()
form1.title("Знаменитые программисты России")
form1.geometry('800x600+300+100')
form1.resizable(False, False)

menu0 = Menu()
form1.config(menu=menu0)

menu1 = Menu(tearoff=False)
menu1.add_command(label="Найти", command=search)
menu1.add_separator()
menu1.add_command(label="Добавить", accelerator="F2", command=insertData)
menu1.add_command(label="Удалить", accelerator="F3", command=deleteData)
menu1.add_command(label="Изменить", accelerator="F4", command=updateData)
menu1.add_separator()
menu1.add_command(label="Выход", command=cmQuit, accelerator="Ctrl+X")
menu0.add_cascade(label="Фонд", menu=menu1)

menu2 = Menu(tearoff=False)
menu2.add_command(label="Содержание", command=contentOp)
menu2.add_separator()
menu2.add_command(label="О программе", command=aboutProgInfo)
menu0.add_cascade(label="Справка", menu=menu2)

status_bord = Canvas(bg="blue")
status_bord.create_text(180, 10, text="F1 - справка F2 - добавить F3 - удалить F4 - изменить F10 - меню", fill="white")
status_bord.place(x=-2, y=580, width=810, height=50)

form1.bind("<F1>", contentOp)
form1.bind("<F2>", insertData)
form1.bind("<F3>", deleteData)
form1.bind("<F4>", updateData)
form1.bind("<F10>", cmQuit)
form1.bind("<Control-x>", cmQuit)

photo_canvas = Canvas()
selectedText = Text()
selectedText.place(x=590, y=10, width=200, height=600)
selectedText.place_forget()
selectedText.bind("<Key>", lambda e: "break")

selectAll()
sur_list = Listbox(form1, width=30, height=35, listvariable=Variable(value=namelist), exportselection=0)
sur_list.place(x=5, y=5)
sur_list.bind('<<ListboxSelect>>', listSelect)
sur_list.bind('<FocusOut>', lambda e: sur_list.selection_clear(0, END))

form1.mainloop()
