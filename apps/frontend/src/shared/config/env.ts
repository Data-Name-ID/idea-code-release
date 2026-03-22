const rawUseMocks = import.meta.env.VITE_USE_MOCKS

// In local dev, enable mocks by default when variable is omitted.
export const USE_MOCKS = rawUseMocks === 'true' || (import.meta.env.DEV && rawUseMocks == null)
