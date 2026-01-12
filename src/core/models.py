"""Data models for the champPackage core module."""


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
        self.running_orders_df = None  # DataFrame to hold running orders

    def __repr__(self):
        return (f"ShowClassInfo(class_type={self.class_type}, status={self.status}, "
                f"order={self.order}, running_orders_url={self.running_orders_url}, "
                f"results_url={self.results_url}, "
                f"class_number={self.class_number})")
    
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
        """combine results from both classes to create final results. combination via run results (e.g. jumping faults + agility faults)"""
        self.combination_method = "resultsBased"

    def combine_positionBased(self):
        """combine results from both classes to create final results. combination via positions (e.g. 1st in jumping + 2nd in agility = 3 overall points)"""
        self.combination_method = "positionBased"
    