# Guildmaster.py

import GuildCreator
import QuestCreator
from random import randint, random, choice


'''
    AI as Guildmaster runs on a genetic algorithm where the individual is
    an instance of party composition, and the genome is a combination of 
    party members with their stats.
'''

# *** Determine range of levels required of party members
def level_range(difficulty):
  if 1 <= difficulty and difficulty <= 20:
    min_lvl, max_lvl = 5, 10

  elif 21 <= difficulty and difficulty <= 40:
    min_lvl, max_lvl = 11, 20

  elif 41 <= difficulty and difficulty <= 60:
    min_lvl, max_lvl = 21, 30

  elif 61 <= difficulty and difficulty <= 80:
    min_lvl, max_lvl = 31, 40

  elif 81 <= difficulty and difficulty <= 100:
    min_lvl, max_lvl = 41, 50

  else:
    min_lvl, max_lvl = 5, 50    #should never be the case

  return min_lvl, max_lvl


# *** Defines individual as a dictionary-type party of guild members, 
#     constrained by quest requirements.
#
#     Arguments: (dict) guild, (Object) quest
def individual(guild, quest):
  new_party = {}
  min_lvl, max_lvl = level_range(quest.diff)

  # determine required member type
  if quest._type == "bounty":
    quest_req = "Attacker"
  elif quest._type == "escort":
    quest_req = "Defender"
  elif quest._type == "fetch":
    quest_req = "Runner"

  # randomly choose party size <= specified max size 
  party_size = randint(1, quest.size)   

  # randomly assign a valid guild member to the party
  x = 0
  while x != party_size:
    some_member = choice(list(guild))

    #check for valid level
    if min_lvl <= guild[some_member].level and guild[some_member].level <= max_lvl:
      #check for valid type
      if guild[some_member]._type == quest_req:
        new_party[some_member] = guild[some_member]
        x += 1

  return new_party


# *** Generates a list-type population of party compositions
def population(guild, quest, count):
  party_pool = []
  while len(party_pool) != count:
    party_pool.append(individual(guild, quest))

  return party_pool


# *** Determines the success rate (AKA fitness) of a party for a certain quest
def fitness(party, quest):
  Atk_avg = 0
  Def_avg = 0
  Speed_avg = 0
  SucessRate = 0

  #Finds avg Atk stat
  for member in party:
    Atk_avg += party[member].attack
  Atk_avg = Atk_avg/len(party)

  #Finds avg Def stat
  for member in party:
    Def_avg += party[member].defense
  Def_avg = Def_avg/len(party)

  #Finds avg Speed stat
  for member in party:
    Speed_avg += party[member].speed
  Speed_avg = Speed_avg/len(party)

  '''
  Bounty: atk, spd, def
  Escort: def, atk,spd
  Fetch: spd, atk, def
  '''
  if quest._type is "bounty":
    Def_avg = Def_avg/2
    Speed_avg = Speed_avg/3
    PartyPoints = Atk_avg + Def_avg + Speed_avg
    SucessRate = (PartyPoints/quest.diff)*100
    return SucessRate
  
  if quest._type is "escort":
    Atk_avg = Atk_avg/2
    Speed_avg = Speed_avg/3
    PartyPoints = Atk_avg + Def_avg + Speed_avg
    SucessRate = (PartyPoints/quest.diff)*100
    return SucessRate
  
  if quest._type is "fetch":
    Atk_avg = Atk_avg/2
    Def_avg =Def_avg/3
    PartyPoints = Atk_avg + Def_avg + Speed_avg
    SucessRate = (PartyPoints/quest.diff)*100
    return SucessRate


# *** Find average success rate among all party compositions (used for comparison)
def grade(population, quest):
  total_fitness = 0
  for party in population:
    # print("The party fitness is: {}" .format(fitness(party, quest)))
    total_fitness += fitness(party, quest)

  return total_fitness / len(population)


# *** Selects pairs of parties with the most suitable members (good grade)
def selection(population, quest, grade):
  selected_parents = []
  for party in population:
    if fitness(party, quest) >= grade:
  #     print("The selected party fitness is: {}" .format(fitness(party, quest)))
      selected_parents.append(party)
  # print('\n')

  return selected_parents


