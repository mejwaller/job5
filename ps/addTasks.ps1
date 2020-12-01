 

# Usually changes for each Sprint - both specific to your environment
[string] $areaPath = "Backlog\GUCCI"
[string] $iterationPath = "Backlog\GUCCI"
 
# Usually changes for each CR
[string] $changeRequestName = Read-Host -Prompt 'Input UserStory Number'
[string] $assignee = "Charlie Salmon"
 
# Values represent units of work, often 'man-hours'
[decimal[]] $taskEstimateArray = @(0,0,0,0,0)
# Remaining Time is usually set to Estimated time at start (optional use of this array)
[decimal[]] $taskRemainingArray = @(0,0,0,0,0)
# Completed Time is usually set to zero at start (optional use of this array)
[decimal[]] $tasktaskCompletedArray = @(0,0,0,0,0,0)
 
# Usually remains constant
# TFS Server address - specific to your environment
[string] $tfsServerString = "http://tfs:8080/tfs/asos/"
 
# Work Item Type - specific to your environment
[string] $workItemType = "Backlog\Task"
 
[string[]] $taskNameArray = @("ALL: BA Sign Off/ Demo", "ALL: Code Review","ALL: Check DoD" ,"QA: Test Plan")
 
# Loop and create of eack of the Tasks in prioritized order
[int] $i = 0
 
Write-Host `n`r**** Script started...`n`r
 
while ($i -le 3) {
    # Concatenate name of task with CR name for Title and Description fields
    $taskDesc = $taskNameArray[$i] + ": " + $changeRequestName
 
    # Build string of field parameters (key/value pairs)
    [string] $fields = "Title=$($taskDesc);Description=$($taskDesc);Assigned To=$($assignee);"
    $fields += "Area Path=$($areaPath);Iteration Path=$($iterationPath);Priority=$($i+1);"
    $fields += "Estimate=$($taskEstimateArray[$i]);Remaining Work=$($taskRemainingArray[$i]);Completed Work=$($tasktaskCompletedArray[$i])"
 
    #For debugging - optional console output
    #Write-Host $fields
 
    # Create the Task (Work Item)
    tfpt workitem /new $workItemType /collection:$tfsServerString /fields:$fields
 
    $i++
 }
 
 Write-Host `n`r**** Script completed...