import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.basemap import Basemap

def plotStdErrorsOnMap(lons, lats, ses, numPts=None, basemap=None, ax=None,
                        ptids=None, clabel=None, vmax=None):
    basemap = basemap or Basemap()
    if ax is None:
        fig, ax = plt.subplots(1,1, figsize=(15,10))

    if numPts is None:
        s = 50
    else:
        normPts = numPts/float(max(numPts))
        s = 500*normPts

    clabel = clabel or 'Standard Error (m)'

    datamax = np.mean(np.abs(ses)) + np.std(np.abs(ses))
    datamag = np.floor(np.log10(datamax))
    if vmax is None:
        vmax = (10**datamag)*np.maximum(
                np.floor(datamax/(10**datamag))*2, 1.)

    if np.alltrue(ses >= 0):
        cmap = 'Reds'
        vmin = 0
    else:
        cmap = 'RdYlBu_r'
        vmin=-vmax


    basemap.drawcoastlines(color=(1,1,1,1), ax=ax, zorder=0)
    xs, ys = basemap(lons, lats)
    p = basemap.scatter(xs, ys, c=ses, s=s, 
                        vmin=vmin, vmax=vmax, cmap=cmap, 
                        ax=ax, edgecolor='None', alpha=0.5)
    ax.set_axis_bgcolor((0,0,0,0.2))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='2%', pad=0.05)
    plt.colorbar(p, cax=cax, label=clabel)

    if ptids is not None:
        for x, y, ptid in zip(xs, ys, ptids):
            ax.text(x, y, ptid, va='center', ha='center', fontsize=10,
            transform=ax.transData)

    # If scaling point size by number of points, add a label.
    if numPts is not None:
        samplept = int(5*10**(np.floor(np.log10(max(numPts)))-1))
        smaplept = np.floor((max(numPts) + min(numPts))/2)
        basemap.scatter([0.05], [0.05], c='k', alpha=0.75, 
                        s=500*samplept/float(max(numPts)),
                        vmin=vmin, vmax=vmax, ax=ax,
                        edgecolor='None', transform=ax.transAxes)
        ax.text(0.065, 0.05, '- {0:d} observations at site'.format(samplept),
            transform=ax.transAxes, va='center', fontsize=12)

    return ax

def plotLocTimeseries(data, calc, ax=None, title=False, nbr=False, **kwargs):
    if ax is None:
        fig, ax = plt.subplots(1,1)

    marker = kwargs.get('marker', '+')
    color = kwargs.get('color', 'k')
    alpha = kwargs.get('alpha', 1.0)
    ms = kwargs.get('ms', 15)
    ls = kwargs.get('ls', 'None')

    ax.plot(data.ts, data.ys, marker=marker, color=color, alpha=alpha,
            ms=ms, ls=ls)
    ax.plot(calc.ts, calc.ys)

    if title:
        ax.set_title(str(data))
    elif nbr:
        ax.set_title(data.recnbr)
    ax.invert_xaxis()
    return plt.gca()