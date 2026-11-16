import api from './axios'

export const getDocuments = async () => {
  const response = await api.get('/documents')

  return response.data
}

export const uploadDocument = async (
  file,
  subjectId = null,
  topicId = null
) => {
  const formData = new FormData()

  formData.append('file', file)

  if (subjectId !== null) {
    formData.append('subject_id', String(subjectId))
  }

  if (topicId !== null) {
    formData.append('topic_id', String(topicId))
  }

  const response = await api.post(
    '/documents/upload',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )

  return response.data
}

export const deleteDocument = async (documentId) => {
  await api.delete(`/documents/${documentId}`)
}