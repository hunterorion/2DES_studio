#Add a header to this file when modified
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
from scipy.constants import speed_of_light
    
class Spectrum:
    def __init__(self,data):
        self.data = data
        if data == None:
            self.is_loaded = False
        else:
            self.is_loaded = True
        #SI prefixes tabulated from NIST on 12/01/2021 08:50 GMT https://www.nist.gov/pml/weights-and-measures/metric-si-prefixes
        self.SIprefix = {"yotta":["Y",1E24],"zetta":["Z",1E21],"exa":["E",1E18],
                         "peta":["P",1E15],"tera":["T",1E12],"giga":["G",1E9],
                         "mega":["M",1E6],"kilo":["k",1E3],"hecto":["h",1E2],
                         "deka":["da",1E1],"deci":["d",1E-1],"centi":["c",1E-2],
                         "milli":["m",1E-3],"micro":["",1E-6],"nano":["n",1E-9],
                         "pico":["p",1E-12],"femto":["f",1E-15],"atto":["a",1E-18],
                         "zepto":["z",1E-21],"yocto":["y",1E-24]}
            

    def nm2Hz(self,wavelength,input_si_prefix="nano"):
        wavel = wavelength * self.SIprefix[input_si_prefix][1]
        return speed_of_light/wavel

    def Hz2nm(self,frequency,output_si_prefix="nano"):
        wavel = speed_of_light/frequency
        return wavel / self.SIprefix[output_si_prefix][1]

