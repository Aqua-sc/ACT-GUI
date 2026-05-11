
# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import sys

from util import format_carbon

class Fab_DRAM():
    def __init__(self,  config = "ddr4_10nm", fab_yield=0.875):

        ###############################
        # Carbon per capacity
        ###############################
        with open("dram/dram_hynix.json", 'r') as f:
            dram_config = json.load(f)

        assert config in dram_config.keys() and "DRAM configuration not found"

        comp_str = ""
        comp_str += f"CAPACITY\t= __CAP__ GB\n"

        self.fab_yield = fab_yield

        self.carbon_per_gb = dram_config[config] / self.fab_yield
        comp_str += f"CPS\t\t\t= {self.carbon_per_gb:.2f} g/GB\n"
        comp_str += f"\n"
        comp_str += f"E_DRAM\t\t= 1/{fab_yield:.3f} x CPS x CAPACITY\n"
        comp_str += f"\t\t\t= __TOTAL__"

        self.carbon        = 0
        self.computation_string = comp_str

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

