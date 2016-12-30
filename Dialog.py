import wx
import wx.lib.plot as plot
import os,sys
import time
import xlsxwriter

import Excel
import Preview

# The recommended way to use wx with mpl is with the WXAgg
# backend. 
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
#-------------------------------------------------------

class AboutDialog(wx.Dialog):
    '''window for 'About' dialog box
    '''

    def __init__(self, parent, id, title):
        ''' Constructor of 'About' dialog box

        @type self: AboutDialog
        @type parent: wx.Dialog | None
        @type id: int
            id number of parent window
        @type title: str
            Label for top on window
        @rtype: None
        '''
        wx.Dialog.__init__(self, parent, id, title)

        self.SetIcon(wx.Icon('Images/questionmark.ico', wx.BITMAP_TYPE_ICO))                
        self.rootPanel = wx.Panel(self)        
        innerPanel = wx.Panel(
            self.rootPanel,-1, size=(500,260), style=wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.HORIZONTAL) 
        vbox = wx.BoxSizer(wx.VERTICAL)
        innerBox = wx.BoxSizer(wx.VERTICAL)

        # Creating objects to place in window
        txt1 = "Visualized Automator of Compartment Analysis by Tracer Efflux Automator (vaCATE)"
        txt2 = "Alpha Version 1.0 as of September 1, 2016"
        txt3 = "This program is designed to automate the output of parameters"
        txt4 = "extracted by CATE (as input into a generated template file)."
        txt5 = "Prior to extraction of automated data analysis into an Microsoft Excel (.xls)"
        txt6 = "users are able to preview data and dynamically change the analysis."
        txt7 = "More detailed information about how to do this can be found"
        txt8 = "in the 'README.txt' file found in the directory from which"
        txt9 = "the vaCATE was downloaded/cloned."
        txt10 = "Copyright 2016 Ruben Flam-Shepherd. All rights reserved."
        txt11 = "This work is licensed under a"
        txt12 = "Creative Commons Attribution 4.0 International License."
                
        static_txt1 = wx.StaticText(
            innerPanel, id=-1, label=txt1, style=wx.ALIGN_CENTER, name="")
        static_txt2 = wx.StaticText(
            innerPanel, id=-1, label=txt2, style=wx.ALIGN_CENTER, name="")
        static_txt3 = wx.StaticText(
            innerPanel, id=-1, label=txt3, style=wx.ALIGN_CENTER, name="")
        static_txt4 = wx.StaticText(
            innerPanel, id=-1, label=txt4, style=wx.ALIGN_CENTER, name="")
        static_txt5 = wx.StaticText(
            innerPanel, id=-1, label=txt5, style=wx.ALIGN_CENTER, name="")
        static_txt6 = wx.StaticText(
            innerPanel, id=-1, label=txt6, style=wx.ALIGN_CENTER, name="")
        static_txt7 = wx.StaticText(
            innerPanel, id=-1, label=txt7, style=wx.ALIGN_CENTER, name="")
        static_txt8 = wx.StaticText(
            innerPanel, id=-1, label=txt8, style=wx.ALIGN_CENTER, name="")
        static_txt9 = wx.StaticText(
            innerPanel, id=-1, label=txt9, style=wx.ALIGN_CENTER, name="")
        static_txt10 = wx.StaticText(
            innerPanel, id=-1, label=txt10, style=wx.ALIGN_CENTER, name="")
        static_txt11 = wx.StaticText(
            innerPanel, id=-1, label=txt11, style=wx.ALIGN_CENTER, name="")
        static_txt12 = wx.HyperlinkCtrl(
            innerPanel, id=-1, label=txt12,
            url="http://creativecommons.org/licenses/by/4.0/", name="")
        btn1 = wx.Button (innerPanel, id=1, label="Close")
        
        line1 = wx.StaticLine(innerPanel, -1, style=wx.LI_HORIZONTAL)
        line2 = wx.StaticLine(innerPanel, -1, style=wx.LI_HORIZONTAL)
        
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=1)
        
        # Placing created objects in window
        innerBox.AddSpacer((150,10))
        innerBox.Add(static_txt1, 0, wx.CENTER)
        innerBox.AddSpacer((150,6))
        innerBox.Add(static_txt2, 0, wx.CENTER)
        innerBox.AddSpacer((150,6))
        
        innerBox.Add(line1, 0, wx.CENTER|wx.EXPAND)
        innerBox.AddSpacer((150,6))
        innerBox.Add(static_txt3, 0, wx.CENTER)
        innerBox.Add(static_txt4, 0, wx.CENTER)
        innerBox.Add(static_txt5, 0, wx.CENTER)
        innerBox.Add(static_txt6, 0, wx.CENTER)
        innerBox.AddSpacer((150,6))
        innerBox.Add(static_txt7, 0, wx.CENTER)
        innerBox.Add(static_txt8, 0, wx.CENTER)
        innerBox.Add(static_txt9, 0, wx.CENTER)
        innerBox.AddSpacer((150,6))
        
        innerBox.Add(line2, 0, wx.CENTER|wx.EXPAND)
        innerBox.AddSpacer((150,6))
        innerBox.Add(static_txt10, 0, wx.CENTER)
        innerBox.AddSpacer((150,6))        
        innerBox.Add(static_txt11, 0, wx.CENTER)
        innerBox.AddSpacer((150,3))    
        innerBox.Add(static_txt12, 0, wx.CENTER)
        innerBox.AddSpacer((150,10))        
        innerBox.Add(btn1, 0, wx.CENTER)
        innerBox.AddSpacer((150,6))
        
        innerPanel.SetSizer(innerBox)

        hbox.Add(innerPanel, 0, wx.ALL|wx.ALIGN_CENTER)
        vbox.Add(hbox, 1, wx.ALL|wx.ALIGN_CENTER, 5)
        

        self.rootPanel.SetSizer(vbox)
        vbox.Fit(self)        
        

    def OnClose(self, event):
        '''Closing window when 'x' in top right corner is pressed

        @type self: AboutDialog
        @type event: Event
        @rtype: None
        '''
        self.Close()

