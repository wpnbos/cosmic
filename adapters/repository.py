import abc

import domain.model as model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference: str) -> model.Batch:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list[model.Batch]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch) -> None:
        self.session.add(batch)

    def get(self, reference: str) -> model.Batch:
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self) -> list[model.Batch]:
        return self.session.query(model.Batch).all()


class FakeRepository(AbstractRepository):
    def __init__(self, batches: list[model.Batch]) -> None:
        self._batches = batches

    def add(self, batch: model.Batch):
        self._batches.append(batch)

    def get(self, reference: str) -> model.Batch:
        return next(batch for batch in self._batches if batch.reference == reference)

    def list(self) -> list[model.Batch]:
        return self._batches
