

def getFilePath(windowTitle="Select binary file"):
    from pathlib import Path
    from tkinter import Tk
    from tkinter import filedialog

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    binFullPath = Path(filedialog.askopenfilename(title=windowTitle))
    root.destroy()
    return binFullPath
