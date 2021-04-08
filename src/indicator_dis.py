#coding:utf-8
from typing import Set
from scipy.optimize.optimize import main
from basic_config import *
import seaborn as sns
import pandas as pd
import numpy as np
import statsmodels.api as sm
lowess = sm.nonparametric.lowess
from patsy import dmatrices
import statsmodels.formula.api as smf


def hist_attrs(data, attr_names, logs, outpath, col=2, indexed=True):

    indexes = 'abcdefghijklmnopqrst'

    attr_num = len(attr_names)

    if attr_num == 0:
        logging.error('No attrname stated.')
        return None

    if attr_num != len(logs):
        logging.error('log scale list do not has same length as attr_names.')
        return None

    if attr_num == 1:
        indexed = False

    row = attr_num // col

    fig, axes = plt.subplots(row, col, figsize=(col * 4.5, row * 3.5))

    for i, attr_name in enumerate(attr_names):

        r = i // col
        c = i % col

        ax = axes[r][c]
        log = logs[i]

        hist_one_attr(data, attr_name, ax, log=log)

        xlabel = attr_name

        if indexed:
            xlabel += '\n(' + indexes[i] + ')'

        ax.set_xlabel(xlabel)

    plt.tight_layout()

    plt.savefig(outpath, dpi=400)
    logging.info(f'fig saved to {outpath}')


#一个属性的分布
def hist_one_attr(data, attr_name, ax, log=True):

    sns.histplot(data,
                 x=attr_name,
                 ax=ax,
                 log_scale=log,
                 kde=True,
                 stat='probability')


def relations_maps(data,
                   xs=['UNT', 'diversity'],
                   ys=['productivity', 'hindex'],
                   outpath=None):

    # indexes = 'abcdefghijklmn'
    indexes = 'abcdefghijklmnopqrst'

    row = len(xs)
    col = len(ys)
    fig, axes = plt.subplots(col, row, figsize=(row * 4.5, col * 3.5))

    figindex = 0
    for i, x in enumerate(ys):

        for j, y in enumerate(xs):

            ax = axes[i][j]

            rel_two_attrs(data, x, y, ax)

            xlabel = x
            ax.set_xlabel(xlabel + '\n(' + indexes[figindex] + ')')
            ax.set_ylabel(y)

            if x == 'productivity':
                ax.set_xscale('log')

            figindex += 1

    plt.tight_layout()

    plt.savefig(outpath, dpi=400)
    logging.info(f'fig saved to {outpath}')


def rel_two_attrs(data, x, y, ax):
    sns.lineplot(data=data, x=x, y=y, ax=ax, alpha=0.5, ci=None)
    xs, ys = zip(*lowess(data[y], data[x], frac=1. / 3, it=0))

    # ax.plot(xs, ys)

    # xs, ys = zip(*lowess(data[y], data[x], frac=1. / 3))

    # ax.plot(xs, ys)

    # xs, ys = zip(*lowess(data[y], data[x]))

    ax.plot(xs, ys)


def variable_dis():
    data = pd.read_csv('data/author_topic_indicators.txt')
    sns.set_theme(style='ticks')

    # 自变量
    data['NUNT'] = data['UNT'] / data['productivity']
    data['persistence'] = data['MAX PNUOT'] / data['productivity']

    hist_attrs(data, ['UNT', 'NUNT', 'persistence', 'diversity'],
               [False, False, False, False], 'fig/fig1.png')

    # 因变量分布
    hist_attrs(data, ['TNC', 'ANC', 'hindex', 'productivity'],
               [False, False, False, True], 'fig/fig2.png')

    relations_maps(data,
                   xs=['UNT', 'NUNT', 'diversity', 'persistence'],
                   ys=['hindex', 'TNC', 'ANC', 'productivity'],
                   outpath='fig/fig3.png')

    relations_maps(data,
                   ys=['UNT', 'NUNT', 'diversity', 'persistence'],
                   xs=['hindex', 'TNC', 'ANC', 'productivity'],
                   outpath='fig/fig4.png')

    relations_maps(data,
                   ys=['productivity', 'UNT'],
                   xs=['hindex', 'TNC', 'ANC'],
                   outpath='fig/fig5.png')


def regression_analysis():

    data = pd.read_csv('data/author_topic_indicators.txt')

    data['NUNT'] = data['UNT'] / data['productivity']
    data['persistence'] = data['MAX PNUOT'] / data['productivity']

    print('----------------------------------------------------')
    print('hindex ~ UNT + NUNT + diversity + persistence + productivity')

    mod = smf.ols(
        formula='hindex ~ UNT + NUNT + diversity + persistence + productivity',
        data=data)

    res = mod.fit()

    print(res.summary())

    print('----------------------------------------------------')
    print('hindex ~ UNT + NUNT + diversity + persistence')

    mod = smf.ols(formula='hindex ~ UNT + NUNT + diversity + persistence',
                  data=data)

    res = mod.fit()

    print(res.summary())

    print('----------------------------------------------------')
    print('np.log(TNC+1) ~ UNT + NUNT + diversity + persistence')

    mod = smf.ols(
        formula='np.log(TNC+1) ~ UNT + NUNT + diversity + persistence',
        data=data)

    res = mod.fit()

    print(res.summary())

    print('----------------------------------------------------')
    print('np.log(productivity) ~ UNT + NUNT + diversity + persistence')

    mod = smf.ols(
        formula='np.log(productivity) ~ UNT + NUNT + diversity + persistence',
        data=data)

    res = mod.fit()

    print(res.summary())

    print('----------------------------------------------------')
    print('np.log(ANC+1) ~ UNT + NUNT + diversity + persistence')

    mod = smf.ols(
        formula='np.log(ANC+1) ~ UNT + NUNT + diversity + persistence',
        data=data)

    res = mod.fit()

    print(res.summary())


if __name__ == "__main__":

    # variable_dis()

    regression_analysis()