import os
import msvcrt 
import time
import random
import pygame
import sys

pygame.init()
pygame.mixer.init()


class Enemy:
    def __init__(self,loot,dmg,special,health,agility = 0.025,extra_loot_odds = None):
        self.loot = loot
        self.dmg = dmg
        self.special = special
        self.hp = health
        self.agility = agility
        self.extra_loot_odds = extra_loot_odds
    def shout(self):
        shouts = []
        shouts.append("You dare challenge me?")
        shouts.append("Prepare to meet your doom!")
        shouts.append("I will crush you!")
        shouts.append("You are no match for me!")
        print(shouts[random.randint(0,len(shouts)-1)])

class ArmoredEnemy(Enemy):
    def __init__(self,loot,dmg,special,health,armor,extra_loot_odds=None):
        super().__init__(loot,dmg,special,health,0,extra_loot_odds)
        self.armor = armor
    
class Game:
    def __init__(self):
        d = {}
        try:
            with open("Last saved game.txt","r") as file:
                lines = file.read().splitlines()
                for line in lines:
                    key,value = line.split(":")
                    d[key] = value
        except FileNotFoundError:
            pass
        self.difficulty = d.get("difficulty","Medium")
        self.volume = int(d.get("volume",5))
        self.inventory = list(d.get("inventory",[]).split(",") if d.get("inventory") else [])
        self.gold = int(d.get("gold",0))
        self.swords_powers = {'broken sword':{'hand damage':5,'two hand damage':8,'special':'chance to miss','piercing':0.1},
                              'normal sword':{'hand damage':10,'two hand damage':15,'special':'none','piercing':0.25},
                              'long sword':{'hand damage':15,'two hand damage':25,'special':'armor piercing','piercing':0.5},
                              'great sword':{'hand damage':25,'two hand damage':40,'special':'bleed chance','piercing':0.75},
                              'dark sword':{'hand damage':40,'two hand damage':60,'special':'life steal','piercing':0.9}}
        

        self.items_effects = {'health potion':{self.use_health_potion},
                              'stamina potion':{self.use_stamina_potion},
                              'strength potion':{self.use_strength_potion}}
        

        self.market_prices = {'broken sword':10,
                                'normal sword':25,
                                'long sword':50,
                                'great sword':100,
                                'health potion':15,
                                'stamina potion':10,
                                'broken bones':5,
                                'magical sandwatch':200,
                                'wooden planks':8,
                                'cut limb':25}

        self.taken_upgrades = d.get("taken_upgrades",[]).split(",") if d.get("taken_upgrades") else []

        
        



        self.current_sword = d.get("current_sword",None)
        self.hp = int(d.get("hp",10))
        self.max_hp = int(d.get('max_hp',10))
        self.last_checkpoint = self.__getattribute__(d.get("last_checkpoint",None)) if d.get("last_checkpoint") else self.start_game
        self.agility = float(d.get("agility",5))
        self.sea_level = int(d.get("sea level",1))

        while True:
            time.sleep(3)
            menu_options = ["Option 1: Start Game", "Option 2: Settings", "Option 3: Exit"]
            selected_option = self.interactive_menu(menu_options)
            self.clear_console()
            if selected_option == "Option 1: Start Game":
                print("Starting the game...")
                self.last_checkpoint()
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
        if self.current_sword:
            self.current_sword['current hand damage'] = self.current_sword['hand damage'] if self.current_sword else 0
            self.current_sword['current two hand damage'] = self.current_sword['two hand damage'] if self.current_sword else 0
        self.current_agility = self.agility
        print("You engage in combat!")
        while enemy.hp > 0:
            print(f"Enemy Health: {enemy.hp}")
            print("Choose your action:")
            time.sleep(3)
            options = ["Attack", "Defend", "Use Item", "Run"]
            choice = self.interactive_menu(options)
            if choice == "Attack":
                if random.random() < enemy.agility/100:
                    print("The enemy dodged your attack!")
                    continue
                if self.current_sword.get('special') == 'chance to miss' and random.random() < 0.2:
                    print("Your attack missed due to the sword's flaw!")
                    print("The enemy counters")
                    enemy_damage = enemy.dmg * round(min(max(0.75,random.random()+0.25),1.25),0) * difficult_key[self.difficulty] * 0.75
                    print(f"The enemy attacks you for {enemy_damage} damage!")
                    self.hp -= enemy_damage
                    print(f"Your Health: {self.hp}")
                    continue
                if enemy.isinstance(ArmoredEnemy):
                    effective_damage = self.current_sword['current hand damage'] * (self.current_sword['piercing'] - enemy.armor)
                    damage = max(0, effective_damage) * round(min(max(0.75,random.random()+0.25),1.25),0) if self.current_sword else 3
                damage = self.current_sword['current hand damage'] * round(min(max(0.75,random.random()+0.25),1.25),0) if self.current_sword else 3
                enemy.hp -= damage
                print(f"You attack the enemy for {damage} damage!")
            elif choice == "Defend":
                print("You brace yourself for the enemy's attack!")
                enemy_damage = enemy.dmg * round(min(max(0.75,random.random()+0.25),1.25),0) * difficult_key[self.difficulty] * random.ranint(15,20)/100
                heal = self.max_hp * random.randint(5,15)/100
                self.hp += heal - enemy_damage
                print(f"You take {enemy_damage} while defending")
                print(f"While you heal {heal}")
                print(f"Your health: {self.hp}")
                if self.hp <= 0:
                    print("You got defeated!")
                    print("You Lose all your gold to the bandit")
                    self.gold = 0
                    time.sleep(3)
                    if self.last_checkpoint:
                        self.last_checkpoint()

            elif choice == "Use Item":
                print("You rummage through your inventory for an item to use.")
                options = [self.items_effects.keys()]
                item_choice = self.interactive_menu(options)
                if item_choice in self.items_effects:
                    self.items_effects[item_choice](level=1)
                    print(f"You used a {item_choice}.")
                    self.inventory.remove(item_choice)
            else:
                print("You attempt to flee from the combat!")
                if random.random() < 0.2 + (self.agility/100):
                    print("You successfully escaped!")
                    next_action_after_fight()
                else:
                    print("You failed to escape!")
                    print("The enemy attacks you as you try to flee!")

                    enemy_damage = enemy.dmg * round(min(max(0.75,random.random()+0.25),1.25),0) * difficult_key[self.difficulty] * 1.5
                    print(f"The enemy attacks you for {enemy_damage} damage!")
                    self.hp -= enemy_damage
                    print(f"Your Health: {self.hp}")
                    continue
            if random.random() < self.current_agility/100:
                print("You dodged the enemy's attack!")
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
                if self.last_checkpoint:
                    self.last_checkpoint()

        print("You have defeated the enemy!")
        print(f"you gained {enemy.loot} gold from the enemy")
        self.gold += enemy.loot
        print(f"you now have {self.gold} gold")
        if enemy.extra_loot:
            extra_loot_item = self.loot([(item,1) for item in enemy.extra_loot])
            print(f"You also found a {extra_loot_item} on the enemy!")
            self.inventory.append(extra_loot_item)
        next_action_after_fight()
    def use_health_potion(self,level):
        levels = [5,7,10,15,20,30]
        self.hp  = min(self.max_hp, self.hp + levels[level-1])
    def use_strength_potion(self,level):
        levels = [2,3,5,7,10,15]
        if self.current_sword:
            self.current_sword['current hand damage'] += levels[level-1]
            self.current_sword['current two hand damage'] += levels[level-1] * 1.5
    def use_stamina_potion(self,level):
        levels = [2,3,5,7,10,15]
        self.current_agility += levels[level-1]
    
    def loot(self,items):
        upper_ends = {}
        lower_ends = {}
        last_end = 0
        for key,value in items:
            lower_ends[key] = last_end
            upper_ends[key] = last_end + value
            last_end += value
        rand_num = random.randint(0,last_end-1)
        for key in items:
            if lower_ends[key] <= rand_num < upper_ends[key]:
                return key
    

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
        with open("Last saved game.txt","w") as file:
            file.write(f"difficulty:{self.difficulty}\n")
            file.write(f"volume:{self.volume}\n")
            file.write(f"inventory:{','.join(self.inventory)}\n")
            file.write(f"gold:{self.gold}\n")
            file.write(f"current_sword:{self.current_sword}\n")
            file.write(f"hp:{self.hp}\n")
            file.write(f"max_hp:{self.max_hp}\n")
            file.write(f"last_checkpoint:{self.last_checkpoint}\n")
            file.write(f"taken_upgrades:{self.taken_upgrades}\n")
            file.write(f"agility:{self.agility}\n")
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
            self.blacksmit_act1()
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
    def blacksmit_act1(self):
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
                    self.blacksmit_act1()
                else:
                    print("You don't have enough gold to buy the broken sword.")
                    print("The blacksmith laughs and says: 'Come back when you have enough gold! broke boy'")
                    self.blacksmit_act1()
                    time.sleep(5)
            elif choice == "Buy a normal sword for 25 gold":
                if self.gold >= 25:
                    self.gold -= 25
                    print("You buy the normal sword.")
                    self.inventory.append('normal sword')
                    self.blacksmit_act1()
                else:
                    print("You don't have enough gold to buy the normal sword.")
                    print("The blacksmith glares at you and says: 'Get out of my shop you poor fool!'")
                    self.blacksmit_act1()
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
            print("The bartender tells you a tale:")
            print("A traveler once got lost, finding two paths. He fought bandits in forests with swords and items,")
            print("using gold to buy better gear. Along the way, he discovered new villages and learned about this mysterious place.")
            if '1st health upgrade' not in self.taken_upgrades:
                print("He says 'young man, would you like to learn how to be more durable?")
                options = ["Yes for 25 gold","No"]
                teach_choice = self.interactive_menu(options)
                if teach_choice == "Yes for 25 gold":
                    if self.gold >= 25:
                        self.max_hp += 5
                        print("The bartender teaches you how to be more durable. Your max HP increases by 5")
                        self.taken_upgrades.append('1st health upgrade')
                    else:
                        print("You don't have enough gold to learn this skill")
                else:
                    print("The bartender shrugs and goes back to cleaning glasses")
                

            self.tavern_act1()
        elif choice == "Talk to a patron":
            print("A patron nods and adds to the tale:")
            print("He fought bandits in forests with swords and items, using gold to buy better gear.")
            print("Along the way, he discovered new villages and learned about this mysterious place.")
            if '1st agility upgrade' not in self.taken_upgrades:
                print("He says: 'hey bud, want me to teach you how to be more agile?'")
                options = ["Yes for 20 gold","No"]
                teach_choice = self.interactive_menu(options)
                if teach_choice == "Yes for 20 gold":
                    if self.gold >= 20:
                        self.gold -= 20
                        print("The patron teaches you how to be more agile. Your chance to dodge increases by 5%")
                        self.taken_upgrades.append('1st agility upgrade')
                    else:
                        print("You don't have enough gold to learn this skill")
                else:
                    print("The patron shrugs and goes back to his drink")
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
                    if item_to_sell in self.market_prices:
                        sell_price = self.market_prices[item_to_sell]
                        self.gold += sell_price
                        print(f"You sold {item_to_sell} for {sell_price} gold")
                        self.inventory.remove(item_to_sell)
                    else:
                        print(f"The merchant is not interested in buying {item_to_sell}")
                    
            self.market_act1()
        else:
            print("You leave the Market.")
            self.village_act1()
    def forest_act1(self):
        print("You enter the forest")
        print("The forest is dark and eerie")
        print("Suddenly, a bandit jumps out from behind a tree!")
        bandit = Enemy(loot=random.randint(4,6),dmg=2,special='steal',health=6,extra_loot_odds={'health potion':6,'stamina potion':4,'broken bones':10,'normal sword':2,'wooden planks':2})
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
        with open("Last saved game.txt","w") as file:
            file.write(f"difficulty:{self.difficulty}\n")
            file.write(f"volume:{self.volume}\n")
            file.write(f"inventory:{','.join(self.inventory)}\n")
            file.write(f"gold:{self.gold}\n")
            file.write(f"current_sword:{self.current_sword}\n")
            file.write(f"hp:{self.hp}\n")
            file.write(f"max_hp:{self.max_hp}\n")
            file.write(f"last_checkpoint:{self.last_checkpoint}\n")
            file.write(f"taken_upgrades:{self.taken_upgrades}\n")
            file.write(f"agility:{self.agility}\n")



        time.sleep(5)
        print("saved as checkpoint")
        print("You see a Blacksmith, a Tavern, an inn, and a Market")
        print("which way do you head?")
        time.sleep(3)
        options = ["Go to the Blacksmith", "Go to the Tavern", "Go to the Market", "Go to rest at an inn","Fight other bandits in the previous forest", "Go to the forest"]
        choice = self.interactive_menu(options)
        if choice == "Go to the Blacksmith":
            self.blacksmit_act2()
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
    def blacksmit_act2(self):
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
                    self.blacksmit_act2()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act2()
            elif choice == "Buy a normal sword for 17 gold":
                if self.gold >= 17:
                    self.gold -= 17
                    print("You buy the normal sword.")
                    self.inventory.append('normal sword')
                    self.blacksmit_act2()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act2()
            elif choice == "Buy a long sword for 50 gold":
                if self.gold >= 50:
                    self.gold -= 50
                    print("You buy the long sword.")
                    self.inventory.append('long sword')
                    self.blacksmit_act2()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act2()
            elif choice == "Buy a great sword for 100 gold":
                if self.gold >= 100:
                    self.gold -= 100
                    print("You buy the great sword.")
                    self.inventory.append('great sword')
                    self.blacksmit_act2()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act2()
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
            print("The bartender continues the story:")
            print("His mission was to return to his main city after finding the shore, building a ship, and acquiring a map.")
            print("On his journey, he encountered pirates, sea monsters, and other creatures, often needing to rest on nearby islands.")
            if '2nd health upgrade' not in self.taken_upgrades:
                print("He says: 'hey man, want me to teach you how to be more durable?'")
                options = ["Yes for 25 gold","No"]
                teach_choice = self.interactive_menu(options)
                if teach_choice == "Yes for 25 gold":
                    if self.gold >= 25:
                        self.max_hp += 5
                        print("The bartender teaches you how to be more durable. Your max HP increases by 5")
                        self.taken_upgrades.append("2nd health upgrade")
                    else:
                        print("You don't have enough gold to learn this skill")
                else:
                    print("The bartender shrugs and goes back to cleaning glasses")
                self.tavern_act2()
        elif choice == "Talk to a patron":
            print("A patron chimes in:")
            print("On his journey, he encountered pirates, sea monsters, and other creatures, often needing to rest on nearby islands.")
            if '2nd agility upgrade' not in self.taken_upgrades:
                print("He says: 'hey bud, want me to teach you how to be more agile?'")
                options = ["Yes for 20 gold","No"]
                teach_choice = self.interactive_menu(options)
                if teach_choice == "Yes for 20 gold":
                    if self.gold >= 20:
                        self.gold -= 20
                        print("The patron teaches you how to be more agile. Your chance to dodge increases by 5%")
                        self.taken_upgrades.append("2nd agility upgrade")
                    else:
                        print("You don't have enough gold to learn this skill")
                else:
                    print("The patron shrugs and goes back to his drink")
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
            print("You look through your inventory to sell items.")
            if not self.inventory:
                print("You dont have anything to sell")
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
                    if item_to_sell in self.market_prices:
                        sell_price = self.market_prices[item_to_sell]
                        self.gold += sell_price
                        print(f"You sold {item_to_sell} for {sell_price} gold")
                        self.inventory.remove(item_to_sell)
                    else:
                        print(f"The merchant is not interested in buying {item_to_sell}")
                    
            self.market_act2()
        else:
            print("You leave the Market.")
            self.village_act4()
    def forest_act2(self):
        print("You enter the forest")
        print("The forest is dark and eerie")
        print("Suddenly, a bandit jumps out from behind a tree!")
        print("He shouts at you:'You killed my brother, now you will pay!'")
        bandit = Enemy(loot=random.randint(8,12),dmg=5,special='steal',health=12,extra_loot_odds={'health potion':5,'stamina potion':5,'broken bones':8,'normal sword':4,'wooden planks':3})
        bandit.shout()
        self.fight(bandit,self.village_act6)
    def village_act6(self):
        print("You see a new village ahead")
        print("saving game...")
        self.last_checkpoint = self.village_act6
        with open("Last saved game.txt","w") as file:
            file.write(f"difficulty:{self.difficulty}\n")
            file.write(f"volume:{self.volume}\n")
            file.write(f"inventory:{','.join(self.inventory)}\n")
            file.write(f"gold:{self.gold}\n")
            file.write(f"current_sword:{self.current_sword}\n")
            file.write(f"hp:{self.hp}\n")
            file.write(f"max_hp:{self.max_hp}\n")
            file.write(f"last_checkpoint:{self.last_checkpoint}\n")
            file.write(f"taken_upgrades:{self.taken_upgrades}\n")
            file.write(f"agility:{self.agility}\n")
        time.sleep(5)
        print("saved as checkpoint")
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
        with open("Last saved game.txt","w") as file:
            file.write(f"difficulty:{self.difficulty}\n")
            file.write(f"volume:{self.volume}\n")
            file.write(f"inventory:{','.join(self.inventory)}\n")
            file.write(f"gold:{self.gold}\n")
            file.write(f"current_sword:{self.current_sword}\n")
            file.write(f"hp:{self.hp}\n")
            file.write(f"max_hp:{self.max_hp}\n")
            file.write(f"last_checkpoint:{self.last_checkpoint}\n")
            file.write(f"taken_upgrades:{self.taken_upgrades}\n")
            file.write(f"agility:{self.agility}\n")

        time.sleep(5)
        print("saved as checkpoint")
        print("You see a Blacksmith, a Tavern, an inn, and a Market")
        print("which way do you head?")
        time.sleep(3)
        options = ["Go to the Blacksmith", "Go to the Tavern", "Go to the Market", "Go to rest at an inn","Fight other bandits in the previous forest", "Go to the forest"]
        choice = self.interactive_menu(options)
        if choice == "Go to the Blacksmith":
            self.blacksmit_act3()
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
    def blacksmit_act3(self):
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
            options = ["Buy a broken sword for 2 gold","Buy a normal sword for 10 gold","Buy a long sword for 30 gold","Buy a great sword for 70 gold", "Leave the Blacksmith"]
            choice = self.interactive_menu(options)
            if choice == "Buy a broken sword for 2 gold":
                if self.gold >= 2:
                    self.gold -= 2
                    print("You buy the broken sword.")
                    self.inventory.append('broken sword')
                    self.blacksmit_act3()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act3()
            elif choice == "Buy a normal sword for 10 gold":
                if self.gold >= 10:
                    self.gold -= 10
                    print("You buy the normal sword")
                    self.inventory.append('normal sword')
                    self.blacksmit_act3()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act3()
            elif choice == "Buy a long sword for 30 gold":
                if self.gold >= 30:
                    self.gold -= 30
                    print("You buy the long sword.")
                    self.inventory.append('long sword')
                    self.blacksmit_act3()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act3()
            elif choice == "Buy a great sword for 70 gold":
                if self.gold >= 70:
                    self.gold -= 70
                    print("You buy the great sword.")
                    self.inventory.append('great sword')
                    self.blacksmit_act3()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act3()
            else:
                print("You leave the Blacksmith.")
                self.village_act7()
        else:
            print("You leave the Blacksmith.")
            self.village_act7()
    def tavern_act3(self):
        print("You head to the tavern")
        print("The tavern is full of action")
        print("What do you do?")
        time.sleep(5)
        options = ["Talk to the bartender", "Talk to a patron", "Leave the Tavern"]
        choice = self.interactive_menu(options)
        if choice == "Talk to the bartender":
            print("The bartender concludes the legend:")
            print("After returning, his story lived on for a long time as the man who came back after his memorial.")
            print("He became a symbol of patience and hard work in his village.")
            if '3rd health upgrade' not in self.taken_upgrades:
                print("He says: 'hey bro, do you want me to teach you how to be more durable?'")
                options = ["Yes for 25 gold","No"]
                teach_choice = self.interactive_menu(options)
                if teach_choice == "Yes for 25 gold":
                    if self.gold >= 25:
                        self.max_hp += 5
                        print("The bartender teaches you how to be more durable. Your max HP increases by 5")
                        self.taken_upgrades.append("3rd health upgrade")
                    else:
                        print("You don't have enough gold to learn this skill")
                else:
                    print("The bartender shrugs and goes back to cleaning glasses")
            self.tavern_act3()
        elif choice == "Talk to a patron":
            print("A wise old patron adds:")
            print("He became a symbol of patience and hard work in his village, his story living on for a long time.")
            if '3rd agility upgrade' not in self.taken_upgrades:
                print("He says: 'hey mate, do you want me to teach you how to be more agile?'")
                options = ["Yes for 20 gold","No"]
                teach_choice = self.interactive_menu(options)
                if teach_choice == "Yes for 20 gold":
                    if self.gold >= 20:
                        self.gold -= 20
                        print("The patron teaches you how to be more agile. Your chance to dodge increases by 5%")
                        self.taken_upgrades.append("3rd agility upgrade")
                    else:
                        print("You don't have enough gold to learn this skill")
                else:
                    print("The patron shrugs and goes back to his drink")
            self.tavern_act3()
        else:
            print("You leave the Tavern.")
            self.village_act7()
    def market_act3(self):
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
            options = ["Buy a health potion for 10 gold","Buy a stamina potion for 5 gold", "Leave the Market"]
            choice = self.interactive_menu(options)
            if choice == "Buy a health potion for 10 gold":
                if self.gold >= 10:
                    self.gold -= 10
                    print("You buy a health potion.")
                    self.inventory.append('health potion')
                else:
                    print("You don't have enough gold to buy a health potion.")
                    print("The merchant shakes his head and says: 'Come back when you have enough gold! you broke fool'")
            elif choice == "Buy a stamina potion for 5 gold":
                if self.gold >= 5:
                    self.gold -= 5
                    print("You buy a stamina potion.")
                    self.inventory.append('stamina potion')
                else:
                    print("You don't have enough gold to buy a stamina potion.")
                    print("The merchant frowns and says: 'Get out of my shop you poor fool!'")
            else:
                print("You leave the Market")
                self.village_act7()
            self.market_act3()
        elif choice == "Sell items":
            print("You look through your inventory to sell items.")
            if not self.inventory:
                print("You dont have anything to sell")
            else:
                print("Your Inventory:")
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
                    if item_to_sell in self.market_prices:
                        sell_price = self.market_prices[item_to_sell]
                        self.gold += sell_price
                        print(f"You sold {item_to_sell} for {sell_price} gold")
                        self.inventory.remove(item_to_sell)
                    else:
                        print(f"The merchant is not interested in buying {item_to_sell}")
            self.market_act3()
        else:
            print("You leave the Market.")
            self.village_act7()
    def forest_act3(self):
        print("You enter the forest")
        print("The forest is dark and eerie")
        print("Suddenly, a bandit jumps out from behind a tree!")
        print("He shouts at you:'You killed my brother, now you will pay!'")
        bandit = Enemy(loot=random.randint(13,18),dmg=8,special='steal',health=20,extra_loot_odds = {'health potion':1,'stamina potion':1,'wooden planks':3}) if random.random() > 0.25 else ArmoredEnemy(loot=random.randint(15,20),dmg=6,special='steal',health=25,armor=0.1,extra_loot_odds={"health potion":4,"stamina potion":7,"wooden planks":3})
        bandit.shout()
        self.fight(bandit,self.village_act9)
    def village_act9(self):
        print("You see a new village ahead")
        print("You enter the village and see some people there")
        print("you ask them where you are")
        print("They say: 'You are in the village of Maplewood'")
        print("what do you do?")
        time.sleep(5)
        options = ["Talk to the villagers", "Explore the village", "Leave the village and return to the forest"]
        choice = self.interactive_menu(options)
        if choice == "Talk to the villagers":
            self.village_act9()
        elif choice == "Explore the village":
            print("You head to the village center.")
            self.village_act10()
        else:
            print("You leave the village.")
            self.forest_act3()
    def village_act10(self):
        print("You head to the village center")
        print("Saving game")
        self.last_checkpoint = self.village_act10
        with open("Last saved game.txt","w") as file:
            file.write(f"difficulty:{self.difficulty}\n")
            file.write(f"volume:{self.volume}\n")
            file.write(f"inventory:{','.join(self.inventory)}\n")
            file.write(f"gold:{self.gold}\n")
            file.write(f"current_sword:{self.current_sword}\n")
            file.write(f"hp:{self.hp}\n")
            file.write(f"max_hp:{self.max_hp}\n")
            file.write(f"last_checkpoint:{self.last_checkpoint}\n")
            file.write(f"taken_upgrades:{self.taken_upgrades}\n")
            file.write(f"agility:{self.agility}\n")
        time.sleep(5)
        print("saved as checkpoint")
        print("what do you do?")
        time.sleep(3)
        options = ["Go to the Blacksmith", "Go to the Tavern", "Go to the Market", "Go to rest at an inn","Fight other bandits in the previous forest", "Go to the forest"]
        choice = self.interactive_menu(options)
        if choice == "Go to the Blacksmith":
            self.blacksmit_act4()
        elif choice == "Go to the Tavern":
            print("You head to the Tavern.")
            self.tavern_act4()
        elif choice == "Go to the Market":
            print("You head to the Market.")
            self.market_act4()
        elif choice == "Go to the forest":
            self.forest_act4()
        elif choice == "Fight other bandits in the previous forest":
            self.forest_act3()
        else:
            print("You head to the inn to rest")
            self.inn_scence()
    def blacksmit_act4(self):
        print("You head to the Blacksmith.")
        print("He greets you and offers to sell you some weapons.")
        print("What do you do?")
        time.sleep(3)
        options = ["Buy a weapon", "Leave the Blacksmith"]
        choice = self.interactive_menu(options)
        if choice == "Buy a weapon":
            print("The blacksmith shows you his swords")
            print("what do you do?")
            time.sleep(3)
            options = ["Buy a broken sword for 1 gold","Buy a normal sword for 5 gold","Buy a long sword for 20 gold","Buy a great sword for 50 gold", "Leave the Blacksmith"]
            choice = self.interactive_menu(options)
            if choice == "Buy a broken sword for 1 gold":
                if self.gold >= 1:
                    self.gold -= 1
                    print("You buy the broken sword.")
                    self.inventory.append('broken sword')
                    self.blacksmit_act4()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act4()
            elif choice == "Buy a normal sword for 5 gold":
                if self.gold >= 5:
                    self.gold -= 5
                    print("You buy the normal sword.")
                    self.inventory.append('normal sword')
                    self.blacksmit_act4()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act4()
            elif choice == "Buy a long sword for 20 gold":
                if self.gold >= 20:
                    self.gold -= 20
                    print("You buy the long sword.")
                    self.inventory.append('long sword')
                    self.blacksmit_act4()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act4()
            elif choice == "Buy a great sword for 50 gold":
                if self.gold >= 50:
                    self.gold -= 50
                    print("You buy the great sword.")
                    self.inventory.append('great sword')
                    self.blacksmit_act4()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act4()
            else:
                print("You leave the Blacksmith.")

            self.blacksmit_act4()
        else:
            print("You leave the Blacksmith.")
            self.village_act10()
    def tavern_act4(self):
        print("You head to the tavern")
        print("The tavern is full of action")
        print("What do you do?")
        time.sleep(5)
        options = ["Talk to the bartender", "Talk to a patron", "Leave the Tavern"]
        choice = self.interactive_menu(options)
        if choice == "Talk to the bartender":
            print("The bartender tells you a tale:")
            print("Once a man set out on a journey to find a distant shore.")
            print("After facing numerous challenges, he finally reached his destination and built a ship to return home.")
            if '4th health upgrade' not in self.taken_upgrades:
                print("He says: 'so,do you want me to teach you how to be strong as him?'")
                options = ["Yes for 25 gold","No"]
                teach_choice = self.interactive_menu(options)
                if teach_choice == "Yes for 25 gold":
                    if self.gold >= 25:
                        self.max_hp += 5
                        print("The bartender teaches you how to be more durable. Your max HP increases by 5")
                        self.taken_upgrades.append("4th health upgrade")
                    else:
                        print("You don't have enough gold to learn this skill")
                else:
                    print("The bartender shrugs and goes back to cleaning glasses")
            self.tavern_act4()
        elif choice == "Talk to a patron":
            print("A patron nods and adds to the tale:")
            print("He faced numerous challenges, he finally reached his destination and built a ship to return home.")
            if '4th agility upgrade' not in self.taken_upgrades:
                print("He says: 'hey bud, want me to teach you how to be agile like him?'")
                options = ["Yes for 20 gold","No"]
                teach_choice = self.interactive_menu(options)
                if teach_choice == "Yes for 20 gold":
                    if self.gold >= 20:
                        self.gold -= 20
                        print("The patron teaches you how to be more agile. Your chance to dodge increases by 5%")
                        self.taken_upgrades.append("4th agility upgrade")
                    else:
                        print("You don't have enough gold to learn this skill")
                else:
                    print("The patron shrugs and goes back to his drink")
            self.tavern_act4()
        else:
            print("You leave the Tavern.")
            self.village_act10()
    def market_act4(self):
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
            options = ["Buy a health potion for 7 gold","Buy a stamina potion for 3 gold","Buy wooden planks for 10 gold", "Leave the Market"]
            choice = self.interactive_menu(options)
            if choice == "Buy a health potion for 7 gold":
                if self.gold >= 7:
                    self.gold -= 7
                    print("You buy a health potion.")
                    self.inventory.append('health potion')
                else:
                    print("You don't have enough gold to buy a health potion.")
                    print("The merchant shakes his head and says: 'Come back when you have enough gold! you broke fool'")
            elif choice == "Buy a stamina potion for 3 gold":
                if self.gold >= 3:
                    self.gold -= 3
                    print("You buy a stamina potion.")
                    self.inventory.append('stamina potion')
                else:
                    print("You don't have enough gold to buy a stamina potion.")
                    print("The merchant frowns and says: 'Get out of my shop you poor fool!'")
            elif choice == "Buy wooden planks for 10 gold":
                if self.gold >= 10:
                    self.gold -= 10
                    print("You buy wooden planks.")
                    self.inventory.append('wooden planks')
                else:
                    print("You don't have enough gold to buy wooden planks.")
                    print("The merchant frowns and says: 'Get out of my shop you poor fool!'")
            else:
                print("You leave the Market")
                self.village_act10()
            self.market_act4()
        elif choice == "Sell items":
            print("You look through your inventory to sell items.")
            if not self.inventory:
                print("You dont have anything to sell")
            else:
                print("Your Inventory:")
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
                    if item_to_sell in self.market_prices:
                        sell_price = self.market_prices[item_to_sell]
                        self.gold += sell_price
                        print(f"You sold {item_to_sell} for {sell_price} gold")
                        self.inventory.remove(item_to_sell)
                    else:
                        print(f"The merchant is not interested in buying {item_to_sell}")
            self.market_act4()
        else:
            print("You leave the Market.")
            self.village_act10()
    def forest_act4(self):
        print("You enter the forest")
        print("The forest is dark and eerie")
        print("Suddenly, a bandit jumps out from behind a tree!")
        print("He shouts at you:'You killed my brother, now you will pay!'")
        bandit = Enemy(loot=random.randint(15,25),dmg=10,special='steal',health=30,extra_loot_odds={'magical sandwatch':1,"health potion":5,"stamina potion":4,"wooden planks":6}) if random.random() > 0.35 else ArmoredEnemy(loot=random.randint(20,30),dmg=8,special='steal',health=35,armor=0.3,extra_loot_odds={'magical sandwatch':1,"health potion":4,"stamina potion":3,"wooden planks":5})
        bandit.shout()
        self.fight(bandit,self.shore_act1)
    def shore_act1(self):
        print("You find a shore ahead")
        print("Saving game...")
        with open("Last saved game","w") as file:
            file.write(f"difficulty:{self.difficulty}\n")
            file.write(f"volume:{self.volume}\n")
            file.write(f"inventory:{','.join(self.inventory)}\n")
            file.write(f"gold:{self.gold}\n")
            file.write(f"current_sword:{self.current_sword}\n")
            file.write(f"hp:{self.hp}\n")
            file.write(f"max_hp:{self.max_hp}\n")
            file.write(f"last_checkpoint:{self.last_checkpoint}\n")
            file.write(f"taken_upgrades:{self.taken_upgrades}\n")
            file.write(f"agility:{self.agility}\n")
        time.sleep(5)
        print("Saved as checkpoint")
        print("You find a Sailor next to a broken ship")
        print("'Hey, Stop where you are, bandit' shouted the Sailor")
        print("You raise your hands in the air and try to explain that you are not a bandit")
        print("He says 'why should i keep you alive then'")
        print("What do you do?")
        options = ["Challenge him to a duel","Say that you are here by accident","Say that you also want to go out of this mysterious island"]
        time.sleep(10)
        choice = self.interactive_menu(options)
        if choice == "Challege him to a duel":
            self.fight(ArmoredEnemy(150,20,'Critic',100,0.25,{'wooden planks':1,'dark sword':10}),self.evil_ending)
        elif choice == "Say that you are here by accident":
            print("He says: 'And why would you be here by accident!?'")
            print("You don`t seem friendly")
            self.shore_act1()
        else:
            print("'So you want to get out of here little boy?' says the Sailor")
            print("If you want to leave with me you will have to get me some planks so i can make this boat larger")
            print("so it can fit us both")
            print("i will need 25 planks and a compass")
            print("Get me these things and we can leave together")
            print("If you attempt to leave alone")
            print("I will just shoot you with my gun")
            print("I wont hesitate to fire it")
            time.sleep(15)
            self.shore_act2()
    def shore_act2(self):
        print("Saving game...")
        with open("Last_save_game","w") as file:
            file.write(f"difficulty:{self.difficulty}\n")
            file.write(f"volume:{self.volume}\n")
            file.write(f"inventory:{','.join(self.inventory)}\n")
            file.write(f"gold:{self.gold}\n")
            file.write(f"current_sword:{self.current_sword}\n")
            file.write(f"hp:{self.hp}\n")
            file.write(f"max_hp:{self.max_hp}\n")
            file.write(f"last_checkpoint:{self.last_checkpoint}\n")
            file.write(f"taken_upgrades:{self.taken_upgrades}\n")
            file.write(f"agility:{self.agility}\n")
        time.sleep(5)
        print("Saved as checkpoint")
        print("You see a market, a blacksmith, the sailor, and the forest to the east")
        print("What do you do?")
        time.sleep(5)
        options = ["Go to the market","Go to the black smith","Talk to the sailor","Go to the forest"]
        choice = self.interactive_menu(options)
        if choice == "Go to the market":
            self.market_act5()
        elif choice == "Go to the black smith":
            self.blacksmit_act5()
        elif choice == "Talk to the sailor":
            self.shore_act3()
        else:
            self.forest_act5()
    
    def forest_act5(self):
        print("You enter the forest")
        print("The forest is voidious")
        print("Suddenly, a bandit jumps out from behind a tree!")
        print("He shouts at you:'You killed my whole family, now you will pay!'")
        bandit = Enemy(loot=random.randint(30,40),dmg=20,special='steal',health=40,extra_loot_odds={"wooden planks":10,"health potion":5,"stamina potion":4,"cut limb":6}) if random.random() > 0.5 else ArmoredEnemy(loot=random.randint(50,60),dmg=15,special='steal',health=50,armor=0.5,extra_loot_odds={"wooden planks":20,"health potion":10,"stamina potion":8,"cut limb":12,"magical sandwatch":1})
        bandit.shout()
        self.fight(bandit,self.shore_act1)
    def market_act5(self):
        print("You head to the market")
        print("You see a merchant")
        time.sleep(3)
        print("What do you do?")
        options = ["Buy supplies","Sell items","Leave the market"]
        choice = self.interactive_menu(options)
        if choice == "Buy supplies":
            print("The merchant shows you his items")
            print("What do you do?")
            time.sleep(3)
            options = ["Buy a health potion for 7 gold","Buy a stamina potion for 4 gold","Buy wooden planks for 15 gold","Buy a magical sandwatch for 300 gold","Leave the market"]
            item_choice = self.interactive_menu(options)
            if item_choice == "Buy a health potion for 7 gold":
                if self.gold >= 7:
                    self.gold -= 7
                    print("You buy a health potion")
                    self.inventory.append("health potion")
                else:
                    print("You dont have enough gold to buy a health potion")
                    print("The merchant shakes his head and says: 'Come back when you have enough gold! you broke fool'")
            elif item_choice == "Buy a stamina potion for 4 gold":
                if self.gold >= 4:
                    self.gold -= 4
                    print("You buy a stamina potion")
                    self.inventory.append("stamina potion")
                else:
                    print("You dont have enough gold to buy a stamina potion")
                    print("The merchant shakes his head and says: 'Come back when you have enough gold! you broke fool'")
            elif item_choice == "Buy wooden planks for 15 gold":
                if self.gold >= 15:
                    self.gold -= 15
                    print("You buy wooden planks")
                    self.inventory.append("wooden planks")
                else:
                    print("You dont have enough gold to buy wooden planks")
            elif item_choice == "Buy a magical sandwatch for 300 gold":
                if "magical sandwatch" in self.inventory or "compass" in self.inventory:
                    print("The merchant says: 'I cant sell you this item but i can upgrade it to you to a compass for 150 gold'")
                    time.sleep(3)
                    upgrade_options = ["Yes for 150 gold","No"]
                    upgrade_choice = self.interactive_menu(upgrade_options)
                    if upgrade_choice == "Yes for 150 gold":
                        if self.gold >= 150:
                            self.gold -= 150
                            print("Upgraded your magical sandwatch to a compass")
                            self.inventory.remove("magical sandwatch")
                            self.inventory.append("compass")
                        else:
                            print("You dont have enough gold to upgrade the magical sandwatch")
                            print("The merchant shrugs and says: 'Come back when you have enough gold! you broke fool'")
                    else:
                        print("The merchant shrugs and shows you his items again")

                elif self.gold >= 300:
                    self.gold -= 300
                    print("You buy the magical sandwatch")
                    self.inventory.append("magical sandwatch")
                else:
                    print("You dont have enough gold to buy a magical sandwatch")
                    print("The merchant shakes his head and says: 'Come back when you have enough gold! you broke fool'")
            else:
                print("You leave the market")
                self.shore_act2()
        elif choice == "Sell items":
            print("You look through your inventory to sell items.")
            if not self.inventory:
                print("You dont have anything to sell")
            else:
                print("Your Inventory:")
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
                    if item_to_sell in self.market_prices:
                        sell_price = self.market_prices[item_to_sell]
                        self.gold += sell_price
                        print(f"You sold {item_to_sell} for {sell_price} gold")
                        self.inventory.remove(item_to_sell)
                    else:
                        print(f"The merchant is not interested in buying {item_to_sell}")
            self.market_act5()
        else:
            print("You leave the market")
            self.shore_act2()

    def blacksmit_act5(self):
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
            options = ["Buy a normal sword for 5 gold","Buy a long sword for 25 gold","Buy a great sword for 55 gold","Buy a dark sword for 250 gold", "Leave the Blacksmith"]
            choice = self.interactive_menu(options)
            if choice == "Buy a dark sword for 250 gold":
                if self.gold >= 250:
                    self.gold -= 250
                    print("You buy the dark sword.")
                    self.inventory.append('dark sword')
                    self.blacksmit_act5()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act5()
            elif choice == "Buy a normal sword for 5 gold":
                if self.gold >= 5:
                    self.gold -= 5
                    print("You buy the normal sword")
                    self.inventory.append('normal sword')
                    self.blacksmit_act5()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act5()
            elif choice == "Buy a long sword for 25 gold":
                if self.gold >= 25:
                    self.gold -= 25
                    print("You buy the long sword.")
                    self.inventory.append('long sword')
                    self.blacksmit_act5()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act5()
            elif choice == "Buy a great sword for 55 gold":
                if self.gold >= 55:
                    self.gold -= 55
                    print("You buy the great sword.")
                    self.inventory.append('great sword')
                    self.blacksmit_act5()
                else:
                    print("You dont have enough gold to buy this item")
                    print("The blacksmith says:'Go out of my shop, you poor fool!'")
                    self.blacksmit_act5()
            else:
                print("You leave the Blacksmith.")
                self.shore_act2()
        else:
            print("You leave the Blacksmith.")
            self.shore_act2()
    
    def shore_act3(self):
        print("You go back to the Sailor")
        print("'Did you get these planks i told you to get, young man?' shouts the Sailor")
        print("What do you do?")
        time.sleep(5)
        options = ["Yes","No"]
        choice = self.interactive_menu(options)
        if choice == "Yes":
            x = True
            if not self.planks_mission_done:
                for i in range(25):
                        try:
                            self.inventory.remove("wooden planks")
                        except ValueError:
                            for j in range(i):
                                self.inventory.append("wooden planks")
                            x = False
            if x or self.planks_mission_done:
                if not self.planks_mission_done:
                    for i in range(25):
                        try:
                            self.inventory.remove("wooden planks")
                        except ValueError:
                            self.inventory += ["wooden planks"]*i
                            x = False
                if "compass" in self.inventory:
                    print("Then lets start our journey")
                    print("You start sailing through the seas")
                    self.sea_act1()
                else:
                    print("'Why didnt you get the compass, you idiot' shouted the Sailor at you")
                    print("Go get it then come back to me")
                    self.shore_act2()
            else:
                print("'How would I make the boat bigger if I dont have plans you idiot' shouts the Sailor at you")
                print("Go get it then come back to me")
                self.shore_act2()
    def sea_act1(self):
        print("You Sail off to the seas")
        print("Buy along the way you find a shark that starts to harass you")
        print("The shark is breaking the ship")
        print("What do you do?")
        time.sleep(5)
        options = ["Fight the shark","Try to go faster with the ship","Go swiming and try to go to the nearest island while the shark is busy with the ship"]
        choice = self.interactive_menu(options)
        if choice == "Fight the shark":
            shark = ArmoredEnemy(100,50,"",200,0.7,{})
            self.sea_level += 1
            self.fight(shark,self.sea_act2)
        elif choice == "Try to go faster with the ship":
            if random.random > 0.8:
                print("You run away with the ship and the Shark leaves you alone")
                self.sea_level += 1
                self.sea_act3()
            else:
                self.ship_health -= 1
                print("You couldnt escape the shark")
                print("But the ship is still entact")
                print(f"Your ship health is {self.ship_health}")
                self.sea_act1()
        else:
            print("You jump out of the ship and let the sailor and the ship be eaten by the shark")
            print("While you escape to the nearest island")
            self.lost_ending()
    

    def sea_act2(self):
        print("You kill the shark")
        print("You continue sailing to your hometown with the Sailor")
        print("But ahead you see a light")
        print("But its not what you excepected")
        print("It turns out that the ship is damaged")
        print("and it cant get you to your hometown in one go")
        print("So you and the Sailor sail off to the nearest island to gather some wood")
        print("So you can fix the ship")
        time.sleep(10)
        self.island_act1()
    
    def island_act1(self):
        print("You end up at the nearest island")
        print("Saving game")
        self.last_checkpoint = self.island_act1
        with open("Last saved game.txt","w") as file:
            file.write(f"difficulty:{self.difficulty}\n")
            file.write(f"volume:{self.volume}\n")
            file.write(f"inventory:{','.join(self.inventory)}\n")
            file.write(f"gold:{self.gold}\n")
            file.write(f"current_sword:{self.current_sword}\n")
            file.write(f"hp:{self.hp}\n")
            file.write(f"max_hp:{self.max_hp}\n")
            file.write(f"last_checkpoint:{self.last_checkpoint}\n")
            file.write(f"taken_upgrades:{self.taken_upgrades}\n")
            file.write(f"agility:{self.agility}\n")
            file.write(f"sea level:{self.sea_level}\n")
        print("Now you have to gather some wood to fix the ship")
        print("For each 5 planks you can increase the ship health by 1")
        print(f"The current ship health is {self.ship_health}")
        print("What do you do?")
        options = ["Go to a forest to gather wood","Repair the ship","Go back sailing"]
        choice = self.interactive_menu(options)
        if choice == "Go to a forest to gather wood":
            print("You head to the forest")
            self.forest_act6()
        elif choice == "Repair the ship":
            for i in range(5):
                try:
                    self.inventory.remove("wooden planks")
                except ValueError:
                    self.inventory += ["wooden planks"]*i
        else:
            print("You Sail with the ship to the sea")
            if self.sea_level >= 5:
                self.good_ending()
            self.sea_act1()
    def forest_act6(self):
        print("You head to the forest on the island")
        print("You find some bandits waiting for you")
        print("They duel you but one at a time")
        self.fight(Enemy(50,20,"steal",50))
        self.fight(ArmoredEnemy(70,15,"steal",75,0.4))
        print("After you unalive them you take thier wooden planks")
        x = random.randint(8,14)
        print(f"You find {x} wooden planks")
        self.inventory += ["wooden planks"]*x
        print("You head back to the shore of the island")
        self.island_act1()

        


    def lost_ending(self):
        print("You end up lost in the seas")
        print("You find an island but you dont have a way out")
        print("Your only hope is for someone to get you out")
        print("You live on that island for years but no one comes")
        print("You die peacfully on that island")
        time.sleep(10)
        print("Thanks for playing this game")
        print("So hackclub")
        print("Please give us more funds")
        kinda_homeless = pygame.mixer.Sound("my-mom-is-kinda-homeless.mp3")
        kinda_homeless.set_volume(self.volume)
        while True:
            kinda_homeless.play()
            time.sleep(4)
        sys.exit(0)
        

    







    def good_ending(self):
        print("After you sail with him")
        print("You finnaly find your home town")
        print("You tell your tale to all your friends")
        print("They dont believe you")
        print("It turns out it was a dream after all")
        print("You get dissapointed")
        print("So you fall back asleep")
        time.sleep(10)
        print("Thanks for playing this game")
        print("So hackclub")
        print("Please give us more funds")
        kinda_homeless = pygame.mixer.Sound("my-mom-is-kinda-homeless.mp3")
        kinda_homeless.set_volume(self.volume)
        while True:
            kinda_homeless.play()
            time.sleep(4)
        sys.exit(0)

        

                
                














    def evil_ending(self):
        print("You finally escape")
        print("You take the Sailor`s boat and sail to your home town with his map")
        print("But at what cost, you are now a disgrace to your home town and everybody hates you")
        time.sleep(10)
        print("Thanks for playing this game")
        print("So hackclub")
        print("Please give us more funds")
        kinda_homeless = pygame.mixer.Sound("my-mom-is-kinda-homeless.mp3")
        kinda_homeless.set_volume(self.volume)
        while True:
            kinda_homeless.play()
            time.sleep(4)
        sys.exit(0)


    




    

    





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
