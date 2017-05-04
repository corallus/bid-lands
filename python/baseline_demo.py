from baseline import BaseLine

from settings import *


class BaseLineDemo(BaseLine):
    """
    Demo config
    """
    def getTrainData_b(self, ifname_data, ifname_bid):
        """
         
        :param ifname_data: String
        :param ifname_bid: String
        :return: w: List, winAuctions: List, winbid: Dict, losebid: Dict
        """
        fin = open(ifname_data, 'r')
        i = 0
        w = []
        winAuctions = []
        winbid = {}
        losebid = {}
        for line in fin:
            i += 1
            if i == 1:
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

