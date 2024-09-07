const API_BASE_URL = import.meta.env.SERVER_URL || 'http://localhost:8000';

/**
 *
 * @param stream_url
 * @param generationRequest
 * @param onChunk
 * @param buffer
 * @param responses
 * @param onError
 * @param onComplete
 * @returns {Promise<void>}
 */
export const stream = async (stream_url, generationRequest, onChunk, buffer, responses, onError, onComplete) => {
  try {
    const response = await fetch(`${API_BASE_URL}${stream_url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(generationRequest),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        onComplete();
        break;
      }
      const chunk = decoder.decode(value);
      onChunk(chunk,buffer,responses);
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
        const response = await fetch(`${API_BASE_URL}/models`);
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
 * @param {Object} promptRequest - The prompt data to save.
 * @returns {Promise<Object>} A promise that resolves to the server's response.
 */
export const createPrompt = async (promptRequest) => {
    try {
        const response = await fetch(`${API_BASE_URL}/prompts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(promptRequest),
        });

        // Ensure response is defined and has an 'ok' property
        if (!response || !response.ok) {
            throw new Error(`HTTP error! status: ${response ? response.status : 'undefined'}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error saving prompt:', error);
        throw error;
    }
};

/**
 * Sends the collected responses to the /usercontext endpoint.
 * @param {object} structuredResponse - Array of response objects to send.
 * @param callback
 * @returns {Promise<void>} A promise that resolves when the request is complete.
 */
export const saveUserContext = async (structuredResponse, callback=null) => {
    try {
        const response = await fetch(`${API_BASE_URL}/usercontext`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(structuredResponse), // Directly send the structured response
        });

        if(callback){
            return callback(response);
        }

    } catch (error) {
        console.error('Error sending responses to /usercontext:', error);
        throw error;
    }
};

/**
 * Fetches the user context from the server based on the provided user and thread ID.
 * @param {string} user - The UUID of the user.
 * @param {number} threadId - The ID of the thread.
 * @returns {Promise<Object>} A promise that resolves to the user context data.
 */
export const fetchUserContext = (user, threadId) => {
    try {


        const url = new URL(`${API_BASE_URL}/usercontext`);
        url.searchParams.append('user', user);
        url.searchParams.append('thread_id', String(threadId));

        return fetch(url.toString(), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
    } catch (error) {
        console.error('Error fetching user context:', error);
        throw error;
    }
};

export  const processChunk = (chunk, buffer, responses) => {
      buffer.value += chunk; // Add chunk to buffer


      let boundary;
      while ((boundary = buffer.value.indexOf('}\n' + '{')) !== -1) {  // Find boundary between JSON objects


        const jsonString = buffer.value.slice(0, boundary + 1);
        buffer.value = buffer.value.slice(boundary + 1);


        let responseModel;
        try {
          responseModel = JSON.parse(jsonString);



          const responseIndex = responses.value.findIndex(
              r => r.id === responseModel.id && r.model === responseModel.model
          );

          if (responseIndex !== -1) {
            responses.value[responseIndex] = {
              ...responses.value[responseIndex],
              completion: responseModel.completion,
            };
          } else {
            responses.value.push(responseModel);
          }
        } catch (error) {
          console.log("Error parsing JSON chunk:", error, jsonString);
        }
      }
    };
/**
 * Deletes a user context by thread ID.
 * @param {number} threadId - The ID of the thread.
 * @returns {Promise<void>} A promise that resolves when the user context is deleted.
 */
export const deleteUserContext = async (threadId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/usercontext/${threadId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to delete user context. HTTP status: ${response.status}`);
        }

        console.log(`User context with thread ID ${threadId} deleted successfully.`);
    } catch (error) {
        console.error('Error deleting user context:', error);
        throw error;
    }
};