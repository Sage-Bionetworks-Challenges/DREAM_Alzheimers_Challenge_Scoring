# scoring.r

# draft of scoring functions for AD challenge
# david fardo - created 5/15/2014 - last updated: 5/19/2014



# Question 1 - Predict MMSE at 24 months ----------------------------------

# input question for CHRIS: how will these be formatted ?  the functions are easy --
#  the only issue is ensuring proper matching by ID

Q1_score = function (q1.submission, rosmap.q1.test.data) {
  # q1.submission should be a data.frame with ROSMAP ID and MMSE at 24 month predictions
  # rosmap.q1.test.data is a data.frame for testing with ROSMAP ID (rosmap.id) and actual MMSE at 24 month (mmse.24)

  # check data submission
  if (!is.data.frame (q1.submission)) {
    q1.submission <- as.data.frame (q1.submission)
  }
  names (q1.submission) <- c("rosmap.id", "mmse.24.prediction")
  if (any (dim (rosmap.q1.test.data) != dim (q1.submission))) stop ("Data format is invalid: dimensions do not match")
  if (any (is.na(q1.submission))) stop ("Data format is invalid: all subjects must be predicted")
  if (!identical (sort (unique (as.character (q1.submission$rosmap.id))), 
                  sort (unique (as.character (rosmap.q1.test.data$rosmap.id))))) stop ("IDs do not match")
  
  # combine data
  combined.df <- merge (q1.submission.test, rosmap.q1.test.data)
  
  # calculate correlation
  q1.corr <- with (combined.df, cor(mmse.24.prediction, mmse.24))
  if (is.na (q1.corr)) stop ("Undiscovered matching error: recode")
  
  list(correlation=q1.corr)
}


# testing

# q1.submission.test = data.frame (ID=c("1423", "HI", "hasdf", "4"), MMSE=c(23.3,21.7,30,28))
# q1.matrix = as.matrix (q1.submission.test)
# names (q1.submission.test) <- c("rosmap.id", "mmse.24.prediction")
# rosmap = data.frame (rosmap.id=c("1423", "HI", " 4", "hasdf"), mmse.24=c(23,25,24,29))
# rosmap2 = data.frame (rosmap.id=c("1423", "HI", "4", "hasdf"), mmse.24=c(23,25,24,29))
# 
# Q1_score (q1.submission.test, rosmap)
# Q1_score (q1.submission.test, rosmap2)



Q2_score = function (q2.submission, rosmap.q2.test.data) {
  # q2.submission should be a data.frame with ROSMAP ID and discordance probability predictions
  # rosmap.q2.test.data is a data.frame for testing with ROSMAP ID (rosmap.id) and discordance indicator (disc.ind)
  
  require (pROC)
  
  # check data submission
  if (!is.data.frame (q2.submission)) {
    q2.submission <- as.data.frame (q2.submission)
  }
  names (q2.submission) <- c("rosmap.id", "disc.ind.prediction")
  if (any (dim (rosmap.q2.test.data) != dim (q2.submission))) stop ("Data format is invalid: dimensions do not match")
  if (any (is.na(q2.submission))) stop ("Data format is invalid: all subjects must be predicted")
  if (!identical (sort (unique (as.character (q2.submission$rosmap.id))), 
                  sort (unique (as.character (rosmap.q2.test.data$rosmap.id))))) stop ("IDs do not match")
  
  # combine data
  combined.df <- merge (q2.submission, rosmap.q2.test.data)
  
  
  # calculate metrics
  # Brier's score
  q2.brier <- with (combined.df, mean ((disc.ind.prediction - disc.ind)^2))
  if (is.na (q2.brier)) stop ("Undiscovered matching error: recode")
  # AUC and CI
  q2.auc <- with (combined.df, as.numeric (roc(disc.ind ~ disc.ind.prediction)$auc))#, ci = TRUE))
  if (is.na (q2.auc)) stop ("Undiscovered matching error: recode")
  ## Somer's D
  q2.s <- 2*(q2.auc - 0.5)
  
  list(brier=q2.brier, auc=q2.auc, somer=q2.s)
}


# testing

# q2.submission.test = data.frame (ID=c("1423", "HI", "hasdf", "4"), preds1=c(.54,.2,.92,.8))
# q2.matrix = as.matrix (q2.submission.test)
# names (q2.submission.test) <- c("rosmap.id", "prediction")
# rosmap = data.frame (rosmap.id=c("1423", "HI", " 4", "hasdf"), disc.ind=c(0,0,0,1))
# rosmap2 = data.frame (rosmap.id=c("1423", "HI", "4", "hasdf"), disc.ind=c(0,0,1,0))
# 
# Q2_score (q2.submission.test, rosmap)
# Q2_score (q2.submission.test, rosmap2)
