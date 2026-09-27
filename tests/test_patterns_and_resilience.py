from app.coordinator.events import EventBus
from app.coordinator.mediator import CoordinatorMediator
from app.coordinator.strategy import RoundRobinStrategy, WorkerDescriptor
from app.common.local_transport import LocalWorkerAdapter
from app.worker.executor import WorkerExecutor


def make_system(failed: set[str] | None = None):
    workers = {
        "w1": WorkerExecutor("w1", 2),
        "w2": WorkerExecutor("w2", 2),
        "w3": WorkerExecutor("w3", 2),
    }
    descriptors = [WorkerDescriptor(k, f"local://{k}") for k in workers]
    events = EventBus()
    observed: list[tuple[str, dict]] = []
    for event_name in ("job.dispatched", "job.completed", "worker.failed"):
        events.subscribe(event_name, lambda payload, e=event_name: observed.append((e, payload)))
    mediator = CoordinatorMediator(
        strategy=RoundRobinStrategy(descriptors),
        worker_port=LocalWorkerAdapter(workers, failed),
        events=events,
    )
    return workers, mediator, observed


def test_round_robin_distributes_jobs():
    workers, mediator, _ = make_system()
    try:
        ids = [mediator.dispatch(f"job-{i}", 1, set(workers))["worker_id"] for i in range(6)]
        assert ids == ["w1", "w2", "w3", "w1", "w2", "w3"]
    finally:
        for worker in workers.values():
            worker.close()


def test_failed_worker_is_bypassed():
    workers, mediator, observed = make_system({"w1"})
    try:
        result = mediator.dispatch("resilient-job", 1, set(workers))
        assert result["worker_id"] in {"w2", "w3"}
        assert any(event == "worker.failed" for event, _ in observed)
    finally:
        for worker in workers.values():
            worker.close()


def test_observer_receives_completion_event():
    workers, mediator, observed = make_system()
    try:
        mediator.dispatch("observable-job", 1, set(workers))
        assert any(event == "job.completed" for event, _ in observed)
    finally:
        for worker in workers.values():
            worker.close()
