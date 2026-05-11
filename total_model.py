
# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import sys

from util import format_carbon

class Total_Logic():
    def __init__(self, 
            operational=0,
            embodied=0,
            lifetime=0,
            runtime=0,
            application_enabled=False
        ):


        ###############################
        # Aggregating model
        ###############################

        if not application_enabled:
            factor = 0
        elif lifetime == 0:
            factor = 1
        else:
            factor = runtime/lifetime
        
        comp_str = ""
        comp_str += f"OP_CF\t= {operational:.2f} g CO2\n"
        comp_str += f"E_CF\t= {embodied:.2f} g CO2\n"
        comp_str += f"T/LT\t= "
        if not application_enabled or lifetime == 0:
            comp_str += f"{factor} (disabled or lifetime 0)\n"
        else:
            comp_str += f"{runtime:.2f} h/{lifetime:.2f} h = {factor:.2f}\n"
        self.carbon = operational + factor * embodied

        comp_str += "\n"
        comp_str += f"CF\t\t= OP_CF + T/LT x E_CF = {format_carbon(self.carbon)}"

        self.computation_string = comp_str
        return 

    def get_computation_string(self):
        return self.computation_string

    def get_carbon(self, ):
        return self.carbon


