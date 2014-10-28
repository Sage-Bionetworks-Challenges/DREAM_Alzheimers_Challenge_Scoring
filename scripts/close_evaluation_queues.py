
participants_teamid = 2223741 ## for all challenge participants 2223741
approved_teamid = 2223742 ## Alzheimers Challenge 1 Approved Participants


## close the evaluation queues
eids = [2480750, 2700273]
for eid in eids:
    evaluation = syn.getEvaluation(eid)
    acl1 = syn.setPermissions(evaluation, principalId=participants_teamid, accessType=['PARTICIPATE'], overwrite=True)
    acl2 = syn.setPermissions(evaluation, principalId=approved_teamid, accessType=['PARTICIPATE'], overwrite=True)
    print evaluation, acl1, acl2

eids = [2480744, 2480748, 2700269, 2700271]
for eid in eids:
    evaluation = syn.getEvaluation(eid)
    acl1 = syn.setPermissions(evaluation, principalId=participants_teamid, accessType=['PARTICIPATE'], overwrite=True)
    acl2 = syn.setPermissions(evaluation, principalId=approved_teamid, accessType=['PARTICIPATE'], overwrite=True)
    print evaluation, acl1, acl2



## reopen the evaluation queues
eids = [2480750, 2700273] ## Q3
teamid = 2223741 ## for all challenge participants 2223741
for eid in eids:
    evaluation = syn.getEvaluation(eid)
    acl = syn.setPermissions(evaluation, principalId=teamid, accessType=['PARTICIPATE', 'SUBMIT'], overwrite=True)
    print evaluation, acl

eids = [2480744, 2480748, 2700269, 2700271] ## Q1, Q2
teamid = 2223742 ## Alzheimers Challenge 1 Approved Participants
for eid in eids:
    evaluation = syn.getEvaluation(eid)
    acl = syn.setPermissions(evaluation, principalId=teamid, accessType=['PARTICIPATE', 'SUBMIT'], overwrite=True)
    print evaluation, acl


## check status of evaluation queues
eids = [2480750, 2700273, 2480744, 2480748, 2700269, 2700271]
## 2223741: for all challenge participants
## 2223742: Alzheimers Challenge 1 Approved Participants
for eid in eids:
    evaluation = syn.getEvaluation(eid)
    acl1 = syn.getPermissions(evaluation, principalId=2223741)
    acl2 = syn.getPermissions(evaluation, principalId=2223742)
    print evaluation, acl1, acl2

