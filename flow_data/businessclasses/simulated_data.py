from swmmtoolbox import swmmtoolbox
from flow_data.businessclasses.data import Data
import numpy as np

class SimulatedData(Data):
    def __init__(self, node_name=None, link_name=None):
        super().__init__()
        self.node_name = node_name
        self.link_name = link_name

    def _get_sim_timestep(self):
        self.time_step = np.timedelta64((self.flow_data.index.values[1] - self.flow_data.index.values[0]), 'm').astype(int)

    def get_sim_flow_data(self, outfile):
        self.flow_data = swmmtoolbox.extract(outfile, ['link', self.link_name, 'Flow_rate'])
        self._get_sim_timestep()

    def get_sim_depth_data(self, outfile):
        self.depth_data = swmmtoolbox.extract(outfile, ['node', self.node_name, 'Depth'])
        self._get_sim_timestep()