class DialogFrame(wx.Frame):
    '''First dialog window presented to the user
    '''

    def __init__(self, parent, id, title):
        ''' Constructor of first dialog window presented to user

        @type self: DialogFrame
        @type parent: wx.Dialog | None
        @type id: int
            id number of parent window
        @type title: str
            Label for top on window
        @rtype: None
        '''
        wx.Frame.__init__(self, parent, id, title)
        self.SetIcon(wx.Icon('Images/testtube.ico', wx.BITMAP_TYPE_ICO))

        self.rootPanel = wx.Panel(self)
        
        innerPanel = wx.Panel(
            self.rootPanel,-1, size=(500,160), style=wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.HORIZONTAL) 
        vbox = wx.BoxSizer(wx.VERTICAL)
        innerBox = wx.BoxSizer(wx.VERTICAL)
        buttonBox1 = wx.BoxSizer(wx.HORIZONTAL)
        buttonBox2 = wx.BoxSizer(wx.HORIZONTAL)
        buttonBox3 = wx.BoxSizer(wx.HORIZONTAL)
        
        # Main text presented to user
        txt1 = "     Welcome to the CATE Data Analyzer!     "
        txt2 = "Please choose an option below:"
        static_txt1 = wx.StaticText(
            innerPanel, id=-1, label=txt1, style=wx.ALIGN_CENTER, name="")
        static_txt2 = wx.StaticText(
            innerPanel, id=-1, label=txt2, style=wx.ALIGN_CENTER, name="")
        
        # Disclaimer text (under buttons)
        txt3 = "Note: .xls output file will be written in the same folder"
        txt4 = "that data is being extracted from"
        static_txt3 = wx.StaticText(
            innerPanel, id=-1, label=txt3, style=wx.ALIGN_CENTER, name="")
        static_txt4 = wx.StaticText(
            innerPanel, id=-1, label=txt4, style=wx.ALIGN_CENTER, name="")
        
        font3 = wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        static_txt3.SetFont(font3)
        static_txt4.SetFont(font3)
        
        # Option Buttons        
        btn1 = wx.Button(innerPanel, id=1, label="Analyze CATE Data")
        btn2 = wx.Button(innerPanel, id=2, label="Generate CATE Template")
        self.checkbox = wx.CheckBox (
            innerPanel, id=5, label="Automatically analyze")
        self.checkbox.SetValue(True)
        btn3 = wx.Button(innerPanel, id=3, label="About")
        btn4 = wx.Button(innerPanel, id=4, label="Quit")
        
        # Binding events to buttons
        self.Bind(wx.EVT_BUTTON, self.OnAnalyze, id=1)        
        self.Bind(wx.EVT_BUTTON, self.OnGenerate, id=2)        
        self.Bind(wx.EVT_BUTTON, self.OnAbout, id=3)        
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=4)
        
        # Adding main text to main spacer 'innerBox'
        innerBox.AddSpacer((150,15))
        innerBox.Add(static_txt1, 0, wx.CENTER)
        innerBox.AddSpacer((150,15))
        innerBox.Add(static_txt2, 0, wx.CENTER)
        innerBox.AddSpacer((150,15))
        
        # Adding main program buttons to main spacer 'innerBox'
        buttonBox1.AddSpacer(7,10)        
        buttonBox1.Add(btn1, 0, wx.CENTER)
        buttonBox1.AddSpacer(7,10)
        buttonBox1.Add(self.checkbox, 0, wx.CENTER)
        buttonBox1.AddSpacer(7,15)
        buttonBox2.AddSpacer(7,10)
        buttonBox2.Add(btn2, 0, wx.CENTER)
        buttonBox3.AddSpacer(7,10)
        buttonBox3.Add(btn3, 0, wx.CENTER)
        buttonBox3.AddSpacer(7,15)        
        buttonBox3.Add(btn4, 0, wx.CENTER)
        buttonBox3.AddSpacer(7,10)        
        innerBox.Add(buttonBox1, 0, wx.CENTER)
        innerBox.AddSpacer ((150,10))
        innerBox.Add(buttonBox2, 0, wx.CENTER)
        innerBox.AddSpacer ((150,10))
        innerBox.Add(buttonBox3, 0, wx.CENTER)
        innerBox.AddSpacer ((150,10))
        
        # Adding disclaimer text to main spacer 'innerBox' (under buttons)
        innerBox.Add(static_txt3, 0, wx.CENTER)
        innerBox.Add(static_txt4, 0, wx.CENTER)
        innerBox.AddSpacer((150,10))        
        innerPanel.SetSizer(innerBox)

        hbox.Add(innerPanel, 0, wx.ALL|wx.ALIGN_CENTER)
        vbox.Add(hbox, 1, wx.ALL|wx.ALIGN_CENTER, 5)
        
        self.rootPanel.SetSizer(vbox)
        vbox.Fit(self)
        

    def OnClose(self, event):
        '''Closing window when 'x' in top right corner is pressed

        @type self: DialogFrame
        @type event: Event
        @rtype: None
        '''
        self.Close()
        

    def OnAnalyze(self, event):
        '''Creating preview of data analysis when 'Analyse' button is pushed

        @type self: DialogFrame
        @type event: Event
        @rtype: None        
        '''
        dlg = wx.FileDialog(
            self,
            "Choose the file which contains the data you'd like to perform CATE upon",
            os.getcwd(), "", "")
        if dlg.ShowModal() == wx.ID_OK:
            directory, filename = dlg.GetDirectory(), dlg.GetFilename()

            # Formatting the directory (and path) to unicode w/ forward slash
            # so it can be passed between methods/classes w/o bugs
            file_path = os.path.join(directory, filename)
            directory = u'%s' %directory
            directory = directory.replace (u'\\', '/')            
            
            temp_CATE_data = Excel.grab_data(file_path)
            if self.checkbox.GetValue():
                for temp_analysis in temp_CATE_data.analyses:
                    temp_analysis.kind = 'obj'
                    temp_analysis.obj_num_pts = 8
                    temp_analysis.analyze()
            frame = Preview.MainFrame(temp_CATE_data)
            frame.Show(True)
            frame.MakeModal(True)            
            dlg.Destroy()
                        
        self.Close()                         
            

    def OnAbout(self, event):
        '''Creating About window when 'About' button is pushed
        
        @type self: DialogFrame
        @type event: Event
        @rtype: None        
        '''        
        dlg = AboutDialog (self, -1, 'vaCATE - About')
        val = dlg.ShowModal()
        dlg.Destroy()
    

    def OnGenerate(self, event): # Event when 'Generate Template' button is pushed
        '''Creating a template input file when when 'Generate' button is pushed

        Template file is generating in directory selected by user
        
        @type self: DialogFrame
        @type event: Event
        @rtype: None        
        '''
        dlgChoose = wx.DirDialog(self, "Choose the directory to generate the template file inside:")
                        
        if dlgChoose.ShowModal() == wx.ID_OK:
            directory = dlgChoose.GetPath()
            dlgChoose.Destroy()
                    
            # Formatting the directory (and path) to unicode w/ forward slash so
            # it can be passed between methods/classes w/o bugs
            directory = u'%s' %directory
            self.directory = directory.replace (u'\\', '/')
            
            output_name = 'CATE Template - ' + time.strftime("(%Y_%m_%d).xlsx")
            output_file_path = os.path.join(directory, output_name)            
            
            workbook = xlsxwriter.Workbook(output_file_path)
            Excel.generate_template(workbook)
            
            workbook.close()        
               
if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = DialogFrame(None, -1, 'vaCATE')
    app.frame.Show(True)
    app.frame.Center()
    app.MainLoop()    