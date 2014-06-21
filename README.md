AD_Challenge_Scoring
====================

Scoring code for the [Alzheimer's challenge](https://www.synapse.org/#!Synapse:syn2290704).


## Running the scoring script

The entry point to the scoring code is a Python script named _challenge.py_. It has several subcommands including _list_, _validate_, _score_, _status_, _reset_ and _score-challenge_. To get help, type:

    python challenge.py -h


### Synapse login

The script needs a Synapse login. The easiest way to do this is establish a cached API key by typing:

    synapse login -u [USER_NAME] -p [PASSWORD] --rememberMe

Alternatively, the script will look for the environment variables SYNAPSE_USER and SYNAPSE_PASSWORD:

    export SYNAPSE_USER=user_name
    export SYNAPSE_PASSWORD=super\ secret\ dont\ tell\ nobody

The script also accepts login information as parameters.

### Subcommands

**score-challenge**: Validate and score submissions to all evaluations in a challenge. Evaluations in
                     the challenge are configured in the code. See _ad_challenge_scoring.py_:

    challenge_evaluations = [
        {
            'id':2480744,
            'validation_function': 'validate_q1',
            'scoring_function': 'score_q1'
        },
        {
            'id':2480746,
            'validation_function': 'validate_q1',
            'scoring_function': 'score_q1'
        },
        {
            'id':2480748,
            'validation_function': 'validate_q2',
            'scoring_function': 'score_q2'
        }
    ]


**validate**

**score**

**list**

**status**

**reset**


## TO DO

* validate --evaluation [evaluation] and validate --submission [submission]
* score --evaluation [evaluation] and validate --submission [submission]
* reset more than one submission at a time? Likewise for all submission or evaluation parameters?

