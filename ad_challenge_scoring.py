##
## This file is a layer that sits between challenge.py 
## and the R scoring code. It's purpose is to be an
## adaptor between generic code and scoring code specific
## to a given challenge question.
## Communication with R is through the RPy2 package.
############################################################

import rpy2.robjects as robjects
import synapseclient


## Configure scoring of evaluation queues
##
## These parameters link an evaluation queue to a validation
## function and a scoring function and supply other bits of
## configuration.
##
## The scoring functions defined below (score_q1, score_q2, etc.) insert
## statistics onto the submission status annotations. Later, the 'fields'
## named in config_evaluations are used to compute mean ranking.
config_evaluations = [

    ## Q1
    {
        'id':2480744,
        'score_as_part_of_challenge': True,
        'validation_function': 'validate_q1',
        'validation_expected_format': 'q1.txt',
        'scoring_function': 'score_q1',
        'observed': 'q1.rosmap.csv',
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
        'validation_expected_format': 'q2.txt',
        'scoring_function': 'score_q2',
        'observed': 'q2.observed.txt',
        'fields': ['auc', 'accuracy'],
        'submission_quota': 50
    },

    ## Q3
    {
        'id':2480750,
        'score_as_part_of_challenge': True,
        'validation_function': 'validate_q3',
        'validation_expected_format': 'q3.txt',
        'scoring_function': 'score_q3',
        'observed': 'q3.observed.csv',
        'fields': ['pearson_mmse', 'ccc_mmse'],
        'submission_quota': 50
    },

    ## Q1 final
    {
        'id':2700269,
        'score_as_part_of_challenge': False,
        'validation_function': 'validate_q1',
        'validation_expected_format': 'q1.final.example.txt',
        'scoring_function': 'score_q1',
        'observed': 'q1.final.observed.txt',
        'fields': ['correlation_pearson_clin',
                   'correlation_pearson_clin_gen',
                   'correlation_spearman_clin',
                   'correlation_spearman_clin_gen']
    },

    ## Q2 final
    {
        'id':2700271,
        'score_as_part_of_challenge': False,
        'validation_function': 'validate_q2',
        'validation_expected_format': 'q2.final.example.txt',
        'scoring_function': 'score_q2',
        'observed': 'q2.final.observed.txt',
        'fields': ['auc', 'accuracy']
    },

    ## Q3 final
    {
        'id':2700273,
        'score_as_part_of_challenge': False,
        'validation_function': 'validate_q3',
        'validation_expected_format': 'q3.final.example.txt',
        'scoring_function': 'score_q3',
        'observed': 'q3.final.observed.txt',
        'fields': ['pearson_mmse', 'ccc_mmse']
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
config_evaluations_map = {ev['id']:ev for ev in config_evaluations}

robjects.r('source("validate_and_score.R")')
r_mean_rank = robjects.r['mean_rank']

output_templates = {
    "score_q1":
    "Submission scored.\n\n    Correlations are:\n" \
    "    Pearson, clinical:          {correlation_pearson_clin}\n" \
    "    Pearson, clinical+genetic:  {correlation_pearson_clin_gen}\n" \
    "    Spearman, clinical:         {correlation_spearman_clin}\n" \
    "    Spearman, clinical+genetic: {correlation_spearman_clin_gen}\n",
    "score_q2":
    "Submission scored.\n\n" \
    "    Accuracy = {accuracy}\n" \
    "    AUC = {auc}\n" \
    "    Brier's score = {brier}\n" \
    "    Somer's D = {somer}\n",
    "score_q3":
    "Submission scored.\n\n" \
    "    Pearson correlation = {pearson_mmse}\n" \
    "    Concordance correlation coefficient = {ccc_mmse}\n" \
    "    Diagnosis percent correct = {percent_correct_diagnosis}\n"
}


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


def validate_submission(evaluation, submission, status):
    """
    To be called by challenge.py:validate()
    """
    config = config_evaluations_map[evaluation.id]

    ## get the R function that validates submissions for
    ## this evaluation
    r_validate_submission = robjects.r[config['validation_function']]

    ## call an R function with signature: function(submission_path, expected_filename)
    result = as_dict(r_validate_submission(submission.filePath, config['validation_expected_format']))
    print result
    status.status = "VALIDATED" if result['valid'] else "INVALID"
    return status, result['message']


def score_submission(evaluation, submission, status):
    """
    To be called by challenge.py:score()
    """
    config = config_evaluations_map[evaluation.id]

    ## get the R function that scores submissions for this
    ## evaluation and a matching template for formatting the output
    r_score_submission = robjects.r[config['scoring_function']]
    template = output_templates[config['scoring_function']]

    ## call an R function with signature: function(submission_path, observed_path)
    result = as_dict(r_score_submission(submission.filePath, config['observed']))
    print result
    status.status = "SCORED"

    ## add scoring statistics to submission status annotations
    if 'annotations' in status:
        annotations = synapseclient.annotations.from_submission_status_annotations(status.annotations)
    else:
        annotations = {}
    annotations.update(result)

    status.annotations = synapseclient.annotations.to_submission_status_annotations(annotations, is_private=False)
    return status, (template).format(**annotations)


def mean_rank(data):
    ## convert to an R data frame
    df = robjects.DataFrame({key:robjects.FloatVector(values) for key,values in data.iteritems()})

    ## calculate the mean and final rankings
    r_results = r_mean_rank(df)

    return {name:col for name, col in r_results.items()}


