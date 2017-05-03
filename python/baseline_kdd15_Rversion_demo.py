from baseline_kdd15_Rversion import *


def baseline_kdd15_Rversion_demo(campaign_list):
    """

    :param campaign_list: List[String] 
    """
    BASE_BID = '0'
    IFROOT_TRAIN = '../data/kdd15/WinningPrice/'
    IFROOT_TEST = '../make-ipinyou-data/'
    OFROOT = '../data/baseline_kdd15_Rversion/'

    q = {}
    w = {}
    for campaign in campaign_list:
        print
        print campaign
        # create os directory
        if not os.path.exists(OFROOT + campaign):
            os.makedirs(OFROOT + campaign)
        # info assignment
        info = Info()
        info.basebid = BASE_BID
        info.campaign = campaign
        info.laplace = LAPLACE
        info.fname_trainlog = IFROOT_TRAIN + 'price_all_'
        info.fname_testlog = IFROOT_TEST + campaign + '/test.yzx.demo.txt'
        info.fname_baseline_kdd15 = OFROOT + campaign + '/baseline_kdd15_' + campaign + '.txt'
        info.fname_baseline_kdd15_q = OFROOT + campaign + '/baseline_kdd15_q_' + campaign + '.txt'
        info.fname_baseline_kdd15_w = OFROOT + campaign + '/baseline_kdd15_w_' + campaign + '.txt'

        q[campaign], w[campaign] = baseline_kdd15_Rversion0(info)


if __name__ == '__main__':
    baseline_kdd15_Rversion_demo(CAMPAIGN_LIST)
