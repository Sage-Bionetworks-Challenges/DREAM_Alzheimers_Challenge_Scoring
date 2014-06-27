##
##  Validate and score AD Challenge submissions
############################################################
suppressMessages(require(pROC))

DATA_DIR = "data/scoring"

## cache the answers so we don't keep reading them
EXPECTED_FORMAT_FILES = list()

## read either a csv or tab delimited file and return a data frame
read_delim_or_csv <- function(filename) {
    if (grepl('.csv$', filename)) {
        read.csv(filename, stringsAsFactors=FALSE)
    } else {
        read.delim(filename, stringsAsFactors=FALSE)
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
}

validate_q3 <- function(filename) {
    df = read_delim_or_csv(filename)
    result = validate_subjects_data_frame(get_expected_format("q3.txt"), df)

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

    # calculate correlation
    corr_clin <- with (combined.df, cor(delta_MMSE_clin, MMSEm24-MMSEbl))
    if (is.na (corr_clin)) stop ("Unable to match subject identifiers")

    corr_clin_gen <- with (combined.df, cor(delta_MMSE_clin_gen, MMSEm24-MMSEbl))
    if (is.na (corr_clin_gen)) stop ("Unable to match subject identifiers")

    list(correlation_clin=corr_clin, correlation_clin_gen=corr_clin_gen)
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

    list(brier=q2.brier, auc=q2.auc, somer=q2.s)
}


score_q1 <- function(filename) {
    df = read_delim_or_csv(filename)
    expected = get_expected_format("q1.rosmap.csv")
    df = df[match(expected$Subject, df$Subject),]
    Q1_score(df, expected)
}

score_q2 <- function(filename) {
    df = read_delim_or_csv(filename)
    expected = get_expected_format("q2.observed.txt")
    df = df[match(expected$Subject, df$Subject),]
    Q2_score(df, expected)
}

