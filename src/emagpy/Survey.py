#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 20:27:12 2019

@author: jkl
"""
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
#from pykrige.ok import OrdinaryKriging
from scipy.stats import linregress, binned_statistic
from scipy.spatial.distance import cdist, pdist
from scipy.interpolate import griddata
from scipy.spatial import Delaunay
from scipy.spatial import ConvexHull


def clipConvexHull(xdata,ydata,x,y,z):
    """ set to nan data outside the convex hull of xdata, yxdata
    
    Parameters:
        xdata, ydata (arrays) : x and y position of the data collected
        x, y (arrays) : x and y position of the computed interpolation points
        z (arrays) : value of the interpolation
    
    Return:
        znew (array) : a copy of z with nan when outside convexHull
    """
    knownPoints = np.array([xdata, ydata]).T
    newPoints = np.array([x,y]).T
    _, idx = np.unique(xdata+ydata, return_index=1)
    q = ConvexHull(knownPoints[idx,:])
    hull = Delaunay(q.points[q.vertices, :])
#    qq = q.points[q.vertices,:]
        
    znew = np.copy(z)
    for i in range(0, len(z)):
        if hull.find_simplex(newPoints[i,:])<0:
            znew[i] = np.nan
    return znew


def idw(xnew, ynew, xknown, yknown, zknown):
    znew = np.zeros(len(xnew))
    for i,(x,y) in enumerate(zip(xnew, ynew)):
#        dist = pdist(x, y, xknown, yknown)
        dist = np.sqrt((x-xknown)**2+(y-yknown)**2)
        # if we consider all the points (might be not good)
        w = (1/dist)**2 # exponent to be chosen
        znew[i] = np.sum(zknown*w)/np.sum(w)
    return znew


class Survey(object):
    ''' Create a Survey object containing the raw EMI data.
    Raw EMI file is
    '''
    def __init__(self, fname=None, freq=None, hx=None):
        self.df = None # main dataframe
        self.freqs = [] # frequency of each coil [Hz]
        self.errorModel = None # a function that returns an error
        self.sensor = None # sensor name (+ company)
        self.coils = [] # columns with the coils names and configuration
        self.cpos = [] # orientation of the coils
        self.cspacing = [] # spacing between Tx and Rx [m]
        self.coilsInph = [] # name of the coils with inphase value in [ppt]
        self.hx = [] # height of the instrument above the ground [m]
        self.name = ''
        if fname is not None:
            self.readFile(fname)
            if freq is not None:
                self.freqs = np.ones(len(self.coils))*freq
            if hx is not None:
                self.hx = np.ones(len(self.coils))*hx

        
    
    def readFile(self, fname, sensor=None):
        self.name = os.path.basename(fname)[:-4]
        df = pd.read_csv(fname)
        for c in df.columns:
            orientation = c[:3]
            if ((orientation == 'VCP') | (orientation == 'VMD') | (orientation == 'PRP') |
                    (orientation == 'HCP') | (orientation == 'HMD')):
                # replace all orientation in HCP/VCP/PRP mode
                if orientation == 'HMD':
                    df = df.rename(columns={c:c.replace('HMD','VCP')})
                if orientation == 'VMD':
                    df = df.rename(columns={c:c.replace('VMD','HCP')})
                if c[-5:] == '_inph':
                    self.coilsInph.append(c)
                else:
                    self.coils.append(c)
        if 'x' not in df.columns:
            df['x'] = 0
        if 'y' not in df.columns:
            df['y'] = 0 # maybe not needed
        coilInfo = [self.getCoilInfo(c) for c in self.coils]
        self.freqs = [a['freq'] for a in coilInfo]
        self.hx = [a['height'] for a in coilInfo]
        self.cspacing = [a['coilSeparation'] for a in coilInfo]
        self.cpos = [a['orientation'] for a in coilInfo]
        self.df = df
        self.sensor = sensor

        
    def getCoilInfo(self, arg):
        orientation = arg[:3].lower()
        b = arg[3:].split('f')
        coilSeparation = float(b[0])
        if len(b) > 1:
            c = b[1].split('h')
            freq = float(c[0])
            if len(c) > 1:
                height = float(c[1])
            else:
                height = 0
        else:
            freq = None
            height = 0
        return {'orientation': orientation,
                'coilSeparation': coilSeparation,
                'freq': freq,
                'height': height}
        
    
    def keepBetween(self, vmin=None, vmax=None):
        '''Filter out measurements that are not between vmin and vmax.
        
        Parameters
        ----------
        vmin : float, optional
            Minimal ECa value, default is minimum observed.
        vmax : float, optional
            Maximum ECa value, default is maximum observed.
        '''
        if vmin is not None:
            ie1 = (self.df[self.coils].values > vmin).all(1)
        else:
            ie1 = np.ones(self.df.shape[0], dtype=bool)
        if vmax is not None:
            ie2 = (self.df[self.coils].values < vmax).all(1)
        else:
            ie2 = np.ones(self.df.shape[0], dtype=bool)
        ie = ie1 & ie2
        print('Deleted {:d}/{:d} measurements'.format(np.sum(~ie), len(ie)))
        self.df = self.df[ie]
        
        
    def rollingMean(self, window=3):
        '''Perform a rolling mean on the data.
        
        Parameters
        ----------
        window : int, optional
            Size of the windows for rolling mean.
        '''
        for coil in self.coils:
            self.df[coil] = self.df[coil].rolling(window).mean()
        
    
    def show(self, coil='all', attr='ECa', ax=None, contour=False, vmin=None, 
             vmax=None, pts=False):
        ''' Show the data.
        '''
        if coil == 'all':
            cols = self.coils
        else:
            cols = coil
        
        if ax is None:
            fig, ax = plt.subplots()
       
        ax.set_title(coil)
        ax.plot(self.df[cols].values, 'o-')
        ax.legend(cols)
        ax.set_ylim([vmin, vmax])
        ax.set_xlabel('Measurements')
        if coil[-5:] == '_inph':
            ax.set_ylabel('Inphase [ppt]')
        else:
            ax.set_ylabel('Apparent Conductivity [mS/m]')
        

    def tcorrECa(self, tdepths, tprofile):
        '''Temperature correction using XXXX formula.
        
        Parameters
        ----------
        tdepths : array-like
            Depths in meters of the temperature sensors (negative downards).
        tprofile : array-like
            Temperature values corresponding in degree Celsius.
        '''
        # TODO if ECa -> compute an 'apparent' temperature
        # TODO what about per survey ?
        pass


    def convertFromNMEA(self, targetProjection='EPSG:27700'): # British Grid 1936
        ''' Convert NMEA string to selected CRS projection.
        
        Parameters
        ----------
        targetProjection : str, optional
            Target CRS, in EPSG number: e.g. `targetProjection='EPSG:27700'`
            for the British Grid.
        '''
        import pyproj
        
        df = self.df
        def func(arg):
            """ Convert NMEA string to WGS84 (GPS) decimal degree.
            """
            letter = arg[-1]
            if (letter == 'W') | (letter == 'S'):
                sign = -1
            else:
                sign = 1
            arg = arg[:-1]
            x = arg.index('.')
            a = float(arg[:x-2]) # degree
            b = float(arg[x-2:]) # minutes
            return (a + b/60)*sign
        gps2deg = np.vectorize(func)
        
        df['lat'] = gps2deg(df['Latitude'].values)
        df['lon'] = gps2deg(df['Longitude'].values)
        
        wgs84 = pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth
        osgb36 = pyproj.Proj("+init=" + targetProjection) # UK Ordnance Survey, 1936 datum
        
        df['x'], df['y'] = pyproj.transform(wgs84, osgb36, 
                                              df['lon'].values, df['lat'].values)
        self.df = df

    
    def showMap(self, coil=None, contour=False, ax=None, vmin=None, vmax=None,
                pts=False):
        ''' Display a map of the measurements.
        
        Parameters
        ----------
        coil : str, optional
            Name of the coil to plot. By default, the first coil is plotted.
        contour : bool, optional
            If `True` filled contour will be plotted using `tricontourf`.
        ax : Matplotlib.Axes, optional
            If specified, the graph will be plotted against the axis.
        vmin : float, optional
            Minimum of the colorscale.
        vmax : float, optional
            Maximum of the colorscale.
        pts : bool, optional
            If `True` the measurements location will be plotted on the graph.
        '''
        if coil is None:
            coil = self.coils[0]
        x = self.df['x'].values
        y = self.df['y'].values
        val = self.df[coil].values
        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.figure
        if vmin is None:
            vmin = np.nanpercentile(val, 5)
        if vmax is None:
            vmax = np.nanpercentile(val, 95)
        ax.set_title(coil)
        if contour is True:
            levels = np.linspace(vmin, vmax, 7)
            cax = ax.tricontourf(x, y, val, levels=levels, extend='both')
            if pts is True:
                ax.plot(x, y, 'k+')
        else:
            cax = ax.scatter(x, y, s=15, c=val, vmin=vmin, vmax=vmax)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        if coil[-5:] == '_inph':
            fig.colorbar(cax, ax=ax, label='Inphase [ppt]')
        else:
            fig.colorbar(cax, ax=ax, label='Conductivity [mS/m]')
        

    
    def pointsKiller(self):
        '''Interactively kill points. Then save df after that.
        '''
        pass
        
    
    
    def gridData(self, nx=100, ny=100, method='idw'):
        ''' Grid data (for 3D).
        
        Parameters
        ----------
        nx : int, optional
            Number of points in x direction.
        ny : int, optional
            Number of points in y direction.
        method : str, optional
            Interpolation method (nearest, cubic or linear see
            `scipy.interpolate.griddata`) or IDW (default).
        '''
        x = self.df['x'].values
        y = self.df['y'].values
        X, Y = np.meshgrid(np.linspace(np.min(x), np.max(x), nx),
                           np.linspace(np.min(y), np.max(y), ny))
        inside = np.ones(nx*ny)
        inside2 = clipConvexHull(self.df['x'].values,
                                 self.df['y'].values,
                                 X.flatten(), Y.flatten(), inside)
        ie = ~np.isnan(inside2)
        df = pd.DataFrame()
        df['x'] = X.flatten()
        df['y'] = Y.flatten()
        for coil in self.coils:
            values = self.df[coil].values
            if method == 'idw':
                z = idw(X.flatten(), Y.flatten(), x, y, values)
            else:
                z = griddata(np.c_[x, y], values, (X, Y), method=method)
            df[coil] = z.flatten()
        self.dfg = df[ie]
        # TODO add OK kriging ?
        
    
    def crossOverPoints(self, coil=None, ax=None, ax1=None, iplot=True):
        ''' Build an error model based on the cross-over points.
        
        Parameters
        ----------
        coil : str, optional
            Name of the coil.
        ax : Matplotlib.Axes, optional
            Matplotlib axis on which the plot is plotted against if specified.
        '''
        if coil is None:
            coil = self.coils[0]
        df = self.df
        dist = cdist(df[['x', 'y']].values,
                     df[['x', 'y']].values)
        minDist = 1 # points at less than 1 m from each other are identical
        ix, iy = np.where(((dist < minDist) & (dist > 0))) # 0 == same point
        ifar = (ix - iy) > 200 # they should be at least 200 measuremens apart
        ix, iy = ix[ifar], iy[ifar]
        print('found', len(ix), '/', df.shape[0], 'crossing points')
        
        # plot cross-over points
        xcoord = df['x'].values
        ycoord = df['y'].values
        icross = np.unique(np.r_[ix, iy])
        
        if iplot is True:
            if ax1 is None:
                fig1, ax1 = plt.subplots()
            ax1.set_title(coil)
            ax1.plot(xcoord, ycoord, '.')
            ax1.plot(xcoord[icross], ycoord[icross], 'ro', label='crossing points')
            ax1.set_xlabel('x [m]')
            ax1.set_ylabel('y [m]')

            
        val = df[coil].values
        x = val[ix]
        y = val[iy]
        means = np.mean(np.c_[x,y], axis=1)
        error = np.abs(x - y)
        
        # bin data (constant number)
        nbins = 30 # number of data per bin
        end = int(np.floor(len(means)/nbins)*nbins)
        errorBinned = error[:end].reshape((-1, nbins)).mean(axis=1)
        meansBinned = means[:end].reshape((-1, nbins)).mean(axis=1)
        
        # bin data (constant width)
        errorBinned, binEdges, _ = binned_statistic(
                means, error, 'mean', bins=20)
        meansBinned = binEdges[:-1] + np.diff(binEdges)

        # compute model
        inan = ~np.isnan(meansBinned) & ~np.isnan(errorBinned)
        inan = inan & (meansBinned > 0) & (errorBinned > 0)
        slope, intercept, r_value, p_value, std_err = linregress(
                np.log10(meansBinned[inan]), np.log10(errorBinned[inan]))
        
        self.df[coil + '_err'] = intercept + slope * self.df[coil]
            
        # plot
        if iplot is True:
            if ax is None:
                fig, ax = plt.subplots()
            ax.set_title(coil)
            ax.loglog(means, error, '.')
            ax.loglog(meansBinned, errorBinned, 'o')
            predError = 10**(intercept + slope * np.log10(means))
            eq = r'$\epsilon = {:.2f} \times \sigma^{{{:.2f}}}$'.format(10**intercept, slope)
            isort = np.argsort(means)
            ax.loglog(means[isort], predError[isort], 'k-', label=eq)
            ax.legend()
            ax.set_xlabel(r'Mean $\sigma_a$ [mS/m]')
            ax.set_ylabel(r'Error $\epsilon$ [mS/m]')
     

    
    def gfCorrection(self):
        ''' Apply the correction due to the 1m calibration.
        '''
        
    def importGF(self, fnameLo, fnameHi, device='Mini-Explorer', hx=0):
        '''Import GF instrument data with Lo and Hi file mode. If spatial data
        a regridding will be performed to match the data.
        
        Parameters
        ----------
        fnameLo : str
            Name of the file with the Lo settings.
        fnameHi : str
            Name of the file with the Hi settings.
        device : str, optional
            Type of device. Default is Mini-Explorer.
        hx : float, optional
            Height of the device above the ground in meters.
        '''
        self.name = os.path.basename(fnameLo)[:-4]
        loFile = pd.read_csv(fnameLo, sep='\t')
        hiFile = pd.read_csv(fnameHi, sep='\t')

        if device == 'Mini-Explorer':
            freq = 30000
            csep = [0.32, 0.71, 1.18]
        elif device == 'Explorer':
            freq = 10000
            csep = []# TODO
        else:
            raise ValueError('Device ' + device + ' unknown.')

        loCols = ['VCP{:.2f}'.format(a) for a in csep]
        hiCols = ['HCP{:.2f}'.format(a) for a in csep]
        loCols += [a + '_inph' for a in loCols]
        hiCols += [a + '_inph' for a in hiCols]
        cols = ['Cond.1[mS/m]', 'Cond.2[mS/m]', 'Cond.3[mS/m]',
                'Inph.1[ppt]', 'Inph.2[ppt]', 'Inph.3[ppt]']
        loFile = loFile.rename(columns=dict(zip(cols, loCols)))
        hiFile = hiFile.rename(columns=dict(zip(cols, hiCols)))
        
        if 'Latitude' not in loFile.columns and 'Latitude' not in hiFile.columns:
            if loFile.shape[0] == hiFile.shape[0]:
                print('importGF: joining on rows.')
                df = loFile[loCols].join(hiFile[hiCols])
                df['x'] = np.arange(df.shape[0])
                df['y'] = 0
            else:
                raise ValueError('Can not join the dataframe as they have different lengths: {:d} and {:d}'.format(loFile.shape[0], hiFile.shape[0]))
        else:
            pass
            # TODO regridding here :/
        
        self.coils = loCols[:3] + hiCols[:3]
        self.coilsInph = loCols[3:] + hiCols[3:]
        coilInfo = [self.getCoilInfo(c) for c in self.coils]
        self.freqs = np.repeat([freq], len(self.coils))
        self.hx = np.repeat([hx], len(self.coils))
        self.cspacing = [a['coilSeparation'] for a in coilInfo]
        self.cpos = [a['orientation'] for a in coilInfo]
        self.df = df
        self.sensor = device
        
        


#%% test


if __name__ == '__main__':
    #s = Survey('test/coverCrop.csv')
    #s.show(coils='HCP0.32')
    #s.showMap(contour=True, vmax=40)
    
#    s = Survey('test/potatoesLo.csv')
#    s.show(s.coils[1])
#    s.keepBetween(-5,11)
#    s.rollingMean(10)
#    s.show()
    
#    s.convertFromNMEA()
#    s.showMap(contour=True)
#    s.crossOverPoints(s.coils[1])
#    s.gridData(method='idw')
#    s.showMap(s.coils[1])
#    s.df = s.dfg
#    s.showMap(s.coils[1], contour=True)



#%%

    s = Survey()
    s.importGF('test/coverCropLo.dat', 'test/coverCropHi.dat')
    