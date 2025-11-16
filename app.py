import random

# Base Character class
class Character:
    def __init__(self, name, health, attack_power):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.max_health = health  
        self.defense_active = False

    def attack(self, opponent):
        if opponent.defense_active:
            print(f"{opponent.name} defends against the attack!")
            opponent.defense_active = False
            return
        damage = random.randint(self.attack_power - 5, self.attack_power + 5)
        damage = max(1, damage)
        opponent.health -= damage
        print(f"{self.name} attacks {opponent.name} for {damage} damage!")
        if opponent.health <= 0:
            opponent.health = 0
            print(f"{opponent.name} has been defeated!")

    def heal(self):
        heal_amount = 20
        self.health = min(self.max_health, self.health + heal_amount)
        print(f"{self.name} heals for {heal_amount} health. Current health: {self.health}")

    def display_stats(self):
        print(f"{self.name}'s Stats - Health: {self.health}/{self.max_health}, Attack Power: {self.attack_power}")

    def use_special_ability(self, opponent):
        print("This character has no special abilities implemented.")

# Warrior class (inherits from Character)
class Warrior(Character):
    def __init__(self, name):
        super().__init__(name, health=140, attack_power=25)

    def use_special_ability(self, opponent):
        print("Choose ability:")
        print("1. Power Strike (bonus damage attack)")
        print("2. Guard (blocks the next attack)")
        choice = input("Enter ability number: ")
        if choice == '1':
            damage = random.randint(self.attack_power + 5, self.attack_power + 15)
            damage = max(1, damage)
            opponent.health -= damage
            print(f"{self.name} uses Power Strike for {damage} damage!")
            if opponent.health <= 0:
                opponent.health = 0
                print(f"{opponent.name} has been defeated!")
        elif choice == '2':
            self.defense_active = True
            print(f"{self.name} raises Guard to block the next attack!")
        else:
            print("Invalid choice. No ability used.")

# Mage class (inherits from Character)
class Mage(Character):
    def __init__(self, name):
        super().__init__(name, health=100, attack_power=35)

    def use_special_ability(self, opponent):
        print("Choose ability:")
        print("1. Fireball (high damage attack)")
        print("2. Mana Shield (blocks the next attack)")
        choice = input("Enter ability number: ")
        if choice == '1':
            damage = random.randint(self.attack_power + 10, self.attack_power + 20)
            damage = max(1, damage)
            opponent.health -= damage
            print(f"{self.name} casts Fireball for {damage} damage!")
            if opponent.health <= 0:
                opponent.health = 0
                print(f"{opponent.name} has been defeated!")
        elif choice == '2':
            self.defense_active = True
            print(f"{self.name} activates Mana Shield to block the next attack!")
        else:
            print("Invalid choice. No ability used.")

# EvilWizard class (inherits from Character)
class EvilWizard(Character):
    def __init__(self, name):
        super().__init__(name, health=150, attack_power=15)

    def regenerate(self):
        self.health += 5
        if self.health > self.max_health:
            self.health = self.max_health
        print(f"{self.name} regenerates 5 health! Current health: {self.health}")

# Create Archer class
class Archer(Character):
    def __init__(self, name):
        super().__init__(name, health=110, attack_power=30)

    def use_special_ability(self, opponent):
        print("Choose ability:")
        print("1. Quick Shot (double arrow attack)")
        print("2. Evade (evades the next attack)")
        choice = input("Enter ability number: ")
        if choice == '1':
            for _ in range(2):
                damage = random.randint(self.attack_power // 2 - 3, self.attack_power // 2 + 3)
                damage = max(1, damage)
                opponent.health -= damage
                print(f"{self.name} shoots a quick arrow for {damage} damage!")
            if opponent.health <= 0:
                opponent.health = 0
                print(f"{opponent.name} has been defeated!")
        elif choice == '2':
            self.defense_active = True
            print(f"{self.name} prepares to Evade the next attack!")
        else:
            print("Invalid choice. No ability used.")

# Create Paladin class 
class Paladin(Character):
    def __init__(self, name):
        super().__init__(name, health=150, attack_power=20)

    def use_special_ability(self, opponent):
        print("Choose ability:")
        print("1. Holy Strike (bonus damage attack)")
        print("2. Divine Shield (blocks the next attack)")
        choice = input("Enter ability number: ")
        if choice == '1':
            damage = random.randint(self.attack_power + 5, self.attack_power + 15)
            damage = max(1, damage)
            opponent.health -= damage
            print(f"{self.name} uses Holy Strike for {damage} damage!")
            if opponent.health <= 0:
                opponent.health = 0
                print(f"{opponent.name} has been defeated!")
        elif choice == '2':
            self.defense_active = True
            print(f"{self.name} activates Divine Shield to block the next attack!")
        else:
            print("Invalid choice. No ability used.")

def create_character():
    print("Choose your character class:")
    print("1. Warrior")
    print("2. Mage")
    print("3. Archer") 
    print("4. Paladin")  

    class_choice = input("Enter the number of your class choice: ")
    name = input("Enter your character's name: ")

    if class_choice == '1':
        return Warrior(name)
    elif class_choice == '2':
        return Mage(name)
    elif class_choice == '3':
        return Archer(name)
    elif class_choice == '4':
        return Paladin(name)
    else:
        print("Invalid choice. Defaulting to Warrior.")
        return Warrior(name)

def battle(player, wizard):
    while wizard.health > 0 and player.health > 0:
        print("\n--- Your Turn ---")
        print("1. Attack")
        print("2. Use Special Ability")
        print("3. Heal")
        print("4. View Stats")

        choice = input("Choose an action: ")

        if choice == '1':
            player.attack(wizard)
        elif choice == '2':
            player.use_special_ability(wizard)
        elif choice == '3':
            player.heal()
        elif choice == '4':
            player.display_stats()
        else:
            print("Invalid choice. Try again.")

        if wizard.health > 0:
            wizard.regenerate()
            wizard.attack(player)

        if player.health <= 0:
            print(f"{player.name} has been defeated!")
            break

    if wizard.health <= 0:
        print(f"The wizard {wizard.name} has been defeated by {player.name}!")

def main():
    player = create_character()
    wizard = EvilWizard("The Dark Wizard")
    battle(player, wizard)

if __name__ == "__main__":
    main()