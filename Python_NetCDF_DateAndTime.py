"""
Code by Felicia Brisc (CEN University of Hamburg), distributed under a BSD 3-Clause License

A Python filter for ParaView (www.paraview.org). Displays the date and time of NetCDF files in the 3D viewport. 
Version 1.0

*** This version will work only if the cftime package version is less than 1.5.0. ***
*** Starting with cftime version 1.5.0 the utime class was removed.               ***
*** Therefore, this script will give an error at this line:                       ***
*** self.cdftime = utime(time_units.GetValue(0))                                  ***
***                                                                               ***
*** Version 1.1 of this script addresses this issue and is compatible with        ***
*** cftime versions that do or do not include the utime class.                    ***
***                                                                               ***
*** To check the version of cftime you have installed, type in Python:            ***
*** >>> import cftime                                                             ***
*** >>> print(cftime.__version__)                                                 ***

The filter works with ParaView 5.6+ ( it was developed and tested on ParaView 5.8.1) 
and requires the netcdf4-python module https://github.com/Unidata/netcdf4-python

The examples made available by Kitware at the link below have been useful for this filter
https://gitlab.kitware.com/paraview/paraview/blob/master/Examples/Plugins/PythonAlgorithm/PythonAlgorithmExamples.py

"""
__version__ = "1.0"

#if you didn't add netcdf4-python to the system path, add it here
#import sys
#sys.path.append('path_to_your_netcdf4_python_folder')

# VTKPythonAlgorithmBase, the base class for all python-based vtkAlgorithm 
#subclasses in VTK and decorators used to 'register' the algorithm with ParaView 
#along with information about UI.
from paraview.util.vtkAlgorithm import *
from vtkmodules.vtkCommonDataModel import vtkTable
import vtk

from paraview.simple import *
from paraview.numpy_support import *

from datetime import datetime
from cftime import num2date, date2num
from cftime import utime

import ctypes #for the message box 


def createModifiedCallback(anobject):
    import weakref
    weakref_obj = weakref.ref(anobject)
    anobject = None
    def _markmodified(*args, **kwars):
        o = weakref_obj()
        if o is not None:
            o.Modified()
    return _markmodified


#Decorators:
@smproxy.filter( )
@smhint.xml("""
    <ShowInMenu category="Annotation"/>
    <Visibility replace_input="0" />
    <RepresentationType port="0" view="RenderView" type="text" />
    <OutputPort index="0"  name="Output-0"  type="text" />
""")
@smproperty.input(name="Input")
@smdomain.datatype(dataTypes=["vtkDataSet"], composite_data_supported=False)


