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

    ## Q1
    {
        'id':2480744,
        'score_as_part_of_challenge': True,
        'validation_function': 'validate_q1',
        'scoring_function': 'score_q1',
        'fields': ['correlation_pearson_clin',
                   'correlation_pearson_clin_gen',
                   'correlation_spearman_clin',
                   'correlation_spearman_clin_gen'],
        'submission_quota': 100
    },

    ## Q2
    {
        'id':2480748,
        'score_as_part_of_challenge': True,
        'validation_function': 'validate_q2',
        'scoring_function': 'score_q2',
        'fields': ['auc', 'accuracy'],
        'submission_quota': 50
    },

    ## Q3
    {
        'id':2480750,
        'score_as_part_of_challenge': True,
        'validation_function': 'validate_q3',
        'scoring_function': 'score_q3',
        'fields': ['pearson_mmse', 'ccc_mmse'],
        'submission_quota': 50
    },

    ## testing
    {
        'id':2495614,
        'score_as_part_of_challenge': False,
        'validation_function': 'validate_q3',
        'scoring_function': 'score_q3',
        'fields': ['pearson_mmse', 'ccc_mmse']
    },

    ## use old Q1b queue for testing, too
    {
        'id':2480746,
        'score_as_part_of_challenge': False,
        'validation_function': 'validate_q1',
        'scoring_function': 'score_q1',
        'fields': ['correlation_pearson_clin',
           'correlation_pearson_clin_gen',
           'correlation_spearman_clin',
           'correlation_spearman_clin_gen'],
        'submission_quota': 50
    }
]
challenge_evaluations_map = {ev['id']:ev for ev in challenge_evaluations}

robjects.r('source("validate_and_score.R")')
r_validate_q1 = robjects.r['validate_q1']
r_validate_q2 = robjects.r['validate_q2']
r_validate_q3 = robjects.r['validate_q3']
r_score_q1 = robjects.r['score_q1']
r_score_q2 = robjects.r['score_q2']
r_score_q3 = robjects.r['score_q3']
r_mean_rank = robjects.r['mean_rank']


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

    if 'annotations' in status:
        annotations = synapseclient.annotations.from_submission_status_annotations(status.annotations)
    else:
        annotations = {}
    annotations.update(result)

    status.annotations = synapseclient.annotations.to_submission_status_annotations(annotations, is_private=False)
    return status, ("Submission scored.\n\n    Correlations are:\n" +
        "    Pearson, clinical:          {correlation_pearson_clin}\n" +
        "    Pearson, clinical+genetic:  {correlation_pearson_clin_gen}\n" +
        "    Spearman, clinical:         {correlation_spearman_clin}\n" +
        "    Spearman, clinical+genetic: {correlation_spearman_clin_gen}\n").format(**annotations)


def score_q2(submission, status):
    result = as_dict(r_score_q2(submission.filePath))
    print result
    status.status = "SCORED"

    if 'annotations' in status:
        annotations = synapseclient.annotations.from_submission_status_annotations(status.annotations)
    else:
        annotations = {}
    annotations.update(result)

    # keys = ['brier', 'auc', 'somer', 'accuracy']
    # annotations = {key:result[key] for key in keys}

    status.annotations = synapseclient.annotations.to_submission_status_annotations(annotations, is_private=False)
    return status, ("Submission scored.\n\n" +
        "    Accuracy = {accuracy}\n" +
        "    AUC = {auc}\n" +
        "    Brier's score = {brier}\n" +
        "    Somer's D = {somer}\n").format(**annotations)


def score_q3(submission, status):
    result = as_dict(r_score_q3(submission.filePath))
    print result
    status.status = "SCORED"

    if 'annotations' in status:
        annotations = synapseclient.annotations.from_submission_status_annotations(status.annotations)
    else:
        annotations = {}
    annotations.update(result)

    # keys = ['pearson_mmse', 'ccc_mmse', 'percent_correct_diagnosis']
    # annotations = {key:result[key] for key in keys}

    status.annotations = synapseclient.annotations.to_submission_status_annotations(annotations, is_private=False)
    return status, ("Submission scored.\n\n" +
        "    Pearson correlation = {pearson_mmse}\n" +
        "    Concordance correlation coefficient = {ccc_mmse}\n" +
        "    Diagnosis percent correct = {percent_correct_diagnosis}\n").format(**annotations)


def mean_rank(data):
    ## convert to an R data frame
    df = robjects.DataFrame({key:robjects.FloatVector(values) for key,values in data.iteritems()})

    ## calculate the mean and final rankings
    r_results = r_mean_rank(df)

    return {name:col for name, col in r_results.items()}


