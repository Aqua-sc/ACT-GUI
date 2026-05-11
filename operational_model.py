
# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import sys

from util import format_carbon

class Operational_Logic():
    def __init__(self, 
                    carbon_intensity="loc_taiwan",
                    debug=False,
                    energy=0
                ):

        self.debug = debug

        ###############################
        # Carbon intensity of use
        ###############################
        if "loc" in carbon_intensity:
            with open("carbon_intensity/location.json", 'r') as f:
                loc_configs = json.load(f)

                loc = carbon_intensity.replace("loc_", "")

                assert loc in loc_configs.keys()

                fab_ci = loc_configs[loc]

        elif "src" in carbon_intensity:
            with open("carbon_intensity/source.json", 'r') as f:
                src_configs = json.load(f)

                src = carbon_intensity.replace("src_", "")

                assert src in src_configs.keys()

                fab_ci = src_configs[src]

        else:
            print("Error: Carbon intensity must either be loc | src dependent")
            sys.exit()

        ###############################
        # Aggregating model
        ###############################
        comp_str = ""
        comp_str += f"CI_use\t= {fab_ci} g/J\n"
        comp_str += f"ENERGY\t= {energy} J\n"
        self.carbon = fab_ci * energy
        comp_str += "\n"
        comp_str += f"OP_CF\t = {format_carbon(self.carbon)}"

        self.computation_string = comp_str
        return

    def get_computation_string(self):
        return self.computation_string

    def get_carbon(self, ):
        return self.carbon


