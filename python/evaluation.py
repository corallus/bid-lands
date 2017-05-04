from random import randint

from matplotlib.pyplot import *

from DecisionTree import *
from settings import *


def isChild(p, c):
    """

    :param p: Int 
    :param c: Int
    :return: Bool
    """
    while p < c:
        c /= 2
    if p == c:
        return True
    else:
        return False


# get q of any node
def getNodeQ(nodeIndex, mp, info):
    """
    
    :param nodeIndex: Int
    :param mp: 
    :param info: 
    :return: 
    """
    laplace = info.laplace
    q = [0.0] * UPPER
    count = 0
    for k in mp.keys():
        if not isChild(nodeIndex, k):
            continue
        for i in range(0, len(mp[k])):
            q[i] += mp[k][i]
            count += mp[k][i]

    for i in range(0, len(q)):
        q[i] = (q[i] + laplace) / (count + len(q) * laplace)  # laplace

    return q


def plotSubBidLands(q1, q2, nodeInfo):
    """

    :param q1: List[Float]
    :param q2: List[Float]
    :param nodeInfo: NodeInfo
    """
    logq1 = [log(x) for x in q1]
    logq2 = [log(x) for x in q2]

    figure(1)
    figure(figsize=(6, 5))

    grid(True)
    plot(range(0, len(logq1)), logq1, 'sb-')
    plot(range(0, len(logq2)), logq2, '+r-')
    xlabel("market price")
    ylabel("market price log probability")
    legend(['Set1', 'Set2'], loc='upper right')

    # tight_layout()
    close(1)


def getNodeInfos(info):
    """

    :param info: Info
    :return: List[NodeInfo]
    """
    print "getNodeInfos()"
    fin_nodeInfo = open(info.fname_nodeInfo, 'r')
    lines = fin_nodeInfo.readlines()

    nodeInfos = {}
    lineIndex = 0
    for line in lines:
        lineIndex += 1
        if len(line) == 0:
            print "Empty line: " + str(lineIndex)
            continue
        items = line.split()

        if lineIndex % 6 == 1:
            nodeIndex = eval(items[1])
        if lineIndex % 6 == 2:
            bestFeat = eval(items[2])
            KLD = eval(items[4])
        if lineIndex % 6 == 4:
            s1 = []
            for i in range(0, len(items)):
                s1.append(items[i])
        if lineIndex % 6 == 0:
            s2 = []
            for i in range(0, len(items)):
                s2.append(items[i])
            nodeInfos[nodeIndex] = NodeInfo(nodeIndex, bestFeat, KLD, deepcopy(s1), deepcopy(s2))

    print "getNodeInfos() ends."
    return nodeInfos


def getTrainPriceCount(info):
    """

    :param info: Info
    :return: wcount: Dict, winbids: Dict, losebids: Dict, minPrice: Float, maxPrice: Float, mp: Dict
    """
    print "getTrainPriceCount()"
    fin_nodeData = open(info.fname_nodeData, 'r')
    lines = fin_nodeData.readlines()
    wcount = {}
    winbids = {}
    losebids = {}
    minPrice = 0
    maxPrice = 0
    mp = {}

    for line in lines:
        items = line.split()
        if items[0] == "nodeIndex":
            nodeIndex = eval(items[1])
            if not wcount.has_key(nodeIndex):
                wcount[nodeIndex] = [0] * UPPER
                winbids[nodeIndex] = {}
                losebids[nodeIndex] = {}
                mp[nodeIndex] = [0] * UPPER
            continue

        if len(items) < WIN_AUCTION_INDEX:
            for i in range(0, len(items)):
                print str(items[i]),
            print
            continue

        pay_price = eval(items[PAY_PRICE_INDEX])
        mp[nodeIndex][pay_price] += 1

        if eval(items[WIN_AUCTION_INDEX]) == 0:
            mybidprice = eval(items[MY_BID_INDEX])
            if not losebids[nodeIndex].has_key(mybidprice):
                losebids[nodeIndex][mybidprice] = 0
            losebids[nodeIndex][mybidprice] += 1
            continue

        if not winbids[nodeIndex].has_key(pay_price):
            winbids[nodeIndex][pay_price] = 0
        winbids[nodeIndex][pay_price] += 1

        wcount[nodeIndex][pay_price] += 1

        if minPrice > pay_price:
            minPrice = pay_price
        if maxPrice < pay_price:
            maxPrice = pay_price

    print "getTrainPriceSet() ends."
    return wcount, winbids, losebids, minPrice, maxPrice, mp


