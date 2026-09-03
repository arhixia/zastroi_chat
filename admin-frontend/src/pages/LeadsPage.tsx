import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"

// --- Интерфейсы для типизации ---

interface Lead {
  id: string;
  site_name: string;
  name: string;
  phone: string;
  interest: { last_question?: string };
  created_at: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface LeadDetailsResponse {
  lead: Lead;
  messages: Message[];
}

export function LeadsPage() {
  const { logout } = useAuth()
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [searchPhone, setSearchPhone] = useState("")
  
  // Состояние для деталей заявки
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null)
  const [leadDetails, setLeadDetails] = useState<Lead | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loadingDetails, setLoadingDetails] = useState(false)

  async function loadLeads(phone?: string) {
    setLoading(true)
    try {
      const url = phone ? `/api/v1/admin/leads?phone=${phone}` : "/api/v1/admin/leads"
      // Явно указываем тип ответа: массив лидов
      const data = await api.get<Lead[]>(url)
      setLeads(data)
    } catch {
      alert("Не удалось загрузить заявки")
    } finally {
      setLoading(false)
    }
  }

  async function openLeadDetails(leadId: string) {
    setSelectedLeadId(leadId)
    setLoadingDetails(true)
    try {
      // Явно указываем тип ответа: объект с деталями
      const data = await api.get<LeadDetailsResponse>(`/api/v1/admin/leads/${leadId}/details`)
      setLeadDetails(data.lead)
      setMessages(data.messages || [])
    } catch {
      alert("Не удалось загрузить историю диалога")
    } finally {
      setLoadingDetails(false)
    }
  }

  useEffect(() => { loadLeads() }, [])

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    loadLeads(searchPhone)
  }

    async function handleExport() {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/v1/admin/leads/export/csv`, 
        {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`
          }
        }
      )

      if (!response.ok) throw new Error("Ошибка экспорта")
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      
      const a = document.createElement("a")
      a.style.display = "none"
      a.href = url
      a.download = "leads_export.csv" 
      document.body.appendChild(a)
      a.click()
      

      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
    } catch (err) {
      alert("Не удалось скачать файл. Проверьте подключение.")
    }
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/sites">
            <Button variant="ghost" size="sm">← Назад к сайтам</Button>
          </Link>
          <h1 className="text-2xl font-bold">Заявки от клиентов</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>📥 Скачать CSV</Button>
          <Button variant="outline" onClick={logout}>Выйти</Button>
        </div>
      </div>

      {/* Поиск */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <Input 
              placeholder="Поиск по номеру телефона..." 
              value={searchPhone}
              onChange={(e) => setSearchPhone(e.target.value)}
              className="max-w-sm"
            />
            <Button type="submit">Найти</Button>
            {searchPhone && (
              <Button type="button" variant="ghost" onClick={() => { setSearchPhone(""); loadLeads(); }}>
                Сбросить
              </Button>
            )}
          </form>
        </CardContent>
      </Card>

      {/* Таблица заявок */}
      {loading ? (
        <p>Загрузка данных...</p>
      ) : leads.length === 0 ? (
        <div className="text-center py-10 text-muted-foreground">
          Заявок пока нет.
        </div>
      ) : (
        <div className="rounded-md border">
          <table className="w-full text-sm">
            <thead className="bg-muted">
              <tr>
                <th className="p-3 text-left font-medium">Дата</th>
                <th className="p-3 text-left font-medium">Сайт</th>
                <th className="p-3 text-left font-medium">Имя</th>
                <th className="p-3 text-left font-medium">Телефон</th>
                <th className="p-3 text-left font-medium">Интерес</th>
                <th className="p-3 text-left font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id} className="border-t hover:bg-muted/50">
                  <td className="p-3 text-muted-foreground">
                    {new Date(lead.created_at).toLocaleString("ru-RU")}
                  </td>
                  <td className="p-3 font-medium">{lead.site_name}</td>
                  <td className="p-3">{lead.name}</td>
                  <td className="p-3">
                    <a href={`tel:${lead.phone}`} className="text-blue-600 hover:underline">
                      {lead.phone}
                    </a>
                  </td>
                  <td className="p-3 max-w-xs truncate">{lead.interest?.last_question}</td>
                  <td className="p-3 text-right">
                    <Button size="sm" variant="outline" onClick={() => openLeadDetails(lead.id)}>
                      История диалога
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Модальное окно с историей диалога */}
      {selectedLeadId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[80vh] flex flex-col shadow-xl">
            <div className="p-4 border-b flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold">
                  История диалога: {leadDetails?.name || "Клиент"}
                </h2>
                <p className="text-sm text-muted-foreground">
                  Телефон: {leadDetails?.phone} | Сайт: {leadDetails?.site_name}
                </p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setSelectedLeadId(null)}>
                ✕
              </Button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {loadingDetails ? (
                <p className="text-center text-muted-foreground py-8">Загрузка истории...</p>
              ) : messages.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">Сообщений в этом диалоге нет.</p>
              ) : (
                messages.map((msg) => (
                  <div 
                    key={msg.id} 
                    className={`p-3 rounded-lg text-sm max-w-[85%] ${
                      msg.role === 'user' 
                        ? 'bg-blue-600 text-white ml-auto rounded-br-none' 
                        : 'bg-gray-100 text-gray-900 mr-auto rounded-bl-none'
                    }`}
                  >
                    <p className="font-bold text-xs mb-1 opacity-70">
                      {msg.role === 'user' ? '👤 Клиент' : '🤖 Бот'}
                    </p>
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <p className="text-[10px] mt-1 opacity-50 text-right">
                      {new Date(msg.created_at).toLocaleTimeString("ru-RU", { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="p-3 border-t bg-gray-50 rounded-b-lg text-center">
              <Button variant="outline" size="sm" onClick={() => setSelectedLeadId(null)}>
                Закрыть
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}