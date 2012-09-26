"""Classes for working with armor, master lists and other constants"""
from xml.dom import minidom
import sys

import UI

EffectTypeFortify = 0
EffectTypeHeal = 1


class ItemClass:
    ID = ""
    Name = ""
    Value = 0
    Probability = 1
    CanEquip = 0
    Type = "Misc"
    def descString(self):
        return self.Name


class InventoryItemClass:
    def __init__(self, Base = None, Equipped = 0, Count = 1):
        self.Base = Base
        self.Equipped = Equipped
        self.Count = Count


class InventoryClass:
    """Inventory, used for containers, shops and player objects"""
    def __init__(self):
        self.List = []

    def addItem(self, ItemBase, Count = 1):
        """Adds item to player's inventory, increases count if it's already here"""
        Found = 0
        for CurrItem in self.List:
            if CurrItem.Base == ItemBase:
                Found = 1
                break

        if Found: CurrItem.Count += Count
        else:
            NewItem = InventoryItemClass()
            NewItem.Count = Count
            NewItem.Base = ItemBase
            self.List.append(NewItem)

    def removeItem(self, ItemBase, Count = 1):
        """Removes item from player's inventory (Decreases count)"""
        Found = 0
        for CurrItem in self.List:
            if CurrItem.Base == ItemBase:
                Found = 1
                break

        if Found:
            CurrItem.Count -= Count
            if CurrItem.Count <= 0:
                self.List.remove(CurrItem)

    def getItemCount(self, ItemBase):
        """Returns a count of items in inventory with base ItemBase"""
        Found = 0
        for CurrItem in self.List:
            if CurrItem.Base == ItemBase:
                Found = 1
                break

        if not Found: return 0
        else: return CurrItem.Count

    def chooseInventoryItem(self, Title = "", Filter = []):
        """Shows an inventory menu of a character, returns a pointer or None"""
        InventoryMenu = UI.MenuClass()
        InventoryMenu.Title = Title

        #Show all inventory items if Filter not specified
        if Filter == []: ShowAll = 1
        else: ShowAll = 0

        #Generate inventory menu
        MyInvMenu = {} #Dictionary (item type : list of items)
        for InvItem in self.List:
            if InvItem.Base.Type in Filter or ShowAll:
                if not InvItem.Base.Type in MyInvMenu:
                    #Create new dictionary key if it isn't here
                    MyInvMenu[InvItem.Base.Type] = []
                MyInvMenu[InvItem.Base.Type].append(InvItem)

        #Merge list of all inventory items, sorted by type
        MyInvMenuData = []
        for InvItemKey in MyInvMenu:
            MyInvMenuData += MyInvMenu[InvItemKey]


        #Form the menu
        InventoryMenu.clear()

        for InvItemKey in MyInvMenu:
            InventoryMenu.addSeparator("--" + InvItemKey + "--")
            for InvItem in MyInvMenu[InvItemKey]:
                if InvItem.Count == 1:
                    Name = InvItem.Base.descString()
                else:
                    Name = InvItem.Base.descString() + " x" + str(InvItem.Count)
                if InvItem.Equipped: Name = "".join((Name, " (equipped)"))
                InventoryMenu.addItem(Name)

        #Restore old menu position
        InventoryMenu.restoreMenuPos()

        Choice = InventoryMenu.doMenu()
        if InventoryMenu.Returned: return None
        return MyInvMenuData[Choice]


class ArmorClass(ItemClass):
    def __init__(self):
        self.Type = "Armor"
        self.AR = 0
        self.MaxDEXMod = 100
        self.CanEquip = 1
    def descString(self):
        """Returns a formatted description string"""
        return "".join ([self.Name, " (AR ", str(self.AR), ", Max DEX "\
            , str(self.MaxDEXMod), ") - ", str(self.Value), " gp"])


