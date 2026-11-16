import { useEffect, useRef, useState } from 'react'

import './App.css'

import {
  loginUser,
  getCurrentUser,
} from './api/auth'

import {
  getSubjects,
  createSubject,
  deleteSubject,
} from './api/subjects'

import {
  getDocuments,
  uploadDocument,
  deleteDocument,
} from './api/documents'

import { askQuestion } from './api/chat'

// User ki learning preferences fetch aur update karne ke liye
import { getPreferences, updatePreferences } from './api/preferences'


function App() {
  // -----------------------------
  // AUTH STATE
  // -----------------------------

  const [user, setUser] = useState(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const [loading, setLoading] = useState(false)
  const [authMessage, setAuthMessage] = useState('')
  // -----------------------------
  // LEARNING PREFERENCES STATE
  // -----------------------------

  const [preferences, setPreferences] = useState(null)
  const [preferencesLoading, setPreferencesLoading] = useState(false)
  const [preferencesMessage, setPreferencesMessage] = useState('')
  const [onboardingAnswers, setOnboardingAnswers] = useState({ goal: 'exam_preparation', level: 'beginner', depth: 'balanced', approach: 'mixed' })

  // -----------------------------
  // SUBJECT STATE
  // -----------------------------

  const [subjects, setSubjects] = useState([])
  const [newSubject, setNewSubject] = useState('')
  const [subjectMessage, setSubjectMessage] = useState('')

  // -----------------------------
  // DOCUMENT STATE
  // -----------------------------

  const [documents, setDocuments] = useState([])

  // Search and filter uploaded documents
  const [documentSearch, setDocumentSearch] = useState('')
  const [documentSubjectFilter, setDocumentSubjectFilter] = useState('all')

  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedSubjectId, setSelectedSubjectId] = useState('')

  const [documentLoading, setDocumentLoading] = useState(false)
  const [documentMessage, setDocumentMessage] = useState('')

  // -----------------------------
  // CHAT STATE
  // -----------------------------

  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [conversationId, setConversationId] = useState(null)

  const [chatLoading, setChatLoading] = useState(false)
  const [chatMessage, setChatMessage] = useState('')

  const chatEndRef = useRef(null)

  // -----------------------------
  // CHECK AUTH ON START
  // -----------------------------

  useEffect(() => {
    const token = localStorage.getItem('access_token')

    if (!token) {
      return
    }

    loadCurrentUser()
  }, [])

  // -----------------------------
  // SCROLL CHAT
  // -----------------------------

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    })
  }, [messages])

  // -----------------------------
  // LOAD CURRENT USER
  // -----------------------------

  // -----------------------------
  // LOAD LEARNING PREFERENCES
  // -----------------------------

  const loadUserPreferences = async () => {
    setPreferencesLoading(true)
    setPreferencesMessage('')

    try {
      const data = await getPreferences()
      setPreferences(data)
    } catch (error) {
      console.error('Could not load preferences:', error)
      setPreferencesMessage(
        error.response?.data?.detail ||
        'Could not load learning preferences.'
      )
    } finally {
      setPreferencesLoading(false)
    }
  }
  const loadCurrentUser = async () => {
    try {
      const currentUser = await getCurrentUser()

      setUser(currentUser)

      // Login ke baad saved learning preferences load karo.
      await loadUserPreferences()

      await loadDashboardData()
    } catch (error) {
      localStorage.removeItem('access_token')
      setUser(null)
    }
  }

  // -----------------------------
  // LOAD DASHBOARD DATA
  // -----------------------------

  const loadDashboardData = async () => {
    try {
      const subjectData = await getSubjects()
      const documentData = await getDocuments()

      setSubjects(subjectData)
      setDocuments(documentData)
    } catch (error) {
      console.error('Dashboard loading failed:', error)
    }
  }

  // -----------------------------
  // LOGIN
  // -----------------------------

  const handleLogin = async (event) => {
    event.preventDefault()

    setLoading(true)
    setAuthMessage('')

    try {
      const data = await loginUser(
        email,
        password
      )

      localStorage.setItem(
        'access_token',
        data.access_token
      )

      await loadCurrentUser()

      setEmail('')
      setPassword('')
    } catch (error) {
      console.error(error)

      const detail =
        error.response?.data?.detail

      setAuthMessage(
        detail || 'Login failed. Please check your credentials.'
      )
    } finally {
      setLoading(false)
    }
  }

  // -----------------------------
  const handleSaveOnboarding = async (event) => {
    event.preventDefault()
    setPreferencesLoading(true)
    setPreferencesMessage('')
    try {
      const updated = await updatePreferences({ learning_profile: onboardingAnswers, onboarding_completed: true })
      setPreferences(updated)
      setPreferencesMessage('Learning profile saved successfully.')
    } catch (error) {
      setPreferencesMessage(error.response?.data?.detail || 'Could not save learning profile.')
    } finally {
      setPreferencesLoading(false)
    }
  }

  // LOGOUT
  // -----------------------------

  const handleLogout = () => {
    localStorage.removeItem('access_token')

    setUser(null)

    setSubjects([])
    setDocuments([])

    setMessages([])
    setConversationId(null)

    setQuestion('')
  }

  // -----------------------------
  // CREATE SUBJECT
  // -----------------------------

  const handleCreateSubject = async () => {
    if (!newSubject.trim()) {
      return
    }

    setSubjectMessage('')

    try {
      const subject = await createSubject(
        newSubject.trim()
      )

      setSubjects((previous) => [
        ...previous,
        subject,
      ])

      setNewSubject('')

      setSubjectMessage(
        'Subject created successfully.'
      )
    } catch (error) {
      const detail =
        error.response?.data?.detail

      setSubjectMessage(
        detail || 'Could not create subject.'
      )
    }
  }

  // -----------------------------
  // DELETE SUBJECT
  // -----------------------------

  const handleDeleteSubject = async (
    subjectId
  ) => {
    const confirmed = window.confirm(
      'Are you sure you want to delete this subject?'
    )

    if (!confirmed) {
      return
    }

    try {
      await deleteSubject(subjectId)

      setSubjects((previous) =>
        previous.filter(
          (subject) =>
            subject.id !== subjectId
        )
      )

      if (
        String(selectedSubjectId) ===
        String(subjectId)
      ) {
        setSelectedSubjectId('')
      }
    } catch (error) {
      setSubjectMessage(
        error.response?.data?.detail ||
        'Could not delete subject.'
      )
    }
  }

  // -----------------------------
  // FILE SELECT
  // -----------------------------

  const handleFileChange = (event) => {
    const file = event.target.files?.[0]

    setDocumentMessage('')

    if (!file) {
      setSelectedFile(null)
      return
    }

    const fileName = file.name.toLowerCase()

    const isValid =
      fileName.endsWith('.pdf') ||
      fileName.endsWith('.pptx')

    if (!isValid) {
      setSelectedFile(null)

      setDocumentMessage(
        'Only PDF and PPTX files are supported.'
      )

      return
    }

    setSelectedFile(file)
  }

  // -----------------------------
  // UPLOAD DOCUMENT
  // -----------------------------

  const handleDocumentUpload = async () => {
    if (!selectedFile) {
      setDocumentMessage(
        'Please select a PDF or PPTX file.'
      )

      return
    }

    setDocumentLoading(true)
    setDocumentMessage('')

    try {
      const subjectId =
        selectedSubjectId
          ? Number(selectedSubjectId)
          : null

      await uploadDocument(
        selectedFile,
        subjectId,
        null
      )

      setDocumentMessage(
        'Document uploaded and processed successfully.'
      )

      setSelectedFile(null)

      setSelectedSubjectId('')

      const updatedDocuments =
        await getDocuments()

      setDocuments(updatedDocuments)
    } catch (error) {
      console.error(error)

      if (error.response) {
        const detail =
          error.response.data.detail

        if (Array.isArray(detail)) {
          setDocumentMessage(
            detail
              .map((item) => {
                if (item.msg) {
                  return item.msg
                }

                return 'Document validation failed'
              })
              .join(', ')
          )
        } else {
          setDocumentMessage(
            detail ||
            'Document upload failed.'
          )
        }
      } else {
        setDocumentMessage(
          'Cannot connect to backend.'
        )
      }
    } finally {
      setDocumentLoading(false)
    }
  }

  // -----------------------------
  // DELETE DOCUMENT
  // -----------------------------

  const handleDeleteDocument = async (
    documentId
  ) => {
    const confirmed = window.confirm(
      'Are you sure you want to delete this document?'
    )

    if (!confirmed) {
      return
    }

    try {
      await deleteDocument(documentId)

      setDocuments((previous) =>
        previous.filter(
          (document) =>
            document.id !== documentId
        )
      )
    } catch (error) {
      setDocumentMessage(
        error.response?.data?.detail ||
        'Could not delete document.'
      )
    }
  }

  // -----------------------------
  // FILTER DOCUMENTS BY NAME AND SUBJECT
  const filteredDocuments = documents.filter((document) => {
    const filename = String(document.filename || '').toLowerCase()
    const searchTerm = documentSearch.trim().toLowerCase()

    const matchesSearch = filename.includes(searchTerm)

    const matchesSubject =
      documentSubjectFilter === 'all' ||
      (documentSubjectFilter === 'none' && !document.subject_id) ||
      String(document.subject_id) === documentSubjectFilter

    return matchesSearch && matchesSubject
  })
  // SEND CHAT QUESTION
  // -----------------------------

  const handleAskQuestion = async (
    event
  ) => {
    event?.preventDefault()

    const trimmedQuestion =
      question.trim()

    if (!trimmedQuestion) {
      return
    }

    if (chatLoading) {
      return
    }

    setChatMessage('')

    // Immediately show user's message
    setMessages((previous) => [
      ...previous,
      {
        role: 'user',
        content: trimmedQuestion,
      },
    ])

    setQuestion('')
    setChatLoading(true)

    try {
      const result =
        await askQuestion(
          trimmedQuestion,
          conversationId,
          5
        )

      // Save conversation ID returned
      // by backend
      setConversationId(
        result.conversation_id
      )

      // Add AI answer
      setMessages((previous) => [
        ...previous,
        {
          role: 'assistant',
          content: result.answer,
          sources:
            result.sources || [],
        },
      ])
    } catch (error) {
      console.error(
        'Chat request failed:',
        error
      )

      const detail =
        error.response?.data?.detail

      setChatMessage(
        detail ||
        'Could not get an answer from the AI.'
      )

      setMessages((previous) => [
        ...previous,
        {
          role: 'assistant',
          content:
            'Sorry, I could not process your question. Please try again.',
        },
      ])
    } finally {
      setChatLoading(false)
    }
  }

  // -----------------------------
  // NEW CONVERSATION
  // -----------------------------

  const handleNewConversation = () => {
    setMessages([])
    setConversationId(null)
    setQuestion('')
    setChatMessage('')
  }

  // -----------------------------
  // LOGIN PAGE
  // -----------------------------

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center px-4">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">

          <div className="text-center mb-8">
            <div className="text-4xl mb-3">
              <svg className="ui-feature-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H12v17H6.5A2.5 2.5 0 0 0 4 22z"/><path d="M20 5.5A2.5 2.5 0 0 0 17.5 3H12v17h5.5A2.5 2.5 0 0 1 20 22z"/></svg>
            </div>

            <h1 className="text-3xl font-bold text-slate-800">
              StudyAI
            </h1>

            <p className="text-slate-500 mt-2">
              Personalized RAG Study Assistant
            </p>
          </div>

          <form
            onSubmit={handleLogin}
            className="space-y-5"
          >

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                placeholder="Enter your email"
                required
                className="w-full border border-slate-300 rounded-lg px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Enter your password"
                required
                className="w-full border border-slate-300 rounded-lg px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {authMessage && (
              <div className="bg-red-50 text-red-600 border border-red-200 rounded-lg px-4 py-3 text-sm">
                {authMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-semibold rounded-lg py-3 transition"
            >
              {loading
                ? 'Logging in...'
                : 'Login'}
            </button>

          </form>
        </div>
      </div>
    )
  }

  // -----------------------------
  // DASHBOARD
  // -----------------------------

  return (
    <div className="min-h-screen bg-slate-100">

      {/* HEADER */}

      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">

          <div>
            <h1 className="text-2xl font-bold text-slate-800">
               StudyAI
            </h1>

            <p className="text-sm text-slate-500">
              Personalized RAG Study Assistant
            </p>
          </div>

          <div className="flex items-center gap-4">

            <div className="text-right">
              <p className="font-semibold text-slate-700">
                {user.email}
              </p>

              <p className="text-xs text-slate-500">
                Student
              </p>
            </div>

            <button
              onClick={handleLogout}
              className="bg-slate-800 hover:bg-slate-900 text-white px-4 py-2 rounded-lg text-sm"
            >
              Logout
            </button>

          </div>

        </div>
      </header>


      <div className="saas-layout">
        <aside className="saas-sidebar">
          <div className="saas-sidebar-brand">
            <span className="saas-brand-mark" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 19V5l7 10 7-10v14" /></svg></span>
            <div><strong>StudyAI</strong><span>Your learning space</span></div>
          </div>
          <p className="saas-nav-label">WORKSPACE</p>
          <nav className="saas-nav" aria-label="Workspace navigation">
            <a href="#dashboard" className="saas-nav-link"><span aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z" /></svg></span> Dashboard</a>
            <a href="#subjects" className="saas-nav-link"><span aria-hidden="true"><svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg></span> Subjects &amp; Uploads</a>
            <a href="#documents" className="saas-nav-link"><span aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M6 3h8l5 5v13H6z"/><path d="M14 3v6h5M9 13h7M9 17h7"/></svg></span> My Documents</a>
            <a href="#ai-chat" className="saas-nav-link"><span aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3v4m0 10v4M3 12h4m10 0h4M5.6 5.6l2.8 2.8m7.2 7.2 2.8 2.8m0-12.8-2.8 2.8m-7.2 7.2-2.8 2.8"/></svg></span> AI Study Chat</a>
          </nav>
          <div className="saas-sidebar-note">
            <span className="saas-note-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5z"/></svg></span>
            <strong>Your personal AI tutor</strong>
            <p>Learn from your own study material.</p>
          </div>
        </aside>
        <div className="saas-content">
          <main id="dashboard" className="max-w-7xl mx-auto px-6 py-8">
        {preferences && !preferences.onboarding_completed && (
          <section className="mb-8 rounded-2xl border border-indigo-100 bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-800">Personalize your learning</h2>
            <p className="mt-2 text-slate-500">Answer these four questions to tailor your study experience.</p>
            <form onSubmit={handleSaveOnboarding} className="mt-5 grid gap-5 md:grid-cols-2">
              <label className="block text-sm font-semibold text-slate-700">1. Your learning goal<select className="mt-2 w-full rounded-lg border p-3" value={onboardingAnswers.goal} onChange={e => setOnboardingAnswers({...onboardingAnswers, goal:e.target.value})}><option value="exam_preparation">Exam preparation</option><option value="concept_understanding">Understand concepts</option><option value="interview_prep">Interview preparation</option><option value="mixed">Mixed goals</option></select></label>
              <label className="block text-sm font-semibold text-slate-700">2. Current level<select className="mt-2 w-full rounded-lg border p-3" value={onboardingAnswers.level} onChange={e => setOnboardingAnswers({...onboardingAnswers, level:e.target.value})}><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select></label>
              <label className="block text-sm font-semibold text-slate-700">3. Explanation depth<select className="mt-2 w-full rounded-lg border p-3" value={onboardingAnswers.depth} onChange={e => setOnboardingAnswers({...onboardingAnswers, depth:e.target.value})}><option value="concise">Concise</option><option value="balanced">Balanced</option><option value="detailed">Detailed</option></select></label>
              <label className="block text-sm font-semibold text-slate-700">4. Teaching approach<select className="mt-2 w-full rounded-lg border p-3" value={onboardingAnswers.approach} onChange={e => setOnboardingAnswers({...onboardingAnswers, approach:e.target.value})}><option value="examples">Examples first</option><option value="step_by_step">Step by step</option><option value="analogy">Practical analogies</option><option value="mixed">Mix of approaches</option></select></label>
              <div className="md:col-span-2"><button type="submit" disabled={preferencesLoading} className="rounded-lg bg-indigo-600 px-5 py-3 font-semibold text-white disabled:opacity-50">{preferencesLoading ? 'Saving...' : 'Save learning profile'}</button>{preferencesMessage && <p className="mt-3 text-sm text-slate-600">{preferencesMessage}</p>}</div>
            </form>
          </section>
        )}

        {/* WELCOME */}

        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-800">
            Welcome back!
          </h2>

          <p className="text-slate-500 mt-2">
            Upload your study material and ask questions using your personalized AI assistant.
          </p>
        </div>


        {/* STATS */}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
            <p className="text-sm text-slate-500">
              Subjects
            </p>

            <p className="text-3xl font-bold text-indigo-600 mt-2">
              {subjects.length}
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
            <p className="text-sm text-slate-500">
              Documents
            </p>

            <p className="text-3xl font-bold text-indigo-600 mt-2">
              {documents.length}
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
            <p className="text-sm text-slate-500">
              Current Conversation
            </p>

            <p className="text-lg font-semibold text-slate-700 mt-3">
              {conversationId
                ? `#${conversationId}`
                : 'New'}
            </p>
          </div>

        </div>


        {/* SUBJECTS + DOCUMENT UPLOAD */}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">

          {/* SUBJECTS */}

          <section id="subjects" className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">

            <h2 className="text-xl font-bold text-slate-800 mb-1">
               Subjects
            </h2>

            <p className="text-sm text-slate-500 mb-5">
              Organize your study material by subject.
            </p>

            <div className="flex gap-2 mb-4">

              <input
                type="text"
                value={newSubject}
                onChange={(event) =>
                  setNewSubject(event.target.value)
                }
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    handleCreateSubject()
                  }
                }}
                placeholder="e.g. Computer Networks"
                className="flex-1 border border-slate-300 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-indigo-500"
              />

              <button
                onClick={handleCreateSubject}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 rounded-lg font-medium"
              >
                Add
              </button>

            </div>

            {subjectMessage && (
              <p className="text-sm text-slate-600 mb-4">
                {subjectMessage}
              </p>
            )}

            <div className="space-y-2 max-h-64 overflow-y-auto">

              {subjects.length === 0 ? (
                <p className="text-sm text-slate-400 py-4">
                  No subjects yet.
                </p>
              ) : (
                subjects.map((subject) => (
                  <div
                    key={subject.id}
                    className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                  >

                    <span className="font-medium text-slate-700">
                      {subject.name}
                    </span>

                    <button
                      onClick={() =>
                        handleDeleteSubject(
                          subject.id
                        )
                      }
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      Delete
                    </button>

                  </div>
                ))
              )}

            </div>

          </section>


          {/* DOCUMENT UPLOAD */}

          <section id="subjects" className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">

            <h2 className="text-xl font-bold text-slate-800 mb-1">
               Upload Study Material
            </h2>

            <p className="text-sm text-slate-500 mb-5">
              Add PDF or PPTX files to your personal knowledge base.
            </p>

            <div className="space-y-4">

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Subject
                </label>

                <select
                  value={selectedSubjectId}
                  onChange={(event) =>
                    setSelectedSubjectId(
                      event.target.value
                    )
                  }
                  className="w-full border border-slate-300 rounded-lg px-4 py-3 bg-white"
                >
                  <option value="">
                    No subject
                  </option>

                  {subjects.map((subject) => (
                    <option
                      key={subject.id}
                      value={subject.id}
                    >
                      {subject.name}
                    </option>
                  ))}
                </select>
              </div>


              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Document
                </label>

                <input
                  type="file"
                  accept=".pdf,.pptx"
                  onChange={handleFileChange}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2.5"
                />
              </div>


              {selectedFile && (
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg px-4 py-3">
                  <p className="font-medium text-indigo-800">
                    {selectedFile.name}
                  </p>

                  <p className="text-xs text-indigo-600 mt-1">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              )}


              {documentMessage && (
                <div className="bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-700">
                  {documentMessage}
                </div>
              )}


              <button
                onClick={handleDocumentUpload}
                disabled={
                  documentLoading ||
                  !selectedFile
                }
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white font-semibold rounded-lg py-3"
              >
                {documentLoading
                  ? 'Processing document...'
                  : 'Upload Document'}
              </button>

            </div>

          </section>

        </div>


        {/* DOCUMENT LIST */}

        <section id="documents" className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">

          <div className="flex items-center justify-between mb-5">

            <div>
              <h2 className="text-xl font-bold text-slate-800">
                 My Documents
              </h2>

              <p className="text-sm text-slate-500 mt-1">
                Documents available to your personalized RAG system.
              </p>
            </div>

          </div>


          {/* SEARCH AND SUBJECT FILTER */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
            <input
              type="search"
              value={documentSearch}
              onChange={(event) => setDocumentSearch(event.target.value)}
              placeholder="Search documents by filename..."
              aria-label="Search documents"
              className="w-full border border-slate-300 rounded-lg px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500"
            />

            <select
              value={documentSubjectFilter}
              onChange={(event) => setDocumentSubjectFilter(event.target.value)}
              aria-label="Filter documents by subject"
              className="w-full border border-slate-300 rounded-lg px-4 py-3 bg-white"
            >
              <option value="all">All subjects</option>
              <option value="none">No subject</option>

              {subjects.map((subject) => (
                <option key={subject.id} value={String(subject.id)}>
                  {subject.name}
                </option>
              ))}
            </select>
          </div>

          {filteredDocuments.length === 0 ? (
            <div className="text-center py-10 text-slate-400">
              {documents.length === 0 ? 'No documents uploaded yet.' : 'No documents match your search or subject filter.'}
            </div>
          ) : (
            <div className="space-y-3">

              {filteredDocuments.map((document) => (
                <div
                  key={document.id}
                  className="flex items-center justify-between border border-slate-200 rounded-lg px-4 py-4"
                >

                  <div>
                    <p className="font-semibold text-slate-700">
                      {document.filename}
                    </p>

                    <p className="text-xs text-slate-500 mt-1">
                      Document ID: {document.id}
                    </p>

                    {document.subject_id && (
                      <p className="text-xs text-indigo-600 mt-1">
                        Subject ID: {document.subject_id}
                      </p>
                    )}
                  </div>

                  <button
                    onClick={() =>
                      handleDeleteDocument(
                        document.id
                      )
                    }
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Delete
                  </button>

                </div>
              ))}

            </div>
          )}

        </section>


        {/* ============================= */}
        {/* AI CHAT */}
        {/* ============================= */}

        <section id="ai-chat" className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">

          {/* CHAT HEADER */}

          <div className="border-b border-slate-200 px-6 py-5 flex items-center justify-between">

            <div>
              <h2 className="text-2xl font-bold text-slate-800">
                 AI Study Chat
              </h2>

              <p className="text-sm text-slate-500 mt-1">
                Ask questions from your uploaded study materials.
              </p>
            </div>

            <button
              onClick={handleNewConversation}
              className="border border-slate-300 hover:bg-slate-50 text-slate-700 px-4 py-2 rounded-lg text-sm font-medium"
            >
              + New Chat
            </button>

          </div>


          {/* CHAT AREA */}

          <div className="h-[500px] overflow-y-auto bg-slate-50 px-6 py-6">

            {messages.length === 0 && (
              <div className="h-full flex items-center justify-center">

                <div className="text-center max-w-lg">

                  <div className="text-5xl mb-4">
                    <svg className="ui-feature-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v4m0 10v4M3 12h4m10 0h4M5.6 5.6l2.8 2.8m7.2 7.2 2.8 2.8m0-12.8-2.8 2.8m-7.2 7.2-2.8 2.8"/></svg> 
                  </div>

                  <h3 className="text-xl font-bold text-slate-700">
                    Ask your study assistant
                  </h3>

                  <p className="text-slate-500 mt-2">
                    Try questions like:
                  </p>

                  <div className="mt-4 space-y-2">
                    {/* PROMPT_BUTTONS_V1 */}

                    <button type="button" onClick={() => setQuestion('Explain this topic in simple language.')} className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-600 text-left shadow-sm transition hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400">Explain this topic in simple language.</button>

                    <button type="button" onClick={() => setQuestion('Give me a 5-mark exam answer.')} className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-600 text-left shadow-sm transition hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400">Give me a 5-mark exam answer.</button>

                    <button type="button" onClick={() => setQuestion('What are the important points from my notes?')} className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-600 text-left shadow-sm transition hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400">What are the important points from my notes?</button>

                  </div>

                </div>

              </div>
            )}


            <div className="space-y-5">

              {messages.map((message, index) => {

                const isUser =
                  message.role === 'user'

                return (
                  <div
                    key={index}
                    className={`flex ${
                      isUser
                        ? 'justify-end'
                        : 'justify-start'
                    }`}
                  >

                    <div
                      className={`max-w-[80%] rounded-2xl px-5 py-4 ${
                        isUser
                          ? 'bg-indigo-600 text-white'
                          : 'bg-white border border-slate-200 text-slate-700 shadow-sm'
                      }`}
                    >

                      <p className="text-xs font-semibold mb-2 opacity-70">
                        {isUser
                          ? 'You'
                          : 'StudyAI'}
                      </p>

                      <p className="whitespace-pre-wrap leading-relaxed">
                        {message.content}
                      </p>


                      {/* SOURCES */}

                      {!isUser &&
                        message.sources &&
                        message.sources.length > 0 && (

                          <div className="mt-4 pt-4 border-t border-slate-200">

                            <p className="text-xs font-semibold text-slate-500 mb-2">
                               Sources
                            </p>

                            <div className="space-y-2">

                              {message.sources.map(
                                (
                                  source,
                                  sourceIndex
                                ) => (

                                  <div
                                    key={
                                      sourceIndex
                                    }
                                    className="bg-slate-50 rounded-lg px-3 py-2 text-xs text-slate-600"
                                  >
                                    {typeof source ===
                                    'string'
                                      ? source
                                      : (
                                          source.filename ||
                                          source.document_name ||
                                          source.file_name ||
                                          `Source ${sourceIndex + 1}`
                                        )}
                                  </div>

                                )
                              )}

                            </div>

                          </div>

                        )}

                    </div>

                  </div>
                )
              })}


              {/* LOADING */}

              {chatLoading && (
                <div className="flex justify-start">

                  <div className="bg-white border border-slate-200 rounded-2xl px-5 py-4 shadow-sm">

                    <p className="text-xs font-semibold text-slate-500 mb-2">
                      StudyAI
                    </p>

                    <div className="flex items-center gap-2 text-slate-500 text-sm">
                      <span className="animate-pulse">
                        Thinking...
                      </span>
                    </div>

                  </div>

                </div>
              )}

              <div ref={chatEndRef} />

            </div>

          </div>


          {/* CHAT ERROR */}

          {chatMessage && (
            <div className="px-6 pt-4">

              <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg px-4 py-3 text-sm">
                {chatMessage}
              </div>

            </div>
          )}


          {/* CHAT INPUT */}

          <form
            onSubmit={handleAskQuestion}
            className="border-t border-slate-200 p-5"
          >

            <div className="flex gap-3">

              <input
                type="text"
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                placeholder="Ask a question about your study material..."
                disabled={chatLoading}
                className="flex-1 border border-slate-300 rounded-xl px-5 py-3.5 outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-slate-100"
              />

              <button
                type="submit"
                disabled={
                  chatLoading ||
                  !question.trim()
                }
                className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white font-semibold px-6 rounded-xl"
              >
                {chatLoading
                  ? '...'
                  : 'Send'}
              </button>

            </div>

            <p className="text-xs text-slate-400 mt-2">
              Press Enter to send your question.
            </p>

          </form>

        </section>

      </main>
        </div>
      </div>
    </div>
  )
}

export default App


















