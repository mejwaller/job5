#see http://matplotlib.org/examples/pylab_examples/barchart_demo.html

import numpy as np
import matplotlib.pyplot as plt

n_stories=5

ests=(26,40,10,47,33)
acts=(33.5,99,11.5,27,38.5)
bugs=(6.5,17,2,0,0.5)

fig,ax=plt.subplots()

index=np.arange(n_stories)

bar_width=0.3

est_rects=plt.bar(index,ests,bar_width,color='g',label="Estimates")
act_rects=plt.bar(index+bar_width,acts,bar_width,color='r',label="Actual")
bug_rects=plt.bar(index+2*bar_width,bugs,bar_width,color='b',label="Bug hrs")

plt.xlabel('Story')
plt.ylabel('hours')
plt.title('estimates,actuals and bug hours per story (*=unfinished')

plt.xticks(index+bar_width,("align w/ bag\n(4 bugs)","capture reg*\n(10 bugs)","disp t&cs*\n(3 bugs)","create card pmnt*\n(0 bugs)","design ref. cntry and eml*\n(9 bugs)"))
plt.legend()

#plt.tight_layout()
plt.show()

