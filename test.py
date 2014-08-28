import glob
import os
import synapseclient
import uuid
from synapseclient import Project, File, Folder, Evaluation
from challenge import *
import challenge
from collections import OrderedDict

syn = synapseclient.Synapse()
syn.login()

CLEANUP = False

## module scope variable to hold project
project = None
evaluation = None

## point the scoring code at the test files rather than real challenge assets
challenge.robjects.r('DATA_DIR <- "test_data"')

WIKI_TEMPLATE = """\

## Q1
${{supertable?path=%2Fevaluation%2Fsubmission%2Fquery%3Fquery%3Dselect+%2A+from+evaluation_{q1_evaluation_id}+where+status+%3D%3D+%22SCORED%22&paging=true&queryTableResults=true&showIfLoggedInOnly=false&pageSize=25&showRowNumber=false&jsonResultsKeyName=rows&columnConfig0=none%2CID%2CobjectId%3B%2CNONE&columnConfig1=none%2Cname%2Cname%3B%2CNONE&columnConfig2=synapseid%2Centity%2CentityId%3B%2CNONE&columnConfig3=none%2Cteam%2CsubmitterAlias%3B%2CNONE&columnConfig4=none%2CPearson-clin%2Ccorrelation_pearson_clin%3B%2CNONE%2C4&columnConfig5=none%2CPearson-clin-gen%2Ccorrelation_pearson_clin_gen%3B%2CNONE%2C4&columnConfig6=none%2CSpearman-clin%2Ccorrelation_spearman_clin%3B%2CNONE%2C4&columnConfig7=none%2CSpearman-clin-gen%2Ccorrelation_spearman_clin_gen%3B%2CNONE%2C4&columnConfig8=none%2CMean Rank%2Cmean_rank%3B%2CNONE%2C2&columnConfig9=none%2CFinal Rank%2Cfinal_rank%3B%2CNONE%2C2}}

## Q2
${{supertable?path=%2Fevaluation%2Fsubmission%2Fquery%3Fquery%3Dselect+%2A+from+evaluation_{q2_evaluation_id}+where+status+%3D%3D+%22SCORED%22&paging=true&queryTableResults=true&showIfLoggedInOnly=false&pageSize=25&showRowNumber=false&jsonResultsKeyName=rows&columnConfig0=none%2CID%2CobjectId%3B%2CNONE&columnConfig1=none%2Cname%2Cname%3B%2CNONE&columnConfig2=synapseid%2Centity%2CentityId%3B%2CNONE&columnConfig3=none%2Cteam%2CsubmitterAlias%3B%2CNONE&columnConfig4=none%2CAUC%2Cauc%3B%2CNONE%2C4&columnConfig5=none%2CAccuracy%2Caccuracy%3B%2CNONE%2C4}}

## Q3
${{supertable?path=%2Fevaluation%2Fsubmission%2Fquery%3Fquery%3Dselect+%2A+from+evaluation_{q3_evaluation_id}+where+status+%3D%3D+%22SCORED%22&paging=true&queryTableResults=true&showIfLoggedInOnly=false&pageSize=25&showRowNumber=false&jsonResultsKeyName=rows&columnConfig0=none%2CID%2CobjectId%3B%2CNONE&columnConfig1=none%2Cname%2Cname%3B%2CNONE&columnConfig2=synapseid%2Centity%2CentityId%3B%2CNONE&columnConfig3=none%2Cteam%2CsubmitterAlias%3B%2CNONE&columnConfig4=none%2CPercent Correct%2Cpercent_correct_diagnosis%3B%2CNONE%2C4&columnConfig5=none%2CPearson MMSE%2Cpearson_mmse%3B%2CNONE%2C4&columnConfig6=none%2CCCC MMSE%2Cccc_mmse%3B%2CNONE%2C4}}

"""

try:
    challenge.syn = syn

    project = syn.store(Project("Alzheimers scoring test project" + unicode(uuid.uuid4())))
    print "Project:", project.id, project.name

    print "\n\nQ1 --------------------"
    q1_evaluation = syn.store(Evaluation(name=unicode(uuid.uuid4()), description="for testing Q1", contentSource=project.id))
    print "Evaluation, Q1:", q1_evaluation.id

    for filename in glob.iglob("test_data/q1.0*"):
        entity = syn.store(File(filename, parent=project))
        submission = syn.submit(q1_evaluation, entity, name=filename, teamName="Mean Squared Error Blues")

    ## submit one again that will be over quota, since we
    ## already have 1 good submission
    entity = syn.store(File("test_data/q1.0001.txt", parent=project))
    submission = syn.submit(q1_evaluation, entity, teamName="Mean Squared Error Blues")

    list_submissions(q1_evaluation)

    validate(q1_evaluation, validation_func=challenge.validate_q1, submission_quota=1)
    score(q1_evaluation, scoring_func=challenge.score_q1)
    rank(q1_evaluation, fields=['correlation_pearson_clin',
                             'correlation_pearson_clin_gen',
                             'correlation_spearman_clin',
                             'correlation_spearman_clin_gen'])

    print "\n\nQ2 --------------------"
    q2_evaluation = syn.store(Evaluation(name=unicode(uuid.uuid4()), description="for testing Q2", contentSource=project.id))
    print "Evaluation, Q2:", q2_evaluation.id

    for filename in glob.iglob("test_data/q2.0*"):
        entity = syn.store(File(filename, parent=project))
        submission = syn.submit(q2_evaluation, entity, name=filename, teamName="Mean Squared Error Blues")

    list_submissions(q2_evaluation)

    validate(q2_evaluation, validation_func=challenge.validate_q2)
    score(q2_evaluation, scoring_func=challenge.score_q2)
    rank(q2_evaluation, fields=['auc', 'accuracy'])

    print "\n\nQ3 --------------------"
    q3_evaluation = syn.store(Evaluation(name=unicode(uuid.uuid4()), description="for testing Q3", contentSource=project.id))
    print "Evaluation, Q3:", q3_evaluation.id

    for filename in glob.iglob("test_data/q3.0*"):
        entity = syn.store(File(filename, parent=project))
        submission = syn.submit(q3_evaluation, entity, name=filename, teamName="Mean Squared Error Blues")

    list_submissions(q3_evaluation)

    validate(q3_evaluation, validation_func=challenge.validate_q3)
    score(q3_evaluation, scoring_func=challenge.score_q3)
    rank(q3_evaluation, fields=['pearson_mmse', 'ccc_mmse'])

    wiki = Wiki(title="Leaderboards",
                owner=project,
                markdown=WIKI_TEMPLATE.format(
                    q1_evaluation_id=q1_evaluation.id,
                    q2_evaluation_id=q2_evaluation.id,
                    q3_evaluation_id=q3_evaluation.id))
    wiki = syn.store(wiki)

finally:
    if CLEANUP:
        if evaluation:
            syn.delete(evaluation)
        if project:
            syn.delete(project)
    else:
        print "don't clean up"

