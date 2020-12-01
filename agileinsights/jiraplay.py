from jira import JIRA #pip install JIRA
import pprint
import getpass


#jirauser = raw_input("Jira user name: ")
#jirapwd = getpass.getpass("Jira password:")

jirauser="martin.waller@asos.com"
#jirapwd="NotHacked!"
jirapwd="oG3GNvHGefmboeGRHZLsDCF9"


options = {
        'server': 'https://asosmobile.atlassian.net/'}

jira = JIRA(options,basic_auth=(jirauser,jirapwd))


projects = jira.projects()

pprint.pprint(projects)



pprint.pprint("Android boards:")
boards = jira.boards('project = LAA')

pprint.pprint(boards)

'''
pprint.pprint("IOs biards:")
boards = jira.boards("project = ISAV")

pprint.pprint(boards)


#stuff = jira.issue_types()

#pprint.pprint(stuff)
'''

'''
sprints = jira.sprints(149)

totlen=0;

for sprint in sprints:
    #pprint.pprint(sprint.id)
    jql = "status=DONE AND updated >= -90d AND sprint=" + str(sprint.id)
    block_size=100 #get 100 results at a time - i doubt there will be more than that very often
    block_num=0
    while True:
        start_idx = block_num*block_size
        res = jira.search_issues(jql,start_idx,block_size)
        if len(res) == 0:
            #no more issues to retrieve!
            break
        for r in res:
            if not r.fields.customfield_11700.value=="Hubble":
                pprint.pprint(r.raw['fields'])
        block_num+=1
        totlen+=len(res)

pprint.pprint("Number found by querying sprints")
pprint.pprint(totlen)
'''

'''
totlen=0
block_num=0
block_size=100
while True:
    start_idx = block_num*block_size
    iss = jira.search_issues('(status=DONE OR status=CLOSED) AND (issuetype=Story OR issuetype=Spike OR issuetype=Bug) AND resolutiondate >= "2018-09-24" AND resolutiondate <= "2018-09-30" AND cf[11700]="SWAT Team"',start_idx,block_size)
#    iss = jira.search_issues('status=CLOSED AND (issuetype=Story OR issuetype=Spike OR issuetype=Bug) AND updated >= -90d AND cf[11700]="A Team"',start_idx,block_size)
    if len(iss) == 0:
        break
    #pprint.pprint(iss[1].raw['fields'])
    #pprint.pprint(iss[1].fields.votes.self)
    for issue in iss:
        #pprint.pprint(issue.fields.votes.self)
        pprint.pprint(issue.raw['fields'])
    block_num+=1
    totlen+=len(iss)

pprint.pprint("Number found by direct query filtering on team name")
pprint.pprint(totlen)



#getit = jira.issue("WD-8774")
#pprint.pprint(getit.raw['fields'])
#pprint.pprint(getit.fields.customfield_11700.value)

#pprint.pprint(sprints)

#iss = jira.search_issues("status=Done AND sprint=645 AND updated >= -90d")

#for i in iss:
#    pprint.pprint(i.raw['fields'])
#    pprint.pprint(i.fields.created)
#    pprint.pprint(i.fields.updated)
'''




