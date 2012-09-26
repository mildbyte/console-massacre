"""
d20 Character Class Module

Contains a CharClass class, implementing basic d20 character with parameters for
name, level, HP, EXP, STR, DEX, CON...
"""

import random
import Item
import UI

def diceRoll(DiceMax, DiceCount = 1):
    """Performs canonic DiceCount rolls of DiceMax-sided die"""
    sum = 0
    for _ in range(DiceCount):
        sum += random.randint(1, DiceMax)
    return sum

class CharClass:
    """d20 Character Class"""
    def __init__(self):
        random.seed()
        self.Exists = 0     #Character is defined
        self.Name = ""
        self.Level = 1
        self.Health = 10
        self.MaxHealth = 10
        self.Experience = 0
        self.ExpGoal = 1000
        self.IsPlayer = 0   #Character is Player Character
        self.MaxWon = 0
        self.Equipment = {"Armor": Item.NoArmor, "Weapon":  Item.NoWeapon}
        self.Gold = 0
        self.Attributes = {"STR": 8, "DEX": 8, "CON": 8}
        self.Modifiers = {"STR": 0, "DEX": 0, "CON": 0}
        self.Effects = []
        self.AttackRoll = 0
        self.ArmorCheck = 0
        self.Initiative = 0
        self.Inventory = Item.InventoryClass()
        self.Hostile = 0

    def generate(self, Level = 1):
        """Creates a random Level level character"""
        self.Exists = 1
        for Attr in self.Attributes:
            self.Attributes [Attr] = 5 + diceRoll(3, 3)
        self.calcModifiers()
        self.MaxHealth = 10 + self.Modifiers["CON"]
        self.Health = self.MaxHealth
        for _ in range(Level-2): self.levelUp()
        if Level != 1:
            self.Experience = self.ExpGoal
            self.levelUp()

    def calcModifiers(self):
        """Calculates STR, DEX & CON modifiers by d20 rules"""
        for Attr in self.Attributes:
        	self.Modifiers [Attr] = (self.Attributes [Attr]-10)//2

    def calcArmorCheck(self):
        """Calculates Armor Check (used for attack) by d20 rules"""
        self.calcModifiers()
        if self.Modifiers["DEX"] > self.Equipment["Armor"].Base.MaxDEXMod:
            CurrDEX = self.Equipment["Armor"].Base.MaxDEXMod
        else: CurrDEX = self.Modifiers["DEX"]
        self.ArmorCheck = 10 + CurrDEX + self.Equipment["Armor"].Base.AR

    def calcAttackRoll(self):
        """Calculates Attack Roll by d20 rules, returns critical multiplier if exists"""
        self.calcModifiers()
        Roll = diceRoll(20)
        self.AttackRoll = Roll + self.Modifiers["STR"]+ self.Level

        if (Roll >= self.Equipment["Weapon"].Base.CritRollMin)\
        and (Roll <= self.Equipment["Weapon"].Base.CritRollMax):
            return self.Equipment["Weapon"].Base.CritRollMult
        else: return 1

    def calcInitiative(self):
        """Calculates player Initiative by d20 rules (used for determining order in a battle)"""
        self.Initiative = diceRoll(20) + self.Modifiers["DEX"]

    def attack(self, Target):
        """Performs an attack of Target by d20 rules, outputting info"""

        #Calculate my attack roll and target's armor check
        RollResult = self.calcAttackRoll()
        Target.calcArmorCheck()

        #If attack doesn't succeed (roll < check), exit
        if self.AttackRoll < Target.ArmorCheck:
            print(self.Name, "misses", Target.Name, "(", self.AttackRoll, "vs", Target.ArmorCheck, ")")
            return

        #Notify if the character has a multiplier
        if RollResult != 1:
            print(self.Name, "gets a critical multiplier!")

        #Calculate damage and substract it from target's health, RollResult times
        for _ in range(RollResult):
            Damage = self.Modifiers["STR"] +\
                diceRoll(self.Equipment["Weapon"].Base.RollMax,\
                self.Equipment["Weapon"].Base.RollCount)

            Target.Health -= Damage;
            if Target.Health < 0: Target.Health = 0
            print(self.Name, "hits", Target.Name, "with his", self.Equipment["Weapon"].Base.Name,\
                    "for", Damage, "points of damage(", self.AttackRoll, "vs", Target.ArmorCheck, ")!")

        print(Target.Name, "has", Target.Health, "HP left.")

    def levelUp(self):
        """Performs a level-up, increasing max health; EXP and an attribute"""
        self.Level += 1
        self.ExpGoal += self.Level * 1000
        self.MaxHealth += diceRoll(10) + self.Modifiers ["CON"]
        self.Health = self.MaxHealth

        LevelUpMenu = UI.MenuClass()
        LevelUpMenu.Title = "Level up"
        LevelUpMenu.CustomText = "Select an attribute to increase!"
        for Attr in self.Attributes:
            LevelUpMenu.addItem(Attr + " (" + str(self.Attributes[Attr]) + ")")
        LevelUpMenu.HasReturn = 0

        while 1:

            if self.IsPlayer:
                Choice = LevelUpMenu.doMenu()
            else: Choice = diceRoll(3)

            #Requests attribute to modify until it doesn't exceed 20, using menu
            #interface for player, 1d3 dice roll for monster
            if Choice == 0: Attr = "STR"
            elif Choice == 1: Attr = "DEX"
            elif Choice == 2: Attr = "CON"
            if self.Attributes[Attr] == 20:
                    if self.IsPlayer: print ("You cannot increase this attribute!")
                    continue
            self.Attributes[Attr] += 1
            break

        self.calcModifiers()

    def showInfo(self):
        """Shows information of a character"""
        if not self.Exists:
            print("You have to create a character first!")
            return

        print(self.Name)
        print("Health: ", self.Health, "/", self.MaxHealth)
        print("Level: ", self.Level)
        if (self.IsPlayer): print("XP: ", self.Experience, "/", self.ExpGoal)
        for Attr in self.Modifiers:
            print(Attr, ": ", self.Attributes[Attr], "(", self.Modifiers[Attr], ")")
        print("Armor: ", self.Equipment["Armor"].Base.descString())
        print("Weapon: ", self.Equipment["Weapon"].Base.descString())
        if (self.IsPlayer): print("Gold: ", self.Gold)
        if (self.IsPlayer): print("Max level won:", self.MaxWon)

    def addItem(self, ItemBase, Count = 1):
        """Adds item to player's inventory"""
        self.Inventory.addItem(ItemBase, Count)

    def removeItem(self, ItemBase, Count = 1):
        """Removes item from player's inventory."""
        self.Inventory.removeItem(ItemBase, Count)
        self.unequip(ItemBase)

    def getItemCount(self, ItemBase):
        """Returns a count of items in inventory with base ItemBase"""
        return self.Inventory.getItemCount(ItemBase)

    def addGold(self, Gold):
        self.Gold += Gold

    def equip(self, ItemBase):
        """Equips an item if found"""
        for CurrItem in self.Inventory.List:
            if CurrItem.Base == ItemBase:
                if not CurrItem.Base.CanEquip: return
                CurrItem.Equipped = 1
                self.unequip(self.Equipment[CurrItem.Base.Type].Base)
                self.Equipment[CurrItem.Base.Type] = CurrItem

    def unequip(self, ItemBase):
        """Unequips an item if found"""
        for CurrItem in self.Inventory.List:
            if CurrItem.Base == ItemBase:
                if not CurrItem.Base.CanEquip: return
                CurrItem.Equipped = 0
                self.Equipment[ItemBase.Type] = Item.NoItem[ItemBase.Type]

    def addEffect(self, Effect):
        """Adds an effect to the character, applying all bonuses"""
        if Effect.Type == Item.EffectTypeFortify:
            self.Attributes[Effect.Attribute] += Effect.Magnitude
        NewEffect = Item.ActiveEffectClass()
        NewEffect.Base = Effect
        NewEffect.TTL = Effect.Duration
        self.Effects.append(NewEffect)

    def removeEffect(self, Effect):
        """Removes an effect from effects' list, disabling all bonuses"""
        if Effect.Base.Type == Item.EffectTypeFortify:
            self.Attributes[Effect.Base.Attribute] -= Effect.Base.Magnitude
        self.Effects.remove(Effect)

    def clearEffects(self):
        """Clears all effects from a character with non-perpetual TTL"""
        #Iterating backwards to be able to remove items from the list on-the-fly
        I = len(self.Effects)
        while I != 0:
            CurrEffect = self.Effects[I-1]
            if CurrEffect.TTL != -1:
                self.removeEffect(CurrEffect)
            I -= 1

    def doEffects(self):
        """Decreases all effects' TTL, applies per-turn bonuses and removes expired effects"""
        #Iterating backwards to be able to remove items from the list on-the-fly
        I = len(self.Effects)
        while I != 0:
            CurrEffect = self.Effects[I-1]
            if CurrEffect.Base.Type == Item.EffectTypeHeal:
                self.Health += CurrEffect.Base.Magnitude
                if self.Health > self.MaxHealth: self.Health = self.MaxHealth
            if CurrEffect.TTL != -1:
                CurrEffect.TTL -= 1
                if CurrEffect.TTL == 0:
                    self.removeEffect(CurrEffect)
            I -= 1
            
    def useItem(self, ItemBase):
        """Makes player consume a potion described by ItemBase"""
        if self.getItemCount(ItemBase) == 0: return
        if ItemBase.Type != "Potion": return

        for CurrEffect in ItemBase.Effects:
            self.addEffect(CurrEffect)

        self.removeItem(ItemBase)

    def doInventory(self, MyCell):
        """Shows character inventory menu"""
        while 1:
            ChosenItem = self.Inventory.chooseInventoryItem("Your inventory")
            if ChosenItem == None: break

            InventoryItemMenu = UI.MenuClass()
            InventoryItemMenu.Title = ChosenItem.Base.Name
            if ChosenItem.Base.CanEquip:
                if ChosenItem.Equipped:
                    InventoryItemMenu.addItem("Unequip", lambda:
                        self.unequip(ChosenItem.Base), "U", 1)
                else:
                    InventoryItemMenu.addItem("Equip",  lambda:
                        self.equip(ChosenItem.Base), "E", 1)

            InventoryItemMenu.addItem("Drop", UI.emptyCallback, "D")

            Choice = InventoryItemMenu.doMenu()
            if InventoryItemMenu.Returned: continue

            if InventoryItemMenu.Items[Choice].Text == "Drop":
                if ChosenItem.Count == 1:
                    self.removeItem((ChosenItem.Base))
                    MyCell.Items.append(ChosenItem.Base)
                    print(ChosenItem.Base.Name, "dropped")
                    break

                while 1:
                    ToDrop = UI.inputNumber("Enter count of items to drop (max "\
                    + str(ChosenItem.Count) + "): ")
                    if ToDrop in range(ChosenItem.Count + 1): break
                    print("Invalid choice")

                self.removeItem(ChosenItem.Base, ToDrop)
                print(ChosenItem.Base.Name, "x", ToDrop, "dropped")
                MyCell.Items.append(ChosenItem.Base)
                UI.waitForKey()
