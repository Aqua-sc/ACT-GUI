# ACT: Architectural Carbon Modeling Tool - GUI Extension

From the [original ACT repository:](https://github.com/alugupta/ACT)

> ACT is an carbon modeling tool to enable carbon-aware design space exploration. ACT comprises an analytical, architectural carbon-footprint model and use-case dependent optimization metrics to estimate the carbon footprint of hardware. The proposed model estimates emissions from hardware manufacturing (i.e., embodied carbon) based on workload characteristics, hardware specifications, semiconductor fab characteristics, and environmental factors.
> 
> ACT addresses a crucial gap in quantifying and enabling sustainability-driven hardware design space exploration, and serves as a call-to-action for computer architects to consider sustainability as a first-order citizen, alongside performance, power, and area (PPA).

This projects completes the implementation of the full ACT model and extends it with a graphical user interface. For any details regarding the model or python models, refer to the [original repository](https://github.com/alugupta/ACT)

## Starting the GUI

* Install all packages specified in `requirements.txt`
* Run `python app.py`

## Acknowledgements

This project is based on ACT (Architectural Carbon Modeling Tool):

Gupta et al., "ACT: Designing Sustainable Computer Systems with an
Architectural Carbon Modeling Tool", ISCA 2022.

Original repository:
https://github.com/alugupta/ACT

The original ACT implementation is licensed under the MIT License.

This project extends ACT by:
- Implementing additional parameters from the paper
- Adding a graphical user interface
- Adding interactive graph visualizations

# License
ACT is MIT licensed, as found in the LICENSE file.
