# coding=utf-8
import time

from DecisionTree import *
from evaluation import getANLP
from settings import *


def getWinningPrice(ifname_price):
    """

    :param ifname_price: String 
    :return: List[Int] 
    """
    fin = open(ifname_price, 'r')
    w = []
    for line in fin:
        w.append(int(round(eval(line.split()[0]))))
    fin.close()
    return w


def getTestData_yzx(ifname_data):
    """

    :param ifname_data: String 
    :return: List[Any] 
    """
    fin = open(ifname_data, 'r')
    wt = []

    for line in fin:
        items = line.split()
        wt.append(eval(items[1]))

    fin.close()
    return wt


def getQ(w, info):
    """

    :param w: List[] 
    :param info: Info
    :return: [Float]
    """
    laplace = info.laplace
    q = [0.0] * UPPER
    count = 0
    for i in range(0, len(w)):
        q[w[i]] += 1
        count += 1

    for i in range(0, len(q)):
        q[i] = (q[i] + laplace) / (count + len(q) * laplace)  # laplace

    return q


def baseline_kdd15_Rversion0(info):
    """

    :param info: Info
    :return: q: List[Float], w: Union[float, dict, List[float]]
    """
    w = []
    for day in DAY_LIST:
        tmpw = getWinningPrice(os.path.join(info.fname_trainlog, 'price_all_%s.txt' % day))
        w.extend(tmpw)
    wt = getTestData_yzx(info.fname_testlog)

    # q calculation
    q = getQ(w, info)
    w = q2w(q)
    fout_q = open(info.fname_baseline_kdd15_q, 'w')
    fout_w = open(info.fname_baseline_kdd15_w, 'w')
    if len(q) != 0:
        fout_q.write(str(q[0]))
        for i in range(1, len(q)):
            fout_q.write(' ' + str(q[i]))
    fout_q.close()
    if len(w) != 0:
        fout_w.write(str(w[0]))
        for i in range(1, len(w)):
            fout_w.write(' ' + str(w[i]))
    fout_w.close()

    # n calculation
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), "n calculation begins."
    minPrice = 0
    maxPrice = max(wt)
    n = [0.] * UPPER
    for pay_price in wt:
        n[pay_price] += 1

    # qt,wt calculation
    qt = calProbDistribution_n(n, minPrice, maxPrice, info)
    wt = q2w(qt)

    # evaluation
    fout_baseline_kdd15 = open(info.fname_baseline_kdd15, 'w')
    fout_baseline_kdd15.write("baseline_kdd15 campaign " + str(info.campaign) + " basebid " + info.basebid + '\n')
    print "baseline campaign " + str(info.campaign) + " basebid " + info.basebid
    for step in STEP_LIST:
        qi = changeBucketUniform(q, step)
        ni = deepcopy(n)
        bucket = len(qi)
        anlp, N = getANLP(qi, ni, minPrice, maxPrice)

        fout_baseline_kdd15.write("bucket " + str(bucket) + " step " + str(step) + "\n")
        fout_baseline_kdd15.write("Average negative log probability = " + str(anlp) + "  N = " + str(N) + "\n")
        print "bucket " + str(bucket) + " step " + str(step)
        print "Average negative log probability = " + str(anlp) + "  N = " + str(N)

    # KLD
    bucket = len(q)
    step = STEP_LIST[0]
    KLD = KLDivergence(q, qt)
    N = sum(n)
    fout_baseline_kdd15.write("bucket " + str(bucket) + " step " + str(step) + "\n")
    fout_baseline_kdd15.write("KLD = " + str(KLD) + "  N = " + str(N) + "\n")
    print "bucket " + str(bucket) + " step " + str(step)
    print "KLD = " + str(KLD) + "  N = " + str(N)

    fout_baseline_kdd15.close()
    fout_q.close()
    fout_w.close()

    return q, w


def baseline_kdd15_Rversion(campaign_list):
    """

    :param campaign_list: List[String] 
    """

    q = {}
    w = {}
    for campaign in campaign_list:
        print
        print campaign
        # create os directory
        results_dir = os.path.join(KDD15_RESULTS, campaign)
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        # info assignment
        info = Info()
        info.basebid = BASE_BID
        info.campaign = campaign
        info.laplace = LAPLACE
        info.fname_trainlog = KDD15_TRAIN
        info.fname_testlog = os.path.join(MAKE_IPINYOU_DATA, campaign, 'test.yzx.txt')
        info.fname_baseline_kdd15 = os.path.join(results_dir, 'baseline_kdd15_%s.txt' % campaign)
        info.fname_baseline_kdd15_q = os.path.join(results_dir, 'baseline_kdd15_q_%s.txt' % campaign)
        info.fname_baseline_kdd15_w = os.path.join(results_dir, 'baseline_kdd15_w_%s.txt' % campaign)

        q[campaign], w[campaign] = baseline_kdd15_Rversion0(info)


if __name__ == '__main__':
    baseline_kdd15_Rversion(CAMPAIGN_LIST)
