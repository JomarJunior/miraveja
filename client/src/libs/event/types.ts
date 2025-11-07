export interface DomainEvent<T> {
    id: string;
    topic: string;
    type: string;
    aggregateId: string;
    aggregateType: string;
    version: number;
    occurredAt: string;
    payload: T;
};