"""Main unit, includes CharGen functions and entry point with loop"""
import World
import Item
import os.path
import sys
import pickle
import os

import Character
import UI
import BattleField
import Shop


def save():
    """Saves user character progress, returns 0 on success, -1 on failure"""
    global Player

    FileName = UI.xInput("Enter filename to save to (default: player.dat): ", "player.dat")
    FileName = "".join(("saves/", FileName))
    
    try:

        if os.path.exists(FileName):
            if input("Warning! File already exists. Type \'yes\' if you want to continue: ") != "yes":
                return 0

        Out = open(FileName, "wb")
        pickle.dump(Player, Out)
        Out.close()
        
    except Exception:
        print ("Error: " + sys.exc_info()[0])
        UI.waitForKey()
        return -1

    print("Complete")
    UI.waitForKey()
    return 0
    

def load():
    global Player
    global Arena
    
    FileName = UI.xInput("Enter filename to load from (default: player.dat): ", "player.dat")
    FileName = "".join(("saves/", FileName))
    
    try:
        if not os.path.exists(FileName):
            print("File doesn't exist!")
            UI.waitForKey()
            return -1

        Out = open(FileName, "rb")
        Player = pickle.load(Out)
        Out.close()

        # Resolve player's items to pointers
        # TODO: Use ID's to do it, save IDs to file
        for InvItem in Player.Inventory:
            for MasterItem in Item.ItemList:
                if InvItem.Base.Name == MasterItem.Name:
                    InvItem.Base = MasterItem

        for InvItem in Player.Inventory:
            if not InvItem.Equipped: break
            Player.Equipment[InvItem.Base.Type] = InvItem
		
        Arena.Opponent1 = Player

		
    except Exception:
        print ("Error: " + sys.exc_info()[0])
        UI.waitForKey()
        return -1


    print("Complete")
    UI.waitForKey()
    return 0
    

def charGen():
    """Player character generation with dialogue to replace an existing character"""
    global Player
    
    if Player.Exists and Player.Health != 0:
        choice = input ("Doing this will delete your current character, are you sure(yes)?")
        if (choice.strip() != "yes"): return
    
    Player.__init__()
    Player.IsPlayer = 1
    Player.generate()
    while not CharGenMenu.Returned:
        CharGenMenu.doMenu()
        if CharGenMenu.Returned:
            CharGenMenu.Returned = 0
            break


def charGenEnterName():
    """Small function to enter character name"""
    global Player
    NewName = input("Enter Character Name: ")
    Player.Name = NewName.strip ()

    #Easter Egg
    if Player.Name == "God":
        Player.Experience = 900
        Player.STR = 19
        Player.DEX = 19
        Player.CON = 19
        Player.MaxHealth = 1000
        Player.Health = 1000
        Player.calcModifiers()
        Player.Gold = 10000


def charGenRollForStats ():
    """Roll for player stats and display them"""
    global Player
    Player.generate()
    Player.showInfo()


Player = Character.CharClass()
Arena = BattleField.BattleFieldClass(Player)
NewWorld = World.WorldClass()
NewCell1 = World.CellClass()
NewCell2 = World.CellClass()

ToCell1 = World.CellExitClass()
ToCell1.Name = "To Cell 1"
ToCell1.Cell = NewCell1

ToCell2 = World.CellExitClass()
ToCell2.Name = "To Cell 2"
ToCell2.Cell = NewCell2

NewCell1.Name = "Cell 1"
NewCell1.Exits = [ToCell2]

NewCell2.Name = "Cell 2"
NewCell2.Exits = [ToCell1]

NewCell1.Chars.append(Player)
NewWorld.Cells = [NewCell1, NewCell2]

NewCell1.Items.append(Item.TestPotion)

TestMonster = Character.CharClass()
TestMonster.Name = "Rat"
TestMonster.generate()

TestMonster1 = Character.CharClass()
TestMonster1.Name = "Angry Rat"
TestMonster1.generate()

NewCell2.Chars += [TestMonster, TestMonster1]

#Main Menu
MainMenu = UI.MenuClass()
MainMenu.Title = "Console Massacre"
MainMenu.HasReturn = 0
#Character Generation Menu
CharGenMenu = UI.MenuClass()
CharGenMenu.Title = "Create Character"
CharGenMenu.addItem("Enter Name", charGenEnterName, "N")
CharGenMenu.addItem("Roll for Stats", charGenRollForStats, "S", 1)
CharGenMenu.addItem("View Stats", lambda: Player.showInfo(), "V", 1)


while 1:
    #Main game loop which just outputs menu, further choices are handled by menu logic
    MainMenu.clear()
    MainMenu.addItem("Create Character", charGen, "c")
    if Player.Exists and Player.Health > 0:
        MainMenu.addItem("Shop", lambda: Shop.Shop.doShop(Player), "s")
        MainMenu.addItem("Battle!", lambda: Arena.battle(), "b")
        MainMenu.addItem("Add Test Potion", lambda: Player.addItem(Item.TestPotion))
        MainMenu.addItem("Add Money", lambda: Player.addGold(10000))
        MainMenu.addItem("Teleport", lambda: NewWorld.doWorld(Player))
        MainMenu.addItem("Save", save, "v")
    MainMenu.addItem("Load", load, "l")
    MainMenu.addItem("Quit", exit, "q")
    
    MainMenu.doMenu()