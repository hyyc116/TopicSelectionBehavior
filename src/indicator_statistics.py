#coding:utf-8
from typing import Set
from scipy.optimize.optimize import main
from basic_config import *
import seaborn as sns
import pandas as pd


def hist_attr(data, attr_names, logs, outpath, col=2, indexed=True):

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


def hist_indicators():
    # read data
    data = pd.read_csv('data/author_topic_indicators.txt')
    sns.set_theme(style='ticks')

    # 每位作者所有了论文的unique 主题数量
    data['NUNT'] = data['UNT'] / data['productivity']
    prod_list = data['productivity']
    hindex_list = data['hindex']
    tnc_list = data['TNC']
    anc_list = data['ANC']

    utn_list = data['UNT']
    attr1VsALL(utn_list, 'UNT', 'unique number of topics', prod_list,
               hindex_list, tnc_list, anc_list)

    nutn_list = data['NUNT']
    attr1VsALL(nutn_list,
               'NUNT',
               'normalized unique number of topics',
               prod_list,
               hindex_list,
               tnc_list,
               anc_list,
               is_con=True)

    data['MAX PNUOT N'] = data['MAX PNUOT'] / data['productivity']
    maxPNUOT = data['MAX PNUOT N']
    attr1VsALL(maxPNUOT,
               'MAX PNUOT N',
               'normed max(PNUOT)',
               prod_list,
               hindex_list,
               tnc_list,
               anc_list,
               is_con=True)

    diversity_list = data['diversity']
    attr1VsALL(diversity_list,
               'diversity',
               'diversity',
               prod_list,
               hindex_list,
               tnc_list,
               anc_list,
               is_con=True)

    persistance_list = data['persistance']
    attr1VsALL(persistance_list,
               'persistance',
               'persistance',
               prod_list,
               hindex_list,
               tnc_list,
               anc_list,
               is_con=True)


def attr1VsALL(utn_list,
               attrName,
               attrLabel,
               prod_list,
               hindex_list,
               tnc_list,
               anc_list=None,
               is_con=False):
    #MAX PNUOT 与个属性之间的关系
    attr1_dis(utn_list, attrName, attrLabel, is_continous=is_con)
    attr1_vs_attr2(utn_list,
                   prod_list,
                   attrLabel,
                   'number of papers',
                   f'{attrName}_productivity',
                   set([5, 6, 8, 10, 15, 20]),
                   is_con=is_con)

    # unique主题数量与hindex的关系
    attr1_vs_attr2(utn_list,
                   hindex_list,
                   attrLabel,
                   'hindex',
                   f'{attrName}_hindex',
                   logX=False,
                   sample_set=set([5, 10, 15, 20]),
                   is_con=is_con)

    # unique主题数量与total nummber of citations的关系
    attr1_vs_attr2(utn_list,
                   tnc_list,
                   attrLabel,
                   'TNC',
                   f'{attrName}_TNC',
                   logX=True,
                   sample_set=set([5, 10, 20, 50, 100]),
                   is_con=is_con)

    # unique主题数量与平均值的关系
    attr1_vs_attr2(utn_list,
                   anc_list,
                   attrLabel,
                   'ANC',
                   f'{attrName}_ANC',
                   logX=True,
                   sample_set=set([5, 7, 8, 10, 20]),
                   is_con=is_con)


def histXY(utn_list, continuous):

    if not continuous:
        xs = []
        ys = []
        unique_topic_numbers_counter = Counter(utn_list)

        for utn in sorted(unique_topic_numbers_counter.keys()):
            xs.append(utn)
            ys.append(unique_topic_numbers_counter[utn])

        ys = np.array(ys) / float(np.sum(ys))
    else:

        ys, edges = np.histogram(utn_list, bins=7)

        xs = (edges[:-1] + edges[1:]) / 2

    return xs, ys


def attr1_dis(utn_list, attr_name, attr_label, logX=False, is_continous=False):

    mean = np.mean(utn_list)
    median = np.median(utn_list)

    xs, ys = histXY(utn_list, is_continous)

    plt.figure(figsize=(5, 4))

    plt.plot(xs, ys, '-o')

    plt.plot([mean] * 10,
             np.linspace(np.min(ys) * 1.5,
                         np.max(ys) * 1.2, 10),
             '--',
             label='mean')
    plt.plot([median] * 10,
             np.linspace(np.min(ys) * 1.5,
                         np.max(ys) * 1.2, 10),
             '-.',
             label='median')

    plt.xlabel(attr_label)
    plt.ylabel('number of authors')

    if logX:
        plt.xscale('log')

    plt.legend()

    plt.tight_layout()
    plt.savefig(f'fig/{attr_name}_dis.png', dpi=400)


