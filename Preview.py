"""
This demo demonstrates how to embed a matplotlib (mpl) plot 
into a wxPython GUI application, including:

* Using the navigation toolbar
* Adding data to the plot
* Dynamically modifying the plot's properties
* Processing mpl events
* Saving the plot to a file from a menu

The main goal is to serve as a basis for developing rich wx GUI
applications featuring mpl plots (using the mpl OO API).

Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 30.07.2008
"""

# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
import os
import pprint
import random
import wx
import numpy as np
import Operations
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib import gridspec
from matplotlib import pyplot as plt


x_series = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.5, 13.0, 14.5, 16.0, 17.5, 19.0, 20.5, 22.0, 23.5, 25.0, 27.0, 29.0, 31.0, 33.0, 35.0, 37.0, 39.0, 41.0, 43.0, 45.0]
y_series = [5.134446324653075, 4.532511080497156, 3.9647696512150836, 3.6692523925695686, 3.509950796085591, 3.3869391729764766, 3.287809993163619, 3.230048067964903, 3.169204739621747, 3.1203409378545346, 2.95145986473132, 2.8916143915841324, 2.8589559610792583, 2.8463057128814175, 2.8413779879066166, 2.7532261939625293, 2.750050822474359, 2.6735829597693206, 2.7024903224651338, 2.661606690643107, 2.5998423959455335, 2.57889496358432, 2.5921979525818397, 2.557187996704314, 2.529320391444595, 2.558194007072854, 2.4833719392530966, 2.5557756556810562, 2.4045248209763437, 2.4642132678099204]

x = np.array (x_series)
y = np.array (y_series)

class MainFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'Compartmental Analysis of Tracer Efflux: Data Analyzer'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()
        
        # Default analysis of data is an objective regression using the last
        # 4 data points
        self.obj_textbox.SetValue ('2')        
        
        self.draw_figure()

    def create_menu(self):
        """ Creating a file menu that allows saving of graphs to .pngs, opening
        of a help dialog, or quitting the application
        Notes: adapted from original program, pseudo-useless
        """
        
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu() # 'File' menu
        
        # 'Save' option of 'File' menu
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        
        menu_file.AppendSeparator()
        
        # 'Exit' option of 'File' menu
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
        
        menu_help = wx.Menu() #'Help' menu
        
        # 'About' option of 'Help' menu        
        m_about = menu_help.Append(-1, "&About\tF1", "About the demo")
        self.Bind(wx.EVT_MENU, self.on_about, m_about)
        
        # Creating menu
        self.menubar.Append(menu_file, "&File")
        self.menubar.Append(menu_help, "&Help")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        """ Creates the main panel with all the controls on it:
             * mpl canvas 
             * mpl navigation toolbar
             * Control panel for interaction
        """
        self.panel = wx.Panel(self)
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((10, 4.0), dpi=self.dpi)
        self.canvas = FigCanvas(self.panel, -1, self.fig)
       
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        
        # Allows us to set custom sizes of subplots
        gs = gridspec.GridSpec(2, 2)
        self.plot_phase3 = self.fig.add_subplot(gs[1:-1, 0])
        self.plot_phase2 = self.fig.add_subplot(gs[1, 1]) 
        self.plot_phase1 = self.fig.add_subplot(gs[0, 1]) 
                
        # Bind the 'pick' event for clicking on one of the bars
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Bind the 'check' event for ticking 'Show Grid' option
        self.cb_grid = wx.CheckBox(self.panel, -1, 
            "Show Grid",
            style=wx.ALIGN_CENTER)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)

        # Create the navigation toolbar, tied to the canvas
        self.toolbar = NavigationToolbar(self.canvas)
        
        # Layout with box sizers
                
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.toolbar, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
                
        # Text labels describing regression inputs
        self.obj_title = wx.StaticText (
	    self.panel,
	    label="Objective Regression",
	    style=wx.ALIGN_CENTER)
        self.obj_label = wx.StaticText (
	    self.panel,
	    label="Number of points to use:",
	    style=wx.ALIGN_CENTER)
        self.subj_title = wx.StaticText (
	    self.panel,
	    label="Subjective Regression",
	    style=wx.ALIGN_CENTER)
        self.subj1_label = wx.StaticText (
	    self.panel,
	    label="First Point:",
	    style=wx.ALIGN_CENTER)
        self.subj2_label = wx.StaticText (
	    self.panel,
	    label="Last Point:",
	    style=wx.ALIGN_CENTER)
        self.subj_disclaimer = wx.StaticText (
	    self.panel,
	    label="Points are numbered from left to right",
	    style=wx.ALIGN_CENTER)
        self.linedata_title = wx.StaticText (
	    self.panel,
	    label="Regression Parameters",
	    style=wx.ALIGN_CENTER)
        
        # Text boxs for collecting regression parameter input
        self.obj_textbox = wx.TextCtrl(self.panel, 
	    size=(50,-1),
	    style=wx.TE_PROCESS_ENTER)
        
        self.subj_p1_1textbox = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_PROCESS_ENTER)        
	
	self.subj_p1_2textbox = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_PROCESS_ENTER)
        
        self.subj_p2_1textbox = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_PROCESS_ENTER)        
        self.subj_p2_2textbox = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_PROCESS_ENTER)
        
        self.subj_p3_1textbox = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_PROCESS_ENTER)        
        self.subj_p3_2textbox = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_PROCESS_ENTER)        
                    
        
        # Buttons for identifying collect regression parameter event
        self.obj_drawbutton = wx.Button(self.panel, -1,
	                                "Draw Objective Regresssion")
        self.Bind(wx.EVT_BUTTON, self.on_obj_draw, self.obj_drawbutton)
        
        self.subj_drawbutton = wx.Button(self.panel, -1,
	                                 "Draw Subjective Regression")
        self.Bind(wx.EVT_BUTTON, self.on_subj_draw, self.subj_drawbutton)
        self.line = wx.StaticLine(self.panel, -1, style=wx.LI_VERTICAL)
        self.line2 = wx.StaticLine(self.panel, -1, style=wx.LI_VERTICAL)
        self.line3 = wx.StaticLine(self.panel, -1, style=wx.LI_VERTICAL)
        
        # Alignment flags (for adding things to spacers) and fonts
        flags = wx.ALIGN_RIGHT | wx.ALL | wx.ALIGN_CENTER_VERTICAL
        box_flag = wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_CENTER_VERTICAL
        button_flag = wx.ALIGN_BOTTOM
        title_font = wx.Font (8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        widget_title_font = wx.Font (8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, True)
        disclaimer_font = wx.Font (6, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        
        # Setting fonts
        self.obj_title.SetFont(title_font)
        self.subj_title.SetFont(title_font)
        self.linedata_title.SetFont(title_font)
        self.subj_disclaimer.SetFont(disclaimer_font)
        
        # Adding objective widgets to objective sizer
        self.vbox_obj = wx.BoxSizer(wx.VERTICAL)
        self.vbox_obj.Add (self.obj_title, 0, border=3, flag=box_flag)
        self.vbox_obj.AddSpacer(7)
        self.vbox_obj.Add (self.obj_label, 0, border=3, flag=box_flag)
        self.vbox_obj.AddSpacer(5)
        self.vbox_obj.Add (self.obj_textbox, 0, border=3, flag=box_flag)
        self.vbox_obj.AddSpacer(5)
        self.vbox_obj.Add (self.obj_drawbutton, 0, border=3, flag=button_flag)
        
        # Adding subjective widgets to subjective sizer
        self.gridbox_subj = wx.GridSizer (rows=4, cols=3, hgap=1, vgap=1)
        self.gridbox_subj.Add (wx.StaticText (self.panel, id=-1, label=""),
	                       0, border=3, flag=flags)
        self.gridbox_subj.Add (self.subj1_label, 0, border=3,
	                       flag=box_flag)
        self.gridbox_subj.Add (self.subj2_label, 0, border=3,
	                       flag=box_flag)
                
        self.gridbox_subj.Add (wx.StaticText (self.panel, label="Phase I:"),
	                       0, border=3, flag=flags)        
        self.gridbox_subj.Add (self.subj_p1_1textbox, 0, border=3,
	                       flag=box_flag)
        self.gridbox_subj.Add (self.subj_p1_2textbox, 0, border=3,
	                       flag=box_flag)
                
        self.gridbox_subj.Add (wx.StaticText (self.panel, label="Phase II:"),
	                       0, border=3, flag=flags)        
        self.gridbox_subj.Add (self.subj_p2_1textbox, 0, border=3,
	                       flag=box_flag)
        self.gridbox_subj.Add (self.subj_p2_2textbox, 0, border=3,
	                       flag=box_flag)
                
        self.gridbox_subj.Add (wx.StaticText (self.panel, label="Phase III:"),
	                       0, border=3, flag=flags)        
        self.gridbox_subj.Add (self.subj_p3_1textbox, 0, border=3,
	                       flag=box_flag)
        self.gridbox_subj.Add (self.subj_p3_2textbox, 0, border=3,
	                       flag=box_flag)
                
        self.vbox_subj = wx.BoxSizer(wx.VERTICAL)
        self.vbox_subj.Add (self.subj_title, 0, border=3, flag=box_flag)
        self.vbox_subj.Add (self.gridbox_subj, 0, border=3, flag=box_flag)
        self.vbox_subj.Add (self.subj_drawbutton, 0, border=3,
	                    flag=box_flag)
        self.vbox_subj.Add (self.subj_disclaimer, 0, border=3,
	                    flag=box_flag)
        
        # Creating widgets for data output
        self.data_p1_int = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_READONLY)
        self.data_p1_slope = wx.TextCtrl(
            self.panel, 
            size=(50,-1),
            style=wx.TE_READONLY)
        self.data_p1_r2 = wx.TextCtrl(
            self.panel, 
            size=(50,-1),
            style=wx.TE_READONLY)
        
        self.data_p2_int = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_READONLY)
        self.data_p2_slope = wx.TextCtrl(
            self.panel, 
            size=(50,-1),
            style=wx.TE_READONLY)
        self.data_p2_r2 = wx.TextCtrl(
            self.panel, 
            size=(50,-1),
            style=wx.TE_READONLY)                   
        
        self.data_p3_int = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_READONLY)
        self.data_p3_slope = wx.TextCtrl(
            self.panel, 
            size=(50,-1),
            style=wx.TE_READONLY)
        self.data_p3_r2 = wx.TextCtrl(
            self.panel, 
            size=(50,-1),
            style=wx.TE_READONLY)
	
	# Creating labels for data output
	empty_text = wx.StaticText (self.panel, label = "")
	slope_text = wx.StaticText (self.panel, label="Slope")
	intercept_text = wx.StaticText(self.panel, label = "Intercept")
	r2_text = wx.StaticText (self.panel, label = "R^2")
	p1_text = wx.StaticText (self.panel, label = "Phase I: ")
	p2_text = wx.StaticText (self.panel, label = "Phase II: ")
	p3_text = wx.StaticText (self.panel, label = "Phase II: ")
        
        # Adding data output widgets to data output gridsizers        
        self.gridbox_data = wx.GridSizer (rows=4, cols=4, hgap=1, vgap=1)
        
        self.gridbox_data.Add (empty_text, 0, border=3, flag=flags)
        self.gridbox_data.Add (slope_text, 0, border=3, flag=box_flag)
        self.gridbox_data.Add (intercept_text, 0, border=3, flag=box_flag)
        self.gridbox_data.Add (r2_text, 0, border=3, flag=box_flag)

        self.gridbox_data.Add (p1_text, 0, border=3, flag=flags)
        self.gridbox_data.Add (self.data_p1_slope, 0, border=3, flag=box_flag)
        self.gridbox_data.Add (self.data_p1_int, 0, border=3, flag=box_flag)
        self.gridbox_data.Add (self.data_p1_r2, 0, border=3, flag=box_flag)
        
        self.gridbox_data.Add (p2_text, 0, border=3, flag=flags)
        self.gridbox_data.Add (self.data_p2_slope, 0, border=3, flag=box_flag)
        self.gridbox_data.Add (self.data_p2_int, 0, border=3, flag=box_flag)
        self.gridbox_data.Add (self.data_p2_r2, 0, border=3, flag=box_flag)        
        
        self.gridbox_data.Add (p3_text, 0, border=3, flag=flags)
        self.gridbox_data.Add (self.data_p3_slope, 0, border=3, flag=box_flag)
        self.gridbox_data.Add (self.data_p3_int, 0, border=3, flag=box_flag)
        self.gridbox_data.Add (self.data_p3_r2, 0, border=3, flag=box_flag)
        
        self.vbox_linedata = wx.BoxSizer(wx.VERTICAL)
        self.vbox_linedata.Add (self.linedata_title, 0, border=3, flag=box_flag)
        self.vbox_linedata.Add (self.gridbox_data, 0, border=3, flag=box_flag)
        
        # Build the widgets and the sizer contain(s) containing them all
	
	# Build slider to adjust point radius
        self.slider_label = wx.StaticText(
	    self.panel,
	    -1,
	    "Point Radius",
	    style=wx.ALIGN_CENTER)
        self.slider_label.SetFont (widget_title_font)
        self.slider_width = wx.Slider(self.panel, -1, 
            value=40, 
            minValue=1,
            maxValue=200,
            style=wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.slider_width.SetTickFreq(10, 1)
        self.Bind(wx.EVT_COMMAND_SCROLL_THUMBTRACK, self.on_slider_width, self.slider_width)        
        self.vbox_widgets = wx.BoxSizer(wx.VERTICAL)
        self.vbox_widgets.Add(self.cb_grid, 0, border=3, flag=box_flag)
        self.vbox_widgets.Add(self.slider_label, 0, flag=box_flag)
        self.vbox_widgets.Add(self.slider_width, 0, border=3, flag=box_flag)
        
        # Build widget that displays information about last widget clicked
	
	# Creating the 'last clicked' items
        self.xy_clicked_label = wx.StaticText(
	    self.panel,
	    -1,
	    "Last point clicked",
	    style=wx.ALIGN_CENTER)
        self.xy_clicked_label.SetFont (widget_title_font)
        self.x_clicked_label = wx.StaticText(
	    self.panel,
	    -1,
	    "Elution Time (x): ",
	    style=wx.ALIGN_CENTER)
        self.y_clicked_label = wx.StaticText(
	    self.panel,
	    -1,
	    "Log cpm (y): ",
	    style=wx.ALIGN_CENTER)
        self.num_clicked_label = wx.StaticText(
	    self.panel,
	    -1,
	    "Point Number: ",
	    style=wx.ALIGN_CENTER)
        self.x_clicked_data = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_READONLY)
        self.y_clicked_data = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_READONLY)
        self.num_clicked_data = wx.TextCtrl(
	    self.panel, 
	    size=(50,-1),
	    style=wx.TE_READONLY)        
        
        # Assembling the 'last clicked' items into sizers
        self.hbox_x_clicked = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_x_clicked.AddSpacer(10)
        self.hbox_x_clicked.Add (self.x_clicked_label, 0, flag=flags)
        self.hbox_x_clicked.Add (self.x_clicked_data, 0, flag=flags)
        self.hbox_y_clicked = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_y_clicked.AddSpacer(10)
        self.hbox_y_clicked.Add (self.y_clicked_label, 0, flag=flags)
        self.hbox_y_clicked.Add (self.y_clicked_data, 0, flag=flags)
        self.hbox_num_clicked = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_num_clicked.AddSpacer(10)
        self.hbox_num_clicked.Add (self.num_clicked_label, 0, flag=flags)
        self.hbox_num_clicked.Add (self.num_clicked_data, 0, flag=flags)        
        
        self.vbox_widgets.Add(self.xy_clicked_label, 0, flag=box_flag)
        self.vbox_widgets.Add(self.hbox_x_clicked, 0, flag=flags)
        self.vbox_widgets.Add(self.hbox_y_clicked, 0, flag=flags)
        self.vbox_widgets.Add(self.hbox_num_clicked, 0, flag=flags)
        
        # Assembling items for subjective regression field into sizers
        self.hbox_regres = wx.BoxSizer(wx.HORIZONTAL)        
        self.hbox_regres.Add (self.vbox_obj)
        self.hbox_regres.AddSpacer(5)
        self.hbox_regres.Add (self.line, 0, wx.CENTER|wx.EXPAND)
        self.hbox_regres.AddSpacer(5)
        self.hbox_regres.Add (self.vbox_subj)
        self.hbox_regres.Add (self.line2, 0, wx.CENTER|wx.EXPAND)
        self.hbox_regres.AddSpacer(5)
        self.hbox_regres.Add (self.vbox_linedata)
        self.hbox_regres.Add (self.line3, 0, wx.CENTER|wx.EXPAND)        
        self.hbox_regres.Add (self.vbox_widgets, 0, wx.CENTER|wx.EXPAND)
        
        self.vbox.Add(self.hbox_regres, 0, flag = wx.ALIGN_CENTER | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def draw_figure(self):
        """ Redraws the figure
        """     
        
        # clear the axes and redraw the plot anew
        self.plot_phase3.clear()        
        self.plot_phase3.grid(self.cb_grid.IsChecked())        
        
        # Graphing complete log efflux data set
        self.plot_phase3.scatter(
            x,
            y,
            s = self.slider_width.GetValue(),
            alpha = 0.5,
            edgecolors = 'k',
            facecolors = 'w',
            picker = 5
        )
        
        # Setting axes labels/limits
        self.plot_phase3.set_xlabel ('Elution time (min)')
        self.plot_phase3.set_ylabel (u"Log cpm released/g RFW/min")
        self.plot_phase3.set_xlim (left = 0)
        self.plot_phase3.set_ylim (bottom = 0)
        
        
        # Getting linear regression data
        num_points_obj = self.obj_textbox.GetValue ()
        if num_points_obj == '': # SUBJECTIVE REGRESSION
            if self.subj_p1_1textbox.GetValue () != '' and self.subj_p1_2textbox.GetValue () != '':
                sub_p1_start = int(self.subj_p1_1textbox.GetValue ()) - 1 # We get position in the series fromm the user; must convert to indexs 
                sub_p1_end = int(self.subj_p1_2textbox.GetValue ()) - 1
                x1_p1, x2_p1, y1_p1, y2_p1, r2_p1, slope_p1, intercept_p1 = Operations.subj_regression (x, y, sub_p1_start, sub_p1_end)
                # Drawing the subj linear regression line
                self.line_p1 = matplotlib.lines.Line2D ([x1_p1,x2_p1], [y1_p1,y2_p1], ls = '--', color = 'r', label = 'Phase I')
                self.plot_phase3.add_line (self.line_p1)
            
                # setting the series involved in linear regression
                x_p1 = x [sub_p1_start: sub_p1_end + 1] # Last index is not inclusive!
                y_p1 = y [sub_p1_start: sub_p1_end + 1]
                
                # Graphing p1 linear regression        
                self.plot_phase3.scatter(
                            x_p1,
                            y_p1,
                            s = self.slider_width.GetValue(),
                            alpha = 0.25,
                            edgecolors = 'k',
                            facecolors = 'k'
                        )
                self.data_p1_slope.SetValue ('%0.3f'%(slope_p1))
                self.data_p1_int.SetValue ('%0.3f'%(intercept_p1))
                self.data_p1_r2.SetValue ('%0.3f'%(r2_p1))
            else:
                self.data_p1_slope.SetValue ('')
                self.data_p1_int.SetValue ('')
                self.data_p1_r2.SetValue ('')                
                
            if self.subj_p2_1textbox.GetValue () != '' and self.subj_p2_2textbox.GetValue () != '':
                sub_p2_start = int(self.subj_p2_1textbox.GetValue ()) - 1 # We get position in the series fromm the user; must convert to indexs 
                sub_p2_end = int(self.subj_p2_2textbox.GetValue ()) - 1
                x1_p2, x2_p2, y1_p2, y2_p2, r2_p2, slope_p2, intercept_p2 = Operations.subj_regression (x, y, sub_p2_start, sub_p2_end)
                # Drawing the subj linear regression line
                self.line_p2 = matplotlib.lines.Line2D ([x1_p2,x2_p2], [y1_p2,y2_p2], ls = ':', color = 'r', label = 'Phase II')
                self.plot_phase3.add_line (self.line_p2)
            
                # setting the series involved in linear regression
                x_p2 = x [sub_p2_start: sub_p2_end + 1] # Last index is not inclusive!
                y_p2 = y [sub_p2_start: sub_p2_end + 1]
                
                # Graphing p2 linear regression        
                self.plot_phase3.scatter(
                            x_p2,
                            y_p2,
                            s = self.slider_width.GetValue(),
                            alpha = 0.5,
                            edgecolors = 'k',
                            facecolors = 'k'
                        )
                self.data_p2_slope.SetValue ('%0.3f'%(slope_p2))
                self.data_p2_int.SetValue ('%0.3f'%(intercept_p2))
                self.data_p2_r2.SetValue ('%0.3f'%(r2_p2))
            else:
                self.data_p2_slope.SetValue ('')
                self.data_p2_int.SetValue ('')
                self.data_p2_r2.SetValue ('') 
                
            if self.subj_p3_1textbox.GetValue () != '' and self.subj_p3_2textbox.GetValue () != '':
                sub_p3_start = int(self.subj_p3_1textbox.GetValue ()) - 1 # We get position in the series fromm the user; must convert to indexs 
                sub_p3_end = int(self.subj_p3_2textbox.GetValue ()) - 1
                x1_p3, x2_p3, y1_p3, y2_p3, r2_p3, slope_p3, intercept_p3 = Operations.subj_regression (x, y, sub_p3_start, sub_p3_end)
                # Drawing the subj linear regression line
                self.line_p3 = matplotlib.lines.Line2D ([x1_p3,x2_p3], [y1_p3,y2_p3], ls = '-', color = 'r', label = 'Phase III')
                self.plot_phase3.add_line (self.line_p3)
            
                # setting the series involved in linear regression
                x_p3 = x [sub_p3_start: sub_p3_end + 1] # Last index is not inclusive!
                y_p3 = y [sub_p3_start: sub_p3_end + 1]
                
                # Graphing p3 linear regression        
                self.plot_phase3.scatter(
                            x_p3,
                            y_p3,
                            s = self.slider_width.GetValue(),
                            alpha = 0.75,
                            edgecolors = 'k',
                            facecolors = 'k'
                        )
                self.data_p3_slope.SetValue ('%0.3f'%(slope_p3))
                self.data_p3_int.SetValue ('%0.3f'%(intercept_p3))
                self.data_p3_r2.SetValue ('%0.3f'%(r2_p3))
            else:
                self.data_p3_slope.SetValue ('')
                self.data_p3_int.SetValue ('')
                self.data_p3_r2.SetValue ('') 
            
                                   
        else: # OBJECTIVE REGRESSION
            num_points_obj = int (num_points_obj)
            if num_points_obj < 2:
                num_points_obj = 2
                self.obj_textbox.SetValue ('2')
                
            # Getting parameters from regression of p3
            #r2_p1, slope_p1, intercept_p1 = reg_p1_raw [6], reg_p1_raw [7], reg_p1_raw [8]
            x1_p3, x2_p3, y1_p3, y2_p3, r2, slope, intercept, reg_end_index = Operations.obj_regression_p3 (x, y, num_points_obj)
            # p3 is plotted later so that the legend entries are in order
                        
            # Getting parameters from regression of p1-2
            last_used_index = reg_end_index + 3
            reg_p1_raw, reg_p2_raw = Operations.obj_regression_p12 (x, y, last_used_index)
            
            # Unpacking parameters of p1 regression
            x_p1 = reg_p1_raw [0]
            y_p1 = reg_p1_raw [1]
            x1_p1, x2_p1 = reg_p1_raw [2], reg_p1_raw [3]
            y1_p1, y2_p1 = reg_p1_raw [4], reg_p1_raw [5]
            r2_p1, slope_p1, intercept_p1 = reg_p1_raw [6], reg_p1_raw [7], reg_p1_raw [8]
            
            # redefine second point in the p1 regression line to extend to x-axis
            y2_p1 = 0
            x2_p1 = -intercept_p1/slope_p1
            
            # Graphing the p1 series and regression line
            self.plot_phase3.scatter(
                        x_p1,
                        y_p1,
                        s = self.slider_width.GetValue(),
                        alpha = 0.25,
                        edgecolors = 'k',
                        facecolors = 'k'
                    )
            self.line_p1 = matplotlib.lines.Line2D ([x1_p1,x2_p1], [y1_p1,y2_p1], color = 'r', ls = '--', label = 'Phase I')
            self.plot_phase3.add_line (self.line_p1)            
            
            # Unpacking parameters of p2 regression
            x_p2 = reg_p2_raw [0]
            y_p2 = reg_p2_raw [1]
            x1_p2, x2_p2 = reg_p2_raw [2], reg_p2_raw [3]
            y1_p2, y2_p2 = reg_p2_raw [4], reg_p2_raw [5]
            r2_p2, slope_p2, intercept_p2 = reg_p2_raw [6], reg_p2_raw [7], reg_p2_raw [8]
            
            # redefine second point in the p2 regression line to extend to x-axis
            x2_p2 = x [-1]
            y2_p2 = slope_p2 * x2_p2 + intercept_p2
            
            # Graphing the p2 series and regression line
            self.plot_phase3.scatter(
                        x_p2,
                        y_p2,
                        s = self.slider_width.GetValue(),
                        alpha = 0.50,
                        edgecolors = 'k',
                        facecolors = 'k'
                    )
            self.line_p2 = matplotlib.lines.Line2D ([x1_p2,x2_p2], [y1_p2,y2_p2], color = 'r', ls = ':', label = 'Phase II')
            self.plot_phase3.add_line (self.line_p2)              
                        
            # Unpacking parameters of p3 regression            
            intercept_p3 = intercept[3]
            slope_p3 = slope [3]
            r2_p3 = r2[3]
            x_p3 = x [reg_end_index+3:] # setting the series' involved in linear regression
            y_p3 = y [reg_end_index+3:]            
            
            # Graphing the p3 series and regression line
            self.plot_phase3.scatter(
                        x_p3,
                        y_p3,
                        s = self.slider_width.GetValue(),
                        alpha = 0.75,
                        edgecolors = 'k',
                        facecolors = 'k'
                    )            
            self.line_p3 = matplotlib.lines.Line2D ([x1_p3,x2_p3], [y1_p3,y2_p3], color = 'r', ls = '-', label = 'Phase III')
            self.plot_phase3.add_line (self.line_p3)
            
            # Distiguishing the intial points used to start the regression and plotting them (solid red)
            x_init = x[len(x) - num_points_obj:] 
            y_init = y[len(x) - num_points_obj:]
            self.plot_phase3.scatter(
                        x_init,
                        y_init,
                        s = self.slider_width.GetValue(),
                        alpha = 0.5,
                        edgecolors = 'r',
                        facecolors = 'r'
                    )            
        
            # Outputting the data from the linear regressions
            self.data_p1_slope.SetValue ('%0.3f'%(slope_p1))
            self.data_p1_int.SetValue ('%0.3f'%(intercept_p1))
            self.data_p1_r2.SetValue ('%0.3f'%(r2_p1))
            
            self.data_p2_slope.SetValue ('%0.3f'%(slope_p2))
            self.data_p2_int.SetValue ('%0.3f'%(intercept_p2))
            self.data_p2_r2.SetValue ('%0.3f'%(r2_p2))        
            
            self.data_p3_slope.SetValue ('%0.3f'%(slope_p3))
            self.data_p3_int.SetValue ('%0.3f'%(intercept_p3))
            self.data_p3_r2.SetValue ('%0.3f'%(r2_p3))         
        
        # Adding our legend
        self.plot_phase3.legend(loc='upper right')
        self.fig.subplots_adjust(bottom = 0.13, left = 0.10)
        self.canvas.draw()
        
    def on_obj_draw (self, event):
        self.subj_p1_1textbox.SetValue ('')
        self.subj_p1_2textbox.SetValue ('')
        self.subj_p2_1textbox.SetValue ('')
        self.subj_p2_2textbox.SetValue ('')
        self.subj_p3_1textbox.SetValue ('')
        self.subj_p3_2textbox.SetValue ('')
        self.draw_figure()
        
    def on_subj_draw (self, event):
        self.obj_textbox.SetValue ('')
        self.draw_figure()    
    
    def on_cb_grid(self, event):
        self.draw_figure()
    
    def on_slider_width(self, event):
        self.draw_figure()
    
    def on_draw_button(self, event):
        self.draw_figure()
    
    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
        ind = event.ind
        x_clicked = np.take(x, ind)
        
        self.x_clicked_data.SetValue ('%0.2f'%(np.take(x, ind)[0]))
        self.y_clicked_data.SetValue ('%0.3f'%(np.take(y, ind)[0]))
        self.num_clicked_data.SetValue ('%0.0f'%(ind[0]+1))
        
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
        
    def on_exit(self, event):
        self.Destroy()
        
    def on_about(self, event):
        msg = """ A demo using wxPython with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw!")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        dlg = wx.MessageDialog(self, msg, "About", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')


if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = MainFrame()
    app.frame.Show()
    app.frame.Center()
    app.MainLoop()