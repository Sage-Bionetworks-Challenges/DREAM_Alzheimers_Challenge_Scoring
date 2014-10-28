library(synapseClient)
synapseLogin()

library(tools)

#tar_path = '/bin/tar'
tar_path = '/usr/bin/tar'
if (!file.exists(tar_path)) {
    stop("locate path to the tar utility!")
}

## read either a csv or tab delimited file and return a data frame
read_delim_or_csv <- function(path) {
    if (grepl('.csv$', path)) {
        read.csv(path, stringsAsFactors=FALSE)
    } else {
        read.table(path, header=TRUE, quote="\"", fill=TRUE, stringsAsFactors=FALSE)
    }
}

folder <- synGet("syn2773668")

eids <- c(q1=2480744, q2=2480748, q3=2480750, q1f=2700269, q2f=2700271, q3f=2700273)
evaluations <- lapply(eids, function(eid) synGetEvaluation(eid))

for (abr in names(evaluations)) {

    evaluation <- evaluations[[abr]]

    cat("processing submissions for: ", abr, "\n")

    ## get a list of submissions and download prediction files
    subs <- synGetSubmissions(evaluation$id, status="SCORED", limit=10000)
    subs <- lapply(subs@results, function(sub) synGetSubmission(sub@properties$id))

    cat(sprintf("retrieved %d submissions\n", length(subs)))

    ## load the prediction files into a list
    preds <- lapply(subs, function(sub) read_delim_or_csv(sub@filePath))
    names(preds) <- sapply(subs, function(sub) sub$id)

    cat(sprintf("loaded %d predictions\n", length(preds)))

    rdatafile <- paste0(abr,".submissions.RData")
    save(preds, file=rdatafile)
    file1 <- synStore(File(rdatafile, parentId=folder@properties$id), used='syn2290704', executed='syn2773839')

    cat(sprintf("stored in synapse %s\n", file1@properties$id))

    tar_dir <- evaluation$name
    dir.create(tar_dir)
    source_files <- sapply(subs, function(sub) sub@filePath)
    dest_files <- paste0(tar_dir, '/', sapply(subs, function(sub) sub$id), '.', file_ext(source_files))

    file.copy(from=source_files, to=dest_files)

    tarfile <- paste0(abr,".submissions.tgz")
    tar(tarfile, files=tar_dir, compression="gzip", tar=tar_path)
    file1 <- synStore(File(tarfile, parentId=folder@properties$id), used='syn2290704', executed='syn2773839')

    cat(sprintf("stored in synapse %s\n", file1@properties$id))
}


anno_to_list <- function(annos) {
    results = list()
    atypes = c('stringAnnos', 'doubleAnnos', 'longAnnos')
    for (atype in intersect(atypes, names(annos))) {
        for (anno in annos[[atype]]) {
            results[anno$key] = anno$value
        }
    }
    return (results)
}

anno_to_keys <- function(annos) {
    atypes = c('stringAnnos', 'doubleAnnos', 'longAnnos')
    c(lapply( intersect(atypes, names(annos)), function(atype) {
            sapply(annos[[atype]], function(anno) anno$key)
        }), recursive=T)
}

filter_list <- function(lst, accept_keys) {
    lst[intersect(names(lst), accept_keys)]
}


## capture submission metadata
for (abr in names(evaluations)) {

    evaluation <- evaluations[[abr]]

    cat("processing submissions for: ", abr, "\n")

    ## get a list of submissions and status objects
    subs <- synGetSubmissions(evaluation$id, status="SCORED", limit=10000)
    subs <- subs@results
    statuses <- lapply(subs, function(sub) synGetSubmissionStatus(sub@properties$id))

    cat(sprintf("retrieved %d submissions\n", length(subs)))

    name <- paste0(abr,".submissions.metadata")

    ## Some status objects have extra keys (for example, submission ID 2773627).
    ## To make a data.frame, we need to filter those out, so we end up with a
    ## rectangular data set with all rows having the same columns.
    common_keys <- Reduce(intersect, lapply(statuses, function(status) anno_to_keys(status@properties$annotations)))

    ## create a data.frame holding submission details
    assign(name,
        do.call(rbind, mapply(function(sub, status) {
            as.data.frame(append(
                list(id=sub@properties$id,
                     createdOn=sub@properties$createdOn,
                     modifiedOn=status@properties$modifiedOn,
                     userId=sub@properties$userId,
                     name=sub@properties$name,
                     entityId=sub@properties$entityId,
                     entityId=sub@properties$entityId,
                     version=sub@properties$versionNumber),
                filter_list(anno_to_list(status@properties$annotations), accept_keys=common_keys)),
                stringsAsFactors=FALSE)
        }, subs, statuses, SIMPLIFY=F)))

    rdatafile <- paste0(abr,".submissions.metadata.RData")
    save(list=name, file=rdatafile)
    file1 <- synStore(File(rdatafile, parentId=folder@properties$id), used='syn2290704', executed='syn2773839')

    cat(sprintf("stored in synapse %s\n", file1@properties$id))
}
