import { validateEvent } from "./validator";
import type { DomainEvent } from "./types";

export class EventClient {
    private socket: WebSocket;

    constructor(socket: WebSocket) {
        this.socket = socket;
    }

    publish<T>(event: DomainEvent<T>): void {
        validateEvent(event.topic, event.payload);

        const message = JSON.stringify(event);
        this.socket.send(message);
    }

    subscribe<T>(
        topic: string,
        handler: (event: DomainEvent<T>) => void,
    ): void {
        this.socket.addEventListener("message", (messageEvent) => {
            const event: DomainEvent<unknown> = JSON.parse(messageEvent.data as string) as DomainEvent<unknown>;
            if (event.topic === topic) {
                validateEvent(event.topic, event.payload);
                handler(event as DomainEvent<T>);
            }
        });
    }
};