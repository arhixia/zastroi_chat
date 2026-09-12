import { useEffect, useState, type FormEvent } from "react"
import { Link } from "react-router-dom"
import {
  ClipboardList,
  Code2,
  FileText,
  Paintbrush,
  Pencil,
  Play,
  Plus,
  Power,
  PowerOff,
  Upload,
  X,
} from "lucide-react"
import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"

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
  widget_logo_url: string | null;
  widget_primary_color: string;
  widget_bot_name: string;
  widget_welcome_message: string;
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
  const [isWidgetModalOpen, setIsWidgetModalOpen] = useState(false)
  const [widgetSite, setWidgetSite] = useState<Site | null>(null)
  const [widgetFormData, setWidgetFormData] = useState({
    widget_bot_name: "",
    widget_welcome_message: "",
    widget_primary_color: "#2563eb",
    widget_logo_url: "",
  })
  const [savingWidget, setSavingWidget] = useState(false)

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

function openWidgetSettings(site: Site) {
  setWidgetSite(site)
  setWidgetFormData({
    widget_bot_name: site.widget_bot_name || "",
    widget_welcome_message: site.widget_welcome_message || "",
    widget_primary_color: site.widget_primary_color || "#2563eb",
    widget_logo_url: site.widget_logo_url || "",
  })
  setIsWidgetModalOpen(true)
}

