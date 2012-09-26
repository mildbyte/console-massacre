"""
User Interface-related functions and classes

Includes platform-related functions for console handling and Menu class,
implementing basic text menu system.
"""

#import msvcrt

import UI

# The platform-independent getch courtesy of 
#http://code.activestate.com/recipes/134892/ (r2)
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()
## end of http://code.activestate.com/recipes/134892/

def emptyCallback():
    """Empty callback for menu which does nothing."""
    pass


def clrScr():
    """Clears screen, I have no better way to do it :D"""
    for _ in range (100):
        print("")


def waitForKey():
    """Blocks until user presses a key"""
    getch()


def printNow(ToPrint, Color = -1):
    """Prints a line without line break"""
    print(ToPrint, end = "")


def xInput(Prompt = "", Default = ""):
    """Inputs a line, having default parameter"""
    Choice = input(Prompt)
    if Choice == "": return Default
    else: return Choice


def choice (ChoicesList, Prompt = "", WaitForEnter = 0):
    """Choice dialogue, returns one of choices in ChoicesList, its code if WaitForEnter == 0"""
    if WaitForEnter:
        while 1:
            Choice = input (Prompt)
            if Choice in ChoicesList: break
            print ("Invalid choice")
        return Choice
    else:
        print (Prompt)
        while 1:
            Choice = getch()
            if ord(Choice) in ChoicesList: break
        return ord(Choice)


def inputNumber(Prompt = ""):
    """Requests a number from user, accepting only integers"""
    CanPass = 0
    while CanPass != 1:
        try:
            CanPass = 1
            if Prompt == "": Number = int(input ())
            else: Number = int(input (Prompt))
        except Exception:
            CanPass = 0
            print ("Invalid input")
    return Number


class MenuItemClass:
    """Menu Item class (a member of list for MenuClass)"""
    def __init__(self):
        self.Text = ""
        self.CallBack = lambda: emptyCallback #What to execute after activation
        self.WaitAfter = 0 #Wait for keypress after the activation
        self.IsSeparator = 0
        self.Key = ""
        self.ID = 0

class MenuPageClass:
    """A Menu page, normally one in a menu"""
    def __init__(self):
        self.Items = []
        self.PossibleKeys = []

class MenuClass:
    """Basic text letter-driven menu"""
    def __init__(self):
        self.Pages = [MenuPageClass()]
        self.PageIndex = 0
        self.OldPageIndex = 0
        self.Items = self.Pages[0].Items
        self.PossibleKeys = self.Pages[0].PossibleKeys
        self.Title = ""
        self.CustomText = ""
        self.HasReturn = 1
        self.Returned = 0
        self.ItemCount = 0
        self.DoCLS = 1
        
    def doMenu(self):
        """Executes the menu, executes user's chosen line, returns its index"""
        while 1:
            self.Items = self.Pages[self.PageIndex].Items
            self.PossibleKeys = self.Pages[self.PageIndex].PossibleKeys
            
            if self.DoCLS: clrScr()
            self.Returned = 0

            if self.Title != "": print("********"+ self.Title+ "********")
            if self.PageIndex > 0: print("...")
            for item in self.Items:
                if item.IsSeparator:
                    print(item.Text)
                else:
                    print(item.Key.upper(), item.Text)
            if self.PageIndex < len(self.Pages)-1: print("...")
            if self.CustomText != "": print (self.CustomText)

            #Get player's choice
            if self.HasReturn:
                if len(self.Pages) > 1:
                    choice = UI.choice(self.PossibleKeys + [27, ord('\xe0')], "Enter your choice (ESC to return): ")
                else:
                    choice = UI.choice(self.PossibleKeys + [27], "Enter your choice (ESC to return): ")
            else:
                if len(self.Pages) > 1:
                    choice = UI.choice(self.PossibleKeys + [ord('\xe0')], "Enter your choice: ")
                else:
                    choice = UI.choice(self.PossibleKeys, "Enter your choice: ")

            #If user has pressed ESC
            if self.HasReturn and choice == 27:
                self.Returned = 1
                return 0

            #If user has pressed an arrow key
            if choice == ord('\xe0') and len(self.Pages) > 1:
                choice = getch()
                if ord(choice) == ord('M'): #Right arrow
                    self.PageIndex += 1
                    if self.PageIndex >= len(self.Pages):
                        self.PageIndex = 0
                if ord(choice) == ord('K'): #Left arrow
                    self.PageIndex -= 1
                    if self.PageIndex < 0:
                        self.PageIndex = len(self.Pages)-1

                # Restart the loop with new variables
                continue

            for Temp in self.Items:
                if Temp.IsSeparator: continue
                if chr(choice) == Temp.Key.lower():
                    ChosenItem = Temp
                    break

            print ("")
            print ("")

            #Do an action described in MenuItem, wait for keypress if asked to, return user's choice
            ChosenItem.CallBack()
            if ChosenItem.WaitAfter: waitForKey()
            
            return ChosenItem.ID

    def clear(self):
        """Clears the menu"""
        self.Pages = [MenuPageClass()]

        self.Items = self.Pages[0].Items
        self.PossibleKeys = self.Pages[0].PossibleKeys

        self.OldPageIndex = self.PageIndex
        self.PageIndex = 0
        self.ItemCount = 0
        
    def addItem(self, Text = "No text defined!", CallBack = emptyCallback,  Key = "", WaitAfter = 0):
        """Adds an item to menu, default callback - empty, doesn't wait after execution"""
        NewItem = MenuItemClass()
        NewItem.Text = Text
        NewItem.CallBack = CallBack
        NewItem.WaitAfter = WaitAfter
        NewItem.ID = self.ItemCount
        self.ItemCount += 1
        
        if Key != "":
            if ord(Key.lower()) in self.PossibleKeys: Key = ""

        if Key == "":
            for i in range(97, 122):
                if not i in self.PossibleKeys:
                    NewItem.Key = chr(i)
                    break
        else: NewItem.Key = Key
        
        self.Items.append(NewItem)
        self.PossibleKeys.append(ord(NewItem.Key.lower()))

        #Create a new menu page if too much items
        if len(self.Items) >= 20:
            NewPage = MenuPageClass()
            self.Pages.append(NewPage)
            self.Items = NewPage.Items
            self.PossibleKeys = NewPage.PossibleKeys
       
    def addSeparator(self, Text = ""):
        NewItem = MenuItemClass()
        NewItem.IsSeparator = 1
        NewItem.Text = Text
        self.Items.append(NewItem)

    def restoreMenuPos(self):
        if len(self.Pages) > self.OldPageIndex:
            self.PageIndex = self.OldPageIndex
