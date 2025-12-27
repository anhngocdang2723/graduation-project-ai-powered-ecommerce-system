import { defineRouteConfig } from "@medusajs/admin-sdk"
import { ChatBubbleLeftRight } from "@medusajs/icons"
import { Container, Heading, Text, Table, Badge, Button, Tabs } from "@medusajs/ui"
import { useState, useEffect } from "react"

interface ChatSession {
  id: string
  session_id: string
  customer_id?: string
  customer_email?: string
  status: string
  created_at: string
  updated_at: string
  message_count?: number
  last_message?: string
}

interface ChatMessage {
  id: string
  role: string
  content: string
  timestamp: string
  intent?: string
  products?: any[]
}

const ChatbotPage = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [selectedSession, setSelectedSession] = useState<ChatSession | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [stats, setStats] = useState({
    total_sessions: 0,
    active_sessions: 0,
    escalated_sessions: 0,
    total_messages: 0
  })
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("all")

  useEffect(() => {
    loadSessions()
    loadStats()
  }, [])

  const loadSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/admin/sessions')
      if (response.ok) {
        const data = await response.json()
        setSessions(data.sessions || [])
      }
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/admin/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  const loadSessionMessages = async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/chat/history/${sessionId}`)
      if (response.ok) {
        const data = await response.json()
        setMessages(data.messages || [])
      }
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }

  const handleSessionClick = (session: ChatSession) => {
    setSelectedSession(session)
    loadSessionMessages(session.session_id)
  }

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      active: "green",
      waiting_for_staff: "orange",
      resolved: "blue",
      closed: "grey"
    }
    return (
      <Badge color={statusColors[status] || "default"}>
        {status.replace(/_/g, ' ').toUpperCase()}
      </Badge>
    )
  }

  const filteredSessions = sessions.filter(session => {
    if (activeTab === "all") return true
    if (activeTab === "active") return session.status === "active"
    if (activeTab === "escalated") return session.status === "waiting_for_staff"
    if (activeTab === "resolved") return session.status === "resolved" || session.status === "closed"
    return true
  })

  return (
    <div className="flex h-screen">
      {/* Left Panel - Sessions List */}
      <div className="w-1/3 border-r overflow-y-auto">
        <Container className="p-6">
          <Heading level="h1" className="mb-4">Chatbot Management</Heading>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <Text className="text-sm text-gray-600">Total Sessions</Text>
              <Text className="text-2xl font-bold">{stats.total_sessions}</Text>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <Text className="text-sm text-gray-600">Active</Text>
              <Text className="text-2xl font-bold">{stats.active_sessions}</Text>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <Text className="text-sm text-gray-600">Escalated</Text>
              <Text className="text-2xl font-bold">{stats.escalated_sessions}</Text>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <Text className="text-sm text-gray-600">Total Messages</Text>
              <Text className="text-2xl font-bold">{stats.total_messages}</Text>
            </div>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-4">
            <Tabs.List>
              <Tabs.Trigger value="all">All</Tabs.Trigger>
              <Tabs.Trigger value="active">Active</Tabs.Trigger>
              <Tabs.Trigger value="escalated">Escalated</Tabs.Trigger>
              <Tabs.Trigger value="resolved">Resolved</Tabs.Trigger>
            </Tabs.List>
          </Tabs>

          {/* Sessions List */}
          <div className="space-y-2">
            {filteredSessions.map((session) => (
              <div
                key={session.id}
                onClick={() => handleSessionClick(session)}
                className={`p-4 border rounded-lg cursor-pointer hover:bg-gray-50 ${
                  selectedSession?.id === session.id ? 'bg-blue-50 border-blue-500' : ''
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <Text className="font-medium truncate">
                    {session.customer_email || `Session ${session.session_id.slice(0, 8)}`}
                  </Text>
                  {getStatusBadge(session.status)}
                </div>
                <Text className="text-xs text-gray-500 mb-1">
                  {session.message_count || 0} messages
                </Text>
                <Text className="text-xs text-gray-400">
                  {new Date(session.created_at).toLocaleString('vi-VN')}
                </Text>
              </div>
            ))}
          </div>
        </Container>
      </div>

      {/* Right Panel - Conversation View */}
      <div className="flex-1 flex flex-col">
        {selectedSession ? (
          <>
            {/* Conversation Header */}
            <div className="border-b p-6">
              <div className="flex justify-between items-start">
                <div>
                  <Heading level="h2">
                    {selectedSession.customer_email || `Session ${selectedSession.session_id.slice(0, 12)}`}
                  </Heading>
                  <Text className="text-sm text-gray-500">
                    Started: {new Date(selectedSession.created_at).toLocaleString('vi-VN')}
                  </Text>
                </div>
                <div className="flex gap-2">
                  {getStatusBadge(selectedSession.status)}
                  {selectedSession.status === "waiting_for_staff" && (
                    <Button size="small" variant="secondary">Take Over</Button>
                  )}
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : message.role === 'system'
                        ? 'bg-orange-100 text-orange-900 border border-orange-300'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Text className={`text-xs font-medium ${message.role === 'user' ? 'text-blue-200' : 'text-gray-500'}`}>
                        {message.role === 'user' ? 'Customer' : message.role === 'system' ? 'System' : 'AI Assistant'}
                      </Text>
                      {message.intent && (
                        <Badge size="2xsmall">{message.intent}</Badge>
                      )}
                    </div>
                    <Text className="whitespace-pre-wrap">{message.content}</Text>
                    <Text className={`text-xs mt-2 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-400'}`}>
                      {new Date(message.timestamp).toLocaleTimeString('vi-VN')}
                    </Text>
                    
                    {/* Show products if any */}
                    {message.products && message.products.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {message.products.map((product: any, idx: number) => (
                          <div key={idx} className="bg-white p-2 rounded border text-sm">
                            <Text className="font-medium text-gray-900">{product.title}</Text>
                            <Text className="text-xs text-gray-600">
                              {product.price} {product.currency_code?.toUpperCase()}
                            </Text>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <ChatBubbleLeftRight className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <Text className="text-gray-500">Select a session to view conversation</Text>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export const config = defineRouteConfig({
  label: "Chatbot",
  icon: ChatBubbleLeftRight,
})

export default ChatbotPage
