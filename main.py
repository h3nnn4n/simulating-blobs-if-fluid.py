from simulating_blobs_of_fluid.simulation import Simulation
from simulating_blobs_of_fluid.fluid_renderer import FluidRenderer

import arcade


def main():
    simulation = Simulation()
    FluidRenderer(simulation.box_width, 800, simulation)

    arcade.run()


if __name__ == "__main__":
    main()