# *** Takes the best members from either parent party to form a new party
def crossover(Parent1, Parent2, quest, guild):
  child_party = {}
  #For loop of one parent in another
  #Add all items to Child
  #Then while the size of the party is bigger than the Parent
  #For loop to get rid of the smallest elments
  child_party = {**Parent1,**Parent2}
  while len(child_party) > quest.size:
      dict1 = {next(iter(child_party)):child_party[(next(iter(child_party)))]}
      min_fitness =  fitness(dict1, quest)
      min = next(iter(child_party))
      for member in child_party:
        dict2={member:child_party[member]}
        if min_fitness >= fitness(dict2, quest):
           min_fitness = fitness(dict2, quest)
           min = member
      del child_party[min]
              # mutate some parties by replacing random party members          
  return mutate(child_party, guild)



# *** Switch some party member(s) around for possibly better results
def mutate(child_party, guild):
  # mutated_party = {}
  new_member = choice(list(guild))

  # ensures new_member isn't already in child_party
  while(new_member in child_party):
    new_member = choice(list(guild))

  # replaces a random original member with another outside the party
  some_member = choice(list(child_party))
  del child_party[some_member]
  child_party[new_member] = guild[new_member]

  return child_party  # this is now a mutated child
    

# *** Bulk of the genetic algorithm; finds best party out of all choices
def evolve(pop_count, guild, quest):
  new_population = []

  party_pool = population(guild, quest, pop_count)
  avg_fitness = grade(party_pool, quest)
  parent_parties = selection(party_pool, quest, avg_fitness)

  while(parent_parties):
    parent_1 = choice(parent_parties)
    parent_parties.remove(parent_1)     #ensures 2nd parent isn't the same
    new_population.append(parent_1)            

    parent_2 = choice(parent_parties)
    parent_parties.remove(parent_2)
    new_population.append(parent_2)

    # crossover two (parent) parties to create a better (child) party composition
    new_population.append(crossover(parent_1, parent_2, quest, guild))

    # randomly add other parties to promote genetic diversity (pending)

    best_party = choice(new_population)

    return best_party



# *** Main function (for testing; will possibly migrate to evolve())
#if __name__ == "__main__":

  # # # Builds the guild with random guild members of varying stats
  # guild = GuildCreator.generate()

  # # # Creates the quest for which a party will be assembled for
  # questBoard = {}
  # title, _type, diff, size = QuestCreator.create_quest()
  # questBoard[title] = QuestCreator.Quest(title, _type, diff, size)

  # # Creates the population of possible parties for the quest
  # pop_count = 100
  # party_pool = population(guild, questBoard[title], pop_count)
  # # i = 1
  # # for party in party_pool:
  # #   print("Party {}: " .format(i))
  # #   for member in party:
  # #     print(str(party[member]))
  # #   print('\n')
  # #   i += 1

  # # Finds the average success rate for the quest among all parties
  # avg_fitness = grade(party_pool, questBoard[title])
  # print("\nThe average party fitness is: {}\n" .format(avg_fitness))
  
  # # Selects parties if they are at or above the average success rate
  # parent_parties = selection(party_pool, questBoard[title], avg_fitness)
  # # for party in parent_parties:
  # #   for member in party:
  # #     print(str(party[member]))
  # #   print('\n')
  # print("The number of eligible parties to crossover is: {}" \
  #       .format(len(parent_parties)))

  # # Tests whether mutate() works
  # mutated_parties = []
  # for parent in parent_parties:
  #   mutated_parties.append(mutate(parent, guild))
  # # for mutant in mutated_parties:
  # #   for member in mutant:
  # #     print(str(mutant[member]))
  # #   print('\n')

  # # Creates new parties from existing parent parties



  # # Runs the genetic algorithm until a suitable party is made for each quest
  # for quest in questBoard:
  #     final_gen = sorted(evolve(guild, questBoard[quest]), key=Individual.fitness, reverse=True)
  #     best_party = final_gen[0]