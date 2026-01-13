"""Data models for the champPackage core module."""
from .debug_logger import *

class ClassInfo:
    def __init__(self, class_type, class_number = None, order = 0, running_orders_url = None, results_url = None):
        """information about a specific class within a show"""
        self.class_type = class_type
        # self.status = status
        self.order = order
        self.running_orders_url = running_orders_url
        self.results_url = results_url
        self.class_number = class_number
        self.status = None  # e.g., "completed", "in progress", "not started"
        self.order_hierarchy = {"first": 0, "second": 1, "same state": 2}

        self.results_df = None  # DataFrame to hold results
        self.eliminations = []  # List to hold eliminations
        self.running_orders_df = None  # DataFrame to hold running orders

    def __repr__(self):
        results_message = 0
        if self.results_df is not None:
            results_message = f"results_df={len(self.results_df)} rows"
        return (f"ShowClassInfo(\n"
                f"  class_type={self.class_type},\n"
                f"  status={self.status},\n"
                f"  order={self.order},\n"
                f"  running_orders_url={self.running_orders_url},\n"
                f"  results_url={self.results_url},\n"
                f"  class_number={self.class_number}),\n"
                f"  results_df={results_message},\n"
                f"  eliminations={len(self.eliminations)})")
    
    def update_status(self):
        if self.running_orders_url and self.results_url:
            self.status = 'in progress'
        elif self.results_url and not self.running_orders_url:
            self.status = 'completed'
        elif self.running_orders_url and not self.results_url:
            self.status = 'not started'
        else:
            self.status = 'not started, no running orders'

    def update_order(self, other):
        status_hierarchy = {"completed": 0, "in progress": 1, "not started": 2}
        if status_hierarchy[self.status] < status_hierarchy[other.status]:
            self.order = 0
            other.order = 1
        elif status_hierarchy[self.status] > status_hierarchy[other.status]:
            self.order = 1
            other.order = 0
        else:
            self.order = 2
            other.order = 2

class Final:
    def __init__(self, jumpingClass: ClassInfo, agilityClass: ClassInfo):
        """information about the final show"""
        self.jumpingClass = jumpingClass
        self.agilityClass = agilityClass
        
        self.status = self.update_status()
        self.final_results_df = None  # DataFrame to hold final combined results
        self.combination_method = None  # e.g., "resultsBased", "positionBased"

        self.jumpingWinner = []
        self.agilityWinner = []


    def update_status(self):
        if self.jumpingClass.status == 'completed' and self.agilityClass.status == 'completed':
            self.status = 'final running order'
        elif ((self.jumpingClass.status == 'in progress' and self.agilityClass.status == 'completed') or
             (self.jumpingClass.status == 'completed' and self.agilityClass.status == 'in progress')):
            self.status = 'partial running order'
        elif (self.jumpingClass.status == 'not started' and self.agilityClass.status == 'not started'):
            self.status = 'not started'
        elif (self.jumpingClass.status == 'in progress' or self.agilityClass.status == 'in progress'):
            self.status = 'in progress'
        else:
            self.status = 'not started'

    def combine_resultsBased(self):
        """combine results from both classes to create final results. combination via run results (e.g. jumping faults + agility faults). This is Crufts singles style."""
        self.combination_method = "resultsBased"

        # Load round dataframes
        jumping_df = self.jumpingClass.results_df
        agility_df = self.agilityClass.results_df

    def combine_positionBased(self):
        """combine results from both classes to create final results. combination via positions (e.g. 1st in jumping + 2nd in agility = 3 overall points). This is Champ style."""
        self.combination_method = "positionBased"

        # Load round dataframes
        jumping_df = self.jumpingClass.results_df
        agility_df = self.agilityClass.results_df
    
        winners_list = []
        first_class = None
        second_class = None
        if self.jumpingClass.order < self.agilityClass.order:
            first_class = self.jumpingClass
            second_class = self.agilityClass
        else:
            first_class = self.agilityClass
            second_class = self.jumpingClass

        # row = first_class.results_df.iloc[0]
        for i, row in first_class.results_df.iterrows():
            
            score = {'faults': row['Faults'], 'time': row['Time']}
            pairing = pairingInfo(row['Name'])
            pairing.set_jumping_results(row['Rank'], score)

            # Look for matching pairing in agility results
            agility_match = second_class.results_df[second_class.results_df['Name'] == row['Name']]
            ag_elimMatch = second_class.eliminations
            if not agility_match.empty:
                ag_row = agility_match.iloc[0]
                ag_score = {'faults': ag_row['Faults'], 'time': ag_row['Time']}
                pairing.set_agility_results(ag_row['Rank'], ag_score)
            # elif 
            else:
                print_debug(f"No matching agility result for {row['Name']}")
    

            if i == 0:
                winners_list.append(pairing)



        print_debug(pairing)
                       
        
        # print_debug(jumping_df.head())

class pairingInfo:
    def __init__(self, pairingName):
        """information about a specific pairing of dog and handler"""
        self.pairingName = pairingName

        self.jumpingRank = None
        self.agilityRank = None
        self.jmpScore = None
        self.agScore = None
        self.finalRank = None

        self.champFinalPoints = None
        self.combinedFaults = None
        self.combinedTime = None
        self.requiredScore = None
    
    def set_jumping_results(self, position, score):
        self.jumpingRank = position
        self.jmpScore = score
    
    def set_agility_results(self, position, score):
        self.agilityRank = position
        self.agScore = score

    def __repr__(self):
        return f"pairingInfo(\n" \
        f"  pairingName={self.pairingName},\n" \
        f"  jumpingRank={self.jumpingRank},\n" \
        f"  agilityRank={self.agilityRank},\n" \
        f"  jmpScore={self.jmpScore},\n" \
        f"  agScore={self.agScore},\n" \



if __name__ == "__main__":
    from .plaza_scraper import *
    from .plaza_resultsRunningOrder import *


    simulation_soup = read_from_file(os.path.join("NorthDerbySaves", "NorthDerbyShow_SecondClass.html"))
    agility_class, jumping_class = find_champ_classes(simulation_soup, 'Lge')

    jumping_class.results_df, jumping_class.eliminations = import_results(jumping_class, simulation=True)
    agility_class.results_df, agility_class.eliminations = import_results(agility_class, simulation=True)

    print_debug(agility_class)
    print_debug(jumping_class)
    # jumping_running_orders = import_running_orders(jumping_class, simulation=True)

    final = Final(jumping_class, agility_class)
    final.combine_positionBased()
