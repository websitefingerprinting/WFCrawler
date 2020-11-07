import subprocess
import os
import sys
from os import makedirs
import argparse
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
import utils as ut
from common import *
from torcontroller import *
import logging
import math
import datetime


def config_logger(log_file):
    logger = logging.getLogger("crawler")
    # Set logging format
    LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    # Set file
    ch1 = logging.StreamHandler(sys.stdout)
    ch1.setFormatter(logging.Formatter(LOG_FORMAT))
    ch1.setLevel(logging.INFO)
    logger.addHandler(ch1)

    if log_file is not None:
        pardir = os.path.split(log_file)[0]
        f = open(log_file, "w")
        f.close()
        if not os.path.exists(pardir):
            os.makedirs(pardir)
        ch2 = logging.FileHandler(log_file)
        ch2.setFormatter(logging.Formatter(LOG_FORMAT))
        ch2.setLevel(logging.DEBUG)
        logger.addHandler(ch2)
    logger.setLevel(logging.INFO)
    return logger


def init_directories(mode, u):
    # Create a results dir if it doesn't exist yet
    if not os.path.exists(DumpDir):
        makedirs(DumpDir)

    # Define output directory
    timestamp = time.strftime('%m%d_%H%M%S')
    if args.u:
        output_dir = join(DumpDir, 'u' + mode + '_' + timestamp)
    else:
        output_dir = join(DumpDir, mode + '_' + timestamp)
    makedirs(output_dir)

    return output_dir


def parse_arguments():
    parser = argparse.ArgumentParser(description='Crawl Alexa top websites and capture the traffic')

    parser.add_argument('-start',
                        type=int,
                        metavar='<start ind>',
                        default=0,
                        help='Start from which site in the list (include this ind).')
    parser.add_argument('-end',
                        type=int,
                        metavar='<end ind>',
                        default=50,
                        help='End to which site in the list (exclude this ind).')
    parser.add_argument('-b',
                        type=int,
                        metavar='<Num of batches>',
                        default=5,
                        help='Crawl batches, Tor restarts at each batch.')
    parser.add_argument('-m',
                        type=int,
                        metavar='<Num of instances in each batch>',
                        default=5,
                        help='Number of instances for each website in each batch to crawl. In unmon mode, for every m instances, restart tor.')
    parser.add_argument('-mode',
                        type=str,
                        required=True,
                        metavar='<parse mode>',
                        help='The type of dataset: clean, burst?.')
    parser.add_argument('-device',
                        type=str,
                        default='eth0',
                        help='Network device name.')
    parser.add_argument('-s',
                        action='store_true',
                        default=False,
                        help='Take a screenshot? (default:False)')
    parser.add_argument('-u',
                        action='store_true',
                        default=False,
                        help='is monitored webpage or unmonitored? (default:is monitored, false)')
    parser.add_argument('-p',
                        action='store_false',
                        default=True,
                        help='Parse file after crawl? (default:true)')
    parser.add_argument('-torrc',
                        type=str,
                        default=None,
                        help='Torrc file path.')
    parser.add_argument('-c',
                        action='store_true',
                        default=False,
                        help='Whether use dumpcap to capture network traffic? (default: is false)')
    parser.add_argument('-w',
                        type=str,
                        default=None,
                        help='Self provided web list.')
    parser.add_argument('-l',
                        type=str,
                        default=None,
                        help='Crawl specific unmon sites, given a list')
    parser.add_argument('-log',
                        type=str,
                        metavar='<log path>',
                        default=None,
                        help='path to the log file. It will print to stdout by default.')

    # Parse arguments
    args = parser.parse_args()
    return args


def get_driver():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.socks", "127.0.0.1")
    profile.set_preference("network.proxy.socks_port", 9050)
    profile.set_preference("network.proxy.socks_version", 5)
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("network.http.use-cache", False)
    profile.update_preferences()
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox(firefox_profile=profile, options=opts)
    driver.set_page_load_timeout(SOFT_VISIT_TIMEOUT)
    return driver


