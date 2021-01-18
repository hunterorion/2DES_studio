# A framework to develop tkinter GUIs originally
# Developed by Daniel Oliver BMIRG Nottingham Trent University
# This code is based on the framework in Chapter 6 of 'Tkinter GUI Application Development Blueprints' Bhaskar Chaudhary 1st Edition 2015 Packt Publishing
# subsequently the framework was further developed to support matplotlib functionality.

import tkinter as tk
from tkinter import ttk, font
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Framework():
    """
    GUIFramework is a class that provides a higher level of abstraction for
    the development of Tkinter graphic user interfaces (GUIs).
    Every class that uses this GUI framework must inherit from this class
    and should pass the root window as an arguement to this class by calling
    the super method as follows:
        super().__init__(root)

    Building Menus:
    To build a menu, call build_menu() method with one argument for
    menu_definition, where menu_definition is a tuple where each item is a string
    of the format:
        'Top Level Menu Name - MenuITEMName/Accelerator/Commandcallback/Underlinenumber'.

        MenuSeparator is denoted by a string 'sep'.
    For instance, passing this typle as an arguement to this method

        menu_definition = (
                    'File - &New/Ctrl+N/new_file, &Open/Ctrl+O/openfile, &Save/Ctrl+S/save, Save&As//saveas, sep, Exit/Alt+F4/close', 
                    'Edit - Cut/Ctrl+X/cut, Copy/Ctrl+C/copy, Paste/Ctrl+V/paste, Sep',
                    )
    will generate a File and Edit Menu Buttons with listed menu items for each of the buttons.
    """
    def __init__(self, root, title=None,versionNo=None):
        self.root = root
        if title != None:
            self.root.wm_title(title)
        self.title = title
        self.versionNo = versionNo #Allows for baked in version tracking
        self.bms = []
        self.about_us_wraplength = 350
        self.disclaimer = 'THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. \
IN NO EVENT SHALL THE AUTHORS, COPYRIGHT OWNERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES \
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED \
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF \
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.' #This should be revised in future to auto-update depending on the licence type used

    def build_tab_control(self, tab_definition):
        #Tab control for plots
        tabControl = ttk.Notebook(self.root)
        self.tabs = {}
        for definition in tab_definition:
            frameDict = {}
            name,_type,rowcolwshs,axes = definition.split('-')
            ##Creating Frame
            frameDict["frame"] = ttk.Frame(tabControl)
            tabControl.add(frameDict["frame"], text = name)

            if _type == "p":
                ##Creating Figures
                frameDict["fig"] = plt.figure()
                frameDict["canvas_frame"] = ttk.Frame(frameDict["frame"],width=900,height=900)
                frameDict["canvas_frame"].pack(side="right",expand="yes",fill="both")
                frameDict["canvas"] = FigureCanvasTkAgg(frameDict["fig"],master=frameDict["canvas_frame"])
                frameDict["blit_manager"] = BlitManager(frameDict["canvas"])
                self.bms.append(frameDict["blit_manager"])
                frameDict["canvas"].draw()
                frameDict["canvas"].get_tk_widget().pack(side=tk.RIGHT,expand=tk.YES,fill=tk.BOTH)
            

                ##Creating the gridSpec for the subplots
                row,col,ws,hs = rowcolwshs.split(',')
                row = self.strToInd(row)
                col = self.strToInd(col)
                ws = float(ws)
                hs = float(hs)
                frameDict["grid"] = plt.GridSpec(int(row),int(col),wspace=ws,hspace=hs,figure=frameDict["fig"])
                
                #Creating subplots
                items = map(str.strip, axes.split(','))
                for item in items:
                    self._add_subplot(frameDict, item)
            self.tabs[name] = frameDict
        tabControl.pack(expand=1,fill="both")

    def _add_subplot(self,frameDict, item):
        axis,row,col,animated,eventFunc = item.split('/')
        row = self.strToInd(row)
        col = self.strToInd(col)
        frameDict[axis] = frameDict["fig"].add_subplot(frameDict["grid"][row,col],animated=self.parser(animated))
        if animated == "True":
            frameDict["blit_manager"].add_artist(frameDict[axis])
        if eventFunc != "None":
            if "&" not in eventFunc:
                raise Exception("Invalid eventFunc parameter")
            event,func = eventFunc.split("&")
            frameDict[axis].figure.canvas.mpl_connect(event,eval(func))

    def parser(self,string):
        d = {"True":True,"False":False}
        return d.get(string, string)
    
    def strToInd(self,string):
        if ":" in string:
            ar = string.split(":")
            if len(ar) > 2:
                raise Exception("Improper slice")
            return slice(int(ar[0]),int(ar[1]))
        else:
            return int(string)
    
    ### Creating Menu Elements ###
    def build_menu(self, menu_definitions):
        menu_bar = tk.Menu(self.root)
        for definition in menu_definitions:
            menu = tk.Menu(menu_bar, tearoff = 0)#May want to implement tear off
            top_level_menu, pull_down_menus = definition.split('-')
            menu_items = map(str.strip, pull_down_menus.split(','))
            for item in menu_items:
                self._add_menu_command(menu,item)
            menu_bar.add_cascade(label=top_level_menu, menu=menu)
        self.root.config(menu=menu_bar)

    def _add_menu_command(self, menu, item):
        if item == 'sep':
            menu.add_separator()
        else:
            menu_label, accelerator_key, command_callback = item.split('/')
            try:
                underline = menu_label.index('&')
                menu_label = menu_label.replace('&','',1)
            except ValueError:
                underline = None
            menu.add_command(label=menu_label, underline=underline, accelerator=accelerator_key, command=eval(command_callback))
    
    ### Generating UI elements ###
    def create_about_window(self,developers,developers_address = None):
        #creating popup window
        about = tk.Toplevel(self.root)
        #Displayign software name and version number in first line
        heading = tk.Label(about, text = self.title + " version {0}".format(self.versionNo))
        heading.pack(side="top")
        
        #Displaying author names
        authors = tk.Label(about,text="Developed by {0}".format(developers),wraplength=self.about_us_wraplength)
        authors.pack(side="top")

        if developers_address != None:
            author_address = tk.Label(about,text=developers_address,wraplength=self.about_us_wraplength)
            author_address.pack(side = "top")
        
        #Creating Disclaimer heading
        disclaimer_heading = tk.Label(about,text="DISCLAIMER",pady=10)
        disclaimer_heading.pack(side="top")
        #Underlining Disclaimer heading
        f = font.Font(disclaimer_heading, disclaimer_heading.cget("font"))
        f.configure(underline=True)
        disclaimer_heading.configure(font=f)

        disclaimer = tk.Label(about,text=self.disclaimer,anchor="e",wraplength=self.about_us_wraplength,justify="left")
        disclaimer.pack(side="top")
        button = ttk.Button(about,text='Close',command=about.destroy)
        button.pack(side="top")
    
    def create_gui(self):
        self.create_menu() # this needs addressing as this function is not present here
        self.create_top_bar()

    def create_top_bar(self):
        self.top_bar = ttk.Frame(self.root, height=25, relief="raised")
        self.top_bar.pack(fill="x", side="top",pady=2)

    def create_tool_bar(self):
        self.tool_bar = ttk.Frame(self.root, relief="raised", width=50)
        self.tool_bar.pack(fill="y",side="left",pady=3)

    def create_bottom_bar(self):
        self.right_bar = ttk.Frame(self.root, relief="raised", height=25)
        self.right_bar.pack(fill="y",side="bottom",pady=2)
        
