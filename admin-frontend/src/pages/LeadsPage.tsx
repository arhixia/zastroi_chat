import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { ArrowLeft, Download, MessageSquareText, User, Bot } from "lucide-react"
import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"

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

interface Filters {
  name: string
  phone: string
  dateFrom: string
  dateTo: string
  jk: string
  obj: string
  conversationId: string
}

const emptyFilters: Filters = {
  name: "", phone: "", dateFrom: "", dateTo: "", jk: "", obj: "", conversationId: "",
}

function buildQuery(f: Filters) {
  const params = new URLSearchParams()
  if (f.name.trim()) params.set("name", f.name.trim())
  if (f.phone.trim()) params.set("phone", f.phone.trim())
  if (f.dateFrom) params.set("date_from", f.dateFrom)
  if (f.dateTo) params.set("date_to", f.dateTo)
  if (f.jk.trim()) params.set("jk", f.jk.trim())
  if (f.obj.trim()) params.set("obj", f.obj.trim())
  if (f.conversationId.trim()) params.set("conversation_id", f.conversationId.trim())
  const q = params.toString()
  return q ? `?${q}` : ""
}

export function LeadsPage() {
  const { logout } = useAuth()
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<Filters>(emptyFilters)
  const setFilter = (key: keyof Filters) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setFilters((f) => ({ ...f, [key]: e.target.value }))
  const hasFilters = Object.values(filters).some(Boolean)
  

  // Состояние для деталей заявки
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null)
  const [leadDetails, setLeadDetails] = useState<Lead | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loadingDetails, setLoadingDetails] = useState(false)

  async function loadLeads(f: Filters = filters) {
    setLoading(true)
    try {
      const data = await api.get<Lead[]>(`/api/v1/admin/leads${buildQuery(f)}`)
      setLeads(data)
    } catch {
      alert("Не удалось загрузить заявки")
    } finally {
      setLoading(false)
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    loadLeads()
  }

  function handleReset() {
    setFilters(emptyFilters)
    loadLeads(emptyFilters)
}

  async function openLeadDetails(leadId: string) {
    setSelectedLeadId(leadId)
    setLoadingDetails(true)
    try {
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
        <div className="flex items-center gap-3">
          <Link to="/sites">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="size-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-semibold">Заявки</h1>
            <p className="text-sm text-muted-foreground">Обращения клиентов со всех подключённых сайтов</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="size-4" />
            Скачать CSV
          </Button>
          <Button variant="outline" onClick={logout}>Выйти</Button>
        </div>
      </div>

      <Card className="mb-6">
  <CardContent className="pt-6">
<form onSubmit={handleSearch} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
  <Input placeholder="Имя" value={filters.name} onChange={setFilter("name")} />
  <Input placeholder="Телефон" value={filters.phone} onChange={setFilter("phone")} />
  <Input placeholder="ЖК (часть названия)" value={filters.jk} onChange={setFilter("jk")} />
  <Input placeholder="Объект (часть названия)" value={filters.obj} onChange={setFilter("obj")} />
  <div className="flex items-center gap-2">
    <span className="text-sm text-muted-foreground">с</span>
    <Input type="date" value={filters.dateFrom} onChange={setFilter("dateFrom")} />
  </div>
  <div className="flex items-center gap-2">
    <span className="text-sm text-muted-foreground">по</span>
    <Input type="date" value={filters.dateTo} onChange={setFilter("dateTo")} />
  </div>
  <Input placeholder="ID диалога" value={filters.conversationId} onChange={setFilter("conversationId")} />
  <div className="flex gap-2">
    <Button type="submit" variant="secondary">Найти</Button>
    {hasFilters && (
      <Button type="button" variant="ghost" onClick={handleReset}>Сбросить</Button>
    )}
  </div>
</form>
  </CardContent>
</Card>

      {loading ? (
        <p className="text-sm text-muted-foreground">Загрузка данных...</p>
      ) : leads.length === 0 ? (
        <div className="py-10 text-center text-sm text-muted-foreground">
          Заявок пока нет.
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Дата</TableHead>
                <TableHead>Сайт</TableHead>
                <TableHead>Имя</TableHead>
                <TableHead>Телефон</TableHead>
                <TableHead>Интерес</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {leads.map((lead) => (
                <TableRow key={lead.id}>
                  <TableCell className="text-muted-foreground">
                    {new Date(lead.created_at).toLocaleString("ru-RU")}
                  </TableCell>
                  <TableCell className="font-medium">{lead.site_name}</TableCell>
                  <TableCell>{lead.name}</TableCell>
                  <TableCell>
                    <a href={`tel:${lead.phone}`} className="text-primary hover:underline">
                      {lead.phone}
                    </a>
                  </TableCell>
                  <TableCell className="max-w-xs truncate text-muted-foreground">
                    {lead.interest?.last_question}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button size="sm" variant="outline" onClick={() => openLeadDetails(lead.id)}>
                      <MessageSquareText className="size-3.5" />
                      Диалог
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Модальное окно с историей диалога */}
      <Dialog open={!!selectedLeadId} onOpenChange={(open) => !open && setSelectedLeadId(null)}>
        <DialogContent className="flex max-h-[80vh] max-w-2xl flex-col">
          <DialogHeader>
            <DialogTitle>История диалога — {leadDetails?.name || "клиент"}</DialogTitle>
            <DialogDescription>
              {leadDetails?.phone} · {leadDetails?.site_name}
            </DialogDescription>
          </DialogHeader>

          <div className="-mx-6 flex-1 space-y-3 overflow-y-auto px-6">
            {loadingDetails ? (
              <p className="py-8 text-center text-sm text-muted-foreground">Загрузка истории...</p>
            ) : messages.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">Сообщений в этом диалоге нет.</p>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`max-w-[85%] rounded-lg p-3 text-sm ${
                    msg.role === 'user'
                      ? 'ml-auto rounded-br-none bg-primary text-primary-foreground'
                      : 'mr-auto rounded-bl-none bg-muted'
                  }`}
                >
                  <p className="mb-1 flex items-center gap-1.5 text-xs font-medium opacity-70">
                    {msg.role === 'user' ? <User className="size-3" /> : <Bot className="size-3" />}
                    {msg.role === 'user' ? 'Клиент' : 'Бот'}
                  </p>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  <p className="mt-1 text-right text-[10px] opacity-50">
                    {new Date(msg.created_at).toLocaleTimeString("ru-RU", { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              ))
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
