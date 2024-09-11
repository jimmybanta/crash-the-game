
import axios from 'axios';

import { BASE_URL } from './BaseUrl';

// function for making an API call - that isn't streaming
export async function apiCall({method, url, 
                                data = null, params = null}) {
    try {

    let response; 
    if (method === 'get') {
    response = await axios ({
    method: method,
    url: url,
    params: params, 
    });
    }
    else if (method === 'post') {
    response = await axios ({
    method: method,
    url: url,
    data: data,
    });
    }
    else {
    response = await axios ({
    method: method,
    url: url,
    data: data,
    });
    }

    if (response.status === 200) {
    return [true, response.data];
    } else {
    return [false, response.data];
    }
    } catch (error) {
    return [false, `There was a problem communicating with the server - please try again.`];
    }
    };

// functions for streaming data from the server
// for use when the server returns a StreamingHttpResponse

// generateStream takes a url and data and returns an async generator
export const generateStream = async (url, data)  => {
    // fetch data from the server
    const response = await fetch(
        BASE_URL + url,
        {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        }
      
    )
    if (response.status !== 200) throw new Error(response.status.toString())
    if (!response.body) throw new Error('Response body does not exist')
    return getIterableStream(response.body)
  }
  

// getIterableStream takes a response body and returns an async generator
export async function* getIterableStream(body) {
    const reader = body.getReader()
    const decoder = new TextDecoder()
  
    while (true) {
      const { value, done } = await reader.read()
      if (done) {
        break
      }
      const decodedChunk = decoder.decode(value, { stream: true })
      yield decodedChunk
    }
  }
  