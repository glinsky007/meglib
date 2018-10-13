#!/usr/bin/env ipython --pylab -i

### Python script to act as command line invocation of AppRunner as a GUI
###    driven application

from meglib.app_runner import AppRunner

#-------------------------------------------
if __name__ == "__main__":
    p = AppRunner()
    p.edit()