import tkinter as tk
from tkinter import filedialog

root = None


FILETYPES = (
    ("PDFs", "*.pdf"),
    ("Text", "*.txt"),
    ("LaTeX", "*.tex"),
    ("Markdown", "*.md"),
    ("HTML", "*.html"),
)


def getRoot():
    global root
    if not root:
        createWindow()
    return root


def createWindow():
    global root
    root = tk.Tk()
    root.title("PaperCheck")

    argG = tk.IntVar()
    argY = tk.IntVar()
    argS = tk.IntVar()

    tk.Label(root, text="Select Checks:").grid(row=0, sticky=tk.W)
    cG = tk.Checkbutton(root, text="Grammar Checks", variable=argG).grid(
        row=1, sticky=tk.W
    )
    cY = tk.Checkbutton(root, text="Style Checks", variable=argY).grid(
        row=2, sticky=tk.W
    )
    cS = tk.Checkbutton(root, text="Spell Checks", variable=argS).grid(
        row=3, sticky=tk.W
    )

    b = tk.Button(root, text="Save Report", command=askSaveReport).grid(
        row=4, sticky=tk.W, pady=4
    )
    root.geometry("400x200+120+120")
    return root


def askOpenFile():
    return filedialog.askopenfilename(title="Select Paper/Article", filetypes=FILETYPES)


def askSaveReport():
    global root
    outfile = filedialog.asksaveasfilename(
        title="Save Report", filetypes=(("HTML", "*.html"),)
    )
    root.destroy()


def runGUI():
    global root
    createWindow()
    askOpenFile()

    root.mainloop()


# window.withdraw()
runGUI()
