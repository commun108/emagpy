# EMagPy

Python API for inversion/modelling of frequency domain electromagnetic data (FDEM).

EMagPy is divided into a python API and a standalone graphical user interface (GUI).
It aims to be a powerfull but simple tool for inverting EMI data obtain from conductimeter.
EMagPy document can be viewed at https://hkex.gitlab.io/emagpy.

# Graphical User Interface (GUI)
<img src='src/image/gui.gif' width="600">


# Getting started
Clone the repository:
```sh
git clone https://gitlab.com/hkex/emagpy
```
Change to the `src` directory and run `ui.py` to start the GUI.
```sh
cd emgapy/src
python ui.py # this will start the GUI
```
The python API is available by simply importing the `emagpy` module from the python shell:
```python
import emagpy
k = Problem()
k.createSurvey('./test/coverCrop.csv')
k.invert(forwardModel='CS') # specify the forward model (here the Cumulative Sensitivty of McNeil1980)
k.showResults() # display the section
k.showMisfit() # display predicted and observed apparent EC
k.showOne2one() # 1:1 line of misfit of apparent EC
```

For more example, check out the [jupyter-notebook](jupyter notebooks).


Downloads
---------
as a self-extractable executable:

[![win](https://img.shields.io/badge/Windows%2064bit-EMagPy%20v1.1.0-blue.svg?style=flat&logo=Microsoft&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.1.0/EMagPy-windows.exe)
[![mac](https://img.shields.io/badge/macOS%2064bit-EMagPy%20v1.1.0-lightgrey.svg?style=flat&logo=Apple&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.1.0/EMagPy-macos.dmg)
[![linux](https://img.shields.io/badge/Linux%2064bit-EMagPy%20v1.1.0-orange.svg?style=flat&logo=Linux&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.1.0/EMagPy-linux)

as a zip file:

[![win](https://img.shields.io/badge/Windows%2064bit-EMagPy%20v1.1.0-blue.svg?style=flat&logo=Microsoft&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.1.0/EMagPy-windows.zip)
[![mac](https://img.shields.io/badge/macOS%2064bit-EMagPy%20v1.1.0-lightgrey.svg?style=flat&logo=Apple&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.1.0/EMagPy-macos.zip)
[![linux](https://img.shields.io/badge/Linux%2064bit-EMagPy%20v1.1.0-orange.svg?style=flat&logo=Linux&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.1.0/EMagPy-linux.zip)


Older versions
--------------
v 1.0.0

[![win](https://img.shields.io/badge/Windows%2064bit-EMagPy%20v1.0.0-blue.svg?style=flat&logo=Microsoft&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.0.0/EMagPy-windows.exe)
[![mac](https://img.shields.io/badge/macOS%2064bit-EMagPy%20v1.0.0-lightgrey.svg?style=flat&logo=Apple&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.0.0/EMagPy-macos.dmg)
[![linux](https://img.shields.io/badge/Linux%2064bit-EMagPy%20v1.0.0-orange.svg?style=flat&logo=Linux&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.0.0/EMagPy-linux)

[![win](https://img.shields.io/badge/Windows%2064bit-EMagPy%20v1.0.0-blue.svg?style=flat&logo=Microsoft&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.0.0/EMagPy-windows.zip)
[![mac](https://img.shields.io/badge/macOS%2064bit-EMagPy%20v1.0.0-lightgrey.svg?style=flat&logo=Apple&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.0.0/EMagPy-macos.app.zip)
[![linux](https://img.shields.io/badge/Linux%2064bit-EMagPy%20v1.0.0-orange.svg?style=flat&logo=Linux&logoColor=white)](https://github.com/hkexgroup/emagpy/releases/download/v1.0.0/EMagPy-linux.zip)



[![coverage report](https://gitlab.com/hkex/emagpy/badges/master/coverage.svg)](https://gitlab.com/hkex/emagpy/-/commits/master)
