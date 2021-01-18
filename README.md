# 2DFM Studio
Daniel J. Oliver & Carole C. Perry

Interdisciplinary Biomedical Research Centre, School of Science and Technology, Nottingham Trent University, Clifton Lane, Nottingham NG11 8NS, United Kingdom.

## Introduction
This software was developed to assist fitting 2D-lineshapes to 2D-datasets by allowing the user to see the topology of both the data and the model as well as individual horizontal or vertical 1D-slices to help attain a high quality of fit without having to write a line of code.

## User Guide
This software package can be used without writing a single line of code, just download the repository and run the 2DFM_Studio.py script.

Once the software is open the first thing you will need to do is open up the dataset you want to explore to do this go to File>Open Data or press Ctrl+O this will open up a window prompt where you can select the dataset you would like to open.

<b>NB</b> The datasets used with this software must use the csv file format and have the following layout: first cell is empty, first row excitation wavelengths, first column emission wavelengths and the rest of the cells contain the intensity data.
  
Once opened the data can be explored using either the view or fit tabs, the view tab allows for a large view of the contour plot, while the fit tabs focuses more on the 1D-slices. To move through the 1D-slices in the data hover the mouse over the 1D-plots and scroll the mouse wheel this will move forward and backwards through the available 1D-spectral slices.

To open model files and determine their quality of fit to the open dataset go to File> Open Model or press Ctrl+M this will open up a window prompt where you can select the model you would like to open. However, there are 3 criteria you fulfill:
1. A dataset must be open to view a model
2. The model must be a csv file and have the following format row 1 headings (Amplitude,X-Center (nm),Y-Center (nm),X-Width	Y-Width,lineshape,draw), each following row is a new 2D-lineshape. The software solely supports gaussian lineshapes currently; however, more lineshapes are planned in the future.
3. The M0 matrix must be present in the programs main directory, this file provides infromation on where spectral data has been collected in the experimental data meaning any modelled features outside the collected spectral range are discarded when determining the quality of fit. The M0.csv file provided is for emission spectral data sampled 30 nm away from the excitation wavelength. However, this may need to be modified or replaced if you have a different setup.

Scrolling through the slices are synchronised for both the model and experimental data meaning the user does not need to return to a specific point before opening a new model.

If the user is using this tool to develop a new model or improve the fit of an exisiting model the csv file can be tweaked using software such as microsoft excel or libre office calc, save the changes and push the 'update model' button in the toolbar to reload the model allowing for rapid testing of model parameters.

## Technical Details
This software was developed in Python 3.9.0 and uses the following additional libraries: matplotlib, scipy, pandas, numpy, lmfit. A GUI framework has been written by Daniel J. Oliver based on the framework in Chapter 6 of 'Tkinter GUI Application Development Blueprints' (Bhaskar Chaudhary 1st Edition 2015 Packt Publishing) which was further developed to support matplotlib functionality.   

## Disclaimer
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS, COPYRIGHT OWNERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
