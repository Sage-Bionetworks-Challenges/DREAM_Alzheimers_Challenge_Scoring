library(synapseClient)
synapseLogin()

q1f <- synGet("syn2775267", downloadLocation='.')
q2f <- synGet("syn2775268", downloadLocation='.')
q3f <- synGet("syn2775269", downloadLocation='.')

load('q1f.submissions.metadata.RData')
load('q2f.submissions.metadata.RData')
load('q3f.submissions.metadata.RData')

## Do we want to be strict about excluding submissions that
## were accepted when the leaderboards were officially supposed
## to be closed?
filter_on_timestamps = FALSE

for (abr in c("q1f", "q2f", "q3f")) {

    df <- get(paste0(abr,".submissions.metadata"))

    ## curses upon you, stringsAsFactors!
    df$createdOn <- as.character(df$createdOn)
    df$team <- as.character(df$team)
    df$userId <- as.character(df$userId)

    ## remove admin team users
    ## 1421212 = Chris Bare
    ##  377358 = Chris Bare
    ##  273995 = Mette Peters
    df <- df[!df$userId %in% c(273995, 1421212, 377358),]

    ## correct fat-fingered team names
    df$team[df$team=='ATeam with Organizers'] <- 'ATeam of Organizers'
    df$team[df$team=='BIAS'] <- 'UNC-BIAS'
    df$team[df$team=='BAIS'] <- 'UNC-BIAS'
    df$team[grep("guanlab", df$team , ignore.case=T)] <- 'GuanLab_UMich'

    ## filter based on eligible time stamps:
    ## By Saturday 10/18 7am GMT
    ## Between Thursday 10/23 7pm GMT and Friday 10/24 7pm GMT
    ## But, we made an exception for the 'Chipmunks' team...
    if (filter_on_timestamps) {
        eligible <- (df$createdOn < "2014-10-18T07:00:00" |
                     (df$createdOn > "2014-10-23T19:00:00" & df$createdOn < "2014-10-24T19:00:00") |
                     df$team == 'Chipmunks')
        if (nrow(df) > sum(eligible)) {
            print(sprintf("Excluding from %s based on dates:", abr))
            print(df[!eligible, c('id', 'createdOn', 'userId', 'team', 'final_rank')])
        }
        df <- df[eligible,]
    }

    ## select the latest two submissions from each team
    two_latest_submissions <- lapply(unique(df$team), function(team) {
        df_team <- df[ df$team==team, ]
        df_team <- df_team[ order(df_team$createdOn), ]
        df_team[ max(1,nrow(df_team)-1):max(1, nrow(df_team)), ]
    })

    df_latest_two <- do.call(rbind, two_latest_submissions)

    assign(paste0(abr, ".eligible.submissions.metadata"), df_latest_two)
}

