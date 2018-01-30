import matplotlib.pyplot as plt
import pandas
import seaborn

pandas.read_csv('log.csv', header=None)[[1, 2]].plot()
plt.show()
