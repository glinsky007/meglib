#!/usr/bin/env ipython --pylab -i

### Python script to act as command line invocation of DemoApp as a GUI
###    driven application


from meglib.app_runner import DemoApp

#-------------------------------------------
if __name__ == "__main__":
    p = DemoApp()
    p.edit()