# Import Python modules
import numpy as np
from matplotlib import pyplot as plt

# Import acuaponia modules
from acuaponia.dimensions import Qty
from acuaponia.classes import Module
from acuaponia.acuaplots import plot_lines

###TODO: Instead of importing p from FISH, declare them for feeder itself, 
# to avoid dependencies that may force a certain order when initializing
###TODO: Variable feed ratio. Perhaps as dictionary {mass_fish:daily_feed_ratio}

# ---- CLASS DEFINITION ----
# This object is based on the time of growth, with independent (re-)start
# The only objective of 'run' is to provide feed at specific tsim_i
class Feeder(Module):
    def __init__(self,tsim,dtsub,x0,p,Fish,status='growth'):
        Module.__init__(self,tsim,dtsub,x0,p)
        self.status = status
        self.y_units = {'f_feed':'g/s'}
        # -- Ideal fish growth --
        # Fish object. Initial conditions & parameters (already in base units)
        m0 = Fish.x0['m'][0]
        nfish0 = Fish.x0['nfish'][0]
        n = Fish.p['n']
        K = Fish.p['K']
        Tbase = Fish.p['Tbase']
        TUbase = Fish.p['TUbase']
        Tideal = Fish.p['Tideal']
        # Ideal growth
        dL_dt = (Tideal-Tbase)/TUbase
        L0 = (100*m0/nfish0/K)**(1/n)
        Lideal = L0 + dL_dt*self.tsubsim
        self.mideal = nfish0*0.01*K*Lideal**n
        # Index to correlate full ideal growth curve to submodel growth
        self.idx0 = 0
    
    def model(self,tsub,u,ut,x0,p):
        # Inputs, initial conditions & parameters
        t0_of_day = u['t0_of_day']
        daily_feed_ratio = p['daily_feed_ratio']
        daily_feed_schedule = p['daily_feed_schedule']
        feeds_per_day = p['daily_feed_schedule'].size
        if self.status == 'restart':
            self.status = 'growth'
            self.idx0 = 0
        if self.status == 'growth':
            # Indexes to correlate full ideal growth curve to submodel growth
            idx0 = self.idx0
            idx1 = self.idx0 + self.tsub.size-1
            # Ideal feed
            msub_ideal = self.mideal[idx0:idx1+1]
            tsub_of_day = tsub + t0_of_day
            dtsub = tsub[1]-tsub[0]
            switch = np.ones_like(tsub)
            switch = switch*np.isin(tsub_of_day,daily_feed_schedule)
            f_feed = switch*daily_feed_ratio*msub_ideal/feeds_per_day/dtsub            
            self.idx0 = idx1
        elif self.status == 'starve' or self.status == 'harvest' or self.status == 'stop':
            f_feed = np.zeros_like(tsub)
        return {'f_feed':f_feed.reshape((tsub.size,1))}

    
    def plots(self,save_figs=False):
        fig1 = plt.figure('Feeder-f_feed')
        x = [self.tsubsim.to('day'),]
        y1 = [self.logs['f_feed'].to('kg/hr'),]
        ax1 = plt.subplot2grid((3,1), (0, 0), rowspan=2)
        plot_lines(ax1,x,y1,
                   xlabel=r'$t\ [{day}]$',
                   ylabel=r'$\phi_{feed}\ [kg/hr]$',
                   linestyle_list=['steps-post',],
                   marker_list=[None,],label_list=['Ideal',],
                   legend_loc='upper left', xpad=0.1, ypad=1.,)
        fig1.set_size_inches(8.5/2.54 , 6/2.54)
    
        fig2 = plt.figure('Feeder-m_feed_cumul')
        dtsub = self.tsub[1] - self.tsub[0]
        m_feed_cumul = np.cumsum(self.logs['f_feed']*dtsub)
        x2 = x.copy()
        y2 = [m_feed_cumul.to('kg'),]
        ax2 = plt.subplot2grid((3,1), (0, 0), rowspan=2)
        plot_lines(ax2,x2,y2,
                   xlabel=r'$t\ [{day}]$',
                   ylabel=r'$m\ [kg]$',
                   linestyle_list=['-',],
                   marker_list=[None],
                   label_list=[r'$m_{feed,cumul}$'],
                   legend_loc='upper left', xpad=0.1, ypad=1.,)
        fig2.tight_layout()
        fig2.set_size_inches(8.5/2.54 , 6/2.54)
        
        # Save figures
        if save_figs:
            fig1.savefig('f-Feeder-f_feed.pdf',dpi=300,bbox_inches='tight')
            fig2.savefig('f-Feeder-m_feed.pdf',dpi=300,bbox_inches='tight')
        
         
# ---- TEST RUN ----
if __name__ == '__main__':
    import pandas as pd
    from acuaponia.classes import Module
    from acuaponia.fishtank.fish_control import fish_control
    
    # ---- Time ----
    t_dates = pd.date_range('2017/01/01 07:00:00',
                            '2017/01/12 07:00:00' ,freq='1H')
    tsim = ((t_dates-t_dates[0])/pd.Timedelta('1H')).values
    tsim = Qty(tsim,'hr')
    tsim_of_day = t_dates.hour.values
    
    # ---- Define fish object ----
    class Fish(Module):
        def __init__(self,tsim,Dtsub,x0,p):
            Module.__init__(self,tsim,Dtsub,x0,p)
    # Initial mass
    fish_x0 = {'m':Qty(100,'g'), 'nfish':Qty(1,'')}
    # Parameters
    Tideal = Qty(28.0 + 273, 'K')
    # Species dependent parameters for tilapia growth (Timmons 2010, p. 95-97)
    n_til = Qty(3.0,'')
    K_til = Qty( 2.08,'g/cm**{}'.format(n_til) )
    Tbase = Qty(18.3+273.15,'K')
    TUbase = Qty(98.4,'K*day/cm')
    #T_max = Qty(29.5+273.15,'K')
    fish_p = {
        'n':n_til,
        'K':K_til,
        'Tbase':Tbase,
        'TUbase':TUbase,
        'Tideal':Tideal,
        }
    # Start object
    dummyfish = Fish(tsim,Qty(60,'min'),fish_x0,fish_p)

    # ---- Feed object ----       
    dtsub = Qty(15,'min')
    p = {'daily_feed_ratio':Qty(0.02,''),
         'daily_feed_schedule':Qty(np.array([8.,12.,17.]),''),
         'N_fraction':Qty(0.1,''),
         'P_fraction':Qty(0.1,''),
         'K_fraction':Qty(0.1,''),
         }
    feeder = Feeder(tsim,dtsub,None,p,dummyfish,status='growth')
    
    # Fish control
    dtgrowth = Qty(5,'day')
    dtstarve = Qty(3,'day')
    dtharvest = Qty(1,'day')
    dtstop = Qty(2,'day')
    ctrl = fish_control(tsim,dtgrowth,dtstarve,dtharvest,dtstop)
    # ---- Simulation run ----
    for i,ti in enumerate(tsim[:-1]):
        t01 = tsim[i:i+2]
        u = {'t0_of_day':Qty(tsim_of_day[i],'')}
        feeder.status = ctrl[i]
        f_feed = feeder.run(t01,u=u)

    # ---- Plots ----
    feeder.plots(save_figs=False)
