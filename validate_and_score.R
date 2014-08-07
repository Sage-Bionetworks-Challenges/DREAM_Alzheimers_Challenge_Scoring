##
##  Validate and score AD Challenge submissions
############################################################
suppressMessages(require(pROC))
suppressMessages(require(synapseClient))


DATA_DIR = "data/scoring"

## cache the answers so we don't keep reading them
EXPECTED_FORMAT_FILES = list()

## read either a csv or tab delimited file and return a data frame
read_delim_or_csv <- function(filename) {
    if (grepl('.csv$', filename)) {
        read.csv(filename, stringsAsFactors=FALSE)
    } else {
        read.table(filename, header=TRUE, quote="\"", fill=TRUE, stringsAsFactors=FALSE)
    }
}

## get the test data from cache or read from disk
get_expected_format <- function(filename) {
    if (!(filename %in% names(EXPECTED_FORMAT_FILES))) {
        expected <- read_delim_or_csv(file.path(DATA_DIR, filename))
        EXPECTED_FORMAT_FILES[[filename]] <- expected
    }
    return(EXPECTED_FORMAT_FILES[[filename]])
}



## parameters:
##   expected: a data.frame with the expected dimensions and column identifiers
##         df: the data.frame to be validated
##
## returns a list of two elements:
##      valid: TRUE / FALSE
##    message: a string
validate_data_frame <- function(expected, df) {
    if (any (is.na(df))) stop ("Data format is invalid: all subjects must be predicted")

    ## Either exceptions or returning a list works, not
    ## sure which is better, yet.

    if (!all(colnames(expected)==colnames(df))) {
        stop(sprintf(
            "Column names of submission were (%s) but should be (%s).",
            paste(colnames(df), collapse=", "),
            paste(colnames(expected), collapse=", ")))
    }

    if (!all(dim(expected)==dim(df))) {
        stop(sprintf(
            "Dimensions of submission (%s) are not as expected (%s).",
            paste(dim(df), collapse=', '),
            paste(dim(expected), collapse=', ')))
    }

    return(list(valid=TRUE, message="OK"))
}

validate_projids <- function(expected, df) {
    if (!setequal(df$projid, expected$projid)) {
        return(list(
            valid=FALSE,
            message=sprintf("The projid column contained unrecognized identifiers: \"%s\". The expected identifiers look like these: \"%s\".",
                paste(head(setdiff(df$projid, expected$projid)), collapse=", "),
                paste(head(expected$projid), collapse=", "))))
    }

    return(list(valid=TRUE, message="OK"))
}


validate_q1 <- function(filename) {
    df = read_delim_or_csv(filename)
    expected = get_expected_format("q1.txt")
    result = validate_data_frame(expected, df)
    if (!result$valid) {
        return(result)
    }

    result = validate_projids(expected, df)
    if (!result$valid) {
        return(result)
    }

    ## check for zero variance predictions
    result$valid = var(df$delta_MMSE_clin) > 0 && var(df$delta_MMSE_clin_gen) > 0
    if (!result$valid) {
        result$message = paste(
            "Your prediction has zero variance, which means your submission can't be scored.",
            "Submissions are scored by correlation with the observed values for change in MMSE, but correlation is",
            "undefined when either of the correlates has zero variance.")
    }

    return(result)
}

validate_q2 <- function(filename) {
    df = read_delim_or_csv(filename)
    expected = get_expected_format("q2.txt")
    result = validate_data_frame(expected, df)

    if (!result$valid) {
        return(result)
    }

    result = validate_projids(expected, df)

    if (!result$valid) {
        return(result)
    }

    ## check that the Discordance column is either Concordant or Discordant
    allowed_values = c('concordant', 'discordant')
    lower_cased_discordance = tolower(df$Discordance)
    result$valid = all(lower_cased_discordance %in% allowed_values)
    if (!result$valid) {
        result$message = sprintf("Unrecognized values in the Discordance column: (%s). Allowed values are (%s).",
            paste(setdiff(lower_cased_discordance, allowed_values), collapse=','),
            paste(allowed_values, collapse=','))
    }

    return(result)
}

validate_q3 <- function(filename) {
    df = read_delim_or_csv(filename)
    result = validate_data_frame(get_expected_format("q3.txt"), df)

    if (!result$valid) {
        return(result)
    }

    ## check that Diagnoses all come from the set of allowed values
    # TODO do we allow NAs?
    diagnosis_values = c('Normal', 'MCI', 'AD')
    result$valid = all(df$Diagnosis %in% diagnosis_values)
    if (!result$valid) {
        result$message = sprintf("Unrecognized values in the Diagnosis column: (%s). Allowed values are (%s).",
            paste(setdiff(df$Diagnosis, diagnosis_values), collapse=','),
            paste(diagnosis_values, collapse=','))
    }

    return(result)
}



