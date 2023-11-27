def check_operation(id, details):
    authorized = False
#     print(f"[debug] checking policies for event {id}, details: {details}")
#     print(f"[info] checking policies for event {id},"\
#           f" {details['source']}->{details['deliver_to']}: {details['operation']}")
    src = details['source']
    dst = details['deliver_to']
    operation = details['operation']
    
    if src == 'drone_com_val' and dst == 'drone_diagnostic' \
        and operation == 'get_battery':
        authorized = True
    if src == 'drone_com_val' and dst == 'drone_diagnostic' \
        and operation == 'engines_status':
        authorized = True
    if src == 'drone_com_val' and dst == 'drone_diagnostic' \
        and operation == 'flight_controller_status':
        authorized = True
    
    if src == 'drone_battery_control' and dst == 'drone_diagnostic' \
        and operation == 'get_battery':
        authorized = True    
        
    if src == 'drone_com_val' and dst == 'drone_aut_ver' \
        and operation == 'check_authentication':
        authorized = True
    if src == 'drone_com_val' and dst == 'drone_navigation_handler' \
        and operation == 'get_coordinate':
        authorized = True   
    if src == 'drone_com_val' and dst == 'drone_nav_ver' \
        and operation == 'check_navigation':
        authorized = True     

    if src == 'drone_navigation_handler' and dst == 'drone_com_val' \
        and operation == 'coordinate':
        authorized = True  
    if src == 'drone_navigation_handler' and dst == 'drone_gps' \
        and operation == 'get_gps_coordinate':
        authorized = True  
    if src == 'drone_navigation_handler' and dst == 'drone_ins' \
        and operation == 'get_ins_coordinate':
        authorized = True  
        
    if src == 'drone_aut_ver' and dst == 'drone_com_val' \
        and operation == 'accept_command':
        authorized = True  
    if src == 'drone_aut_ver' and dst == 'drone_crit' \
        and operation == 'cancel_command':
        authorized = True  
        
    if src == 'drone_nav_ver' and dst == 'drone_com_val' \
        and operation == 'accept_coordinate':
        authorized = True  
    if src == 'drone_nav_ver' and dst == 'drone_crit' \
        and operation == 'cancel_command':
        authorized = True  
          
    if src == 'drone_crit' and dst == 'drone_flight_controller' \
        and operation == 'stop':
        authorized = True  
    if src == 'drone_crit' and dst == 'drone_battery_control' \
        and operation == 'off_drives':
        authorized = True  
    if src == 'drone_crit' and dst == 'drone_ccu' \
        and operation == 'critical_situation':
        authorized = True  
        
    if src == 'drone_ccu' and dst == 'drone_flight_controller' \
        and operation == 'stop':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_flight_controller' \
        and operation == 'clear':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_flight_controller' \
        and operation == 'move_to':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'watchdog':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_data_aggregation' \
        and operation == 'camera_on':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_data_aggregation' \
        and operation == 'camera_off':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'log':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_diagnostic' \
        and operation == 'get_status':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'register':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'sign_out':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'send_position':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'data':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_com_val' \
        and operation == 'check_command':
        authorized = True
        
    if src == 'drone_communication_in' and dst == 'drone_ccu' \
        and operation == 'in':
        authorized = True
        
    if src == 'drone_data_aggregation' and dst == 'drone_ccu' \
        and operation == 'data':
        authorized = True
    if src == 'drone_data_aggregation' and dst == 'drone_data_saver' \
        and operation == 'smth':
        authorized = True
    if src == 'drone_data_aggregation' and dst == 'drone_com_val' \
        and operation == 'data':
        authorized = True
        
    if src == 'drone_diagnostic' and dst == 'drone_ccu' \
        and operation == 'diagnostic_status':
        authorized = True
    if src == 'drone_diagnostic' and dst == 'drone_battery_control' \
        and operation == 'get_battery':
        authorized = True
    if src == 'drone_diagnostic' and dst == 'drone_com_val' \
        and operation == 'diagnostic_battery_status':
        authorized = True
        
    if src == 'drone_flight_controller' and dst == 'drone_gps' \
        and operation == 'get_coordinate':
        authorized = True
    if src == 'drone_flight_controller' and dst == 'drone_ins' \
        and operation == 'get_coordinate':
        authorized = True
    if src == 'drone_flight_controller' and dst == 'drone_ccu' \
        and operation == 'reached':
        authorized = True
    if src == 'drone_flight_controller' and dst == 'drone_battery_control' \
        and operation == 'change_battery':
        authorized = True
    if src == 'drone_flight_controller' and dst == 'drone_engines' \
        and operation == 'smth':
        authorized = True
        
    if src == 'drone_gps' and dst == 'drone_navigation_handler' \
        and operation == 'gps_coordinate':
        authorized = True
        
    if src == 'drone_ins' and dst == 'drone_navigation_handler' \
        and operation == 'ins_coordinate':
        authorized = True


    return authorized