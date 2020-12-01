#so $tfs object available outside function I think
$global:tfs
$global:sprint
$global:devworked = 0;
$global:qaworked = 0;
$global:uiworked = 0;

add-pssnapin Microsoft.TeamFoundation.PowerShell

#see http://blogs.msdn.com/b/yao/archive/2011/06/15/tfs-integration-pack-and-scripting-using-powershell.aspx
[System.Reflection.Assembly]::LoadWithPartialName("Microsoft.TeamFoundation.Client")
[System.Reflection.Assembly]::LoadWithPartialName("Microsoft.TeamFoundation.WorkItemTracking.Client")

$hostname = "http://tfs.kingsway.asos.com:8080/tfs/ASOS/"

function TFS-Connect {
	$username = (read-host -prompt "User name for $hostname")
	#$raw = (read-host -prompt "Password for $hostname")
	$password = (read-host -assecurestring -prompt "Password for $hostname")
	#$password = ConvertTo-SecureString $raw -AsPlainText -Force
	$global:sprint = (read-host -prompt "Sprint name:")
	$credential =  New-Object System.Management.Automation.PSCredential ($username, $password)
	$global:tfs = get-tfsserver -name $hostName -credential $credential
	return $global:tfs
}

TFS-Connect

#get the work store:
$global:ws = $global:tfs.getservice([type]"Microsoft.TeamFoundation.WorkItemTracking.Client.WorkItemStore")

#get the backlog
$global:backlog = $global:ws.projects | where {$_.name -eq "Backlog" } 

#get query for "Sprint 20" (have to create in tfs first - could build up tho):
$global:query20 = $global:backlog.storedqueries | where {$_.name -eq $sprint}

$global:querytext = "SELECT [System.Id],[System.WorkItemType],[System.Title],[System.AssignedTo],[System.State],[System.Tags] FROM WorkItems
WHERE [System.TeamProject] = 'Backlog' AND [System.IterationPath] = 'Backlog\Bag and Checkout\juggernaut\" + $global:sprint + "' AND [System.WorkItemType] = 'User Story'"

#get the query text and updatye to replace @project with 'Backlog':
#$global:querytext = $global:query20.querytext.replace("@project","'Backlog'")
#SELECT [System.Id],[System.WorkItemType],[System.Title],[System.AssignedTo],[System.State],[System.Tags] FROM WorkItem
# WHERE [System.TeamProject] = 'Backlog' AND [System.IterationPath] = 'Backlog\Juggernaut\Sprint 20' AND [System.State]

#User stories:
#SELECT [System.Id],[System.WorkItemType],[System.Title],[System.AssignedTo],[System.State],[System.Tags] FROM WorkItems
# WHERE [System.TeamProject] = 'Backlog' AND [System.IterationPath] = 'Backlog\Juggernaut\Sprint 20' AND [System.WorkIte
#mType] = 'User Story'

#get the list 


#run the query:
$global:results = $global:ws.query($querytext)

#this gives us a list of user stories - to get the tasks from each story, get the links from each
#e.g.
#$global:tasks = $results[2].links
#gets all links related to the 3rd story in the list of stories
#a link that has a BaseType of 'RelatedLink' will be an associated task (or maybe something different?)
#you can then get the id:
#$global:link0id = $results[2].links[0].RelatedWorkItemId

#and from *that* get the workitem:
#$global:wi=$global:ws.getworkitem($global:link0id)

#fields contains all the fields - we want fields named 'Original Estimate', 'Completed Work' 
#also need to check iteration path - maybe a task carried over from a different sprint.
#$wi.fields["iteration path"].value is of form "Backlog\Juggernaut\Sprint nn"
#so $wi.fields["iteration path"].value.split("\")[2] will be "Sprint nn" and we have to check it equals $sprint
 
#get an individual iteration root:
#this has all the sprint in it - we are nearly where we want to be?
#$global:jugs = $global:backlog.IterationRootNodes | where {$_.name -eq "Juggernaut" }

$global:outfile = "results.txt"

#write out sprint name
$sprint | out-file $global:outfile 


#write each story ID an title
$global:results | foreach {

	#user story tasks will be the story links that of basetype "RelatedLink"
	$tasks = $_.links | where {$_.BaseType -eq "Relatedlink"}
	$totest = 0;
	$totworked =0;

	$tasks | foreach {
		$wi = $global:ws.getworkitem($_.RelatedWorkItemId)
		#make sure the tasks are ones from this sprint (story may have straddled sprints), not test cases and not removed items
		if($wi.fields["Iteration Path"].value.split("\")[3] -eq $sprint -And $wi.Type.name -ne "Test Case" -And $wi.state -ne "Removed") {
			$totest += $wi.fields["Original Estimate"].value
			$totworked += $wi.fields["Completed Work"].value
			if($wi.title.StartsWith("DEV:")) {
				$global:devworked += $wi.fields["Completed Work"].value 
			}
			elseif($wi.title.StartsWith("QA:")) {
				$global:qaworked += $wi.fields["Completed Work"].value 
			}
			elseif($wi.title.StartsWith("UI:")) {
				$global:uiworked += $wi.fields["Completed Work"].value 
			}
		}
	}

	$userstorytext = $_.title + "		" + [String]$totest + "	" + [String]$totworked
	$userstorytext | out-file $global:outfile -append		
		
	#todo - should be able to create collection of strings so above loopand this one can be done in tandem
	#efficiency not important currently...
	$tasks | foreach {
		$wi = $global:ws.getworkitem($_.RelatedWorkItemId)
		if($wi.fields["Iteration Path"].value.split("\")[3] -eq $sprint -And $wi.Type.name -ne "Test Case" -And $wi.state -ne "Removed" -And $wi.fields["Original Estimate"].value -gt 0) {
			$tasktext = "	" + $wi.title + "	" + [String]$wi.fields["Original Estimate"].value + "	" +
				[String]$wi.fields["Completed Work"].value
			$tasktext | out-file $global:outfile -append
		}
	}
}

$captext = "devcapused:	" + [String]$global:devworked + "	qacapused:	" + [String]$global:qaworked + "	uicapused	" + [String]$global:uiworked
$captext | out-file $global:outfile -append
 

#get sprints
#$global:sprints=$global:jugs.ChildNodes

#get specific sprint
#$global:twenty = $global:sprints | where { $_.name -eq $sprint }

#get an indivdual item from the work item store
#$wi=$ws.getworkitem(269898)

 

