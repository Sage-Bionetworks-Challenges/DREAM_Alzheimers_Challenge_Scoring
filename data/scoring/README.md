Truth files for scoring
=======================

Truth files are secret and not kept in source control and must be uploaded to the scoring machine separately, possibly with a command such as:

    scp -i [key] data/scoring/* ubuntu@[scoring-machine]:/home/ubuntu/DREAM_Alzheimers_Challenge_Scoring/data/scoring/

They are loaded by the validate_Q[n] and score_Q[n] functions in the R source file _validate_and_score.R_. See lines that contain calls that look like: _get_expected_format("q1.rosmap.csv")_.

See the Synapse project [ADChallenge_WorkingGroup](https://www.synapse.org/#!Synapse:syn2480825).

Test data for leader board phase:
 * q1.rosmap.csv
 * q2.observed.txt
 * q3.observed.csv

Test data for final phase:
 * q1.final.observed.txt
 * q2.final.observed.txt
 * q3.final.observed.txt