class NetCDF_DateAndTime(VTKPythonAlgorithmBase):

    def __init__(self):
               
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=1, nOutputPorts=1, outputType="vtkTable")   
        
        self.dateTimeTable = vtk.vtkTable()
        self.displayHoursEnabled = True
        self.displayMinutesEnabled = True
        self.displaySecondsEnabled = True
        self.displayDateEnabled = True
        self.cdftime = None
        
     
    def RequestDataObject(self, request, inInfoVec, outInfoVec):
                
        inData = self.GetInputData(inInfoVec, 0, 0)
        assert inData is not None
        
        inFieldData = inData.GetFieldData()
        time_units = inFieldData.GetAbstractArray(0)
        self.cdftime = utime(time_units.GetValue(0)) 

        return super().RequestDataObject(request, inInfoVec, outInfoVec)
        
    
    def RequestInformation(self, request, inInfoVec, outInfoVec):
        executive = self.GetExecutive()
        outInfo = outInfoVec.GetInformationObject(0)
        return 1
    

    def RequestData(self, request, inInfoVec, outInfoVec):  

        executive = self.GetExecutive()
        #executive.GetInputInformation(0) contains time related fields
        executiveInfo = executive.GetInputInformation(0).GetInformationObject(0)

        if (executiveInfo.Has(executive.UPDATE_TIME_STEP()) ):
            utime = executiveInfo.Get(executive.UPDATE_TIME_STEP())
            current_time = self.cdftime.num2date(utime)
 
        current_time_formatted = ""
        spacer = "   "
        
        #This will display the date in DD/MM/YYYY format. 
        #Modify here the order, for example if you prefer to display MM/DD/YYYY
        if self.displayDateEnabled: 
            current_time_formatted = "%02i/%02i/%02i" % (current_time.day, current_time.month, current_time.year)
        
        if self.displayHoursEnabled:
            if self.displayDateEnabled: 
                current_time_formatted += spacer+"%02i" % current_time.hour
            else:
                current_time_formatted += "%02i" % current_time.hour
        if self.displayMinutesEnabled:
            if self.displayHoursEnabled:
                current_time_formatted += ":%02i" % current_time.minute
            else:
                current_time_formatted += spacer +"%02i" % current_time.minute
        if self.displaySecondsEnabled:
            if self.displayMinutesEnabled: 
                current_time_formatted += ":%02i" % current_time.second
            else:
                ctypes.windll.user32.MessageBoxW(0, "Seconds can be displayed only when minutes are displayed, too. " + "\nPlease check first the 'Display Minutes', then the 'Display Seconds' checkbox!", "Error Alert", 0)
                return 1
            

        self.dateTimeTable.SetNumberOfRows(1)
        col = vtk.vtkStringArray()
        col.SetName("Text")
        col.SetNumberOfComponents(1) #rows
        col.InsertNextValue(str(current_time_formatted))
        self.dateTimeTable.AddColumn(col)   
        
        #text = "%02i/%02i/%02i   %02i:%02i" % (current_time.day, current_time.month, current_time.year, current_time.hour, current_time.minute)
        
        day = current_time.day
        month = "%02i" % (current_time.month)
        year = current_time.year
        hour = current_time.hour
        minute = current_time.minute
        second = "%02i" % (current_time.second)
        
        outData = vtk.vtkTable.GetData(outInfoVec, 0)
        outData.ShallowCopy(self.dateTimeTable)

        return 1
        
 
    #GUI - Properties tab 
    @smproperty.xml("""
       <IntVectorProperty name="DisplayDate"
           number_of_elements="1"
           default_values="1"
           command="DisplayDate">
           <BooleanDomain name="bool"/>
           <Documentation>Check to display date</Documentation>
       </IntVectorProperty>""")
    def DisplayDate(self, x):
        if x == 1:
            self.displayDateEnabled = True
        else:
            self.displayDateEnabled = False
        self.Modified() 
        

    @smproperty.xml("""
       <IntVectorProperty name="DisplayHours"
           number_of_elements="1"
           default_values="1"
           command="DisplayHours">
           <BooleanDomain name="bool"/>
           <Documentation>Check to display hours</Documentation>
       </IntVectorProperty>""")
    def DisplayHours(self, x):
        if x == 1:
            self.displayHoursEnabled = True
        else:
            self.displayHoursEnabled = False
        self.Modified() 
        
        
    @smproperty.xml("""
       <IntVectorProperty name="DisplayMinutes"
           number_of_elements="1"
           default_values="1"
           command="DisplayMinutes">
           <BooleanDomain name="bool"/>
           <Documentation>Check to display minutes</Documentation>
       </IntVectorProperty>""")
    def DisplayMinutes(self, x):
        if x == 1:
            self.displayMinutesEnabled = True
        else:
            self.displayMinutesEnabled = False
        self.Modified() 
        
        
    @smproperty.xml("""
       <IntVectorProperty name="DisplaySeconds"
           number_of_elements="1"
           default_values="0"
           command="DisplaySeconds">
           <BooleanDomain name="bool"/>
           <Documentation>Check to display seconds. Works only when 'Display Minutes' is previously checked. </Documentation>
       </IntVectorProperty>""")
    def DisplaySeconds(self, x):
        if x == 1:
            self.displaySecondsEnabled = True
        else:
            self.displaySecondsEnabled = False
        self.Modified() 
     
