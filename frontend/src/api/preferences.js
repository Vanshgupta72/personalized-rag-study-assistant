import api from './axios'

// Logged-in user ki saved preferences fetch karo.
export const getPreferences = async () => {
  const response = await api.get('/preferences')
  return response.data
}

// Sirf supplied fields backend ko bhejo, taaki existing preferences reset na hon.
export const updatePreferences = async ({
  preferred_language,
  explanation_style,
  learning_profile,
  onboarding_completed,
}) => {
  const payload = {}

  if (preferred_language !== undefined) payload.preferred_language = preferred_language
  if (explanation_style !== undefined) payload.explanation_style = explanation_style
  if (learning_profile !== undefined) payload.learning_profile = learning_profile
  if (onboarding_completed !== undefined) payload.onboarding_completed = onboarding_completed

  const response = await api.put('/preferences', payload)
  return response.data
}
