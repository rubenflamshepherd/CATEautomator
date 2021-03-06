# The recommended way to use wx with mpl is with the WXAgg
# backend. 
import wx
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
	FigureCanvasWxAgg as FigCanvas
from matplotlib import gridspec
import numpy as np
import Custom

matplotlib.use('WXAgg')


# noinspection PyUnusedLocal
class RegError(wx.Dialog):
	"""window for user input error when invalid regression parameters received.
	"""

	def __init__(self, parent, id, error_msg, title='ERROR'):
		""" Constructor of 'Regression Analysis Error' box

		@type self: RegError
		@type parent: wx.Dialog | None
		@type id: int
			id number of parent window
		@type error_msg: str
			Error-specific message that is to be displayed.
		@type title: str
			Label for top on window
		@rtype: None
		"""
		wx.Dialog.__init__(self, parent, id, title)
		self.SetIcon(wx.Icon('Images/questionmark.ico', wx.BITMAP_TYPE_ICO))
		self.rootPanel = wx.Panel(self)
		inner_panel = wx.Panel(
			self.rootPanel, -1, size=(500, 260), style=wx.ALIGN_CENTER)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		vbox = wx.BoxSizer(wx.VERTICAL)
		inner_box = wx.BoxSizer(wx.VERTICAL)

		# Creating objects to place in window
		txt1 = "ERROR"
		txt2 = error_msg
		txt3 = "Please modify your input so that it is valid."
		line1 = wx.StaticLine(inner_panel, -1, style=wx.LI_HORIZONTAL)
		static_txt1 = wx.StaticText(
			inner_panel, id=-1, label=txt1, style=wx.ALIGN_CENTER, name="")
		static_txt2 = wx.StaticText(
			inner_panel, id=-1, label=txt2, style=wx.ALIGN_CENTER, name="")
		static_txt3 = wx.StaticText(
			inner_panel, id=-1, label=txt3, style=wx.ALIGN_CENTER, name="")
		btn1 = wx.Button(inner_panel, id=1, label="Ok")

		self.Bind(wx.EVT_BUTTON, self.on_close, id=1)

		inner_box.AddSpacer((150, 10))
		inner_box.Add(static_txt1, 0, wx.CENTER)
		inner_box.AddSpacer((150, 10))
		inner_box.Add(line1, 0, wx.CENTER | wx.EXPAND)
		inner_box.AddSpacer((150, 6))
		inner_box.Add(static_txt2, 0, wx.CENTER)
		inner_box.AddSpacer((150, 6))
		inner_box.Add(static_txt3, 0, wx.CENTER)
		inner_box.AddSpacer((150, 6))
		inner_box.Add(btn1, 0, wx.CENTER)
		inner_box.AddSpacer((150, 6))

		inner_panel.SetSizer(inner_box)
		hbox.Add(inner_panel, 0, wx.ALL | wx.ALIGN_CENTER)
		vbox.Add(hbox, 1, wx.ALL | wx.ALIGN_CENTER, 5)

		self.rootPanel.SetSizer(vbox)
		vbox.Fit(self)

	def on_close(self, event):
		"""Closing window when 'x' in top right corner is pressed

		@type self: AboutDialog
		@type event: Event
		@rtype: None
		"""
		self.Close()