# Question 1 - Predict change in MMSE at 24 months ------------------------

Q1_score = function (predicted, observed) {
    # predicted: a data.frame with two columns, ROSMAP ID and MMSE at 24 month predictions
    # observed: a data.frame with ROSMAP ID (rosmap.id) and actual MMSE at 24 month (mmse.24)

    # combine data
    combined.df <- merge (predicted, observed, by='projid')

    # calculate correlations
    corr_pearson_clin <- with (combined.df, cor(delta_MMSE_clin, MMSEm24-MMSEbl))
    if (is.na (corr_pearson_clin)) stop ("Unable to match subject identifiers")

    corr_pearson_clin_gen <- with (combined.df, cor(delta_MMSE_clin_gen, MMSEm24-MMSEbl))
    if (is.na (corr_pearson_clin_gen)) stop ("Unable to match subject identifiers")

    corr_spearman_clin <- with (combined.df, cor(delta_MMSE_clin, MMSEm24-MMSEbl, method="spearman"))
    if (is.na (corr_spearman_clin)) stop ("Unable to match subject identifiers")

    corr_spearman_clin_gen <- with (combined.df, cor(delta_MMSE_clin_gen, MMSEm24-MMSEbl, method="spearman"))
    if (is.na (corr_spearman_clin_gen)) stop ("Unable to match subject identifiers")

    list(correlation_pearson_clin=corr_pearson_clin,
         correlation_pearson_clin_gen=corr_pearson_clin_gen,
         correlation_spearman_clin=corr_spearman_clin,
         correlation_spearman_clin_gen=corr_spearman_clin_gen)
}


mean_rank = function (df) {
    ranks <- as.data.frame(lapply(df, function(x) {rank(-x)}))
    mean_rank <- apply(ranks, 1, mean)
    final_rank <- rank(mean_rank)

    results <- data.frame(mean_rank=mean_rank, final_rank=final_rank)
    rownames(results) <- rownames(df)

    return(results)
}


# Question 2 - Discordance ------------------------------------------------

Q2_score = function (predicted, observed) {
    # predicted should be a data.frame with ROSMAP ID and discordance probability predictions
    # observed is a data.frame for testing with ROSMAP ID (rosmap.id) and discordance indicator (disc.ind)

    # combine data
    combined.df <- merge (predicted, observed, by='projid')

    # calculate metrics
    # Brier's score
    q2.brier <- with (combined.df, mean ((Confidence - actual_discordance)^2))
    if (is.na (q2.brier)) stop ("Unable to match subject identifiers")
    # AUC and CI
    q2.auc <- with (combined.df, as.numeric (roc(actual_discordance ~ Confidence)$auc))#, ci = TRUE))
    if (is.na (q2.auc)) stop ("Unable to match subject identifiers")
    ## Somer's D
    q2.s <- 2*(q2.auc - 0.5)

    balancedAccuracy <- function(pred,true){
        pred <- as.numeric(pred)
        true <- as.numeric(true)
        if(sum(!unique((c(pred,true)))%in%c(0,1))>0) stop ("Undiscovered matching error: recode")
        res <- table(pred,true)
        tp <- sum((pred==1)&(true==1))
        tn <- sum((pred==0)&(true==0))
        return(0.5*tp/(sum(true==1))+0.5*tn/(sum(true==0)))
    }

    ## Accuracy: according to the AD Challenge wiki, 1=Discordant and 0=Concordant
    predicted_discordance <- tolower(predicted$Discordance) == "discordant"
    q2.accuracy <- sum(predicted_discordance==observed$actual_discordance) / length(observed$actual_discordance)

    q2.balancedAccuracy <- balancedAccuracy(predicted_discordance,observed$actual_discordance)

    #logDeviance <- function(confidence,true){
    #    if((min(confidence,na.rm=T)<0)|(max(confidence>1,na.rm=T))|(sum(is.na(confidence)>0))) stop ("Undiscovered matching error: recode")
    #    ld <- -2*sum(log(confidence[true==1]))
    #    ld <- ld-2*sum(log(1-confidence[true==0]))
    #    return(ld)
    #}

    #q2.logDeviance <- with(combined.df, logDeviance(Confidence,actual_discordance))

    list(brier=q2.brier, auc=q2.auc, somer=q2.s, accuracy=q2.balancedAccuracy)
}


score_q1 <- function(filename) {
    df = read_delim_or_csv(filename)
    expected = get_expected_format("q1.rosmap.csv")
    df = df[match(expected$projid, df$projid),]
    Q1_score(df, expected)
}

score_q2 <- function(filename) {
    df = read_delim_or_csv(filename)
    expected = get_expected_format("q2.observed.txt")
    df = df[match(expected$projid, df$projid),]
    Q2_score(df, expected)
}