async function handleWidgetSubmit(e: FormEvent) {
  e.preventDefault()
  if (!widgetSite) return

  setSavingWidget(true)
  try {
    await api.patch(`/api/v1/admin/sites/${widgetSite.id}`, {
      widget_bot_name: widgetFormData.widget_bot_name,
      widget_welcome_message: widgetFormData.widget_welcome_message,
      widget_primary_color: widgetFormData.widget_primary_color,
      widget_logo_url: widgetFormData.widget_logo_url || null,
    })
    setIsWidgetModalOpen(false)
    loadSites()
  } catch (err: any) {
    const message = err?.response?.data?.detail || err.message || "Ошибка сохранения настроек виджета"
    alert(message)
  } finally {
    setSavingWidget(false)
  }
}

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const payload = {
    name: formData.name,
    domain: formData.domain,
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
    const message = err?.response?.data?.detail || err.message || "Ошибка сохранения"
    alert(message)
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
      loadSites()
    } catch {
      alert("Ошибка загрузки")
    }
  }

  async function handleDeleteDocument(docId: string) {
    if (!confirm("Вы уверены, что хотите удалить этот документ из базы знаний?")) return

    try {
      await api.delete(`/api/v1/admin/sources/${docId}?source_type=document`)

      setSites(prevSites => prevSites.map(site => ({
        ...site,
        documents: site.documents.filter(doc => doc.id !== docId)
      })))

      loadSites()
    } catch (err: any) {
      alert(err.message || "Ошибка удаления")
    }
  }

  async function handleTriggerCrawl(siteId: string) {
    if (!confirm("Вы действительно хотите запустить полный парсинг сайта и обработку всех файлов?")) return

    try {
      await api.post(`/api/v1/admin/sites/${siteId}/crawl`)
      alert("Парсинг запущен!")
    } catch (err: any) {
      alert(err.message || "Ошибка запуска")
    }
  }

  async function handleToggleActive(site: Site) {
  const action = site.is_active ? "отключить" : "включить"
  if (!confirm(`Вы действительно хотите ${action} сайт «${site.name}»?`)) return

  try {
    await api.patch(`/api/v1/admin/sites/${site.id}`, { is_active: !site.is_active })
    loadSites()
  } catch (err: any) {
    alert(err.message || "Ошибка изменения статуса сайта")
  }
}

  return (
    <div className="mx-auto max-w-6xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Сайты</h1>
          <p className="text-sm text-muted-foreground">Управление подключёнными сайтами застройщика</p>
        </div>
        <div className="flex gap-2">
          <Link to="/leads">
            <Button variant="secondary">
              <ClipboardList className="size-4" />
              Заявки
            </Button>
          </Link>
          <Button variant="outline" onClick={logout}>Выйти</Button>
        </div>
      </div>

      <Button onClick={openCreate} className="mb-6">
        <Plus className="size-4" />
        Добавить сайт
      </Button>

      {loading ? (
        <p className="text-sm text-muted-foreground">Загрузка...</p>
      ) : sites.length === 0 ? (
        <p className="text-sm text-muted-foreground">Сайтов пока нет — добавьте первый.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {sites.map((site) => (
            <Card key={site.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <CardTitle>{site.name}</CardTitle>
                    <CardDescription>{site.domain}</CardDescription>
                  </div>
                  <Badge variant={site.is_active ? "success" : "warning"}>
                    {site.is_active ? "Активен" : "Отключён"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <Button size="sm" variant="outline" onClick={() => openEdit(site)}>
                    <Pencil className="size-3.5" />
                    Изменить
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => openWidgetSettings(site)}>
                    <Paintbrush className="size-3.5" />
                    Настроить виджет
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => getSnippet(site.id)}>
                    <Code2 className="size-3.5" />
                    Код виджета
                  </Button>
                  <Button
                    size="sm"
                    variant={site.is_active ? "outline" : "secondary"}
                    onClick={() => handleToggleActive(site)}
                  >
                    {site.is_active ? (
                      <>
                        <PowerOff className="size-3.5" />
                        Отключить
                      </>
                    ) : (
                      <>
                        <Power className="size-3.5" />
                        Включить
                      </>
                    )}
                  </Button>
                </div>

                <div className="border-t pt-4">
                  <Label className="mb-2 block text-xs font-medium text-muted-foreground">
                    База знаний · документы
                  </Label>
                  {site.documents && site.documents.length > 0 ? (
                    <ul className="mb-3 max-h-40 space-y-1.5 overflow-y-auto pr-1">
                      {site.documents.map(doc => (
                        <li
                          key={doc.id}
                          className="group flex items-center justify-between gap-2 rounded-md bg-muted/60 px-2.5 py-1.5 text-xs"
                        >
                          <div className="flex min-w-0 items-center gap-2">
                            <FileText className="size-3.5 shrink-0 text-muted-foreground" />
                            <span className="truncate font-medium">{doc.filename}</span>
                          </div>
                          <button
                            onClick={() => handleDeleteDocument(doc.id)}
                            className="shrink-0 rounded p-1 text-muted-foreground opacity-0 transition-opacity hover:bg-destructive/10 hover:text-destructive group-hover:opacity-100"
                            title="Удалить документ"
                            aria-label="Удалить документ"
                          >
                            <X className="size-3.5" />
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mb-3 text-xs italic text-muted-foreground">Нет загруженных файлов</p>
                  )}

                  <Label htmlFor={`upload-${site.id}`} className="mb-1.5 flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Upload className="size-3.5" />
                    Загрузить новый файл
                  </Label>
                  <Input
                    id={`upload-${site.id}`}
                    type="file"
                    accept=".pdf,.docx,.xlsx,.txt"
                    onChange={(e) => e.target.files?.[0] && handleFileUpload(site.id, e.target.files[0])}
                  />
                </div>

                <Button
                  size="sm"
                  variant="secondary"
                  className="w-full"
                  onClick={() => handleTriggerCrawl(site.id)}
                >
                  <Play className="size-3.5" />
                  Запустить полный парсинг
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Модалка создания/редактирования */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{modalMode === "create" ? "Новый сайт" : "Редактирование сайта"}</DialogTitle>
            <DialogDescription>
              {modalMode === "create"
                ? "Укажите домен и, при необходимости, стартовые URL для парсинга."
                : "Измените настройки сайта и правила парсинга."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label>Название</Label>
              <Input value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required />
            </div>
            <div className="flex flex-col gap-2">
            <Label>Домен</Label>
            <Input
              value={formData.domain}
              onChange={e => setFormData({ ...formData, domain: e.target.value })}
              placeholder="example.ru"
              required
            />
            {modalMode === "edit" && (
              <p className="text-xs text-muted-foreground">
                Изменение домена обновит адрес, с которого принимаются запросы виджета.
              </p>
            )}
          </div>
            <div className="flex flex-col gap-2">
              <Label>Стартовые URL</Label>
              <Textarea
                value={formData.startUrls}
                onChange={e => setFormData({ ...formData, startUrls: e.target.value })}
                placeholder={"https://example.ru\nhttps://example.ru/catalog"}
                rows={3}
              />
              <p className="text-xs text-muted-foreground">По одному URL на строку или через запятую</p>
            </div>
            <div className="flex flex-col gap-2">
              <Label>Исключить URL</Label>
              <Textarea
                value={formData.excludeUrls}
                onChange={e => setFormData({ ...formData, excludeUrls: e.target.value })}
                placeholder={"/news\n/vacancies"}
                rows={2}
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Отмена</Button>
              <Button type="submit">Сохранить</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Модалка настроек виджета */}
<Dialog open={isWidgetModalOpen} onOpenChange={setIsWidgetModalOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Настройка виджета — {widgetSite?.name}</DialogTitle>
      <DialogDescription>
        Эти параметры увидят посетители сайта {widgetSite?.domain} в чат-виджете.
      </DialogDescription>
    </DialogHeader>
    <form onSubmit={handleWidgetSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <Label>Название бота</Label>
        <Input
          value={widgetFormData.widget_bot_name}
          onChange={e => setWidgetFormData({ ...widgetFormData, widget_bot_name: e.target.value })}
          placeholder="Помощник"
          maxLength={100}
          required
        />
        <p className="text-xs text-muted-foreground">Отображается в шапке чата.</p>
      </div>

      <div className="flex flex-col gap-2">
        <Label>Приветственное сообщение</Label>
        <Textarea
          value={widgetFormData.widget_welcome_message}
          onChange={e => setWidgetFormData({ ...widgetFormData, widget_welcome_message: e.target.value })}
          placeholder="Здравствуйте! Чем могу помочь?"
          rows={3}
          maxLength={1000}
          required
        />
        <p className="text-xs text-muted-foreground">
          Первое сообщение, которое посетитель увидит при открытии чата.
        </p>
      </div>

      <div className="flex flex-col gap-2">
        <Label>Основной цвет виджета</Label>
        <div className="flex items-center gap-3">
          <input
            type="color"
            value={widgetFormData.widget_primary_color}
            onChange={e => setWidgetFormData({ ...widgetFormData, widget_primary_color: e.target.value })}
            className="h-10 w-14 cursor-pointer rounded border"
          />
          <Input
            value={widgetFormData.widget_primary_color}
            onChange={e => setWidgetFormData({ ...widgetFormData, widget_primary_color: e.target.value })}
            placeholder="#2563eb"
            className="max-w-[140px]"
          />
        </div>
        <p className="text-xs text-muted-foreground">
          Цвет кнопки чата, шапки и сообщений пользователя.
        </p>
      </div>

      <div className="flex flex-col gap-2">
        <Label>URL логотипа (необязательно)</Label>
        <Input
          value={widgetFormData.widget_logo_url}
          onChange={e => setWidgetFormData({ ...widgetFormData, widget_logo_url: e.target.value })}
          placeholder="https://example.ru/logo.png"
          type="url"
        />
        <p className="text-xs text-muted-foreground">
          Заменит стандартную иконку бота в шапке чата. Оставьте пустым, чтобы использовать иконку по умолчанию.
        </p>
      </div>

      {widgetFormData.widget_primary_color && (
        <div className="rounded-lg border p-3">
          <p className="mb-2 text-xs font-medium text-muted-foreground">Предпросмотр шапки</p>
          <div
            className="flex items-center gap-2 rounded-lg p-3 text-white"
            style={{
              background: `linear-gradient(135deg, ${widgetFormData.widget_primary_color}, ${widgetFormData.widget_primary_color}cc)`,
            }}
          >
            <div className="flex h-8 w-8 items-center justify-center overflow-hidden rounded-full bg-white/20">
              {widgetFormData.widget_logo_url ? (
                <img src={widgetFormData.widget_logo_url} alt="" className="h-full w-full object-cover" />
              ) : (
                <span className="text-xs">🤖</span>
              )}
            </div>
            <div>
              <p className="text-sm font-semibold leading-tight">
                {widgetFormData.widget_bot_name || "Помощник"}
              </p>
              <p className="text-[11px] opacity-85">Онлайн</p>
            </div>
          </div>
        </div>
      )}

      <DialogFooter>
        <Button type="button" variant="outline" onClick={() => setIsWidgetModalOpen(false)}>
          Отмена
        </Button>
        <Button type="submit" disabled={savingWidget}>
          {savingWidget ? "Сохранение..." : "Сохранить"}
        </Button>
      </DialogFooter>
    </form>
  </DialogContent>
</Dialog>

      {/* Модалка кода виджета */}
      <Dialog open={showSnippetModal} onOpenChange={setShowSnippetModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Код для установки</DialogTitle>
            <DialogDescription>Вставьте этот тег перед закрывающим &lt;/body&gt; на сайте застройщика.</DialogDescription>
          </DialogHeader>
          <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-xs">{snippet}</pre>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSnippetModal(false)}>Закрыть</Button>
            <Button onClick={() => navigator.clipboard.writeText(snippet)}>Скопировать</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
