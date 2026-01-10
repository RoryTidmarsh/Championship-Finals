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
