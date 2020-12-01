import ConfigParser
import pprint
import time
from datetime import datetime, timedelta
from dateutil import rrule #pip install python-dateutil
import getpass
from isoweek import Week

#https://github.com/Microsoft/vsts-python-api/blob/master/README.md
from vsts.vss_connection import VssConnection
from msrest.authentication import BasicAuthentication

import numpy as np #pip install numpy
import matplotlib.pyplot as plt #pip install matplotlib
from matplotlib.backends.backend_pdf import PdfPages
from collections import OrderedDict

#https://skjira.readthedocs.io/en/latest/apidoc.html
from jira import JIRA #pip install JIRA


'''
Setup time related stuff
'''
period = 90 #90 day period

#see https://gist.github.com/dogsbody/8dce2429da2bddae2c31b67e0471b683
def get_holidays(a, b):
    rs = rrule.rruleset()
    # Include all potential holidays
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 1, bymonthday= 1))                     # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 1, bymonthday= 2, byweekday=rrule.MO)) # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 1, bymonthday= 3, byweekday=rrule.MO)) # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, byeaster= -2))                                  # Good Friday
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, byeaster= 1))                                   # Easter Monday
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 5, byweekday=rrule.MO, bysetpos=1))    # May Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 5, byweekday=rrule.MO, bysetpos=-1))   # Spring Bank Holiday
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 8, byweekday=rrule.MO, bysetpos=-1))   # Late Summer Bank Holiday
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=25))                     # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=26, byweekday=rrule.MO)) # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=27, byweekday=rrule.MO)) # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=26))                     # Boxing Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=27, byweekday=rrule.MO)) # Boxing Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=27, byweekday=rrule.TU)) # Boxing Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=28, byweekday=rrule.MO)) # Boxing Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=28, byweekday=rrule.TU)) # Boxing Day
    # Exclude potential holidays that fall on weekends
    rs.exrule(rrule.rrule(rrule.WEEKLY, dtstart=a, until=b, byweekday=(rrule.SA,rrule.SU)))
    return rs

def get_working_days(a, b):
    rs = rrule.rruleset()
    rs.rrule(rrule.rrule(rrule.DAILY, dtstart=a, until=b))                         # Get all days between a and b
    rs.exrule(rrule.rrule(rrule.WEEKLY, dtstart=a, byweekday=(rrule.SA,rrule.SU))) # Exclude weekends
    rs.exrule(get_holidays(a,b))                                                   # Exclude holidays
    return rs

'''
Read config file
'''
Config = ConfigParser.ConfigParser()
Config.read('insights.ini')
#Config.read('reduced.ini')
#Config.read('retail.ini')
#Config.read('web.ini')
#pprint.pprint(Config.sections())

'''helper function'''
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            pprint.pprint("Exception on %s!" % option)
            dict1[option] = None
    return dict1


'''
VSTS connection setup
'''
vstsuser=raw_input("VSTS user name (asos email...):")
token=getpass.getpass("VSTS access token:")
jirauser=raw_input("jira user name:")
jirapwd=getpass.getpass("Jira password:")

credentials = BasicAuthentication(vstsuser,token)

#generic
team_instance='https://asos.visualstudio.com'
connection = VssConnection(base_url=team_instance, creds=credentials)
core_client = connection.get_client('vsts.core.v4_0.core_client.CoreClient')
wi_client = connection.get_client('vsts.work_item_tracking.v4_0.work_item_tracking_client.WorkItemTrackingClient')


joptions = {
        'server':'https://asosmobile.atlassian.net/'}

jiras = JIRA(joptions,basic_auth=(jirauser,jirapwd))


#get start date of week
#see https://stackoverflow.com/questions/5882405/get-date-from-iso-week-number-in-python
startdate = (datetime.today()+timedelta(days=-period)).isocalendar()
weekstart = Week(startdate[0],startdate[1]).monday()
startweek = weekstart.strftime("%Y%m%d")

enddate = datetime.today().isocalendar()
endweek = Week(enddate[0],enddate[1]).monday().strftime("%Y%m%d")

j=0
weeks=[]
weeks.append(startweek)
step=0

while j<endweek:
    i=(datetime.today()+timedelta(days=(-period+step))).isocalendar()
    j=Week(i[0],i[1]).monday().strftime("%Y%m%d")
    #pprint.pprint(j)
    weeks.append(j)
    step+=7

#pprint.pprint(weeks)
    




