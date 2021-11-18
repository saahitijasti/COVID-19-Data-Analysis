# Saahiti Jasti
# Lab 3
# lab3front.py reads from the Covid19 SQL database to display data to the user

import sqlite3
import matplotlib
matplotlib.use('TkAgg')
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class MainWin(tk.Tk):
    def __init__(self):
        """
        Constructor for the main window. 
        Sets up connection to Covid19 SQL Database
        Sets up the window with size, title, and delete window protocol.
        Configures Label and Button widgets.
        Queries data for main labels.
        """        
        super().__init__()
        self.conn = sqlite3.connect('covid19.db')
        self.cur = self.conn.cursor()
        
        self.minsize(200, 50)
        self.title("Covid-19 Cases")
        self.protocol("WM_DELETE_WINDOW", self.exitProgram)
        
        self.cur.execute("SELECT * FROM Covid19 "\
                         "WHERE CountryNumber!=0")
        numCountries = len(self.cur.fetchall())
        tk.Label(self, text="Worldwide: " + str(numCountries) +\
                 " countries").grid(row=0, column=0, sticky='w')
        
        self.cur.execute("SELECT CasesPer1M FROM Covid19 WHERE Country='World'")
        worldwideCases = self.cur.fetchone()
        tk.Label(self, text="Worldwide: " + str(*worldwideCases) + \
                 " cases per 1M people").grid(row=1, column=0, sticky='w')  
        
        self.cur.execute("SELECT DeathsPer1M FROM Covid19 WHERE Country='World'")
        worldwideCases = self.cur.fetchone()
        tk.Label(self, text="Worldwide: " + str(*worldwideCases) + \
                 " deaths per 1M people").grid(row=2, column=0, sticky='w')
        
        F = tk.Frame(self)
        B1 = tk.Button(F, text="New Cases", command=self.displayNewCases)
        B1.grid(row=0, column=0, padx=5, pady=5)
        B2 = tk.Button(F, text="Top 20 Cases", command=self.displayTop20)
        B2.grid(row=0, column=1, padx=5, pady=5) 
        B3 = tk.Button(F, text="Compare Countries", command=self.compareCountries)
        B3.grid(row=0, column=2, padx=5, pady=5) 
        F.grid(row=3, column=0, columnspan=3)
        
    def displayNewCases(self):
        """
        Queries data from database for New Cases display window.
        Creates a new instance of a display window to display new cases and new deaths for current day.
        """        
        self.cur.execute("SELECT Country, NewCases, NewDeaths " \
                         "FROM Covid19 " \
                         "WHERE Country!='World' AND CountryNumber IS NOT NULL " \
                         "ORDER BY NewCases DESC")
        newCases = self.cur.fetchall()
        self.cur.execute("SELECT Country, NewCases " \
                         "FROM Covid19 " \
                         "WHERE Country!='World' AND CountryNumber IS NULL " \
                         "ORDER BY NewCases DESC")
        highestContinent = self.cur.fetchone()
        dWin = DisplayWin(self, newCases, 10, highestContinent)
        dWin.newCases()
        
    def displayTop20(self):
        """
        Queries data from database for Top 20 Cases display window.
        Creates a new instance of a display window to display 20 countries with the highest number of cases.
        """            
        self.cur.execute("SELECT Country, CasesPer1M, DeathsPer1M, TestsPer1M " \
                         "FROM Covid19 " \
                         "WHERE Country!='World' AND CountryNumber IS NOT NULL " \
                         "ORDER BY CasesPer1M DESC " \
                         "LIMIT 20")
        top20 = self.cur.fetchall() 
        dWin = DisplayWin(self, top20, 20)
        dWin.top20()
        
    def compareCountries(self):
        """
        Queries data from database for Compare Countries display window.
        Creates a new instance of a dialog window for the user to select countries and plots the
        new cases for each country chosen.
        """              
        self.cur.execute("SELECT Country, CasesPer1M " \
                         "FROM Covid19 " \
                         "WHERE Country!='World' AND CountryNumber IS NOT NULL " \
                         "ORDER BY Country ASC") 
        self._countries = self.cur.fetchall()
        dWin = DialogWin(self, self._countries)
        self.wait_window(dWin)
        choices = dWin.getChoices()
        if choices:
            PlotWin(self,self._countries, choices) 
       
    def exitProgram(self):
        """
        Closes the main window, closes the connection to the database, and ends the program.
        """
        self.conn.commit()
        self.conn.close()
        self.destroy
        self.quit()    
        
class DisplayWin(tk.Toplevel):      
    def __init__(self, master, lines, numLines, highestContinent=None):
        """
        Constructor for display window.
        
        Args:
        master: The master of this Toplevel window.
        lines: A tuple with elements the listboxes will display.
        numLines: The height of the listboxes.
        highestContinent(optional): The continent with the highest new cases that the
        New Cases window will display.
        """        
        super().__init__(master)
        self.grab_set() 
        self.focus_set()           
        self.lines = lines 
        self.numLines = numLines
        self.highestContinent = highestContinent
        
    def newCases(self):
        """
        Creates a new instance of a MultiListbox to display the new cases and new deaths of all countries.
        """         
        self.title("New Cases")
        mlb = MultiListbox(self, (('Country', 30), ('New Cases', 10), ('New Deaths', 10)), self.numLines, True)
        for i in range(len(self.lines)):
            country, newCases, newDeaths = self.lines[i]
            mlb.insert(tk.END, (country, newCases, newDeaths))
        mlb.grid(sticky='nsew')        
        L = tk.Label(self, bg='light gray', text="Highest: " + str(self.highestContinent[1]) + " new cases in " + \
                 str(self.highestContinent[0])).grid(sticky='we')
        
    def top20(self):
        """
        Creates a new instance of a MultiListbox to display the 20 countries with the highest number of cases.
        """           
        self.title("Top 20 Cases")
        mlb = MultiListbox(self, (('Country', 30), ('Cases/1M', 10), ('Deaths/1M', 10),\
                                  ('Tests/1M', 10)), self.numLines, False)
        for i in range(len(self.lines)):
            country, cases, deaths, tests = self.lines[i]
            mlb.insert(tk.END, (country, cases, deaths, tests))
        mlb.grid(sticky='nsew')                
              
