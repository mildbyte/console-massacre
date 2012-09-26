"""Battle simulation module with only function for battle simulation"""
import time
from collections import deque

import UI
import Character
import Item
import Shop

def genOpponent(MaxLevel):
    """Generates a monster with level chosen by user, max MaxLevel"""
    #If Player has won over a level 1 opponent, he's given choice of other
    #opponents up to his level (1..maximal level won + 1)
    if MaxLevel != 1:
        while 1:
            UI.printNow("Select monster level to battle (1.. " + str(MaxLevel) + " ): ")
            choice = UI.inputNumber()
            if (choice < 1) or (choice > MaxLevel):
                print("Invalid choice!")
            else: break
    else: choice = 1

    #Generate a random monster of a given level
    Monster = Character.CharClass()
    Monster.generate(choice)
    Monster.Name = "Level " + str(Monster.Level) + " Monster"

    return Monster


class BattleFieldClass:
    """Battlefield simulation class"""
    def __init__(self, Opponent1 = None, Opponent2 = None, ClassicMode = 1):
        self.Opponent1 = Opponent1
        self.Opponent2 = Opponent2
        self.ClassicMode = ClassicMode
        self.Initiative = None
    def battle(self, Op1 = None, Op2 = None):
        """Simulates a battle between two opponents"""

        UI.clrScr()
        
        if Op1 != None: self.Opponent1 = Op1
        if Op2 != None: self.Opponent1 = Op2
        
        if self.Opponent1 == None:
            print("Battle error: opponent 1 not defined")
            UI.waitForKey()
            return

        if self.ClassicMode:
            self.Opponent2 = genOpponent(self.Opponent1.MaxWon+1)

        #Shortcuts for Opponents 1 and 2
        P1 = self.Opponent1
        P2 = self.Opponent2

        #If no player amongst the combatants, do not display any information
        if not P1.IsPlayer and not P2.IsPlayer:
            Silent = 1
        else:
            Silent = 0

        #Battle choice menu
        BattleChoiceMenu = UI.MenuClass()
        BattleChoiceMenu.DoCLS = 0
        BattleChoiceMenu.HasReturn = 0
        BattleChoiceMenu.addItem("Attack", UI.emptyCallback, "A")
        BattleChoiceMenu.addItem("Flee", UI.emptyCallback, "F")
        BattleChoiceMenu.addItem("Use Potion", UI.emptyCallback, "P")

        if not Silent: print("Battle between", P1.Name, "and", P2.Name)
        P1.calcModifiers()
        P2.calcModifiers()

        if self.Initiative == None:
            P1.calcInitiative()
            P2.calcInitiative()
            if P1.Initiative > P2.Initiative:
                self.Initiative = P1
            else:
                self.Initiative = P2

        #Who goes first is based on the initiative.
        #Opponents exchange blows until someone is dead.
        #Turn == 0 - first opponent's turn
        if self.Initiative == P1:
            BattleQueue = deque([P1, P2])
        else:
            BattleQueue = deque([P2, P1])
            
        while BattleQueue[0].Health > 0 and BattleQueue[1].Health > 0:
            for Fighter in BattleQueue:
                Fighter.doEffects()
                Fighter.calcModifiers()

            Fighter = BattleQueue[0]
            if Fighter.IsPlayer:
                while 1:
                    Choice = BattleChoiceMenu.doMenu()
                    if Choice != 2: break
                    ToDrink = Fighter.Inventory.chooseInventoryItem("Potions", ["Potion"])
                    if ToDrink == None: continue
                    else: break
            else:
                if not Silent: time.sleep(2)
                Choice = 0

            #Attack, drink potion or flee?
            if Choice == 0:
                Fighter.attack(BattleQueue[1])
            elif Choice == 1:
                print("You flee the battle!")
                Fighter.Health = Fighter.MaxHealth
                UI.waitForKey()
                return
            elif Choice == 2:
                print("You drink", ToDrink.Base.Name)
                Fighter.useItem(ToDrink.Base)
                UI.waitForKey()
            BattleQueue.popleft()
            BattleQueue.append(Fighter)

        #Battle over
        #Expire all effects
        for Fighter in BattleQueue:
            Fighter.clearEffects()
            if Fighter.Health == 0:
                if not Silent: print(Fighter.Name, "is dead!")
                if Fighter.IsPlayer:
                    UI.waitForKey()
                    return
            
        #If we are there, a player is here and he's still alive
        if BattleQueue[0].Health == 0:
            Player = BattleQueue[1]
            Monster = BattleQueue[0]
        else:
            Player = BattleQueue[0]
            Monster = BattleQueue[1]
            
        Player.Health = Player.MaxHealth
        if Monster.Level > Player.MaxWon:
            Player.MaxWon = Monster.Level

        #Calculate player and monster level difference (0 - 5 levels weaker, 10 -
        #5+ levels stronger than the monster)
        LevelDiff = Monster.Level-Player.Level + 5
        if LevelDiff <= 0: LevelDiff = 0
        if LevelDiff >= 10: LevelDiff = 10

        #Give player gold and experience based on level difference and monster level
        EXP = Item.ExpReward[LevelDiff]
        Gold = Item.GoldReward[Monster.Level-1]
        print(Player.Name, "gets", EXP, "XP and", Gold, "gold pieces")
        Player.Experience += EXP
        Player.Gold += Gold

        #Update armor and weapon lists in shop
        Shop.Shop.generateLists()

        #Level up the player if his experience reaches goal
        if Player.Experience >= Player.ExpGoal:
            print(Player.Name, "has leveled up to level", Player.Level + 1)
            UI.waitForKey()
            Player.levelUp()
        else: UI.waitForKey()

        UI.clrScr()