#pprint.pprint(ConfigSectionMap('Teams').values())

'''Data structures for different rollup levels.
each is a dictionary with team/domain/platform as the key, and a tuple containing another dictionary (key=weeknum, value=throughput for that wek) and 2 lista (leadtimes and cycle times):
    {({},[],[])}
'''

Domains={}
Platforms={}
Teams={}
Totals={}


def setup(team, options):
    #Teams[team]=({}.fromkeys(range(startweek,endweek+1)),[],[])
    Teams[team]=({}.fromkeys(weeks),[],[])
        
    for week in weeks:
        Teams[team][0][week]=0
    
#if entry doesn't already exist for the Domain of this team, add it
    if not options[1] in Domains:
        Domains[options[1]] = ({}.fromkeys(weeks),[],[])
        for week in weeks:
            Domains[options[1]][0][week]=0

#if entry doesn't already exist for the platform of this team, add it
    if not options[2] in Platforms:
        Platforms[options[2]] = ({}.fromkeys(weeks),[],[])
        for week in weeks:
            Platforms[options[2]][0][week]=0
    if not "Totals" in Totals:
        Totals["Totals"]=({}.fromkeys(weeks),[],[])
        for week in weeks:
            Totals["Totals"][0][week]=0

def storeData(created,closed, started, team, options):

        #only do cycle times if data available
        startedstr=""
        started_date=0
        if started != 0:
            startedstr=started.split('T')[0]
            started_date=datetime.strptime(startedstr,'%Y-%m-%d')

        createdstr = created.split('T')[0]
        closedstr = closed.split('T')[0]
        created_date = datetime.strptime(createdstr,'%Y-%m-%d')
        closed_date = datetime.strptime(closedstr,'%Y-%m-%d')
        isocal = datetime.date(closed_date).isocalendar()        
        closedweek=Week(isocal[0],isocal[1]).monday()
        weeknum=closedweek.strftime("%Y%m%d")

        #thruput
        Teams[team][0][weeknum]+=1
        newval = Domains[options[1]][0][weeknum]+1
        domain = options[1]
        #pprint.pprint("updating domain %s for weeknum %s to %d " % (domain, weeknum, newval))  
        Domains[options[1]][0][weeknum]+=1
        Platforms[options[2]][0][weeknum]+=1
        Totals["Totals"][0][weeknum]+=1

        leadtime = len(list(get_working_days(created_date,closed_date)))
        #leadtime
        Teams[team][1].append(leadtime)
        Domains[options[1]][1].append(leadtime)
        Platforms[options[2]][1].append(leadtime)
        Totals["Totals"][1].append(leadtime)

        #cycle time if there
        if started != 0:
            cycletime = len(list(get_working_days(started_date,closed_date)))
            Teams[team][2].append(cycletime)
            Domains[options[1]][2].append(cycletime)
            Platforms[options[2]][2].append(cycletime)
            Totals["Totals"][2].append(cycletime)




def getData(team, options, query_res):

    for item in query_res.work_items:
        witem = wi_client.get_work_item(item.id)
        #pprint.pprint(witem.fields)
        #check if in progress state has been used, and if so store it to
        if "Scrumformigration.REFDATE_InProgress" in witem.fields:#scrumformigration process projects
            startdate=witem.fields["Scrumformigration.REFDATE_InProgress"]
        elif "Microsoft.VSTS.Common.ActivatedDate" in witem.fields:#Team ERM process projects            
            startdate= witem.fields[ "Microsoft.VSTS.Common.ActivatedDate"]
        else:
            startdate=0

        #if team=="Blaze":
        #    pprint.pprint(witem.fields)
        #storeData(witem.fields["System.CreatedDate"],witem.fields["System.ChangedDate"],startdate,team,options)
        if "Microsoft.VSTS.Common.ClosedDate" in witem.fields:
            storeData(witem.fields["System.CreatedDate"],witem.fields["Microsoft.VSTS.Common.ClosedDate"],startdate,team,options)
        elif team=="TitansNew" or team=="BlackOps":#new Titans not using REFDATE_done for PBIS (or MS ClosedDate)
            storeData(witem.fields["System.CreatedDate"],witem.fields["System.ChangedDate"],startdate,team,options)
        else: #BabyShadow. Kermit, PhoenixNew - setup strangely, and bugs use dufferent fields for done date...(???)
            if witem.fields["System.WorkItemType"] =="Bug":
                storeData(witem.fields["System.CreatedDate"],witem.fields["System.ChangedDate"],startdate,team,options)
            else:
                #pprint.pprint(team)
                #pprint.pprint(witem.fields)
                storeData(witem.fields["System.CreatedDate"],witem.fields["DataService.REFDATE_Done"],startdate,team,options)

        
        


