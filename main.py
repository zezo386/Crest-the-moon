import os
import msvcrt 
import time
import random
import pygame

pygame.init()
pygame.mixer.init()


class Enemy:
    def __init__(self,loot,dmg,special,health):
        self.loot = loot
        self.dmg = dmg
        self.special = special
        self.hp = health
    def shout(self):
        shouts = []
        shouts.append("You dare challenge me?")
        shouts.append("Prepare to meet your doom!")
        shouts.append("I will crush you!")
        shouts.append("You are no match for me!")
        print(shouts[random.randint(0,len(shouts)-1)])

class Game:
    def __init__(self):
        self.difficulty = "Medium"
        self.volume = 5
        self.inventory = []
        self.gold = 0
        self.swords_powers = {'broken sword':{'hand damage':5,'two hand damage':8,'special':'chance to miss'},
                              'normal sword':{'hand damage':10,'two hand damage':15,'special':'none'},
                              'long sword':{'hand damage':15,'two hand damage':25,'special':'armor piercing'},
                              'great sword':{'hand damage':25,'two hand damage':40,'special':'bleed chance'}}
        

        self.items_effects = {'health potion':{self.use_health_potion}}


        self.current_sword = None
        self.hp = 10
        self.max_hp = 10
        self.last_checkpoint = None

        while True:
            time.sleep(3)
            menu_options = ["Option 1: Start Game", "Option 2: Settings", "Option 3: Exit"]
            selected_option = self.interactive_menu(menu_options)
            self.clear_console()
            if selected_option == "Option 1: Start Game":
                print("Starting the game...")
                self.start_game()
            elif selected_option == "Option 2: Settings":
                print("Opening settings...")
                self.settings()
            else:
                print("Exiting the program...")
        
    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def interactive_menu(self,options):
        current_selection = 0
        while True:
            self.clear_console()
            print("Please choose an option:")
            for i, option in enumerate(options):
                if i == current_selection:
                    print(f"-> {option}")
                else:
                    print(f"   {option}")

            key = msvcrt.getch()
            
            # Arrow keys on Windows are often preceded by a null byte (0xe0)
            if key == b'\xe0':
                key = msvcrt.getch() # Read the actual arrow key code
                if key == b'H':  # Up arrow
                    current_selection = (current_selection - 1) % len(options)
                elif key == b'P':  # Down arrow
                    current_selection = (current_selection + 1) % len(options)
            elif key == b'\r':  # Enter key
                return options[current_selection]
    def selection_only_interactive_menu(self,options):
        current_selection = 0
        while True:
            self.clear_console()
            print("Please choose an option:")
            for i, option in enumerate(options):
                if i == current_selection:
                    print(f"-> {option}")
                    test_sound = pygame.mixer.Sound("test sound.mp3")
                    test_sound.set_volume(int(option) / 10)
                    test_sound.play()

            key = msvcrt.getch()
            
            # Arrow keys on Windows are often preceded by a null byte (0xe0)
            if key == b'\xe0':
                key = msvcrt.getch() # Read the actual arrow key code
                if key == b'H':  # Up arrow
                    current_selection = (current_selection - 1) % len(options)
                elif key == b'P':  # Down arrow
                    current_selection = (current_selection + 1) % len(options)
            elif key == b'\r':  # Enter key
                return options[current_selection]
    def fight(self,enemy,next_action_after_fight):
        difficult_key = {'Easy':0.75,'Medium':1,'Hard':1.25}
        print("You engage in combat!")
        while enemy.hp > 0:
            print(f"Enemy Health: {enemy.hp}")
            print("Choose your action:")
            time.sleep(3)
            options = ["Attack", "Defend", "Use Item", "Run"]
            choice = self.interactive_menu(options)
            if choice == "Attack":
                damage = self.current_sword['hand damage'] * round(min(max(0.75,random.random()+0.25),1.25),0) if self.current_sword else 3
                enemy.hp -= damage
                print(f"You attack the enemy for {damage} damage!")
            elif choice == "Defend":
                print("You brace yourself for the enemy's attack!")

            elif choice == "Use Item":
                print("You rummage through your inventory for an item to use.")
            else:
                print("You attempt to flee from the combat!")
                if random.random() < 0.5:
                    print("You successfully escaped!")
                    return
                else:
                    print("You failed to escape!")
                    print("The enemy attacks you as you try to flee!")

                    enemy_damage = enemy.dmg * round(min(max(0.75,random.random()+0.25),1.25),0) * difficult_key[self.difficulty] * 1.5
                    print(f"The enemy attacks you for {enemy_damage} damage!")
                    self.hp -= enemy_damage
                    print(f"Your Health: {self.hp}")
                    continue
            enemy_damage = enemy.dmg * round(min(max(0.75,random.random()+0.25),1.25),0) * difficult_key[self.difficulty]
            print(f"The enemy attacks you for {enemy_damage} damage!")
            self.hp -= enemy_damage
            print(f"Your Health: {self.hp}")
            if self.hp <= 0:
                print("You got defeated!")
                print("You Lose all your gold to the bandit")
                self.gold = 0
                time.sleep(3)
                self.last_checkpoint()

        print("You have defeated the enemy!")
        print(f"you gained {enemy.loot} gold from the enemy")
        self.gold += enemy.loot
        print(f"you now have {self.gold} gold")
        next_action_after_fight()
    def use_health_potion(self,level):
        levels = [5,7,10,15,20,30]
        self.hp  = min(self.max_hp, self.hp + levels[level-1])

    def inn_scence(self):
        print("what do you do?")
        time.sleep(3)
        options = ["Rest for 5 gold","See inventory", "Leave the inn"]
        choice = self.interactive_menu(options)
        if choice == "Rest for 5 gold":
            if self.gold >= 5:
                self.gold -= 5
                self.hp = self.max_hp
                print("You rest at the inn and recover your health.")
            else:
                print("You don't have enough gold to rest at the inn.")
            self.inn_scence()
        elif choice == "See inventory":
            print("Your inventory:")
            for item in self.inventory:
                print(f"- {item}")
            print(f"- Gold: {self.gold}")
            print("Do you want to equip an item?")
            time.sleep(3)
            options = ["Yes","No"]
            equip_choice = self.interactive_menu(options)
            time.sleep(5)
            if equip_choice == "Yes":
                print("Which item do you want to equip?")
                time.sleep(3)
                sword_options = [item for item in self.inventory if item in self.swords_powers]
                if not sword_options:
                    print("You have no swords to equip.")
                    self.inn_scence()
                sword_choice = self.interactive_menu(sword_options)
                self.current_sword = self.swords_powers[sword_choice]
                print(f"You have equipped the {sword_choice}.")
            self.inn_scence()
        else:
            print("You leave the inn.")
            self.last_checkpoint()

    def start_game(self):
        print("Game started!")
        print("You are in a forest, you dont know where you are and you have to find your way out.")
        print("You see a path to the north and a river to the east.")
        print("Which way do you go?")
        time.sleep(3)
        options = ["Go North", "Go East"]
        choice = self.interactive_menu(options)
        if choice == "Go North":
            print("You walk north and find a village.")
            self.village_act1()
        else:
            print("You follow the river and find a bridge.")
    def village_act1(self):
        print("Game saving")
        self.last_checkpoint = self.village_act1
        time.sleep(5)
        print("saved as checkpoint")
        print("You enter the village and see some people there")
        print("you ask them where you are")
        print("he says:'you are in the village of straws men'")
        print("he says:'be careful there are bandits around'")
        print("What do you do?")
        while True:
            time.sleep(3)
            options = ["ask the villager about the bandits", "ask him for a weapon","leave the villager"]
            choice = self.interactive_menu(options)
            if choice == "ask the villager about the bandits":
                print("he says:'the bandits have been attacking travelers on the road to the north")
                print("they are dangerous and well armed'")
                print("they use knifes to attack the wandering travelers'")
            elif choice == "ask him for a weapon":
                print("he gives you a sword")
                self.inventory.append('broken sword')
                print("he says: 'use it well traveler")
                print("no one will help you out here'")
            else:
                print("you leave the villager and head back to the village")
                break
        print("You head back to the village center.")
        print("you see a Blacksmith, a Tavern, a forest, an inn, the villager from before and a Market")
        print("which way do you head?")
        time.sleep(3)
        options = ["Go to the Blacksmith", "Go to the Tavern", "Go to the Market", "Talk to the Villager again","Go to rest at an inn", "Go to the forest"]
        choice = self.interactive_menu(options)
        if choice == "Go to the Blacksmith":
            self.village_act2()
        elif choice == "Go to the Tavern":
            print("You head to the Tavern.")
            self.tavern_act1()
        elif choice == "Go to the Market":
            print("You head to the Market.")
            self.market_act1()
        elif choice == "Go to the forest":
            self.forest_act1()
        elif choice == "Go to rest at an inn":
            print("You head to the inn to rest")
            self.inn_scence()
        else:
            self.village_act1()
    def village_act2(self):
        print("You head to the Blacksmith.")
        print("He greets you and offers to sell you some weapons.")
        print("What do you do?")
        time.sleep(3)
        options = ["Buy a weapon", "Leave the Blacksmith"]
        choice = self.interactive_menu(options)
        if choice == "Buy a weapon":
            print("The blacksmith shows you his swords.")
            print("What do you do?")
            time.sleep(3)
            options = ["Buy a broken sword for 10 gold","Buy a normal sword for 25 gold", "Leave the Blacksmith"]
            choice = self.interactive_menu(options)
            if choice == "Buy a broken sword for 10 gold":
                if self.gold >=10:
                    self.gold -= 10
                    print("You buy the broken sword.")
                    self.inventory.append('broken sword')
                    self.village_act2()
                else:
                    print("You don't have enough gold to buy the broken sword.")
                    print("The blacksmith laughs and says: 'Come back when you have enough gold! broke boy'")
                    self.village_act2()
                    time.sleep(5)
            elif choice == "Buy a normal sword for 25 gold":
                if self.gold >= 25:
                    self.gold -= 25
                    print("You buy the normal sword.")
                    self.inventory.append('normal sword')
                    self.village_act2()
                else:
                    print("You don't have enough gold to buy the normal sword.")
                    print("The blacksmith glares at you and says: 'Get out of my shop you poor fool!'")
                    self.village_act2()
            else:
                print("You leave the Blacksmith.")
                self.village_act1()
        else:
            print("You leave the Blacksmith.")
            self.village_act1()
    def tavern_act1(self):
        print("You head to the Tavern.")
        print("The tavern is bustling with activity.")
        print("What do you do?")
        time.sleep(5)
        options = ["Talk to the bartender", "Talk to a patron", "Leave the Tavern"]
        choice = self.interactive_menu(options)
        if choice == "Talk to the bartender":
            print("The bartender tells you about the bandits.")
            self.tavern_act1()
        elif choice == "Talk to a patron":
            print("The patron shares a story about a hidden treasure.")
            self.tavern_act1()
        else:
            print("You leave the Tavern.")
            self.village_act1()
    def market_act1(self):
        print("You head to the Market.")
        print("The market is lively with merchants and buyers.")
        print("What do you do?")
        time.sleep(5)
        options = ["Buy supplies", "Sell items", "Leave the Market"]
        choice = self.interactive_menu(options)
        if choice == "Buy supplies":
            print("The merchant shows you his wares.")
            print("What do you do?")
            time.sleep(3)
            options = ["Buy a health potion for 15 gold","Buy a stamina potion for 10 gold", "Leave the Market"]
            choice = self.interactive_menu(options)
            if choice == "Buy a health potion for 15 gold":
                if self.gold >= 15:
                    self.gold -= 15
                    self.inventory.append('health potion')
                    print("You buy a health potion.")
                else:
                    print("You don't have enough gold to buy a health potion.")
                    print("The merchant shakes his head and says: 'Come back when you have enough gold! you broke fool'")
            elif choice == "Buy a stamina potion for 10 gold":
                if self.gold >= 10:
                    self.gold -= 10
                    self.inventory.append('stamina potion')
                    print("You buy a stamina potion.")
                else:
                    print("You don't have enough gold to buy a stamina potion.")
                    print("The merchant frowns and says: 'Get out of my shop you poor fool!'")
            else:
                print("You leave the Market.")
                self.village_act1()
            self.market_act1()
            
        elif choice == "Sell items":
            print("You look through your inventory to sell items.")
            if not self.inventory:
                print("You have no items to sell.")
            else:
                print("Your inventory:")
                for i, item in enumerate(self.inventory):
                    choice.append(f"{i + 1}. {item}")
                choice.append("Leave the Market")
                time.sleep(3)
                sell_choice = self.interactive_menu(choice)
                if sell_choice == "Leave the Market":
                    print("You leave the Market.")
                else:
                    item_index = int(sell_choice.split(".")[0]) - 1
                    item_to_sell = self.inventory[item_index]
                    if item_to_sell == 'broken sword':
                        self.gold += 5
                        print("You sold the broken sword for 5 gold.")
                    elif item_to_sell == 'normal sword':
                        self.gold += 15
                        print("You sold the normal sword for 15 gold.")
                    elif item_to_sell == 'health potion':
                        self.gold += 7
                        print("You sold the health potion for 7 gold.")
                    elif item_to_sell == 'stamina potion':
                        self.gold += 5
                        print("You sold the stamina potion for 5 gold.")
                    self.inventory.remove(item_to_sell)
            self.market_act1()
        else:
            print("You leave the Market.")
            self.village_act1()
    def forest_act1(self):
        print("You enter the forest")
        print("The forest is dark and eerie")
        print("Suddenly, a bandit jumps out from behind a tree!")
        bandit = Enemy(loot=5,dmg=2,special='steal',health=6)
        bandit.shout()
        self.fight(bandit,self.village_act3)
    def village_act3(self):
        print("You see a new village ahead")
        print("You enter the village and see some people there")
        print("you ask them where you are")
        print("They say: 'You are in the village of Oakwood'")
        print("What do you do?")
        time.sleep(5)
        options = ["Talk to the villagers", "Explore the village", "Leave the village and return to the forest"]
        choice = self.interactive_menu(options)
        if choice == "Talk to the villagers":
            print("The villagers tell you about the dangers ahead.")
            self.village_act3()
        elif choice == "Explore the village":
            print("You head to the village center.")
            self.village_act4()
        else:
            print("You leave the village.")
            self.forest_act1()
    def village_act4(self):
        print("Saving game")
        self.last_checkpoint = self.village_act3
        time.sleep(5)
        print("saved as checkpoint")
        print("You see a Blacksmith, a Tavern, an inn, and a Market")
        print("which way do you head?")
        time.sleep(3)
        options = ["Go to the Blacksmith", "Go to the Tavern", "Go to the Market", "Go to rest at an inn","Fight other bandits in the previous forest", "Go to the forest"]
        choice = self.interactive_menu(options)
        if choice == "Go to the Blacksmith":
            self.village_act5()
        elif choice == "Go to the Tavern":
            print("You head to the Tavern.")
            self.tavern_act2()
        elif choice == "Go to the Market":
            print("You head to the Market.")
            self.market_act2()
        elif choice == "Go to the forest":
            self.forest_act2()
        elif choice == "Fight other bandits in the previous forest":
            self.forest_act1()
        else:
            print("You head to the inn to rest")
            self.inn_scence()
    def village_act5(self):
        print("You head to the Blacksmith.")
        print("He greets you and offers to sell you some weapons.")
        print("What do you do?")
        time.sleep(3)
        options = ["Buy a weapon", "Leave the Blacksmith"]
        choice = self.interactive_menu(options)
        if choice == "Buy a weapon":
            print("The blacksmith shows you his swords.")
            print("What do you do?")
            time.sleep(3)
            options = ["Buy a broken sword for 3 gold","Buy a normal sword for 17 gold","Buy a long sword for 50 gold","Buy a great sword for 100 gold", "Leave the Blacksmith"]
            choice = self.interactive_menu(options)
            if choice == "Buy a broken sword for 3 gold":
                if self.gold >= 3:
                    self.gold -= 3
                    print("You buy the broken sword.")
                    self.inventory.append('broken sword')
                    self.village_act5()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.village_act5()
            elif choice == "Buy a normal sword for 17 gold":
                if self.gold >= 17:
                    self.gold -= 17
                    print("You buy the normal sword.")
                    self.inventory.append('normal sword')
                    self.village_act5()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.village_act5()
            elif choice == "Buy a long sword for 50 gold":
                if self.gold >= 50:
                    self.gold -= 50
                    print("You buy the long sword.")
                    self.inventory.append('long sword')
                    self.village_act5()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.village_act5()
            elif choice == "Buy a great sword for 100 gold":
                if self.gold >= 100:
                    self.gold -= 100
                    print("You buy the great sword.")
                    self.inventory.append('great sword')
                    self.village_act5()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.village_act5()
            else:
                print("You leave the Blacksmith.")
                self.village_act4()
        else:
            print("You leave the Blacksmith.")
            self.village_act4()
    def tavern_act2(self):
        print("You head to the tavern")
        print("The tavern is full of action")
        print("What do you do?")
        time.sleep(5)
        options = ["Talk to the bartender", "Talk to a patron", "Leave the Tavern"]
        choice = self.interactive_menu(options)
        if choice == "Talk to the bartender":
            print("The bartender tells you about the bandits.")
            self.tavern_act2()
        elif choice == "Talk to a patron":
            print("The patron shares a story about a hidden treasure.")
            self.tavern_act2()
        else:
            print("You leave the Tavern.")
            self.village_act4()
    def market_act2(self):
        print("You head to the Market.")
        print("The market is lively with merchants and buyers.")
        print("What do you do?")
        time.sleep(5)
        options = ["Buy supplies", "Sell items", "Leave the Market"]
        choice = self.interactive_menu(options)
        if choice == "Buy supplies":
            print("The merchant shows you his items")
            print("What do you do?")
            time.sleep(3)
            options = ["Buy a health potion for 13 gold","Buy a stamina potion for 8 gold", "Leave the Market"]
            choice = self.interactive_menu(options)
            if choice == "Buy a health potion for 13 gold":
                if self.gold >= 13:
                    self.gold -= 13
                    print("You buy a health potion.")
                    self.inventory.append('health potion')
                else:
                    print("You don't have enough gold to buy a health potion.")
                    print("The merchant shakes his head and says: 'Come back when you have enough gold! you broke fool'")
            elif choice == "Buy a stamina potion for 8 gold":
                if self.gold >= 8:
                    self.gold -= 8
                    print("You buy a stamina potion.")
                    self.inventory.append('stamina potion')
                else:
                    print("You don't have enough gold to buy a stamina potion.")
                    print("The merchant frowns and says: 'Get out of my shop you poor fool!'")
            else:
                print("You leave the Market.")
                self.village_act4()
        elif choice == "Sell items":
            print("Still developing")
            self.market_act2()
        else:
            print("You leave the Market.")
            self.village_act4()
    def forest_act2(self):
        print("You enter the forest")
        print("The forest is dark and eerie")
        print("Suddenly, a bandit jumps out from behind a tree!")
        print("He shouts at you:'You killed my brother, now you will pay!'")
        bandit = Enemy(loot=10,dmg=4,special='steal',health=12)
        bandit.shout()
        self.fight(bandit,self.village_act6)
    def village_act6(self):
        print("You see a new village ahead")
        print("You enter the village and see some people there")
        print("you ask them where you are")
        print("They say: 'You are in the village of Pinehill'")
        print("What do you do?")
        time.sleep(5)
        options = ["Talk to the villagers", "Explore the village", "Leave the village and return to the forest"]
        choice = self.interactive_menu(options)
        if choice == "Talk to the villagers":
            print("The villagers tell you about the dangers ahead.")
            self.village_act6()
        elif choice == "Explore the village":
            print("You head to the village center.")
            self.village_act7()
        else:
            print("You leave the village.")
            self.forest_act2()
    def village_act7(self):
        print("Saving game")
        self.last_checkpoint = self.village_act6
        time.sleep(5)
        print("saved as checkpoint")
        print("You see a Blacksmith, a Tavern, an inn, and a Market")
        print("which way do you head?")
        time.sleep(3)
        options = ["Go to the Blacksmith", "Go to the Tavern", "Go to the Market", "Go to rest at an inn","Fight other bandits in the previous forest", "Go to the forest"]
        choice = self.interactive_menu(options)
        if choice == "Go to the Blacksmith":
            self.village_act8()
        elif choice == "Go to the Tavern":
            print("You head to the Tavern.")
            self.tavern_act3()
        elif choice == "Go to the Market":
            print("You head to the Market.")
            self.market_act3()
        elif choice == "Go to the forest":
            self.forest_act3()
        elif choice == "Fight other bandits in the previous forest":
            self.forest_act2()
        else:
            print("You head to the inn to rest")
            self.inn_scence()
            
    

    





    def settings(self):
        print("Settings menu")
        print("1. Change difficulty")
        print("2. Adjust volume")
        print("3. Back to main menu")
        time.sleep(3)
        options = ["Change difficulty", "Adjust volume", "Back to main menu"]
        choice = self.interactive_menu(options)
        if choice == "Change difficulty":
            time.sleep(3)
            options = ["Easy", "Medium", "Hard"]
            self.difficulty = self.interactive_menu(options)
            print(f"Difficulty set to {self.difficulty}!")
        elif choice == "Adjust volume":
            volume_levels = [str(i) for i in range(10,-1,-1)]
            self.volume = int(self.selection_only_interactive_menu(volume_levels))
            test_sound = pygame.mixer.Sound("test sound.mp3")
            test_sound.set_volume(self.volume / 10)
            test_sound.play()

            print(f"Volume set to {self.volume}!")
        else:
            return

if __name__ == "__main__":
    
    game = Game()
    
