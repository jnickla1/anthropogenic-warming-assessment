import os
import sys

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


from attribution_methods.GlobalWarmingIndex.src import graphing as gr
#from attribution_methods.GlobalWarmingIndex.src import definitions as defs


from pandas import Index

# If for any reason your pandas 1.x still lacks Index.infer_objects,
# make it a no-op so scmdata can call it.
if not hasattr(Index, "infer_objects"):
    Index.infer_objects = lambda self, copy=True: self

# now proceed to import the rest
from attribution_methods.GlobalWarmingIndex.src import definitions as defs

# …and your existing code…
#df_temp_PiC = defs.load_PiC_CMIP6(n_yrs, start_pi, end_pi)



###############################################################################
# Checklist of inputs to this script that need updating each year:
# 1. GWI Results (manually add csv to results/ directory)
# 2. KCC Results (manually add csv to results/ directory)
# 3. ROF Results (manually add csv to results/ directory)
# 4. Observed Warming Update (manually add in this script - get from IGCC team)
# 5. HadCRUT Observed Warming (manually add csv to
#    attribution_methods/GlobalWarmingIndex/data/Temp/HadCRUT)

# Checklist of inputs that don't need updating each year
# 1. CMIP6 PiControl simulations (update only when CMIP7 is ready)
# 2. IPCC Quoted reults (never update; they are quotes from IPCC AR6 and SR1.5)

