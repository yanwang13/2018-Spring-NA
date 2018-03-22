import sys
from datetime import datetime
from prettytable import PrettyTable

filename = sys.argv[1]

reverse = False
sort_by_user = False
after = False
before = False
Nth_time = 0
T_time = 0
#after_dt = datetime.now()
#before_dt = datetime.now()

i = 1
while i < len(sys.argv):
    #print(sys.argv[i])
    if sys.argv[i] in ('-h', '--help'):
        print("usage: nahw1-2_0416246.py [-h] [-u] [-after AFTER] [-before BEFORE] [-n N] [-t T] [-r] filename\n")
        print("Auth log parser.\n")
        print("positional arguments:\n  filename\tLog file path.\n")
        print("optinal arguments:")
        print("  -h, --help    show this help message and exit")
        print("-u              Summary failed login and sort log by user")
        print("-after AFTER    Filter log after date. format YYYY-MM-DD-HH:MM:SS")
        print("-before BEFORE  Filter log before date. format YYYY-MM-DD-HH:MM:SS")
        print("-n N            Show only the user of most N-th times")
        print("-t T            Show only the user of attacking equal or more than T times")
        print("-r              Sort in reverse order")
        sys.exit(0)
    elif sys.argv[i] == '-u':
        sort_by_user = True
    elif sys.argv[i] == '-after':
        i = i+1
        after_dt = datetime.strptime(sys.argv[i],'%Y-%m-%d-%H:%M:%S')
        after = True        
    elif sys.argv[i] == '-before':
        i = i+1
        before_dt = datetime.strptime(sys.argv[i],'%Y-%m-%d-%H:%M:%S')
        before = True        
    elif sys.argv[i] == '-n':
        i = i+1
        Nth_time = int(sys.argv[i])
    elif sys.argv[i] == '-t':
        i = i+1
        T_time = int(sys.argv[i])
    elif sys.argv[i] == '-r':
        reverse = True
    i = i+1


#print("sort_by_user: ", sort_by_user)
#print("reverse: ", reverse)
#print("Nth_time: ", Nth_time)
#if after:
#    print("AFTER: ", after_dt)
#if before:
#    print("BEFORE: ", before_dt)

#print("T_time: ", T_time)
#print("filename: ", filename)

dic = {}

def extract_user(ss):
    split_str = ss.split(" ")
    #for ele in split_str:
        #print(ele)
    i = 0
    while i != len(split_str):
        if (split_str[i]=="Invalid" or split_str[i]=="invalid") and split_str[i+1]=="user":
            break
        else:
            i=i+1
    if i!=len(split_str):
        return split_str[i+2]
    else:
        return None

def update_dic(user, dic):
    if user not in dic:
        dic[user] = 1
    else:
        dic[user] = dic[user] +1

with open(filename, "r") as log_file:
    for line in log_file:
        #find if there is invalid user
        dt = datetime.strptime(line[:15] , "%b %d %H:%M:%S")#extract the date time
        dt = dt.replace(year=2018)
        #print(dt)
        user = extract_user(line[15:])
        if user==None:
            continue
            
        if after==True and before==False and dt >= after_dt:
            update_dic(user, dic)
        elif before==True  and after==False and dt <= before_dt:
            update_dic(user, dic)
        elif after==True and before==True and dt >= after_dt and dt <= before_dt:
            update_dic(user, dic)
        elif after==False and before==False:
            update_dic(user, dic)

user_list = []

for key, value in dic.items():
    #temp = [key, value]
    #user_list.append(temp)
    if T_time > 0 and value >= T_time:
        user_list.append([key, value])
    elif T_time == 0:
        user_list.append([key, value])

table = PrettyTable(['user', 'count'])#set the original table
sortkey = 'count'
table.reversesort = True

for x in user_list:
    table.add_row([x[0], int(x[1])])

if Nth_time >0: #deal with Nth_time
    table = table[0:Nth_time]

if sort_by_user:
    sortkey = 'user'
    table.reversesort = False
if reverse:
    if table.reversesort == True:
        table.reversesort = False
    else:
        table.reversesort = True
#print(sortkey)
#print(table.reversesort)
print(table.get_string(sortby=sortkey))