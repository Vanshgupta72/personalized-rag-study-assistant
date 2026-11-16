import api from './axios'

export const getSubjects = async () => {
  const response = await api.get('/subjects')

  return response.data
}

export const createSubject = async (name) => {
  const response = await api.post('/subjects', {
    name,
  })

  return response.data
}

export const deleteSubject = async (subjectId) => {
  await api.delete(`/subjects/${subjectId}`)
}