if __name__ == '__main__':
    ###########################################################################
    # LOAD DATA ###############################################################
    ###########################################################################

    start_pi, end_pi = 1850, 1900
    start_yr, end_yr = 1850, 2023

    # Temperature dataset
    df_temp_Obs = defs.load_HadCRUT(start_pi, end_pi, start_yr, end_yr)
    n_yrs = df_temp_Obs.shape[0]
    timeframes = [1, 3, 30]
    df_temp_PiC = defs.load_PiC_CMIP6(n_yrs, start_pi, end_pi)
    df_temp_PiC = defs.filter_PiControl(df_temp_PiC, timeframes)
    df_temp_PiC.set_index(np.arange(n_yrs)+start_yr, inplace=True)

    # RESULTS FROM ANNUAL UPDATES #############################################
    # Combine dataframes of results from all attribution methods (Walsh (GWI),
    # Ribes (KCC), Gillett (ROF)) into one dictionary.
    dict_updates_hl = {}  # Headline results
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

    # MULTI-METHOD ASSESSMENT - AR6 STYLE - TIMESERIES ########################
    # Conclusion: no uncertainty plumes available at time of writing for ROF
    # (Gillett) method, so a multi-method timeseries is not created here.
    # Instead, we plot the individual methods separately as an indicative
    # alternative later.

   

    # OBSERVATIONS ############################################################
    # Add updated observation results from the annual updates paper section 4
    df_update_Obs_repeat = pd.DataFrame({
        # (VARIABLE, PERCENTILE): VALUE
        # 2010-2019 (2023 analysis): 1.07 [0.89-1.22] From Blair, paper Sect. 6
        # 2010-2019 (2022 analysis): 1.07 [0.89-1.22] From Blair, paper Sect. 4
        ('Obs', '50'): 1.07,
        ('Obs',  '5'): 0.89,
        ('Obs', '95'): 1.22
    }, index=['2010\N{EN DASH}2019'])
    df_update_Obs_repeat.columns.names = ['variable', 'percentile']
    df_update_Obs_repeat.index.name = 'Year'

    df_update_Obs_update = pd.DataFrame({
        # (VARIABLE, PERCENTILE): VALUE
        # 2014-2023 (2023 analysis): 1.19 [1.06-1.30] From Blair, paper Sect. 6
        # 2013-2022 (2022 analysis): 1.14 [1.00-1.25] From Blair, paper Sect. 4
        ('Obs', '50'): 1.19,
        ('Obs',  '5'): 1.06,
        ('Obs', '95'): 1.30,
    }, index=['2014\N{EN DASH}2023'])

    df_update_Obs_update.columns.names = ['variable', 'percentile']
    df_update_Obs_update.index.name = 'Year'

    # Add observations quoted from AR6
    df_AR6_Obs = pd.DataFrame({
        # (VARIABLE, PERCENTILE): VALUE
        ('Obs', '50'): 1.06,  # AR6 3.3.1.1.2 p442 from observations
        ('Obs',  '5'): 0.88,  # AR6 3.3.1.1.2 p442 from observations
        ('Obs', '95'): 1.21,  # AR6 3.3.1.1.2 p442 from observations
    }, index=['2010\N{EN DASH}2019'])
    df_AR6_Obs.columns.names = ['variable', 'percentile']
    df_AR6_Obs.index.name = 'Year'

    # Combine all observations into one dictionary
    df_All_Obs = pd.concat([
                            # df_AR6_Obs,
                            df_update_Obs_repeat,
                            df_update_Obs_update
                            ])
    dict_updates_Obs_hl = {'Assessment': df_All_Obs}
    dict_IPCC_Obs_hl = {'Assessment': df_AR6_Obs}

    # QUOTED HEADLINE RESULTS FROM IPCC 6TH ASSESSMENT CYCLE ##################
    # Create dataframe of results from AR6 WG1 Ch.3
    df_AR6_assessment = pd.DataFrame({
        # (VARIABLE, PERCENTILE): VALUE
        ('Ant', '50'): 1.07,  # AR6 3.3.1.1.2 p442, and SPM A.1.3
        ('Ant',  '5'): 0.80,  # AR6 3.3.1.1.2 p442, and SPM A.1.3
        ('Ant', '95'): 1.30,  # AR6 3.3.1.1.2 p442, and SPM A.1.3
        ('GHG', '50'): 1.40,  # AR6 We introduce multi-method assessment here;
        # 3.3.1.1.2 had no value for this, and SPM2 just plotted midpoint of
        # likely range to give 1.5
        ('GHG',  '5'): 1.00,  # AR6 3.3.1.1.2 p442, SPM A.1.3
        ('GHG', '95'): 2.00,  # AR6 3.3.1.1.2 p442, SPM A.1.3
        ('Nat', '50'): 0.03,  # We introduce multi-method assessment here;
        # 3.3.1.1.2 had no value for this, and SPM2 just plotted midpoint of
        # likely range to give 0.0
        ('Nat',  '5'): -0.10,  # AR6 3.3.1.1.2 p442, SPM A.1.3
        ('Nat', '95'): 0.10,  # AR6 3.3.1.1.2 p442, SPM A.1.3
        ('OHF', '50'): -0.32,  # We introduce multi-method assessment here;
        # 3.3.1.1.2 had no value for this, and SPM2 just plotted midpoint of
        # likely range to give -0.4
        ('OHF',  '5'): -0.80,  # AR6 3.3.1.1.2 p442, SPM A.1.3
        ('OHF', '95'): 0.00,  # AR6 3.3.1.1.2 p442, SPM A.1.3
        ('Int', '50'): 0.00,  # AR6 3.3.1.1.2 had no value for this, and SPM2
        # just plotted midpoint of likely range to give 0.0, which is still
        # used here.
        ('Int',  '5'): -0.20,  # AR6 3.3.1.1.2 p443, SPM A.1.3
        ('Int', '95'): 0.20,  # AR6 3.3.1.1.2 p443, SPM A.1.3
    }, index=['2010\N{EN DASH}2019'])
    df_AR6_assessment.columns.names = ['variable', 'percentile']
    df_AR6_assessment.index.name = 'Year'

    # Create dataframe of results from SR15 Ch.1
    df_SR15_assessment = pd.DataFrame({
        # (VARIABLE, PERCENTILE): VALUE
        ('Ant', '50'): 1.0,  # SR15 1.2.1.3
        ('Ant',  '5'): 0.8,  # SR15 1.2.1.3
        ('Ant', '95'): 1.2,  # SR15 1.2.1.3
    }, index=['2017'])
    df_SR15_assessment.columns.names = ['variable', 'percentile']
    df_SR15_assessment.index.name = 'Year'

    # Combine 6th assessment cycle results from both SR1.5 and AR6
    df_IPCC_assessment = pd.concat([df_AR6_assessment, df_SR15_assessment])
    unendashed_assessment = defs.un_en_dash_ify(df_IPCC_assessment.copy())
    unendashed_assessment.to_csv('results/Assessment-6thIPCC_headlines.csv')

 
    ###########################################################################
    # CREATE PLOTS ############################################################
    ###########################################################################

    # Plotting colours
    var_colours = {
        'Tot': '#d7827e',
        'Ant': '#b4637a',
        'Nat': '#56949f',
        'GHG': '#907aa9',
        'OHF': '#ea9d34',
        'Res': '#9893a5',
        'Obs': '#797593',
        'PiC': '#cecacd'}
    var_names = {
        'Obs': 'Observed Warming',
        'Ant': 'Total Human-induced Warming',
        'GHG': 'Well-mixed Greenhouse Gases',
        'OHF': 'Other Human Forcings',
        'Nat': 'Natural Forcings',
        'Tot': 'Total Attributable Warming'
        }

    source_markers = {
        'Haustein': 'o',  # Walsh and Haustein are both GWI so get same symbol.
        'Walsh': 'o',
        'Ribes': 'v',
        'Gillett': 's',
        'Smith': 'D'}

    labels = {
        'Haustein': 'Global Warming Index',
        'Walsh': 'Global Warming Index',
        'Ribes': 'Kriging for Climate Change',
        'Gillett': 'Regularised Optimal Fingerprinting',
        'Smith': 'Finite Amplitude Impulse Response',
        'Nicklas': 'Energy Balance Model Kalman Filter'
        }

    plot_folder = f'./plots/{end_yr}/'
    if not os.path.exists(plot_folder):
        os.makedirs(plot_folder)

    # PLOT TIMESERIES FOR EACH METHOD #########################################
    for method in dict_updates_ts.keys():
        print(f'Creating {method} Simple Plot...')
        plot_vars = ['Ant', 'GHG', 'Nat', 'OHF']
        fig = plt.figure(figsize=(12, 8))
        ax = plt.subplot2grid(shape=(1, 1), loc=(0, 0), rowspan=1, colspan=1)
        gr.gwi_timeseries(
            ax, df_temp_Obs, df_temp_PiC, dict_updates_ts[method],
            plot_vars, var_colours)
        ax.set_ylim(-1, 2)
        ax.set_xlim(start_yr, end_yr)
        ax.text(1875, -0.85, '1850\N{EN DASH}1900\nPreindustrial Baseline',
                ha='center')
        gr.overall_legend(fig, 'lower center', 6)
        fig.suptitle(f'{method} Timeseries Plot')
        fig.savefig(f'{plot_folder}/2_{method}_timeseries.png')
        fig.savefig(f'{plot_folder}/2_{method}_timeseries.pdf')

    # PLOT THE MULTI-METHOD TIMESERIES IN SINGLE FIGURE #######################
    print('Creating Multi-Method Stacked Plot...')
    fig = plt.figure(figsize=(12, 8))
    ax = plt.subplot2grid(shape=(1, 1), loc=(0, 0), rowspan=1, colspan=1)

    # Plot simplified (5-95% only) plumes for GWI method.
    gr.gwi_timeseries(ax, df_temp_Obs, df_temp_PiC, dict_updates_ts['Walsh'],
                      plot_vars, var_colours, sigmas=['5', '95', '50'],
                      labels=True)
    # Plot the median best-estimate for each method on top of the GWI plumes.
    for m, l in zip(['Walsh', 'Ribes', 'Gillett','Smith','Nicklas'], ['-', '--', (0, (1,1)),'-.',(0, (3, 1, 1, 1, 1, 1))]):
        for v in plot_vars:
            ax.plot(
                dict_updates_ts[m].index,
                dict_updates_ts[m].loc[:, (v, '50')].values,
                color=var_colours[v],
                ls=l, lw=2, alpha=0.7)
        # Plot arbitrary lines so that separate black lines for each method
        # appear in the legend.
        ax.plot([100, 100], [100, 100], color='black', lw=2, alpha=0.7, ls=l,
                label=f'{m}: {labels[m]}')

    ax.set_ylim(-1, 2)
    ax.set_xlim(start_yr, end_yr)
    ax.text(1875, -0.85, '1850\N{EN DASH}1900\nPreindustrial Baseline',
            ha='center')
    fig.suptitle('Timeseries for each attribution method used '
                 'in the assessment of contributions to observed warming')
    fig.tight_layout(rect=(0.02, 0.08, 0.98, 0.98))
    gr.overall_legend(fig, 'lower center', 3,
                      reorder=[10, 0, 1, 2, 3, 4, 5, 6, 7,8,9])
    fig.savefig(f'{plot_folder}/2_stacked-multi_method_timeseries.png')
    fig.savefig(f'{plot_folder}/2_stacked-multi_method_timeseries.pdf')

    # PLOT THE MULTI-METHOD TIMESERIES IN MULTI-FIGURE ########################
    print('Creating Multi-Method Aligned Plot...')
    fig = plt.figure(figsize=(16, 6))
    methods = ['Walsh', 'Ribes', 'Gillett','Smith','Nicklas']
    subs = ['(a)', '(b)', '(c)','(d)','(e)']

    for m in methods:
        ax = plt.subplot2grid(shape=(1, 5), loc=(0, methods.index(m)),
                              rowspan=1, colspan=1)
        PiC = df_temp_PiC if m == 'Walsh' else None
        gr.gwi_timeseries(ax, df_temp_Obs, PiC, dict_updates_ts[m],
                          ['Tot', 'GHG', 'Nat', 'OHF'], var_colours)
        ax.set_ylim(-1, 2)
        ax.set_xlim(1900, end_yr)
        if methods.index(m) > 0:
            ax.set_ylabel('')
            ax.set_yticklabels([])
        ax.set_title(f'{subs[methods.index(m)]} {m}: {labels[m]}')
    gr.overall_legend(fig, 'lower center', 6)
    # fig.suptitle('Testing one two three how do we think this looks?')
    fig.tight_layout(rect=(0.02, 0.08, 0.98, 0.94))
    fig.suptitle('Timeseries for each attribution method used '
                 'in the assessment of contributions to observed warming')
    fig.savefig(f'{plot_folder}/2_aligned-multi_method_timeseries.png')
    fig.savefig(f'{plot_folder}/2_aligned-multi_method_timeseries.pdf')

  
    ###########################################################################
  