def crawl_without_cap(url, filename, guards, s, device):
    if not os.path.exists(golang_communication_path):
        raise FileNotFoundError("The golang communication file {} is not existed.".format(golang_communication_path))

    try:
        with ut.timeout(HARD_VISIT_TIMEOUT):
            driver = get_driver()
            src = ' or '.join(guards)
            start = time.time()
            with open(golang_communication_path,'w') as f:
                f.write('StartRecord\n')
                f.write('{}.cell\n'.format(filename))
                # proxy side directory is different
                basedir, file = os.path.split(filename)
                proxy_filename = join(basedir.rstrip('/')+'_proxy', file)
                f.write('{}.cell'.format(proxy_filename))
                logger.info("Start capturing.")
            time.sleep(0.5)
            driver.get(url)
            time.sleep(0.5)
            if s:
                driver.get_screenshot_as_file(filename + '.png')
    except (ut.HardTimeoutException, TimeoutException):
        logger.warning("{} got timeout".format(url))
    except Exception as exc:
        logger.warning("Unknow error:{}".format(exc))
    finally:
        # Log loading time
        if 'driver' in locals():
            # avoid exception happens before driver is declared and assigned
            # which triggers exception here
            driver.quit()
        if 'start' in locals():
            # avoid exception happens before start is declared and assigned
            # which triggers exception here
            t = time.time() - start
            logger.info("Load {:.2f}s".format(t))
        with open(golang_communication_path, 'w') as f:
            f.write('StopRecord')
            logger.info("Stop capturing.")
        time.sleep(GAP_BETWEEN_SITES)
        logger.info("Sleep {}s and capture killed, capture {:.2f} MB.".format(GAP_BETWEEN_SITES,
                                                                              os.path.getsize(filename + ".cell") / (
                                                                                          1024 * 1024)))


def crawl(url, filename, guards, s, device):
    try:
        with ut.timeout(HARD_VISIT_TIMEOUT):
            driver = get_driver()
            src = ' or '.join(guards)
            # start tcpdump
            # cmd = "tcpdump host \(" + src + "\) and tcp -i eth0 -w " + filename+'.pcap'
            pcap_filter = "tcp and (host " + src + ") and not tcp port 22 and not tcp port 20 "
            cmd = 'dumpcap -P -a duration:{} -a filesize:{} -i {} -s 0 -f \'{}\' -w {}' \
                .format(HARD_VISIT_TIMEOUT, MAXDUMPSIZE, device,
                        pcap_filter, filename + '.pcap')
            logger.info(cmd)
            pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            tcpdump_timeout = TCPDUMP_START_TIMEOUT  # in seconds
            while tcpdump_timeout > 0 and not ut.is_tcpdump_running(pro):
                time.sleep(0.1)
                tcpdump_timeout -= 0.1
            if tcpdump_timeout < 0:
                raise ut.TcpdumpTimeoutError()
            logger.info("Launch dumpcap in {:.2f}s".format(TCPDUMP_START_TIMEOUT - tcpdump_timeout))
            start = time.time()
            driver.get(url)
            time.sleep(1)
            if s:
                driver.get_screenshot_as_file(filename + '.png')
    except (ut.HardTimeoutException, TimeoutException):
        logger.warning("{} got timeout".format(url))
    except ut.TcpdumpTimeoutError:
        logger.warning("Fail to launch dumpcap")
    except Exception as exc:
        logger.warning("Unknow error:{}".format(exc))
    finally:
        # post visit
        # Log loading time
        if 'driver' in locals():
            # avoid exception happens before driver is declared and assigned
            # which triggers exception here
            driver.quit()
        if 'start' in locals():
            # avoid exception happens before start is declared and assigned
            # which triggers exception here
            t = time.time() - start
            logger.info("Load {:.2f}s".format(t))
            # with open(filename + '.time', 'w') as f:
            #     f.write("{:.4f}".format(t))
        time.sleep(GAP_BETWEEN_SITES)
        ut.kill_all_children(pro.pid)
        pro.kill()
        # subprocess.call("killall dumpcap", shell=True)
        logger.info("Sleep {}s and capture killed, capture {:.2f} MB.".format(GAP_BETWEEN_SITES,
                                                                              os.path.getsize(filename + ".pcap") / (
                                                                                          1024 * 1024)))

        # filter ACKs and retransmission
        if os.path.exists(filename + '.pcap'):
            cmd = 'tshark -r ' + filename + '.pcap' + ' -Y "not(tcp.analysis.retransmission or tcp.len == 0 )" -w ' + filename + ".pcap.filtered"
            subprocess.call(cmd, shell=True)
            # remove raw pcapfile
            cmd = 'rm ' + filename + '.pcap'
            subprocess.call(cmd, shell=True)
        else:
            logger.warning("{} not captured for site {}".format(filename + '.pcap', url))


