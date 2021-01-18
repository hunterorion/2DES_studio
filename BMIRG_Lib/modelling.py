#Add
import lmfit
import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable

class Modelling:
    def __init__(self):
        self.file = None
        self.model_init = None
        self.is_loaded = False
        self.em_wavelengths = None
        self.ex_wavelengths = None
        self.model_init = None
        self.lmfit_model=None
        self.M0 = None
        self.data=None
        self.params = None
        self.adj_r2 = None
        self.eval_res = None
        self.em_ind = 0
        self.ex_ind = 0
        self.aa = True  #antialiasing
        self.ex_wavelengths = None
        self.em_wavelengths = None
        self.alpha = 1
        self.facecolour = (0,0,1)
        self.cmap = 'viridis'

    def clear(self,tabDict,emPlot_ax,exPlot_ax,cont_ax):
        #Removing the colour bar from contour plot then clearing the axis
        tabDict["{0}_cb".format(cont_ax)].remove()
        tabDict["blit_manager"].remove_artist(tabDict["{0}_em_ind".format(cont_ax)])
        tabDict["blit_manager"].remove_artist(tabDict["{0}_ex_ind".format(cont_ax)])
        tabDict[cont_ax].clear()
        tabDict["{0}_em_model".format(emPlot_ax)][0].remove()
        tabDict["{0}_ex_model".format(exPlot_ax)][0].remove()
    
    def open(self,file,mask):
        try:
            self.file = file
            self.model_init = pd.read_csv(file)
            self.is_loaded = True
            self.M0 = pd.read_csv(mask,header=None)
        except:
            raise Exception("Model or Mask not found")

    def generateModel(self):
        for i in range(0,self.model_init.shape[0]):
            if self.model_init.iloc[i,6] == "yes":
                first_lineshape = i
                if self.model_init.iloc[i,5] == "gaussian":
                    self.lmfit_model = lmfit.Model(self.amp_gaussian_2d,prefix="ls{0}_".format(i+1),independent_vars=["xy_mesh","mask"])
                else:
                    raise Exception("Unsupported Lineshape, defaulting to Gaussian")
                    self.lmfit_model = lmfit.Model(self.amp_gaussian_2d,prefix="ls{0}_".format(i+1),independent_vars=["xy_mesh","mask"])
                break
        if self.model_init.shape[0] > 1:
            for i in range(first_lineshape+1,self.model_init.shape[0]):
                if self.model_init.iloc[i,6] == "yes":
                    if self.model_init.iloc[i,5] == "gaussian":
                        self.lmfit_model += lmfit.Model(self.amp_gaussian_2d,prefix="ls{0}_".format(i+1),independent_vars=["xy_mesh","mask"])
                    else:
                        raise Exception("Unsupported Lineshape, defaulting to Gaussian")
                        self.lmfit_model += lmfit.Model(self.amp_gaussian_2d,prefix="ls{0}_".format(i+1),independent_vars=["xy_mesh","mask"])
        self.lmfit_model

    def amp_gaussian_2d(self,xy_mesh,mask,amp,xc,yc,xwidth,ywidth)-> np.ndarray:
        """A two dimensional gaussian distribution.
            =amp*np.exp(-((x-xc)**2/(2*sigma_x**2)+(y-yc)**2/(2*sigma_y**2)))/(2*np.pi*sigma_x*sigma_y)
        """
        (x,y) = xy_mesh
        gauss = amp*np.exp(-((x-xc)**2/(2*xwidth**2)+(y-yc)**2/(2*ywidth**2)))/(2*np.pi*xwidth*ywidth)
        gauss*=mask
        return np.ravel(gauss)

    def set_ex_em_range(self,ex_wav,em_wav):
        self.ex_wavelengths = ex_wav
        self.em_wavelengths = em_wav

    def eval(self,data,xy_mesh):
        self.eval_res = self.lmfit_model.fit(np.ravel(data),self.params,xy_mesh=xy_mesh,mask=self.M0)
        self.adj_r2 = self.adj_rsquared()

    def generate_Params(self):
        self.params = lmfit.Parameters()
        for i in range(0,self.model_init.shape[0]):
            if self.model_init.iloc[i,6] == "yes":
                self.params.add("ls{0}_amp".format(i+1),value = self.model_init.iloc[i,0],vary=False)
                self.params.add("ls{0}_xc".format(i+1),value = self.model_init.iloc[i,1],vary=False)
                self.params.add("ls{0}_yc".format(i+1),value = self.model_init.iloc[i,2],vary=False)
                self.params.add("ls{0}_xwidth".format(i+1),value = self.model_init.iloc[i,3],vary=False)
                self.params.add("ls{0}_ywidth".format(i+1),value = self.model_init.iloc[i,4],vary=False)

    def adj_rsquared(self):
        k = 0
        for i in self.eval_res.params:
            if self.eval_res.params[i].vary == True:
                k+=1
        return 1-(1-self.rsquared())*((len(self.eval_res.data)-1)/(len(self.eval_res.data)-(k+1)))

    def rsquared(self):
        return 1-self.eval_res.residual.var()/np.var(self.eval_res.data)

    def plot(self,tabDict,ax,axisLabels=False,title=None):
        self.data = self.eval_res.best_fit.reshape(np.outer(self.em_wavelengths,self.ex_wavelengths).shape)
        psm = tabDict[ax].contourf(self.ex_wavelengths,self.em_wavelengths,self.data.astype("float64"),antialiased=self.aa,alpha=self.alpha,cmap=self.cmap)
        tabDict[ax].set_xlim(230,810)
        tabDict[ax].set_ylim(850,280)
        tabDict[ax].set_facecolor(self.facecolour)
        if axisLabels:
            tabDict[ax].set_xlabel("Excitation Wavelength (nm)")
            tabDict[ax].set_ylabel("Emission Wavelength (nm)")
        tabDict["{0}_orig_loc".format(ax)] = tabDict[ax].get_axes_locator()
        tabDict["{0}_cax".format(ax)] = make_axes_locatable(tabDict[ax]).append_axes("right", size="5%", pad=0.05)
        tabDict["{0}_cb".format(ax)] = tabDict["fig"].colorbar(psm, cax=tabDict["{0}_cax".format(ax)])     
        tabDict["{0}_cb".format(ax)].set_label("Fluoresence")
        
        if title != None:
            tabDict[ax].set_title(title)
    
    def emplot(self,tabDict,ax,colour="steelblue",rotate=False,invert_x_ax = False, invert_y_ax = False, x_label = None, y_label = None):
        if rotate:
            tabDict["{0}_rotate".format(ax)] = True
            tabDict["{0}_em_model".format(ax)] =tabDict[ax].plot(self.data[:,self.ex_ind],self.em_wavelengths,color=colour,linewidth=1)
            tabDict[ax].invert_xaxis()
        else:
            tabDict["{0}_rotate".format(ax)] = False
            tabDict["{0}_em_model".format(ax)] = tabDict[ax].plot(self.em_wavelengths,self.data[:,self.ex_ind],color=colour,linewidth=1)
        tabDict["{0}_em_model_ylabel".format(ax)] = y_label
        if invert_x_ax:
            tabDict[ax].invert_xaxis()
        if invert_y_ax:
            tabDict[ax].invert_yaxis()
        if x_label != None:
            tabDict[ax].set_xlabel(x_label)
        if y_label != None:
            tabDict[ax].set_ylabel(y_label)
        

    def explot(self,tabDict,ax,colour="steelblue", x_label = None, y_label = None):
        tabDict["{0}_ex_model".format(ax)] = tabDict[ax].plot(self.ex_wavelengths,self.data[self.em_ind,:],color=colour,linewidth=1)
        tabDict["{0}_ex_model_ylabel".format(ax)] = y_label
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

    def refresh(self,data,xy_mesh,tabDict,emPlot_ax,exPlot_ax,cont_ax):
        #Regenerating the updated model
        self.open(self.file,"M0.csv")
        self.generateModel()
        self.generate_Params()
        self.eval(data,xy_mesh)

        #Removing colourbar and clearing contour plot
        tabDict["{0}_cb".format(cont_ax)].remove()
        tabDict[cont_ax].clear()

        #replotting contour plot
        self.plot(tabDict,cont_ax,title="Model Adj-R squared: {0:.2f}".format(self.adj_r2))
        self.indicators(tabDict,cont_ax,animated=True)

        #updating 1D-slices
        tabDict["{0}_ex_model".format(exPlot_ax)][0].set_ydata(self.data[self.em_ind,:])
        if tabDict["{0}_rotate".format(emPlot_ax)]:
            tabDict["{0}_em_model".format(emPlot_ax)][0].set_xdata(self.data[:,self.ex_ind])
        else:
            tabDict["{0}_em_model".format(emPlot_ax)][0].set_ydata(self.data[:,self.ex_ind])
        
        
    
    def update(self,tabDict,emPlot_ax,exPlot_ax,cont_ax):
        if type(self.data) != type(None):
            tabDict["{0}_em_ind".format(cont_ax)].set_xdata(self.ex_wavelengths[self.ex_ind])
            tabDict["{0}_ex_ind".format(cont_ax)].set_ydata(self.em_wavelengths[self.em_ind])
            tabDict["{0}_ex_model".format(exPlot_ax)][0].set_ydata(self.data[self.em_ind,:])
            if tabDict["{0}_rotate".format(emPlot_ax)]:
                tabDict["{0}_em_model".format(emPlot_ax)][0].set_xdata(self.data[:,self.ex_ind])
            else:
                tabDict["{0}_em_model".format(emPlot_ax)][0].set_ydata(self.data[:,self.ex_ind])
            if tabDict["{0}_ex_model_ylabel".format(exPlot_ax)] != None:
                tabDict[exPlot_ax].set_ylabel("Intensity (Em. {0} nm)".format(self.em_wavelengths[self.ex_ind]))
            if tabDict["{0}_em_model_ylabel".format(emPlot_ax)] != None:
                tabDict[emPlot_ax].set_ylabel("Intensity (Ex. {0} nm)".format(self.ex_wavelengths[self.em_ind]))
                
            tabDict[emPlot_ax].relim()
            tabDict[emPlot_ax].autoscale_view()
            tabDict[exPlot_ax].relim()
            tabDict[exPlot_ax].autoscale_view()
        else:
            pass
    

    
