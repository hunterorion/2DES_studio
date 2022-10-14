from BMIRG_Lib import Framework
from BMIRG_Lib import _2DFM
from BMIRG_Lib import Modelling
import tkinter as tk
from tkinter import ttk
import lmfit
import pathlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

#Upon opening a new file the axes are still not clearing properly this needs to be addressed!!
class _2DFM_Studio(Framework):
    def __init__(self, root):
        super().__init__(root,title="2DES Studio",versionNo="1.0")
        self.create_gui()
        self._2DFM = _2DFM()
        self.model = Modelling()
        
        self.scrollLock = True

        self.exp_cb = None
        self.mod_cb = None
        
        self.mod_em_ind = None
        self.mod_ex_ind = None
        self.mod_em_plot = None
        self.mod_ex_plot = None

        ##Settings##
        showResidual = False
        #Colours - Maybe should add colour-blind toggle?
        self.em_slice_col = "k"
        self.ex_slice_col = "r"
        self.fit_col = "steelblue"
        self.resid_col = "green"
        self.focus_col = "m"
        self.em_step = 1 #maybe should add a course control toggle into the program
        self.ex_step = 10
        
    def create_gui(self):
        super().create_gui()
        tab_definitions = ("view-p- 3,3,0.5,0.3 - ax1/0/1:3/True/scroll_event&self.onscroll ,ax2/1:3/0/True/scroll_event&self.onscroll , ax3/1:3/1:3/False/None "
                     ,"fit-p- 2,3,0.4,0.3 - ax1/0/0:2/True/scroll_event&self.onscroll,ax2/0/2/False/None ,ax3/1/0:2/True/scroll_event&self.onscroll ,ax4/1/2/True/None " )
        self.build_tab_control(tab_definitions)
        self.create_bottom_bar()
        self.bind_menu_accelerator_keys()
        self.button = ttk.Button(self.top_bar, text="Update Model")
        self.button.bind("<Button-1>",self.update_model)
        self.button.pack(side="right")
    
    def onscroll(self,event):
        #Future revisions should limit the number of frames and updates per second similar to modern game enegines to ensure consistent performance across different computers.
        if event.inaxes == self.tabs["view"]["ax2"] and not self.scrollLock or event.inaxes == self.tabs["fit"]["ax1"] and not self.scrollLock:
            if event.button == "up":
                self._2DFM.ex_ind = (self._2DFM.ex_ind + self.em_step) % self._2DFM.data.shape[1]
                self.model.ex_ind = self._2DFM.ex_ind
            else:
                self._2DFM.ex_ind = (self._2DFM.ex_ind - self.em_step) % self._2DFM.data.shape[1]
                self.model.ex_ind = self._2DFM.ex_ind

            self._2DFM.update(self.tabs["view"],"ax2","ax1","ax3")
            self._2DFM.update(self.tabs["fit"],"ax1","ax3","ax2")
            self.model.update(self.tabs["fit"],"ax1","ax3","ax4")
            self.update()
            
        elif event.inaxes == self.tabs["view"]["ax1"] and not self.scrollLock or event.inaxes == self.tabs["fit"]["ax3"] and not self.scrollLock:
            if event.button == "up":
                self._2DFM.em_ind = (self._2DFM.em_ind + self.ex_step) % self._2DFM.data.shape[0]
                self.model.em_ind = self._2DFM.em_ind
            else:
                self._2DFM.em_ind = (self._2DFM.em_ind - self.ex_step) % self._2DFM.data.shape[0]
                self.model.em_ind = self._2DFM.em_ind
            
            self._2DFM.update(self.tabs["view"],"ax2","ax1","ax3")
            self._2DFM.update(self.tabs["fit"],"ax1","ax3","ax2")
            self.model.update(self.tabs["fit"],"ax1","ax3","ax4")
            self.update()
    
    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        menu_definitions = (
            'File- Open Data/Ctrl+O/self.on_open_data_clicked,sep, Open Model/Ctrl+M/self.on_open_model_clicked, sep, Exit/Alt+F4/self.on_close_menu_clicked',
            'About- About/F1/self.on_about_menu_clicked'
        )
        self.build_menu(menu_definitions)

    def bind_menu_accelerator_keys(self):
        self.root.bind('<KeyPress-F1>', self.on_about_menu_clicked)
        self.root.bind('<Control-M>', self.on_open_model_clicked)
        self.root.bind('<Control-m>', self.on_open_model_clicked)
        self.root.bind('<Control-O>', self.on_open_data_clicked)
        self.root.bind('<Control-o>', self.on_open_data_clicked)
        

    def on_open_data_clicked(self, event=None):
        #Opening the dataset
        #First we check to see if the cancel button is pressed
        p = tk.filedialog.askopenfilename()
        if p == "":
            pass
        else:
            #currently on opening a new dataset the model is removed
            if self._2DFM.is_loaded:
                #note: should use artist remove for any animated objects I add and remove from the axes
                self._2DFM.em_ind = 0 #now don't need to set these to zero if we want to change this in the future
                self._2DFM.ex_ind = 0
                self._2DFM.clear(self.tabs["fit"],"ax1","ax3","ax2")
                self._2DFM.clear(self.tabs["view"],"ax2","ax1","ax3")
            
            if self.model.is_loaded:
                #Removing the existing model before opening the new model
                self.model.clear(self.tabs["fit"],"ax1","ax3","ax4")
                self.model.is_loaded = False
            path = pathlib.Path(p)
            self._2DFM.open(path)
            