def getQ(info):
    """

    :param info: Info
    :return: q: Dict, minPrice: Float, maxPrice: Float
    """
    print "getQ()"
    fout_q = open(info.fname_tree_q, 'w')
    fout_w = open(info.fname_tree_w, 'w')
    q = {}
    w = {}
    num = {}  # num of
    bnum = {}
    wcount, winbids, losebids, minPrice, maxPrice, mp = getTrainPriceCount(info)

    # get q
    for k in wcount.keys():
        q[k] = calProbDistribution(wcount[k], winbids[k], losebids[k], minPrice, maxPrice, info)
        w[k] = q2w(q[k])
        num[k] = sum(wcount[k])
        b1 = set(winbids[k].keys())
        b2 = set(losebids[k].keys())
        b = b1 | b2
        bnum[k] = len(b)

    # fout
    for k in q.keys():
        fout_q.write('nodeIndex ' + str(k) + ' num ' + str(num[k]) + ' bnum ' + str(bnum[k]) + '\n')
        if len(q[k]) == 0:
            continue
        for i in range(0, len(q[k])):
            fout_q.write(str(q[k][i]) + ' ')
        fout_q.write(str(sum(q[k])))
        fout_q.write(' ' + str(num[k]) + ' ' + str(bnum[k]))
        fout_q.write('\n')
    fout_q.close()
    for k in w.keys():
        fout_w.write('nodeIndex ' + str(k) + ' len ' + str(num[k]) + '\n')
        if len(w[k]) == 0:
            continue
        fout_w.write(str(w[k][0]))
        for i in range(1, len(w[k])):
            fout_w.write(' ' + str(w[k][i]))
        fout_w.write('\n')
    fout_w.close()

    print "getQ() ends."
    return q, minPrice, maxPrice


def getN(info):
    """

    :param info: Info 
    :return: n: Dict, minPrice: Float, maxPrice: Float
    """
    print "getN()"
    testset = getTestData(info.fname_testlog)
    nodeInfos = getNodeInfos(info)
    n = {}
    priceSet = [eval(data[PAY_PRICE_INDEX]) for data in testset]
    minPrice = 0
    maxPrice = max(priceSet)

    for i in range(0, len(testset)):
        if i % 10000 == 0:
            print str(i),

        pay_price = eval(testset[i][PAY_PRICE_INDEX])
        nodeIndex = 1
        if len(nodeInfos.keys()) == 0:
            if not n.has_key(nodeIndex):
                n[nodeIndex] = [0.] * UPPER
            n[nodeIndex][pay_price] += 1
            continue
        while True:
            bestFeat = nodeInfos[nodeIndex].bestFeat
            KLD = nodeInfos[nodeIndex].KLD
            s1_keys = nodeInfos[nodeIndex].s1_keys
            s2_keys = nodeInfos[nodeIndex].s2_keys
            if testset[i][bestFeat] in s1_keys:
                nodeIndex = 2 * nodeIndex
            elif testset[i][bestFeat] in s2_keys:
                nodeIndex = 2 * nodeIndex + 1
            else:  # feature value doesn't appear in train data
                nodeIndex = 2 * nodeIndex + randint(0, 1)

            if not nodeInfos.has_key(nodeIndex):
                if not n.has_key(nodeIndex):
                    n[nodeIndex] = [0.] * UPPER
                n[nodeIndex][pay_price] += 1

                break

    print "\ngetN() ends."
    return n, minPrice, maxPrice


def getANLP(q, n, minPrice, maxPrice):
    """

    :param q: 
    :param n: 
    :param minPrice: Int
    :param maxPrice: Int
    :return: Int 
    """
    anlp = 0.0
    N = 0
    if isinstance(q, dict):
        for k in n.keys():
            if not q.has_key(k):
                print k
                continue
            for i in range(0, len(n[k])):
                if i > len(q[k]) - 1:  # test price doesn't appear in train price
                    break  # remain to be modify
                if q[k][i] < 0:
                    print q[k][i]
                anlp += -log(q[k][i]) * n[k][i]
                N += n[k][i]
        anlp = anlp / N
    if isinstance(q, list):
        for i in range(0, len(n)):
            if i > len(q) - 1:
                break
            anlp += -log(q[i]) * n[i]
            N += n[i]
        anlp = anlp / N

    return anlp, N


