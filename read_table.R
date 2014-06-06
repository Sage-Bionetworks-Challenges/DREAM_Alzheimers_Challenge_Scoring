

read_delim_or_csv <- function(filename) {
    if grepl('.csv$', filename) {
        read.csv(filename)
    } else {
        read.delim(filename)
    }
}

validate_test <- function(df) {
    expected_dim = c(10,2)

    expected_columns = c('Subject', 'MMSE_24')
    subjects = letters[1:10]

    if (!all(expected_dim==dim(df))) {
        return(
            sprintf("Dimensions of submission (%s) are not as expected (%s).", 
                paste(expected_dim, collapse=','),
                paste(dim(df), collapse=',')))
    }

    if (!all(expected_columns==colnames(df))) {
        return(
            sprintf("Column names of submission were (%s) but should be (%s).",
                paste(expected_column, collapse=","),
                paste(colnames(df), collapse=",")))
    }

    if (!setequal(df$Subjects, subjects)) {
        return(
            sprintf("Subjects of submission were (%s)... but should be (%s)...",
                paste(subjects, collapse=","),
                paste(df$Subjects, collapse=",")))
    }
}
validate_test(df)

