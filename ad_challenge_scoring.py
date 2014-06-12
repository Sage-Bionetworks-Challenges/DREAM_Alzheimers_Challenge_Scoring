##
## This file sits between challenge.py and the R scoring
## code. Communication with R is through the RPy2 package.
############################################################

import rpy2.robjects as robjects


## Evaluation queues
challenge_evaluations = [
    # {
    #     'id':2480744,
    #     'validation_function': 'validate_q1',
    #     'scoring_function': 'score_q1a'
    # }, {
    #     'id':2480746,
    #     'validation_function': 'validate_q1',
    #     'scoring_function': 'score_q1b'
    # }, {
    #     'id':2480748,
    #     'validation_function': 'validate_q2',
    #     'scoring_function': 'score_q2'
    # }, {
    #     'id':2480750,
    #     'validation_function': 'validate_q3',
    #     'scoring_function': 'score_q3'
    # },
    {
        'id':2495614,
        'validation_function': 'validate_q1',
        'scoring_function': 'score_submission'
    }
]


robjects.r('source("validate_and_score.R")')
r_validate_q1 = robjects.r['validate_q1']
r_validate_q2 = robjects.r['validate_q2']
r_validate_q3 = robjects.r['validate_q3']


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

