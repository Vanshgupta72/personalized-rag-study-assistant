import api from './axios'

export const askQuestion = async (
  question,
  conversationId = null,
  topK = 5
) => {
  const response = await api.post('/chat/ask', {
    question,
    conversation_id: conversationId,
    top_k: topK,
  })

  return response.data
}