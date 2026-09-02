import { useEffect, useState, type FormEvent } from "react"
import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

interface DocumentOut {
  id: string;
  filename: string;
  file_type: string;
  status: string;
}

interface Site {
  id: string;
  name: string;
  domain: string;
  crawl_start_urls: string[];
  crawl_excluded_urls: string[];
  is_active: boolean;
  documents: DocumentOut[];
}

export function SitesPage() {
  const { logout } = useAuth()
  const [sites, setSites] = useState<Site[]>([])
  const [loading, setLoading] = useState(true)
  
  // Состояния для модалок
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [modalMode, setModalMode] = useState<"create" | "edit">("create")
  const [currentSite, setCurrentSite] = useState<Site | null>(null)
  const [snippet, setSnippet] = useState("")
  const [showSnippetModal, setShowSnippetModal] = useState(false)

  // Поля формы
  const [formData, setFormData] = useState({
    name: "",
    domain: "",
    startUrls: "",
    excludeUrls: ""
  })

  async function loadSites() {
    setLoading(true)
    try {
      const data = await api.get<Site[]>("/api/v1/admin/sites")
      setSites(data)
    } catch {
      alert("Не удалось загрузить список сайтов")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadSites() }, [])

  // --- Логика форм ---
  function openCreate() {
    setModalMode("create")
    setCurrentSite(null)
    setFormData({ name: "", domain: "", startUrls: "", excludeUrls: "" })
    setIsModalOpen(true)
  }

  function openEdit(site: Site) {
    setModalMode("edit")
    setCurrentSite(site)
    setFormData({
      name: site.name,
      domain: site.domain,
      startUrls: site.crawl_start_urls.join("\n"),
      excludeUrls: site.crawl_excluded_urls.join("\n")
    })
    setIsModalOpen(true)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const payload = {
      name: formData.name,
      ...(modalMode === "create" && { domain: formData.domain }),
      crawl_start_urls: formData.startUrls.split(/[\n,]/).map(s => s.trim()).filter(Boolean),
      crawl_excluded_urls: formData.excludeUrls.split(/[\n,]/).map(s => s.trim()).filter(Boolean)
    }

    try {
      if (modalMode === "create") {
        await api.post("/api/v1/admin/sites", payload)
      } else if (currentSite) {
        await api.patch(`/api/v1/admin/sites/${currentSite.id}`, payload)
      }
      setIsModalOpen(false)
      loadSites()
    } catch (err: any) {
      alert(err.message || "Ошибка сохранения")
    }
  }

  // --- Виджет и Файлы ---
  async function getSnippet(siteId: string) {
    const res = await api.get<{ snippet: string }>(`/api/v1/admin/sites/${siteId}/snippet`)
    setSnippet(res.snippet)
    setShowSnippetModal(true)
  }

  async function handleFileUpload(siteId: string, file: File) {
    const fd = new FormData()
    fd.append("file", file)
    try {
      await fetch(`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/v1/admin/sites/${siteId}/documents`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` },
        body: fd
      })
      alert("Файл загружен!")
      loadSites() // Обновляем список после загрузки
    } catch {
      alert("Ошибка загрузки")
    }
  }

  async function handleDeleteDocument(docId: string) {
    if (!confirm("Вы уверены, что хотите удалить этот документ из базы знаний?")) return
    
    try {
      // Используем наш универсальный эндпоинт удаления источников
      await api.delete(`/api/v1/admin/sources/${docId}?source_type=document`)
      loadSites()
    } catch (err: any) {
      alert(err.message || "Ошибка удаления")
    }
  }

  async function handleTriggerCrawl(siteId: string) {
    if (!confirm("Вы действительно хотите запустить полный парсинг сайта и обработку всех файлов?")) return
    
    try {
      await api.post(`/api/v1/admin/sites/${siteId}/crawl`)
      alert("Задача отправлена в очередь!")
    } catch (err: any) {
      alert(err.message || "Ошибка запуска")
    }
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Управление сайтами</h1>
        <Button variant="outline" onClick={logout}>Выйти</Button>
      </div>

      <Button onClick={openCreate} className="mb-6">Добавить сайт</Button>

      {loading ? <p>Загрузка...</p> : (
        <div className="grid gap-6 md:grid-cols-2">
          {sites.map((site) => (
            <Card key={site.id}>
              <CardHeader>
                <CardTitle>{site.name}</CardTitle>
                <CardDescription>{site.domain}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <Button size="sm" onClick={() => openEdit(site)}>✏️ Изменить</Button>
                  <Button size="sm" variant="outline" onClick={() => getSnippet(site.id)}>📋 Код виджета</Button>
                </div>
                
                <div className="pt-2 border-t">
                  <Label className="text-xs font-bold mb-2 block">База знаний (Файлы):</Label>
                  {site.documents && site.documents.length > 0 ? (
                    <ul className="text-xs space-y-2 mb-3 max-h-40 overflow-y-auto pr-1">
                      {site.documents.map(doc => (
                        <li key={doc.id} className="flex items-center justify-between bg-muted p-2 rounded group">
                          <div className="flex items-center gap-2 truncate">
                            <span>📄</span>
                            <span className="truncate font-medium">{doc.filename}</span>
                          </div>
                          <button 
                            onClick={() => handleDeleteDocument(doc.id)}
                            className="text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100 transition-opacity px-2"
                            title="Удалить документ"
                          >
                            ✕
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-xs text-muted-foreground mb-3 italic">Нет загруженных файлов</p>
                  )}

                  <Label className="text-xs text-muted-foreground mb-1 block">Загрузить новый файл:</Label>
                  <Input 
                    type="file" 
                    accept=".pdf,.docx,.xlsx,.txt"
                    onChange={(e) => e.target.files?.[0] && handleFileUpload(site.id, e.target.files[0])} 
                  />
                </div>

                <Button 
                  size="sm" 
                  variant="secondary" 
                  className="w-full mt-2"
                  onClick={() => handleTriggerCrawl(site.id)}
                >
                Запустить полный парсинг
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Модалка Создания/Редактирования */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">{modalMode === "create" ? "Новый сайт" : "Редактирование"}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label>Название</Label>
                <Input value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
              </div>
              {modalMode === "create" && (
                <div>
                  <Label>Домен</Label>
                  <Input value={formData.domain} onChange={e => setFormData({...formData, domain: e.target.value})} required />
                </div>
              )}
              <div>
                <Label>Стартовые URL (через запятую)</Label>
                <Input value={formData.startUrls} onChange={e => setFormData({...formData, startUrls: e.target.value})} placeholder="https://..." />
              </div>
              <div>
                <Label>Исключить URL</Label>
                <Input value={formData.excludeUrls} onChange={e => setFormData({...formData, excludeUrls: e.target.value})} placeholder="/news, /vacancies" />
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Отмена</Button>
                <Button type="submit">Сохранить</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модалка Кода Виджета */}
      {showSnippetModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-lg">
            <h2 className="text-xl font-bold mb-2">Код для вставки</h2>
            <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto mb-4 whitespace-pre-wrap">{snippet}</pre>
            <div className="flex justify-end gap-2">
              <Button onClick={() => navigator.clipboard.writeText(snippet)}>Копировать</Button>
              <Button variant="outline" onClick={() => setShowSnippetModal(false)}>Закрыть</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}