##    def add_plot(self,parent):
##        fig = plt.figure()
##        canvas_frame = ttk.Frame(parent,width=900,height=900)
##        canvas_frame.pack(side="right",expand="yes",fill="both")
##        canvas = FigureCanvasTkAgg(fig,master=canvas_frame)
##        canvas.draw()
##        canvas.get_tk_widget().pack(side=tk.RIGHT,expand=tk.YES,fill=tk.BOTH)
##        return fig, canvas_frame, canvas

    def update(self):
        for bm in self.bms:
            bm.update()

class BlitManager:
    #This was copied from the matplotlibs tutorial page
    def __init__(self, canvas, animated_artists=()):
        """
        Parameters
        ----------
        canvas : FigureCanvasAgg
            The canvas to work with, this only works for sub-classes of the Agg
            canvas which have the `~FigureCanvasAgg.copy_from_bbox` and
            `~FigureCanvasAgg.restore_region` methods.

        animated_artists : Iterable[Artist]
            List of the artists to manage
        """
        self.canvas = canvas
        self._bg = None
        self._artists = []

        for a in animated_artists:
            self.add_artist(a)
        # grab the background on every draw
        self.cid = canvas.mpl_connect("draw_event", self.on_draw)

    def on_draw(self, event):
        """Callback to register with 'draw_event'."""
        cv = self.canvas
        if event is not None:
            if event.canvas != cv:
                raise RuntimeError
        self._bg = cv.copy_from_bbox(cv.figure.bbox)
        self._draw_animated()

    def add_artist(self, art):
        """
        Add an artist to be managed.

        Parameters
        ----------
        art : Artist

            The artist to be added.  Will be set to 'animated' (just
            to be safe).  *art* must be in the figure associated with
            the canvas this class is managing.

        """
        if art.figure != self.canvas.figure:
            raise RuntimeError
        art.set_animated(True)
        self._artists.append(art)

    def remove_artist(self,art):
        if art.figure != self.canvas.figure:
            raise RuntimeError
        if art in self._artists:
            self._artists.remove(art)
        else:
            raise RuntimeError
        

    def _draw_animated(self):
        """Draw all of the animated artists."""
        fig = self.canvas.figure
        for a in self._artists:
            fig.draw_artist(a)

    def update(self):
        """Update the screen with animated artists."""
        cv = self.canvas
        fig = cv.figure
        # paranoia in case we missed the draw event,
        if self._bg is None:
            self.on_draw(None)
        else:
            # restore the background
            cv.restore_region(self._bg)
            # draw all of the animated artists
            self._draw_animated()
            # update the GUI state
            cv.blit(fig.bbox)
            ##cv.blit(fig.clipbox)
        # let the GUI event loop process anything it has to do
        cv.flush_events()
        
class TestThisFramework(Framework):

    def new_file(self):
        print('new tested OK')

    def open_file(self):
        print('open tested OK')

    def undo(self):
        print ('undo tested OK')

    def options(self):
        print ('options tested OK')

    def about(self):
        print ('about tested OK')

if __name__ == '__main__':

    root = tk.Tk()
    menu_items = (
        'File- &New/Ctrl+N/self.new_file, &Open/Ctrl+O/self.open_file',
        'Edit- Undo/Ctrl+Z/self.undo, sep, Options/Ctrl+T/self.options',
        'About- About//self.about'
    )
    app = TestThisFramework(root)
    app.build_menu(menu_items)
    root.mainloop()
    
