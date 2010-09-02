#!/usr/bin/python
import sys, os
import pickle
from shutil import copy
import wx
"""
To Do:
1. Is there a way to make the initial image grey?
2. Make the button length consisten with the radio box in mac and windows
3. Splash screen
4. Icon
5. Spruce up the about menu
6. Iphoto Library support (ambitious!)
7. Refactor!
8. Make the parameters configurable through an Edit Menu

"""

class Parameters():
    def __init__(self):
        self.PhotoMaxSize = 520
        self.formats = ('.jpg', '.jpeg', '.tiff', '.png', 'gif', '.bmp')
        self.wildcard = "All files (*.*)|*.*"
        self.rankList = ['1', '2', '3', '4', '5']
        #self.iconimg = os.path.join(os.getcwd(), 'thumb_sideways.png')
        self.about = """
            This is a program I wrote to learn wxPython, and do something
            useful.  Basically, the program will import Image files or search
            a directory for images, and display them in a window.  Rank the
            photos on a scale of 1 to 5.  As you rank photos, you can import
            additional photos, or save your session to continue later.  Once
            you have ranked all the photos, you can export the files you like
            that meet a certain rank to another location to do something else
            with.
            """
        
        
class GUI(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(900, 700))
        self.Center(direction=wx.BOTH)
        self.functions = Events(self)
        self.parameters = Parameters()
        #iconimg = wx.Image(self.parameters.iconimg, wx.BITMAP_TYPE_PNG)
        #iconbmp = iconimg.ConvertToBitmap()
        #splash = wx.SplashScreen(iconbmp, wx.SPLASH_CENTER_ON_SCREEN | wx.SPLASH_TIMEOUT, 2000, None, -1)
        self.splitter = wx.SplitterWindow(self)
        self.leftpanel = wx.Panel(self.splitter, style=wx.SUNKEN_BORDER)
        self.rightpanel = wx.Panel(self.splitter, style=wx.SUNKEN_BORDER)
        self.statusbar = self.CreateStatusBar()
        
        # menubar 
        fileMenu = wx.Menu()
        openFile = fileMenu.Append(-1, "Import F&ile")
        openDir = fileMenu.Append(-1, "Import &Directory (Recursive)")
        fileMenu.AppendSeparator()
        openPickle = fileMenu.Append(-1, "&Restore Saved Session")
        savePickle = fileMenu.Append(-1, "&Save Session")
        fileMenu.AppendSeparator()
        exportPhotos = fileMenu.Append(-1, "&Export Photos")
        fileMenu.AppendSeparator()
        exit = fileMenu.Append(-1, "E&xit")
        helpMenu = wx.Menu()
        about = helpMenu.Append(-1, "&About")
        menubar = wx.MenuBar()
        menubar.Append(fileMenu, "&File")
        menubar.Append(helpMenu, "&Help")
        self.SetMenuBar(menubar)
                
        #Add left hand side widgets
        img = wx.EmptyImage(240,240)
        self.imageCtrl=wx.StaticBitmap(self.leftpanel, wx.ID_ANY, wx.BitmapFromImage(img))
        
        #Add left hand size sizers
        lefthsizer = wx.BoxSizer(wx.HORIZONTAL)
        leftvsizer = wx.BoxSizer(wx.VERTICAL)
        leftvsizer.Add((20,20), flag=wx.EXPAND)
        leftvsizer.Add(self.imageCtrl)
        leftvsizer.Add((20,20), flag=wx.EXPAND)
        lefthsizer.Add((20,20), flag=wx.EXPAND)
        lefthsizer.Add(leftvsizer)
        lefthsizer.Add((20,20), flag=wx.EXPAND)
        self.leftpanel.SetSizer(lefthsizer)
        
        #Add right hand side widgets
        nextBtn = wx.Button(self.rightpanel, -1, "Next", size=(93,25))
        spacer1 = wx.StaticText(self.rightpanel, -1, "")
        prevBtn = wx.Button(self.rightpanel, -1, "Prev", size=(93,25))
        spacer2 = wx.StaticText(self.rightpanel, -1, "")
        self.radioGroup = wx.RadioBox(self.rightpanel, -1, "Rank the photo", wx.DefaultPosition, wx.DefaultSize, \
            self.parameters.rankList, 1, wx.RA_SPECIFY_COLS)

        #Add right hand side sizers
        righthsizer = wx.BoxSizer(wx.HORIZONTAL)
        rightvsizer = wx.BoxSizer(wx.VERTICAL)
        rightvsizer.Add(nextBtn)
        rightvsizer.Add(spacer1)
        rightvsizer.Add(prevBtn)
        rightvsizer.Add(spacer2)
        rightvsizer.Add(self.radioGroup)
        righthsizer.Add((20,20), flag=wx.EXPAND)
        righthsizer.Add(rightvsizer)
        righthsizer.Add((20,20), flag=wx.EXPAND)
        self.rightpanel.SetSizer(righthsizer)

        # bind events to widgets
        self.Bind(wx.EVT_MENU, self.functions.OnExit, id = exit.GetId())
        self.Bind(wx.EVT_MENU, self.functions.OnOpenFile, id = openFile.GetId())
        self.Bind(wx.EVT_MENU, self.functions.OnOpenDir, id = openDir.GetId())
        self.Bind(wx.EVT_MENU, self.functions.OnAbout, id = about.GetId()) 
        self.Bind(wx.EVT_MENU, self.functions.OnOpenPickle, id = openPickle.GetId())
        self.Bind(wx.EVT_MENU, self.functions.OnSavePickle, id = savePickle.GetId())
        self.Bind(wx.EVT_MENU, self.functions.OnExport, id = exportPhotos.GetId())
        self.Bind(wx.EVT_BUTTON, self.functions.OnNext, id = nextBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.functions.OnPrev, id = prevBtn.GetId())
        self.Bind(wx.EVT_RADIOBOX, self.functions.OnRank, id = self.radioGroup.GetId())

        #draw
        #self.leftpanel.Layout()
        #self.rightpanel.Layout()
        self.splitter.SplitVertically(self.leftpanel, self.rightpanel, 700)
        
