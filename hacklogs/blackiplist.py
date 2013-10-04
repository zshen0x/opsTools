#! /usr/bin/env python

import re, sys
from operator import itemgetter

def ip2int(ip):
    return reduce(lambda x,y:(x<<8)+y,map(int,ip.split('.')))


def is_in_network(ip, network):
    """decide weather ip in the network"""
    network = network.split('/')
    ip_int = ip2int(ip)
    network_ip_int = ip2int(network[0])
    mask_len = int(network[1])
    mask_int = (2**mask_len - 1) << (32 - mask_len)
    #print mask_int
    if ip_int & mask_int == network_ip_int:
        return True
    else:
        return False


def analyse_log(log_path):
    """analyse log counts the most aggressive ip"""
    ip_dict = {}
    hack_log = open(log_path)
    try:
        for each_line in hack_log:
            match_info = re.match(r'\d+\.\d+\.\d+\.\d+', each_line)
            if match_info:
                ip = match_info.group()
                if ip_dict.has_key(ip):
                    ip_dict[ip] += 1
                else:
                    ip_dict[ip] = 1
        #ip_list = sorted(ip_dict.iteritems(), key=itemgetter(1), reverse=True)
        return ip_dict
    except Exception, e:
        print traceback.print_exc()
        #print 'analyse_log %s error' % log_path
        return {}
    finally:
        hack_log.close()


def existed_ips(blacklist_path):
    """already existed in blackips"""
    ip_set = set()
    blacklist_file = open(blacklist_path)
    try:
        for line in blacklist_file:
            ip_set.add(line.strip('\n'))
        return ip_set
    except Exception, e:
        print 'blackiplist %s error' % blacklist_path
        return ip_set
    finally:
        blacklist_file.close()


def blackiplist_generator(log_path_list, blacklist_path):
    """generate blackiplist"""
    existed_ip_set = existed_ips(blacklist_path)
    ip_dicts = []
    for log_path in log_path_list:
        ip_dicts.append(analyse_log(log_path))
    
    #combine ip_dicts generated by each log
    daily_ip_dict = {}
    for each_ip_dict in ip_dicts:
        for ip in iter(each_ip_dict):
            if daily_ip_dict.has_key(ip):
                daily_ip_dict[ip] += each_ip_dict[ip]
            else:
                daily_ip_dict[ip] = each_ip_dict[ip]

    # filter the daily_ip_dict
    # daily attack counts < 100
    # ip inside campus
    networks = ['115.200.0.0/16', '172.16.0.0/12',
             '10.0.0.0/8', '210.32.200.0/21', 
             '192.168.0.0/16', '221.12.171.64/26', 
             '183.246.0.0/16', '115.236.0.0/16'
            ]
    for ip in daily_ip_dict.keys():
        if daily_ip_dict[ip] > 50:
            for network in networks:
                if not is_in_network(ip, network):
                    continue
                else:
                    daily_ip_dict.pop(ip)
                    break
        else:
            daily_ip_dict.pop(ip)

    daily_ip_list = daily_ip_dict.iteritems()
    ip_set = set([ip_tuple[0] for ip_tuple in daily_ip_list])
    ip_set = ip_set - existed_ips(blacklist_path)
    ip_list = list(ip_set)
    with open(blacklist_path, 'a') as blacklist:
        for ip in ip_list:
            blacklist.write(ip + '\n')


if __name__ == '__main__':
    log_path_list = ['down.zjut.com_sec.log', 'www.zjut.com_sec.log']
    blacklist_path = 'blackip'
    blackiplist_generator(log_path_list, blacklist_path)
