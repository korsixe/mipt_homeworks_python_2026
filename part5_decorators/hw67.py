import json
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


@dataclass
class _BreakerState:
    error_count: int = 0
    blocked_since: datetime | None = None


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime) -> None:
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        errors = []
        if not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))
        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        func_name = f"{func.__module__}.{func.__name__}"
        state = _BreakerState()

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            self._maybe_unblock(state, func_name)
            try:
                result = func(*args, **kwargs)
            except self.triggers_on as exc:
                state.error_count, state.blocked_since = self._count_error(state.error_count)
                if state.blocked_since is not None:
                    raise BreakerError(
                        func_name=func_name,
                        block_time=state.blocked_since,
                    ) from exc
                raise exc from None
            else:
                state.error_count = 0
                return result

        return wrapper

    def _maybe_unblock(self, state: _BreakerState, func_name: str) -> None:
        if state.blocked_since is None:
            return
        self._raise_if_still_blocked(state.blocked_since, func_name)
        state.error_count = 0
        state.blocked_since = None

    def _raise_if_still_blocked(self, block_time: datetime, func_name: str) -> None:
        elapsed = (datetime.now(UTC) - block_time).total_seconds()
        if elapsed < self.time_to_recover:
            raise BreakerError(func_name=func_name, block_time=block_time)

    def _count_error(self, faild_count: int) -> tuple[int, datetime | None]:
        new_count = faild_count + 1
        if new_count < self.critical_count:
            return new_count, None
        return new_count, datetime.now(UTC)


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
