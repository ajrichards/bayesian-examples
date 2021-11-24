#!/usr/bin/python
"""
This is a mixture of two gaussians example

We mode the proportion of one distribution with a random variable.

For the sample error it would be nice to use:

precision = Gamma('precision', alpha=0.1, beta=0.1

as it is the conjugate prior of the precision.

However, this produced odd results.  In order to get this example to 
work properly I had to modify the Uniform range for the precision parameter
until the results were reasonable.  Oddly enough increasing this range
will decrease DIC (good), but the visible fit is worse.

"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import pymc as mc

## example from elem. stat. learning book
book_mu1 = 4.62
book_mu2 = 1.06
book_var1 = 0.87
book_var2 = 0.77 
book_pi = 0.546

x1 = np.array([-0.39,0.12,0.94,1.67,1.76,2.44,3.72,4.28,4.92,5.53])
x2 = np.array([ 0.06,0.48,1.01,1.68,1.80,3.25,4.12,4.60,5.28,6.22])
x  = np.hstack([x1,x2])

## the mixing parameter
pi = mc.Uniform('pi',lower=0,upper=1)
delta = mc.Bernoulli( "delta",p=pi,size=x.size) # produces 1 with proportion p.

## other model parameters
sigma = mc.Uniform("sigma", 0.0,0.5)
var1 = mc.Uniform('var1',0,1)
var2 = mc.Uniform('var2',0,1)
mode1 = mc.Normal("mode1",mu=0,tau=var1**-2)
mode2 = mc.Normal("mode2",mu=0,tau=var2**-2)


@mc.deterministic(plot=False)
def mix_model(delta=delta,mode1=mode1,mode2=mode2):
    return (1.0-delta)*mode1 + delta*mode2

obs = mc.Normal("obs",mu=mix_model,tau=sigma**-2,value=x,observed=True)
model = mc.Model({"mode1":mode1,"mode2":mode2,"sigma":sigma,"pi":pi,
                  "var1":var1,"var2":var2,"obs":obs})

M = mc.MCMC(model)
M.sample(100000,50000)
mc.Matplot.plot(M)

## relabel the estimates if necessary
if M.trace('mode1')[:].mean() > M.trace('mode2')[:].mean():
    est_mu1  = M.trace('mode1')[:].mean()
    est_var1 = M.trace('var1')[:].mean()
    est_mu2  = M.trace('mode2')[:].mean()
    est_var2 = M.trace('var2')[:].mean()
    est_pi   = M.trace('pi')[:].mean() 
else:
    est_mu1  = M.trace('mode2')[:].mean()
    est_var1 = M.trace('var2')[:].mean()
    est_mu2  = M.trace('mode1')[:].mean()
    est_var2 = M.trace('var1')[:].mean()
    est_pi   = 1.0 - M.trace('pi')[:].mean() 


print 'book,model'
print 'mu1', book_mu1,est_mu1
print 'mu2', book_mu2,est_mu2
print 'var1', book_var1,est_var1
print 'var2', book_var2,est_var2
print 'pi', book_pi, est_pi
print 'DIC',M.dic

fig = plt.figure(1)
ax = fig.add_subplot(111)
n,bins,patches = ax.hist(x,15,normed=1,facecolor='gray',alpha=0.75)

p1 = mlab.normpdf(bins, book_mu1, np.sqrt(book_var1))
p2 = mlab.normpdf(bins, book_mu2, np.sqrt(book_var2))
l1 = plt.plot(bins, p1, 'r--', linewidth=1)
l2 = plt.plot(bins, p2, 'r--', linewidth=1)

## add a 'best fit' line (results from here)
p3 = mlab.normpdf(bins, est_mu1, np.sqrt(est_var1))
p4 = mlab.normpdf(bins, est_mu2, np.sqrt(est_var2))
l3 = plt.plot(bins, p3, 'k-', linewidth=1)
l4 = plt.plot(bins, p4, 'k-', linewidth=1)

plt.xlabel('x')
plt.ylabel('freq')
plt.ylim([0,0.8])

ax.legend((l1[0], l3[0]), ('Book Estimate', 'My Estimate') )
#plt.savefig('../TwoComponentGauss.png')
plt.show()
