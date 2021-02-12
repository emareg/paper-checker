"""Make a gui from a command line interface."""
import argparse
import tkinter as tk
from tkinter import ttk
from collections import OrderedDict
from tkinter import filedialog

"""Wrap stdout so that print calls can go to an io.StringIO object."""
import sys
import io

_stdout = sys.stdout


FILETYPES = (
    ("PDFs", "*.pdf"),
    ("Text", "*.txt"),
    ("LaTeX", "*.tex"),
    ("Markdown", "*.md"),
    ("HTML", "*.html"),
)

g_gui = None
g_infileentry = None


class Wrapper(io.StringIO):
    """Wrap stdout, so that print calls can go to a buffer."""

    def __init__(self, onwrite=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.onwrite = onwrite
        sys.stdout = self

    def write(self, *args, **kwargs):
        if self.onwrite:
            self.onwrite(*args, **kwargs)
        _stdout.write(*args, **kwargs)
        io.StringIO.write(self, *args, **kwargs)

    def __del__(self):
        """Put sys.stdout back in the right place."""
        sys.stdout = _stdout


class Frame(tk.Frame):
    """A Frame with some cool defaults. (that can be overwridden)"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        fill = kwargs.get("fill", tk.BOTH)
        expand = kwargs.get("expand", True)
        pady = kwargs.get("pady", 3)
        self.parent = parent
        self.pack(fill=fill, expand=expand, pady=pady)


class Widget(object):
    """A bridge between the GUI and the command line argument."""

    # The entry for a thing.
    ENTRY_WIDTH = 30

    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :param tk.Frame parent:
        :return:
        """

        self.action = action
        self.frame = tk.Frame(parent)
        self.frame.pack(fill=tk.X, expand=True, side=tk.TOP)
        self.__class__ = _widgetmap[type(action)]

    def _dolabel(self):
        text = self.action.dest + ("*:" if self.action.required else ":")
        self._label = tk.Label(self.frame, text=text, anchor=tk.E, width=10)
        self._label.pack(side=tk.LEFT)

    def _dohelp(self):
        self._help = tk.Label(self.frame, text=self.action.help, anchor=tk.W, width=30)
        self._help.pack(side=tk.LEFT)


class _AppendWidget(Widget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)
        raise NotImplementedError("{} has not been implemented.".format(self.__class__))

    def getval(self):
        pass


class _AppendConstWidget(Widget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)
        raise NotImplementedError("{} has not been implemented.".format(self.__class__))

    def getval(self):
        pass


class _CountWidget(Widget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)
        raise NotImplementedError("{} has not been implemented.".format(self.__class__))

    def getval(self):
        pass


class _HelpWidget(Widget):
    def __init__(self, action, parent):

        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)

    def getval(self):
        pass


def askOpenFile(entry):
    global g_infileentry
    file = filedialog.askopenfilename(title="Select Paper/Article", filetypes=FILETYPES)
    # g_infileentry.delete(0, tk.END)
    # g_infileentry.insert(0, str(file))
    g_infileentry.insert(tk.END, str(file) + ",")
    print(
        "Added:  '{}'\nOutput: '{}'".format(
            file, "".join(file.split(".")[:-1]) + "_papercheck.html"
        )
    )


class _StoreWidget(Widget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)
        self._dolabel()
        if action.choices:
            self._entry = ttk.Combobox(self.frame, state="readonly")
            self._entry["values"] = action.choices
            self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if action.default and action.default in action.choices:
                self._entry.current(action.choices.index(action.default))

        else:
            self._entry = tk.Entry(self.frame)
            self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            # PayperChecker Injection
            if action.dest == "files":
                global g_infileentry
                g_infileentry = self._entry
                self._entry.bind("<1>", askOpenFile)
            if action.default:
                self._entry.insert(0, str(action.default))
        self._dohelp()

    def getval(self):
        textval = self._entry.get()
        if self.action.type:
            return self.action.type(textval)
        else:
            if self.action.dest == "files":
                return textval.split(",")[:-1]
            return textval


class _StoreConstWidget(Widget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)
        raise NotImplementedError("{} has not been implemented.".format(self.__class__))

    def getval(self):
        pass


class _StoreBoolWidget(Widget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)
        self._dolabel()
        default = 1 if action.default else 0
        self.state = tk.IntVar(value=default)
        self.cb = tk.Checkbutton(self.frame, anchor=tk.W, variable=self.state)
        self.cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._dohelp()

    def getval(self):
        return self.state.get()


class _StoreTrueWidget(_StoreBoolWidget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)


class _StoreFalseWidget(_StoreBoolWidget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)
        self.cb.select()

    def getval(self):
        pass


_widgetmap = {
    argparse._StoreAction: _StoreWidget,
    argparse._AppendAction: _AppendWidget,
    argparse._AppendConstAction: _AppendConstWidget,
    argparse._CountAction: _CountWidget,
    argparse._HelpAction: _HelpWidget,
    argparse._StoreConstAction: _StoreConstWidget,
    argparse._StoreFalseAction: _StoreFalseWidget,
    argparse._StoreTrueAction: _StoreTrueWidget,
}


class CliGui(object):
    """Turn a command line script into a GUI.  It's pretty ugly, but effective."""

    def __init__(self, parser, onrun, show=True):
        """
        :param argparse.ArgumentParser parser: parser to turn into a gui

        :param callable onrun: callable to run when the run button is pressed.
          The callable must take an argparse.Namespace as its only argument.
        :param bool show: Whether to show the GUI by default.  The only use case
          for this to be False is for testing.
        """
        self.parser = parser
        self.onrun = onrun
        self.widgets = OrderedDict()
        self.make_gui()
        self.stdout = Wrapper(self.onwrite)
        if show:
            self.show()

    def make_gui(self):
        global g_gui
        self.root = tk.Tk()
        self.root.title("PaperCheck")
        g_gui = self
        self.frame = Frame(self.root)
        self.groupframes = []
        for group in self.parser._action_groups:
            frame = Frame(self.frame, borderwidth=10)
            self.groupframes.append(frame)
            group_label = tk.Label(frame, text=group.title)
            group_label.pack(fill=tk.X)
            for action in group._group_actions:
                self.widgets[action] = self.add_action(action, frame)

        # add run and cancel buttons.
        buttonframes = tk.Frame(self.frame)
        self.run = tk.Button(buttonframes, text="Run", command=self.parse_args)
        self.cancel = tk.Button(buttonframes, text="Cancel", command=self.quit)
        self.run.pack(side=tk.LEFT)
        self.cancel.pack(side=tk.LEFT)
        buttonframes.pack()

        # add stdout wrapper
        self.stdoutframe = Frame(self.frame)

        self.entry = tk.Text(self.stdoutframe)
        self.entry.configure(state="disabled")
        self.entry.pack(fill=tk.BOTH)

    def onwrite(self, text):
        self.entry.configure(state="normal")
        self.entry.insert(tk.END, text)
        self.entry.configure(state="disabled")

    def parse_args(self):
        ns = argparse.Namespace()
        for action, widget in self.widgets.items():
            if isinstance(widget, _HelpWidget):
                continue
            val = widget.getval()
            setattr(ns, widget.action.dest, val)

        if self.onrun:
            self.onrun(ns)
            print("-" * 25)
            print()
        return ns

    def quit(self):
        self.frame.parent.quit()

    def show(self):
        self.root.geometry("600x600+300+300")
        self.root.mainloop()

    def add_action(self, action, frame):
        """
        :param argparse.Action action:
        :return: None
        """
        widget = _widgetmap[type(action)](action, frame)
        return widget
