import os
import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

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

    dict_updates_ts['Gillett'].loc[:, ('Tot', '5')] = (
        dict_updates_ts['Gillett'].loc[:, ('Ant', '5')] +
        dict_updates_ts['Gillett'].loc[:, ('Nat', '5')]
        )

    dict_updates_ts['Gillett'].loc[:, ('Tot', '95')] = (
        dict_updates_ts['Gillett'].loc[:, ('Ant', '95')] +
        dict_updates_ts['Gillett'].loc[:, ('Nat', '95')]
        )

    
    var_names = {
        'Obs': 'Observed Warming',
        'Ant': 'Anthropogenic (Human-Induced)',
        'GHG': 'Well-mixed Greenhouse Gases',
        'OHF': 'Other Human Forcings',
        'Nat': 'Natural Forcings',
        'Tot': 'Total Attributable Warming'
        }

    labels = {
        'Haustein/Forster': 'Global Warming Index',
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

    plot_vars = ['Ant', 'GHG', 'Tot', 'OHF','Nat']
    #fig,axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8),sharex=True, sharey=True)

    fig = plt.figure(figsize=(10, 8))

    # Create gridspec: 2 rows and 2 columns for main panels,
    # and an additional lower-right block with 2 smaller panels stacked
    gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[1,1])

    # Main panels
    ax00 = fig.add_subplot(gs[0,0])
    ax01 = fig.add_subplot(gs[0,1], sharey=ax00,sharex=ax00)
    ax10 = fig.add_subplot(gs[1,0], sharey=ax00,sharex=ax00)

    # Lower-right: split the (1,1) grid into two stacked panels
    gs_lr = gridspec.GridSpecFromSubplotSpec(2,1, subplot_spec=gs[1,1], hspace=0.1)
    ax11_top = fig.add_subplot(gs_lr[0],sharex=ax00)
    ax11_bottom = fig.add_subplot(gs_lr[1],sharex=ax00)
    axes = [ax00,ax01,ax10,ax11_top,ax11_bottom]

    for ax,v in zip(axes,plot_vars):
        ax.set_title(var_names[v])
        ax.axhline(y=0,color='k',lw=0.5)
        if(not( v in ["OHF","Nat"])):
            ax.scatter(years, temperature, color='lightgrey', label='HadCRUT5, annual',s=2)
        for i, m, l in zip(range(5),['Walsh', 'Ribes', 'Gillett','Smith','Nicklas'], ['-', '--', ':','-','-']):
            if m=='Walsh':
                mn='Haustein/Forster'
            else:
                mn=m
            ax.plot(
                dict_updates_ts[m].index,
                dict_updates_ts[m].loc[:, (v, '50')].values,
                color=method_colors[m],
                ls=l, lw=2, alpha=0.7,label=(mn+": "+labels[m]))
            for erryr in (np.array([start_yr/2+end_yr/2,end_yr])-8 + i*2):
                errind = np.int16(erryr-start_yr)
                ax.errorbar(erryr, dict_updates_ts[m].loc[:, (v, '50')].values[errind],
                        yerr=[[dict_updates_ts[m].loc[:, (v, '95')].values[errind] - dict_updates_ts[m].loc[:, (v, '50')].values[errind]],
                              [dict_updates_ts[m].loc[:, (v, '50')].values[errind] - dict_updates_ts[m].loc[:, (v, '5')].values[errind]]],
                        color=method_colors[m],capsize=3)
        # Plot arbitrary lines so that separate black lines for each method
        # appear in the legend.
        if(v=="Ant"):
            ax.legend(fontsize=9.5)
       # ax.plot([100, 100], [100, 100], color='black', lw=2, alpha=0.7, ls=l,
       #         label=f'{m}: {labels[m]}')

    main_ylim=[-0.5,2]
    ax00.set_ylim(main_ylim)

    # Step 2: compute physical height ratio of stacked panels relative to main panel
    # Use ax10 as reference
    ax10_pos = ax10.get_position()  # Bbox: (x0, y0, x1, y1)
    ax11_top_pos = ax11_top.get_position()
    ax11_bottom_pos = ax11_bottom.get_position()
    assert (ax11_top_pos.height)== (ax11_bottom_pos.height)
    ratio =  ax11_bottom_pos.height /ax10_pos.height
    stacked_range = (main_ylim[1]-main_ylim[0]) * ratio
    stacked_mid1 = -0.2
    stacked_ylim1 = (stacked_mid1 - stacked_range/2, stacked_mid1 + stacked_range/2)
    ax11_top.set_ylim(stacked_ylim1)
    stacked_mid2 = 0
    stacked_ylim2 = (stacked_mid2 - stacked_range/2, stacked_mid2 + stacked_range/2)
    ax11_bottom.set_ylim(stacked_ylim2)
    ax11_top.set_title(var_names[plot_vars[3]], loc='center', pad=5, y=0.8)
    ax11_bottom.set_title(var_names[plot_vars[4]], loc='center', pad=5, y=0.8)

    
    ax00.set_ylabel("Temperature Δ °C\n relative to 1850-1900")
    ax10.set_ylabel("Temperature Δ °C\n relative to 1850-1900")
    ax10.set_xlabel("Year")
    ax11_bottom.set_xlabel("Year")

    # Optional: remove x labels on shared axes to reduce clutter
    for ax in [ax11_top, ax11_bottom]:
        ax.label_outer()
    plt.tight_layout()
    #plt.savefig("multi_method_newStyle.pdf")
    plt.savefig("multi_method_newStyle2.png", dpi=500, bbox_inches='tight')
    plt.show()
    
