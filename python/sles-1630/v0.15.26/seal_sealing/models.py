import functools
from enum import Enum


@functools.total_ordering
class Result(Enum):
    started = "started"
    finished = "finished"
    failed = "failed"

    def __lt__(self, other: "Result") -> bool:
        order = [
            Result.started,
            Result.failed,
            Result.finished,
        ]
        return order.index(self) < order.index(other)


@functools.total_ordering
class Stage(Enum):
    acknowledged = "acknowledged"
    getVersions = "getVersions"
    createPatchFiles = "createPatchFiles"
    waitForPRChecks = "waitForPRChecks"
    buildArtifacts = "buildArtifacts"
    replaceContentInFile = "replaceContentInFile"
    runCI = "runCI"
    addCommitAndPushGit = "addCommitAndPushGit"
    generateMetadataPR = "generateMetadataPR"
    getVersionsToFix = "getVersionsToFix"
    unknown = "unknown"
    uploaded = "uploaded"

    def __lt__(self, other: "Stage") -> bool:
        order = [
            # These two statuses aren't coresponding to a stage
            Stage.addCommitAndPushGit,
            Stage.replaceContentInFile,
            # acknowledged is the first stage, anything before that isn't really considered as a stage
            Stage.acknowledged,
            Stage.getVersions,
            Stage.getVersionsToFix,
            Stage.generateMetadataPR,
            Stage.createPatchFiles,
            Stage.runCI,
            Stage.buildArtifacts,
            Stage.waitForPRChecks,
            Stage.unknown,
            Stage.uploaded,
        ]
        return order.index(self) < order.index(other)
