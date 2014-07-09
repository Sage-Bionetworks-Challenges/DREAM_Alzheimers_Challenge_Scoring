##
## This file is a layer that sits between challenge.py 
## and the R scoring code. It's purpose is to be an
## adaptor between generic code and scoring code specific
## to a given challenge question.
## Communication with R is through the RPy2 package.
############################################################

import rpy2.robjects as robjects
import synapseclient


## Evaluation queues
challenge_evaluations = [
    {
        'id':2480744,
        'validation_function': 'validate_q1',
        'scoring_function': 'score_q1'
    },
    # {
    #     'id':2480746,
    #     'validation_function': 'validate_q1',
    #     'scoring_function': 'score_q1'
    # },
    {
        'id':2480748,
        'validation_function': 'validate_q2',
        'scoring_function': 'score_q2'
    },
    # {
    #     'id':2480750,
    #     'validation_function': 'validate_q3',
    #     'scoring_function': 'score_q3'
    # },
    {
        'id':2495614,
        'validation_function': 'validate_q2',
        'scoring_function': 'score_q2'
    }
]
challenge_evaluations_map = {ev['id']:ev for ev in challenge_evaluations}


robjects.r('source("validate_and_score.R")')
r_validate_q1 = robjects.r['validate_q1']
r_validate_q2 = robjects.r['validate_q2']
r_validate_q3 = robjects.r['validate_q3']
r_score_q1 = robjects.r['score_q1']
r_score_q2 = robjects.r['score_q2']


def as_dict(vector):
    """Convert an RPy2 ListVector to a Python dict"""
    result = {}
    for i, name in enumerate(vector.names):
        if isinstance(vector[i], robjects.ListVector):
            result[name] = as_dict(vector[i])
        elif len(vector[i]) == 1:
            result[name] = vector[i][0]
        else:
            result[name] = vector[i]
    return result


def validate_q1(submission, status):
    result = as_dict(r_validate_q1(submission.filePath))
    print result
    status.status = "VALIDATED" if result['valid'] else "INVALID"
    return status, result['message']


def validate_q2(submission, status):
    result = as_dict(r_validate_q2(submission.filePath))
    print result
    status.status = "VALIDATED" if result['valid'] else "INVALID"
    return status, result['message']


def validate_q3(submission, status):
    result = as_dict(r_validate_q3(submission.filePath))
    print result
    status.status = "VALIDATED" if result['valid'] else "INVALID"
    return status, result['message']


def score_q1(submission, status):
    result = as_dict(r_score_q1(submission.filePath))
    print result
    status.status = "SCORED"

    keys = ['correlation_pearson_clin',
            'correlation_pearson_clin_gen',
            'correlation_spearman_clin',
            'correlation_spearman_clin_gen']
    annotations = {key:result[key] for key in keys}

    status.annotations = synapseclient.annotations.to_submission_status_annotations(annotations, is_private=False)
    return status, ("Submission scored.\n\n    Correlations are:\n" +
        "    pearson, clinical:          {correlation_pearson_clin}\n" +
        "    pearson, clinical+genetic:  {correlation_pearson_clin_gen}\n" +
        "    spearman, clinical:         {correlation_spearman_clin}\n" +
        "    spearman, clinical+genetic: {correlation_spearman_clin_gen}\n").format(**annotations)


def score_q2(submission, status):
    result = as_dict(r_score_q2(submission.filePath))
    print result
    status.status = "SCORED"

    keys = ['brier', 'auc', 'somer', 'accuracy', 'balancedAccuracy', 'logDeviance']
    annotations = {key:result[key] for key in keys}

    status.annotations = synapseclient.annotations.to_submission_status_annotations(annotations, is_private=False)
    return status, ("Submission scored.\n\n" +
        "    Accuracy = {accuracy}\n" +
        "    AUC = {auc}\n" +
        "    Brier's score = {brier}\n" +
        "    Somer's D = {somer}\n" +
        "    Balanced Accuracy = {balancedAccuracy}\n" +
        "    Log Deviance = {logDeviance}\n").format(**annotations)

