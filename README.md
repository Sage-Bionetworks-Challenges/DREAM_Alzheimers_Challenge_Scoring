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


## Notes

 * assign submit/participate permissions on the evaluations to the teams
   - evaluations now have permissions for me and admin team
   - the ADNI and AddNeuroMed subchallenges need to allow Team 2223741 to submit
   - the RUSH-data related subchallenge needs to allow Team 2223742 to submit.
 * Leaderboard text (syn2376428/wiki/63024) - AD challenge Synapse documentation
 * Implement leaderboards for Q1, Q2, Q3
 * ROS map imputed genotypes - need to be moved betw folders

Scoring Q 1/2:
 * robustness of ranking over 1000 bootstrap replicates
 * make sure this is compatible with Q3



Q1a: 2480744
Predict progression of MMSE scores using clinical data
Training: ADNI/ test: ROS/MAP  team: 

Q1b: 2480746
Predict progression of MMSE scores using clinical and genetic data
Training: ADNI/ test: ROS/MAP  team: 

Q2:  2480748
Find discordance between cognitive normal and amyloid
Training: ADNI/ test: ROS/MAP  team: 

Q3:  2480750
Predict progression of MMSE scores from imaging
Training: ADNI/ test: AddNeuroMed  team: 