def getJiraData(team,options):
    totlen=0
    #query for stories that are done and that were last updated (to done presumably...) in the last 90 days
    #'cf[11700' is custom field that holds the team name (cf[12151] for web since last month)
    jql1 = '(status=Closed OR status=Done) AND issuetype in(Story,Spike,Bug,Task,"Tech Story") AND (resolution not in("Cannot Reproduce", "Won\'t Do","Won\'t Fix", Withdrawn, Duplicate)) AND resolutiondate >= -90d AND '
    
    if options[2]=="Web":
#        jql = jql1 + '(cf[11700]="' + team + '" OR cf[12151]="' + team + '")'
        jql = jql1 + 'cf[12151]="' + team + '"'
    elif options[2]=="Apps":
        appteam = team[:-4]#yuck - hack
        if options[3]=="Android":#Android project
            jql = jql1 + 'project in(LAA) AND cf[11700]="' + appteam + '"'
        else:#iOS project
            jql = jql1 + 'project in(ISAV) AND cf[11700]="' + appteam + '"'
    else:
        jql = jql1 + 'cf[11700]="' + team + '"'
    total_issues=[]

    pprint.pprint("team and jql for team:")
    pprint.pprint(team)
    pprint.pprint(jql)
    #pprint.pprint("options[2]:")
    #pprint.pprint(options[2])

    #query only returns max number of results,  not all of them
    #so loop through until none are left
    block_size=100 #get 100 results at a time - i doubt there will be more than that very often
    block_num=0
    while True:
        start_idx = block_num*block_size
        isses = jiras.search_issues(jql,start_idx,block_size)
        if len(isses) == 0:
            #no more issues to retrieve!
            break;
        block_num+=1
        totlen+=len(isses)
        total_issues.append(isses)

    pprint.pprint(totlen)

    for iss in total_issues:
        for i in iss:
           #pprint.pprint(i)
           #0 in place of in progress date as dunno how to get tehm from jira yet
           storeData(i.fields.created,i.fields.updated,0,team,options)


def plotDomainThruput():
    
    fig = plt.figure()

    ax = plt.subplot(111) 

    plt.grid(axis='y')
    plt.xlabel('Week Number')
    plt.xticks(rotation=90)
    for label in (ax.get_xticklabels()):
        label.set_fontsize(5)
    plt.ylabel=('Thruput (number of stories)')
    for domain in Domains:
        od = OrderedDict(sorted(Domains[domain][0].items()))
        plt.plot(od.keys(), od.values(),label=domain)
    plt.legend()
    plt.title("Domain Throughput")
    #plt.show()
    return fig


def plotTotalsThruput():

    fig = plt.figure()

    ax = plt.subplot(111) 


    plt.grid(axis='y')
    plt.xlabel('Week Number')
    for label in (ax.get_xticklabels()):
        label.set_fontsize(5)
    plt.xticks(rotation=90)
    plt.ylabel=('Thruput (number of stories)')
    od = OrderedDict(sorted(Totals["Totals"][0].items()))
    plt.plot(od.keys(), od.values(),label="Totals")

    #use 15th percentile - "85% of the time team will deliver x stories per week - this is bottom 15% of the weekly thrupits
    text="50th Percentile: %d\n85th percentile: %d" % (int(np.median(od.values())+0.5),int(np.percentile(od.values(),15)+0.5))
    plt.text(0.5,0.5,text, transform = ax.transAxes)

    plt.title("Total Throughput across all teams")
    #plt.show()

    return fig

def plotTotalsCumThruput():

    fig = plt.figure()

    ax = plt.subplot(111)

    plt.grid(axis='y')
    plt.xlabel('Week number')
    plt.xticks(rotation=90)
    for label in (ax.get_xticklabels()):
        label.set_fontsize(5)
    plt.ylabel=('Cumulative thruput (number of stories)')
    od = OrderedDict(sorted(Totals["Totals"][0].items()))
    cumulative = np.cumsum(od.values())

    plt.plot(od.keys(), cumulative,label="Cumulative Totals")

    plt.title("Cumulative Total Throughput across all teams")
    #plt.show()

    return fig

