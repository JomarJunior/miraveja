// Use MUI components
import * as MuiMaterial from '@mui/material';
import React from 'react';

export interface MiraFormField<target extends object> {
    label: string;
    field: keyof target;
    type: 'text' | 'number' | 'textarea' | 'select' | 'checkbox' | 'loraselect';
    placeholder?: string;
    defaultValue?: unknown;
    icon?: React.ReactNode;
    items?: { label: string; value: string | number | readonly string[] }[];
};

interface MiraFormProps<T extends object> {
    target: T;
    fields: MiraFormField<T>[];
    onChange: (updatedTarget: T, field: keyof T) => void;
    onInputChange?: (field: keyof T, value: unknown) => void;
};

const getFieldComponent = <T extends object>(
    fieldDef: MiraFormField<T>, value: unknown,
    onChange: (value: unknown, field: keyof T) => void,
    onInputChange?: (field: keyof T, value: unknown) => void
) => {
    const fieldType = fieldDef.type;
    const fieldMap: Record<string, React.ReactNode> = {
        text: (
            <MuiMaterial.TextField
                fullWidth
                variant="outlined"
                value={value as string ?? fieldDef.defaultValue ?? ''}
                label={fieldDef.label}
                placeholder={fieldDef.placeholder}
                slotProps={
                    {
                        input: {
                            startAdornment: (
                                <MuiMaterial.InputAdornment position="start">
                                    {fieldDef.icon}
                                </MuiMaterial.InputAdornment>
                            )
                        }
                    }
                }
                onChange={(e) => onChange(e.target.value, fieldDef.field)}
            />
        ),
        number: (
            <MuiMaterial.TextField
                fullWidth
                variant="outlined"
                type="number"
                value={value as number ?? fieldDef.defaultValue ?? 0}
                label={fieldDef.label}
                placeholder={fieldDef.placeholder}
                slotProps={{
                    input: {
                        startAdornment: (
                            <MuiMaterial.InputAdornment position="start">
                                {fieldDef.icon}
                            </MuiMaterial.InputAdornment>
                        )
                    }
                }}
                onChange={(e) => onChange(Number(e.target.value), fieldDef.field)}
            />
        ),
        textarea: (
            <MuiMaterial.TextField
                fullWidth
                variant="outlined"
                multiline
                minRows={3}
                value={value as string ?? fieldDef.defaultValue ?? ''}
                label={fieldDef.label}
                placeholder={fieldDef.placeholder}
                slotProps={
                    {
                        input: {
                            startAdornment: (
                                <MuiMaterial.InputAdornment position="start">
                                    {fieldDef.icon}
                                </MuiMaterial.InputAdornment>
                            )
                        }
                    }
                }
                sx={{
                    '& .MuiInputBase-input': { // Target the actual input element
                        overflow: 'hidden',
                        maxHeight: '150px',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'pre-wrap',
                    },
                }}
                onChange={(e) => onChange(e.target.value, fieldDef.field)}
            />
        ),
        select: (
            <MuiMaterial.Select
                fullWidth
                label={fieldDef.label}
                value={value as string | undefined ?? fieldDef.defaultValue ?? ''}
                onChange={(e) => onChange(e.target.value, fieldDef.field)}
            >
                {fieldDef.items?.map((item) => (
                    <MuiMaterial.MenuItem key={String(item.value)} value={String(item.value)}>
                        {item.label}
                    </MuiMaterial.MenuItem>
                ))}
            </MuiMaterial.Select>
        ),
        checkbox: (
            <MuiMaterial.FormControlLabel
                control={
                    <MuiMaterial.Checkbox
                        value={value as boolean ?? fieldDef.defaultValue ?? false}
                        checked={Boolean(value)}
                        onChange={(e) => onChange(e.target.checked, fieldDef.field)}
                    />
                }
                label={fieldDef.label}
            />
        ),
        loraselect: (
            <MuiMaterial.Autocomplete
                multiple
                freeSolo
                options={fieldDef.items ?? []}
                value={fieldDef.defaultValue as { label: string; value: string }[] ?? []}
                getOptionLabel={getOptionLabel}
                getOptionKey={getOptionKey}
                renderInput={(params) => (
                    <MuiMaterial.TextField
                        {...params}
                        label={fieldDef.label}
                        placeholder={fieldDef.placeholder}
                        variant="outlined"
                        fullWidth
                    />
                )}
                renderOption={(props, option) => {
                    return (
                        <li {...props} key={getOptionUniqueKey(option)}>
                            {getOptionLabel(option)}
                        </li>
                    );
                }}
                onChange={(_, newValue) => onChange(newValue, fieldDef.field)}
                onInputChange={(_, newValue) => onInputChange?.(fieldDef.field, newValue)}
            />
        ),
    };

    return fieldMap[fieldType] ?? null;
};

const getOptionLabel = (option: unknown): string => {
    if (option && typeof option === 'object' && 'label' in option) {
        return option.label as string;
    }
    return String(option);
};

const getOptionKey = (option: unknown): string => {
    if (option && typeof option === 'object' && 'label' in option) {
        return option.label as string;
    }
    return String(option);
};

const getOptionUniqueKey = (option: unknown): string => {
    if (option && typeof option === 'object' && 'value' in option) {
        const { id } = JSON.parse(option.value as string) as { id?: number };
        return id ? String(id) : String(option.value);
    }
    return '';
};

interface OnInputChangeCallbackMap<T extends object> {
    field: keyof T;
    value: unknown;
    timeoutId?: number;
    callback: (field: keyof T, value: unknown) => void;
};

export default function MiraForm<T extends object>({ target, fields, onChange, onInputChange }: MiraFormProps<T>) {
    const [inputChangeCallbacks, setInputChangeCallbacks] = React.useState<OnInputChangeCallbackMap<T>[]>([]);

    const handleFieldChange = (field: keyof T, value: unknown) => {
        onChange({ ...target, [field]: value }, field);
    };

    const handleInputChange = (field: keyof T, value: unknown) => {
        // This function should debounce the input changes
        if (onInputChange) {
            // Clear any existing timeout for this field
            const existingCallback = inputChangeCallbacks.find((cb) => cb.field === field);
            if (existingCallback?.timeoutId) {
                clearTimeout(existingCallback.timeoutId);
                setInputChangeCallbacks((prev) => prev.filter((cb) => cb.field !== field));
            }
            // Set a new timeout for the input change
            const timeoutId = window.setTimeout(() => {
                onInputChange(field, value);
            }, 300);
            // Store the timeoutId to allow clearing if needed
            setInputChangeCallbacks((prev) => [...prev, { field, value, timeoutId, callback: onInputChange }]);
        }
    };

    return (
        <MuiMaterial.Stack spacing={1} sx={{ mt: 2 }}>
            {fields.map((fieldDef) => {
                let value = target[fieldDef.field] as unknown;
                if (Array.isArray(value)) {
                    value = value.map((v: { name: string }) => v.name);
                }
                return (
                    <MuiMaterial.FormControl key={String(fieldDef.field)} fullWidth>
                        {getFieldComponent(
                            fieldDef,
                            value,
                            (val) => handleFieldChange(fieldDef.field, val),
                            (fld, val) => handleInputChange(fld, val),
                        )}
                    </MuiMaterial.FormControl>
                );
            })}
        </MuiMaterial.Stack>
    );
};
