import os
import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


##def load_HadCRUT(start_pi, end_pi, start_yr, end_yr):
##    """Load HadCRUT5 observations and remove PI baseline."""
##    here = os.path.dirname(os.path.realpath(__file__))
##    temp_ens_Path = (
##        '/attribution_methods/GlobalWarmingIndex/data/Temp/HadCRUT/' +
##        'HadCRUT.5.0.2.0.analysis.ensemble_series.global.annual.csv')
##    temp_ens_Path = here + temp_ens_Path
##    # read temp_Path into pandas dataframe, rename column 'Time' to 'Year'
##    # and set the index to 'Year', keeping only columns with 'Realization' in
##    # the column name, since these are the ensembles
##    df_temp_Obs = pd.read_csv(temp_ens_Path,
##                              ).rename(columns={'Time': 'Year'}
##                                       ).set_index('Year'
##                                                   ).filter(regex='Realization'
##                                                            )
##
##    # Find PI offset that is the PI-mean of the median (HadCRUT best estimate)
##    # of the ensemble and substract this from entire ensemble. Importantly,
##    # the same offset is applied to the entire ensemble to maintain accurate
##    # spread of HadCRUT (ie it is wrong to subtract the PI-mean for each
##    # ensemble member from itself).
##    ofst_Obs = df_temp_Obs.median(axis=1).loc[
##        (df_temp_Obs.index >= start_pi) &
##        (df_temp_Obs.index <= end_pi),
##        ].mean(axis=0)
##    df_temp_Obs -= ofst_Obs
##
##    # Filter only years between start_yr and end_yr
##    df_temp_Obs = df_temp_Obs.loc[
##        (df_temp_Obs.index >= start_yr) &
##        (df_temp_Obs.index <= end_yr),
##        ]
##
##    return df_temp_Obs



if __name__ == '__main__':
    start_pi, end_pi = 1850, 1900
    start_yr, end_yr = 1850, 2023
    df_temp_Obs = pd.read_csv("../../../../Common_Data/HadCRUT.5.0.2.0.analysis.summary_series.global.annual.csv")
    years = df_temp_Obs["Time"].to_numpy()
    temperature = df_temp_Obs["Anomaly (deg C)"].to_numpy()
    offset_t = np.mean(temperature[0:51]) #1850-1900
    temperature = temperature - offset_t
    dict_updates_ts = {}  # Timeseries results
    files = os.listdir('results')  # Files in the results/ directory
    for method in ['Walsh', 'Ribes', 'Gillett','Smith','Nicklas']:
        file_ts = [f for f in files if f'{method}_GMST_timeseries' in f][0]
      #  file_hs = [f for f in files if f'{method}_GMST_headlines' in f][0]
        skiprows = 0
        df_method_ts = pd.read_csv(
            f'results/{file_ts}',
            index_col=0,  header=[0, 1], skiprows=skiprows)
     #   df_method_hl = pd.read_csv(
     #       f'results/{file_hs}',
     #       index_col=0,  header=[0, 1], skiprows=skiprows)
        if method == 'Walsh':
            n = file_ts.split('.csv')[0].split('_')[-1]
      #  df_method_hl - defs.en_dash_ify(df_method_hl)

     #   dict_updates_hl[method] = df_method_hl
        dict_updates_ts[method] = df_method_ts

    # No Tot warming provided for ROF, so include an indicative approximation
    # as the sum of Ant and Nat warming
    dict_updates_ts['Gillett'].loc[:, ('Tot', '50')] = (
        dict_updates_ts['Gillett'].loc[:, ('Ant', '50')] +
        dict_updates_ts['Gillett'].loc[:, ('Nat', '50')]
        )

    
    var_names = {
        'Obs': 'Observed Warming',
        'Ant': 'Total Human-induced Warming',
        'GHG': 'Well-mixed Greenhouse Gases',
        'OHF': 'Other Human Forcings',
        'Nat': 'Natural Forcings',
        'Tot': 'Total Attributable Warming'
        }

    labels = {
        'Haustein': 'Global Warming Index',
        'Walsh': 'Global Warming Index',
        'Ribes': 'Kriging for Climate Change',
        'Gillett': 'Regularised Optimal Fingerprinting',
        'Smith': 'Finite Amplitude Impulse Response',
        'Nicklas': 'Energy Balance Model Kalman Filter'
        }

    method_colors = {
        'Walsh': "#AA4499",  #pink
        'Ribes': "#AA4499",  #pink
        'Gillett': "#AA4499",  #pink
        'Smith': "#44AA99",  # teal
        'Nicklas': "#999933",  # mustard
        }

    plot_vars = ['Ant', 'GHG', 'Nat', 'OHF']
    fig,axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8),sharex=True, sharey=True)
    
    for ax,v in zip(axes.flatten(),plot_vars):
        ax.set_title(var_names[v])
        ax.scatter(years, temperature, color='lightgrey', label='HadCRUT5, annual',s=2)
        for m, l in zip(['Walsh', 'Ribes', 'Gillett','Smith','Nicklas'], ['-', '--', ':','-','-']):
            if m=='Walsh':
                mn='Haustein'
            else:
                mn=m
            ax.plot(
                dict_updates_ts[m].index,
                dict_updates_ts[m].loc[:, (v, '50')].values,
                color=method_colors[m],
                ls=l, lw=2, alpha=0.7,label=(mn+": "+labels[m]))
        # Plot arbitrary lines so that separate black lines for each method
        # appear in the legend.
        if(v=="OHF"):
            ax.legend()
       # ax.plot([100, 100], [100, 100], color='black', lw=2, alpha=0.7, ls=l,
       #         label=f'{m}: {labels[m]}')

    axes[0,0].set_ylim(-1, 2)
    axes[0,0].set_ylabel("Temperature Δ °C\n relative to 1850-1900")
    axes[1,0].set_ylabel("Temperature Δ °C\n relative to 1850-1900")
    axes[1,0].set_xlabel("Year")
    axes[1,1].set_xlabel("Year")
    axes[0,0].set_xlim(start_yr, end_yr)
    plt.tight_layout()
    plt.savefig("multi_method_newStyle.pdf")
    plt.savefig("multi_method_newStyle.png", dpi=500, bbox_inches='tight')
    plt.show()
    