def plotThruputHist(thruput,team):

    pprint.pprint("Thruput hist for team %s" % team)
    
    fig=plt.figure()

    ax = plt.subplot(111)

    d=np.array(thruput.values())
    numbins=d.max()-d.min()
    if numbins==0:
        numbins=1
    n, bins, patches = plt.hist(x=d,bins=numbins)

    plt.grid(axis='Count')
    plt.xlabel("Thruput (stories delivered per week)")

    title = team + ' weekly thruput histogram'
    plt.title(title)

    maxfreq=n.max()

    plt.ylim(ymax=np.ceil(maxfreq/10)*10 if maxfreq % 10 else maxfreq + 10)

    text="50th percentile: %d\n85th percentile: %d" % (int(np.median(d)+0.5),int(np.percentile(d,85)+0.5))

    plt.text(0.5,0.5,text, transform = ax.transAxes)

    return fig


def plotLeadTimeHist(leadtimes,team):

    pprint.pprint("Leadtime for team %s" % team)
       
    fig = plt.figure()

    ax = plt.subplot(111)

    d=np.array(leadtimes)
    numbins = d.max() - d.min()
    if numbins==0:
        numbins=1
    n, bins, patches = plt.hist(x=d,bins=numbins)#color='#0504aa'

    plt.grid(axis='y')
    plt.xlabel('Leadtime (days)')
    
    title = team + ' Leadtime Histogram'
    plt.title(title)

    maxfreq = n.max()
    plt.ylim(ymax=np.ceil(maxfreq/10)*10 if maxfreq % 10 else maxfreq + 10)

    text="50th percentile: %d\n85th percentile: %d" % (int(np.median(d)+0.5),int(np.percentile(d,85)+0.5))

    plt.text(0.5,0.5,text, transform = ax.transAxes)
    #plt.show()
    return fig

def plotCycleTimeHist(cycletimes,team):

    pprint.pprint("Cycletime for team %s" % team)
   
    fig = plt.figure()

    ax = plt.subplot(111)

    d=np.array(cycletimes)
    numbins = d.max() - d.min()
    if numbins==0:
        numbins=1
    n, bins, patches = plt.hist(x=d,bins=numbins)#color='#0504aa'

    plt.grid(axis='y')
    plt.xlabel('Cycletime (days)')
    
    title = team + ' Cycletime Histogram'
    plt.title(title)

    maxfreq = n.max()
    plt.ylim(ymax=np.ceil(maxfreq/10)*10 if maxfreq % 10 else maxfreq + 10)

    text="50th percentile: %d\n85th percentile: %d" % (int(np.median(d)+0.5),int(np.percentile(d,85)+0.5))

    plt.text(0.5,0.5,text, transform = ax.transAxes)
    #plt.show()
    return fig


def plotThruput(thruput,team):

    pprint.pprint("Throughput for team %s" % team)

    fname=team + "_thruputs.txt"

    f = open(fname,"w")
    
    fig = plt.figure()

    ax = plt.subplot(111) 

    plt.grid(axis='y')
    plt.xlabel('Week Number')
    for label in (ax.get_xticklabels()):
        label.set_fontsize(5)
    plt.xticks(rotation=90)
    plt.ylabel('Throughput (number of stories)')
    od = OrderedDict(sorted(thruput.items()))

    title = team + ' Weekly Throughput (last 90 days)'
    plt.title(title)

    #use 15th percentile - "85% of the time team will deliver x stories per week - this is bottom 15% of the weekly thrupits
    text="50th percentile: %d\n85th percentile: %d" % (int(np.median(od.values())+0.5),int(np.percentile(od.values(),15)+0.5))

    plt.text(0.5,0.5,text, transform = ax.transAxes)

    for k,v in od.items():
        out = str(k) + "," + str(v) + "\n"
        f.write(out)
    f.close()
   

    plt.plot(od.keys(), od.values(),label=team)

    

    #plt.legend()
    #plt.show()

    return fig


for team in ConfigSectionMap('Teams').values():
    pprint.pprint(team + ':')
    options = []
    try:        
        settings = Config.options(team)
        for setting in settings:
            val = Config.get(team,setting)
            options.append(val)
        pprint.pprint(options)
