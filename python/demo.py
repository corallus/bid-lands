import time

from baseline_kdd15_Rversion_demo import baseline_kdd15_Rversion_demo
from evaluation import *
from merge_eval_demo import merge_eval_demo
from baseline_demo import *
from settings import *


def getTrainData_demo(ifname_data, ifname_bid):
    """
    returns training data
    :param ifname_data: String 
    :param ifname_bid: String
    :return: List[List] 
    """

    fin = open(ifname_data, 'r')
    lines = fin.readlines()
    dataset = []
    i = -2
    for line in lines:
        i += 1
        if i == -1:
            featName = line.split()
            featName.append('nclick')  # 27
            featName.append('nconversation')  # 28
            featName.append('index')  # 29
            featName.append('mybidprice')  # 30
            featName.append('winAuction')  # 31
            continue

        items = line.split()
        dataset.append(items)
        dataset[len(dataset) - 1].append('0')  # virtual value
        dataset[len(dataset) - 1].append('0')  # virtual value
        dataset[len(dataset) - 1].append(str(len(dataset) - 1))  # ith row from i=0
    fin.close()

    fin = open(ifname_bid, 'r')
    lines = fin.readlines()
    i2 = -1
    for line in lines:
        i2 += 1
        linelist = line.split()
        mybidprice = linelist[0]
        winAuction = linelist[1]
        dataset[i2].append(mybidprice)
        dataset[i2].append(winAuction)
    # monitor

    fin.close()
    return dataset


def main(campaign_list):
    """
    generate DecisionTree and fout
    :param campaign_list: List[String]
    """
    runtimes = {}
    for campaign in campaign_list:
        # create os directory
        campaign_results_dir = os.path.join(SURVIVAL_MODEL, campaign)
        if not os.path.exists(campaign_results_dir):
            os.makedirs(campaign_results_dir)
        campaign_data_dir = os.path.join(MAKE_IPINYOU_DATA, campaign)
        if not os.path.exists(campaign_data_dir):
            os.makedirs(campaign_data_dir)
        for mode in MODE_LIST:
            # tempt filter
            start_time = time.clock()

            info = Info()
            info.basebid = BASE_BID
            info.campaign = campaign
            info.mode = mode
            modeName = MODE_NAME_LIST[mode]
            suffix = SUFFIX_LIST[mode]

            info.laplace = LAPLACE
            info.leafSize = LEAF_SIZE
            info.treeDepth = TREE_DEPTH

            # create os directory
            mode_dir = os.path.join(campaign_results_dir, modeName)
            if not os.path.exists(mode_dir):
                os.makedirs(mode_dir)
            # info assignment
            info.fname_trainlog = os.path.join(campaign_data_dir, 'train.log.demo.txt')
            info.fname_testlog = os.path.join(campaign_data_dir, 'test.log.demo.txt')
            info.fname_nodeData = os.path.join(mode_dir, 'nodeData_%s%s.txt' % (campaign, suffix))
            info.fname_nodeInfo = os.path.join(mode_dir, 'nodeInfos_%s%s.txt' % (campaign, suffix))

            info.fname_trainbid = os.path.join(campaign_data_dir, 'train_bid_demo.txt')
            info.fname_testbid = os.path.join(campaign_data_dir, 'test_bid_demo.txt')
            info.fname_baseline = os.path.join(mode_dir, 'baseline_%s%s.txt' % (campaign, suffix))

            info.fname_monitor = os.path.join(mode_dir, 'monitor_%s%s.txt' % (campaign, suffix))
            info.fname_testKmeans = os.path.join(mode_dir, 'testKmeans_%s%s.txt' % (campaign, suffix))
            info.fname_testSurvival = os.path.join(mode_dir, 'testSurvival_%s%s.txt' % (campaign, suffix))

            info.fname_evaluation = os.path.join(mode_dir, 'evaluation_%s%s.txt' % (campaign, suffix))
            info.fname_baseline_q = os.path.join(mode_dir, 'baseline_q_%s%s.txt' % (campaign, suffix))
            info.fname_tree_q = os.path.join(mode_dir, 'tree_q_%s%s.txt' % (campaign, suffix))
            info.fname_baseline_w = os.path.join(mode_dir, 'baseline_w_%s%s.txt' % (campaign, suffix))
            info.fname_tree_w = os.path.join(mode_dir, 'tree_w_%s%s.txt' % (campaign, suffix))

            info.fname_pruneNode = os.path.join(mode_dir, 'pruneNode_%s%s.txt' % (campaign, suffix))
            info.fname_pruneEval = os.path.join(mode_dir, 'pruneEval_%s%s.txt' % (campaign, suffix))
            info.fname_testwin = os.path.join(mode_dir, 'testWin_%s%s.txt' % (campaign, suffix))
            # baseline
            print campaign + " " + modeName + " baseline begins."
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            baseline = BaseLineDemo()
            baseline.baseline(info)
            print campaign + " " + modeName + " baseline ends."
            # getDataset
            dataset = getTrainData_demo(info.fname_trainlog, info.fname_trainbid)

            print campaign + " " + modeName + " decisionTree2 begins."
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            decisionTree2(dataset, info)

            # evaluation
            print "evaluation begins."
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            evaluate(info)

            # runtime
            end_time = time.clock()
            if not runtimes.has_key(campaign):
                runtimes[campaign] = []
            runtimes[campaign].append(end_time - start_time)

            print campaign + " run time: " + str(end_time - start_time) + " s"

    for campaign in runtimes:
        for mode in range(0, len(runtimes[campaign])):
            print campaign + " " + MODE_NAME_LIST[mode] + " runtime " + str(runtimes[campaign][mode])


campaign_list = ['2259']
main(campaign_list)
baseline_kdd15_Rversion_demo(campaign_list)
merge_eval_demo(campaign_list)
