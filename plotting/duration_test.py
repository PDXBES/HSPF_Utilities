import numpy as np
from plotting import flow_duration_curve as fd
import matplotlib.pyplot as plt
import pandas as pd

# Create test data
np_array_one_dim = np.random.rayleigh(5, [1, 300])
np_array_75_dim = np.c_[np.random.rayleigh(11,[25, 300]),
                        np.random.rayleigh(10, [25, 300]),
                        np.random.rayleigh(8, [25, 300])]
df_one_dim = pd.DataFrame(np.random.rayleigh(9, [1, 300]))
df_75_dim = pd.DataFrame(np.c_[np.random.rayleigh(8, [25, 300]),
                               np.random.rayleigh(15, [25, 300]),
                               np.random.rayleigh(3, [25, 300])])
df_75_dim_transposed = pd.DataFrame(np_array_75_dim.transpose())

# Call the function with all different arguments
fig, subplots = plt.subplots(nrows=2, ncols=3)
ax1 = fd.flow_duration_curve(np_array_one_dim, ax=subplots[0, 0], plot=False,
                          axis=1, fdc_kwargs={"linewidth":0.5})
ax1.set_title("np array one dim\nwith kwargs")

ax2 = fd.flow_duration_curve(np_array_75_dim, ax=subplots[0,1], plot=False,
                          axis=1, log=False, percentiles=(0,100))
ax2.set_title("np array 75 dim\nchanged percentiles\nnolog")

ax3 = fd.flow_duration_curve(df_one_dim, ax=subplots[0,2], plot=False, axis=1,
                          log=False, fdc_kwargs={"linewidth":0.5})
ax3.set_title("\ndf one dim\nno log\nwith kwargs")

ax4 = fd.flow_duration_curve(df_75_dim, ax=subplots[1,0], plot=False, axis=1,
                          log=False)
ax4.set_title("df 75 dim\nno log")

ax5 = fd.flow_duration_curve(df_75_dim_transposed, ax=subplots[1,1],
                          plot=False)
ax5.set_title("df 75 dim transposed")

ax6 = fd.flow_duration_curve(df_75_dim, ax=subplots[1,2], plot=False,
                          comparison=np_array_one_dim, axis=1,
                          fdc_comparison_kwargs={"color":"black",
                                                 "label":"comparison",
                                                 "linewidth":0.5},
                          fdc_range_kwargs={"label":"range_fdc"})
ax6.set_title("df 75 dim\n with comparison\nwith kwargs")
ax6.legend()

# Show the beauty
fig.tight_layout()
plt.show()