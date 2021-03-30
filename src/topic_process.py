#coding:utf-8

from basic_config import *
'''
APS处理处理

1. 保留文章数量超过100的主题, 65个主题，
2. 查看保留主题的分布
3. TOP10主题随着年份的变化

'''

APS_PROJECT_PATH = 'F:\\APS_data_processing'


def APS_PCASCODE_process():

    paper_year = json.loads(
        open(APS_PROJECT_PATH + '\\data\\pid_pubyear.json').read())

    logging.info(f'{len(paper_year)} has year labels.')

    topic_year_num = defaultdict(lambda: defaultdict(int))

    paper_topic = {}
    topic_num = defaultdict(int)
    for line in open('G:\\APS\\PCAS.txt', encoding='utf-8'):

        line = line.strip()

        if line.startswith('DOI'):
            continue

        splits = line.split(',')

        doi = splits[0]

        year = paper_year.get(doi, None)

        if year is None:
            continue

        codes = []
        for code in splits[1:]:

            if code.strip() == '':
                continue

            # 只保留一级主题
            codes.append(code.split('.')[0].split(' ')[-1])

        topic_counter = Counter(codes)
        # 选取出现次数最高的主题
        topic = sorted(topic_counter.keys(),
                       key=lambda x: topic_counter[x],
                       reverse=True)[0]

        topic_year_num[topic][year] += 1

        paper_topic[doi] = topic

        topic_num[topic] += 1

    logging.info('{} papers has topics.'.format(len(paper_topic)))

    open(APS_PROJECT_PATH + '\\data\paper_topic.json',
         'w').write(json.dumps(paper_topic))

    logging.info(f'{len(paper_topic)} new paper topic saved.')

    open('data/topic_year_num.json', 'w').write(json.dumps(topic_year_num))

    selected_topics = set([t for t in topic_num.keys() if topic_num[t] > 100])

    logging.info(f'number of topics:{len(selected_topics)}')

    new_paper_topic = {}
    for paper in paper_topic.keys():
        if paper_topic[paper] in selected_topics:
            new_paper_topic[paper] = paper_topic[paper]

    open('data/paper_topic.json', 'w').write(json.dumps(new_paper_topic))
    logging.info(f'{len(new_paper_topic)} new paper topic saved.')

    logging.info('data saved.')

    xs = []
    ys = []
    for i, st in enumerate(
            sorted(selected_topics, key=lambda x: topic_num[x], reverse=True)):
        xs.append(i + 1)
        ys.append(topic_num[st])

    plt.figure(figsize=(5, 4))

    plt.plot(xs, ys)

    plt.xlabel('topic rank')
    plt.ylabel('number of publications ')

    plt.yscale('log')
    plt.ylim(100, 30000)

    plt.tight_layout()

    plt.savefig('fig/topic_dis.png', dpi=400)


if __name__ == '__main__':

    APS_PCASCODE_process()
