from enum import Enum


class SimplifiedApplicationStateType(Enum):
    PendingState = "PENDING"
    RunningState = "RUNNING"
    CompletedState = "COMPLETED"
    FailedState = "FAILED"

    @property
    def is_terminal(self) -> bool:
        return self in [
            SimplifiedApplicationStateType.CompletedState,
            SimplifiedApplicationStateType.FailedState,
        ]

    @property
    def is_successful(self) -> bool:
        return self == SimplifiedApplicationStateType.CompletedState


class ApplicationStateType(Enum):
    NewState = ""
    SubmittedState = "SUBMITTED"
    RunningState = "RUNNING"
    CompletedState = "COMPLETED"
    FailedState = "FAILED"
    FailedSubmissionState = "SUBMISSION_FAILED"
    PendingRerunState = "PENDING_RERUN"
    InvalidatingState = "INVALIDATING"
    SucceedingState = "SUCCEEDING"
    FailingState = "FAILING"
    UnknownState = "UNKNOWN"

    @property
    def simplified(self) -> SimplifiedApplicationStateType:
        return _state_mapping[self]


_state_mapping = {
    ApplicationStateType.NewState: SimplifiedApplicationStateType.PendingState,
    ApplicationStateType.SubmittedState: SimplifiedApplicationStateType.PendingState,
    ApplicationStateType.PendingRerunState: SimplifiedApplicationStateType.PendingState,
    ApplicationStateType.UnknownState: SimplifiedApplicationStateType.PendingState,
    ApplicationStateType.RunningState: SimplifiedApplicationStateType.RunningState,
    ApplicationStateType.InvalidatingState: SimplifiedApplicationStateType.RunningState,
    ApplicationStateType.SucceedingState: SimplifiedApplicationStateType.RunningState,
    ApplicationStateType.FailingState: SimplifiedApplicationStateType.RunningState,
    ApplicationStateType.CompletedState: SimplifiedApplicationStateType.CompletedState,
    ApplicationStateType.FailedState: SimplifiedApplicationStateType.FailedState,
    ApplicationStateType.FailedSubmissionState: SimplifiedApplicationStateType.FailedState,
}
