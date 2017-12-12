from network_2 import Router, Host
from link_2 import Link, LinkLayer
import threading
from time import sleep
import sys
from copy import deepcopy

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 10 #give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads at the end
    
    #create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    host_3 = Host('H3')
    object_L.append(host_3)
    
    # tables for router a 
    encap_tbl_D = {0: ('11', 3), 1: ('12', 2)}    # table used to encapsulate network packets into MPLS frames {(in interface: (out label, out interface)}
    frwd_tbl_D = {}     # table used to forward MPLS frames {(in label, in interface): (out label, out interface)}
    decap_tbl_D = {('21', 3): 1}    # table used to decapsulate network packets from MPLS frames {(in label, in interface): out interface}
    router_a = Router(name='RA', 
                              intf_capacity_L=[500,500,500,500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_a)

    # tables for router b
    encap_tbl_D = {}    # table used to encapsulate network packets into MPLS frames {in interface: (out label, out interface)}
    frwd_tbl_D = {('12', 0): ('15', 1)}     # table used to forward MPLS frames {(in label, in interface): (out label, out interface)}
    decap_tbl_D = {}    # table used to decapsulate network packets from MPLS frames {(in label, in interface): out interface}
    
    router_b = Router(name='RB', 
                              intf_capacity_L=[500,100],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_b)

    # tables for router c
    encap_tbl_D = {}    # table used to encapsulate network packets into MPLS frames {in interface: (out label, out interface)}
    frwd_tbl_D = {('11', 0): ('18', 1), ('19', 1): ('21', 0)}     # table used to forward MPLS frames {(in label, in interface): (out label, out interface)}
    decap_tbl_D = {}    # table used to decapsulate network packets from MPLS frames {(in label, in interface): out interface}
    
    router_c = Router(name='RC', 
                              intf_capacity_L=[500,100],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_c)
   
    # tables for router d  
    encap_tbl_D = {2: ('19', 1)}    # table used to encapsulate network packets into MPLS frames {in interface: (out label, out interface)}
    frwd_tbl_D = {}     # table used to forward MPLS frames {(in label, in interface): (out label, out interface)}
    decap_tbl_D = {('15', 0): 2, ('18', 1): 2}    # table used to decapsulate network packets from MPLS frames {(in label, in interface): out interface}
    
    router_d = Router(name='RD', 
                              intf_capacity_L=[500,100,500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_d)
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)
    
    #add all the links - need to reflect the connectivity in cost_D tables above
    link_layer.add_link(Link(host_1, 0, router_a, 0))
    link_layer.add_link(Link(host_2, 0, router_a, 1))
    link_layer.add_link(Link(router_a, 2, router_b, 0))
    link_layer.add_link(Link(router_a, 3, router_c, 0))
    link_layer.add_link(Link(router_b, 1, router_d, 0))
    link_layer.add_link(Link(router_c, 1, router_d, 1))
    link_layer.add_link(Link(router_d, 2, host_3, 0))
    
    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run)) 
    
    for t in thread_L:
        t.start()
    
    #create some send events    
    print('\nSending first message from H1. Path should be:\n\n    H1-RA-RC-RD-H3\n')
    host_1.udt_send('h3', 'MESSAGE_1_FROM_H1')
    # give time for message to be received 
    sleep(3)
    print('\nSending second message from H2. Path should be:\n\n    H2-RA-RB-RD-H3\n')
    host_2.udt_send('h3', 'message_2_from_h2')
    sleep(3)
    print('\nSending third message from H3. Path should be:\n\n    H3-RD-RC-RA-H2\n')
    host_3.udt_send('h2', 'message_3_from_h3')
#    for i in range(5):
#        priority = i%2
#        host_1.udt_send('h2', 'message_%d_from_h1' % i, priority)
        
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")