class WeaponClass(ItemClass):
    def __init__(self):
        self.Type = "Weapon"
        self.CanEquip = 1
        self.RollCount = 1
        self.RollMax = 3
        self.CritRollMin = 20
        self.CritRollMax = 20
        self.CritRollMult = 2
    def descString(self):
         """Returns a formatted description string"""
         return "".join ([self.Name, " (", str(self.RollCount), "d"\
            , str(self.RollMax), "; ", str(self.CritRollMin), "-"\
            , str(self.CritRollMax), "x", str (self.CritRollMult)\
            , ") - ", str(self.Value), " gp"])


class EffectClass:
    def __init__(self):
        self.Type = EffectTypeFortify
        self.Attribute = "STR"
        self.Magnitude = 10000
        self.Duration = -1


class ActiveEffectClass:
    """Stores an effect from a potion or a spell with TTL"""
    def __init__(self):
        self.Base = None
        self.TTL = -1


class PotionClass(ItemClass):
    def __init__(self):
        self.Type = "Potion"
        self.Effects = []


ItemList = {}


try:
    dom = minidom.parse("items.xml")
except Exception:
    print("Error while loading items.xml!")
    UI.waitForKey()
    exit()

#Unarmed & Unarmed
NoWeapon = WeaponClass()
NoWeapon.Name = "Fists"
NoWeapon.Probability = 0
NoWeapon = InventoryItemClass(NoWeapon)
NoArmor = ArmorClass()
NoArmor.Name = "Unarmored"
NoArmor.Probability = 0
NoArmor.AR = 0
NoArmor = InventoryItemClass(NoArmor)

NoItem = {"Weapon": NoWeapon, "Armor": NoArmor}

#Import all weapons from an xml file
for item in dom.getElementsByTagName('weapon'):
    try:
        NewWeapon = WeaponClass()

        #Get all string attributes
        if item.hasAttribute("name"):
            NewWeapon.Name = item.attributes["name"].value
        if item.hasAttribute("id"):
            NewWeapon.ID = item.attributes["id"].value
        else: NewWeapon.ID = NewWeapon.Name

        #Get all float attributes
        if item.hasAttribute("probability"):
            if item.attributes["probability"].value != "":
                NewWeapon.Probability = float(item.attributes["probability"].value)
        #Get all other (integer) attributes
        for attr in ("RollCount", "RollMax", "CritRollMin", "CritRollMax", "CritRollMult", "Value"):
            if item.hasAttribute(attr.lower()):
                NewWeapon.__setattr__(attr, int(item.attributes[attr.lower()].value))
    except Exception:
        print("Error while loading WeaponList: ", sys.exc_info()[0])
        UI.waitForKey()
        continue
        
    ItemList[NewWeapon.ID] = NewWeapon


for item in dom.getElementsByTagName('armor'):
    try:
        NewArmor = ArmorClass()

        #Get all string attributes
        if item.hasAttribute("name"):
            NewArmor.Name = item.attributes["name"].value
            
        if item.hasAttribute("id"):
            NewArmor.ID = item.attributes["id"].value
        else: NewArmor.ID = NewArmor.Name

        #Get all float attributes
        if item.hasAttribute("probability"):
            NewArmor.Probability = float(item.attributes["probability"].value)

        #Get all integer attributes
        for attr in ("AR", "MaxDEXMod", "Value"):
            if attr.lower()[0]!="_" and item.hasAttribute(attr.lower()):
                NewArmor.__setattr__(attr, int(item.attributes[attr.lower()].value))

    except Exception:
        print("Error while loading ArmorList: ", sys.exc_info()[0])
        UI.waitForKey()
        continue
        
    ItemList[NewArmor.ID] = NewArmor


TestPotion = PotionClass()
TestPotion.Name = "Potion Of Epic Strength"
TestEffect = EffectClass()
TestPotion.Effects.append(TestEffect)
ItemList["test potion"] = TestPotion
    
ExpReward = (5, 15, 35, 75, 150, 300, 450, 500, 600, 700, 800)
GoldReward = (1, 2, 3, 5, 10, 16, 25, 35, 48, 60, 80, 100, 120, 150, 175, 210, 250, 300, 400, 500)