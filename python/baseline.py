# coding=utf-8
from DecisionTree import *
from evaluation import getANLP


class BaseLine(object):
    """
    Run configuration
    """

    def baseline(self, info):
        """
        :param info: Info
        :return: q: List[float], w: Union[float, dict, List[float]]
        """
        fout_baseline = open(info.fname_baseline, 'w')
        fout_q = open(info.fname_baseline_q, 'w')
        fout_w = open(info.fname_baseline_w, 'w')
        w, winAuctions, winbid, losebid = self.getTrainData_b(info.fname_trainlog, info.fname_trainbid)
        print "trainData read success."
        wt = self.getTestData_b(info.fname_testlog)
        print "testData read success."

        # get priceSet
        wcount = [0] * UPPER
        if info.mode == NORMAL or info.mode == SURVIVAL:
            for i in range(0, len(winAuctions)):
                if winAuctions[i] == 1:
                    wcount[w[i]] += 1
        if info.mode == FULL:
            for i in range(0, len(winAuctions)):
                wcount[w[i]] += 1

        minPrice = 0
        maxPrice = UPPER

        q = calProbDistribution(wcount, winbid, losebid, minPrice, maxPrice, info)
        w = q2w(q)
        print "q calculation success."

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
        priceSet = wt
        minPrice = 0
        maxPrice = max(priceSet)
        n = [0.] * UPPER
        for i in range(0, len(priceSet)):
            pay_price = priceSet[i]
            n[pay_price] += 1
        print "n calculation success."

        # qt,wt calculation
        qt = calProbDistribution_n(n, minPrice, maxPrice, info)
        wt = q2w(qt)

        # evaluation
        # ANLP
        fout_baseline.write("baseline campaign " + str(info.campaign) + " mode " + MODE_NAME_LIST[
            info.mode] + " basebid " + info.basebid + '\n')
        fout_baseline.write("laplace " + str(info.laplace) + "\n")
        print "baseline campaign " + str(info.campaign) + " mode " + MODE_NAME_LIST[info.mode] + " basebid " + info.basebid
        print "laplace " + str(info.laplace)
        for step in STEP_LIST:
            qi = changeBucketUniform(q, step)
            ni = deepcopy(n)
            bucket = len(qi)
            anlp, N = getANLP(qi, ni, minPrice, maxPrice)

            fout_baseline.write("bucket " + str(bucket) + " step " + str(step) + "\n")
            fout_baseline.write("Average negative log probability = " + str(anlp) + "  N = " + str(N) + "\n")
            print "bucket " + str(bucket) + " step " + str(step)
            print "Average negative log probability = " + str(anlp) + "  N = " + str(N)

        # KLD & pearsonr
        bucket = len(q)
        step = STEP_LIST[0]
        KLD = KLDivergence(q, qt)
        N = sum(n)
        fout_baseline.write("bucket " + str(bucket) + " step " + str(step) + "\n")
        fout_baseline.write("KLD = " + str(KLD) + "  N = " + str(N) + "\n")
        print "bucket " + str(bucket) + " step " + str(step)
        print "KLD = " + str(KLD) + "  N = " + str(N)

        fout_baseline.close()
        fout_q.close()
        fout_w.close()

        return q, w

    def getTrainData_b(self, ifname_data, ifname_bid):
        """
         
        :param ifname_data: String
        :param ifname_bid: String
        :return: w: List, winAuctions: List, winbid: Dict, losebid: Dict
        """
        line_num = 0
        fi = open(ifname_data, 'r')
        for line in fi:
            if line.strip():
                line_num += 1
        fi.close()
        seg_point = (line_num - 1) / 3

        # get all price (2/3)
        fin = open(ifname_data, 'r')
        i = 0
        w = []
        winAuctions = []
        winbid = {}
        losebid = {}
        for line in fin:
            i += 1
            if i <= seg_point + 1:
                continue
            w.append(eval(line.split()[PAY_PRICE_INDEX]))
        fin.close()

        i = -1
        fin = open(ifname_bid, 'r')
        for line in fin:
            i += 1
            linelist = line.split()
            mybidprice = eval(linelist[0])
            winAuction = eval(linelist[1])
            winAuctions.append(winAuction)
            if winAuction == 1:
                if not winbid.has_key(w[i]):
                    winbid[w[i]] = 0
                winbid[w[i]] += 1
            elif winAuction == 0:
                if not losebid.has_key(mybidprice):
                    losebid[mybidprice] = 0
                losebid[mybidprice] += 1
        fin.close()
        print len(w), i + 1

        return w, winAuctions, winbid, losebid

    def getTestData_b(self, ifname_data):
        """
        
        :param ifname_data: String 
        :return: wt: List 
        """
        fin = open(ifname_data, 'r')
        wt = []
        i = -2
        for line in fin:
            i += 1
            if i == -1:
                continue
            wt.append(eval(line.split()[PAY_PRICE_INDEX]))
        fin.close()

        return wt
