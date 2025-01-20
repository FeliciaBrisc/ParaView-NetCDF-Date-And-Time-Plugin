# ParaView-NetCDF-Date-And-Time-Plugin
A simple user-friendly Python-based ParaView plugin that displays the date and time of NetCDF files in the 3D viewport. 
*** The current version 1.1 fixes the issue caused by the removal of the utime class from the cftime package since version 1.5.0 ***
Works with ParaView 5.6+, requires the netCDF4-python module https://github.com/Unidata/netcdf4-python. 

The netCDF4-python module can be easily be installed via Anaconda: 
conda install -c anaconda netcdf4   ( https://anaconda.org/anaconda/netcdf4 )
A tutorial (PDF) and an example NetCDF file are provided.

First make sure the Python enviroment you have installed matches the Python version of the ParaView version you are using. 

As an example, the configuration I use on a Windows10 PC:
- I created in Anaconda a PYTHON310 environment, with Python 3.10.
- I plan to use ParaView 5.12, which has Python 3.10 embedded.
- Open an Anaconda Prompt, then:
  1. Activate the PYTHON310 environment:
     conda activate PYTHON310
  3. Set the PYTHONHOME variable to point to the this Python 3.10 installation:
     set PYTHONHOME=C:\Users\your_name\anaconda3\envs\PYTHON310
  4. Set the PYTHONPATH variable to point to the lib folder of Python 3.10:
     set PYTHONPATH=C:\Users\your_name\anaconda3\envs\PYTHON310\lib
  5. Launch ParaView 5.12:
     "C:\ParaView-5.12.0\bin\paraview.exe" , then follow the instructions from the INSTRUCTIONS_NetCDF_DateAndTime.pdf file

