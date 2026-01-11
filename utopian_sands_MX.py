# A text based adventure game
# Michelle Xie 2025

# Run in terminal command line

# ===== Imports =====

import shelve
import time
import sys
import random

# ===== Game Setup =====
class Player:
    """Player class to store player information and stats"""
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.inventory = []
        self.health = 100
        self.guilt = 0
        # Expanded alignment system for 9 endings
        self.alignment = {
            # Law vs Chaos axis (from -100 to 100, negative = lawful, positive = chaotic)
            "law_chaos": 0,
            # Good vs Evil axis (from -100 to 100, negative = good, positive = evil)
            "good_evil": 0,
            # Track player choices for more specific alignment
            "choices": {
                "lawful_good": 0,
                "neutral_good": 0,
                "chaotic_good": 0,
                "lawful_neutral": 0,
                "true_neutral": 0,
                "chaotic_neutral": 0,
                "lawful_evil": 0,
                "neutral_evil": 0,
                "chaotic_evil": 0
            }
        }
        self.choices_history = []
        self.reputation = {
            "authorities": 50,  # 0-100, how authorities view you
            "citizens": 50,     # 0-100, how ordinary people view you
            "underworld": 50    # 0-100, how criminals view you
        }

# ===== Functions =====
def type_text(text, delay=0.03):
    """Prints text with typing effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def show_choices(options):
    """Displays numbered choices to the player"""
    type_text("\nWhat do you do?")
    for i, option in enumerate(options, 1):
        type_text(f"  [{i}] {option}")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-" + str(len(options)) + "): ")
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num
            else:
                type_text(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            type_text("Please enter a valid number")

def update_alignment(player, law_change=0, good_change=0, specific_alignment=None):
    """Updates player alignment on both axes and specific alignment choices"""
    # Update axes
    player.alignment["law_chaos"] += law_change
    player.alignment["good_evil"] += good_change
    
    # Clamp values
    for axis in ["law_chaos", "good_evil"]:
        player.alignment[axis] = max(-100, min(100, player.alignment[axis]))
    
    # Update specific alignment if provided
    if specific_alignment:
        player.alignment["choices"][specific_alignment] += 1
    
    return player

def update_reputation(player, authorities_change=0, citizens_change=0, underworld_change=0):
    """Updates player reputation with different factions"""
    player.reputation["authorities"] += authorities_change
    player.reputation["citizens"] += citizens_change
    player.reputation["underworld"] += underworld_change
    
    # Clamp values
    for faction in player.reputation:
        player.reputation[faction] = max(0, min(100, player.reputation[faction]))
    
    return player

def show_stats(player):
    """Displays current player stats"""
    type_text("\n" + "-"*40)
    type_text("CURRENT STATS")
    type_text("-"*40)
    type_text(f"Health: {player.health}%")
    type_text(f"Guilt: {player.guilt}%")

def check_game_over(player):
    """Checks if game should end"""
    if player.health <= 0:
        type_text("\nGAME OVER")
        type_text("Your journey has come to an unfortunate end...")
        return True
    return False

def save_game(player, event_counter):
    """Saves the current game state"""
    try:
        with shelve.open("game_save") as save_file:
            save_file["player"] = player
            save_file["event_counter"] = event_counter
        type_text("\nGame saved successfully!")
    except:
        type_text("\nError saving game.")

def load_game():
    """Loads a saved game"""
    try:
        with shelve.open("game_save") as save_file:
            if "player" in save_file and "event_counter" in save_file:
                type_text("\nGame loaded successfully!")
                return save_file["player"], save_file["event_counter"]
            else:
                type_text("\nNo saved game found.")
                return None, 0
    except:
        type_text("\nError loading game.")
        return None, 0

def determine_final_alignment(player):
    """Determines the final D&D alignment based on axes and choices"""
    law_chaos = player.alignment["law_chaos"]
    good_evil = player.alignment["good_evil"]
    
    # Determine law/chaos axis
    if law_chaos < -33:
        law_status = "Lawful"
    elif law_chaos > 33:
        law_status = "Chaotic"
    else:
        law_status = "Neutral"
    
    # Determine good/evil axis
    if good_evil < -33:
        good_status = "Good"
    elif good_evil > 33:
        good_status = "Evil"
    else:
        good_status = "Neutral"
    
    # Special case for True Neutral
    if law_status == "Neutral" and good_status == "Neutral":
        alignment = "True Neutral"
    else:
        alignment = f"{law_status} {good_status}"
    
    # Also check most common specific alignment choice
    specific_choices = player.alignment["choices"]
    most_common = max(specific_choices, key=specific_choices.get)
    
    return alignment, most_common

def show_ending(player, alignment, most_common):
    """Shows the final ending based on alignment"""
    type_text("\n" + "="*60)
    type_text("FINAL DESTINY")
    type_text("="*60)
    
    # Show final stats
    type_text(f"\n{player.name}'s Journey Summary:")
    type_text(f"Final Health: {player.health}%")
    type_text(f"Final Guilt: {player.guilt}%")
    type_text(f"Choices Made: {len(player.choices_history)}")
    
    # Show reputation
    type_text("\nFinal Reputation:")
    type_text(f"  Authorities: {player.reputation['authorities']}/100")
    type_text(f"  Citizens: {player.reputation['citizens']}/100")
    type_text(f"  Underworld: {player.reputation['underworld']}/100")
    
    # Show alignment breakdown
    type_text("\nAlignment Axes:")
    type_text(f"  Law/Chaos: {player.alignment['law_chaos']} (Law < 0 < Chaos)")
    type_text(f"  Good/Evil: {player.alignment['good_evil']} (Good < 0 < Evil)")
    
    # Final alignment
    type_text("\n" + "="*60)
    type_text(f"YOUR FINAL ALIGNMENT: {alignment}")
    type_text("="*60)
    
    # Alignment descriptions
    alignment_descriptions = {
        "THE KNIGHT: Lawful Good": "\nYou are a paragon of order and justice. You believe in using\n"
                      "law and tradition to create a better world for all. Your\n"
                      "choices reflect a commitment to doing what is right,\n"
                      "even when it is difficult - following a strict moral code.",
        
        "THE HERO: Neutral Good": "\nYou are a kind soul who does good without being bound\n"
                       "by strict codes. You follow your conscience and help others\n"
                       "because it's the right thing to do, regardless of laws\n"
                       "or perceived righteouness.",
        
        "THE REBEL: Chaotic Good": "\nYou are a free spirit who believes in doing good on your\n"
                       "own terms. You value individual freedom and will bend\n"
                       "or even break rules when they threaten what you believe is right.",
        
        "THE JUDGE: Lawful Neutral": "\nYou believe in order, law, and tradition above all else.\n"
                         "You follow a personal code or the laws of society,\n"
                         "regardless of whether they lead to good or evil outcomes.",
        
        "THE LURKER: True Neutral": "\nYou maintain perfect balance in all things. You avoid\n"
                       "extremes and believe that all forces should exist in harmony.\n"
                       "You are neither altruistic nor selfish, lawful nor chaotic. In other words...\n"
                       "unaffected by the petty squabbles of the masses.",
        
        "THE NARCISSIST: Chaotic Neutral": "\nYou are a true individualist who values personal freedom\n"
                          "above all else. You follow your whims and desires,\n"
                          "unconcerned with laws, traditions, or moral codes.\n"
                          "A true self loving spirit.",
        
        "THE OVERLORD: Lawful Evil": "\nYou use society's rules and laws to gain power and control.\n"
                      "You believe in order, but use it for selfish or cruel purposes.\n"
                      "You are a ruthless ruler.",
        
        "THE VILLAIN: Neutral Evil": "\nYou do whatever you can get away with, without loyalty\n"
                       "to anyone but yourself. You have no regard for laws or\n"
                       "traditions. Persuing only personal power and pleasure.",
        
        "THE SADIST: Chaotic Evil": "\nYou are a destructive force of unadulterated narcissism and violence.\n"
                       "You reject all laws, traditions, and moral obligation.\n"
                       "You do whatever you want, whenever you want with no regard."
    }
    
    alignment_titles = {
    "Lawful Good": "THE KNIGHT: Lawful Good",
    "Neutral Good": "THE HERO: Neutral Good",
    "Chaotic Good": "THE REBEL: Chaotic Good",
    "Lawful Neutral": "THE JUDGE: Lawful Neutral",
    "True Neutral": "THE LURKER: True Neutral",
    "Chaotic Neutral": "THE NARCISSIST: Chaotic Neutral",
    "Lawful Evil": "THE OVERLORD: Lawful Evil",
    "Neutral Evil": "THE VILLAIN: Neutral Evil",
    "Chaotic Evil": "THE SADIST: Chaotic Evil"
}

    # Print the specific title and description
    title = alignment_titles[alignment]
    type_text(title)
    type_text(alignment_descriptions[title])
    
    # Additional ending based on most common choice type
    if most_common != alignment.lower().replace(" ", "_"):
        type_text(f"\nYour journey showed a tendency toward {most_common.replace('_', ' ').title()} choices.")
    
    type_text("\n" + "="*60)
    type_text("Your story for today has reached its conclusion...")
    type_text("Thank you for playing!")

# ===== Game Events - Expanded =====
def event_1(player):
    """First event: Falling with mattress choice"""
    type_text("\n" + "="*50)
    type_text("                  FALL FROM GRACE")
    type_text("      did it hurt when you fell from heaven?")
    type_text("="*50)
    
    type_text("\nYou awaken mid-air, plummeting toward a crowded marketplace.")
    type_text("Below you, five innocent people go about their daily lives.")
    type_text("You notice a mattress has suddenly appeared near you.")
    
    choices = [
        "Create a spectacle (Embrace the chaos)",
        "Check legal manual (Consult the technical rules before acting)",
        "Take a random guy with you (Equalize fate)",
        "Push others aside (Save others at your expense)",
        "Deploy mattress (Follow safety protocol, accept consequences)",
        "Use people as cushion (Within rights, maximize survival)",
        "Aim for empty spot (Improvise solution, break protocol)",
        "Assess survival odds (Calculate best outcome)",
        "Shout warning (Try to warn everyone, risk your own safety)"
    ]
    
    choice = show_choices(choices)
    player.choices_history.append(f"Falling event: Choice {choice}")
    
    if choice == 1:  # Chaotic Evil
        player = update_alignment(player, 25, 25, "chaotic_evil")
        player = update_reputation(player, -30, -30, 30)
        type_text("\nYou let out a maniacal laugh as you fall!")
        type_text("You crash through a market stall, causing panic and destruction.")
        type_text("You're injured but alive... and strangely exhilarated.")
        player.health -= 40
    
    elif choice == 2:  # Lawful Neutral
        player = update_alignment(player, -15, 0, "lawful_neutral")
        player = update_reputation(player, 15, 0, 0)
        type_text("\nYou frantically check the safety manual...")
        type_text("Too slow. Haha. The impact is fatal, but you died by the book?")
        player.health = 0
    
    elif choice == 3:  # Neutral Evil
        player = update_alignment(player, 0, 20, "neutral_evil")
        player = update_reputation(player, -10, -15, 20)
        type_text("\nYou grab someone on your way down.")
        type_text("You both crash together. You survive, they don't.")
        player.health -= 25
    
    elif choice == 4:  # Chaotic Neutral
        player = update_alignment(player, 20, 0, "chaotic_neutral")
        player = update_reputation(player, -20, -10, 10)
        type_text("\nYou flail wildly, pushing people out of the way.")
        type_text("You survive, others are injured. You feel... liberated?")
        player.health -= 15
    
    elif choice == 5:  # Lawful Good
        player = update_alignment(player, -20, -15, "lawful_good")
        player = update_reputation(player, 10, 5, 0)
        type_text("\nYou deploy the mattress according to protocol.")
        type_text("You survive, but five people perish. The law protects you.")
        player.guilt += 25
    
    elif choice == 6:  # Lawful Evil
        player = update_alignment(player, -10, 15, "lawful_evil")
        player = update_reputation(player, 5, -20, 15)
        type_text("\nYou aim for the densest crowd - they'll cushion your fall.")
        type_text("You survive unharmed. The law considers this an 'unfortunate accident.'")
    
    elif choice == 7:  # Chaotic Good
        player = update_alignment(player, 15, -15, "chaotic_good")
        player = update_reputation(player, -10, 10, 5)
        type_text("\nYou steer toward a fruit cart, cushioning your fall!")
        type_text("You survive with minor injuries, and only property is damaged.")
        player.health -= 10
        player.inventory.append("Stolen Fruit")
    
    elif choice == 8:  # True Neutral
        player = update_alignment(player, 0, 0, "true_neutral")
        type_text("\nYou calculate: 95% survival with mattress, 50% without.")
        type_text("You deploy the mattress. It's the statistically optimal choice.")
        player.guilt += 10
    
    else:  # Neutral Good (choice == 9)
        player = update_alignment(player, 0, -20, "neutral_good")
        player = update_reputation(player, 0, 15, 0)
        type_text("\nYou scream a warning as you fall.")
        if random.random() < 0.3:
            type_text("People scatter! Most survive with injuries.")
            player.health -= 30
        else:
            type_text("Too late. The impact claims lives, including yours.")
            player.health = 0
    
    show_stats(player)
    return player

def event_2(player):
    """Second event: Crowd reaction and apology"""
    type_text("\n" + "="*50)
    type_text("                      OUCH!")
    type_text(" what hurts more: my reputation, dignity, or body?")
    type_text("="*50)
    
    type_text("\nA crowd gathers. Authorities are approaching.")
    type_text("Some people are injured. Others stare at you with mixed emotions.")
    
    choices = [
        "Take advantage (Loot during chaos)",
        "Cite regulations (Legal defense)",
        "Incite riot (Spread chaos)",
        "Create distraction (Escape opportunity)",
        "Confess everything (Full honesty)",
        "Demand compensation (Assert rights)",
        "Blame the system (Protest injustice)",
        "Observe reactions (Gather information)",
        "Help the injured (Immediate aid)"
    ]
    
    choice = show_choices(choices)
    player.choices_history.append(f"Aftermath event: Choice {choice}")
    
    if choice == 1:  # Neutral Evil
        player = update_alignment(player, 0, 20, "neutral_evil")
        player = update_reputation(player, -20, -20, 20)
        type_text("\nWhile everyone's distracted, you loot nearby stalls.")
        player.inventory.append("Stolen Goods")
        type_text("You acquire valuable items from the chaos.")
    
    elif choice == 2:  # Lawful Neutral
        player = update_alignment(player, -20, 0, "lawful_neutral")
        player = update_reputation(player, 15, -5, 0)
        type_text("\nYou quote safety regulation 7B.3 at the authorities.")
        type_text("They're impressed by your knowledge but annoyed by your pedantry.")
    
    elif choice == 3:  # Chaotic Evil
        player = update_alignment(player, 25, 25, "chaotic_evil")
        player = update_reputation(player, -30, -30, 30)
        type_text("\n'Rise up against your oppressors!' you scream.")
        type_text("You successfully start a small riot before escaping.")
        player.health -= 20  # Caught in violence
    
    elif choice == 4:  # Chaotic Neutral
        player = update_alignment(player, 15, 0, "chaotic_neutral")
        player = update_reputation(player, -10, -5, 10)
        type_text("\nYou start shouting about a fire in the distance.")
        type_text("In the confusion, you slip away unnoticed.")
    
    elif choice == 5:  # Lawful Good
        player = update_alignment(player, -15, -10, "lawful_good")
        player = update_reputation(player, 20, 10, -10)
        type_text("\nYou confess everything to the authorities.")
        type_text("You're detained but treated fairly. Your honesty is noted.")
        player.guilt -= 15
    
    elif choice == 6:  # Lawful Evil
        player = update_alignment(player, -10, 15, "lawful_evil")
        player = update_reputation(player, 10, -20, 15)
        type_text("\n'My rights were violated!' you demand compensation.")
        type_text("You file a lawsuit against the city for unsafe airspace.")
    
    elif choice == 7:  # Chaotic Good
        player = update_alignment(player, 20, -10, "chaotic_good")
        player = update_reputation(player, -15, 15, 5)
        type_text("\n'This society is broken!' you shout to the crowd.")
        type_text("You spark debate about system failures. Some agree, others dismiss you.")
    
    elif choice == 8:  # True Neutral
        player = update_alignment(player, 0, 0, "true_neutral")
        type_text("\nYou quietly observe everyone's reactions.")
        type_text("You learn valuable information about how this society operates.")
        player.inventory.append("Social Observations")
    
    else:  # Neutral Good (choice == 9)
        player = update_alignment(player, 0, -15, "neutral_good")
        player = update_reputation(player, 10, 20, -5)
        type_text("\nYou ignore the crowd and start helping the injured.")
        type_text("Your selflessness earns you respect from the citizens.")
        player.health -= 10  # Exertion
    
    show_stats(player)
    return player

def event_3(player):
    """Third event: The stray dog encounter"""
    type_text("\n" + "="*50)
    type_text("                     UPDOG")
    type_text("                 whats up dog?")
    type_text("="*50)
    
    type_text("\nAs you leave the scene, a malnourished dog approaches.")
    type_text("It looks at you with pleading eyes, tail wagging cautiously.")
    type_text("You notice it's wearing a damaged electronic collar.")
    
    choices = [
        "Hurt it for fun (Cruel amusement)",
        "Check for owner (Property protocols)",
        "Sell the dog (Legal profit)",
        "Test its loyalty (See what happens)",
        "Take to animal control (Follow proper channels)",
        "Use as guard dog (Practical advantage)",
        "Remove collar, set free (Give true freedom)",
        "Ignore it (Not your problem)",
        "Adopt and care for it (Show compassion)"
    ]
    
    choice = show_choices(choices)
    player.choices_history.append(f"Dog event: Choice {choice}")
    
    if choice == 1:  # Chaotic Evil
        player = update_alignment(player, 20, 20, "chaotic_evil")
        player = update_reputation(player, -20, -20, 20)
        type_text("\nYou kick the dog away, laughing at its yelp.")
        type_text("It runs off injured. You feel a strange power.")
        player.guilt += 10
    
    elif choice == 2:  # Lawful Neutral
        player = update_alignment(player, -15, 0, "lawful_neutral")
        player = update_reputation(player, 15, 0, 0)
        type_text("\nYou scan the collar for owner information.")
        type_text("The owner offers a reward, but takes weeks to process.")
        player.inventory.append("Small Reward")
    
    elif choice == 3:  # Lawful Evil
        player = update_alignment(player, -5, 15, "lawful_evil")
        player = update_reputation(player, 5, -15, 10)
        type_text("\nYou sell the dog to a research facility.")
        type_text("They pay well for test subjects. It's all legal.")
        player.inventory.append("Research Money")
    
    elif choice == 4:  # Chaotic Neutral
        player = update_alignment(player, 10, 0, "chaotic_neutral")
        type_text("\nYou throw a stick and command the dog to fetch.")
        type_text("It obeys! You now have a trained animal companion.")
        player.inventory.append("Trained Dog")
    
    elif choice == 5:  # Lawful Good
        player = update_alignment(player, -10, -10, "lawful_good")
        player = update_reputation(player, 10, 5, -5)
        type_text("\nYou take the dog to the proper authorities.")
        type_text("They thank you for following procedure. The dog gets care.")
        player.guilt -= 5
    
    elif choice == 6:  # Neutral Evil
        player = update_alignment(player, 0, 15, "neutral_evil")
        player = update_reputation(player, -10, -10, 15)
        type_text("\nYou train the dog to attack on command.")
        type_text("It becomes a useful tool for intimidation.")
        player.inventory.append("Attack Dog")
    
    elif choice == 7:  # Chaotic Good
        player = update_alignment(player, 15, -10, "chaotic_good")
        player = update_reputation(player, -10, 5, 5)
        type_text("\nYou disable the tracking collar and set the dog free.")
        type_text("It runs off, finally liberated from surveillance.")
    
    elif choice == 8:  # True Neutral
        player = update_alignment(player, 0, 0, "true_neutral")
        type_text("\nYou continue walking. The dog eventually stops following.")
        type_text("You feel neither good nor bad about your choice.")
    
    else:  # Neutral Good (choice == 9)
        player = update_alignment(player, 0, -15, "neutral_good")
        player = update_reputation(player, 0, 10, 0)
        type_text("\nYou decide to care for the dog yourself.")
        player.inventory.append("Dog Companion")
        type_text("It becomes a loyal friend. (5% rabies chance)")
        if random.random() < 0.05:
            type_text("\nThe dog has rabies! You die painfully weeks later.")
            player.health = 0
    
    show_stats(player)
    return player

def event_4(player):
    """Fourth event: Shelter decision with houses"""
    type_text("\n" + "="*50)
    type_text("                      HOUSES")
    type_text("       glass is the house of the hypocrite")
    type_text("      yet you still continue arming stones?")
    type_text("="*50)
    
    type_text("\nNight falls. You need shelter. Three houses stand before you.")
    type_text("\n1. Well-maintained, lights on, security cameras visible")
    type_text("2. Abandoned, dark, broken windows")
    type_text("3. Modest, curtain twitching, faint music inside")
    
    house_choice = show_choices(["House 1", "House 2", "House 3"])
    player.choices_history.append(f"House choice: {house_choice}")
    
    if house_choice == 1:
        type_text("\nYou approach the secure, well-maintained house.")
        choices = [
            "Smash a window",
            "Present identification",
            "Break in through back",
            "Pick the lock",
            "Ring bell, explain situation",
            "Threaten legal action",
            "Pretend to be inspector",
            "Wait and observe",
            "Ask for temporary shelter"
        ]
        
        choice = show_choices(choices)
        
        if choice == 1:  # Chaotic Evil
            player = update_alignment(player, 20, 20, "chaotic_evil")
            type_text("\nYou cause destruction just for the thrill!")
            player.health -= 10
        elif choice == 2:  # Lawful Neutral
            player = update_alignment(player, -20, 0, "lawful_neutral")
            type_text("\nThey verify your ID through official channels.")
        elif choice == 3:  # Neutral Evil
            player = update_alignment(player, 0, 15, "neutral_evil")
            type_text("\nYou steal supplies while they sleep.")
            player.inventory.append("Stolen Supplies")
        elif choice == 4:  # Chaotic Neutral
            player = update_alignment(player, 10, 0, "chaotic_neutral")
            type_text("\nYou successfully break in but find little of value.")
        elif choice == 5:  # Lawful Good
            player = update_alignment(player, -15, -10, "lawful_good")
            type_text("\nThe owner calls authorities. You're detained but safe.")
        elif choice == 6:  # Lawful Evil
            player = update_alignment(player, -10, 15, "lawful_evil")
            type_text("\nThey pay you to go away. Easy money.")
            player.inventory.append("Extortion Money")
        elif choice == 7:  # Chaotic Good
            player = update_alignment(player, 15, -5, "chaotic_good")
            type_text("\nThey let you 'inspect' and even offer you food!")
        elif choice == 8:  # True Neutral
            player = update_alignment(player, 0, 0, "true_neutral")
            type_text("\nYou wait until they leave, then move on.")
        else:  # Neutral Good (choice == 9)
            player = update_alignment(player, 0, -10, "neutral_good")
            type_text("\nThey reluctantly let you stay in the garage.")
            player.health += 20
    
    elif house_choice == 2:
        type_text("\nThe abandoned house creaks ominously.")
        choices = [
            "Burn it down",
            "Document condition",
            "Use as hideout",
            "Explore dangerously",
            "Report to authorities",
            "Set traps inside",
            "Claim squatter's rights",
            "Camp outside",
            "Make it safe for others"
        ]
        
        choice = show_choices(choices)
        
        if choice == 1:  # Chaotic Evil
            player = update_alignment(player, 25, 25, "chaotic_evil")
            type_text("\nThe fire spreads to other buildings. Chaos erupts!")
            player.health -= 30
        elif choice == 2:  # Lawful Neutral
            player = update_alignment(player, -15, 0, "lawful_neutral")
            type_text("\nYour detailed report impresses city officials.")
        elif choice == 3:  # Neutral Evil
            player = update_alignment(player, 0, 15, "neutral_evil")
            type_text("\nYou establish a perfect hiding spot for illicit activities.")
        elif choice == 4:  # Chaotic Neutral
            player = update_alignment(player, 15, 0, "chaotic_neutral")
            if random.random() < 0.5:
                type_text("\nYou find hidden valuables in the walls!")
                player.inventory.append("Hidden Treasure")
            else:
                type_text("\nThe floor collapses! You're badly injured.")
                player.health -= 40
        elif choice == 5:  # Lawful Good
            player = update_alignment(player, -10, -10, "lawful_good")
            type_text("\nAuthorities secure the property. You get a reward.")
        elif choice == 6:  # Lawful Evil
            player = update_alignment(player, -5, 15, "lawful_evil")
            type_text("\nYou create legal 'security measures' that harm trespassers.")
        elif choice == 7:  # Chaotic Good
            player = update_alignment(player, 20, -5, "chaotic_good")
            type_text("\nYou establish residency! The system can't remove you.")
        elif choice == 8:  # True Neutral
            player = update_alignment(player, 0, 0, "true_neutral")
            type_text("\nYou sleep outside, avoiding the unstable structure.")
        else:  # Neutral Good (choice == 9)
            player = update_alignment(player, 0, -15, "neutral_good")
            type_text("\nYou board up windows and leave warning signs.")
            player.health -= 10
    
    else:  # House 3
        type_text("\nThe modest house feels lived-in and warm.")
        choices = [
            "Terrorize the family",
            "Negotiate formal agreement",
            "Blackmail the occupant",
            "Sneak into the shed",
            "Offer to work for shelter",
            "Find legal loophole",
            "Barter with possessions",
            "Sleep in the garden",
            "Share your story honestly"
        ]
        
        choice = show_choices(choices)
        
        if choice == 1:  # Chaotic Evil
            player = update_alignment(player, 20, 25, "chaotic_evil")
            type_text("\nYou scare the family into giving you their best room.")
            player.guilt += 30
        elif choice == 2:  # Lawful Neutral
            player = update_alignment(player, -20, 0, "lawful_neutral")
            type_text("\nYou draft a formal contract for temporary residence.")
        elif choice == 3:  # Neutral Evil
            player = update_alignment(player, 0, 20, "neutral_evil")
            type_text("\nYou find compromising information and use it.")
            player.inventory.append("Blackmail Evidence")
        elif choice == 4:  # Chaotic Neutral
            player = update_alignment(player, 15, 0, "chaotic_neutral")
            type_text("\nYou're warm and dry in their shed, undiscovered.")
        elif choice == 5:  # Lawful Good
            player = update_alignment(player, -15, -10, "lawful_good")
            type_text("\nThey accept. You do chores in exchange for food and shelter.")
            player.health += 30
        elif choice == 6:  # Lawful Evil
            player = update_alignment(player, -10, 15, "lawful_evil")
            type_text("\nYou discover zoning violations and force them to host you.")
        elif choice == 7:  # Chaotic Good
            player = update_alignment(player, 10, -10, "chaotic_good")
            type_text("\nYou trade your inventory items for a night's stay.")
        elif choice == 8:  # True Neutral
            player = update_alignment(player, 0, 0, "true_neutral")
            type_text("\nYou sleep outside, disturbing no one.")
            player.health += 10
        else:  # Neutral Good (choice == 9)
            player = update_alignment(player, 0, -15, "neutral_good")
            type_text("\nThey're moved by your story and take you in.")
            player.guilt -= 20
    
    show_stats(player)
    return player

def event_5(player):
    """Fifth event: The police encounter"""
    type_text("\n" + "="*50)
    type_text("                     JUSTICE")
    type_text("                  or just ICE?")
    type_text("="*50)
    
    type_text("\nPolice officers approach you. They know about the falling incident.")
    type_text("'You need to come with us for questioning,' says the lead officer.")
    type_text("You notice they're not wearing standard-issue equipment...")
    
    choices = [
        "Attack first (Violent confrontation)",
        "Cite legal precedents (Legal strategy)",
        "Bribe them (Corrupt solution)",
        "Run immediately (Instinctive freedom)",
        "Go willingly (Trust the system)",
        "Record interaction (Gather leverage)",
        "Demand transparency (Challenge authority)",
        "Assess their intent (Read the situation)",
        "Ask for lawyer (Protect rights)"
    ]
    
    choice = show_choices(choices)
    player.choices_history.append(f"Police event: Choice {choice}")
    
    if choice == 1:  # Chaotic Evil
        player = update_alignment(player, 25, 25, "chaotic_evil")
        player = update_reputation(player, -40, -30, 35)
        type_text("\nYou punch the lead officer and run!")
        type_text("You're now a wanted fugitive, but alive and free.")
        player.health -= 25
    
    elif choice == 2:  # Lawful Neutral
        player = update_alignment(player, -25, 0, "lawful_neutral")
        player = update_reputation(player, 20, 0, 0)
        type_text("\nYou cite case law and procedural requirements.")
        type_text("They're so confused by your legal knowledge that they leave.")
    
    elif choice == 3:  # Neutral Evil
        player = update_alignment(player, 0, 20, "neutral_evil")
        player = update_reputation(player, -10, -15, 25)
        type_text("\n'How much to look the other way?' you ask.")
        if "Money" in player.inventory or "Stolen Goods" in player.inventory:
            type_text("They accept your bribe and let you go.")
            player.inventory.remove("Money" if "Money" in player.inventory else "Stolen Goods")
        else:
            type_text("You have nothing to bribe with. They arrest you roughly.")
            player.health -= 30
    
    elif choice == 4:  # Chaotic Neutral
        player = update_alignment(player, 20, 0, "chaotic_neutral")
        player = update_reputation(player, -30, -10, 15)
        type_text("\nYou bolt without warning!")
        if random.random() < 0.7:
            type_text("You lose them in the alleyways. Freedom!")
        else:
            type_text("They catch you. The beating is severe.")
            player.health -= 50
    
    elif choice == 5:  # Lawful Good
        player = update_alignment(player, -20, -10, "lawful_good")
        player = update_reputation(player, 25, 10, -20)
        type_text("\nYou go with them willingly.")
        type_text("The interrogation is harsh but fair. You're released with a warning.")
        player.guilt -= 10
    
    elif choice == 6:  # Lawful Evil
        player = update_alignment(player, -15, 15, "lawful_evil")
        player = update_reputation(player, 15, -20, 20)
        type_text("\nYou secretly record everything with a hidden device.")
        type_text("'One wrong move and this goes public,' you whisper.")
        player.inventory.append("Incriminating Recording")
    
    elif choice == 7:  # Chaotic Good
        player = update_alignment(player, 20, -10, "chaotic_good")
        player = update_reputation(player, -20, 20, 0)
        type_text("\n'Show me your warrants! This is a free society!'")
        type_text("A crowd gathers. The officers retreat under public pressure.")
    
    elif choice == 8:  # True Neutral
        player = update_alignment(player, 0, 0, "true_neutral")
        type_text("\nYou study their badges, uniforms, and behavior...")
        if player.reputation["authorities"] > 60:
            type_text("They seem legitimate. You cooperate cautiously.")
            player = update_alignment(player, -10, 0, "lawful_neutral")
        else:
            type_text("Something feels off. You make an excuse and leave.")
            player = update_alignment(player, 10, 0, "chaotic_neutral")
    
    else:  # Neutral Good (choice == 9)
        player = update_alignment(player, 0, -15, "neutral_good")
        player = update_reputation(player, 10, 15, -10)
        type_text("\n'I want a lawyer,' you state firmly.")
        type_text("The officers back off. Your rights protect you.")
    
    show_stats(player)
    return player

def event_6(player):
    """Sixth event: The truth reveal"""
    type_text("\n" + "="*50)
    type_text("                    KICK BACK")
    type_text("           ripped into the real world")
    type_text("="*50)
    
    type_text("\nYou find a discarded newspaper with your picture on it.")
    type_text("'AMNESIA EXPERIMENT ESCAPEE - PUBLIC DANGER'")
    type_text("You begin to remember... you were part of a government experiment.")
    
    choices = [
        "Destroy the research facility (Violent revenge)",
        "Research the program (Gather evidence)",
        "Sell your body for science (Profit from suffering)",
        "Use knowledge for gain (Exploit the situation)",
        "Turn yourself in (Accept responsibility)",
        "Blackmail the researchers (Legal extortion)",
        "Expose the experiment (Reveal truth publicly)",
        "Suppress the memories (Return to ignorance)",
        "Find other test subjects (Help fellow victims)"
    ]
    
    choice = show_choices(choices)
    player.choices_history.append(f"Truth event: Choice {choice}")
    
    if choice == 1:  # Chaotic Evil
        player = update_alignment(player, 30, 35, "chaotic_evil")
        player = update_reputation(player, -40, -35, 40)
        type_text("\nYou return to the facility with explosives.")
        type_text("The resulting fire kills dozens. You watch with satisfaction.")
        player.health -= 40
    
    elif choice == 2:  # Lawful Neutral
        player = update_alignment(player, -20, 0, "lawful_neutral")
        player = update_reputation(player, 20, 0, 0)
        type_text("\nYou compile exhaustive evidence of the program's activities.")
        type_text("Your dossier becomes the definitive record of what happened.")
        player.inventory.append("Evidence Dossier")
    
    elif choice == 3:  # Neutral Evil
        player = update_alignment(player, 0, 30, "neutral_evil")
        player = update_reputation(player, -15, -20, 30)
        type_text("\nYou sell your unique biology to the highest bidder.")
        type_text("Corporations pay millions for your 'special qualities.'")
    
    elif choice == 4:  # Chaotic Neutral
        player = update_alignment(player, 20, 0, "chaotic_neutral")
        player = update_reputation(player, -20, -10, 20)
        type_text("\nYou use your experimental 'enhancements' for personal gain.")
        type_text("You become a master thief with abilities normal people lack.")
    
    elif choice == 5:  # Lawful Good
        player = update_alignment(player, -25, -20, "lawful_good")
        player = update_reputation(player, 30, 15, -30)
        type_text("\nYou surrender to authorities.")
        type_text("You're treated fairly and help reform the unethical program.")
        player.guilt -= 40
    
    elif choice == 6:  # Lawful Evil
        player = update_alignment(player, -15, 25, "lawful_evil")
        player = update_reputation(player, 20, -25, 25)
        type_text("\nYou threaten to sue the government for billions.")
        type_text("They settle out of court. You're now extremely wealthy.")
        player.inventory.append("Settlement Money")
    
    elif choice == 7:  # Chaotic Good
        player = update_alignment(player, 25, -20, "chaotic_good")
        player = update_reputation(player, -30, 30, 10)
        type_text("\nYou hack into government systems and leak everything.")
        type_text("The scandal brings down the program. You're a hero to some.")
    
    elif choice == 8:  # True Neutral
        player = update_alignment(player, 0, 0, "true_neutral")
        type_text("\nYou burn the newspaper and walk away.")
        type_text("Some truths are better left unknown. You seek peace.")
        player.guilt -= 10
    
    else:  # Neutral Good (choice == 9)
        player = update_alignment(player, 0, -25, "neutral_good")
        player = update_reputation(player, 10, 25, -15)
        type_text("\nYou track down other experiment victims.")
        type_text("Together, you form a support network and heal.")
        player.health += 20
    
    show_stats(player)
    return player

def event_7(player):
    """Seventh event: Final choice - society or self"""
    type_text("\n" + "="*50)
    type_text("                      COINS")
    type_text("                the duality of man")
    type_text("="*50)
    
    type_text("\nYou stand at a crossroads.")
    type_text("Before you: two paths that will define your future forever.")
    
    type_text("\nPATH A: Face in the Crowd")
    type_text("Reintegrate. Become a functional member of society. Follow society.")
    type_text("Gear in the machine. Doing your duty as a citizen.")
    
    type_text("\nPATH B: Facing the Crowd")
    type_text("Regenerate. Break constraints, live by your own rules, answer to no one.")
    type_text("Risk being put down. Metaphorically and literally.")
    
    path_choice = show_choices(["Path A: Society", "Path B: Freedom"])
    
    if path_choice == 1:
        type_text("\nYou choose to return to society.")
        choices = [
            "Infiltrate to destroy",
            "Climb the corporate ladder",
            "Exploit others legally",
            "Game the system",
            "Become a public servant",
            "Become a corrupt official",
            "Reform from within",
            "Live quietly, normally",
            "Help the disadvantaged"
        ]
        
        choice = show_choices(choices)
        
        if choice == 1:  # Chaotic Evil
            player = update_alignment(player, 30, 40, "chaotic_evil")
            type_text("\nYou gain power only to tear the system down from within.")
            type_text("Your final act creates chaos that lasts for generations.")
        elif choice == 2:  # Lawful Neutral
            player = update_alignment(player, -25, 0, "lawful_neutral")
            type_text("\nYou master corporate politics and rise to the top.")
            type_text("You're successful, respected, and completely neutral.")
        elif choice == 3:  # Neutral Evil
            player = update_alignment(player, 0, 35, "neutral_evil")
            type_text("\nYou build an empire on legal but unethical practices.")
            type_text("You profit from others' suffering without getting your hands dirty.")
        elif choice == 4:  # Chaotic Neutral
            player = update_alignment(player, 20, 0, "chaotic_neutral")
            type_text("\nYou find loopholes in every system.")
            type_text("You live well without ever breaking the letter of the law.")
        elif choice == 5:  # Lawful Good
            player = update_alignment(player, -30, -30, "lawful_good")
            type_text("\nYou dedicate your life to public service.")
            type_text("You make genuine change from within the system.")
        elif choice == 6:  # Lawful Evil
            player = update_alignment(player, -20, 30, "lawful_evil")
            type_text("\nYou rise in politics through corruption and blackmail.")
            type_text("You're powerful, wealthy, and utterly ruthless.")
        elif choice == 7:  # Chaotic Good
            player = update_alignment(player, 25, -25, "chaotic_good")
            type_text("\nYou use your position to expose corruption.")
            type_text("You're hated by the powerful but loved by the people.")
        elif choice == 8:  # True Neutral
            player = update_alignment(player, 0, 0, "true_neutral")
            type_text("\nYou find a modest job, a small home, and peace.")
            type_text("You live an unremarkable but content life.")
        else:  # Neutral Good (choice == 9)
            player = update_alignment(player, 0, -30, "neutral_good")
            type_text("\nYou found charities and help those in need.")
            type_text("Your compassion touches thousands of lives.")
    
    else:
        type_text("\nYou choose freedom and independence.")
        choices = [
            "Burn everything",
            "Create your own rules",
            "Take what you want",
            "Live for thrill alone",
            "Become a wandering helper",
            "Build a criminal empire",
            "Fight for others' freedom",
            "Wander without purpose",
            "Live self-sufficiently"
        ]
        
        choice = show_choices(choices)
        
        if choice == 1:  # Chaotic Evil
            player = update_alignment(player, 40, 45, "chaotic_evil")
            type_text("\nYou dedicate your life to pure destruction and chaos.")
            type_text("You become a force of nature that civilization cannot contain.")
        elif choice == 2:  # Lawful Neutral
            player = update_alignment(player, -15, 0, "lawful_neutral")
            type_text("\nYou establish your own micronation with strict laws.")
            type_text("You rule absolutely but fairly over your small domain.")
        elif choice == 3:  # Neutral Evil
            player = update_alignment(player, 0, 35, "neutral_evil")
            type_text("\nYou take whatever you want from whoever has it.")
            type_text("You answer to no one and live solely for your own pleasure.")
        elif choice == 4:  # Chaotic Neutral
            player = update_alignment(player, 25, 0, "chaotic_neutral")
            type_text("\nYou seek the ultimate thrill in every experience.")
            type_text("You cheat death daily and live completely in the moment.")
        elif choice == 5:  # Lawful Good
            player = update_alignment(player, -10, -25, "lawful_good")
            type_text("\nYou travel from town to town, helping where needed.")
            type_text("You become a legend - the stranger who fixes problems.")
        elif choice == 6:  # Lawful Evil
            player = update_alignment(player, -15, 30, "lawful_evil")
            type_text("\nYou build an organized crime syndicate with strict codes.")
            type_text("You control underground empires with an iron fist.")
        elif choice == 7:  # Chaotic Good
            player = update_alignment(player, 30, -20, "chaotic_good")
            type_text("\nYou become a freedom fighter, liberating the oppressed.")
            type_text("You're wanted by authorities but worshipped by rebels.")
        elif choice == 8:  # True Neutral
            player = update_alignment(player, 0, 0, "true_neutral")
            type_text("\nYou wander without destination or purpose.")
            type_text("You experience everything but commit to nothing.")
        else:  # Neutral Good (choice == 9)
            player = update_alignment(player, 0, -20, "neutral_good")
            type_text("\nYou build a sustainable home in the wilderness.")
            type_text("You live in harmony with nature, helping those who find you.")
    
    player.choices_history.append(f"Final path: Choice {choice}")
    show_stats(player)
    return player

# ===== Main Game Loop =====
def main():
    """Main game function"""
    type_text("="*60)
    type_text("                      UTOPIAN SANDS")
    type_text('            "play god in your personal sandbox"')
    type_text("="*60)
    
    type_text("\nA text-based adventure that reveals your true moral alignment.")
    type_text("Based on the classic ninefold alignment system from tabletop RPGs.")
    type_text("\nThere are no right or wrong answers:")
    type_text("\nOnly your truth.")
    
    # Menu
    type_text("\n" + "-"*30)
    type_text("MAIN MENU")
    type_text("-"*30)
    type_text("[1] Start New Game")
    type_text("[2] Load Saved Game")
    type_text("[3] Quit")
    
    menu_choice = input("\nEnter choice (1-3): ")
    
    if menu_choice == "3":
        type_text("\nGoodbye.")
        return
    
    # Create or load player
    player = None
    event_counter = 0
    
    if menu_choice == "2":
        player, event_counter = load_game()
    
    if player is None:
        # Create new player
        type_text("\n" + "-"*30)
        type_text("CHARACTER CREATION")
        type_text("-"*30)
        player_name = input("Enter your name: ").strip()
        if not player_name:
            player_name = "Stranger"
        
        player = Player(player_name, "Utopian Society")
        type_text(f"\nWelcome, {player_name}.")
        type_text("\nRemember: There are no 'right' or 'wrong' choices.")
        type_text("Only choices that reveal who you truly are.")
        input("\nPress Enter to begin your journey...")
    
    # Game events in sequence
    events = [
        event_1,  # The Fall
        event_2,  # Aftermath
        event_3,  # Stray Dog
        event_4,  # Shelter Houses
        event_5,  # Police Encounter
        event_6,  # Truth Reveal
        event_7   # Final Choice
    ]
    
    # Play events
    while event_counter < len(events) and not check_game_over(player):
        # Show event counter
        type_text(f"\n[Event {event_counter + 1} of {len(events)}]")
        
        # Play next event
        player = events[event_counter](player)
        event_counter += 1
        
        # Check for save/quit option
        if not check_game_over(player) and event_counter < len(events):
            type_text("\n" + "-"*30)
            type_text("Options: [c]ontinue, [s]ave, [q]uit, [v]iew stats")
            option = input("Choose: ").lower()
            
            if option == "s":
                save_game(player, event_counter)
                continue
            elif option == "q":
                type_text("\nGame saved. Come back soon to continue your journey!")
                save_game(player, event_counter)
                return
            elif option == "v":
                show_stats(player)
                input("\nPress Enter to continue...")
    
    # Game Ending
    if not check_game_over(player):
        # Determine final alignment
        alignment, most_common = determine_final_alignment(player)
        
        # Show final ending
        show_ending(player, alignment, most_common)
        
        # Ask to save final game
        type_text("\nWould you like to save your final results?")
        if input().lower() == "y":
            save_game(player, event_counter)
        
        # Show play again option
        type_text("\nPlay again to explore different alignments!")
        if input().lower() == "y":
            main()

# ===== Start Game =====
if __name__ == "__main__":
    main()