##            #clearing axes on view tab
##            self.tabs["view"]["ax1"].clear()
##            self.tabs["view"]["ax2"].clear()
##            self.tabs["view"]["ax3"].clear()
##
##            #clearing axes on fit tab
##            self.tabs["fit"]["ax1"].clear()
##            self.tabs["fit"]["ax2"].clear()
##            self.tabs["fit"]["ax3"].clear()
##            self.tabs["fit"]["ax4"].clear() #Maybe add this as a choice in the future
##            
            #Plotting to View Tab
            self._2DFM.plot(self.tabs["view"],"ax3",axisLabels=True)
            self._2DFM.indicators(self.tabs["view"],"ax3",animated=True)
            self._2DFM.explot(self.tabs["view"],"ax1")
            self._2DFM.emplot(self.tabs["view"],"ax2",rotate=True,invert_y_ax=True)

            #Plotting to Fit Tab
            self._2DFM.plot(self.tabs["fit"],"ax2",title="Experimental Data")
            self._2DFM.emplot(self.tabs["fit"],"ax1",y_label="Intensity (Ex. {0} nm)".format(self._2DFM.ex_wavelengths[self._2DFM.em_ind]))
            self._2DFM.explot(self.tabs["fit"],"ax3",x_label="Wavelength (nm)",y_label="Intensity (Em. {0} nm)".format(self._2DFM.em_wavelengths[self._2DFM.ex_ind]))
            self._2DFM.indicators(self.tabs["fit"],"ax2",animated=True)
        
        self.tabs["view"]["canvas"].draw()
        self.tabs["fit"]["canvas"].draw()
        self.scrollLock = False
        

    def on_open_model_clicked(self, event=None):
        #This opening statement maybe written as a function in the GUI framework later
        #Might need to review garbage collection routines to improve stability

        p = tk.filedialog.askopenfilename()
        if p == "":
            pass
        else:

            if self.model.is_loaded:
                #Removing the existing model before opening the new model
                self.model.clear(self.tabs["fit"],"ax1","ax3","ax4")
            
            path = pathlib.Path(p)        

            self.model.open(path,"M0.csv")

            #generating model
            self.model.set_ex_em_range(self._2DFM.ex_wavelengths, self._2DFM.em_wavelengths)
            self.xy_mesh = np.meshgrid(self._2DFM.ex_wavelengths, self._2DFM.em_wavelengths)
            self.model.generateModel()
            self.model.generate_Params()
            self.model.eval(self._2DFM.data,self.xy_mesh)
            
            self.model.plot(self.tabs["fit"],"ax4",title="Model Adj-R squared: {0:.2f}".format(self.model.adj_r2))
            self.model.emplot(self.tabs["fit"],"ax1")
            self.model.explot(self.tabs["fit"],"ax3")
            self.model.indicators(self.tabs["fit"],"ax4",animated=True)
            self.tabs["fit"]["canvas"].draw()

    def update_model(self, event=None):
        if self.model.is_loaded:
            self.model.refresh(self._2DFM.data,self.xy_mesh,self.tabs["fit"],"ax1","ax3","ax4")
            self.update()
    
    
    def update_plot(self):
        pass

    def on_close_menu_clicked(self):
        self.root.destroy()

    def on_about_menu_clicked(self, event=None):
        self.create_about_window("Daniel J. Oliver & Carole C. Perry","Interdisciplinary Biomedical Research Centre, \
School of Science and Technology, Nottingham Trent University, Clifton Lane, Nottingham NG11 8NS, United Kingdom.")

        

if __name__ == '__main__':
    root = tk.Tk()
    app = _2DFM_Studio(root)
    root.mainloop()
