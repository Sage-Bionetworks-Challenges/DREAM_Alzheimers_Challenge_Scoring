import synapseclient
import synapseclient.utils as utils
from synapseclient.exceptions import *
from synapseclient import Activity
from synapseclient import Project, Folder, File
from synapseclient import Evaluation, Submission, SubmissionStatus
from synapseclient import Wiki
import argparse
import json
import math
import random
import sys
import time
import traceback
import urllib
import uuid


# how many submissions will be updated in a single batch
BATCH_SIZE = 100

# how many times to we retry batch uploads of submission annotations
BATCH_UPLOAD_RETRY_COUNT = 5


syn = synapseclient.Synapse()


## Evaluation queues
evaluation_q1a = 2480744
evaluation_q1b = 2480746
evaluation_q2  = 2480748
evaluation_q3  = 2480750

evaluation_test = 2495614


## read in email templates
with open("templates/confirmation_email.txt") as f:
    confirmation_template = f.read()

with open("templates/validation_error_email.txt") as f:
    validation_error_template = f.read()



def update_submissions_status_batch(evaluation, statuses):
    for retry in range(BATCH_UPLOAD_RETRY_COUNT):
        try:
            token = None
            offset = 0
            while offset < len(statuses):
                batch = {"statuses"     : statuses[offset:offset+BATCH_SIZE],
                         "isFirstBatch" : (offset==0),
                         "isLastBatch"  : (offset+BATCH_SIZE>=len(statuses)),
                         "batchToken"   : token}
                response = syn.restPUT("/evaluation/%s/statusBatch" % evaluation.id, json.dumps(batch))
                token = response.get('nextUploadToken', None)
                offset += BATCH_SIZE
        except SynapseHTTPError as err:
            # on 412 ConflictingUpdateException we want to retry
            if err.response.status_code == 412:
                sys.stderr.write('%s, retrying...\n' % err.message)
                time.sleep(2)
            else:
                raise


def validate_submission(file_path):    
    try:
        return True, "OK"
    except Exception as ex1:
        sys.stderr.write('Error processing file %s\n' % file_path)
        traceback.print_exc(file=sys.stderr)
        status.status = "INVALID"


def validate(evaluation, **kwargs):
    """
    It may be convenient to validate submissions in one pass before scoring
    them, especially if scoring takes a long time.
    """
    for submission, status in syn.getSubmissionBundles(evaluation, status='RECEIVED'):

        ## refetch the submission so that we get the file path
        ## to be later replaced by a "downloadFiles" flag on getSubmissionBundles
        submission = syn.getSubmission(submission)

        is_valid, validation_message = validate_submission(submission.filePath)
        print validation_message
        if is_valid:
            status.status = "VALIDATED"
        else:
            status.status = "INVALID"

        syn.store(status)

        ## send message AFTER storing status to ensure we don't get repeat messages
        if kwargs.get('send-messages', False):
            profile = syn.getUserProfile(submission.userId)

            msg_params = dict(
                username=profile.get('firstName', profile.get('userName', profile['ownerId'])),
                submission_id=submission.id,
                submission_name=submission.name,
                evaluation_id=evaluation.id,
                evaluation_name=evaluation.name,
                team= submission.submitterAlias if submission.submitterAlias else 'unknown',
                message=validation_message)

            ## fill in the appropriate template
            template = confirmation_template if is_valid else validation_error_template
            message = template.format(**msg_params)

            syn.sendMessage(
                userIds=[submission.userId],
                messageSubject="Submission to %s (%s)" % (evaluation.name, "OK" if is_valid else "INVALID"),
                messageBody=message)


def score_submission(file_path):
    try:
        return random.random()
    except Exception as ex1:
        sys.stderr.write('Error processing file %s\n' % file_path)
        traceback.print_exc(file=sys.stderr)
        status.status = "INVALID"


def score(evaluation):

    sys.stdout.write('scoring: %s %s\n' % (evaluation.id, evaluation.name))
    sys.stdout.flush()

    ## collect statuses here for batch update
    statuses = []

    for submission, status in syn.getSubmissionBundles(evaluation, status='VALIDATED'):

        ## refetch the submission so that we get the file path
        ## to be later replaced by a "downloadFiles" flag on getSubmissionBundles
        submission = syn.getSubmission(submission)

        score = score_submission(submission.filePath)
        status.score = score
        status.annotations = synapseclient.annotations.to_submission_status_annotations(
            dict(bayesian_whatsajigger=random.random(),
                 root_mean_squared_flapdoodle=random.random()))
        status.status = "SCORED"

        ## we could store each status update individually, but in this example
        ## we collect the updated status objects to do a batch update.
        #status = syn.store(status)
        statuses.append(status)

        sys.stdout.write('.')
        sys.stdout.flush()

    sys.stdout.write('\n')

    ## Update statuses in batch. This can be much faster than individual updates,
    ## especially in rank based scoring methods which recalculate scores for all
    ## submissions each time a new submission is received.
    update_submissions_status_batch(evaluation, statuses)


def list_submissions(evaluation, status=None, **kwargs):

    print '\n\nSubmissions for: %s %s' % (evaluation.id, evaluation.name)
    print '-' * 60

    for submission, status in syn.getSubmissionBundles(evaluation, status=status):
        print submission.id, submission.name, submission.submitterAlias, submission.userId, status.status



# list submissions (with a particular status?)
# score an evaluation
# check status of a submission by ID
# reset a submission for rescoring
# update leaderboards

def command_list(args):
    list_submissions(evaluation=syn.getEvaluation(args.evaluation),
                     status=args.status)


def command_validate(args):
    validate(evaluation=syn.getEvaluation(args.evaluation))



def challenge():

    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--user", help="UserName", default=None)
    parser.add_argument("-p", "--password", help="Password", default=None)

    subparsers = parser.add_subparsers(title="subcommand")

    parser_list = subparsers.add_parser('list')
    parser_list.add_argument("evaluation", metavar="EVALUATION-ID", default=None)
    parser_list.add_argument("-s", "--status", default=None)
    parser_list.set_defaults(func=command_list)

    parser_validate = subparsers.add_parser('validate')
    parser_validate.add_argument("evaluation", metavar="EVALUATION-ID", default=None)
    parser_validate.set_defaults(func=command_validate)

    args = parser.parse_args()


    syn.login(email=args.user, password=args.password)

    args.func(args)


if __name__ == '__main__':
    challenge()
