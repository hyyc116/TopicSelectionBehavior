#coding:utf-8

from scipy.optimize.optimize import main
from basic_config import *

APS_PROJECT_PATH = 'F:\\APS_data_processing'


def APS_PCASCODE_process():

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
            codes.append(code.split('.')[0])

        topic = codes[np.random.randint(0, len(codes))]

        paper_topic[doi] = topic

    logging.info('{} papers has topics.'.format(len(paper_topic)))

    open(APS_PROJECT_PATH + '\\data\paper_topic.json',
         'w').write(json.dumps(paper_topic))

    logging.info('paper topic saved.')


# 根据作者的论文数量对作者进行过滤
def filter_author_by_papernum(min=5, max=100, plot_distribution=True):

    logging.info('loading author paper num data ... ')

    author_year_papers = json.loads(
        open(APS_PROJECT_PATH + '\\data\\author_year_papers.json').read())

    author_papernum = json.loads(
        open(APS_PROJECT_PATH + '\\data\\author_papernum.json').read())

    paper_topic = json.loads(
        open(APS_PROJECT_PATH + '\\data\\paper_topic.json').read())

    logging.info('starting to stat ...')
    author_topics = {}

    for author in author_papernum.keys():

        papernum = author_papernum[author]

        if papernum < min or papernum > max:
            continue

        year_papaers = author_year_papers[author]

        topics = []
        for year in sorted(year_papaers, key=lambda x: int(x)):

            for paper in year_papaers[year]:
                topic = paper_topic.get(paper, None)
                if topic is not None:
                    topics.append(topic)

        author_topics[author] = topics

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


if __name__ == '__main__':

    # APS_PCASCODE_process()
    filter_author_by_papernum()