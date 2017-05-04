import time

from baseline_kdd15_Rversion import baseline_kdd15_Rversion
from enlargeLeafSize import enlargeLeafSize
from evaluation import *
from merge_eval import merge_eval
from settings import *
from treeDepthEval import treeDepthEval
from baseline import *


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
            info.fname_trainlog = os.path.join(campaign_data_dir, 'train.log.txt')
            info.fname_testlog = os.path.join(campaign_data_dir, 'test.log.txt')
            info.fname_nodeData = os.path.join(mode_dir, 'nodeData_%s%s.txt' % (campaign, suffix))
            info.fname_nodeInfo = os.path.join(mode_dir, 'nodeInfos_%s%s.txt' % (campaign, suffix))

            info.fname_trainbid = os.path.join(campaign_data_dir, 'train_bid.txt')
            info.fname_testbid = os.path.join(campaign_data_dir, 'test_bid.txt')
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
            baseline = BaseLine()
            baseline.baseline(info)
            print campaign + " " + modeName + " baseline ends."
            # getDataset
            dataset = getTrainData(info.fname_trainlog, info.fname_trainbid)

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


def paraTune(campaign_list):
    """

    :param campaign_list: List[String] 
    """
    runtimes_leafSize = {}
    for campaign in campaign_list:
        runtimes_leafSize[campaign] = {}
        # create os directory
        campaign_results_dir = os.path.join(SURVIVAL_MODEL, campaign)
        if not os.path.exists(campaign_results_dir):
            os.makedirs(campaign_results_dir)
        campaign_data_dir = os.path.join(MAKE_IPINYOU_DATA, campaign)
        if not os.path.exists(campaign_data_dir):
            os.makedirs(campaign_data_dir)

        for mode in MODE_LIST:
            runtimes_leafSize[campaign][mode] = {}
            modeName = MODE_NAME_LIST[mode]
            suffix = SUFFIX_LIST[mode]

            # create os directory
            mode_dir = os.path.join(campaign_results_dir, modeName)
            if not os.path.exists(mode_dir):
                os.makedirs(mode_dir)
            paratune_dir = os.path.join(mode_dir, 'paraTune')
            if not os.path.exists(paratune_dir):
                os.makedirs(paratune_dir)

            ##################################   leafSize   ######################################
            for leafSize in [0]:
                start_time = time.clock()

                info = Info()
                info.basebid = BASE_BID
                info.campaign = campaign
                info.mode = mode

                info.laplace = LAPLACE
                info.leafSize = leafSize  #
                info.treeDepth = TREE_DEPTH

                # create os directory
                leaf_dir = os.path.join(paratune_dir, 'leafSize_%s' % leafSize)
                if not os.path.exists(leaf_dir):
                    os.makedirs(leaf_dir)
                # info assignment
                info.fname_trainlog = os.path.join(campaign_data_dir, 'train.log.txt')
                info.fname_testlog = os.path.join(campaign_data_dir, 'test.log.txt')
                info.fname_nodeData = os.path.join(leaf_dir, 'nodeData_%s%s.txt' % (campaign, suffix))
                info.fname_nodeInfo = os.path.join(leaf_dir, 'nodeInfos_%s%s.txt' % (campaign, suffix))

                info.fname_trainbid = os.path.join(campaign_data_dir, 'train_bid.txt')
                info.fname_testbid = os.path.join(campaign_data_dir, 'test_bid.txt')
                info.fname_baseline = os.path.join(leaf_dir, 'baseline_%s%s.txt' % (campaign, suffix))

                info.fname_monitor = os.path.join(leaf_dir, 'monitor_%s%s.txt' % (campaign, suffix))
                info.fname_testKmeans = os.path.join(leaf_dir, 'testKmeans_%s%s.txt' % (campaign, suffix))
                info.fname_testSurvival = os.path.join(leaf_dir, 'testSurvival_%s%s.txt' % (campaign, suffix))

                info.fname_evaluation = os.path.join(leaf_dir, 'evaluation_%s%s.txt' % (campaign, suffix))
                info.fname_baseline_q = os.path.join(leaf_dir, 'baseline_q_%s%s.txt' % (campaign, suffix))
                info.fname_tree_q = os.path.join(leaf_dir, 'tree_q_%s%s.txt' % (campaign, suffix))
                info.fname_baseline_w = os.path.join(leaf_dir, 'baseline_w_%s%s.txt' % (campaign, suffix))
                info.fname_tree_w = os.path.join(leaf_dir, 'tree_w_%s%s.txt' % (campaign, suffix))

                info.fname_pruneNode = os.path.join(leaf_dir, 'pruneNode_%s%s.txt' % (campaign, suffix))
                info.fname_pruneEval = os.path.join(leaf_dir, 'pruneEval_%s%s.txt' % (campaign, suffix))
                info.fname_testwin = os.path.join(leaf_dir, 'testwin_%s%s.txt' % (campaign, suffix))
                # baseline
                print campaign, modeName, 'leafSize', leafSize, "baseline begins."
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                baseline(info)
                print campaign, modeName, 'leafSize', leafSize, "baseline ends."
                # getDataset
                dataset = getTrainData(info.fname_trainlog, info.fname_trainbid)

                print campaign, modeName, 'leafSize', leafSize, "decisionTree2 begins."
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                decisionTree2(dataset, info)

                # evaluation
                print campaign, modeName, 'leafSize', leafSize, "evaluation begins."
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                evaluate(info)

                # runtime
                end_time = time.clock()
                runtimes_leafSize[campaign][mode][leafSize] = end_time - start_time

                print campaign, modeName, leafSize, "run time: " + str(end_time - start_time) + " s"

    for campaign in runtimes_leafSize:
        for mode in runtimes_leafSize[campaign]:
            for leafSize in runtimes_leafSize[campaign][mode]:
                print campaign, MODE_NAME_LIST[mode], 'leafSize', leafSize, "runtime " + str(
                    runtimes_leafSize[campaign][mode][leafSize])


# campaign_list = CAMPAIGN_LIST
campaign_list = ['2997']

main(campaign_list)
paraTune(campaign_list)
enlargeLeafSize(campaign_list)
treeDepthEval(campaign_list)
baseline_kdd15_Rversion(campaign_list)
merge_eval(campaign_list)
