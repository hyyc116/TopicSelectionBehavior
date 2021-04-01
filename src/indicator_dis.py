#coding:utf-8
from typing import Set
from scipy.optimize.optimize import main
from basic_config import *
import seaborn as sns
import pandas as pd


def hist_attrs(data, attr_names, logs, outpath, col=2, indexed=True):

    indexes = 'abcdefghijklmn'

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

    indexes = 'abcdefghijklmn'

    row = len(xs)
    col = len(ys)
    fig, axes = plt.subplots(len(xs), len(ys), figsize=(col * 4.5, row * 3.5))

    figindex = 0
    for i, x in enumerate(xs):

        for j, y in enumerate(ys):

            ax = axes[i][j]

            rel_two_attrs(data, x, y, ax)

            xlabel = x
            ax.set_xlabel(xlabel + '\n(' + indexes[figindex] + ')')

            figindex += 1

    plt.tight_layout()

    plt.savefig(outpath, dpi=400)
    logging.info(f'fig saved to {outpath}')


def rel_two_attrs(data, x, y, ax):
    sns.lineplot(data=data, x=x, y=y, ax=ax, ci='sd')


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
                   xs=['NUNT', 'productivity'],
                   ys=['hindex', 'TNC', 'diversity'],
                   outpath='fig/fig3.png')


if __name__ == "__main__":

    variable_dis()