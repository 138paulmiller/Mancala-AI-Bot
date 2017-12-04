# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 17:05:04 2017

@author: Presence
"""


# MatPlotlib
import matplotlib.pyplot as plt
from matplotlib import pylab

# Scientific libraries
import numpy as np

y = [76.0, 84.0, 96.0, 94.0, 78.0, 96.0, 94.0, 94.0, 82.0, 84.0, 98.0, 88.0, 82.0, 92.0, 94.0, 96.0, 90.0, 92.0, 92.0, 92.0]
x = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

#y = [73.33333333333333, 76.66666666666667, 93.33333333333333, 96.66666666666667, 96.66666666666667, 90.0, 93.33333333333333, 93.33333333333333, 96.66666666666667, 96.66666666666667, 90.0, 80.0, 93.33333333333333, 93.33333333333333, 93.33333333333333]
#x = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]


# calculate polynomial
z = np.polyfit(x, y,3)
f = np.poly1d(z)
print (f)

# calculate new x's and y's
x_new = np.linspace(x[0], x[-1], 50)
y_new = f(x_new)
plt.xlabel("Number of Simulations")
plt.ylabel("Win rate(%)")
plt.plot(x,y,'o', x_new, y_new)
pylab.title('Polynomial (3rd order) Regression')
#pylab.title('Linear Regression')
ax = plt.gca()
ax.set_axis_bgcolor((0.898, 0.898, 0.898))
fig = plt.gcf()
py.plot_mpl(fig, filename='polynomial-Fit-with-matplotlib')