def attr1_vs_attr2(utn_list,
                   prod_list,
                   xlabel,
                   ylabel,
                   saveName,
                   sample_set=None,
                   logX=True,
                   is_con=False):

    xlabelS = xlabel.replace(' ', "_")
    ylabelS = ylabel.replace(" ", "_")

    prod_utns = defaultdict(list)

    for i, utn in enumerate(utn_list):
        prod = prod_list[i]
        prod_utns[prod].append(utn)

    prods = []
    mean_Utns = []
    median_utns = []
    plt.figure(figsize=(5, 4))
    for prod in sorted(prod_utns.keys()):
        prods.append(prod)
        mean_Utns.append(np.mean(np.array(prod_utns[prod])))
        median_utns.append(np.median(np.array(prod_utns[prod])))

        if sample_set and prod in set([5, 6, 8, 10, 15, 20]):
            xs, ys = histXY(prod_utns[prod], is_con)
            ys = np.array(ys) / float(np.sum(ys))
            plt.plot(xs, ys, '-o', label=f"{ylabel}={prod}")

    if sample_set:
        plt.legend()

        plt.tight_layout()

        plt.savefig(f'fig/{saveName}_FACETs.png', dpi=400)

    ## 随着作者文章总数量的变化
    plt.figure(figsize=(5, 4))

    plt.plot(prods, mean_Utns, '-o', label='mean')
    plt.plot(prods, median_utns, '-^', label='median')

    plt.xlabel(f'{ylabel}')
    plt.ylabel(f'{xlabel}')

    if logX:
        plt.xscale('log')

    plt.legend()

    plt.tight_layout()

    plt.savefig(f'fig/{saveName}_compare.png', dpi=400)


def dynamic_attrs():

    author_dynamics = json.loads(open('data/trans_dynamic_data.json').read())

    poses = []
    directions = []

    t_intervals = defaultdict(list)

    t_poses = defaultdict(list)
    for author in author_dynamics.keys():

        pos, direction, t = author_dynamics[author]

        # for i, d in enumerate(direction):
        #     if d <= 1:
        #         directions.append(d)
        #         poses.append(pos[i])
        directions.extend(direction)
        poses.extend(pos)
        if t > 15:
            t = 15
        t_poses[t].extend(pos)

        last_i = 0
        for i, p in enumerate(pos):

            interval = p - last_i
            t_intervals[t].append(interval)
            last_i = p

    print(len(poses), len(directions))

    data = pd.DataFrame.from_dict({'POS': poses, 'Direction': directions})

    plt.figure(figsize=(5, 4))

    # plt.plot(xs, ys)
    sns.histplot(data, x='POS', bins=20, kde=True)

    plt.xlabel('selection position')

    plt.savefig('fig/dynamic_pos.png', dpi=400)

    plt.figure(figsize=(5, 4))

    sns.histplot(data, x='Direction', bins=20, kde=True)

    plt.tight_layout()

    plt.savefig('fig/dynamic_direction.png', dpi=400)

    bins_directions = defaultdict(list)
    for i, pos in enumerate(poses):

        direction = directions[i]

        posbin = pos_bin(pos)

        bins_directions[posbin].append(direction)

    xs = []
    ys = []
    for pos in sorted(bins_directions.keys()):
        xs.append(pos)
        ys.append(np.mean(bins_directions[pos]))

    plt.figure(figsize=(5, 4))

    plt.plot(xs, ys)

    plt.tight_layout()

    plt.savefig('fig/bin_directions.png', dpi=400)

    for t in [5, 6, 7, 8, 10, 11]:

        poses = t_poses[t]

        plt.figure(figsize=(5, 4))

        data = pd.DataFrame.from_dict({'POS': poses})

        sns.histplot(data, x='POS', kde=True)

        plt.tight_layout()

        plt.savefig(f'fig/{t}_pos.png', dpi=400)

    for t in [5, 6, 7, 8, 10, 11, 12, 15]:

        poses = t_intervals[t]

        plt.figure(figsize=(5, 4))

        data = pd.DataFrame.from_dict({'interval': poses})

        sns.histplot(data, x='interval', kde=True)

        plt.tight_layout()

        plt.savefig(f'fig/{t}_interval.png', dpi=400)


def pos_bin(pos):

    return int(pos / 0.1)


if __name__ == "__main__":
    hist_indicators()

    # dynamic_attrs()