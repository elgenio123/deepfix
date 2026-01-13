/**
 * Token management utilities for authentication.
 * Centralized token handling to avoid duplicate implementations.
 */

export const TOKEN_KEY = "deepfix_token";

/**
 * Get the authentication token from local storage.
 */
export const getToken = (): string | null => {
    return localStorage.getItem(TOKEN_KEY);
};

/**
 * Store the authentication token in local storage.
 */
export const setToken = (token: string): void => {
    localStorage.setItem(TOKEN_KEY, token);
};

/**
 * Remove the authentication token from local storage.
 */
export const removeToken = (): void => {
    localStorage.removeItem(TOKEN_KEY);
};
