"""Buying and selling-handling functions"""

import random

import Item
import UI

class Shop:
    """Shop-handling class"""
    def __init__(self):
        self.ShopMenu = UI.MenuClass()
        self.ShopMenu.Title = "Shop"
        self.ShopMenu.addItem ("Buy Weapons", UI.emptyCallback, "W")
        self.ShopMenu.addItem ("Buy Armor", UI.emptyCallback, "A")
        self.ShopMenu.addItem ("Sell Items", UI.emptyCallback, "S")

        random.seed()
        
        self.generateLists()
        
    def doShop(self, Player):
        """Starts the shop interface with Player"""

        #If player is dead or doesn't exist, exit the shop
        if Player.Exists == 0:
            print("You have to create a character first!")
            UI.waitForKey()
            UI.clrScr()
            return
        if Player.Health == 0:
            print("Your character is dead! Create a new one!")
            UI.waitForKey()
            UI.clrScr()
            return

        while not self.ShopMenu.Returned:
            Choice = self.ShopMenu.doMenu()
            if self.ShopMenu.Returned:
                self.ShopMenu.Returned = 0
                break
            if Choice == 0: self.doBuyWeapon(Player)
            elif Choice == 1: self.doBuyArmor(Player)
            else: self.doSell(Player)


    def generateLists(self):
        self.ArmorList = []
        self.WeaponList = []

        for Key in Item.ItemList:
            ShopItem = Item.ItemList[Key]
            if ShopItem.Probability >= random.random():
                if ShopItem.Type == "Armor":
                    self.ArmorList.append(ShopItem)
                elif ShopItem.Type == "Weapon":
                    self.WeaponList.append(ShopItem)
        
    def doBuyArmor(self, Player):
        """Initializes armor buy dialogue with player"""
        #Generate shop inventory menu
        ShopWaresMenu = UI.MenuClass()
        ShopWaresMenu.Title = "Armor"

        while not ShopWaresMenu.Returned:
            #Fill with with items & information and trade-in value
            ShopWaresMenu.clear()
            
            for ShopItem in self.ArmorList:
                Name = ShopItem.descString()
                ShopWaresMenu.addItem(Name)
            ShopWaresMenu.CustomText = "You have " + str(Player.Gold) +\
            " gp\nYour armor: " + Player.Equipment["Armor"].Base.descString()

            Index = ShopWaresMenu.doMenu()
            if ShopWaresMenu.Returned: break

            ShopItem = self.ArmorList[Index]
            if Player.Gold < ShopItem.Value:
                print ("You cannot afford that!")
                UI.waitForKey()
                continue

            #Secure the transaction
            self.ArmorList.remove(ShopItem)
            Player.Gold -= ShopItem.Value
            Player.addItem(ShopItem)
            print (ShopItem.Name, "bought")
            UI.waitForKey()

    def doBuyWeapon(self, Player):
        ShopWaresMenu = UI.MenuClass()
        ShopWaresMenu.Title = "Weapons"

        #Do bying menu
        while not ShopWaresMenu.Returned:
            #Fill with with items & information and trade-in value
            ShopWaresMenu.clear()
            for ShopItem in self.WeaponList:
                Name = ShopItem.descString()
                ShopWaresMenu.addItem(Name)
            ShopWaresMenu.CustomText = "You have " + str(Player.Gold) +\
            " gp\nYour weapon: " + Player.Equipment["Weapon"].Base.descString()

            Index = ShopWaresMenu.doMenu()
            if ShopWaresMenu.Returned: break

            ShopItem = self.WeaponList[Index]
            if Player.Gold < ShopItem.Value:
                print ("You cannot afford that!")
                UI.waitForKey()
                continue

            #Secure the transaction
            self.WeaponList.remove(ShopItem)
            Player.addItem(ShopItem)
            Player.Gold -= ShopItem.Value
            print (ShopItem.Name, "bought")
            UI.waitForKey()

    def doSell(self, Player):
        """Initializes sell dialogue with Player"""
        while 1:
            ChosenItem = Player.Inventory.chooseInventoryItem("Sell")
            if ChosenItem == None: break
            
            Player.removeItem(ChosenItem.Base)
            Player.Gold += ChosenItem.Base.Value
            print (ChosenItem.Base.Name, "sold")
            UI.waitForKey()

Shop = Shop()