class Events():
    def __init__(self, parent):
        self.gui = parent
        self.parameters = Parameters()
        self.PhotoMaxSize = self.parameters.PhotoMaxSize
        self.container = DIRContainer()
        
    def OnExit(self, evt):
        self.gui.Close(True)
        
    def OnOpenFile(self, evt):
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", self.parameters.wildcard, wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            filepath = dialog.GetPath()
            filelist = [filepath]
            self.container.addFiles(filelist)
            if self.container.isEmpty:
                self.onView(self.container.fileList[self.container.position])
                self.container.setNotEmpty()
    
    def OnOpenDir(self, evt):
        dialog = wx.DirDialog(None, "Choose a directory", style = wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.gui.statusbar.SetStatusText("Loading. . . ")            
            dirpath = dialog.GetPath()
            search = DirSearch()
            search.search_directory(dirpath)
            self.container.addFiles(search.fqfile_list)
            #Check to see if any images have been loaded
            if self.container.isEmpty:
                self.onView(self.container.fileList[self.container.position])
                self.container.setNotEmpty()               
                
    def OnNext(self, evt):
        if self.container.isEmpty:
            dialog = wx.MessageDialog(None, "No photos loaded!", 'ERROR!', wx.OK | wx.ICON_EXCLAMATION)
            retCode = dialog.ShowModal()
            if retCode == wx.ID_OK:
                dialog.Destroy()
        else:
            self.container.increment()
            self.onView(self.container.fileList[self.container.position])
            rank = self.container.getRank()
            self.gui.radioGroup.SetSelection(rank)
            
    def OnPrev(self, evt):
        if self.container.isEmpty:
            dialog = wx.MessageDialog(None, "No photos loaded!", 'ERROR!', wx.OK | wx.ICON_EXCLAMATION)
            retCode = dialog.ShowModal()
            if retCode == wx.ID_OK:
                dialog.Destroy()
        else:
            self.container.decrement()
            self.onView(self.container.fileList[self.container.position])
            rank = self.container.getRank()
            self.gui.radioGroup.SetSelection(rank)
            
    def OnRank(self, evt):
        if self.container.isEmpty:
            dialog = wx.MessageDialog(None, "No photos loaded!", 'ERROR!', wx.OK | wx.ICON_EXCLAMATION)
            retCode = dialog.ShowModal()
            self.gui.radioGroup.SetSelection(0)
        else:
            rank = self.gui.radioGroup.GetSelection()
            self.container.setRank(rank)
            
    def OnSavePickle(self, evt):
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", self.parameters.wildcard, wx.SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            filepath = dialog.GetPath()
            f = open(filepath, 'w')
            pickle.dump(self.container, f)

    def OnOpenPickle(self, evt):
        if self.container.isEmpty == False:
            dialog = wx.MessageDialog(None, \
                "You have a session in progress.  You will loose any progress if you load a new session now.  Do you want to continue?", \
                'Alert!', wx.YES_NO | wx.ICON_QUESTION)
            if dialog.ShowModal() == wx.ID_YES:
                proceed = True
            else: 
                proceed = False
        else:
            proceed = True
        if proceed:
            dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", self.parameters.wildcard, wx.OPEN)
            if dialog.ShowModal() == wx.ID_OK:
                filepath = dialog.GetPath()
                f = open(filepath, 'r')
                self.container = pickle.load(f)
                self.onView(self.container.fileList[self.container.position])

    def OnExport(self, evt):
        if self.container.isEmpty:
            dialog = wx.MessageDialog(None, "No photos loaded!", 'ERROR!', wx.OK | wx.ICON_EXCLAMATION)
            retCode = dialog.ShowModal()
            if retCode == wx.OK:
                dialog.Destroy()
        else:
            dialog = wx.MultiChoiceDialog(None, "Export photos with the following Ranks.", \
                'Export Photos', self.parameters.rankList, wx.OK | wx.CANCEL)
            dialog.Center(direction=wx.BOTH)
            if dialog.ShowModal() == wx.ID_OK:
                ranks = dialog.GetSelections()
                dialog.Destroy()
                dialog = wx.DirDialog(None, "Choose a directory", style = wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
                if dialog.ShowModal() == wx.ID_OK:
                    exportDir = dialog.GetPath()
                    self.container.export(ranks, exportDir)
                    dialog.Destroy()
            
            
        #dialog = wx.DirDialog(None, "Choose a directory", style = wx.DD_DEFAULT_STYLE| wx.DD_NEW_DIR_BUTTON)
        #if dialog.ShowModal() == wx.ID_OK:
        #    pass
        
    def OnAbout(self, evt):
        dialog = wx.MessageDialog(None, self.parameters.about, 'About', wx.OK | wx.ICON_QUESTION)
        retCode = dialog.ShowModal()
        if retCode == wx.ID_OK:
            dialog.Destroy()

    def onView(self, filepath):        
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        #scale the image, preserving aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H/W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W/H
        img=img.Scale(NewW,NewH)        
        self.gui.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        self.gui.statusbar.SetStatusText("Displaying Image %s of %s: File: %s" \
            % (self.container.position + 1, len(self.container.fileList), self.container.fileList[self.container.position]))
        self.gui.leftpanel.Refresh()

class Application(wx.App):
    def __init__(self, redirect=False):
        wx.App.__init__(self, redirect=False)

    def OnInit(self):
        frame = GUI(None, -1, "Image Ranker")
        frame.Show(True)
        return True
        
class DIRContainer():
    def __init__(self):
        self.position = 0
        self.rankDict = {}
        self.fileList = []
        self.isEmpty = True
        self.parameters = Parameters()
    
    def increment(self):
        if self.position == len(self.fileList) - 1:
            self.position = 0
        else:
            self.position += 1
    
    def decrement(self):
        if self.position == 0:
            self.position = len(self.fileList) - 1
        else:
            self.position -= 1
        
    def addFiles(self, files):
        for file in files:
            self.fileList.append(file)
            self.rankDict[file] = 0
    
    def clearFiles(self):
        self.position = 0
        self.rankDict = {}
        self.fileList = []

    def setRank(self, rank):
        self.rankDict[self.fileList[self.position]] = rank
    
    def getRank(self):
        return self.rankDict[self.fileList[self.position]]

    def export(self, ranks, exportDir):
        exportList = []
        for key in self.rankDict:
            if self.rankDict[key] in ranks:
                exportList.append(key)
        for file in exportList:
            copy(file, exportDir)                    

    def setNotEmpty(self):
        self.isEmpty = False

    def setEmpty(self):
        self.isEmpty = True
        

class DirSearch:
    def __init__(self):
        #basic stats
        self.file_list = []             #all file names in subdirectories
        self.fqfile_list = []           #all fully-qualified file names in subdirectories
        self.file_dict = {}             #dictionary of fully-qualified names (keys) and file names
        self.parameters = Parameters()
        
    def search_directory(self, directory=os.curdir):       
        for root, dirs, files in os.walk(directory):
            for file in files:
                for format in self.parameters.formats:
                    if file.endswith(format.upper()) | file.endswith(format.lower()):
                        pathname = os.path.join(root, file)
                        fq_file_name = os.path.realpath(pathname)
                        self.fqfile_list.append(fq_file_name)
                        self.file_list.append(file)
                        self.file_dict[fq_file_name] = file
                
#helper functions
    def print_fqfile_list(self):
        result = ""
        for element in self.fqfile_list:
            result = result + " " + `element`
        print "Contains:"+ result
    
    def print_file_list(self):
        result = ""
        for element in self.file_list:
            result = result + " " + `element`
        print "Contains:"+result

if __name__ == '__main__':
    Application().MainLoop()
