from os.path import join, abspath, dirname, pardir
WebListDir = './sites.txt'
Pardir = abspath(join(dirname(__file__), pardir))
DumpDir = join( Pardir , "AlexaCrawler/dump")
SOFT_VISIT_TIMEOUT = 60
HARD_VISIT_TIMEOUT = SOFT_VISIT_TIMEOUT + 20
GAP_BETWEEN_BATCHES = 2
GAP_BETWEEN_SITES = 5
GAP_AFTER_LAUNCH = 5
padding_time = 4
My_Bridge_Ips = ['13.75.78.82', '52.175.31.228', '52.175.49.114','40.83.88.194', '13.94.61.159']
