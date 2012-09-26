"""World-management module with game core and cell management"""
import random

import UI
import BattleField

class CellExitClass:
    """An exit from a cell"""
    Name = ""
    Cell = None
    

class CellClass:
    """One game cell"""
    def __init__(self):
        self.Name = ""
        self.Exits = []
        self.Chars = []
        self.Attackable = []
        self.Items = []
        self.Description = ""
        self.LastBattleResult = 0
        
    def doExamine(self, Player):
        """Starts cell object examination dialogue"""
        while 1:
            ObjectMenu = UI.MenuClass()
            ObjectMenu.Title = "Objects"
            for Object in self.Items:
                ObjectMenu.addItem(Object.Name)

            Choice = ObjectMenu.doMenu()
            if ObjectMenu.Returned: break

            Chosen = self.Items[Choice]

            print(Chosen.descString())
            ChosenMenu = UI.MenuClass()
            ChosenMenu.DoCLS = 0
            ChosenMenu.addItem("Take", UI.emptyCallback, "t")

            Choice = ChosenMenu.doMenu()
            if ChosenMenu.Returned: continue

            if Choice == 0:
                self.Items.remove(Chosen)
                Player.Inventory.addItem(Chosen)
                print("You take", Chosen.Name)
                UI.waitForKey()

    def doAttack(self, Player):
        """Allows player to attack a monster. Returns 0 if player wins, 1 if loses, -1 if flees"""
        while 1:
            #Allow player to select his target
            if self.Attackable == []: break
            TargetMenu = UI.MenuClass()
            TargetMenu.Title = "Attack"
            for Target in self.Attackable:
                if Target.Health > 0:
                    TargetMenu.addItem(Target.Name)

            Choice = TargetMenu.doMenu()
            if TargetMenu.Returned: break

            Target = self.Attackable[Choice]

            #Initialise the battlefield
            Battle = BattleField.BattleFieldClass()
            Battle.ClassicMode = 0
            Battle.Opponent1 = Player
            Battle.Initiative = Player
            Battle.Opponent2 = Target

            Battle.battle()

            #Battle result
            if Player.Health <= 0:
                self.LastBattleResult = 1
                break
            elif Target.Health > 0:
                #If player and target are alive, player fled
                self.LastBattleResult = -1
                break
            else:
                self.LastBattleResult = 0
                self.Attackable.remove(Target)

    def doShowInfo(self, Player):
        """Show player' info + waits for key"""
        Player.showInfo()
        UI.waitForKey()
    
    def doCell(self, Player):
        """Performs a cell cycle, getting player's choice. Returns cell ID to which player has gone"""
        while 1:
            UI.clrScr()
            print("***", self.Name, "***")
            if self.Description != "": print(self.Description)
            if self.Items != []:
                print("")
                for Temp in self.Items: print(Temp.Name)

            self.Attackable = []
            for Temp in self.Chars:
                if Temp != Player and Temp.Health >0: self.Attackable.append(Temp)

            if self.Chars != []:
                print("")
                for Temp in self.Chars:
                    if Temp != Player:
                        if Temp.Health > 0:
                            print(Temp.Name)
                        else:
                            print(Temp.Name, "(dead)")

            print("")
            print("")
            
            CellMenu = UI.MenuClass()
            CellMenu.DoCLS = 0
            for Exit in self.Exits:
                CellMenu.addItem(">> " + Exit.Name)

            CellMenu.addSeparator()

            if self.Attackable != []: CellMenu.addItem("Fight", lambda: self.doAttack(Player), "w")
            if self.Items != []:
                CellMenu.addItem("Examine Objects", lambda: self.doExamine(Player), "x")
            
            CellMenu.addItem("Stats", lambda: self.doShowInfo(Player), "y")
            CellMenu.addItem("Inventory", lambda: Player.doInventory(self), "z")

            Choice = CellMenu.doMenu()
            if self.LastBattleResult != 0:  #Last battle didn't pass correctly
                if self.LastBattleResult == 1:
                    return None #Player dead, do a barrel roll
                else:
                    #Player fled, propel him to somewhere else
                    NewCell = random.sample(self.Exits, 1)[0].Cell
                    self.Chars.remove(Player)
                    NewCell.Chars.append(Player)
                    return NewCell

            if Choice + 1 > len(self.Exits):
                continue

            NewCell = self.Exits[Choice].Cell
            if CellMenu.Returned:
                return None

            self.Chars.remove(Player)
            NewCell.Chars.append(Player)
            return NewCell


class WorldClass:
    """Game world class. Performs all interaction between player and world"""
    def __init__(self):
        self.Name = ""
        self.Cells = []
        self.PlayerCell = None
        
    def doWorld(self, Player):
        #If player's cell not defined, find player in current cell list
        if self.PlayerCell == None:
            for Cell in self.Cells:
                if Player in Cell.Chars:
                    self.PlayerCell = Cell
                    break

        #If no player found, bail out
        if self.PlayerCell == None:
            print("No player detected!")
            UI.waitForKey()
            return

        while 1:
            NewCell = self.PlayerCell.doCell(Player)
            if NewCell == None:
                break
            else:
                self.PlayerCell = NewCell
    