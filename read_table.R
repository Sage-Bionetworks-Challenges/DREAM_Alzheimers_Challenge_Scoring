##
##  Validate and score AD Challenge submissions
############################################################

DATA_DIR = "test_data"
EXPECTED_FORMAT_FILES = list()


read_delim_or_csv <- function(filename) {
    if (grepl('.csv$', filename)) {
        read.csv(filename, stringsAsFactors=FALSE)
    } else {
        read.delim(filename, stringsAsFactors=FALSE)
    }
}

get_expected_format <- function(filename) {
    if (!(filename %in% names(EXPECTED_FORMAT_FILES))) {
        expected <- read_delim_or_csv(file.path(DATA_DIR, filename))
        EXPECTED_FORMAT_FILES[[filename]] <- expected
    }
    return(EXPECTED_FORMAT_FILES[[filename]])
}


## parameters:
##   expected: a data.frame with the expected columns and Subject identifiers
##         df: the data.frame to be validated
##
## returns a list of two elements:
##      valid: TRUE / FALSE
##    message: a string
validate_subjects_data_frame <- function(expected, df) {
    if (!all(dim(expected)==dim(df))) {
        return(list(
            valid=FALSE,
            message=sprintf("Dimensions of submission (%s) are not as expected (%s).", 
                paste(dim(df), collapse=','),
                paste(dim(expected), collapse=','))))
    }

    if (!all(colnames(expected)==colnames(df))) {
        return(list(
            valid=FALSE,
            message=sprintf("Column names of submission were (%s) but should be (%s).",
                paste(colnames(df), collapse=","),
                paste(colnames(expected), collapse=","))))
    }

    if (!setequal(df$Subjects, expected$Subjects)) {
        return(list(
            valid=FALSE,
            message=sprintf("Subjects of submission were (%s)... but should be (%s)...",
                paste(df$Subjects, collapse=","),
                paste(expected$Subjects, collapse=","))))
    }

    return(list(valid=TRUE, message="OK"))
}

validate_q1 <- function(filename) {
    df = read_delim_or_csv(filename)
    result = validate_subjects_data_frame(get_expected_format("q1.txt"), df)
}

validate_q2 <- function(filename) {
    df = read_delim_or_csv(filename)
    result = validate_subjects_data_frame(get_expected_format("q2.txt"), df)
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