class _2DFM(Spectrum):
    def __init__(self):
        super().__init__(None)
        self.ex_wavelengths = None
        self.em_wavelengths = None

        ##Positon within 2D spectra
        self.em_ind = 0
        self.ex_ind = 0
        
        ##Plot settings
        self.aa = True  #antialiasing
        self.alpha = 1
        self.facecolour = (0,0,1)
        self.cmap = 'viridis'

    def open(self,file):
        ##Attempting to open file
        try:
            self.data = pd.read_csv(file,header=None)
        except:
            raise Exception("Dataset not found")

        ##Extracting Emission and Excitation Wavelengths
        self.is_loaded = True
        self.ex_wavelengths = self.data.loc[0].values.tolist()
        del self.ex_wavelengths[0]
        self.data.drop(0,0,inplace=True)
        self.em_wavelengths = self.data.iloc[:,0].values.tolist()
        self.data.drop(0,1,inplace=True)
        self.data.reset_index(drop=True,inplace=True)

        self.data.fillna(0,inplace=True) # Removing Nan values
        self.data[self.data<0] = 0 # Removing negative values
    
    def clear(self,tabDict,emPlot_ax,exPlot_ax,cont_ax):
        tabDict["{0}_cb".format(cont_ax)].remove()
        tabDict["blit_manager"].remove_artist(tabDict["{0}_em_ind".format(cont_ax)])
        tabDict["blit_manager"].remove_artist(tabDict["{0}_ex_ind".format(cont_ax)])
        tabDict[cont_ax].clear()
        tabDict[emPlot_ax].clear()
        tabDict[exPlot_ax].clear()
        self.is_loaded=False

    def plot(self,tabDict,ax,axisLabels=False,title=None):
        psm = tabDict[ax].contourf(self.ex_wavelengths,self.em_wavelengths,self.data.astype("float64").values,antialiased=self.aa,alpha=self.alpha,cmap=self.cmap)
        tabDict[ax].set_xlim(230,810)
        tabDict[ax].set_ylim(850,280)
        tabDict[ax].set_facecolor(self.facecolour)
        if axisLabels:
            tabDict[ax].set_xlabel("Excitation Wavelength (nm)")
            tabDict[ax].set_ylabel("Emission Wavelength (nm)")
        tabDict["{0}_orig_loc".format(ax)] = tabDict[ax].get_axes_locator()
        tabDict["{0}_cax".format(ax)] = make_axes_locatable(tabDict[ax]).append_axes("right", size="5%", pad=0.05)
        tabDict["{0}_cb".format(ax)] = tabDict["fig"].colorbar(psm, cax=tabDict["{0}_cax".format(ax)])     
        tabDict["{0}_cb".format(ax)].set_label("Intensity")
        
        if title != None:
            tabDict[ax].set_title(title)

    def emplot(self,tabDict,ax,colour="k",rotate=False,invert_x_ax = False, invert_y_ax = False, x_label = None, y_label = None):
        if rotate:
            tabDict["{0}_rotate".format(ax)] = True
            tabDict["{0}_em_data".format(ax)] =tabDict[ax].plot(self.data.iloc[:,self.em_ind],self.em_wavelengths,color=colour,linewidth=1)
            tabDict[ax].invert_xaxis()
        else:
            tabDict["{0}_rotate".format(ax)] = False
            tabDict["{0}_em_data".format(ax)] = tabDict[ax].plot(self.em_wavelengths,self.data.iloc[:,self.em_ind],color=colour,linewidth=1)
        tabDict[ax].set_title("Emission 1D-Spectral Slice")
        tabDict["{0}_em_data_ylabel".format(ax)] = y_label
        if invert_x_ax:
            tabDict[ax].invert_xaxis()
        if invert_y_ax:
            tabDict[ax].invert_yaxis()
        if x_label != None:
            tabDict[ax].set_xlabel(x_label)
        if y_label != None:
            tabDict[ax].set_ylabel(y_label)
            #Individual plots do not need to be animated as the whole plot area is animated.

    def explot(self,tabDict,ax,colour="r", x_label = None, y_label = None):
        tabDict["{0}_ex_data".format(ax)] = tabDict[ax].plot(self.ex_wavelengths,self.data.iloc[self.ex_ind,:],color=colour,linewidth=1)
        tabDict["{0}_ex_data_ylabel".format(ax)] = y_label
        tabDict[ax].set_title("Excitation 1D-Spectral Slice")
        tabDict["{0}_ex_data_ylabel".format(ax)] = y_label
        if x_label != None:
            tabDict[ax].set_xlabel(x_label)
        if y_label != None:
            tabDict[ax].set_ylabel(y_label)

    def indicators(self,tabDict,ax,em_colour="k",ex_colour="r",animated=False):
        tabDict["{0}_em_ind".format(ax)] = tabDict[ax].axvline(x=self.ex_wavelengths[self.ex_ind],color=em_colour,linewidth=2,linestyle="--",animated=animated,visible=True)
        tabDict["{0}_ex_ind".format(ax)] = tabDict[ax].axhline(y=self.em_wavelengths[self.em_ind],color=ex_colour,linewidth=2,linestyle="--",animated=animated,visible=True)
        if animated:
            tabDict["blit_manager"].add_artist(tabDict["{0}_em_ind".format(ax)])
            tabDict["blit_manager"].add_artist(tabDict["{0}_ex_ind".format(ax)])

    def update(self,tabDict,emPlot_ax,exPlot_ax,cont_ax):
        if type(self.data) != type(None):
            tabDict["{0}_em_ind".format(cont_ax)].set_xdata(self.ex_wavelengths[self.ex_ind])
            tabDict["{0}_ex_ind".format(cont_ax)].set_ydata(self.em_wavelengths[self.em_ind])
            #Updating the plot titled excitation 1D-spectral slice
            tabDict["{0}_ex_data".format(exPlot_ax)][0].set_ydata(self.data.iloc[self.em_ind,:])
            #Updating the plot titled emission 1D-spectral slice
            if tabDict["{0}_rotate".format(emPlot_ax)]:
                tabDict["{0}_em_data".format(emPlot_ax)][0].set_xdata(self.data.iloc[:,self.ex_ind])
            else:
                tabDict["{0}_em_data".format(emPlot_ax)][0].set_ydata(self.data.iloc[:,self.ex_ind])
            #Updating y-labels if present
            if tabDict["{0}_ex_data_ylabel".format(exPlot_ax)] != None:
                tabDict[exPlot_ax].set_ylabel("Intensity (Em. {0} nm)".format(self.em_wavelengths[self.em_ind]))
                #tabDict["{0}_ex_data_ylabel".format(exPlot_ax)].set_text("Intensity (Em. {0} nm)".format(self.em_wavelengths[self.em_ind]))
            if tabDict["{0}_em_data_ylabel".format(emPlot_ax)] != None:
                tabDict[emPlot_ax].set_ylabel("Intensity (Ex. {0} nm)".format(self.ex_wavelengths[self.ex_ind]))
                #tabDict["{0}_em_data_ylabel".format(emPlot_ax)].set_text("Intensity (Ex. {0} nm)".format(self.ex_wavelengths[self.ex_ind]))
            
            tabDict[emPlot_ax].relim()
            tabDict[emPlot_ax].autoscale_view()
            tabDict[exPlot_ax].relim()
            tabDict[exPlot_ax].autoscale_view()
        else:
            pass
        
            
        
        
        
