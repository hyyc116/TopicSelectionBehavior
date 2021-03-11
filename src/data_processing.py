#coding:utf-8

from scipy.optimize.optimize import main
from basic_config import *

APS_PROJECT_PATH = 'F:\\APS_data_processing'


def APS_PCASCODE_process():

    paper_year = json.loads(
        open(APS_PROJECT_PATH + '\\data\\pid_pubyear.json').read())

    topic_year_num = defaultdict(lambda: defaultdict(int))

    paper_topic = {}
    for line in open('G:\\APS\\PCAS.txt', encoding='utf-8'):

        line = line.strip()

        if line.startswith('DOI'):
            continue

        splits = line.split(',')

        doi = splits[0]

        codes = []
        for code in splits[1:]:

            if code.strip() == '':
                continue

            # 只保留一级主题
            codes.append(code.split('.')[0].split(' ')[-1])

        topic = codes[np.random.randint(0, len(codes))]

        year = paper_year.get(doi, -1)

        topic_year_num[topic][year] += 1

        paper_topic[doi] = topic

    logging.info('{} papers has topics.'.format(len(paper_topic)))

    open(APS_PROJECT_PATH + '\\data\paper_topic.json',
         'w').write(json.dumps(paper_topic))

    logging.info('paper topic saved.')

    open('data/topic_year_num.json', 'w').write(json.dumps(topic_year_num))


# 根据作者的论文数量对作者进行过滤
def filter_author_by_papernum(min=5, max=100, plot_distribution=True):

    logging.info('loading author paper num data ... ')

    author_year_papers = json.loads(
        open(APS_PROJECT_PATH + '\\data\\author_year_papers.json').read())

    author_papernum = json.loads(
        open(APS_PROJECT_PATH + '\\data\\author_papernum.json').read())

    paper_topic = json.loads(
        open(APS_PROJECT_PATH + '\\data\\paper_topic.json').read())

    paper_cn = json.loads(
        open(APS_PROJECT_PATH + '\\data\\pid_cn.json').read())

    logging.info('starting to stat ...')
    author_topics = {}

    for author in author_papernum.keys():

        papernum = author_papernum[author]

        if papernum < min or papernum > max:
            continue

        year_papers = author_year_papers[author]

        topics = []
        cns = []
        years = []
        for year in sorted(year_papers, key=lambda x: int(x)):

            for paper in year_papers[year]:
                topic = paper_topic.get(paper, None)
                if topic is not None:
                    topics.append(topic)
                    cns.append(paper_cn.get(paper, 0))
                    years.append(year)

        if len(topics) < 5:
            continue

        author = author.replace(',', '')

        author_topics[author] = [topics, cns, years]

    open('data/author_topics.json', 'w').write(json.dumps(author_topics))

    logging.info(
        '{} authors are filterd, asn saved to data/author_topics.json'.format(
            len(author_topics)))

    logging.info('start to plot author paper num distribution... ')

    pnum_counter = Counter(author_papernum.values())

    xs = []
    ys = []
    for pnum in sorted(pnum_counter.keys()):
        xs.append(pnum)
        ys.append(pnum_counter[pnum])

    plt.figure(figsize=(5, 4))
    plt.plot(xs, ys, 'o', fillstyle='none')

    plt.xscale('log')
    plt.yscale('log')

    plt.xlabel('number of publications')
    plt.ylabel('number of authors')

    plt.tight_layout()

    plt.savefig('fig/author_pnum_dis.png', dpi=400)
    logging.info(
        'Author paper num distribution saved to fig/author_pnum_dis.png.')


# 生成用于本文数据分析的静态指标
# author, hindex, productivity, total number of citations, unique number of topics, MaxNumber under one topic, Diversity, Persistance
def generate_static_data():
    logging.info('loading data ...')
    author_topics = json.loads(open('data/author_topics.json').read())
    topic_year_num = json.loads(open('data/topic_year_num.json').read())
    lines = [
        'author,hindex,productivity,TNC,ANC,UNT,PNUOT,MAX PNUOT,MEAN PNUOT,diversity,persistance'
    ]

    author_trans_data = {}
    for author in author_topics:

        topics, cns, years = author_topics[author]

        yearsI = [int(y) for y in years]

        topic_counter = Counter(topics)

        values = list(topic_counter.values())

        topic_years = defaultdict(list)

        for ti, topic in enumerate(topics):

            topic_years[topic].append(yearsI[ti])

        hindex = Hindex(cns)
        prod = len(topics)
        tnc = np.sum(cns)
        anc = np.sum(cns)
        unt = len(set(topics))
        diversity = gini(values)
        PNUOT = '='.join([str(v) for v in values])
        MAXPNUOT = np.max(values)
        MeanPNUOT = np.mean(values)

        maxtopic = sorted(topic_years.keys(),
                          key=lambda x: len(topic_years[x]),
                          reverse=True)[0]
        max_years = topic_years[maxtopic]
        assert (MAXPNUOT == len(max_years))

        if (np.max(yearsI) - np.min(yearsI)) == 0:
            persistance = 0
        else:
            persistance = (np.max(max_years) - np.min(max_years)) / (
                np.max(yearsI) - np.min(yearsI))

        t = len(topics)
        trans_poses = []
        trans_direction = []
        intopics = set([])
        for i, topic in enumerate(topics):
            if i > 0 and topic not in intopics and topic != topics[i - 1]:
                trans_poses.append(i / float(t))

                year = years[i - 1]
                oldnum = topic_year_num[topics[i - 1]].get(year, 0)
                newnum = topic_year_num[topics[i]].get(year, 0)

                p = newnum - oldnum
                trans_direction.append(p)

            intopics.add(topic)

        author_trans_data[author] = [trans_poses, trans_direction]

        lines.append(
            f"{author},{hindex},{prod},{tnc},{anc},{unt},{PNUOT},{MAXPNUOT},{MeanPNUOT},{diversity},{persistance}"
        )

    open('data/author_topic_indicators.txt', 'w',
         encoding='utf8').write('\n'.join(lines))
    logging.info('data saved to data/author_topic_indicators.txt.')

    open('data/trans_dynamic_data.json',
         'w').write(json.dumps(author_trans_data))
    logging.info('data saved to data/trans_dynamic_data.json')


def Hindex(index_list):

    hindex = 0
    for i, index in enumerate(
            sorted(index_list, key=lambda x: int(x), reverse=True)):

        if i > index:
            break

        hindex = i

    return hindex


if __name__ == '__main__':

    # APS_PCASCODE_process()
    # filter_author_by_papernum()
    generate_static_data()