## Process test data files to create submission templates
## and scoring
## 
## This is scratch code to preserve the steps I took to
## create the files used by the scoring code in
## validate_and_score.R  -chris
############################################################

ROSMAP.MMSE <- read.csv('data/answers/ROSMAP.MMSE.csv', stringsAsFactors=FALSE)
id.tr <- data.frame(id=ROSMAP.MMSE$id, projid=as.integer(gsub("(MAP|ROS)0*", "", ROSMAP.MMSE$id)), stringsAsFactors=F)

lb <- read.csv('/Users/chris/.synapseCache/191/582191/ADChallenge_ROSMAP_Q1_Leaderboard.csv', stringsAsFactors=F)
lb$id <- id.tr$id[match(lb$projid, id.tr$projid)]
lb <- lb[lb$fu_year==0,c(9,3,4,5,6,7,8)]

ROSMAP.MMSE$Subject = as.integer(gsub("(ROS|MAP0*)","",ROSMAP.MMSE$id))
rosmap <- ROSMAP.MMSE[,c(ncol(ROSMAP.MMSE),1:8)]



discordance <- read.csv('/Users/chris/Documents/work/projects/alzheimers_challenge/data/answers/ROSMAP.discordance.csv')
discordance$Subject = as.integer(gsub("(ROS|MAP0*)","",discordance$id))

q1 <- rosmap[,c('Subject','MMSEbl')]
colnames(q1) <- c('Subject', 'MMSE_24')
write.table(q1, file='q1.txt', quote=F, sep='\t', row.names=F, col.names=T)

q2 <- data.frame(Subject=discordance$Subject, Rank=NA, Confidence=runif(length(discordance$Subject),0,1), Discordance=NA)
q2$Rank <- rank(1-q2$Confidence)
q2$Discordance <- ifelse(q2$Confidence > 0.5, 1, 0)
write.table(q2, file='q2.txt', quote=F, sep='\t', row.names=F, col.names=T)

## flip these bastard labels!
q2_observed <- read.table('data/scoring/q2.observed.txt', header=T, stringsAsFactors=F)
q2_observed$actual_discordance_string <- ifelse(q2_observed$actual_discordance == 1, 'discordant', 'concordant')








library(synapseClient)
synapseLogin('chris.bare')

ad_working_group_project_id <- 'syn2343636'
folder <- 'syn2773668'
eids <- c(2480744, 2480748, 2480750, 2700269, 2700271, 2700273)

