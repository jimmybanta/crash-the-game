

const BASE_URL = 'http://127.0.0.1:8000';


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
  