import glob
import os
import synapseclient
import uuid
from synapseclient import Project, File, Folder, Evaluation
from challenge import *
import challenge

syn = synapseclient.Synapse()
syn.login()

## module scope variable to hold project
project = None
evaluation = None

challenge.robjects.r('DATA_DIR <- "test_data"')

try:
    challenge.syn = syn

    project = syn.store(Project("Alzheimers scoring test project" + unicode(uuid.uuid4())))
    evaluation = syn.store(Evaluation(name=unicode(uuid.uuid4()), description="for testing", contentSource=project.id))

    for filename in glob.iglob("test_data/q2.0*"):
        entity = syn.store(File(filename, parent=project))
        submission = syn.submit(evaluation, entity, name=filename, teamName="Mean Squared Error Blues")

    list_submissions(evaluation)

    validate(evaluation, validation_func=challenge.validate_q2)
    score(evaluation)

finally:
    if evaluation:
        syn.delete(evaluation)
    if project:
        syn.delete(project)

