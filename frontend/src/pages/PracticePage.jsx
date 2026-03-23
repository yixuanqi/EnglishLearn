import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'
import './PracticePage.css'

const API_BASE = 'http://localhost:8000/api/v1'

export default function PracticePage() {
  const { scenarioId } = useParams()
  const navigate = useNavigate()
  const { token } = useAuth()

  const [scenario, setScenario] = useState(null)
  const [session, setSession] = useState(null)
  const [currentTurn, setCurrentTurn] = useState(0)
  const [isRecording, setIsRecording] = useState(false)
  const [transcription, setTranscription] = useState('')
  const [feedback, setFeedback] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [recordingStatus, setRecordingStatus] = useState('idle')
  const [audioLevel, setAudioLevel] = useState(0)

  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const recognitionRef = useRef(null)
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)
  const animationFrameRef = useRef(null)
  const streamRef = useRef(null)

  useEffect(() => {
    if (scenarioId) {
      fetchScenario()
      startSession()
    }
    return () => {
      stopRecording()
    }
  }, [scenarioId])

  const fetchScenario = async () => {
    try {
      const response = await axios.get(`${API_BASE}/scenarios/${scenarioId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setScenario(response.data)
    } catch (error) {
      console.error('Failed to fetch scenario:', error)
    }
  }

  const startSession = async () => {
    try {
      setLoading(true)
      const response = await axios.post(
        `${API_BASE}/practice/start`,
        { scenario_id: scenarioId },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      setSession(response.data)
      setCurrentTurn(response.data.current_turn)
    } catch (error) {
      console.error('Failed to start session:', error)
    } finally {
      setLoading(false)
    }
  }

  const initSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      console.warn('Speech recognition not supported')
      return null
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onresult = (event) => {
      let finalTranscript = ''
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' '
        } else {
          interimTranscript += transcript
        }
      }

      if (finalTranscript) {
        setTranscription(prev => prev + finalTranscript)
      }
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      if (event.error !== 'no-speech' && event.error !== 'aborted') {
        setRecordingStatus('error')
      }
    }

    recognition.onend = () => {
      if (isRecording && recordingStatus === 'recording') {
        try {
          recognition.start()
        } catch (e) {
          console.error('Failed to restart recognition:', e)
        }
      }
    }

    return recognition
  }

  const initAudioAnalysis = (stream) => {
    audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
    analyserRef.current = audioContextRef.current.createAnalyser()
    const source = audioContextRef.current.createMediaStreamSource(stream)
    source.connect(analyserRef.current)
    analyserRef.current.fftSize = 256

    const bufferLength = analyserRef.current.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)

    const updateLevel = () => {
      if (!analyserRef.current) return

      analyserRef.current.getByteFrequencyData(dataArray)
      const average = dataArray.reduce((a, b) => a + b) / bufferLength
      setAudioLevel(Math.min(100, (average / 128) * 100))

      if (isRecording) {
        animationFrameRef.current = requestAnimationFrame(updateLevel)
      }
    }

    updateLevel()
  }

  const startRecording = async () => {
    try {
      setRecordingStatus('requesting')
      setTranscription('')
      setFeedback(null)

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        } 
      })
      streamRef.current = stream

      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorderRef.current.start(100)
      setIsRecording(true)
      setRecordingStatus('recording')

      if (!recognitionRef.current) {
        recognitionRef.current = initSpeechRecognition()
      }

      if (recognitionRef.current) {
        try {
          recognitionRef.current.start()
        } catch (e) {
          console.warn('Could not start speech recognition:', e)
        }
      }

      initAudioAnalysis(stream)

    } catch (error) {
      console.error('Failed to start recording:', error)
      setRecordingStatus('error')
      alert('Could not access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch (e) {
        // Ignore
      }
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }

    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }

    setAudioLevel(0)
  }

  const handleRecord = async () => {
    if (!isRecording) {
      await startRecording()
    } else {
      stopRecording()
      setIsRecording(false)
      setRecordingStatus('processing')

      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
      const reader = new FileReader()
      reader.onloadend = () => {
        const base64Audio = reader.result.split(',')[1]
        if (transcription.trim()) {
          handleSubmitWithText(transcription.trim())
        } else {
          setRecordingStatus('no-speech')
        }
      }
      reader.readAsDataURL(audioBlob)
    }
  }

  const handleSubmitWithText = async (text) => {
    if (!text.trim()) return

    try {
      setSubmitting(true)
      setRecordingStatus('submitting')

      const response = await axios.post(
        `${API_BASE}/practice/submit`,
        {
          session_id: session.session_id,
          transcription: text,
          pronunciation_score: Math.floor(Math.random() * 20) + 80,
          accuracy_score: Math.floor(Math.random() * 20) + 80,
          fluency_score: Math.floor(Math.random() * 20) + 80,
          completeness_score: Math.floor(Math.random() * 20) + 80,
          feedback: {
            pronunciation: 'Good pronunciation overall. Pay attention to the "th" sound.',
            fluency: 'Your fluency is improving. Try to speak more naturally.',
            vocabulary: 'Great use of vocabulary in this context.',
            tips: 'Practice the dialogue a few more times to improve confidence.'
          }
        },
        { headers: { Authorization: `Bearer ${token}` } }
      )

      setFeedback(response.data.feedback)
      setCurrentTurn(response.data.next_turn)
      setRecordingStatus('completed')

      if (response.data.is_completed) {
        setCompleted(true)
      }
    } catch (error) {
      console.error('Failed to submit practice:', error)
      setRecordingStatus('error')
    } finally {
      setSubmitting(false)
    }
  }

  const handleNext = () => {
    setFeedback(null)
    setTranscription('')
    setRecordingStatus('idle')
    audioChunksRef.current = []
  }

  const handleFinish = () => {
    stopRecording()
    navigate('/dashboard')
  }

  const renderRecordingButton = () => {
    const buttonClass = `btn-record ${isRecording ? 'recording' : ''}`

    if (recordingStatus === 'requesting' || recordingStatus === 'submitting' || recordingStatus === 'processing') {
      return (
        <button className={`btn-record ${buttonClass}`} disabled>
          <span className="recording-spinner"></span>
          {recordingStatus === 'requesting' && 'Requesting microphone...'}
          {recordingStatus === 'processing' && 'Processing...'}
          {recordingStatus === 'submitting' && 'Submitting...'}
        </button>
      )
    }

    if (recordingStatus === 'no-speech') {
      return (
        <div className="recording-actions">
          <p className="no-speech-message">No speech detected. Try again?</p>
          <button onClick={handleRecord} className="btn-record">
            🎤 Try Again
          </button>
        </div>
      )
    }

    return (
      <button onClick={handleRecord} className={buttonClass}>
        {isRecording ? (
          <>
            <span className="recording-indicator"></span>
            <span>🌿 Stop Recording</span>
          </>
        ) : (
          <span>🎤 Start Recording</span>
        )}
      </button>
    )
  }

  if (loading) {
    return (
      <div className="practice-page loading">
        <div className="loading-spinner"></div>
        <p>Loading practice session...</p>
      </div>
    )
  }

  if (completed) {
    return (
      <div className="practice-page">
        <div className="container">
          <div className="completion-card">
            <div className="completion-icon">🌿</div>
            <h1>Practice Complete!</h1>
            <p>Great job! You've completed this practice session in the forest.</p>

            <div className="score-summary">
              <div className="score-item">
                <div className="score-value">87</div>
                <div className="score-label">Overall Score</div>
              </div>
              <div className="score-item">
                <div className="score-value">92</div>
                <div className="score-label">Pronunciation</div>
              </div>
              <div className="score-item">
                <div className="score-value">85</div>
                <div className="score-label">Fluency</div>
              </div>
              <div className="score-item">
                <div className="score-value">88</div>
                <div className="score-label">Accuracy</div>
              </div>
            </div>

            <button onClick={handleFinish} className="btn btn-primary btn-large">
              🏠 Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="practice-page">
      <div className="container">
        <div className="practice-header">
          <button onClick={handleFinish} className="btn-back">
            ← Back
          </button>
          <div className="scenario-title">
            <h1>{scenario?.title}</h1>
            <span className="turn-counter">
              Turn {currentTurn + 1} of {session?.total_turns || 0}
            </span>
          </div>
        </div>

        <div className="practice-content">
          <div className="dialogue-section">
            <div className="dialogue-card">
              <div className="dialogue-header">
                <div className="speaker-avatar ai">
                  <span>AI</span>
                </div>
                <div className="speaker-info">
                  <h3>{scenario?.ai_role || 'AI Assistant'}</h3>
                  <span className="speaker-role">Conversation Partner</span>
                </div>
              </div>
              <div className="dialogue-message">
                {session?.dialogue?.[currentTurn * 2]?.text || "Hello! How can I help you practice your English today?"}
              </div>
            </div>

            <div className="dialogue-card user">
              <div className="dialogue-header">
                <div className="speaker-avatar user">
                  <span>You</span>
                </div>
                <div className="speaker-info">
                  <h3>{scenario?.user_role || 'Student'}</h3>
                  <span className="speaker-role">Your Turn</span>
                </div>
              </div>
              <div className="dialogue-message">
                {session?.dialogue?.[currentTurn * 2 + 1]?.text || "Your response will appear here..."}
              </div>
            </div>
          </div>

          <div className="practice-section">
            {feedback ? (
              <div className="feedback-card">
                <div className="feedback-header">
                  <h3>🌿 Feedback</h3>
                  <span className="feedback-score">87/100</span>
                </div>
                <div className="feedback-content">
                  <div className="feedback-item">
                    <span className="feedback-icon">🌱</span>
                    <p>{feedback.pronunciation || 'Good pronunciation!'}</p>
                  </div>
                  <div className="feedback-item">
                    <span className="feedback-icon">🍃</span>
                    <p>{feedback.fluency || 'Great fluency!'}</p>
                  </div>
                  <div className="feedback-item">
                    <span className="feedback-icon">🌳</span>
                    <p>{feedback.tips || 'Keep practicing!'}</p>
                  </div>
                </div>
                <button onClick={handleNext} className="btn btn-primary btn-full">
                  🌱 Next Turn →
                </button>
              </div>
            ) : (
              <>
                <div className="recording-card">
                  <div className="recording-status">
                    {recordingStatus === 'recording' && (
                      <div className="recording-live">
                        <span className="recording-dot"></span>
                        Recording
                      </div>
                    )}
                  </div>

                  <div className="audio-visualizer">
                    {isRecording && (
                      <div className="wave-animation">
                        {[...Array(12)].map((_, i) => (
                          <div 
                            key={i} 
                            className="wave-bar"
                            style={{
                              animationDelay: `${i * 0.1}s`,
                              height: `${20 + Math.random() * 40}%`
                            }}
                          ></div>
                        ))}
                      </div>
                    )}
                    {!isRecording && recordingStatus === 'idle' && (
                      <div className="idle-visualizer">
                        <div className="idle-circle">🎤</div>
                        <p>Tap the button below to start speaking</p>
                      </div>
                    )}
                  </div>

                  <div className="transcription-area">
                    <textarea
                      className="input transcription-input"
                      placeholder="Your speech will appear here as you speak..."
                      value={transcription}
                      onChange={(e) => setTranscription(e.target.value)}
                      rows={4}
                    />
                  </div>

                  <div className="recording-controls">
                    {renderRecordingButton()}
                  </div>
                </div>

                <div className="tips-card">
                  <h4>🌿 Tips for this turn</h4>
                  <ul>
                    <li>Speak clearly and at a natural pace</li>
                    <li>Focus on proper pronunciation</li>
                    <li>Use the vocabulary from this scenario</li>
                  </ul>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}