class DialogWin(tk.Toplevel):
    def __init__(self, master, countries):
        """
        Constructor for dialog window.
        
        Args:
        master: The master of this Toplevel window.
        countries: The alphabetized tuple of countries.
        """        
        super().__init__(master)
        self.title("Choose Countries")
        self._choices = ()
        self._F1 = tk.Frame(self)
        self._F1.grid(row=0, column=0)
        self._F2 = tk.Frame(self)
        self._F2.grid(row=0, column=1, sticky="ns")
        self._F2.grid_rowconfigure(0, weight=1)
        self._S = tk.Scrollbar(self._F2)
        self._LB = tk.Listbox(self._F1, height = 10, selectmode="multiple",\
                              yscrollcommand=self._S.set)
        for country in countries:
            self._LB.insert(tk.END, country[0])
        self._S.config(command=self._LB.yview)
        self._LB.grid(row=0, column=0)
        self._S.grid(row=0, column=1, sticky="ns")
        tk.Button(self, text="OK", command=self.setChoices).grid()
        self.grab_set() 
        self.focus_set()  
        
    def setChoices(self):
        """
        Assigns the Listbox selections to the class member variable _choices and
        closes the dialog window.
        """
        self._choices = self._LB.curselection()
        self.destroy()
        
    def getChoices(self):
        """
        Accessor method for the _choices class member variable.
        """
        return self._choices
        

class PlotWin(tk.Toplevel):
    def __init__(self, master, countries, indices):
        """
        Constructor for plot window.
        
        Args:
        master: The master of this Toplevel window.
        countries: A tuple with countries and their associated cases.
        indices: The indices of the user's country choices that correspond to the countries tuple.
        """
        super().__init__(master)
        self.transient(master)
        self.focus_set()
        self._countries = countries
        self.title("Covid-19 Cases")
        fig = plt.figure(figsize=(6,4))
        self.plotCases(indices)
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid()
        canvas.draw()        
        
    def plotCases(self, indices):
        """
        Plots the number of cases for the countries of the user's choice.
        """        
        x = range(len(indices))
        countryNames = []
        numCases = []
        for index in indices:
            countryNames.append(self._countries[index][0])
            numCases.append(self._countries[index][1])
        plt.bar(x, numCases, align="center")
        plt.title("Number of Cases for Chosen Countries")
        plt.xticks(x, countryNames, rotation=75, fontsize=8)
        plt.ylabel("Number of Cases per 1M People")
        plt.tight_layout()  
 
#Extra Credit        
class MultiListbox(tk.Frame):    
    def __init__(self, master, lists, height, needsScrollbar):
        """
        Constructor for MultiListbox.
        
        Args:
        master: The master of this specialized Frame.
        lists: A tuple of tuples that includes the headers and widths of every listbox
        height: The height of the MultiListbox.
        needsScrollbar: boolean value that specifies whether a Scrollbar is needed.
        """         
        tk.Frame.__init__(self, master)
        self.grid_rowconfigure(1, weight=1)
        self.lists = []
        for num, (heading, w) in enumerate(lists):
            frame = tk.Frame(self)
            frame.grid(row=0, column=num, sticky='nsew')
            tk.Label(frame, text=heading, borderwidth=1, relief=tk.RAISED).grid(row=0, column=num, sticky='we')
            lb = tk.Listbox(frame, height=height, width=w, borderwidth=0, selectborderwidth=0, relief=tk.FLAT)
            lb.grid(row=1, column=num, sticky='nsew')
            self.grid_columnconfigure(num, weight=1)
            self.lists.append(lb)
        if needsScrollbar:
            frame = tk.Frame(self)
            frame.grid_rowconfigure(0, weight=1)
            frame.grid(row=0, column=len(self.lists), sticky="ns")
            sb = tk.Scrollbar(frame, command=self.onSB)
            for lb in self.lists:
                lb.bind("<MouseWheel>", self.onMouseWheel)
                lb.config(yscrollcommand=sb.set)
            sb.grid(row=0, column=1, sticky="ns")
            
    def onSB(self, *args):
        """
        Function for if Scrollbar is used.
        """
        for lb in self.lists:
            lb.yview(*args)   
            
    def onMouseWheel(self, event):
        """
        Function for if Mousewheel is used.
        """        
        for lb in self.lists:
            lb.yview_scroll(-1*(event.delta), "units")
        return "break"            
            
    def insert(self, index, *elements):
        """
        Allows fields to be inserted into MultiListbox.
        """          
        for e in elements:
            for i, l in enumerate(self.lists):
                if e[i] == None:
                    l.insert(index, '--') #Insert if no data available
                else:
                    l.insert(index, e[i])  

def main():
    """
    Main driver that instantiates the main window object
    and runs main loop method.
    """
    app = MainWin()
    app.mainloop()
        
if __name__ == '__main__':
    main()