# noinspection PyAttributeOutsideInit,PyShadowingNames,PyUnusedLocal,PyTypeChecker
class MainFrame(wx.Frame):
	"""The main preview frame of the application
	"""

	def __init__(self, experiment):
		"""Constructor of the main preview frame

		@type self: MainFrame
		@type experiment: Experiment
		@rtype: None
		"""
		wx.Frame.__init__(self, None, -1, 'vaCATE - ')

		self.SetIcon(wx.Icon('Images/testtube.ico', wx.BITMAP_TYPE_ICO))
		self.analysis_num = 0  # Attribute of frame, not exp/analysis
		self.experiment = experiment
		self.create_main_panel()
		# Default analysis: objective regression using the last 8 data points
		self.draw_figure()

	def create_main_panel(self):
		""" Creates the main panel with all the controls on it

		The controls are:
			* mpl canvas
			* mpl navigation toolbar
			* Control panel for interaction

		@type self: MainFrame
		@rtype: None
		"""
		self.panel = wx.Panel(self)

		# Create the mpl Figure and FigCanvas objects. 
		# 5x4 inches, 100 dots-per-inch
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
		self.canvas.mpl_connect('pick_event', self.on_pick_unstripped)
		# Bind the 'check' event for ticking 'Show Grid' option
		self.cb_grid = wx.CheckBox(
			self.panel, -1, "Show Grid", style=wx.ALIGN_CENTER)
		self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
		# Create the navigation toolbar, tied to the canvas
		self.toolbar = Custom.Toolbar(self)
		self.toolbar.Realize()
		# Layout with box sizers                
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
		self.vbox.Add(self.toolbar, 0, wx.EXPAND)
		self.vbox.AddSpacer(10)
		# Text labels describing regression inputs
		self.obj_title = wx.StaticText(
			self.panel, label="Objective Regression", style=wx.ALIGN_CENTER)
		self.obj_label = wx.StaticText(
			self.panel, label="Number of points to use:", style=wx.ALIGN_CENTER)
		self.subj_title = wx.StaticText(
			self.panel, label="Subjective Regression", style=wx.ALIGN_CENTER)
		self.subj1_label = wx.StaticText(
			self.panel, label="First Point:", style=wx.ALIGN_CENTER)
		self.subj2_label = wx.StaticText(
			self.panel, label="Last Point:", style=wx.ALIGN_CENTER)
		self.subj_disclaimer = wx.StaticText(
			self.panel, label="Points are elution times.", style=wx.ALIGN_CENTER)
		self.linedata_title = wx.StaticText(
			self.panel, label="Regression Parameters", style=wx.ALIGN_CENTER)

		# Text boxes for collecting subj/obj regression parameter input
		self.obj_textbox = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_PROCESS_ENTER)
		self.subj_p1_start_textbox = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_PROCESS_ENTER)
		self.subj_p1_end_textbox = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_PROCESS_ENTER)
		self.subj_p2_start_textbox = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_PROCESS_ENTER)
		self.subj_p2_end_textbox = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_PROCESS_ENTER)
		self.subj_p3_start_textbox = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_PROCESS_ENTER)
		self.subj_p3_end_textbox = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_PROCESS_ENTER)

		# Buttons + Bindings for identifying collect regression parameter events
		self.obj_draw_bttn = wx.Button(
			self.panel, -1, "Draw Objective Regression")
		self.obj_prop_bttn = wx.Button(
			self.panel, -1, "Propagate Regression")
		self.subj_draw_bttn = wx.Button(
			self.panel, -1, "Draw Subjective Regression")
		self.subj_prop_bttn = wx.Button(
			self.panel, -1, "Propagate Regression")
		self.Bind(wx.EVT_BUTTON, self.on_obj_draw, self.obj_draw_bttn)
		self.Bind(wx.EVT_BUTTON, self.on_obj_prop, self.obj_prop_bttn)
		self.Bind(wx.EVT_BUTTON, self.on_subj_draw, self.subj_draw_bttn)
		self.Bind(wx.EVT_BUTTON, self.on_subj_prop, self.subj_prop_bttn)

		# Lines de-marking separation between GUI sections
		self.line = wx.StaticLine(self.panel, -1, style=wx.LI_VERTICAL)
		self.line2 = wx.StaticLine(self.panel, -1, style=wx.LI_VERTICAL)
		self.line3 = wx.StaticLine(self.panel, -1, style=wx.LI_VERTICAL)
		self.line4 = wx.StaticLine(self.panel, -1, style=wx.LI_HORIZONTAL)

		# Alignment flags (for adding things to spacers) and fonts
		flags = wx.ALIGN_RIGHT | wx.ALL | wx.ALIGN_CENTER_VERTICAL
		box_flag = wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_CENTER_VERTICAL
		title_font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
		widget_title_font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, True)
		disclaimer_font = wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

		# Setting fonts
		self.obj_title.SetFont(title_font)
		self.subj_title.SetFont(title_font)
		self.linedata_title.SetFont(title_font)
		self.subj_disclaimer.SetFont(disclaimer_font)

		# Adding objective widgets to objective sizer
		self.vbox_obj = wx.BoxSizer(wx.VERTICAL)
		self.vbox_obj.Add(self.obj_title, 0, border=3, flag=box_flag)
		self.vbox_obj.AddSpacer(7)
		self.vbox_obj.Add(self.obj_label, 0, border=3, flag=box_flag)
		self.vbox_obj.AddSpacer(5)
		self.vbox_obj.Add(self.obj_textbox, 0, border=3, flag=box_flag)
		self.vbox_obj.AddSpacer(5)
		self.vbox_obj.Add(self.obj_draw_bttn, 0, border=3, flag=box_flag)
		self.vbox_obj.AddSpacer(1)
		self.vbox_obj.Add(self.obj_prop_bttn, 0, border=3, flag=box_flag)

		# Adding subjective widgets to subjective sizer
		self.gridbox_subj = wx.GridSizer(rows=4, cols=3, hgap=1, vgap=1)
		self.gridbox_subj.Add(
			wx.StaticText(self.panel, id=-1, label=""), 0, border=3, flag=flags)
		self.gridbox_subj.Add(self.subj1_label, 0, border=3, flag=box_flag)
		self.gridbox_subj.Add(self.subj2_label, 0, border=3, flag=box_flag)
		self.gridbox_subj.Add(
			wx.StaticText(self.panel, label="Phase I:"), 0, border=3, flag=flags)
		self.gridbox_subj.Add(
			self.subj_p1_start_textbox, 0, border=3, flag=box_flag)
		self.gridbox_subj.Add(
			self.subj_p1_end_textbox, 0, border=3, flag=box_flag)
		self.gridbox_subj.Add(
			wx.StaticText(self.panel, label="Phase II:"), 0, border=3, flag=flags)
		self.gridbox_subj.Add(
			self.subj_p2_start_textbox, 0, border=3, flag=box_flag)
		self.gridbox_subj.Add(
			self.subj_p2_end_textbox, 0, border=3, flag=box_flag)
		self.gridbox_subj.Add(
			wx.StaticText(self.panel, label="Phase III:"), 0, border=3, flag=flags)
		self.gridbox_subj.Add(
			self.subj_p3_start_textbox, 0, border=3, flag=box_flag)
		self.gridbox_subj.Add(
			self.subj_p3_end_textbox, 0, border=3, flag=box_flag)

		self.vbox_subj = wx.BoxSizer(wx.VERTICAL)
		self.vbox_subj.Add(self.subj_title, 0, border=3, flag=box_flag)
		self.vbox_subj.Add(self.gridbox_subj, 0, border=3, flag=box_flag)
		self.vbox_subj.Add(self.subj_draw_bttn, 0, border=3, flag=box_flag)
		self.vbox_subj.Add(self.subj_prop_bttn, 0, border=3, flag=box_flag)
		self.vbox_subj.Add(self.subj_disclaimer, 0, border=3, flag=box_flag)

		# Creating widgets for data output
		self.data_p1_int = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p1_slope = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p1_r2 = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p1_k = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p1_t05 = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p1_efflux = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)

		self.data_p2_int = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p2_slope = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p2_r2 = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p2_k = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p2_t05 = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p2_efflux = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)

		self.data_p3_int = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p3_slope = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p3_r2 = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p3_k = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p3_t05 = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_p3_efflux = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)

		self.data_SA = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_shtcnts = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_rtcnts = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_rtwght = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_loadtime = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_influx = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_netflux = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_ratio = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.data_poolsize = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)

		# Creating labels for data output
		slope_text = wx.StaticText(self.panel, label="Slope")
		intercept_text = wx.StaticText(self.panel, label="Intercept")
		r2_text = wx.StaticText(self.panel, label=u"R\u00B2")
		p1_text = wx.StaticText(self.panel, label="Phase I: ")
		p2_text = wx.StaticText(self.panel, label="Phase II: ")
		p3_text = wx.StaticText(self.panel, label="Phase III: ")
		k_text = wx.StaticText(self.panel, label="k")
		halflife_text = wx.StaticText(self.panel, label="Half Life")
		efflux_text = wx.StaticText(self.panel, label="Efflux")

		# Labels for gridsizer2
		SA_text = wx.StaticText(self.panel, label="SA")
		rtcnts_text = wx.StaticText(self.panel, label="Rt Cnts")
		shtcnts_text = wx.StaticText(self.panel, label="Sh Cnts")
		rtwght_text = wx.StaticText(self.panel, label="Rt Weight")
		loadtime_text = wx.StaticText(self.panel, label="Load Time")
		influx_text = wx.StaticText(self.panel, label="Influx")
		netflux_text = wx.StaticText(self.panel, label="Net Flux")
		ratio_text = wx.StaticText(self.panel, label="E:I Ratio")
		poolsize_text = wx.StaticText(self.panel, label="Pool size")

		# Adding data output widgets to data output gridsizers        
		self.gridbox_data = wx.GridSizer(rows=4, cols=7, hgap=1, vgap=1)

		self.gridbox_data.Add(wx.StaticText(
			self.panel, label=""), 0, border=3, flag=flags)
		self.gridbox_data.Add(slope_text, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(intercept_text, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(r2_text, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(k_text, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(halflife_text, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(efflux_text, 0, border=3, flag=box_flag)

		self.gridbox_data.Add(p1_text, 0, border=3, flag=flags)
		self.gridbox_data.Add(self.data_p1_slope, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p1_int, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p1_r2, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p1_k, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p1_t05, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p1_efflux, 0, border=3, flag=box_flag)

		self.gridbox_data.Add(p2_text, 0, border=3, flag=flags)
		self.gridbox_data.Add(self.data_p2_slope, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p2_int, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p2_r2, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p2_k, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p2_t05, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p2_efflux, 0, border=3, flag=box_flag)

		self.gridbox_data.Add(p3_text, 0, border=3, flag=flags)
		self.gridbox_data.Add(self.data_p3_slope, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p3_int, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p3_r2, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p3_k, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p3_t05, 0, border=3, flag=box_flag)
		self.gridbox_data.Add(self.data_p3_efflux, 0, border=3, flag=box_flag)

		self.gridbox_data2 = wx.GridSizer(rows=2, cols=9, hgap=1, vgap=1)
		self.gridbox_data2.Add(SA_text, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(shtcnts_text, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(rtcnts_text, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(rtwght_text, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(loadtime_text, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(influx_text, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(netflux_text, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(ratio_text, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(poolsize_text, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(self.data_SA, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(self.data_shtcnts, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(self.data_rtcnts, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(self.data_rtwght, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(self.data_loadtime, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(self.data_influx, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(self.data_netflux, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(self.data_ratio, 0, border=3, flag=box_flag)
		self.gridbox_data2.Add(self.data_poolsize, 0, border=3, flag=box_flag)

		self.vbox_linedata = wx.BoxSizer(wx.VERTICAL)
		self.vbox_linedata.Add(self.linedata_title, 0, border=3, flag=box_flag)
		self.vbox_linedata.Add(self.gridbox_data, 0, border=3, flag=box_flag)
		self.vbox_linedata.Add(self.line4, 0, wx.CENTER | wx.EXPAND)
		self.vbox_linedata.Add(self.gridbox_data2, 0, border=3, flag=box_flag)

		# Build the widgets and the sizer contain(s) containing them all
		# Build slider to adjust point radius
		self.slider_label = wx.StaticText(
			self.panel, -1, "Point Radius", style=wx.ALIGN_CENTER)
		self.slider_label.SetFont(widget_title_font)
		self.slider_width = wx.Slider(
			self.panel, -1, value=40, minValue=1, maxValue=200,
			style=wx.SL_AUTOTICKS | wx.SL_LABELS)
		self.slider_width.SetTickFreq(10, 1)
		self.Bind(
			wx.EVT_COMMAND_SCROLL_THUMBTRACK, self.on_slider_width, self.slider_width)
		self.vbox_widgets = wx.BoxSizer(wx.VERTICAL)
		self.vbox_widgets.Add(self.cb_grid, 0, border=3, flag=box_flag)
		self.vbox_widgets.Add(self.slider_label, 0, flag=box_flag)
		self.vbox_widgets.Add(self.slider_width, 0, border=3, flag=box_flag)

		# Build widget that displays information about last widget clicked

		# Creating the 'last clicked' items
		self.xy_clicked_label = wx.StaticText(
			self.panel, -1, "Last point clicked", style=wx.ALIGN_CENTER)
		self.xy_clicked_label.SetFont(widget_title_font)
		self.x_clicked_label = wx.StaticText(
			self.panel, -1, "Elution Time (x): ", style=wx.ALIGN_CENTER)
		self.y_clicked_label = wx.StaticText(
			self.panel, -1, "Log cpm (y): ", style=wx.ALIGN_CENTER)
		self.num_clicked_label = wx.StaticText(
			self.panel, -1, "Point Number: ", style=wx.ALIGN_CENTER)
		self.x_clicked_data = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.y_clicked_data = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)
		self.num_clicked_data = wx.TextCtrl(
			self.panel, size=(50, -1), style=wx.TE_READONLY)

		# Assembling the 'last clicked' items into sizers
		self.hbox_x_clicked = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_x_clicked.AddSpacer(10)
		self.hbox_x_clicked.Add(self.x_clicked_label, 0, flag=flags)
		self.hbox_x_clicked.Add(self.x_clicked_data, 0, flag=flags)
		self.hbox_y_clicked = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_y_clicked.AddSpacer(10)
		self.hbox_y_clicked.Add(self.y_clicked_label, 0, flag=flags)
		self.hbox_y_clicked.Add(self.y_clicked_data, 0, flag=flags)
		self.hbox_num_clicked = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_num_clicked.AddSpacer(10)
		self.hbox_num_clicked.Add(self.num_clicked_label, 0, flag=flags)
		self.hbox_num_clicked.Add(self.num_clicked_data, 0, flag=flags)

		self.vbox_widgets.Add(self.xy_clicked_label, 0, flag=box_flag)
		self.vbox_widgets.Add(self.hbox_x_clicked, 0, flag=flags)
		self.vbox_widgets.Add(self.hbox_y_clicked, 0, flag=flags)
		self.vbox_widgets.Add(self.hbox_num_clicked, 0, flag=flags)

		# Assembling items for subjective regression field into sizers
		self.hbox_regres = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_regres.Add(self.vbox_obj)
		self.hbox_regres.AddSpacer(5)
		self.hbox_regres.Add(self.line, 0, wx.CENTER | wx.EXPAND)
		self.hbox_regres.AddSpacer(5)
		self.hbox_regres.Add(self.vbox_subj)
		self.hbox_regres.Add(self.line2, 0, wx.CENTER | wx.EXPAND)
		self.hbox_regres.AddSpacer(5)
		self.hbox_regres.Add(self.vbox_linedata)
		self.hbox_regres.Add(self.line3, 0, wx.CENTER | wx.EXPAND)
		self.hbox_regres.Add(self.vbox_widgets, 0, wx.CENTER | wx.EXPAND)

		self.vbox.Add(self.hbox_regres, 0, flag=wx.ALIGN_CENTER | wx.TOP)

		self.panel.SetSizer(self.vbox)
		self.vbox.Fit(self)

	def create_status_bar(self):
		"""Creates the status bar

		@type self: MainFrame
		@rtype: None
		"""
		self.statusbar = self.CreateStatusBar()

	def draw_figure(self):
		"""Redraws the figures

		@type self: MainFrame
		@rtype: None
		"""
		analysis = self.experiment.analyses[self.analysis_num]

		if analysis.kind == 'obj':
			self.obj_textbox.SetValue(str(analysis.obj_num_pts))
			self.subj_p1_start_textbox.SetValue('')
			self.subj_p1_end_textbox.SetValue('')
			self.subj_p2_start_textbox.SetValue('')
			self.subj_p2_end_textbox.SetValue('')
			self.subj_p3_start_textbox.SetValue('')
			self.subj_p3_end_textbox.SetValue('')
		elif analysis.kind == 'subj':
			self.obj_textbox.SetValue('')
			if analysis.xs_p3 != ('', ''):
				self.subj_p3_start_textbox.SetValue(
					str(analysis.xs_p3[0]))
				self.subj_p3_end_textbox.SetValue(
					str(analysis.xs_p3[1]))
			if analysis.xs_p2 != ('', ''):
				self.subj_p2_start_textbox.SetValue(
					str(analysis.xs_p2[0]))
				self.subj_p2_end_textbox.SetValue(
					str(analysis.xs_p2[1]))
			if analysis.xs_p1 != ('', ''):
				self.subj_p1_start_textbox.SetValue(
					str(analysis.xs_p1[0]))
				self.subj_p1_end_textbox.SetValue(
					str(analysis.xs_p1[1]))

		title_string = 'vaCATE - '
		detail_string = "Run " + str(self.analysis_num + 1) + "/" \
						+ str(len(self.experiment.analyses))
		name_string = ' - "' + analysis.run.name + '"'
		self.SetTitle(title_string + detail_string + name_string)

		# Making sure toolbar buttons navigate to runs that exist
		if self.analysis_num == 0:
			self.toolbar.EnableTool(self.toolbar.ON_PREVIOUS, False)
		else:
			self.toolbar.EnableTool(self.toolbar.ON_PREVIOUS, True)

		if self.analysis_num == len(self.experiment.analyses) - 1:
			self.toolbar.EnableTool(self.toolbar.ON_NEXT, False)
		else:
			self.toolbar.EnableTool(self.toolbar.ON_NEXT, True)

		# Clearing the plots so they can be redrawn anew
		self.plot_phase1.clear()
		self.plot_phase2.clear()
		self.plot_phase3.clear()

		self.plot_phase1.grid(self.cb_grid.IsChecked())
		self.plot_phase2.grid(self.cb_grid.IsChecked())
		self.plot_phase3.grid(self.cb_grid.IsChecked())

		# Graphing complete log efflux data set
		self.plot_phase3.scatter(
			analysis.run.x, analysis.run.y, s=self.slider_width.GetValue(),
			alpha=0.5, edgecolors='k', facecolors='w', picker=5)

		# Setting axes labels/limits
		self.plot_phase3.set_xlabel('Elution time (min)')
		self.plot_phase2.set_xlabel('Elution time (min)')
		self.plot_phase3.set_ylabel(u"Log cpm released/g RFW/min")
		self.plot_phase3.set_xlim(left=0)
		self.plot_phase3.set_ylim(bottom=0)

		# Graphing the p3 series and regression line
		if analysis.xs_p3 != ('', '') and analysis.phase3.xs != ('', ''):
			self.plot_phase3.scatter(
				analysis.phase3.x_series, analysis.phase3.y_series,
				s=self.slider_width.GetValue(),
				alpha=0.75, edgecolors='k', facecolors='k')
			line_p3 = matplotlib.lines.Line2D(
				[analysis.phase3.xy1[0], analysis.phase3.xy2[0]],
				[analysis.phase3.xy1[1], analysis.phase3.xy2[1]],
				color='r', ls='-', label='Phase III')
			self.plot_phase3.add_line(line_p3)
			# Find+plot initial points used to start obj regression
			if analysis.kind == 'obj':
				self.plot_phase3.scatter(
					analysis.obj_x_start, analysis.obj_y_start,
					s=self.slider_width.GetValue(),
					alpha=0.5, edgecolors='r', facecolors='r')
			# Outputting the data from the linear regressions to widgets         
			self.data_p3_slope.SetValue('%0.4f' % analysis.phase3.slope)
			self.data_p3_int.SetValue('%0.4f' % analysis.phase3.intercept)
			self.data_p3_r2.SetValue('%0.4f' % analysis.phase3.r2)
			self.data_p3_k.SetValue('%0.4f' % analysis.phase3.k)
			self.data_p3_t05.SetValue('%0.4f' % analysis.phase3.t05)
			self.data_p3_efflux.SetValue('%0.4f' % analysis.phase3.efflux)

			self.data_SA.SetValue('%0.0f' % analysis.run.SA)
			self.data_shtcnts.SetValue('%0.0f' % analysis.run.sht_cnts)
			self.data_rtcnts.SetValue('%0.0f' % analysis.run.rt_cnts)
			self.data_rtwght.SetValue('%0.3f' % analysis.run.rt_wght)
			self.data_loadtime.SetValue('%0.2f' % analysis.run.load_time)
			self.data_influx.SetValue('%0.3f' % analysis.influx)
			self.data_netflux.SetValue('%0.3f' % analysis.netflux)
			self.data_ratio.SetValue('%0.3f' % analysis.ratio)
			self.data_poolsize.SetValue('%0.3f' % analysis.poolsize)

		# Graphing raw uncorrected data of p1 and p2
		if analysis.xs_p2 != ('', '') and analysis.phase2.xs != ('', ''):
			self.plot_phase2.scatter(
				analysis.x_p12, analysis.y_p12, s=self.slider_width.GetValue(),
				alpha=0.50, edgecolors='k', facecolors='w', picker=5)

			# Graphing curve-stripped (corrected) phase I and II data, isolated
			# p2 data and line of best fit
			self.plot_phase2.scatter(
				analysis.x_p12_curvestrip_p3,
				analysis.y_p12_curvestrip_p3,
				s=self.slider_width.GetValue(),
				alpha=0.50, edgecolors='r', facecolors='w')

			self.plot_phase2.scatter(
				analysis.phase2.x_series,
				analysis.phase2.y_series,
				s=self.slider_width.GetValue(),
				alpha=0.75, edgecolors='k', facecolors='k')

			self.line_p2 = matplotlib.lines.Line2D(
				[analysis.phase2.xy1[0], analysis.phase2.xy2[0]],
				[analysis.phase2.xy1[1], analysis.phase2.xy2[1]],
				color='r', ls='--', label='Phase II')
			self.plot_phase2.add_line(self.line_p2)  # Outputting the data from the linear regressions to widgets
			self.data_p2_slope.SetValue('%0.3f' % analysis.phase2.slope)
			self.data_p2_int.SetValue('%0.3f' % analysis.phase2.intercept)
			self.data_p2_r2.SetValue('%0.3f' % analysis.phase2.r2)
			self.data_p2_k.SetValue('%0.3f' % analysis.phase2.k)
			self.data_p2_t05.SetValue('%0.3f' % analysis.phase2.t05)
			self.data_p2_efflux.SetValue('%0.2f' % analysis.phase2.efflux)

		# Graphing the p1 series and regression line	
		if analysis.xs_p1 != ('', '') and analysis.phase1.xs != ('', ''):
			self.plot_phase1.scatter(
				analysis.x_p1, analysis.y_p1,
				s=self.slider_width.GetValue(),
				alpha=0.25, edgecolors='k', facecolors='w', picker=5)

			# Graph p1 data corrected for p3
			self.plot_phase1.scatter(
				analysis.x_p1_curvestrip_p3,
				analysis.y_p1_curvestrip_p3,
				s=self.slider_width.GetValue(),
				alpha=0.25, edgecolors='r', facecolors='w')

			self.plot_phase1.scatter(
				analysis.x_p1_curvestrip_p23,
				analysis.y_p1_curvestrip_p23,
				s=self.slider_width.GetValue(),
				alpha=0.75, edgecolors='k', facecolors='k')

			self.line_p1 = matplotlib.lines.Line2D(
				[analysis.phase1.xy1[0], analysis.phase1.xy2[0]],
				[analysis.phase1.xy1[1], analysis.phase1.xy2[1]],
				color='r', ls=':', label='Phase I')
			self.plot_phase1.add_line(self.line_p1)

			# Outputting the data from the linear regressions to widgets        
			self.data_p1_slope.SetValue('%0.3f' % analysis.phase1.slope)
			self.data_p1_int.SetValue('%0.3f' % analysis.phase1.intercept)
			self.data_p1_r2.SetValue('%0.3f' % analysis.phase1.r2)
			self.data_p1_k.SetValue('%0.3f' % analysis.phase1.k)
			self.data_p1_t05.SetValue('%0.3f' % analysis.phase1.t05)
			self.data_p1_efflux.SetValue('%0.1f' % analysis.phase1.efflux)

		# Adding our legends
		self.plot_phase1.legend(loc='upper right')
		self.plot_phase2.legend(loc='upper right')
		self.plot_phase3.legend(loc='upper right')
		self.fig.subplots_adjust(bottom=0.13, left=0.10)
		self.canvas.draw()

	def check_obj_input(self, obj_input_raw):
		"""Check the input for objective regression to make sure its valid

		@type self: MainFrame
		@type obj_input_raw: Object
		@rtype: bool
		"""
		elut_ends_temp = self.experiment.analyses[self.analysis_num].run.elut_ends
		try:
			obj_input = int(obj_input_raw)
			if obj_input not in range(3, len(elut_ends_temp) // 2):
				msg = "'%s' must be between 3 and %s." % (obj_input, len(elut_ends_temp) // 2 - 1)
				dlg = RegError(self, -1, msg)
				dlg.ShowModal()
				dlg.Destroy()
				return False
		except ValueError:
			msg = "'%s' must be convertible to an integer." % obj_input_raw
			dlg = RegError(self, -1, msg)
			dlg.ShowModal()
			dlg.Destroy()
			return False
		return True

	def on_obj_draw(self, event):
		"""Redraws the figures according to new objective analysis
		
		@type self: MainFrame
		@type event: Event
		@rtype: None
		"""
		if self.check_obj_input(self.obj_textbox.GetValue()):
			# Doing new analysis and saving it	
			new_analysis = self.experiment.analyses[self.analysis_num]
			new_analysis.kind = 'obj'
			new_analysis.obj_num_pts = int(self.obj_textbox.GetValue())
			new_analysis.analyze()
			self.experiment.analyses[self.analysis_num] = new_analysis
			self.draw_figure()

	def on_obj_prop(self, event):
		"""Propagates settings of current objective analysis to all analyses
		
		@type self: MainFrame
		@type event: Event
		@rtype: None
		"""
		obj_num_pts = int(self.obj_textbox.GetValue())
		for analysis_num in range(0, len(self.experiment.analyses)):
			new_analysis = self.experiment.analyses[analysis_num]
			new_analysis.kind = 'obj'
			new_analysis.obj_num_pts = obj_num_pts
			new_analysis.analyze()
			self.experiment.analyses[analysis_num] = new_analysis
		self.draw_figure()

	def check_phase_boundary(self, boundary_raw, elut_ends_temp):
		"""Returns whether <boundary_raw> == '' or is in <elut_ends_temp>.

		Creates a dialog box with a meaningful error message if both boundary
			conditions are false.

		@type boundary_raw: Object
		@type elut_ends_temp: [float]
		@rtype: bool
		"""
		try:
			if boundary_raw != '':
				boundary = float(boundary_raw)
				if boundary not in elut_ends_temp:
					msg = "'%s' must be an elution time (min)." % boundary_raw
					dlg = RegError(self, -1, msg)
					val = dlg.ShowModal()
					dlg.Destroy()
					return False
		except ValueError:
			msg = "'%s' must be convertible to a floating point integer." % boundary_raw
			dlg = RegError(self, -1, msg)
			dlg.ShowModal()
			dlg.Destroy()
			return False
		return True

	def check_boundary_order(self, boundary_start, boundary_end):
		"""Returns whether <boundary_start> and <boundary_end> are a valid pair.

		Valid pair: either both '' or both in elut_ends and	
			<boundary_start> < <boundary_end>		
		Creates a dialog box with a meaningful error message if both boundary
			conditions are false.

		Precondition: <boundary_start> and <boundary_end> are valid phase 
			boundaries (either '' or in elut_ends)

		@type boundary_start: str
		@type boundary_end: str
		@rtype: bool
		"""
		if boundary_start == '' and boundary_end == '':
			return True
		elif boundary_start == '' and boundary_end != '':
			msg = "Only one end of a phase (%s min) has been defined." % boundary_end
			dlg = RegError(self, -1, msg)
			dlg.ShowModal()
			dlg.Destroy()
			return False
		elif boundary_start != '' and boundary_end == '':
			msg = "Only one end of a phase (%s min) has been defined." % boundary_start
			dlg = RegError(self, -1, msg)
			dlg.ShowModal()
			dlg.Destroy()
			return False
		elif float(boundary_start) >= float(boundary_end) != '':
			msg = "The start of a defined phase must before after its end (%s must be before %s)." \
					% (boundary_start, boundary_end)
			dlg = RegError(self, -1, msg)
			dlg.ShowModal()
			dlg.Destroy()
			return False
		return True

	def check_phase_order(
			self, previous_start, previous_end, current_start, current_end,
			previous_num, current_num):
		"""Returns whether a previous phase can be defined.

		A previous phase can only be defined if the current phase is defined.
		Phases can not overlap.
		Creates a dialog box with a meaningful error message if the current 
			phase is not defined and the previous one is.

		Precondition: phase boundaries are valid inputs.

		@type previous_start: int
			elution time point where previous phase starts
		@type previous_end: int
			elution time point where previous phase ends			
		@type current_start: int
			elution time point where current phase starts
		@type current_end: int
			elution time point where current phase ends
		@type previous_num: 'I' | 'II'
			phase number of previous phase
		@type current_num: 'II' | 'III'
			phase number of current phase
		@rtype: bool
		"""
		if (previous_start, previous_end) == ('', ''):
			return True
		elif (previous_start, previous_end) != ('', '') and \
							(current_start, current_end) == ('', ''):
			msg = "You can not define Phase %s if a later phase (%s) is undefined." % (previous_num, current_num)
			dlg = RegError(self, -1, msg)
			dlg.ShowModal()
			dlg.Destroy()
			return False
		elif float(previous_end) >= float(current_start):
			msg = "A previous phase extends beyond a later phase (%s >= %s)." % (previous_end, current_start)
			dlg = RegError(self, -1, msg)
			dlg.ShowModal()
			dlg.Destroy()
			return False
		return True

	def check_subj_input(self):
		"""Confirm that subjective analysis input is valid.

		Return True if it is. False otherwise.

		@type self: MainFrame
		@rtype: bool
		"""
		elut_ends_temp = self.experiment.analyses[self.analysis_num].run.elut_ends

		# First confirm that individual inputs are valid		
		p3_start = self.subj_p3_start_textbox.GetValue()
		if not self.check_phase_boundary(p3_start, elut_ends_temp):
			return False
		p3_end = self.subj_p3_end_textbox.GetValue()
		if not self.check_phase_boundary(p3_end, elut_ends_temp):
			return False
		p2_start = self.subj_p2_start_textbox.GetValue()
		if not self.check_phase_boundary(p2_start, elut_ends_temp):
			return False
		p2_end = self.subj_p2_end_textbox.GetValue()
		if not self.check_phase_boundary(p2_end, elut_ends_temp):
			return False
		p1_start = self.subj_p1_start_textbox.GetValue()
		if not self.check_phase_boundary(p1_start, elut_ends_temp):
			return False
		p1_end = self.subj_p1_end_textbox.GetValue()

		# Then determine that input pairs for a phase are valid
		if not self.check_boundary_order(p3_start, p3_end):
			return False
		if not self.check_boundary_order(p2_start, p2_end):
			return False
		if not self.check_boundary_order(p1_start, p1_end):
			return False

		# Finally, determine that phases are valid relative to each other.
		if not self.check_phase_order(
				p1_start, p1_end, p2_start, p2_end, 'I', 'II'):
			return False
		if not self.check_phase_order(
				p2_start, p2_end, p3_start, p3_end, 'II', 'III'):
			return False
		if not self.check_phase_order(
				p1_start, p1_end, p3_start, p3_end, 'I', 'III'):
			return False

		return True

	def create_single_subj(
			self, analysis_num,
			(p3_start, p3_end), (p2_start, p2_end), (p1_start, p1_end)):
		"""Calculate a new subjective analysis from user input

		Phase boundaries are passed as individual tuples because they may not
			necessarily be grabbed from user input every time (i.e. when user
			chooses to propagate regression).

		Precondition: self.check_subj_input() is True
		
		@type self: MainFrame
		@type analysis_num
			index of analysis to be created using subjective regression
		@rtype: None
		"""
		# Start new subjective analysis
		new_analysis = self.experiment.analyses[analysis_num]
		new_analysis.kind = 'subj'
		new_analysis.xs_p3 = ('', '')
		new_analysis.xs_p2 = ('', '')
		new_analysis.xs_p1 = ('', '')
		# Convert subjective analysis textbox entries to floats
		new_analysis.xs_p3 = (p3_start, p3_end)
		if p3_start != '' and p3_end != '':
			p3_start, p3_end = float(p3_start), float(p3_end)
			new_analysis.xs_p3 = (p3_start, p3_end)
		if p2_start != '' and p2_end != '':
			p2_start, p2_end = float(p2_start), float(p2_end)
			new_analysis.xs_p2 = (p2_start, p2_end)
		if p1_start != '' and p1_end != '':
			p1_start, p1_end = float(p1_start), float(p1_end)
			new_analysis.xs_p1 = (p1_start, p1_end)
		new_analysis.analyze()
		self.experiment.analyses[analysis_num] = new_analysis

	def on_subj_draw(self, event):
		"""Redraws the figures according to a single new subjective analysis
		
		@type self: MainFrame
		@type event: Event
		@rtype: None
		"""
		# Get subjective analysis parameters		
		p3_start = self.subj_p3_start_textbox.GetValue()
		p3_end = self.subj_p3_end_textbox.GetValue()
		p2_start = self.subj_p2_start_textbox.GetValue()
		p2_end = self.subj_p2_end_textbox.GetValue()
		p1_start = self.subj_p1_start_textbox.GetValue()
		p1_end = self.subj_p1_end_textbox.GetValue()
		if self.check_subj_input():
			self.create_single_subj(
				self.analysis_num,
				(p3_start, p3_end), (p2_start, p2_end), (p1_start, p1_end)
			)
			self.draw_figure()

	def on_subj_prop(self, event):
		"""Propagates settings of current subjective analysis to all analyses
		
		@type self: MainFrame
		@type event: Event
		@rtype: None
		"""
		# Get subjective analysis parameters		
		p3_start = self.subj_p3_start_textbox.GetValue()
		p3_end = self.subj_p3_end_textbox.GetValue()
		p2_start = self.subj_p2_start_textbox.GetValue()
		p2_end = self.subj_p2_end_textbox.GetValue()
		p1_start = self.subj_p1_start_textbox.GetValue()
		p1_end = self.subj_p1_end_textbox.GetValue()
		if self.check_subj_input():
			for analysis_num in range(0, len(self.experiment.analyses)):
				self.create_single_subj(
					analysis_num,
					(p3_start, p3_end), (p2_start, p2_end), (p1_start, p1_end)
				)
			self.draw_figure()

	def on_cb_grid(self, event):
		"""Redraw figures with grids
		
		@type self: MainFrame
		@type event: Event
		@rtype: None
		"""
		self.draw_figure()

	def on_slider_width(self, event):
		"""Redraw figures with data point size changed
		
		@type self: MainFrame
		@type event: Event
		@rtype: None
		"""
		self.draw_figure()

	def on_pick_unstripped(self, event):
		"""Outputs data when un-stripped data point is clicked
		
		@type self: MainFrame
		@type event: Event
		@rtype: None
		"""
		# The event received here is of the type
		#   matplotlib.backend_bases.PickEvent
		# It carries lots of information, of which we're using
		#   only a small amount here.
		ind = event.ind
		analysis = self.experiment.analyses[self.analysis_num]
		x_clicked = np.take(analysis.run.x, ind)
		self.x_clicked_data.SetValue('%0.2f' % (np.take(analysis.run.x, ind)[0]))
		self.y_clicked_data.SetValue('%0.3f' % (np.take(analysis.run.y, ind)[0]))
		self.num_clicked_data.SetValue('%0.0f' % (ind[0] + 1))

	def on_exit(self, event):
		"""Closes windows when 'x' at top is clicked.
		
		@type self: MainFrame
		@type event: Event
		@rtype: None
		"""
		self.Destroy()


if __name__ == '__main__':
	import os
	import Excel

	directory = os.path.dirname(os.path.abspath(__file__))
	file_path = os.path.join(directory, "Tests/3/Test_MultiRun1.xlsx")
	temp_experiment = Excel.grab_data(file_path)
	for analysis in temp_experiment.analyses:
		analysis.kind = 'subj'
		analysis.xs_p1 = (1, 4)
		analysis.xs_p2 = (5, 10)
		analysis.xs_p3 = (11.5, 40)
		analysis.analyze()
	"""
	temp_experiment.analyses[0].kind = 'obj'
	temp_experiment.analyses[0].obj_num_pts = 8
	temp_experiment.analyses[0].analyze()
	"""
	app = wx.PySimpleApp()
	app.frame = MainFrame(temp_experiment)

	app.frame.Show()
	app.frame.Center()

	app.MainLoop()