def main(args):
    global batch_dump_dir
    start, end, m, s, b = args.start, args.end, args.m, args.s, args.b
    assert end > start
    torrc_path = args.torrc
    device = args.device
    u = args.u
    l = args.l

    if u:
        WebListDir = unmon_list
    else:
        WebListDir = mon_list
    if args.w:
        WebListDir = args.w
    with open(WebListDir, 'r') as f:
        wlist = f.readlines()[start:end]
    websites = []
    for w in wlist:
        if "https" not in w:
            websites.append("https://www." + w.rstrip("\n"))
        else:
            websites.append(w.rstrip("\n"))
    if u and l:
        l_inds = ut.pick_specific_webs(l)
    if l:
        assert len(l_inds) > 0
    batch_dump_dir = init_directories(args.mode, args.u)
    controller = TorController(torrc_path=torrc_path)
    if u:
        # crawl unmonitored webpages, restart Tor every m pages
        b = math.ceil((end - start) / m)
        for bb in range(b):
            with controller.launch():
                logger.info("Start Tor and sleep {}s".format(GAP_AFTER_LAUNCH))
                time.sleep(GAP_AFTER_LAUNCH)
                guards = controller.get_guard_ip()
                # print(guards)
                for mm in range(m):
                    i = bb * m + mm
                    if i >= len(websites):
                        break
                    website = websites[i]
                    wid = i + start
                    if l:
                        if wid not in l_inds:
                            continue
                    filename = join(batch_dump_dir, str(wid))
                    logger.info("{:d}: {}".format(wid, website))
                    # begin to crawl
                    if args.c:
                        crawl(website, filename, guards, s, device)
                    else:
                        crawl_without_cap(website, filename, guards, s, device)
                logger.info("Finish batch #{}, sleep {}s.".format(bb, GAP_BETWEEN_BATCHES))
                time.sleep(GAP_BETWEEN_BATCHES)
    else:
        # crawl monitored webpages, round-robin fashion, restart Tor every m visits of a whole list
        for bb in range(b):
            with controller.launch():
                logger.info("Start Tor and sleep {}s".format(GAP_AFTER_LAUNCH))
                time.sleep(GAP_AFTER_LAUNCH)
                guards = controller.get_guard_ip()
                # print(guards)
                for wid, website in enumerate(websites):
                    wid = wid + start
                    for mm in range(m):
                        i = bb * m + mm
                        filename = join(batch_dump_dir, str(wid) + '-' + str(i))
                        logger.info("{:d}-{:d}: {}".format(wid, i, website))
                        # begin to crawl
                        if args.c:
                            crawl(website, filename, guards, s, device)
                        else:
                            crawl_without_cap(website, filename, guards, s, device)
                logger.info("Finish batch #{}, sleep {}s.".format(bb, GAP_BETWEEN_BATCHES))
                time.sleep(GAP_BETWEEN_BATCHES)



def sendmail(msg):
    cmd = "python3 " + SendMailPyDir + " -m " + msg
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    global batch_dump_dir
    try:
        args = parse_arguments()
        logger = config_logger(args.log)
        logger.info(args)
        main(args)
        msg = "'Crawler Message:Crawl done at {}!'".format(datetime.datetime.now())
        sendmail(msg)
    except KeyboardInterrupt:
        sys.exit(-1)
    except Exception as e:
        msg = "'Crawler Message: An error occurred:\n{}'".format(e)
        sendmail(msg)
    finally:
        subprocess.call("sudo killall tor",shell=True)
        logger.info("Tor killed!")
        if args.p and args.c:
            # parse raw traffic
            logger.info("Parsing the traffic...")
            if args.u:
                suffix = " -u"
            else:
                suffix = ""
            if args.mode == 'clean':
                # use sanity check
                cmd = "python3 parser.py " + batch_dump_dir + " -s -mode clean -proc_num 1" + suffix
                subprocess.call(cmd, shell=True)

            elif args.mode == 'burst':
                cmd = "python3 parser.py " + batch_dump_dir + " -mode burst -proc_num 1" + suffix
                subprocess.call(cmd, shell=True)
            else:
                pass
