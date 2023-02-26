from PyQt5 import QtWidgets as q,uic,QtCore
from sys import argv,exit as e
from datetime import datetime
from threading import Thread
class Functions:
    def __init__(self):
        self.totalList=0
        self.lst=[]
        self.listIndex=0
    def updateDataBase(self):
        with open("tasks.db","w") as f:
            for i in self.lst:
                f.write(i+"\n")
    def updateListsTable(self):
        self.listsTable.setRowCount(len(self.lst))
        for i in range(len(self.lst)):
            lst = self.lst[i].split(";")[0].split("|")
            for j in range(len(lst)):
                self.listsTable.setItem(i,j,q.QTableWidgetItem(str(lst[j])))
    def getFromDataBase(self):
        for i in open("tasks.db"):
            self.lst.append(i.strip("\n"))
            self.totalList+=1
        self.updateListsTable()

    def findName(self,widget,entry):
        name = entry.text().lower()
        for i in range(widget.rowCount()):
            try:
                item = widget.item(i,0)
                widget.setRowHidden(i,name not in item.text().lower())
            except:
                pass
    def __addList(self,txt):
        self.running=True
        self.totalList+=1
        self.listsTable.setRowCount(self.totalList)
        lst=[txt,0,str(datetime.now())[:19]]
        for i in range(len(lst)):
            self.listsTable.setItem(self.totalList-1,i,q.QTableWidgetItem(str(lst[i])))
        self.lst.append(f"{lst[0]}|{lst[1]}|{lst[2]};")
        self.updateDataBase()
        self.running=False
    def addList(self):
        txt = str(self.addListEntry.text())
        if txt.strip():
            Thread(target=self.__addList,args=(txt,)).start()
        self.addListEntry.clear()
    def removeRow(self):
        self.running=True
        row=self.listsTable.currentRow()
        try:
            if row>=0:
                self.listsTable.removeRow(row)
                self.lst.pop(row)
                self.totalList-=1
        except:
            pass
        else:
            self.updateDataBase()
        self.running=False
    def clearList(self):
        self.running=True
        if self.totalList:
            self.lst.clear()
            self.totalList=0
            self.listsTable.setRowCount(0)
            self.updateDataBase()
        self.running=False
    def __select(self):
        self.running=True
        lst=self.lst[self.listIndex].split(";")[1].split("/")
        if "".join(lst).strip():
            self.tasksTable.setRowCount(len(lst))
            for i in range(len(lst)):
                task=lst[i].split(",")
                self.tasksTable.setItem(i,0,q.QTableWidgetItem(str(task[0])))
                self.tasksTable.setItem(i,1,q.QTableWidgetItem(str(task[1])))
        self.running=False
    def select(self):
        self.listIndex=self.listsTable.currentRow()
        if self.listIndex>=0:
            self.stackedWidget.setCurrentWidget(self.allTasks)
            Thread(target=self.__select).start()
    def __addTask(self,task):
        self.running=True
        row=self.tasksTable.rowCount()
        self.tasksTable.setRowCount(row+1)
        tasksList=self.lst[self.listIndex].split(";")[1].split("/")
        if not tasksList[0].strip():tasksList.pop(0)
        lst=[task,str(datetime.now())[:19]]
        for i in range(len(lst)):
            self.tasksTable.setItem(row,i,q.QTableWidgetItem(str(lst[i])))
        tasksList.append(",".join(lst))
        l = self.lst[self.listIndex].split(";")[0].split("|")
        l[1] = str(int(l[1])+1)
        self.lst[self.listIndex] = f"{'|'.join(l)};{'/'.join(tasksList)}"
        self.updateListsTable()
        self.updateDataBase()
        self.running=False
    def addTask(self):
        task = str(self.taskEntry.text())
        if task.strip():
            Thread(target=self.__addTask,args=(task,)).start()
        self.taskEntry.clear()
    def finishTask(self):
        self.running=True
        row = self.tasksTable.currentRow()
        l=self.lst[self.listIndex].split(";")
        tasks=l[1].split("/")
        if tasks[row] and row>=0:
            lst = l[0].split("|")
            tasks.pop(row)
            lst[1] = str(int(lst[1])-1)
            self.tasksTable.removeRow(row)
            self.lst[self.listIndex]=f"{'|'.join(lst)};{'/'.join(tasks)}"
            self.updateListsTable()
            self.updateDataBase()
        self.running=False

    def goBack(self):
        self.stackedWidget.setCurrentWidget(self.allLists)
        self.tasksTable.setRowCount(0)
class Buttons(Functions):
    def addLists(self):
        self.addToListButton.clicked.connect(self.addList if not self.running else lambda:None)
        self.searchListsEntry.textChanged.connect(lambda:self.findName(self.listsTable,self.searchListsEntry))
        self.removeListButton.clicked.connect(self.removeRow if not self.running else lambda:None)
        self.clearListButton.clicked.connect(self.clearList if not self.running else lambda:None)
        self.selectListButton.clicked.connect(self.select if not self.running else lambda:None)
    def addTasks(self):
        self.goBackButton.clicked.connect(self.goBack)
        self.addTaskButton.clicked.connect(self.addTask if not self.running else lambda:None)
        self.searchTasks.textChanged.connect(lambda:self.findName(self.tasksTable,self.searchTasks))
        self.finishTaskButton.clicked.connect(self.finishTask if not self.running else lambda:None)
class window(q.QMainWindow,Buttons):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui",self)
        self.running=False
        self.headerFrame.mouseMoveEvent=self.moveWindow
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.exitButton.clicked.connect(self.close)
        self.minimizeButton.clicked.connect(self.showMinimized)
        self.minMaxButton.clicked.connect(self.minMax)
        self.addLists()
        self.addTasks()
        self.getFromDataBase()
        tables=[self.listsTable,self.tasksTable]
        for i in tables:
            i.horizontalHeader().setSectionResizeMode(q.QHeaderView.Stretch)
            i.horizontalHeader().setSectionsClickable(False)
            i.verticalHeader().setSectionResizeMode(q.QHeaderView.Fixed)
            i.setCornerButtonEnabled(False)
            i.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
    def minMax(self):
        if not self.isMaximized():
            self.showMaximized()
        else:
            self.showNormal()
    def mousePressEvent(self, event):
        self.clickPosition=event.globalPos()
    def moveWindow(self, event):
        try:
            if not self.isMaximized() and event.buttons()==QtCore.Qt.MouseButton.LeftButton:
                self.move(self.pos()+event.globalPos()-self.clickPosition)
                self.clickPosition=event.globalPos()
                event.accept()
        except:
            pass
if __name__=="__main__":
    app=q.QApplication(argv)
    w=window()
    w.show()
    e(app.exec_())
