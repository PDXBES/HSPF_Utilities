from flow_data.businessclasses.temporary_flow_monitor_data import TemporaryFlowMonitorData
from flow_data.businessclasses.simulated_data import SimulatedData
from plotting import flow_duration_curve as fd
import pandas as pd
import matplotlib.pyplot as plt

input_wdm = r"C:\Users\sgould\Desktop\Woods\Simple_with_control\hspf\input.wdm"
flow = "c:\\temp\\flow.dat"
sim_flow = "C:\\Users\\sgould\\Desktop\\woods\\Simple_with_control\\sim\D02yr6h\\D02yr6h.out"
sim_flow10 = "C:\\Users\\sgould\\Desktop\\woods\\Simple_with_control\\sim\D02yr6h10\\D02yr6h.out"
sim_flow172 = "C:\\Users\\sgould\\Desktop\\woods\\Simple_with_control\\sim\D02yr6h172\\D02yr6h.out"
h2_number = 4

begin_date = '2018-12-03 00:00:00'
end_date = '2020-01-06 00:00:00'

model_node = 'ADC182'
model_link = 'M76337' #M14422

location_id = 10519

simulated_data = SimulatedData(model_node, model_link)
simulated_data.get_sim_flow_data(sim_flow)
simulated_data10 = SimulatedData(model_node, model_link)
simulated_data10.get_sim_flow_data(sim_flow10)
simulated_data172 = SimulatedData(model_node, model_link)
simulated_data172.get_sim_flow_data(sim_flow172)

temp_monitor = TemporaryFlowMonitorData(location_id)
temp_monitor.get_raw_data(begin_date, end_date)
temp_monitor.get_visit_data(begin_date, end_date)
temp_monitor.filter_raw_data(15)

flow = temp_monitor.filtered_flow_data[temp_monitor.filtered_flow_data.columns[0]].values
df_obs_flow = pd.DataFrame(flow).dropna().transpose()

fig, subplots = plt.subplots(2)
flow = simulated_data10.flow_data[simulated_data10.flow_data.columns[0]].values
df_flow = pd.DataFrame(flow).transpose()

ax1 = fd.flow_duration_curve(df_obs_flow, ax=subplots[0],
                             plot=False, axis=1, log=True, percentiles=(1, 100))
ax1.set_title("10")

flow = simulated_data10.flow_data[simulated_data10.flow_data.columns[0]].values
df_flow = pd.DataFrame(flow).transpose()
ax1 = fd.flow_duration_curve(df_flow,
                             ax=subplots[0], plot=False, axis=1, log=True, percentiles=(1, 100))
#ax1.set_title("Rain Gage 10")

ax2 = fd.flow_duration_curve(df_obs_flow, ax=subplots[1],
                             plot=False, axis=1, log=True, percentiles=(1, 100))
ax2.set_title("172")

flow = simulated_data172.flow_data[simulated_data172.flow_data.columns[0]].values
df_flow = pd.DataFrame(flow).transpose()
ax2 = fd.flow_duration_curve(df_flow,
                             ax=subplots[1], plot=False, axis=1, log=True, percentiles=(1, 99))
#ax3.set_title("Rain Gage 172")

plt.show()
