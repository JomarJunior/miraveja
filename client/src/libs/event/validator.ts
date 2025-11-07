import Ajv, { type Schema } from "ajv";
import { EventRegistry } from "./registry";

const ajv = new Ajv({ allErrors: true });

export function validateEvent(topic: string, payload: unknown): void {
    const registry = EventRegistry as Record<string, Schema | undefined>;
    const schema = registry[topic];
    if (!schema) throw new Error(`No schema registered for topic: ${topic}`);

    const validate = ajv.compile(schema);
    if (!validate(payload)) {
        throw new Error(`Validation failed for topic: ${topic}, errors: ${ajv.errorsText(validate.errors)}`);
    }
}