def evaluate(info):
    """

    :param info: Info
    :return: None
    """
    fout_evaluation = open(info.fname_evaluation, 'w')
    fout_evaluation.write("evaluation campaign " + str(info.campaign) + " mode " + MODE_NAME_LIST[
        info.mode] + " basebid " + info.basebid + '\n')
    fout_evaluation.write("laplace " + str(info.laplace) + "\n")
    print "evaluation campaign " + str(info.campaign) + " mode " + MODE_NAME_LIST[
        info.mode] + " basebid " + info.basebid
    print "laplace " + str(info.laplace)

    _q, trainMinPrice, trainMaxPrice = getQ(info)
    _n, testMinPrice, testMaxPrice = getN(info)
    for eval_mode in EVAL_MODE_LIST:
        if eval_mode == '0':
            ### ANLP
            fout_evaluation.write("eval mode = ANLP\n")
            print "eval mode = ANLP"
            bucket = 0
            anlp = 0
            N = 0
            for step in STEP_LIST:
                q = deepcopy(_q)
                n = deepcopy(_n)
                for k in q.keys():
                    q[k] = changeBucketUniform(q[k], step)
                    bucket = len(q[k])
                anlp, N = getANLP(q, n, trainMinPrice, trainMaxPrice)
                # fout_evaluation
                fout_evaluation.write("bucket " + str(bucket) + " step " + str(step) + "\n")
                fout_evaluation.write("Average negative log probability = " + str(anlp) + "  N = " + str(N) + "\n")
                print "bucket " + str(bucket) + " step " + str(step)
                print "Average negative log probability = " + str(anlp) + "  N = " + str(N)

            ### KLD
            fout_evaluation.write("eval mode = KLD\n")
            print "eval mode = KLD"
            q = deepcopy(_q)
            n = deepcopy(_n)
            w = q2w(q)
            KLD = 0.
            N = 0
            for k in q.keys():
                if not n.has_key(k):
                    continue
                qtk = calProbDistribution_n(n[k], trainMinPrice, trainMaxPrice, info)
                wtk = q2w(qtk)
                count = sum(n[k])
                KLD += KLDivergence(q[k], qtk) * count
                N += count
            KLD /= N

            # fout_evaluation
            bucket = len(q[q.keys()[0]])
            step = STEP_LIST[0]
            fout_evaluation.write("bucket " + str(bucket) + " step " + str(step) + "\n")
            fout_evaluation.write("KLD = " + str(KLD) + "  N = " + str(N) + "\n")
            print "bucket " + str(bucket) + " step " + str(step)
            print "KLD = " + str(KLD) + "  N = " + str(N)

    fout_evaluation.close()
    return


if __name__ == '__main__':
    for campaign in CAMPAIGN_LIST:
        print
        print campaign
        for mode in MODE_LIST:
            suffix = SUFFIX_LIST[mode]
            modeName = MODE_NAME_LIST[mode]
            # create os directory
            mode_dir = os.path.join(SURVIVAL_MODEL, campaign, modeName)
            if not os.path.exists(mode_dir):
                os.makedirs(mode_dir)
            plot_dir = os.path.join(mode_dir, 'plot')
            if not os.path.exists(plot_dir):
                os.makedirs(plot_dir)
            for laplace in [LAPLACE]:
                print MODE_NAME_LIST[mode],
                info = Info()
                info.laplace = laplace
                info.basebid = BASE_BID
                info.mode = mode
                info.campaign = campaign
                info.fname_trainlog = os.path.join(MAKE_IPINYOU_DATA, campaign, 'train.log.txt')
                info.fname_testLog = os.path.join(MAKE_IPINYOU_DATA, campaign, 'test.log.txt')
                info.fname_nodeData = os.path.join(mode_dir, 'nodeData_%s%s.txt' % (campaign, suffix))
                info.fname_nodeInfo = os.path.join(mode_dir, 'nodeInfos_%s%s.txt' % (campaign, suffix))

                info.fname_trainbid = os.path.join(MAKE_IPINYOU_DATA, campaign, 'train_bid.txt')
                info.fname_testbid = os.path.join(MAKE_IPINYOU_DATA, campaign, 'test_bid.txt')
                info.fname_baseline = os.path.join(mode_dir, 'baseline_%s%s.txt' % (campaign, suffix))

                info.fname_monitor = os.path.join(mode_dir, 'monitor_%s%s.txt' % (campaign, suffix))
                info.fname_testKmeans = os.path.join(mode_dir, 'testKmeans_%s%s.txt' % (campaign, suffix))
                info.fname_testSurvival = os.path.join(mode_dir, 'testSurvival_%s%s.txt' % (campaign, suffix))

                info.fname_evaluation = os.path.join(mode_dir, 'evaluation_%s%s.txt' % (campaign, suffix))
                info.fname_baseline_q = os.path.join(mode_dir, 'baseline_q_%s%s.txt' % (campaign, suffix))
                info.fname_tree_q = os.path.join(mode_dir, 'tree_q_%s%s.txt' % (campaign, suffix))
                info.fname_baseline_w = os.path.join(mode_dir, 'baseline_w_%s%s.txt' % (campaign, suffix))
                info.fname_tree_w = os.path.join(mode_dir, 'tree_w_%s%s.txt' % (campaign, suffix))
                info.fname_test_w = os.path.join(mode_dir, 'test_w_%s%s.txt' % (campaign, suffix))

                info.fname_pruneNode = os.path.join(mode_dir, 'pruneNode_%s%s.txt' % (campaign, suffix))
                info.fname_pruneEval = os.path.join(mode_dir, 'pruneEval_%s%s.txt' % (campaign, suffix))
                info.fname_testwin = os.path.join(mode_dir, 'testwin_%s%s.txt' % (campaign, suffix))

                # evaluation
                evaluate(info)
