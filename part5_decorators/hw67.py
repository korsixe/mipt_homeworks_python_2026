import json
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
        need_error: type[Exception] = Exception,
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
        self.need_error = need_error

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        func_name = f"{func.__module__}.{func.__name__}"
        state: list[Any] = [0, None]

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            return self._invoke(func, func_name, state, args, kwargs)

        return wrapper

    def _invoke(
        self,
        func: CallableWithMeta[P, R_co],
        func_name: str,
        state: list[Any],
        args: Any,
        kwargs: Any,
    ) -> R_co:
        if state[1] is not None:
            self._raise_if_still_blocked(state[1], func_name)
            state[0] = 0
            state[1] = None
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            if isinstance(exc, self.need_error):
                state[0], state[1] = self._count_error(state[0])
            if state[1] is not None:
                raise BreakerError(func_name=func_name, block_time=state[1]) from exc
            raise
        else:
            state[0] = 0
            return result

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
