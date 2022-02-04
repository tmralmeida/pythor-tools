
def get_roles_mapping(experiment : int, run : int) -> dict:
    if experiment == 1:
        if run == 1:
            N_GROUPS = 2
            VISITORS_GROUP1 = [6,7,5] 
            VISITORS_GROUP2 = [8,2,4]
        elif run == 2:
            N_GROUPS = 2
            VISITORS_GROUP1 = [2,6,7,5] 
            VISITORS_GROUP2 = [8, 4]
        elif run == 3:
            N_GROUPS = 3
            VISITORS_GROUP1 = [6,7,8]
            VISITORS_GROUP2 = [4,5]
            VISITORS_GROUP3 = [2]
        elif run == 4:
            N_GROUPS = 2
            VISITORS_GROUP1 = [2, 4, 5, 7, 8]
            VISITORS_GROUP2 = [6]
        
        WORKERS_UTILITY = [3]
        WOKERS_LAB = [9]

    if experiment == 2:
        if run == 1:
            N_GROUPS = 2
            VISITORS_GROUP1 = [4,5,6] 
            VISITORS_GROUP2 = [3,7,9]
        elif run == 2:
            N_GROUPS = 2
            VISITORS_GROUP1 = [3,5,6,9] 
            VISITORS_GROUP2 = [7, 4]
        elif run == 3:
            N_GROUPS = 3
            VISITORS_GROUP1 = [5,7,9]
            VISITORS_GROUP2 = [4,6]
            VISITORS_GROUP3 = [3]
        elif run == 4:
            N_GROUPS = 2
            VISITORS_GROUP1 = [3,5,6,7,9]
            VISITORS_GROUP2 = [4]
        elif run == 5:
            N_GROUPS = 3
            VISITORS_GROUP1 = [3, 6]
            VISITORS_GROUP2 = [4, 9]
            VISITORS_GROUP3 = [5, 7]
        
        WORKERS_UTILITY = [2]
        WOKERS_LAB = [8]
        
    if experiment == 3:
        if run == 1:
            N_GROUPS = 2
            VISITORS_GROUP1 = [2,3,8] 
            VISITORS_GROUP2 = [6,7,9]
        elif run == 2:
            N_GROUPS = 2
            VISITORS_GROUP1 = [2,8,9] 
            VISITORS_GROUP2 = [3,6,7]
        elif run == 3:
            N_GROUPS = 3
            VISITORS_GROUP1 = [2,3,7]
            VISITORS_GROUP2 = [8,9]
            VISITORS_GROUP3 = [6]
        elif run == 4:
            N_GROUPS = 2
            VISITORS_GROUP1 = [2,3,6,7,9]
            VISITORS_GROUP2 = [8]
        
        WORKERS_UTILITY = [5]
        WOKERS_LAB = [4]
        
    INSPECTOR = [10]

    ROLES = {
        "VISITOR" : VISITORS_GROUP1 + VISITORS_GROUP2 if N_GROUPS == 2 else VISITORS_GROUP1 + VISITORS_GROUP2 + VISITORS_GROUP3,
        "WORKER" : WOKERS_LAB + WORKERS_UTILITY,
        "INSPECTOR" : INSPECTOR,
    }
    return ROLES