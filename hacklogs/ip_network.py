#import socket, struct

#def ip2Int(ip):
#    return struct.unpack("!I",socket.inet_aton(ip))[0]
#def int2Ip(i):
#    return socket.inet_ntoa(struct.pack("!I",i))

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
        

if __name__ == '__main__':
    print is_in_network('192.168.1.34', '192.168.2.0/24')
    
    
