// src/services/api.js
// noinspection ExceptionCaughtLocallyJS

const API_BASE_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:5000';

/**
 * Sends a prompt to the server and streams the response.
 * @param {Object} promptData - The data to send to the server.
 * @param {Function} onChunk - Callback function to handle each chunk of the response.
 * @param {Function} onError - Callback function to handle any errors.
 * @param {Function} onComplete - Callback function called when the stream is complete.
 */
export const streamPrompt = async (promptData, onChunk, onError, onComplete) => {
    try {
        const response = await fetch(`${API_BASE_URL}/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(promptData),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                onComplete();
                break;
            }
            const chunk = decoder.decode(value);
            onChunk(chunk);
        }
    } catch (error) {
        console.error('Error in stream:', error);
        onError(error);
    }
};

/**
 * Fetches available models from the server.
 * @returns {Promise<Object>} A promise that resolves to an object containing local and OpenAI models.
 */
export const getModels = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/get_models`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching models:', error);
        throw error;
    }
};

/**
 * Saves a prompt to the server.
 * @param {Object} promptData - The prompt data to save.
 * @returns {Promise<Object>} A promise that resolves to the server's response.
 */

export const createPrompt = async (promptData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/create_prompt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(promptData),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error saving prompt:', error);
        throw error;
    }
};

/**
 * Fetches the prompt history from the server.
 * @returns {Promise<Array>} A promise that resolves to an array of previous prompts.
 */
export const getPromptHistory = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/prompt_history`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching prompt history:', error);
        throw error;
    }
};

export const loadAndValidateModels = async (selectedModels, setSelectedModels) => {
    try {
        const response = await fetch(`${API_BASE_URL}/get_models`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const localModels = data.local_models;
        const openaiModels = data.openai_models;

        // Combine all available models
        const availableModels = [...localModels, ...openaiModels];
        // Validate selected models
        const validSelectedModels = selectedModels.filter(model => availableModels.includes(model));

        if (validSelectedModels.length > 0) {
            setSelectedModels(validSelectedModels);
        } else {
            // If no valid selected models, set the first available model as default
            if (localModels.length > 0) {
                setSelectedModels([localModels[0]]);
            } else if (openaiModels.length > 0) {
                setSelectedModels([openaiModels[0]]);
            }
        }

        return { localModels, openaiModels, validSelectedModels };
    } catch (error) {
        console.error('Error loading and validating models:', error);
        throw error;
    }
};