#        if options[0] != "VSTS":
#            pprint.pprint("Only VSTS supported at present - skipping")
#            continue

        if options[3] == "Unknown":
            pprint.pprint("No backlog location for team %s - skipping" % team)
            continue

        setup(team,options)
        if options[0] == "VSTS":
            query_res=wi_client.query_by_id(options[3])        
            pprint.pprint(len(query_res.work_items))
            getData(team,options,query_res)
        else:
            getJiraData(team,options)
            #pprint.pprint("Skipping - Jira API access broken")
    except:
        pprint.pprint("Unexpected error:")
        raise


#plotTeamThruput()
#plotPlatformThruput()
#plotDomainThruput()
#plotTotalsThruput()

pp1 = PdfPages('teamleadtimes.pdf')
pp2 = PdfPages('teamthruputs.pdf')
pp3 = PdfPages('teamthruputhist.pdf')
pp4 = PdfPages('teamcycletimes.pdf')

'''Graphical output got teams (leadtime hist and thruput plot)
'''
for team in Teams:
    if len(Teams[team][1]) > 0:#in the cas eof no thruout, then can't plot a histogram of leadtimes!
        plot1 = plotLeadTimeHist(Teams[team][1],team)
        pp1.savefig(plot1)
        plot2 = plotThruput(Teams[team][0],team)
        pp2.savefig(plot2)
        plot3 = plotThruputHist(Teams[team][0],team)
        pp3.savefig(plot3)
        if len(Teams[team][2]) > 0: #if no cycletimes, can't plot them...
            plot4 = plotCycleTimeHist(Teams[team][2],team)
            pp4.savefig(plot4)
#        saveTeamThruputs(Teams[team][0],team)
    else:
        pprint.pprint("Skipping throught put and leadtime hist for team %s as they have 0 thruput!" % team)

pp1.close()
pp2.close()
pp3.close()
pp4.close()

pp1 = PdfPages('platformleadtimes.pdf')
pp2 = PdfPages('platformthruputs.pdf')
pp3 = PdfPages('platformcycletimes.pdf')

for platform in Platforms:
    if len(Platforms[platform][1]) > 0:#in the cas eof no thruout, then can't plot a histogram of leadtimes!
        plot1 = plotLeadTimeHist(Platforms[platform][1],platform)
        pp1.savefig(plot1)
        plot2 = plotThruput(Platforms[platform][0],platform)
        pp2.savefig(plot2)
        if len(Platforms[platform][2]) > 0: #can't plot cycletimes if no data
            plot3 = plotCycleTimeHist(Platforms[platform][2],platform)
            pp3.savefig(plot3)

    else:
        pprint.pprint("Skipping throught put and leadtime hist for platform %s as they have 0 thruput!" % platform)


pp1.close()
pp2.close()
pp3.close()


pp1 = PdfPages('domainleadtimes.pdf')
pp2 = PdfPages('domaintrhuputs.pdf')
pp3 = PdfPages('domaincycletimes.pdf')

for domain in Domains:
    if len(Domains[domain][1]) > 0:#in the cas eof no thruout, then can't plot a histgran of leadtimes!
        plot1= plotLeadTimeHist(Domains[domain][1],domain)
        pp1.savefig(plot1)
        plot2 = plotThruput(Domains[domain][0],domain)
        pp2.savefig(plot2)
        if len(Domains[domain][2]) > 0: #can't plot cycletimes if there are none
            plot3 = plotCycleTimeHist(Domains[domain][2],domain)
            pp3.savefig(plot3)
    else:
        pprint.pprint("Skipping throught put and leadtime hist for domain %s as they have 0 thruput!" % domain)



pp1.close()
pp2.close()
pp3.close()

pp1 = PdfPages('domainrollupthruputs.pdf')
plot1 = plotDomainThruput()
pp1.savefig(plot1)
plot2= plotTotalsThruput()
pp1.savefig(plot2)
plot3 = plotTotalsCumThruput()
pp1.savefig(plot3)

pp1.close()

pp1 = PdfPages("TotalLeadtimes.pdf")
plot1 = plotLeadTimeHist(Totals["Totals"][1],"Total")
pp1.savefig(plot1)

pp1.close()

if len(Totals["Totals"][2]) > 0:
    pp1 = PdfPages("TotalCycletimes.pdf")
    plot1 = plotCycleTimeHist(Totals["Totals"][2],"Total")
    pp1.savefig(plot1)
    pp1.close()








