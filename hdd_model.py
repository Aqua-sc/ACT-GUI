
# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import sys

from util import format_carbon

class Fab_HDD():
    def __init__(self, config="BarraCuda"):
        ###############################
        # Carbon per capacity
        ###############################
        with open("hdd/hdd_consumer.json", 'r') as f:
            hdd_config = json.load(f)

        with open("hdd/hdd_enterprise.json", 'r') as f:
            hdd_config.update(json.load(f))

        assert config in hdd_config.keys() and "HDD configuration not found"

        comp_str = ""
        comp_str += f"CAPACITY\t= __CAP__ GB\n"

        self.carbon_per_gb = hdd_config[config]
        comp_str += f"CPS\t\t\t= {self.carbon_per_gb:.2f} g/GB\n"
        comp_str += f"\n"
        comp_str += f"E_HDD\t\t= CPS x CAPACITY\n"
        comp_str += f"\t\t\t= __TOTAL__"

        self.carbon        = 0
        self.computation_string = comp_str
        return

    def get_computation_string(self):
        return self.computation_string.replace("__CAP__", f"{self.capacity}").replace("__TOTAL__", format_carbon(self.carbon))

    def get_cpg(self, ):
        return self.carbon_per_gb

    def set_capacity(self, capacity):
        self.capacity = capacity
        self.carbon = self.carbon_per_gb * self.capacity

        return 

    def get_carbon(self, ):
        return self.carbon

