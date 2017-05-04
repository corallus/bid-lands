from baseline_kdd15_Rversion import *


def baseline_kdd15_Rversion_demo(campaign_list):
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
        info.fname_testlog = os.path.join(MAKE_IPINYOU_DATA, campaign, 'test.yzx.demo.txt')
        info.fname_baseline_kdd15 = os.path.join(results_dir, 'baseline_kdd15_%s.txt' % campaign)
        info.fname_baseline_kdd15_q = os.path.join(results_dir, 'baseline_kdd15_q_%s.txt' % campaign)
        info.fname_baseline_kdd15_w = os.path.join(results_dir, 'baseline_kdd15_w_%s.txt' % campaign)

        q[campaign], w[campaign] = baseline_kdd15_Rversion0(info)


if __name__ == '__main__':
    baseline_kdd15_Rversion_demo(CAMPAIGN_LIST)
